"""Send email via Gmail API using a saved OAuth token.json.

This module reads credentials from a `token.json` created by the
InstalledAppFlow (we saved this earlier) and uses the Gmail API to send
messages on behalf of the authenticated user.

Functions:
  send_message(token_path, to, subject, body, from_email=None)

Notes:
 - Expects `token.json` at project root (the same path used earlier).
 - Requires `google-api-python-client` and `google-auth`.
"""
from __future__ import annotations
import json
import os
import base64
from email.mime.text import MIMEText
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def load_token(token_path: str) -> Credentials:
    with open(token_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    return creds


def create_message(to: str, subject: str, body_text: str, from_email: Optional[str] = None) -> dict:
    msg = MIMEText(body_text, "plain", "utf-8")
    if from_email:
        msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_message(token_path: str, to: str, subject: str, body_text: str, from_email: Optional[str] = None) -> dict:
    """Send an email using the Gmail API. Returns the API response dict on success.

    Raises exceptions from googleapiclient if something fails.
    """
    creds = load_token(token_path)
    service = build("gmail", "v1", credentials=creds)
    message = create_message(to, subject, body_text, from_email=from_email)
    res = service.users().messages().send(userId="me", body=message).execute()
    return res
