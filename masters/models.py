from django.db import models
from django.utils import timezone


class Rig(models.Model):
    STATUS_CHOICES = [
        ('Active',      'Active'),
        ('Standby',     'Standby'),
        ('Breakdown',   'Breakdown'),
        ('Demobilised', 'Demobilised'),
    ]
    rig_name          = models.CharField(max_length=30, unique=True)
    rig_model         = models.CharField(max_length=80, blank=True)
    rig_type          = models.CharField(max_length=50, blank=True)
    horse_power       = models.IntegerField(null=True, blank=True)
    depth_capacity    = models.IntegerField(null=True, blank=True, help_text='metres')
    year_commissioned = models.IntegerField(null=True, blank=True)
    current_location  = models.CharField(max_length=100, blank=True)
    rig_status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rig_name']

    def __str__(self):
        return self.rig_name


class WellLocation(models.Model):
    CATEGORY_CHOICES = [
        ('BWP',      'Block Well Pad (BWP)'),
        ('AWP',      'Area Well Pad (AWP)'),
        ('MWP',      'Main Well Pad (MWP)'),
        ('NI',       'New Installation (NI)'),
        ('INTERNAL', 'Internal'),
        ('OTHER',    'Other'),
    ]
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]

    location  = models.CharField(max_length=100, unique=True)
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    block     = models.CharField(max_length=50, blank=True)
    district  = models.CharField(max_length=80, blank=True)
    latitude  = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    notes     = models.TextField(blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'location']

    def __str__(self):
        return f'{self.location} ({self.category})'


class Vendor(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]

    vendor_code    = models.CharField(max_length=20, unique=True)
    vendor_name    = models.CharField(max_length=100)
    vendor_type    = models.CharField(max_length=100, default='General',
                                       help_text='e.g. Trailer, Crane, Both, General')
    contact_person = models.CharField(max_length=80, blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    address        = models.TextField(blank=True)
    contract_no    = models.CharField(max_length=50, blank=True)
    contract_from  = models.DateField(null=True, blank=True)
    contract_to    = models.DateField(null=True, blank=True)
    rate_per_day   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['vendor_name']

    def __str__(self):
        return f'{self.vendor_code} — {self.vendor_name}'

    @property
    def is_contract_expired(self):
        if self.contract_to:
            return self.contract_to < timezone.now().date()
        return False

    @property
    def is_contract_expiring_soon(self):
        if self.contract_to:
            from datetime import timedelta
            return self.contract_to <= (timezone.now().date() + timedelta(days=30))
        return False


class Equipment(models.Model):
    """
    Fleet pool — equipment is NOT assigned to a specific rig permanently.
    Use EquipmentDeployment to track where it is at any time.
    """
    TYPE_CHOICES = [
        ('Crane',     'Crane'),
        ('Trailer',   'Trailer'),
        ('Forklift',  'Forklift'),
        ('Hydra',     'Hydra'),
        ('Generator', 'Generator'),
        ('Pump',      'Pump'),
        ('Vehicle',   'Vehicle'),
        ('Other',     'Other'),
    ]
    STATUS_CHOICES = [
        ('Available',         'Available'),
        ('Deployed',          'Deployed'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Retired',           'Retired'),
    ]

    equipment_no      = models.CharField(max_length=30, unique=True)
    registration_no   = models.CharField(max_length=30, blank=True, help_text='Vehicle/equipment registration number')
    equipment_type    = models.CharField(max_length=20, choices=TYPE_CHOICES)
    make_model        = models.CharField(max_length=100, blank=True)
    capacity          = models.CharField(max_length=50, blank=True, help_text='e.g. 50T, 30m3/hr')
    year_of_mfg       = models.IntegerField(null=True, blank=True)
    vendor            = models.ForeignKey(Vendor, null=True, blank=True,
                                           on_delete=models.SET_NULL, related_name='equipment')
    status            = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Available')
    last_service_date = models.DateField(null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['equipment_type', 'equipment_no']

    def __str__(self):
        return f'{self.equipment_no} ({self.equipment_type})'

    @property
    def current_deployment(self):
        return self.deployments.filter(end_date__isnull=True).first()

    @property
    def is_service_due(self):
        if self.next_service_date:
            return self.next_service_date <= timezone.now().date()
        return False


class EquipmentDeployment(models.Model):
    """
    Tracks where equipment is deployed.
    An equipment can move from rig to rig — end the current deployment,
    create a new one.
    """
    DEPLOY_TYPE_CHOICES = [
        ('Rig',      'Rig Operation'),
        ('ILM',      'ILM Move'),
        ('Location', 'Well Location'),
        ('Workshop', 'Workshop / Maintenance'),
        ('Yard',     'Yard / Storage'),
    ]
    equipment    = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='deployments')
    deploy_type  = models.CharField(max_length=20, choices=DEPLOY_TYPE_CHOICES, default='Rig')
    deployed_to  = models.CharField(max_length=100, help_text='Rig name, location, or workshop name')
    start_date   = models.DateField()
    end_date     = models.DateField(null=True, blank=True, help_text='Leave blank if currently deployed')
    notes        = models.TextField(blank=True)
    created_by   = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        end = self.end_date or 'present'
        return f'{self.equipment} → {self.deployed_to} ({self.start_date} to {end})'
