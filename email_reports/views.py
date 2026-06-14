from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.decorators import supervisor_required

from .models import EmailAccount, EmailAttachment, EmailMessage, MissingReport, ProcessingQueue


@login_required
def dashboard(request):
    status_filter = request.GET.get("status", "").strip()
    query = request.GET.get("q", "").strip()
    message_queryset = EmailMessage.objects.select_related("account").annotate(
        attachment_count=Count("attachments")
    )
    if status_filter:
        message_queryset = message_queryset.filter(status=status_filter)
    if query:
        message_queryset = message_queryset.filter(
            Q(subject__icontains=query)
            | Q(sender_email__icontains=query)
            | Q(site_name__icontains=query)
            | Q(rig_name__icontains=query)
            | Q(report_type__icontains=query)
        )
    today = timezone.localdate()
    context = {
        "page_title": "Email Report Collection",
        "messages_list": message_queryset[:100],
        "accounts": EmailAccount.objects.all(),
        "missing_reports": MissingReport.objects.filter(status="missing").select_related("expected_report")[:20],
        "status_choices": EmailMessage.STATUS_CHOICES,
        "filters": {"status": status_filter, "q": query},
        "stats": {
            "received_today": EmailMessage.objects.filter(received_at__date=today).count(),
            "processed_today": EmailMessage.objects.filter(processed_at__date=today, status="processed").count(),
            "needs_review": EmailMessage.objects.filter(status="review").count(),
            "failed": EmailMessage.objects.filter(status="failed").count(),
            "missing": MissingReport.objects.filter(status="missing").count(),
            "queued": ProcessingQueue.objects.filter(status__in=["pending", "processing"]).count(),
        },
    }
    return render(request, "email_reports/dashboard.html", context)


@login_required
def message_detail(request, reference_number):
    message = get_object_or_404(
        EmailMessage.objects.select_related("account", "duplicate_of").prefetch_related(
            "attachments", "history", "notifications"
        ),
        reference_number=reference_number,
    )
    return render(
        request,
        "email_reports/message_detail.html",
        {"page_title": "Email Report Detail", "email_message": message},
    )


@login_required
def download_original(request, reference_number):
    message = get_object_or_404(EmailMessage, reference_number=reference_number)
    return FileResponse(
        message.original_email.open("rb"),
        as_attachment=True,
        filename=f"{message.reference_number}.eml",
        content_type="message/rfc822",
    )


@login_required
def download_attachment(request, reference_number, attachment_id):
    attachment = get_object_or_404(
        EmailAttachment,
        pk=attachment_id,
        message__reference_number=reference_number,
    )
    return FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.filename,
        content_type=attachment.content_type or "application/octet-stream",
    )


@supervisor_required
def review_message(request, reference_number):
    if request.method != "POST":
        return redirect("email_reports:message_detail", reference_number=reference_number)
    message = get_object_or_404(EmailMessage, reference_number=reference_number)
    message.site_name = request.POST.get("site_name", "").strip()
    message.contractor = request.POST.get("contractor", "").strip()
    message.report_type = request.POST.get("report_type", "").strip()
    message.rig_name = request.POST.get("rig_name", "").strip()
    message.department = request.POST.get("department", "").strip()
    message.priority = request.POST.get("priority", "normal")
    message.reporting_date = request.POST.get("reporting_date") or None
    message.status = "processed"
    message.validation_errors = []
    message.processed_at = timezone.now()
    message.save()
    message.history.create(
        stage="human_review",
        status="completed",
        details={"reviewed_by": request.user.username},
    )
    messages.success(request, "Email report review completed.")
    return redirect("email_reports:message_detail", reference_number=reference_number)
