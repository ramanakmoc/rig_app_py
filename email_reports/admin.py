from django import forms
from django.contrib import admin

from .models import (
    EmailAccount,
    EmailAttachment,
    EmailMessage,
    ExpectedReport,
    MissingReport,
    NotificationLog,
    ProcessingHistory,
    ProcessingQueue,
    SenderRegistry,
)


class EmailAccountAdminForm(forms.ModelForm):
    credential_payload = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text=(
            "JSON stored encrypted. Password example: {\"password\":\"...\"}. "
            "OAuth2 may include access_token, refresh_token, client_id, client_secret and tenant_id. "
            "Leave blank to preserve the current credentials."
        ),
    )

    class Meta:
        model = EmailAccount
        fields = "__all__"

    def clean_credential_payload(self):
        value = self.cleaned_data["credential_payload"].strip()
        if not value:
            return None
        import json

        try:
            payload = json.loads(value)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Enter a valid JSON object.") from exc
        if not isinstance(payload, dict):
            raise forms.ValidationError("Credential payload must be a JSON object.")
        return payload

    def save(self, commit=True):
        instance = super().save(commit=False)
        payload = self.cleaned_data.get("credential_payload")
        if payload is not None:
            instance.set_credentials(payload)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    form = EmailAccountAdminForm
    list_display = ("name", "provider", "transport", "email_address", "is_active", "last_success_at")
    list_filter = ("provider", "transport", "auth_method", "is_active")
    readonly_fields = ("last_checked_at", "last_success_at", "last_error", "created_at", "updated_at")


@admin.register(SenderRegistry)
class SenderRegistryAdmin(admin.ModelAdmin):
    list_display = ("value", "match_type", "status", "site_name", "contractor", "is_active")
    list_filter = ("match_type", "status", "is_active")
    search_fields = ("value", "site_name", "contractor")


class AttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    fields = ("filename", "content_type", "size_bytes", "checksum_sha256", "status")
    readonly_fields = fields
    can_delete = False


class HistoryInline(admin.TabularInline):
    model = ProcessingHistory
    extra = 0
    readonly_fields = ("stage", "status", "details", "error_message", "created_at")
    can_delete = False


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "received_at",
        "sender_email",
        "subject",
        "site_name",
        "report_type",
        "status",
        "confidence_score",
    )
    list_filter = ("status", "is_authorized_sender", "priority", "account")
    search_fields = ("message_id", "sender_email", "subject", "site_name", "rig_name", "report_type")
    readonly_fields = (
        "reference_number",
        "message_id",
        "original_email",
        "raw_headers",
        "classification_result",
        "extraction_result",
        "created_at",
        "updated_at",
    )
    inlines = (AttachmentInline, HistoryInline)


@admin.register(ExpectedReport)
class ExpectedReportAdmin(admin.ModelAdmin):
    list_display = ("name", "site_name", "contractor", "report_type", "frequency", "due_time", "is_active")
    list_filter = ("frequency", "is_active")
    search_fields = ("name", "site_name", "contractor", "report_type", "rig_name")


@admin.register(MissingReport)
class MissingReportAdmin(admin.ModelAdmin):
    list_display = ("expected_report", "reporting_date", "due_at", "status", "detected_at")
    list_filter = ("status", "reporting_date")


admin.site.register(ProcessingQueue)
admin.site.register(ProcessingHistory)
admin.site.register(NotificationLog)
