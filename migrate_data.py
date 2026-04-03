#!/usr/bin/env python3
"""
migrate_data.py — Migrate data from MySQL (rig_operations) to PostgreSQL (rig_operations_py)
Run from the project directory:
    source venv/bin/activate
    python migrate_data.py

Requires:  pip install pymysql
"""

import os
import sys
import django

# ── CONFIG ── Edit these if your passwords differ ──────────────────────────
MYSQL_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'rig_user',
    'password': 'Eureka123',   # ← CHANGE THIS
    'database': 'rig_operations',
    'charset':  'utf8mb4',
}
# PostgreSQL is configured in Django settings — no change needed here.
# ───────────────────────────────────────────────────────────────────────────

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pymysql
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from core.models import UserProfile, RigDailyLog
from ilm.models import ILMLog
from masters.models import Rig, WellLocation, Vendor, Equipment


def connect_mysql():
    return pymysql.connect(**MYSQL_CONFIG)


def log(msg, indent=0):
    prefix = '  ' * indent
    print(f"{prefix}{msg}")


def migrate_users(cursor):
    log("Migrating users...")
    cursor.execute("SELECT id, username, password, role, created_at FROM users ORDER BY id")
    rows = cursor.fetchall()
    created = 0
    skipped = 0
    for row in rows:
        uid, username, pw_hash, role, created_at = row
        if User.objects.filter(username=username).exists():
            skipped += 1
            continue
        # BCrypt hashes from PHP work directly in Django (django.contrib.auth supports bcrypt)
        # BUT Django needs it prefixed with 'bcrypt$'
        if pw_hash.startswith('$2y$') or pw_hash.startswith('$2b$'):
            # Convert PHP BCrypt prefix $2y$ → $2b$ (Django compatible)
            dj_hash = pw_hash.replace('$2y$', '$2b$', 1)
            # Django bcrypt format: bcrypt$$2b$...
            dj_hash = 'bcrypt$' + dj_hash
        else:
            # MD5 or unknown — set a temporary password, user must reset
            dj_hash = make_password('TempPass@123')

        u = User(username=username, password=dj_hash, date_joined=created_at or django.utils.timezone.now())
        u.save()
        valid_roles = ['admin', 'supervisor', 'viewer']
        u.profile.role = role if role in valid_roles else 'viewer'
        u.profile.save()
        created += 1
        log(f"User: {username} (role: {u.profile.role})", 1)

    log(f"Users: {created} created, {skipped} skipped (already exist)")
    return {row[1]: User.objects.get(username=row[1]) for row in rows
            if User.objects.filter(username=row[1]).exists()}


def migrate_rigs(cursor):
    log("Migrating rigs...")
    # Check if rigs table has extra columns (from database_masters.sql)
    cursor.execute("SHOW COLUMNS FROM rigs")
    cols = [r[0] for r in cursor.fetchall()]
    has_extras = 'rig_model' in cols

    if has_extras:
        cursor.execute("""
            SELECT rig_name, rig_model, rig_type, horse_power, depth_capacity,
                   year_commissioned, current_location, rig_status, notes
            FROM rigs ORDER BY id
        """)
        rows = cursor.fetchall()
        created = 0
        for row in rows:
            name, model, rtype, hp, depth, year, loc, status, notes = row
            obj, c = Rig.objects.get_or_create(
                rig_name=name,
                defaults={
                    'rig_model': model or '',
                    'rig_type': rtype or '',
                    'horse_power': hp,
                    'depth_capacity': depth,
                    'year_commissioned': year,
                    'current_location': loc or '',
                    'rig_status': status or 'Active',
                    'notes': notes or '',
                }
            )
            if c:
                created += 1
                log(f"Rig: {name}", 1)
        log(f"Rigs: {created} created")
    else:
        cursor.execute("SELECT rig_name FROM rigs ORDER BY id")
        rows = cursor.fetchall()
        created = 0
        for (name,) in rows:
            _, c = Rig.objects.get_or_create(rig_name=name)
            if c:
                created += 1
                log(f"Rig: {name}", 1)
        log(f"Rigs: {created} created")


