from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HSDReceipt(models.Model):
    """
    Records every tanker delivery of diesel.
    A receipt can be at a rig site or a central storage point.
    """
    date          = models.DateField(db_index=True)
    receipt_no    = models.CharField(max_length=50, blank=True, help_text='Challan / Invoice number')
    rig           = models.CharField(max_length=30, db_index=True,
                                      help_text='Rig or location receiving the diesel')
    supplier      = models.ForeignKey('masters.Vendor', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='hsd_receipts',
                                       help_text='Fuel supplier vendor')
    supplier_name = models.CharField(max_length=100, blank=True,
                                      help_text='Supplier name if not in vendor master')
    vehicle_no    = models.CharField(max_length=30, blank=True, help_text='Tanker vehicle number')
    quantity_ltrs = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text='Quantity received in litres')
    rate_per_ltr  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                         help_text='Rate per litre (₹)')
    invoice_amount= models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    received_by   = models.CharField(max_length=80, blank=True)
    remarks       = models.TextField(blank=True)
    created_by    = models.ForeignKey(User, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='hsd_receipts')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'rig']
        indexes  = [
            models.Index(fields=['date']),
            models.Index(fields=['rig']),
        ]

    def __str__(self):
        return f'Receipt: {self.rig} — {self.date} — {self.quantity_ltrs}L'

    @property
    def total_amount(self):
        if self.rate_per_ltr:
            return float(self.quantity_ltrs) * float(self.rate_per_ltr)
        return self.invoice_amount or 0


class HSDIssue(models.Model):
    """
    Records every diesel issue — to a rig engine, generator, equipment, or vehicle.
    The key insight: diesel can be issued to ANY equipment regardless of rig.
    """
    PURPOSE_CHOICES = [
        ('Drilling',   'Drilling / Rig Engine'),
        ('Generator',  'Generator'),
        ('Equipment',  'Equipment (Crane/Trailer/Hydra)'),
        ('Vehicle',    'Vehicle / Transport'),
        ('Camp',       'Camp / Utility'),
        ('Other',      'Other'),
    ]

    date          = models.DateField(db_index=True)
    rig           = models.CharField(max_length=30, db_index=True,
                                      help_text='Rig or location issuing from')
    meter_start   = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True,
                                         help_text='Starting meter/hour reading')
    meter_end     = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True,
                                         help_text='Ending meter/hour reading')
    meter_hours   = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True,
                                         help_text='Hours run (auto = end - start)')
    purpose       = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='Drilling')
    issued_to     = models.CharField(max_length=100,
                                      help_text='Rig name, equipment no, or description')
    equipment     = models.ForeignKey('masters.Equipment', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='hsd_issues',
                                       help_text='Link to fleet equipment if applicable')
    quantity_ltrs = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text='Quantity issued in litres')
    issued_by     = models.CharField(max_length=80, blank=True)
    remarks       = models.TextField(blank=True)
    created_by    = models.ForeignKey(User, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='hsd_issues')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'rig']
        indexes  = [
            models.Index(fields=['date']),
            models.Index(fields=['rig']),
            models.Index(fields=['purpose']),
        ]

    def __str__(self):
        return f'Issue: {self.rig} → {self.issued_to} — {self.date} — {self.quantity_ltrs}L'


class HSDDailyStock(models.Model):
    """
    Daily stock reconciliation per rig.
    Opening stock + Receipts - Issues = Closing stock.
    One record per rig per day.
    """
    date          = models.DateField(db_index=True)
    rig           = models.CharField(max_length=30, db_index=True)
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Stock at start of day (litres)')
    receipts      = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Total received during day (auto-computed)')
    consumption   = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Total issued/consumed during day (auto-computed)')
    closing_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Stock at end of day (auto-computed)')
    remarks       = models.TextField(blank=True)
    created_by    = models.ForeignKey(User, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='hsd_stock_entries')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('date', 'rig')
        ordering        = ['-date', 'rig']
        indexes         = [
            models.Index(fields=['date']),
            models.Index(fields=['rig']),
        ]

    def __str__(self):
        return f'HSD Stock: {self.rig} — {self.date} | Closing: {self.closing_stock}L'

    def recompute(self):
        """Recompute receipts, consumption, closing from related records."""
        from django.db.models import Sum
        r = HSDReceipt.objects.filter(date=self.date, rig=self.rig).aggregate(
            total=Sum('quantity_ltrs'))['total'] or 0
        c = HSDIssue.objects.filter(date=self.date, rig=self.rig).aggregate(
            total=Sum('quantity_ltrs'))['total'] or 0
        self.receipts    = r
        self.consumption = c
        self.closing_stock = float(self.opening_stock) + float(r) - float(c)
        self.save()
