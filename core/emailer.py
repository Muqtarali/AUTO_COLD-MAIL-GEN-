# core/emailer.py
import os
import smtplib
import socket
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_smtp(smtp_from, smtp_password, smtp_to, subject, body):
    """Send via Gmail SMTP using provided credentials."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    if not smtp_from or not smtp_password:
        return False, "SMTP Error: Missing smtp_from or smtp_password"
    if not smtp_to:
        return False, "SMTP Error: Missing recipient address"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = smtp_to

        part_text = MIMEText(body or "", "plain", "utf-8")
        part_html = MIMEText(f"<html><body>{(body or '').replace(chr(10), '<br>')}</body></html>", "html", "utf-8")
        msg.attach(part_text)
        msg.attach(part_html)

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(smtp_from, smtp_password)

        response = server.sendmail(smtp_from, [smtp_to], msg.as_string())
        server.quit()

        if response:
            return False, f"SMTP per-recipient error: {response}"

        return True, None

    except smtplib.SMTPAuthenticationError as e:
        code = getattr(e, "smtp_code", "AUTH")
        err = getattr(e, "smtp_error", b"").decode(errors="ignore")
        return False, f"SMTPAuthenticationError [{code}]: {err}"
    except smtplib.SMTPResponseException as e:
        code = getattr(e, "smtp_code", "RESP")
        err = getattr(e, "smtp_error", b"").decode(errors="ignore")
        return False, f"SMTPResponseException [{code}]: {err}"
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError) as e:
        return False, f"SMTP connection error: {e}"
    except (socket.timeout, ssl.SSLError) as e:
        return False, f"TLS/Network error: {e}"
    except Exception as e:
        return False, f"Unhandled SMTP error: {e}"


def send_email(smtp_from, smtp_password, smtp_to, subject, body):
    """Unified send function: Use SMTP send directly.
    
    Gmail API with token.json is disabled to avoid authentication issues.

    Returns (True, None) on success, (False, error_message) on failure.
    """
    try:
        # Use SMTP directly - more reliable than Gmail API with token management
        return send_email_smtp(smtp_from, smtp_password, smtp_to, subject, body)
    except Exception as e:
        return False, f"Unhandled error in send_email: {e}"