def migrate_daily_log(cursor, user_map):
    log("Migrating rig_daily_log...")
    cursor.execute("SHOW COLUMNS FROM rig_daily_log")
    cols = [r[0] for r in cursor.fetchall()]
    created_by_is_int = False
    for col in cols:
        if col == 'created_by':
            created_by_is_int = True  # live DB has INT, not VARCHAR

    cursor.execute("""
        SELECT date, rig, operating_hours, standby_hours, breakdown_hours,
               ilm_hours, zero_rate_hours, reason, status, created_by, created_at
        FROM rig_daily_log
        ORDER BY date, rig
    """)
    rows = cursor.fetchall()
    created = 0
    skipped = 0
    errors  = 0

    for row in rows:
        date, rig, op, sb, bd, ilm, zr, reason, status, cb, created_at = row

        if RigDailyLog.objects.filter(rig=rig, date=date).exists():
            skipped += 1
            continue

        # Resolve created_by
        created_by_user = None
        if cb:
            if created_by_is_int:
                # cb is user ID — find the User
                try:
                    created_by_user = User.objects.get(pk=int(cb))
                except (User.DoesNotExist, ValueError):
                    pass
            else:
                # cb is username string
                created_by_user = user_map.get(str(cb))

        valid_statuses = ['Running', 'Standby', 'Breakdown']
        entry_status = status if status in valid_statuses else 'Running'

        # Validate total hours
        total = float(op or 0) + float(sb or 0) + float(bd or 0) + float(ilm or 0) + float(zr or 0)
        if total > 24.01:
            log(f"  SKIP {rig}/{date}: total hours {total:.2f} > 24", 1)
            errors += 1
            continue

        try:
            RigDailyLog.objects.create(
                date=date, rig=rig,
                operating_hours=float(op or 0),
                standby_hours=float(sb or 0),
                breakdown_hours=float(bd or 0),
                ilm_hours=float(ilm or 0),
                zero_rate_hours=float(zr or 0),
                reason=reason or '',
                status=entry_status,
                created_by=created_by_user,
                created_at=created_at,
            )
            created += 1
        except Exception as e:
            log(f"  ERROR {rig}/{date}: {e}", 1)
            errors += 1

    log(f"Daily log: {created} created, {skipped} skipped, {errors} errors")


def migrate_ilm_log(cursor, user_map):
    log("Migrating rig_ilm_log...")
    cursor.execute("SHOW TABLES LIKE 'rig_ilm_log'")
    if not cursor.fetchone():
        log("  rig_ilm_log table not found — skipping")
        return

    cursor.execute("""
        SELECT date, rig, move_status, ilm_from_location, ilm_to_location,
               distance_kms, expected_ilm_hrs, during_ilm_hrs,
               rig_move_extra_hrs, rig_move_saving_hrs,
               trailer_reported, trailer_loss, trailer_vendor,
               crane_reported, crane_vendor, remarks, created_by, created_at
        FROM rig_ilm_log
        ORDER BY date, rig
    """)
    rows = cursor.fetchall()
    created = 0
    skipped = 0

    for row in rows:
        (date, rig, status, from_loc, to_loc, dist, exp_hrs, during_hrs,
         extra_hrs, saving_hrs, t_rep, t_loss, t_vend,
         crane_rep, crane_vend, remarks, cb, created_at) = row

        if ILMLog.objects.filter(date=date, rig=rig).exists():
            skipped += 1
            continue

        created_by_user = None
        if cb:
            try:
                created_by_user = User.objects.get(pk=int(cb))
            except Exception:
                created_by_user = user_map.get(str(cb))

        valid_statuses = ['Active', 'Standby', 'Internal', 'Idle']
        move_status = status if status in valid_statuses else 'Active'

        try:
            ILMLog.objects.create(
                date=date, rig=rig, move_status=move_status,
                ilm_from_location=from_loc or '',
                ilm_to_location=to_loc or '',
                distance_kms=str(dist or ''),
                expected_ilm_hrs=str(exp_hrs or ''),
                during_ilm_hrs=float(during_hrs) if during_hrs else None,
                rig_move_extra_hrs=float(extra_hrs or 0),
                rig_move_saving_hrs=float(saving_hrs or 0),
                trailer_reported=int(t_rep or 0),
                trailer_loss=int(t_loss or 0),
                trailer_vendor=t_vend or '',
                crane_reported=str(crane_rep or ''),
                crane_vendor=crane_vend or '',
                remarks=remarks or '',
                created_by=created_by_user,
            )
            created += 1
        except Exception as e:
            log(f"  ERROR {rig}/{date}: {e}", 1)

    log(f"ILM log: {created} created, {skipped} skipped")


def migrate_locations(cursor):
    log("Migrating well_locations...")
    cursor.execute("SHOW TABLES LIKE 'well_locations'")
    if not cursor.fetchone():
        log("  well_locations table not found — skipping (use seed_data instead)")
        return

    cursor.execute("SELECT location, category, block, district, status, notes FROM well_locations")
    rows = cursor.fetchall()
    created = 0
    for row in rows:
        loc, cat, block, dist, status, notes = row
        _, c = WellLocation.objects.get_or_create(
            location=loc,
            defaults={
                'category': cat or 'OTHER',
                'block': block or '',
                'district': dist or '',
                'status': status or 'Active',
                'notes': notes or '',
            }
        )
        if c:
            created += 1
    log(f"Locations: {created} created")


