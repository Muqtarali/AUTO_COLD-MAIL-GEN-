"""Small runner that sends a test email using `core.gmail_send.send_message`.

It will prefer `SMTP_TO_OVERRIDE` from `.env` if set, otherwise `SMTP_FROM`.
If neither exists, it will fail and print instructions.

Run from the project root:
  python core/send_gmail_test.py
"""
import os
from pathlib import Path
import sys

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.gmail_send import send_message


def load_env_file(env_path: Path):
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            if "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)


def main():
    # Load .env if present so we can pick up SMTP_FROM / SMTP_TO_OVERRIDE
    load_env_file(ROOT / ".env")

    smtp_from = os.getenv("SMTP_FROM")
    smtp_to_override = os.getenv("SMTP_TO_OVERRIDE")

    to_addr = smtp_to_override.strip() if smtp_to_override and smtp_to_override.strip() else (smtp_from or "")
    if not to_addr:
        print("No recipient found. Set SMTP_TO_OVERRIDE or SMTP_FROM in .env or pass a recipient.")
        sys.exit(1)

    token_path = ROOT / "token.json"
    if not token_path.exists():
        print(f"token.json not found at {token_path}. Run core/create_gmail_token.py first.")
        sys.exit(1)

    subject = "[Test] Gmail API send from AUTO_COLD MAIL GEN"
    body = "This is a test message sent by the project to verify Gmail API send.\nIf you received this, the OAuth flow and token.json are working." 

    try:
        print(f"Sending test email to: {to_addr} (from: {smtp_from}) using token.json")
        res = send_message(str(token_path), to_addr, subject, body, from_email=smtp_from)
        print("Send API response:")
        print(res)
        print("Test send completed — check the recipient inbox.")
    except Exception as e:
        print("Error while sending test email:", e)
        raise


if __name__ == "__main__":
    main()

