from django.apps import AppConfig


class EmailReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "email_reports"
    verbose_name = "Email Report Collection"

    def ready(self):
        from . import checks  # noqa: F401
