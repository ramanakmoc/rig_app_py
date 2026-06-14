from django.utils import timezone

from email_reports.models import EmailAccount

from .intake import ingest_raw_message
from .notifications import send_operational_alert
from .providers import collector_for


def collect_account(account):
    account.last_checked_at = timezone.now()
    account.last_error = ""
    account.save(update_fields=["last_checked_at", "last_error", "updated_at"])
    collected = 0
    try:
        for provider_message_id, raw_message in collector_for(account).collect(account):
            message, created = ingest_raw_message(account, provider_message_id, raw_message)
            if created:
                collected += 1
                if not message.is_authorized_sender:
                    send_operational_alert(
                        "unauthorized_sender",
                        f"Unauthorized report sender: {message.sender_email}",
                        f"Subject: {message.subject}\nMailbox: {account.email_address}",
                        message=message,
                    )
        account.last_success_at = timezone.now()
        account.last_error = ""
        account.save(update_fields=["last_success_at", "last_error", "updated_at"])
        return collected
    except Exception as exc:
        account.last_error = str(exc)[:4000]
        account.save(update_fields=["last_error", "updated_at"])
        send_operational_alert(
            "mailbox_failure",
            f"Mailbox collection failed: {account.name}",
            f"Mailbox: {account.email_address}\nError: {exc}",
        )
        raise


def active_accounts(account_id=None):
    queryset = EmailAccount.objects.filter(is_active=True)
    if account_id:
        queryset = queryset.filter(pk=account_id)
    return queryset.order_by("name")

