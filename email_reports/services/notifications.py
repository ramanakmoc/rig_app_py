from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from email_reports.models import NotificationLog


def _send(event_type, recipient, subject, body, message=None, missing_report=None):
    log = NotificationLog.objects.create(
        event_type=event_type,
        channel="email",
        recipient=recipient,
        subject=subject,
        payload={"body": body},
        related_message=message,
        related_missing_report=missing_report,
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        log.status = "sent"
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "sent_at"])
    except Exception as exc:
        log.status = "failed"
        log.error_message = str(exc)[:2000]
        log.save(update_fields=["status", "error_message"])
    return log


def send_acknowledgement(message):
    if not message.sender_email or message.sender_email.endswith(".invalid"):
        return
    if NotificationLog.objects.filter(event_type="acknowledgement", related_message=message).exists():
        return
    errors = "; ".join(message.validation_errors) if message.validation_errors else "None"
    body = (
        "Report received successfully.\n\n"
        f"Reference Number: {message.reference_number}\n"
        f"Processing Status: {message.get_status_display()}\n"
        f"Submission Date: {message.received_at:%Y-%m-%d %H:%M %Z}\n"
        f"Error Details: {errors}\n"
    )
    _send(
        "acknowledgement",
        message.sender_email,
        f"Report receipt - {message.reference_number}",
        body,
        message=message,
    )


def send_operational_alert(event_type, subject, body, message=None, missing_report=None, recipients=None):
    recipients = recipients or getattr(settings, "EMAIL_COLLECTION_ALERT_RECIPIENTS", [])
    for recipient in [item.strip() for item in recipients if item and item.strip()]:
        _send(event_type, recipient, subject, body, message=message, missing_report=missing_report)
    NotificationLog.objects.create(
        event_type=event_type,
        channel="dashboard",
        subject=subject,
        payload={"body": body},
        status="sent",
        sent_at=timezone.now(),
        related_message=message,
        related_missing_report=missing_report,
    )

