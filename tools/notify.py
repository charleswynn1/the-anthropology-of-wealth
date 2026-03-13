#!/usr/bin/env python3
"""
Pipeline Notifier — Twilio SMS
Sends a text message to +14045193634 from +14706889390 at key pipeline milestones.

Usage:
  python3 tools/notify.py <milestone> [project]

Milestones:
  research    — Research phase complete (W1c done)
  script      — Script writing phase complete (W2 done)
  images      — All images generated (W3b done)
  remotion    — Remotion preview launched (W8c done)

Examples:
  python3 tools/notify.py research gold-became-money
  python3 tools/notify.py remotion
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_ID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

TO   = "+14045193634"
FROM = "+14706889390"

MESSAGES = {
    "research": "Research phase complete. Ready to write the script.",
    "script":   "Script writing phase complete. Ready to generate audio and images.",
    "images":   "All images generated. Ready for Remotion assembly.",
    "remotion": "Remotion preview is live. The video is ready to review.",
}


def send(milestone: str, project: str = "") -> None:
    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("ERROR: TWILIO_ACCOUNT_ID or TWILIO_AUTH_TOKEN not found in .env")
        sys.exit(1)

    if milestone not in MESSAGES:
        print(f"ERROR: Unknown milestone '{milestone}'. Choose from: {', '.join(MESSAGES)}")
        sys.exit(1)

    body = MESSAGES[milestone]
    if project:
        body = f"[{project}] {body}"

    try:
        from twilio.rest import Client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(body=body, from_=FROM, to=TO)
        print(f"  SMS sent ({milestone}): {message.sid}")
    except ImportError:
        print("ERROR: twilio package not installed. Run: pip install twilio")
        sys.exit(1)
    except Exception as e:
        print(f"  SMS FAILED: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    milestone = sys.argv[1]
    project = sys.argv[2] if len(sys.argv) > 2 else ""
    send(milestone, project)
