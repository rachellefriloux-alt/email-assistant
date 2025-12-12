
import base64
import json
import logging
import os
from pathlib import Path
from typing import List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PATH = PROJECT_ROOT / "sample_emails.json"
TOKEN_PATH = PROJECT_ROOT / "token.json"
CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "credentials.json")

log = logging.getLogger(__name__)


def authenticate_gmail():
    """Perform OAuth flow and return an authenticated Gmail service client."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                log.info("gmail token refreshed")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                log.info("gmail token generated via oauth flow")
            TOKEN_PATH.write_text(creds.to_json())
        except Exception as exc:
            log.exception("gmail auth failed")
            raise
    service = build('gmail', 'v1', credentials=creds)
    return service


def fetch_emails(service, max_results: int = 50) -> List[dict]:
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    email_data: List[dict] = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet', '')
        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown sender')
        body_text, body_html = _extract_body(payload)
        body_content = body_text or body_html
        labels = msg_detail.get('labelIds', [])
        email_data.append({
            'subject': subject,
            'snippet': snippet,
            'body_text': body_content,
            'from_email': sender,
            'gmail_id': msg['id'],
            'is_read': 'UNREAD' not in labels,
            'is_starred': 'STARRED' in labels,
        })
    return email_data


def delete_emails(service, gmail_ids: List[str]) -> None:
    for gid in gmail_ids:
        try:
            service.users().messages().trash(userId='me', id=gid).execute()
        except Exception:
            # Keep best-effort; log in real impl
            continue


def move_emails_to_label(service, gmail_ids: List[str], label_id: str) -> None:
    for gid in gmail_ids:
        try:
            service.users().messages().modify(userId='me', id=gid, body={"addLabelIds": [label_id]}).execute()
        except Exception:
            continue


def load_sample_emails(limit: int = 50) -> List[dict]:
    """Load sample emails from disk for offline testing."""
    if not SAMPLE_PATH.exists():
        return []
    with SAMPLE_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    # add fake ids and from addresses
    enriched = []
    for idx, item in enumerate(data[:limit]):
        enriched.append({
            **item,
            "gmail_id": f"sample-{idx}",
            "from_email": item.get("from_email", "sample@example.com"),
            "body_text": item.get("body_text", item.get("snippet", "")),
        })
    return enriched


def _extract_body(payload: dict) -> Tuple[str, str]:
    """Extract plain text and HTML bodies from a Gmail message payload."""
    if not payload:
        return "", ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")

    plain_parts: List[str] = []
    html_parts: List[str] = []

    if data:
        try:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            if mime_type.startswith("text/plain"):
                plain_parts.append(decoded)
            elif mime_type.startswith("text/html"):
                html_parts.append(decoded)
            else:
                plain_parts.append(decoded)
        except Exception:
            pass

    for part in payload.get("parts") or []:
        text_part, html_part = _extract_body(part)
        if text_part:
            plain_parts.append(text_part)
        if html_part:
            html_parts.append(html_part)

    if plain_parts:
        return "\n".join(plain_parts), ("\n".join(html_parts) if html_parts else "")
    if html_parts:
        return "", "\n".join(html_parts)
    return "", ""
