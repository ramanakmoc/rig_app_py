from django.core.management.base import BaseCommand

from email_reports.services.processor import process_pending_queue


class Command(BaseCommand):
    help = "Process pending email report queue items."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        count = process_pending_queue(options["limit"])
        self.stdout.write(self.style.SUCCESS(f"Processed {count} queue item(s)."))

