from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
from core.config import SETTINGS

def send_via_gmail_smtp(to_email: str, subject: str, body: str) -> str:
    from_addr = SETTINGS.smtp_from.strip()
    app_pw = SETTINGS.smtp_app_password.strip()
    override = (SETTINGS.smtp_to_override or "").strip()
    if override: to_email = override
    if not from_addr or not app_pw:
        raise RuntimeError("SMTP_FROM / SMTP_APP_PASSWORD not configured in .env")

    msg = MIMEText(body, _subtype="plain", _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(from_addr, app_pw)
        server.send_message(msg)

    return f"Sent to {to_email}"
