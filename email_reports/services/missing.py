from datetime import datetime, timedelta

from django.utils import timezone

from email_reports.models import EmailMessage, ExpectedReport, MissingReport

from .notifications import send_operational_alert


def _is_due_on(schedule, reporting_date):
    if schedule.frequency == "daily":
        return not schedule.weekdays or reporting_date.isoweekday() in schedule.weekdays
    if schedule.frequency == "weekly":
        weekdays = schedule.weekdays or [7]
        return reporting_date.isoweekday() in weekdays
    target_day = schedule.day_of_month or 1
    return reporting_date.day == target_day


def _matching_message(schedule, reporting_date):
    queryset = EmailMessage.objects.filter(
        reporting_date=reporting_date,
        site_name__iexact=schedule.site_name,
        report_type__iexact=schedule.report_type,
        status__in=["processed", "review"],
    )
    if schedule.contractor:
        queryset = queryset.filter(contractor__iexact=schedule.contractor)
    if schedule.rig_name:
        queryset = queryset.filter(rig_name__iexact=schedule.rig_name)
    return queryset.order_by("received_at").first()


def check_expected_reports(at=None):
    at = at or timezone.now()
    local_at = timezone.localtime(at)
    created_count = 0
    resolved_count = 0
    for schedule in ExpectedReport.objects.filter(is_active=True):
        # Include yesterday so reports arriving after midnight can resolve an existing alert.
        for reporting_date in [local_at.date() - timedelta(days=1), local_at.date()]:
            if not _is_due_on(schedule, reporting_date):
                continue
            due_at = timezone.make_aware(
                datetime.combine(reporting_date, schedule.due_time), timezone.get_current_timezone()
            ) + timedelta(minutes=schedule.grace_minutes)
            existing_missing = MissingReport.objects.filter(
                expected_report=schedule, reporting_date=reporting_date
            ).first()
            received = _matching_message(schedule, reporting_date)
            if received and existing_missing and existing_missing.status == "missing":
                existing_missing.status = "received_late"
                existing_missing.received_message = received
                existing_missing.resolved_at = at
                existing_missing.save(
                    update_fields=["status", "received_message", "resolved_at"]
                )
                resolved_count += 1
                continue
            if received or at < due_at or existing_missing:
                continue
            missing = MissingReport.objects.create(
                expected_report=schedule,
                reporting_date=reporting_date,
                due_at=due_at,
            )
            created_count += 1
            recipients = schedule.notification_recipients
            send_operational_alert(
                "missing_report",
                f"Missing report: {schedule.name} for {reporting_date:%Y-%m-%d}",
                (
                    f"Expected report: {schedule.name}\n"
                    f"Site: {schedule.site_name}\n"
                    f"Contractor: {schedule.contractor or 'Any'}\n"
                    f"Report type: {schedule.report_type}\n"
                    f"Due: {timezone.localtime(due_at):%Y-%m-%d %H:%M %Z}"
                ),
                missing_report=missing,
                recipients=recipients or None,
            )
    return {"created": created_count, "resolved": resolved_count}