def migrate_vendors(cursor):
    log("Migrating vendors...")
    cursor.execute("SHOW TABLES LIKE 'vendors'")
    if not cursor.fetchone():
        log("  vendors table not found — skipping (use seed_data instead)")
        return

    cursor.execute("""
        SELECT vendor_code, vendor_name, vendor_type, contact_person,
               phone, email, address, contract_no, contract_from,
               contract_to, rate_per_day, status, notes
        FROM vendors
    """)
    rows = cursor.fetchall()
    created = 0
    for row in rows:
        (code, name, vtype, contact, phone, email, address,
         contract_no, cfrom, cto, rate, status, notes) = row
        _, c = Vendor.objects.get_or_create(
            vendor_code=code,
            defaults={
                'vendor_name': name,
                'vendor_type': vtype or 'General',
                'contact_person': contact or '',
                'phone': phone or '',
                'email': email or '',
                'address': address or '',
                'contract_no': contract_no or '',
                'contract_from': cfrom,
                'contract_to': cto,
                'rate_per_day': float(rate) if rate else None,
                'status': status or 'Active',
                'notes': notes or '',
            }
        )
        if c:
            created += 1
    log(f"Vendors: {created} created")


def migrate_equipment(cursor):
    log("Migrating equipment...")
    cursor.execute("SHOW TABLES LIKE 'equipment'")
    if not cursor.fetchone():
        log("  equipment table not found — skipping")
        return

    cursor.execute("SHOW COLUMNS FROM equipment")
    cols = [r[0] for r in cursor.fetchall()]
    has_reg = 'registration_no' in cols

    if has_reg:
        cursor.execute("""
            SELECT equipment_no, registration_no, equipment_type, make_model,
                   capacity, year_of_mfg, status, last_service_date, next_service_date, notes
            FROM equipment
        """)
    else:
        cursor.execute("""
            SELECT equipment_no, '' as registration_no, equipment_type, make_model,
                   capacity, year_of_mfg, status, last_service_date, next_service_date, notes
            FROM equipment
        """)

    rows = cursor.fetchall()
    created = 0
    for row in rows:
        (eq_no, reg_no, eq_type, model, capacity, year,
         status, lsvc, nsvc, notes) = row

        valid_types = ['Crane','Trailer','Forklift','Hydra','Generator','Pump','Vehicle','Other']
        if eq_type not in valid_types:
            eq_type = 'Other'

        valid_statuses = ['Available','Deployed','Under Maintenance','Retired']
        if status not in valid_statuses:
            status = 'Available'

        _, c = Equipment.objects.get_or_create(
            equipment_no=eq_no,
            defaults={
                'registration_no': reg_no or '',
                'equipment_type': eq_type,
                'make_model': model or '',
                'capacity': capacity or '',
                'year_of_mfg': int(year) if year else None,
                'status': status,
                'last_service_date': lsvc,
                'next_service_date': nsvc,
                'notes': notes or '',
            }
        )
        if c:
            created += 1
    log(f"Equipment: {created} created")


def print_summary():
    log("\n" + "="*50)
    log("MIGRATION SUMMARY")
    log("="*50)
    log(f"Users:         {User.objects.count()}")
    log(f"Rigs:          {Rig.objects.count()}")
    log(f"Daily logs:    {RigDailyLog.objects.count()}")
    log(f"ILM entries:   {ILMLog.objects.count()}")
    log(f"Locations:     {WellLocation.objects.count()}")
    log(f"Vendors:       {Vendor.objects.count()}")
    log(f"Equipment:     {Equipment.objects.count()}")
    log("="*50)
    log("DONE. Now visit the app and verify data.")


def main():
    log("="*50)
    log("KRISS DRILLING — MySQL → PostgreSQL Migration")
    log("="*50)

    try:
        import django.utils.timezone
    except ImportError:
        pass

    try:
        conn = connect_mysql()
        cursor = conn.cursor()
        log("Connected to MySQL successfully.\n")
    except Exception as e:
        log(f"ERROR: Cannot connect to MySQL: {e}")
        log("Check MYSQL_CONFIG at top of this file.")
        sys.exit(1)

    try:
        user_map = migrate_users(cursor)
        migrate_rigs(cursor)
        migrate_daily_log(cursor, user_map)
        migrate_ilm_log(cursor, user_map)
        migrate_locations(cursor)
        migrate_vendors(cursor)
        migrate_equipment(cursor)
        print_summary()
    except Exception as e:
        log(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
