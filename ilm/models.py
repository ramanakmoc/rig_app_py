from django.db import models
from django.contrib.auth.models import User


class ILMLog(models.Model):
    STATUS_CHOICES = [
        ('Active',   'Active — Rig Moving'),
        ('Standby',  'Standby — Waiting'),
        ('Internal', 'Internal Move'),
        ('Idle',     'Idle — No Activity'),
    ]

    date                = models.DateField(db_index=True)
    rig                 = models.CharField(max_length=30, db_index=True)
    move_status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    ilm_from_location   = models.CharField(max_length=150, blank=True)
    ilm_to_location     = models.CharField(max_length=150, blank=True)
    distance_kms        = models.CharField(max_length=50, blank=True,
                                            help_text='Can be multi-leg: 46 & 3.9')
    expected_ilm_hrs    = models.CharField(max_length=20, blank=True,
                                            help_text='Can be multi-leg: 54 & 30')
    during_ilm_hrs      = models.DecimalField(max_digits=5, decimal_places=2,
                                               null=True, blank=True, help_text='Actual hours taken')
    rig_move_extra_hrs  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rig_move_saving_hrs = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Trailer details (text fields to handle mixed vendor formats e.g. "SBTC & ACC")
    trailer_reported = models.IntegerField(default=0)
    trailer_loss     = models.IntegerField(default=0)
    trailer_vendor   = models.CharField(max_length=150, blank=True)

    # Crane details
    crane_reported = models.CharField(max_length=50, blank=True,
                                       help_text='Count or description e.g. 2, 1 ARC & 1 ACC')
    crane_vendor   = models.CharField(max_length=150, blank=True)

    remarks    = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='ilm_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'rig']
        indexes  = [
            models.Index(fields=['date']),
            models.Index(fields=['rig']),
            models.Index(fields=['move_status']),
        ]

    def __str__(self):
        return f'{self.rig} ILM — {self.date} ({self.move_status})'


class ILMEquipmentUsage(models.Model):
    """
    Links fleet equipment to a specific ILM log entry.
    This replaces the free-text vendor fields for structured tracking.
    Both can coexist — use this when you want to track specific equipment numbers.
    """
    ROLE_CHOICES = [
        ('Trailer', 'Trailer'),
        ('Crane',   'Crane'),
        ('Forklift','Forklift'),
        ('Hydra',   'Hydra'),
        ('Support', 'Support Vehicle'),
        ('Other',   'Other'),
    ]
    ilm_log   = models.ForeignKey(ILMLog, on_delete=models.CASCADE, related_name='equipment_usage')
    equipment = models.ForeignKey('masters.Equipment', on_delete=models.PROTECT,
                                   related_name='ilm_usages')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Trailer')
    notes     = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('ilm_log', 'equipment')

    def __str__(self):
        return f'{self.equipment} on {self.ilm_log}'
