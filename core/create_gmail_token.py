"""Create Gmail OAuth token.json using credentials.json.

Run this script from the project root. It will open a local browser window
to complete the OAuth consent. After consenting, credentials will be saved
to `token.json` in the same directory as `credentials.json`.

Scopes: https://www.googleapis.com/auth/gmail.send

If the `google-auth-oauthlib` package is not installed, install it with:
    pip install google-auth-oauthlib
"""
import json
from pathlib import Path
import sys

def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except Exception as e:
        print("Missing dependency: google-auth-oauthlib. Install with: pip install google-auth-oauthlib")
        raise

    project_root = Path(__file__).resolve().parent.parent
    cred_path = project_root / "credentials.json"
    token_path = project_root / "token.json"

    if not cred_path.exists():
        print(f"credentials.json not found at {cred_path}. Put your OAuth client credentials there.")
        sys.exit(1)

    scopes = ["https://www.googleapis.com/auth/gmail.send"]

    print("Starting InstalledAppFlow; a browser window will open for you to sign in and grant permissions.")
    flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), scopes=scopes)
    creds = flow.run_local_server(host="localhost", port=0)

    # Save token
    data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    with token_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved token to {token_path}")


if __name__ == "__main__":
    main()
