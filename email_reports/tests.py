import tempfile
from datetime import time, timedelta
from email.message import EmailMessage as MimeMessage

from django.test import TestCase, override_settings
from django.utils import timezone

from .models import EmailAccount, EmailMessage, ExpectedReport, MissingReport, SenderRegistry
from .services.intake import ingest_raw_message, sender_authorization
from .services.missing import check_expected_reports
from .services.processor import process_pending_queue


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="email-report-tests-")


def sample_message(message_id="report-1@example.com", attachment=True):
    message = MimeMessage()
    message["From"] = "Site Reporter <reporter@approved.example>"
    message["To"] = "reports@example.com"
    message["Subject"] = "Daily Rig Report PPE-1 Assam 12 June 2026"
    message["Message-ID"] = f"<{message_id}>"
    message["Date"] = "Fri, 12 Jun 2026 17:00:00 +0530"
    message.set_content("Daily drilling report for Assam site and PPE-1.")
    if attachment:
        message.add_attachment(
            b"field,value\noperating_hours,20\n",
            maintype="text",
            subtype="csv",
            filename="daily-report.csv",
        )
    return message.as_bytes()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class EmailIntakeTests(TestCase):
    def setUp(self):
        self.account = EmailAccount.objects.create(
            name="Reports",
            provider="imap",
            transport="imap",
            auth_method="password",
            email_address="reports@example.com",
        )
        SenderRegistry.objects.create(
            match_type="domain",
            value="approved.example",
            status="approved",
            site_name="Assam",
        )

    def test_sender_registry_approval_and_block_override(self):
        approved, _ = sender_authorization("reporter@approved.example")
        self.assertTrue(approved)
        SenderRegistry.objects.create(
            match_type="email", value="reporter@approved.example", status="blocked"
        )
        approved, _ = sender_authorization("reporter@approved.example")
        self.assertFalse(approved)

    def test_ingestion_is_idempotent_and_creates_queue(self):
        message, created = ingest_raw_message(self.account, "remote-1", sample_message())
        self.assertTrue(created)
        self.assertTrue(message.is_authorized_sender)
        self.assertEqual(message.attachments.count(), 1)
        self.assertEqual(message.status, "queued")
        duplicate, created = ingest_raw_message(self.account, "remote-1", sample_message())
        self.assertFalse(created)
        self.assertEqual(duplicate.pk, message.pk)

    def test_csv_report_is_classified_and_processed(self):
        message, _ = ingest_raw_message(self.account, "remote-2", sample_message("report-2@example.com"))
        self.assertEqual(process_pending_queue(), 1)
        message.refresh_from_db()
        self.assertEqual(message.status, "processed")
        self.assertEqual(message.site_name, "Assam")
        self.assertEqual(message.report_type, "Daily Rig Report")
        self.assertEqual(str(message.reporting_date), "2026-06-12")
        self.assertEqual(message.attachments.get().status, "extracted")


class MissingReportTests(TestCase):
    def test_overdue_schedule_creates_and_then_resolves_alert(self):
        now = timezone.now()
        schedule = ExpectedReport.objects.create(
            name="Assam Daily Rig Report",
            site_name="Assam",
            report_type="Daily Rig Report",
            frequency="daily",
            due_time=(timezone.localtime(now) - timedelta(minutes=5)).time(),
        )
        result = check_expected_reports(now)
        self.assertGreaterEqual(result["created"], 1)
        missing = MissingReport.objects.filter(
            expected_report=schedule, reporting_date=timezone.localdate(now)
        ).get()
        account = EmailAccount.objects.create(
            name="Reports", provider="imap", email_address="reports@example.com"
        )
        EmailMessage.objects.create(
            account=account,
            message_id="<late@example.com>",
            sender_email="reporter@example.com",
            original_email="email_reports/test.eml",
            status="processed",
            site_name="Assam",
            report_type="Daily Rig Report",
            reporting_date=timezone.localdate(now),
        )
        result = check_expected_reports(now + timedelta(minutes=1))
        missing.refresh_from_db()
        self.assertEqual(result["resolved"], 1)
        self.assertEqual(missing.status, "received_late")
