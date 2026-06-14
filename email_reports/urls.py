from django.urls import path

from . import views


app_name = "email_reports"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("messages/<uuid:reference_number>/", views.message_detail, name="message_detail"),
    path("messages/<uuid:reference_number>/original/", views.download_original, name="download_original"),
    path(
        "messages/<uuid:reference_number>/attachments/<int:attachment_id>/",
        views.download_attachment,
        name="download_attachment",
    ),
    path("messages/<uuid:reference_number>/review/", views.review_message, name="review_message"),
]
