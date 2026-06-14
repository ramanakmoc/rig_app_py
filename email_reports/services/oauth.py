import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _post_form(url, data):
    request = Request(
        url,
        data=urlencode(data).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def refresh_oauth_token(account, credentials):
    refresh_token = credentials.get("refresh_token")
    client_id = credentials.get("client_id")
    client_secret = credentials.get("client_secret")
    if not refresh_token or not client_id:
        return credentials

    if account.provider == "microsoft365":
        tenant_id = credentials.get("tenant_id", "common")
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": credentials.get(
                "scope", "https://graph.microsoft.com/.default offline_access"
            ),
        }
    elif account.provider == "gmail":
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
    else:
        return credentials

    if client_secret:
        data["client_secret"] = client_secret
    token_data = _post_form(token_url, data)
    credentials.update(token_data)
    account.set_credentials(credentials)
    account.save(update_fields=["encrypted_credentials", "updated_at"])
    return credentials


def access_token(account, force_refresh=False):
    credentials = account.get_credentials()
    if force_refresh or not credentials.get("access_token"):
        credentials = refresh_oauth_token(account, credentials)
    token = credentials.get("access_token")
    if not token:
        raise ValueError(f"No OAuth access token is configured for {account.name}.")
    return token

