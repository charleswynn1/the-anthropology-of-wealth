#!/usr/bin/env python3
"""
YouTube & Google Sheets OAuth2 Authentication — MoneyMath

Run this to generate/refresh token.pickle (YouTube) and sheets_token.pickle (Sheets).

Usage:
    python youtube_auth.py              # Authenticate both YouTube and Sheets
    python youtube_auth.py --youtube    # YouTube only
    python youtube_auth.py --sheets     # Sheets only
    python youtube_auth.py --check      # Check if tokens are valid (no browser)
"""

import pickle
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLIENT_SECRETS = PROJECT_ROOT / "client_secrets.json"
YT_TOKEN_FILE = PROJECT_ROOT / "token.pickle"
SHEETS_TOKEN_FILE = PROJECT_ROOT / "sheets_token.pickle"

YT_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def authenticate_youtube():
    """Authenticate for YouTube API access."""
    print("\n── YouTube Authentication ──")
    creds = None

    if YT_TOKEN_FILE.exists():
        with open(YT_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired YouTube token...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS.exists():
                print(f"ERROR: Missing {CLIENT_SECRETS}")
                sys.exit(1)
            print("Opening browser for Google login...")
            print(">>> SELECT THE CORRECT YOUTUBE CHANNEL when prompted <<<")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS), YT_SCOPES
            )
            creds = flow.run_local_server(port=0, prompt="consent")

        with open(YT_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print(f"YouTube token saved to {YT_TOKEN_FILE}")
    else:
        print("YouTube token is already valid.")

    print("YouTube: Authenticated successfully.")
    return creds


def authenticate_sheets():
    """Authenticate for Google Sheets API access."""
    print("\n── Google Sheets Authentication ──")
    creds = None

    if SHEETS_TOKEN_FILE.exists():
        with open(SHEETS_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired Sheets token...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS.exists():
                print(f"ERROR: Missing {CLIENT_SECRETS}")
                sys.exit(1)
            print("Opening browser for Google Sheets login...")
            print(">>> Sign in with the account that owns your spreadsheet <<<")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS), SHEETS_SCOPES
            )
            creds = flow.run_local_server(port=0, prompt="consent")

        with open(SHEETS_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print(f"Sheets token saved to {SHEETS_TOKEN_FILE}")
    else:
        print("Sheets token is already valid.")

    print("Sheets: Authenticated successfully.")
    return creds


def check_tokens():
    """Check if existing tokens are valid without opening browser."""
    print("\n── Token Status Check ──")

    for name, path in [("YouTube", YT_TOKEN_FILE), ("Sheets", SHEETS_TOKEN_FILE)]:
        if not path.exists():
            print(f"  {name}: NO TOKEN FILE")
            continue
        with open(path, "rb") as f:
            creds = pickle.load(f)
        if creds and creds.valid:
            print(f"  {name}: VALID")
        elif creds and creds.expired and creds.refresh_token:
            print(f"  {name}: EXPIRED (can be refreshed)")
            creds.refresh(Request())
            with open(path, "wb") as f:
                pickle.dump(creds, f)
            print(f"  {name}: REFRESHED — now valid")
        else:
            print(f"  {name}: INVALID (re-auth needed)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Authenticate YouTube and Google Sheets")
    parser.add_argument("--youtube", action="store_true", help="YouTube only")
    parser.add_argument("--sheets", action="store_true", help="Sheets only")
    parser.add_argument("--check", action="store_true", help="Check token validity only")
    args = parser.parse_args()

    if args.check:
        check_tokens()
    elif args.youtube:
        authenticate_youtube()
    elif args.sheets:
        authenticate_sheets()
    else:
        # Default: authenticate both
        authenticate_youtube()
        authenticate_sheets()
