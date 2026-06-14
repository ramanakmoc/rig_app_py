import base64
import hashlib
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _fernet():
    from cryptography.fernet import Fernet

    configured_key = getattr(settings, "EMAIL_COLLECTION_FERNET_KEY", "").strip()
    if configured_key:
        key = configured_key.encode("ascii")
    else:
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
    try:
        return Fernet(key)
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            "EMAIL_COLLECTION_FERNET_KEY must be a valid Fernet key."
        ) from exc


def encrypt_json(value):
    if not value:
        return ""
    payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(payload).decode("ascii")


def decrypt_json(value):
    if not value:
        return {}
    try:
        from cryptography.fernet import InvalidToken

        payload = _fernet().decrypt(value.encode("ascii"))
        return json.loads(payload.decode("utf-8"))
    except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Stored mailbox credentials cannot be decrypted.") from exc
