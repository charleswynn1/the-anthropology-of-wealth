#!/usr/bin/env python3
"""
Upload aggregated API costs for a MoneyMath project to Google Sheets.

Usage:
    python upload_costs.py <project-slug>
    python upload_costs.py --auth          # Re-authenticate Sheets token

Reads projects/<project>/costs.json, aggregates total production cost,
and appends a row to the configured Google Sheet.

Sheet columns: Content Type | Project Name | Production Cost | Gemini Total |
               ElevenLabs Total | Gemini Text | Gemini Image | EL TTS | EL Music | EL SFX

Requires:
    - GOOGLE_SHEET_ID in .env
    - sheets_token.pickle (run --auth or youtube_auth.py --sheets)
"""

import argparse
import os
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Load .env
_env_path = ROOT / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from cost_tracker import get_total_cost, get_cost_breakdown

SHEETS_TOKEN_FILE = ROOT / "sheets_token.pickle"
CLIENT_SECRETS = ROOT / "client_secrets.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def _authenticate_sheets():
    """Run browser-based OAuth flow for Google Sheets."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CLIENT_SECRETS.exists():
        print(f"ERROR: {CLIENT_SECRETS} not found.", file=sys.stderr)
        sys.exit(1)

    print("Opening browser for Google Sheets login...")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    with open(SHEETS_TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)

    print(f"Sheets token saved to {SHEETS_TOKEN_FILE}")
    return creds


def _get_credentials():
    """Load Google Sheets OAuth credentials."""
    if not SHEETS_TOKEN_FILE.exists():
        print(f"ERROR: {SHEETS_TOKEN_FILE} not found.\nRun: python upload_costs.py --auth", file=sys.stderr)
        sys.exit(1)

    with open(SHEETS_TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(SHEETS_TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
        else:
            print("ERROR: Sheets token expired. Re-run: python upload_costs.py --auth", file=sys.stderr)
            sys.exit(1)

    return creds


def _get_sheet_id() -> str:
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
    if not sheet_id:
        print("ERROR: GOOGLE_SHEET_ID not found in .env", file=sys.stderr)
        sys.exit(1)
    return sheet_id


def upload_cost(project: str):
    """Aggregate costs and append a row to Google Sheets."""
    project_dir = ROOT / "projects" / project
    if not project_dir.is_dir():
        print(f"ERROR: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    total = get_total_cost(project_dir)
    breakdown = get_cost_breakdown(project_dir)

    if total == 0.0:
        print(f"No costs recorded for {project}. Nothing to upload.")
        print(f"  (looked in: {project_dir / 'costs.json'})")
        sys.exit(0)

    print(f"Cost summary for {project}:")
    for key, amount in sorted(breakdown.items()):
        print(f"  {key}: ${amount:.4f}")
    print(f"  TOTAL: ${total:.4f}")

    from googleapiclient.discovery import build

    creds = _get_credentials()
    sheet_id = _get_sheet_id()

    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()

    gemini_total = sum(v for k, v in breakdown.items() if k.startswith("gemini_"))
    elevenlabs_total = sum(v for k, v in breakdown.items() if k.startswith("elevenlabs_"))
    gemini_text = breakdown.get("gemini_text_gen", 0.0)
    gemini_image = breakdown.get("gemini_image_gen", 0.0)
    el_tts = breakdown.get("elevenlabs_tts", 0.0)
    el_music = breakdown.get("elevenlabs_music", 0.0)
    el_sfx = breakdown.get("elevenlabs_sfx", 0.0)

    row = [
        "moneymath",            # A: Content Type
        project,                # B: Project Name
        f"${total:.2f}",        # C: Total Production Cost
        f"${gemini_total:.2f}", # D: Gemini Total
        f"${elevenlabs_total:.2f}",  # E: Elevenlabs Total
        f"${gemini_text:.2f}",  # F: Gemini Text Cost
        f"${gemini_image:.2f}", # G: Gemini Image Cost
        f"${el_tts:.2f}",      # H: ElevenLabs TTS Cost
        f"${el_music:.2f}",    # I: ElevenLabs Music Cost
        f"${el_sfx:.2f}",      # J: ElevenLabs SFX Cost
    ]

    body = {"values": [row]}
    result = sheets.values().append(
        spreadsheetId=sheet_id,
        range="Videos!A:J",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

    updated = result.get("updates", {}).get("updatedRows", 0)
    print(f"\nUploaded to Google Sheets: {updated} row(s) appended")
    print(f"  Content Type: moneymath")
    print(f"  Project Name: {project}")
    print(f"  Total Production Cost: ${total:.2f}")
    print(f"  Gemini Total: ${gemini_total:.2f}  (Text: ${gemini_text:.2f}, Image: ${gemini_image:.2f})")
    print(f"  ElevenLabs Total: ${elevenlabs_total:.2f}  (TTS: ${el_tts:.2f}, Music: ${el_music:.2f}, SFX: ${el_sfx:.2f})")


def main():
    parser = argparse.ArgumentParser(description="Upload MoneyMath API costs to Google Sheets")
    parser.add_argument("project", nargs="?", help="Project slug (e.g. car-note-trap)")
    parser.add_argument("--auth", action="store_true", help="Re-authenticate Google Sheets")

    args = parser.parse_args()

    if args.auth:
        _authenticate_sheets()
        return

    if not args.project:
        parser.error("project slug is required (unless using --auth)")

    upload_cost(project=args.project)


if __name__ == "__main__":
    main()
