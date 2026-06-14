from django.core.management.base import BaseCommand

from email_reports.services.missing import check_expected_reports


class Command(BaseCommand):
    help = "Detect overdue expected reports and generate notifications."

    def handle(self, *args, **options):
        result = check_expected_reports()
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {result['created']} missing report alert(s); resolved {result['resolved']}."
            )
        )
