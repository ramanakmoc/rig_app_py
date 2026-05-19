"""
Auto-create today's POB log for all rigs by carrying forward from yesterday.
Designed to run via cron at 6am every morning.

Usage:
    python manage.py auto_pob_carry_forward
    python manage.py auto_pob_carry_forward --date=2026-05-03
    python manage.py auto_pob_carry_forward --rig=PPE-1

Cron entry (run at 6am daily):
    0 6 * * * cd /var/www/rig_app_py && /var/www/rig_app_py/venv/bin/python manage.py auto_pob_carry_forward >> logs/auto_pob.log 2>&1
"""
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from django.contrib.auth.models import User
from masters.models import Rig
from pob.models import POBDailyLog, POBPerson


class Command(BaseCommand):
    help = 'Carry forward POB from previous day to today for all active rigs'

    def add_arguments(self, parser):
        parser.add_argument('--date', default=None, help='Target date (YYYY-MM-DD), default = today')
        parser.add_argument('--rig',  default=None, help='Specific rig, default = all active')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **opts):
        target_date = (
            datetime.date.fromisoformat(opts['date'])
            if opts['date'] else datetime.date.today()
        )
        dry_run = opts['dry_run']

        if opts['rig']:
            rigs = [opts['rig']]
        else:
            rigs = list(Rig.objects.filter(is_active=True).values_list('name', flat=True))

        if not rigs:
            self.stdout.write(self.style.WARNING('No active rigs found.'))
            return

        # Get a default user for created_by
        default_user = User.objects.filter(is_superuser=True).first()

        total_logs_created  = 0
        total_persons_added = 0

        for rig in rigs:
            self.stdout.write(f'\n--- {rig} ---')

            # Find previous day's log for this rig
            prev_log = POBDailyLog.objects.filter(
                rig=rig, date__lt=target_date
            ).order_by('-date').first()

            if not prev_log:
                self.stdout.write(self.style.WARNING(f'  No previous log found for {rig}'))
                continue

            # Get or create target log
            target_log = POBDailyLog.objects.filter(rig=rig, date=target_date).first()
            if not target_log:
                if dry_run:
                    self.stdout.write(f'  [DRY] Would create new log for {rig} on {target_date}')
                else:
                    target_log = POBDailyLog.objects.create(
                        rig=rig,
                        date=target_date,
                        location=prev_log.location,
                        lti_free_days=prev_log.lti_free_days + 1,
                        remarks=f'Auto-created from {prev_log.date}',
                        created_by=default_user,
                    )
                    total_logs_created += 1
                    self.stdout.write(f'  Created new log pk={target_log.pk}')

            if not target_log and not dry_run:
                continue

            # Carry forward missing persons
            existing_names = set()
            if target_log:
                existing_names = set(
                    p.name.upper().strip() for p in target_log.persons.all()
                )

            next_sno = 1
            if target_log:
                next_sno = (target_log.persons.aggregate(m=Max('sno'))['m'] or 0) + 1

            copied = 0
            skipped = 0

            for p in prev_log.persons.filter(left_site=False, is_active=True):
                if p.name.upper().strip() in existing_names:
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f'  [DRY] Would copy: {p.name}')
                    copied += 1
                    continue

                with transaction.atomic():
                    POBPerson.objects.create(
                        pob_log       = target_log,
                        sno           = next_sno,
                        name          = p.name,
                        category      = p.category,
                        shift         = p.shift,
                        designation   = p.designation,
                        company       = p.company,
                        accommodation = p.accommodation,
                        room_no       = p.room_no,
                        doj           = p.doj,
                        days_on_site  = p.days_on_site + 1,
                        mobile_no     = p.mobile_no,
                        meal_b        = p.meal_b,
                        meal_l        = p.meal_l,
                        meal_d        = p.meal_d,
                        arrived       = p.arrived,
                        left_site     = False,
                        remarks       = p.remarks or '',
                        is_active     = True,
                    )
                    next_sno += 1
                    copied += 1

            total_persons_added += copied
            self.stdout.write(
                self.style.SUCCESS(f'  {rig}: copied {copied}, skipped {skipped} (already present)')
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'DONE: {total_logs_created} new logs, {total_persons_added} persons carried forward to {target_date}'
        ))
