import hashlib
import re
from datetime import timezone as dt_timezone
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.utils import timezone

from email_reports.models import (
    EmailAttachment,
    EmailMessage,
    ProcessingHistory,
    ProcessingQueue,
    SenderRegistry,
)


def _header(value):
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (LookupError, UnicodeDecodeError):
        return str(value)


def _addresses(message, header_name):
    return [address.lower() for _, address in getaddresses(message.get_all(header_name, [])) if address]


def _sender(message):
    values = getaddresses(message.get_all("From", []))
    if not values:
        return "", ""
    name, address = values[0]
    return _header(name), address.lower()


def _date(value, fallback=None):
    if not value:
        return fallback
    try:
        result = parsedate_to_datetime(value)
        if timezone.is_naive(result):
            result = result.replace(tzinfo=dt_timezone.utc)
        return result
    except (TypeError, ValueError, OverflowError):
        return fallback


def _safe_filename(filename, fallback="attachment.bin"):
    name = Path(filename or fallback).name
    name = re.sub(r"[^A-Za-z0-9._() -]", "_", name).strip(" .")
    return (name or fallback)[:240]


def sender_authorization(sender_email):
    sender_email = sender_email.lower()
    domain = sender_email.rsplit("@", 1)[-1] if "@" in sender_email else ""
    records = SenderRegistry.objects.filter(is_active=True)
    blocked = records.filter(status="blocked").filter(
        models.Q(match_type="email", value=sender_email)
        | models.Q(match_type="domain", value=domain)
    ).first()
    if blocked:
        return False, blocked
    approved = records.filter(status="approved").filter(
        models.Q(match_type="email", value=sender_email)
        | models.Q(match_type="domain", value=domain)
    ).first()
    return bool(approved), approved


def _body_parts(message):
    text_parts = []
    html_parts = []
    for part in message.walk() if message.is_multipart() else [message]:
        if part.get_content_disposition() == "attachment":
            continue
        content_type = part.get_content_type()
        if content_type not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeDecodeError):
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if content_type == "text/plain":
            text_parts.append(content)
        else:
            html_parts.append(content)
    return "\n".join(text_parts), "\n".join(html_parts)


@transaction.atomic
def ingest_raw_message(account, provider_message_id, raw_message):
    parsed = BytesParser(policy=policy.default).parsebytes(raw_message)
    raw_hash = hashlib.sha256(raw_message).hexdigest()
    message_id = _header(parsed.get("Message-ID")) or f"sha256:{raw_hash}"
    existing = EmailMessage.objects.filter(account=account, message_id=message_id).first()
    if existing:
        return existing, False

    sender_name, sender_email = _sender(parsed)
    authorized, sender_record = sender_authorization(sender_email)
    body_text, body_html = _body_parts(parsed)
    received_at = _date(parsed.get("Date"), timezone.now())
    message = EmailMessage(
        account=account,
        provider_message_id=provider_message_id,
        message_id=message_id,
        thread_id=_header(parsed.get("Thread-Index") or parsed.get("Thread-Topic")),
        in_reply_to=_header(parsed.get("In-Reply-To")),
        references=_header(parsed.get("References")),
        sender_name=sender_name,
        sender_email=sender_email or "unknown@example.invalid",
        recipients=_addresses(parsed, "To"),
        cc=_addresses(parsed, "Cc"),
        bcc=_addresses(parsed, "Bcc"),
        subject=_header(parsed.get("Subject")),
        body_text=body_text,
        body_html=body_html,
        raw_headers={key: _header(value) for key, value in parsed.items()},
        sent_at=_date(parsed.get("Date")),
        received_at=received_at,
        is_authorized_sender=authorized,
        site_name=sender_record.site_name if sender_record else "",
        contractor=sender_record.contractor if sender_record else "",
        department=sender_record.default_department if sender_record else "",
        status="received" if authorized else "rejected",
    )
    message.original_email.save("original.eml", ContentFile(raw_message), save=False)
    try:
        message.save()
    except IntegrityError:
        return EmailMessage.objects.get(account=account, message_id=message_id), False

    max_bytes = int(getattr(settings, "EMAIL_COLLECTION_MAX_ATTACHMENT_BYTES", 25 * 1024 * 1024))
    for index, part in enumerate(parsed.walk()):
        filename = part.get_filename()
        if not filename:
            continue
        payload = part.get_payload(decode=True) or b""
        safe_name = _safe_filename(_header(filename), f"attachment-{index}.bin")
        checksum = hashlib.sha256(payload).hexdigest()
        attachment = EmailAttachment(
            message=message,
            filename=safe_name,
            content_type=part.get_content_type(),
            size_bytes=len(payload),
            checksum_sha256=checksum,
            status="invalid" if len(payload) > max_bytes else "pending",
            error_message=(
                f"Attachment exceeds the {max_bytes}-byte configured limit."
                if len(payload) > max_bytes
                else ""
            ),
        )
        attachment.file.save(safe_name, ContentFile(payload), save=False)
        attachment.save()

    ProcessingHistory.objects.create(
        message=message,
        stage="intake",
        status="rejected" if not authorized else "completed",
        details={"provider_message_id": provider_message_id, "attachment_count": message.attachments.count()},
    )
    if authorized:
        message.status = "queued"
        message.save(update_fields=["status", "updated_at"])
        ProcessingQueue.objects.create(message=message)
    return message, True


# Imported late to keep module imports readable and avoid shadowing the email package.
from django.db import models
