import re
from datetime import date

from dateutil import parser as date_parser
from django.conf import settings
from django.utils.module_loading import import_string

from masters.models import Rig, Vendor, WellLocation


REPORT_TYPES = {
    "Daily Rig Report": [
        "daily rig report", "drr", "daily drilling report",
        # KRISS naming conventions
        "daily report", "daily all reports", "dcr report", "dcr",
        "ro daily", "all reports of rig",
    ],
    "HSD Report": ["hsd report", "diesel report", "fuel report", "hsd"],
    "POB Report": ["pob report", "personnel on board", "manpower report", "pob"],
    "ILM Report": ["ilm report", "inter location move", "rig move report", "ilm"],
    "Safety Report": ["safety report", "hse report", "incident report", "near miss"],
    "Equipment Report": ["equipment report", "maintenance report", "breakdown report"],
}


def _find_known_value(values, text):
    lower_text = text.lower()
    for value in sorted((value for value in values if value), key=len, reverse=True):
        if value.lower() in lower_text:
            return value
    return ""


def _reporting_date(text):
    patterns = [
        r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b",
        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        try:
            parsed = date_parser.parse(match.group(0), dayfirst=True, fuzzy=False).date()
            if date(2000, 1, 1) <= parsed <= date.today():
                return parsed
        except (ValueError, OverflowError):
            continue
    return None


def classify_message(message):
    attachment_text = "\n".join(
        f"{attachment.filename}\n{attachment.extracted_text[:100000]}"
        for attachment in message.attachments.all()
    )
    text = f"{message.subject}\n{message.body_text}\n{attachment_text}"
    lower_text = text.lower()
    report_type = ""
    for candidate, keywords in REPORT_TYPES.items():
        if any(keyword in lower_text for keyword in keywords):
            report_type = candidate
            break

    rig = _find_known_value(Rig.objects.values_list("rig_name", flat=True), text)
    site = message.site_name or _find_known_value(
        WellLocation.objects.values_list("location", flat=True), text
    )
    contractor = message.contractor or _find_known_value(
        Vendor.objects.values_list("vendor_name", flat=True), text
    )
    reporting_date = _reporting_date(text) or (message.sent_at.date() if message.sent_at else None)
    department = message.department
    if not department:
        department_keywords = {
            "HSE": ["hse", "safety", "incident"],
            "Operations": ["rig", "drilling", "operation"],
            "Maintenance": ["maintenance", "breakdown", "repair"],
            "Logistics": ["logistics", "transport", "move"],
        }
        department = next(
            (name for name, words in department_keywords.items() if any(word in lower_text for word in words)),
            "",
        )

    priority = "normal"
    if any(word in lower_text for word in ("critical", "emergency", "fatal", "shutdown")):
        priority = "critical"
    elif any(word in lower_text for word in ("urgent", "breakdown", "incident", "overdue")):
        priority = "high"

    fields = [site, contractor, report_type, rig, reporting_date, department]
    confidence = sum(bool(value) for value in fields) / len(fields)
    result = {
        "site_name": site,
        "contractor": contractor,
        "report_type": report_type,
        "rig_name": rig,
        "reporting_date": reporting_date.isoformat() if reporting_date else None,
        "department": department,
        "priority": priority,
        "confidence_score": round(confidence, 4),
        "method": "rules",
    }

    extractor_path = getattr(settings, "EMAIL_REPORTS_AI_EXTRACTOR", "").strip()
    if extractor_path:
        ai_result = import_string(extractor_path)(
            {
                "subject": message.subject,
                "body": message.body_text,
                "attachments": [
                    {"filename": item.filename, "text": item.extracted_text[:100000]}
                    for item in message.attachments.all()
                ],
                "current": result,
            }
        )
        if isinstance(ai_result, dict):
            result.update({key: value for key, value in ai_result.items() if value not in (None, "")})
            result["method"] = "ai+rules"
    return result

