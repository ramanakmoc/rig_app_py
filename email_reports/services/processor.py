from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from email_reports.models import EmailAttachment, EmailMessage, ProcessingHistory, ProcessingQueue

from .classification import classify_message
from .extraction import process_attachment
from .notifications import send_acknowledgement, send_operational_alert


def _duplicate_of(message, classification):
    checksums = list(
        message.attachments.exclude(checksum_sha256="").values_list("checksum_sha256", flat=True)
    )
    if checksums:
        duplicate_attachment = (
            EmailAttachment.objects.filter(checksum_sha256__in=checksums)
            .exclude(message=message)
            .filter(message__status__in=["processed", "review", "duplicate"])
            .select_related("message")
            .first()
        )
        if duplicate_attachment:
            return duplicate_attachment.message

    report_date = classification.get("reporting_date")
    site = classification.get("site_name")
    report_type = classification.get("report_type")
    if report_date and site and report_type:
        return (
            EmailMessage.objects.exclude(pk=message.pk)
            .filter(
                reporting_date=report_date,
                site_name__iexact=site,
                report_type__iexact=report_type,
                status__in=["processed", "review", "duplicate"],
            )
            .first()
        )
    return None


def _apply_classification(message, result):
    message.site_name = result.get("site_name", "")
    message.contractor = result.get("contractor", "")
    message.report_type = result.get("report_type", "")
    message.rig_name = result.get("rig_name", "")
    message.reporting_date = result.get("reporting_date") or None
    message.department = result.get("department", "")
    message.priority = result.get("priority", "normal")
    message.confidence_score = result.get("confidence_score")
    message.classification_result = result


def process_message(message):
    message.status = "processing"
    message.save(update_fields=["status", "updated_at"])
    ProcessingHistory.objects.create(message=message, stage="processing", status="started")
    try:
        for attachment in message.attachments.filter(parent_archive__isnull=True):
            process_attachment(attachment)
        result = classify_message(message)
        _apply_classification(message, result)
        duplicate = _duplicate_of(message, result)
        if duplicate:
            message.duplicate_of = duplicate
            message.status = "duplicate"
            message.validation_errors = [f"Duplicate of reference {duplicate.reference_number}."]
        else:
            errors = []
            for label, value in (
                ("site name", message.site_name),
                ("report type", message.report_type),
                ("reporting date", message.reporting_date),
            ):
                if not value:
                    errors.append(f"Could not determine {label}.")
            failed_files = list(
                message.attachments.filter(status__in=["invalid", "failed"]).values_list("filename", flat=True)
            )
            if failed_files:
                errors.append(f"Attachment processing failed: {', '.join(failed_files)}")
            message.validation_errors = errors
            threshold = float(getattr(settings, "EMAIL_COLLECTION_REVIEW_THRESHOLD", 0.65))
            message.status = "review" if errors or float(message.confidence_score or 0) < threshold else "processed"

        message.extraction_result = {
            "attachments": [
                {
                    "filename": attachment.filename,
                    "status": attachment.status,
                    "data": attachment.extracted_data,
                }
                for attachment in message.attachments.all()
            ]
        }
        message.processed_at = timezone.now()
        message.save()
        ProcessingHistory.objects.create(
            message=message,
            stage="processing",
            status=message.status,
            details={"confidence_score": str(message.confidence_score or ""), "errors": message.validation_errors},
        )
        if message.status in {"duplicate", "review"}:
            send_operational_alert(
                message.status,
                f"Email report {message.get_status_display()}: {message.reference_number}",
                f"{message.subject}\nSender: {message.sender_email}\nErrors: {message.validation_errors}",
                message=message,
            )
        send_acknowledgement(message)
        return message
    except Exception as exc:
        message.status = "failed"
        message.validation_errors = [str(exc)[:2000]]
        message.processed_at = timezone.now()
        message.save(update_fields=["status", "validation_errors", "processed_at", "updated_at"])
        ProcessingHistory.objects.create(
            message=message, stage="processing", status="failed", error_message=str(exc)[:4000]
        )
        send_operational_alert(
            "processing_failure",
            f"Email report processing failed: {message.reference_number}",
            f"{message.subject}\nSender: {message.sender_email}\nError: {exc}",
            message=message,
        )
        raise


def process_pending_queue(limit=20):
    processed = 0
    while processed < limit:
        with transaction.atomic():
            item = (
                ProcessingQueue.objects.select_for_update(skip_locked=True)
                .filter(status="pending", available_at__lte=timezone.now())
                .select_related("message")
                .first()
            )
            if not item:
                break
            item.status = "processing"
            item.locked_at = timezone.now()
            item.attempts += 1
            item.save(update_fields=["status", "locked_at", "attempts", "updated_at"])
        try:
            process_message(item.message)
            item.status = "completed"
            item.last_error = ""
        except Exception as exc:
            max_attempts = int(getattr(settings, "EMAIL_COLLECTION_MAX_ATTEMPTS", 3))
            item.status = "failed" if item.attempts >= max_attempts else "pending"
            item.available_at = timezone.now() + timedelta(minutes=2**item.attempts)
            item.last_error = str(exc)[:2000]
        item.save(update_fields=["status", "last_error", "available_at", "updated_at"])
        processed += 1
    return processed
