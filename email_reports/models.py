import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .crypto import decrypt_json, encrypt_json


class EmailAccount(models.Model):
    PROVIDER_CHOICES = [
        ("microsoft365", "Microsoft 365 / Outlook"),
        ("gmail", "Gmail"),
        ("imap", "IMAP-compatible server"),
    ]
    TRANSPORT_CHOICES = [
        ("imap", "IMAP / IMAP OAuth2"),
        ("graph", "Microsoft Graph API"),
        ("gmail_api", "Gmail API"),
    ]
    AUTH_CHOICES = [
        ("password", "Password / app password"),
        ("oauth2", "OAuth2"),
    ]

    name = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    transport = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default="imap")
    auth_method = models.CharField(max_length=20, choices=AUTH_CHOICES, default="oauth2")
    email_address = models.EmailField()
    username = models.CharField(max_length=254, blank=True)
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=993)
    folder = models.CharField(max_length=255, default="INBOX")
    is_shared_mailbox = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=True)
    mark_as_read = models.BooleanField(default=False)
    polling_interval_seconds = models.PositiveIntegerField(default=60)
    last_uid = models.PositiveBigIntegerField(default=0)
    sync_cursor = models.TextField(blank=True)
    encrypted_credentials = models.TextField(blank=True, editable=False)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.email_address})"

    def set_credentials(self, credentials):
        self.encrypted_credentials = encrypt_json(credentials)

    def get_credentials(self):
        return decrypt_json(self.encrypted_credentials)


class SenderRegistry(models.Model):
    TYPE_CHOICES = [("email", "Email address"), ("domain", "Domain")]
    STATUS_CHOICES = [("approved", "Approved"), ("blocked", "Blocked")]

    match_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="approved")
    site_name = models.CharField(max_length=120, blank=True)
    contractor = models.CharField(max_length=160, blank=True)
    default_department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["match_type", "value"]
        constraints = [
            models.UniqueConstraint(
                fields=["match_type", "value"], name="email_sender_registry_match_unique"
            )
        ]

    def save(self, *args, **kwargs):
        self.value = self.value.strip().lower().lstrip("@")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_status_display()}: {self.value}"


def original_email_path(instance, filename):
    received = instance.received_at or timezone.now()
    return f"email_reports/{received:%Y/%m/%d}/{instance.reference_number}/{filename}"


class EmailMessage(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("processed", "Processed"),
        ("review", "Needs human review"),
        ("invalid", "Invalid"),
        ("duplicate", "Duplicate"),
        ("rejected", "Rejected"),
        ("failed", "Failed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    reference_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    account = models.ForeignKey(EmailAccount, on_delete=models.PROTECT, related_name="messages")
    provider_message_id = models.CharField(max_length=512, blank=True)
    message_id = models.CharField(max_length=998)
    thread_id = models.CharField(max_length=998, blank=True)
    in_reply_to = models.CharField(max_length=998, blank=True)
    references = models.TextField(blank=True)
    sender_name = models.CharField(max_length=255, blank=True)
    sender_email = models.EmailField()
    recipients = models.JSONField(default=list, blank=True)
    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)
    subject = models.TextField(blank=True)
    body_text = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    raw_headers = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(default=timezone.now)
    original_email = models.FileField(upload_to=original_email_path, max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received", db_index=True)
    is_authorized_sender = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="duplicates"
    )
    site_name = models.CharField(max_length=120, blank=True, db_index=True)
    contractor = models.CharField(max_length=160, blank=True)
    report_type = models.CharField(max_length=120, blank=True, db_index=True)
    rig_name = models.CharField(max_length=100, blank=True, db_index=True)
    reporting_date = models.DateField(null=True, blank=True, db_index=True)
    department = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="normal")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    classification_result = models.JSONField(default=dict, blank=True)
    extraction_result = models.JSONField(default=dict, blank=True)
    validation_errors = models.JSONField(default=list, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "message_id"], name="email_message_account_id_unique"
            )
        ]
        indexes = [
            models.Index(fields=["site_name", "report_type", "reporting_date"]),
            models.Index(fields=["sender_email", "received_at"]),
        ]

    def __str__(self):
        return f"{self.subject or '(no subject)'} - {self.sender_email}"


def attachment_path(instance, filename):
    received = instance.message.received_at or timezone.now()
    return f"email_reports/{received:%Y/%m/%d}/{instance.message.reference_number}/attachments/{filename}"


class EmailAttachment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("extracted", "Extracted"),
        ("unsupported", "Unsupported"),
        ("invalid", "Invalid"),
        ("failed", "Failed"),
    ]

    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name="attachments")
    parent_archive = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="archive_members"
    )
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64, db_index=True)
    file = models.FileField(upload_to=attachment_path, max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    extracted_text = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["filename"]
        indexes = [models.Index(fields=["checksum_sha256", "size_bytes"])]

    def __str__(self):
        return self.filename


class ProcessingQueue(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    message = models.OneToOneField(EmailMessage, on_delete=models.CASCADE, related_name="queue_item")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    available_at = models.DateTimeField(default=timezone.now, db_index=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProcessingHistory(models.Model):
    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name="history")
    stage = models.CharField(max_length=80)
    status = models.CharField(max_length=30)
    details = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class ExpectedReport(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    name = models.CharField(max_length=160)
    site_name = models.CharField(max_length=120)
    contractor = models.CharField(max_length=160, blank=True)
    report_type = models.CharField(max_length=120)
    rig_name = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="daily")
    due_time = models.TimeField()
    weekdays = models.JSONField(
        default=list,
        blank=True,
        help_text="ISO weekday numbers (1=Monday, 7=Sunday). Empty means every day.",
    )
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    grace_minutes = models.PositiveIntegerField(default=0)
    notification_recipients = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["site_name", "report_type"]

    def __str__(self):
        return self.name


class MissingReport(models.Model):
    STATUS_CHOICES = [
        ("missing", "Missing"),
        ("received_late", "Received late"),
        ("resolved", "Resolved"),
        ("waived", "Waived"),
    ]

    expected_report = models.ForeignKey(ExpectedReport, on_delete=models.CASCADE, related_name="missing_instances")
    reporting_date = models.DateField()
    due_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="missing", db_index=True)
    received_message = models.ForeignKey(
        EmailMessage, null=True, blank=True, on_delete=models.SET_NULL, related_name="resolved_missing_reports"
    )
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-reporting_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["expected_report", "reporting_date"], name="email_missing_report_unique"
            )
        ]


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("dashboard", "Dashboard"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
    ]
    STATUS_CHOICES = [("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed")]

    event_type = models.CharField(max_length=50)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    related_message = models.ForeignKey(
        EmailMessage, null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications"
    )
    related_missing_report = models.ForeignKey(
        MissingReport, null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications"
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

