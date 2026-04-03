from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',      'Admin'),
        ('supervisor', 'Supervisor'),
        ('viewer',     'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f'{self.user.username} ({self.role})'

    def is_admin(self):
        return self.role == 'admin'

    def is_supervisor(self):
        return self.role in ('admin', 'supervisor')


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)


class RigDailyLog(models.Model):
    STATUS_CHOICES = [
        ('Running',   'Running'),
        ('Standby',   'Standby'),
        ('Breakdown', 'Breakdown'),
    ]

    date             = models.DateField()
    rig              = models.CharField(max_length=30, db_index=True)
    operating_hours  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    standby_hours    = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    breakdown_hours  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ilm_hours        = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    zero_rate_hours  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reason           = models.TextField(blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Running')
    created_by       = models.ForeignKey(User, null=True, blank=True,
                                          on_delete=models.SET_NULL, related_name='log_entries')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('rig', 'date')
        ordering = ['-date', 'rig']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['rig']),
            models.Index(fields=['zero_rate_hours']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(operating_hours__gte=0) &
                    models.Q(standby_hours__gte=0) &
                    models.Q(breakdown_hours__gte=0) &
                    models.Q(ilm_hours__gte=0) &
                    models.Q(zero_rate_hours__gte=0)
                ),
                name='rdl_no_negative_hours'
            )
        ]

    def __str__(self):
        return f'{self.rig} — {self.date}'

    @property
    def total_hours(self):
        return (self.operating_hours + self.standby_hours +
                self.breakdown_hours + self.ilm_hours + self.zero_rate_hours)

    @property
    def efficiency_pct(self):
        total = float(self.total_hours)
        if total == 0:
            return 0
        return round(float(self.operating_hours) / total * 100, 1)
