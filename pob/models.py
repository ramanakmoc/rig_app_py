from django.db import models
from django.contrib.auth.models import User


# ── POB MASTERS ─────────────────────────────────────────────────────
class POBDesignation(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    category   = models.CharField(max_length=50, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['category','name']
    def __str__(self): return self.name

class POBCompany(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    short_code = models.CharField(max_length=20, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['name']
    def __str__(self): return self.name

class POBAccommodation(models.Model):
    name      = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['name']
    def __str__(self): return self.name

class POBRoomNo(models.Model):
    accommodation = models.ForeignKey(POBAccommodation, on_delete=models.CASCADE,
                                       related_name='rooms', null=True, blank=True)
    room_no   = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['accommodation__name','room_no']
    def __str__(self): return f"{self.accommodation} — {self.room_no}" if self.accommodation else self.room_no


# ── POB DAILY LOG ────────────────────────────────────────────────────
class POBDailyLog(models.Model):
    rig           = models.CharField(max_length=30, db_index=True)
    date          = models.DateField(db_index=True)
    location      = models.CharField(max_length=50, blank=True)
    lti_free_days = models.IntegerField(default=0)
    remarks       = models.TextField(blank=True)
    created_by    = models.ForeignKey(User, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='pob_logs')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('rig', 'date')
        ordering = ['-date', 'rig']

    def __str__(self): return f'POB {self.rig} — {self.date}'

    @property
    def total_pob(self):
        return self.persons.filter(is_active=True).count()

    @property
    def day_pob_live(self):
        return self.persons.filter(is_active=True, left_site=False).count()

    @property
    def meal_breakfast(self):
        return self.persons.filter(is_active=True, meal_b=True).count()

    @property
    def meal_lunch(self):
        return self.persons.filter(is_active=True, meal_l=True).count()

    @property
    def meal_dinner(self):
        return self.persons.filter(is_active=True, meal_d=True).count()


# ── POB PERSON ───────────────────────────────────────────────────────
class POBPerson(models.Model):
    SHIFT_CHOICES = [('D','Day'),('N','Night'),('G','General')]
    CATEGORY_CHOICES = [
        ('VEDANTA_PERSON',  'Vedanta Person'),
        ('VEDANTA_VISITOR', 'Vedanta Visitor'),
        ('VEDANTA_SERVICE', 'Vedanta Services'),
        ('VEDANTA_DRIVER',  'Vedanta Driver'),
        ('KSD_CREW',        'KSD Drilling Crew'),
        ('CONTRACTOR',      'Contractor / Vendor'),
        ('OTHER',           'Other'),
    ]

    pob_log       = models.ForeignKey(POBDailyLog, on_delete=models.CASCADE, related_name='persons')
    category      = models.CharField(max_length=50, default='KSD_CREW', db_index=True)
    sno           = models.IntegerField(null=True, blank=True)
    name          = models.CharField(max_length=100, db_index=True)
    designation   = models.ForeignKey(POBDesignation, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='pob_persons')
    designation_text = models.CharField(max_length=100, blank=True,
                                         help_text='Free text if not in master')
    shift         = models.CharField(max_length=2, choices=SHIFT_CHOICES, blank=True, default='G')
    company       = models.ForeignKey(POBCompany, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='pob_persons')
    company_text  = models.CharField(max_length=100, blank=True)
    accommodation = models.ForeignKey(POBAccommodation, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='pob_persons')
    accommodation_text = models.CharField(max_length=150, blank=True)
    room_no       = models.ForeignKey(POBRoomNo, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='pob_persons')
    room_no_text  = models.CharField(max_length=50, blank=True)
    doj           = models.DateField(null=True, blank=True)
    days_on_site  = models.IntegerField(default=0)
    nationality   = models.CharField(max_length=50, default='INDIAN')
    mobile_no     = models.CharField(max_length=20, blank=True)
    meal_b        = models.BooleanField(default=False)
    meal_l        = models.BooleanField(default=False)
    meal_d        = models.BooleanField(default=False)
    arrived       = models.BooleanField(default=False)
    left_site     = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=True)
    remarks       = models.TextField(blank=True)

    class Meta: ordering = ['category','sno','name']

    def __str__(self):
        return f'{self.name} — {self.pob_log.rig} {self.pob_log.date}'

    def get_designation(self):
        return self.designation.name if self.designation else self.designation_text

    def get_company(self):
        return self.company.name if self.company else self.company_text

    def get_accommodation(self):
        return self.accommodation.name if self.accommodation else self.accommodation_text

    def get_room_no(self):
        return self.room_no.room_no if self.room_no else self.room_no_text


# ── POB EMPLOYEE MASTER ───────────────────────────────────────────────
class POBEmployee(models.Model):
    """Master list of all personnel — for quick search/auto-fill."""
    name          = models.CharField(max_length=100, db_index=True)
    designation   = models.ForeignKey(POBDesignation, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='employees')
    company       = models.ForeignKey(POBCompany, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='employees')
    rig           = models.CharField(max_length=30, blank=True, help_text='Assigned rig')
    shift         = models.CharField(max_length=2, choices=[('D','Day'),('N','Night'),('G','General')], default='G')
    mobile_no     = models.CharField(max_length=20, blank=True)
    nationality   = models.CharField(max_length=50, default='INDIAN')
    category      = models.CharField(max_length=50, blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    CATEGORY_CHOICES = POBPerson.CATEGORY_CHOICES

    class Meta:
        ordering = ['company__name','name']
        unique_together = ('name', 'company')

    def __str__(self):
        return f"{self.name} — {self.company} ({self.designation})"


# ── POB EMPLOYEE MASTER ───────────────────────────────────────────────


# ── POB CATEGORY MASTER ───────────────────────────────────────────────
class POBCategory(models.Model):
    """Dynamic category list — replaces the hardcoded CATEGORY_CHOICES."""
    key        = models.CharField(max_length=50, unique=True,
                                   help_text='Internal key stored on POBPerson.category')
    label      = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'label']

    def __str__(self):
        return self.label

    @classmethod
    def as_choices(cls):
        return list(cls.objects.filter(is_active=True).values_list('key', 'label'))

    @classmethod
    def seed_defaults(cls):
        defaults = [
            ('VEDANTA_PERSON',  'Vedanta Person',      1),
            ('VEDANTA_VISITOR', 'Vedanta Visitor',     2),
            ('VEDANTA_SERVICE', 'Vedanta Services',    3),
            ('VEDANTA_DRIVER',  'Vedanta Driver',      4),
            ('KSD_CREW',        'KSD Drilling Crew',   5),
            ('KSD_3RD_PARTY',   'KSD 3rd Party',       6),
            ('CONTRACTOR',      'Contractor / Vendor', 7),
            ('OTHER',           'Other',               8),
        ]
        for key, label, order in defaults:
            cls.objects.get_or_create(key=key, defaults={'label': label, 'sort_order': order})
