import time

from django.core.management.base import BaseCommand

from email_reports.services.collection import active_accounts, collect_account
from email_reports.services.missing import check_expected_reports
from email_reports.services.processor import process_pending_queue


class Command(BaseCommand):
    help = "Continuously collect and process reports from configured email accounts."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Run one collection cycle and exit.")
        parser.add_argument("--account", type=int, help="Only collect one EmailAccount primary key.")
        parser.add_argument("--queue-limit", type=int, default=50)

    def handle(self, *args, **options):
        next_poll = {}
        while True:
            accounts = list(active_accounts(options.get("account")))
            current = time.monotonic()
            for account in accounts:
                if not options["once"] and current < next_poll.get(account.pk, 0):
                    continue
                try:
                    count = collect_account(account)
                    self.stdout.write(self.style.SUCCESS(f"{account.name}: collected {count} new message(s)."))
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f"{account.name}: {exc}"))
                next_poll[account.pk] = time.monotonic() + max(account.polling_interval_seconds, 10)
            processed = process_pending_queue(options["queue_limit"])
            missing = check_expected_reports()
            self.stdout.write(
                f"Processed {processed}; missing created {missing['created']}, resolved {missing['resolved']}."
            )
            if options["once"]:
                break
            next_due = min(next_poll.values(), default=time.monotonic() + 60)
            time.sleep(max(min(next_due - time.monotonic(), 10), 1))
