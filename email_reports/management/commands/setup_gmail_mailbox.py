"""
One-time setup command: creates the Gmail IMAP EmailAccount for reportskrissdrilling@gmail.com
and seeds the SenderRegistry with approved krissdrilling.com senders.

Usage:
    python manage.py setup_gmail_mailbox --password "xxxx xxxx xxxx xxxx"

Get the app password from:
  Google Account → Security → 2-Step Verification → App passwords → Mail
"""
import imaplib
import ssl

from django.core.management.base import BaseCommand, CommandError

from email_reports.models import EmailAccount, SenderRegistry


ACCOUNT_NAME = "KRISS Drilling Reports Inbox"
EMAIL_ADDRESS = "reportskrissdrilling@gmail.com"

APPROVED_DOMAINS = [
    "krissdrilling.com",
    "cont-tech.com.sg",
]

APPROVED_EMAILS = []


class Command(BaseCommand):
    help = "Create the reportskrissdrilling@gmail.com IMAP mailbox and seed sender approvals."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help="Gmail App Password for reportskrissdrilling@gmail.com (16-char, spaces ok)",
        )
        parser.add_argument(
            "--folder",
            default="INBOX",
            help="Mailbox folder to monitor (default: INBOX)",
        )
        parser.add_argument(
            "--no-test",
            action="store_true",
            help="Skip live IMAP connection test.",
        )

    def handle(self, *args, **options):
        password = options["password"].replace(" ", "")
        folder = options["folder"]

        if not options["no_test"]:
            self.stdout.write("Testing IMAP connection...")
            try:
                ctx = ssl.create_default_context()
                client = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=ctx)
                client.login(EMAIL_ADDRESS, password)
                client.logout()
                self.stdout.write(self.style.SUCCESS("  IMAP login OK."))
            except imaplib.IMAP4.error as exc:
                raise CommandError(
                    f"IMAP login failed: {exc}\n"
                    "Make sure:\n"
                    "  1. IMAP is enabled in Gmail Settings → See all settings → Forwarding and POP/IMAP\n"
                    "  2. You are using a Gmail App Password, not your regular password\n"
                    "     (Google Account → Security → 2-Step Verification → App passwords)"
                ) from exc

        account, created = EmailAccount.objects.get_or_create(
            name=ACCOUNT_NAME,
            defaults={
                "provider": "gmail",
                "transport": "imap",
                "auth_method": "password",
                "email_address": EMAIL_ADDRESS,
                "username": EMAIL_ADDRESS,
                "host": "imap.gmail.com",
                "port": 993,
                "folder": folder,
                "use_ssl": True,
                "mark_as_read": False,
                "polling_interval_seconds": 120,
                "is_active": True,
            },
        )
        account.set_credentials({"password": password})
        account.save()
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"  {verb} EmailAccount: {ACCOUNT_NAME}"))

        seeded = 0
        for domain in APPROVED_DOMAINS:
            _, was_created = SenderRegistry.objects.get_or_create(
                match_type="domain",
                value=domain,
                defaults={
                    "status": "approved",
                    "site_name": "",
                    "contractor": "KRISS Drilling" if "krissdrilling" in domain else "",
                    "is_active": True,
                    "notes": "Auto-seeded by setup_gmail_mailbox",
                },
            )
            if was_created:
                seeded += 1

        for email in APPROVED_EMAILS:
            _, was_created = SenderRegistry.objects.get_or_create(
                match_type="email",
                value=email,
                defaults={"status": "approved", "is_active": True},
            )
            if was_created:
                seeded += 1

        self.stdout.write(self.style.SUCCESS(f"  Seeded {seeded} new SenderRegistry entries."))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Setup complete. Next steps:"))
        self.stdout.write("  1. Collect existing emails (one-off run):")
        self.stdout.write("       python manage.py monitor_email_reports --once")
        self.stdout.write("  2. Start continuous monitoring:")
        self.stdout.write("       python manage.py monitor_email_reports")
        self.stdout.write("  3. View results at: http://localhost:8000/email-collection/")
        self.stdout.write("")
        self.stdout.write("  To approve additional senders, go to:")
        self.stdout.write("    Django Admin → Email Reports → Sender Registry")
