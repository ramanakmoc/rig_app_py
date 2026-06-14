from django.conf import settings
from django.core.checks import Error, register


@register()
def email_collection_security_checks(app_configs, **kwargs):
    errors = []
    if not settings.DEBUG and not getattr(settings, "EMAIL_COLLECTION_FERNET_KEY", ""):
        errors.append(
            Error(
                "EMAIL_COLLECTION_FERNET_KEY is required when DEBUG is False.",
                hint="Generate a dedicated Fernet key and set it in the deployment environment.",
                id="email_reports.E001",
            )
        )
    return errors
