import base64
import imaplib
import json
import ssl
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .oauth import access_token


def _api_request(account, url, method="GET", payload=None, retry=True):
    token = access_token(account)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            return response.read(), dict(response.headers)
    except HTTPError as exc:
        if exc.code == 401 and retry:
            access_token(account, force_refresh=True)
            return _api_request(account, url, method=method, payload=payload, retry=False)
        raise


class ImapCollector:
    DEFAULT_HOSTS = {
        "gmail": "imap.gmail.com",
        "microsoft365": "outlook.office365.com",
    }

    def collect(self, account):
        host = account.host or self.DEFAULT_HOSTS.get(account.provider)
        if not host:
            raise ValueError("An IMAP host is required.")
        connection_class = imaplib.IMAP4_SSL if account.use_ssl else imaplib.IMAP4
        kwargs = {"host": host, "port": account.port}
        if account.use_ssl:
            kwargs["ssl_context"] = ssl.create_default_context()
        client = connection_class(**kwargs)
        credentials = account.get_credentials()
        username = account.username or account.email_address
        if account.auth_method == "oauth2":
            token = access_token(account)
            auth_string = f"user={username}\x01auth=Bearer {token}\x01\x01"
            client.authenticate("XOAUTH2", lambda _: auth_string.encode("utf-8"))
        else:
            password = credentials.get("password")
            if not password:
                raise ValueError("No mailbox password is configured.")
            client.login(username, password)

        try:
            status, _ = client.select(account.folder, readonly=not account.mark_as_read)
            if status != "OK":
                raise RuntimeError(f"Cannot select mailbox folder {account.folder}.")
            start_uid = account.last_uid + 1
            status, data = client.uid("search", None, f"UID {start_uid}:*")
            if status != "OK":
                raise RuntimeError("IMAP UID search failed.")
            for uid_bytes in (data[0] or b"").split():
                uid = int(uid_bytes)
                status, message_data = client.uid("fetch", uid_bytes, "(RFC822)")
                if status != "OK":
                    continue
                raw = next(
                    (part[1] for part in message_data if isinstance(part, tuple) and len(part) > 1),
                    None,
                )
                if raw:
                    yield str(uid), raw
                    account.last_uid = max(account.last_uid, uid)
                    account.save(update_fields=["last_uid", "updated_at"])
        finally:
            try:
                client.close()
            except imaplib.IMAP4.error:
                pass
            client.logout()


class MicrosoftGraphCollector:
    base_url = "https://graph.microsoft.com/v1.0"

    def collect(self, account):
        owner = f"users/{quote(account.email_address, safe='')}" if account.is_shared_mailbox else "me"
        folder = quote(account.folder or "inbox", safe="")
        query = urlencode({"$filter": "isRead eq false", "$top": "50", "$select": "id"})
        url = account.sync_cursor or f"{self.base_url}/{owner}/mailFolders/{folder}/messages?{query}"
        while url:
            body, _ = _api_request(account, url)
            page = json.loads(body.decode("utf-8"))
            for item in page.get("value", []):
                remote_id = item["id"]
                mime_url = f"{self.base_url}/{owner}/messages/{quote(remote_id, safe='')}/$value"
                raw, _ = _api_request(account, mime_url)
                yield remote_id, raw
                if account.mark_as_read:
                    _api_request(
                        account,
                        f"{self.base_url}/{owner}/messages/{quote(remote_id, safe='')}",
                        method="PATCH",
                        payload={"isRead": True},
                    )
            url = page.get("@odata.nextLink")


class GmailApiCollector:
    base_url = "https://gmail.googleapis.com/gmail/v1/users/me"

    def collect(self, account):
        query = urlencode({"q": "is:unread", "maxResults": "100"})
        url = f"{self.base_url}/messages?{query}"
        while url:
            body, _ = _api_request(account, url)
            page = json.loads(body.decode("utf-8"))
            for item in page.get("messages", []):
                remote_id = item["id"]
                raw_body, _ = _api_request(
                    account, f"{self.base_url}/messages/{quote(remote_id, safe='')}?format=raw"
                )
                payload = json.loads(raw_body.decode("utf-8"))
                raw = base64.urlsafe_b64decode(payload["raw"] + "===")
                yield remote_id, raw
                if account.mark_as_read:
                    _api_request(
                        account,
                        f"{self.base_url}/messages/{quote(remote_id, safe='')}/modify",
                        method="POST",
                        payload={"removeLabelIds": ["UNREAD"]},
                    )
            page_token = page.get("nextPageToken")
            url = (
                f"{self.base_url}/messages?{query}&pageToken={quote(page_token)}"
                if page_token
                else ""
            )


def collector_for(account):
    if account.transport == "graph":
        return MicrosoftGraphCollector()
    if account.transport == "gmail_api":
        return GmailApiCollector()
    return ImapCollector()
