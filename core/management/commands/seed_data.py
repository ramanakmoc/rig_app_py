"""
Management command to seed master data.
Run after migrations:  python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
from masters.models import Rig, WellLocation, Vendor


class Command(BaseCommand):
    help = 'Seed initial master data — rigs, locations, vendors, admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding master data...')

        # ── Rigs ──
        rigs = ['PPE-1', 'PPE-2', 'PPE-3', 'PPE-4', 'PPE-5']
        for name in rigs:
            obj, created = Rig.objects.get_or_create(rig_name=name)
            if created:
                self.stdout.write(f'  Created rig: {name}')

        # ── Well Locations ──
        locations = [
            ('BWP#01','BWP'),('BWP#02','BWP'),('BWP#03','BWP'),('BWP#04','BWP'),
            ('BWP#05','BWP'),('BWP#06','BWP'),('BWP#07','BWP'),('BWP#08','BWP'),
            ('BWP#09','BWP'),('BWP#10','BWP'),('BWP#11','BWP'),('BWP#12','BWP'),
            ('BWP#13','BWP'),('BWP#14','BWP'),('BWP#15','BWP'),
            ('AWP#01','AWP'),('AWP#02','AWP'),('AWP#03','AWP'),
            ('MWP#01','MWP'),('MWP#02','MWP'),('MWP#03','MWP'),('MWP#04','MWP'),
            ('MWP#05','MWP'),('MWP#06','MWP'),('MWP#07','MWP'),('MWP#08','MWP'),
            ('MWP#09','MWP'),('MWP#10','MWP'),('MWP#11','MWP'),('MWP#12','MWP'),
            ('MWP#13','MWP'),
            ('NI#01','NI'),('NI#02','NI'),('NI#03','NI'),
            ('INTERNAL','INTERNAL'),
        ]
        for loc, cat in locations:
            obj, created = WellLocation.objects.get_or_create(
                location=loc, defaults={'category': cat}
            )
            if created:
                self.stdout.write(f'  Created location: {loc}')

        # ── Vendors ──
        vendors = [
            ('SBTC', 'SBTC',  'Trailer'),
            ('ACC',  'ACC',   'Crane,Trailer'),
            ('JEET', 'JEET',  'Trailer'),
            ('ARC',  'ARC',   'Crane'),
        ]
        for code, name, vtype in vendors:
            obj, created = Vendor.objects.get_or_create(
                vendor_code=code,
                defaults={'vendor_name': name, 'vendor_type': vtype}
            )
            if created:
                self.stdout.write(f'  Created vendor: {code}')

        # ── Admin user ──
        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser('admin', '', 'Admin@123')
            u.profile.role = 'admin'
            u.profile.save()
            self.stdout.write('  Created admin user (password: Admin@123 — CHANGE THIS!)')
        else:
            self.stdout.write('  Admin user already exists')

        self.stdout.write(self.style.SUCCESS('Seed complete!'))
