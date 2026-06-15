"""
AI/LLM-assisted report extraction (requirement #6 + #16).

This module plugs into the existing classification hook. Set in the environment:

    EMAIL_REPORTS_AI_EXTRACTOR=email_reports.services.ai_extractor.extract
    ANTHROPIC_API_KEY=sk-ant-...

`classify_message()` first runs the deterministic rules pass, then calls
`extract()` with the email content and the rules result. Whatever non-empty
fields this function returns are merged over the rules result, so the AI acts
as an *upgrade* layer on top of rules — never a replacement.

Design rules:
  * This function must NEVER raise. Any failure (no API key, network error,
    bad response) is swallowed and an empty dict is returned, so processing
    degrades gracefully to the rules-only result instead of failing the email.
  * Output is constrained with structured outputs (JSON schema), so the model
    can only return the fields/enums we accept.
  * Known rigs, sites, and contractors from the masters tables are passed in as
    candidate lists, so the model maps free text to the *canonical* names the
    rest of the pipeline (duplicate detection, missing-report matching) expects.
"""
import json
import logging

from django.conf import settings

from .classification import REPORT_TYPES

logger = logging.getLogger(__name__)

DEPARTMENTS = ["HSE", "Operations", "Maintenance", "Logistics"]
PRIORITIES = ["low", "normal", "high", "critical"]

# Keep the prompt bounded regardless of how large an email/attachment is.
_MAX_BODY_CHARS = 6000
_MAX_ATTACHMENT_CHARS = 8000
_MAX_TOTAL_ATTACHMENT_CHARS = 30000
_MAX_CANDIDATES = 300

_SYSTEM_PROMPT = (
    "You extract structured metadata from operational report emails for KRISS "
    "Drilling, an oil & gas drilling contractor. Reports arrive from rig sites, "
    "contractors, and field staff as email body text and/or attachments "
    "(daily rig reports, HSD/diesel, POB/manpower, ILM rig-move, safety, "
    "equipment).\n\n"
    "Rules:\n"
    "- Map rig, site, and contractor to the EXACT canonical value from the "
    "provided candidate lists when the email clearly refers to one. If it does "
    "not clearly match a candidate, return an empty string for that field.\n"
    "- reporting_date is the date the report is ABOUT (the operational day), in "
    "YYYY-MM-DD format — not the date the email was sent. Empty string if "
    "unknown.\n"
    "- priority reflects operational urgency: 'critical' for fatalities, "
    "blowouts, or shutdowns; 'high' for breakdowns, incidents, or overdue "
    "items; otherwise 'normal'.\n"
    "- confidence_score is your overall 0.0-1.0 confidence in the extraction.\n"
    "- Never guess. An empty string is better than a wrong value."
)


def _candidates():
    """Pull canonical rig / site / contractor names from the masters tables."""
    from masters.models import Rig, Vendor, WellLocation

    def _clean(values):
        seen = [v for v in values if v]
        return sorted(set(seen))[:_MAX_CANDIDATES]

    return {
        "rigs": _clean(Rig.objects.values_list("rig_name", flat=True)),
        "sites": _clean(WellLocation.objects.values_list("location", flat=True)),
        "contractors": _clean(Vendor.objects.values_list("vendor_name", flat=True)),
    }


def _build_user_content(payload, candidates):
    attachments = payload.get("attachments") or []
    parts = []
    budget = _MAX_TOTAL_ATTACHMENT_CHARS
    for item in attachments:
        if budget <= 0:
            break
        text = (item.get("text") or "")[:_MAX_ATTACHMENT_CHARS][:budget]
        budget -= len(text)
        parts.append(f"--- attachment: {item.get('filename', '')} ---\n{text}")
    attachment_block = "\n\n".join(parts) or "(no readable attachments)"

    return (
        f"Known rigs: {', '.join(candidates['rigs']) or '(none on file)'}\n"
        f"Known sites: {', '.join(candidates['sites']) or '(none on file)'}\n"
        f"Known contractors: {', '.join(candidates['contractors']) or '(none on file)'}\n\n"
        f"=== EMAIL SUBJECT ===\n{payload.get('subject', '')}\n\n"
        f"=== EMAIL BODY ===\n{(payload.get('body') or '')[:_MAX_BODY_CHARS]}\n\n"
        f"=== ATTACHMENTS ===\n{attachment_block}"
    )


def _schema():
    return {
        "type": "object",
        "properties": {
            "report_type": {"type": "string", "enum": list(REPORT_TYPES.keys()) + [""]},
            "site_name": {"type": "string"},
            "rig_name": {"type": "string"},
            "contractor": {"type": "string"},
            "reporting_date": {"type": "string"},
            "department": {"type": "string", "enum": DEPARTMENTS + [""]},
            "priority": {"type": "string", "enum": PRIORITIES},
            "confidence_score": {"type": "number"},
        },
        "required": [
            "report_type",
            "site_name",
            "rig_name",
            "contractor",
            "reporting_date",
            "department",
            "priority",
            "confidence_score",
        ],
        "additionalProperties": False,
    }


def extract(payload):
    """Return AI-extracted classification fields, or {} on any failure."""
    subject = payload.get("subject") or ""
    body = payload.get("body") or ""
    attachments = payload.get("attachments") or []
    if not (subject or body or attachments):
        return {}

    try:
        import anthropic

        model = getattr(settings, "EMAIL_REPORTS_AI_MODEL", "claude-opus-4-8")
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_user_content(payload, _candidates())}],
            output_config={"format": {"type": "json_schema", "schema": _schema()}},
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        result = json.loads(text)
    except Exception as exc:  # never let AI failure fail the email
        logger.warning("AI extraction skipped (%s): %s", type(exc).__name__, exc)
        return {}

    # Drop a zero/empty confidence so it can't override the rules confidence.
    if not result.get("confidence_score"):
        result.pop("confidence_score", None)
    return result
