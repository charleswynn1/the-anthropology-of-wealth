#!/usr/bin/env python3
"""
MoneyMath — Background Music Generation Pipeline
Generates background music using ElevenLabs Music API.

Usage:
  1. Set PROJECT_NAME to your project folder name
  2. Optionally customize MUSIC_PROMPT and MUSIC_LENGTH_MS
  3. Run: python3 generate_music.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from cost_tracker import log_elevenlabs_cost

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY not found in .env")
    sys.exit(1)

client = ElevenLabs(api_key=API_KEY)

# ══════════════════════════════════════════════════════════
# CONFIGURATION — Edit these for each new video
# ══════════════════════════════════════════════════════════

PROJECT_NAME = "before-money"  # Folder name under projects/

MUSIC_PROMPT = (
    "Ancient history documentary instrumental: sparse, contemplative strings beneath a low "
    "sustained cello line. The emotional texture of a buried truth being slowly uncovered. "
    "Opens quietly in a minor key, intimate and close, as if in a candlelit room reading "
    "old documents. Through the middle, a sense of accumulating civilizational weight, "
    "the slow mathematics of debt and time building beneath the melody. Closes with a "
    "quiet, unresolved chord that lingers without triumph. Sixty to seventy BPM. No drums "
    "or percussion. No vocals. Cinematic and restrained, suitable for narration spanning "
    "ancient Sumer, medieval England, Aztec markets, Babylon, Roman law, and modern "
    "credit card statements."
)

MUSIC_LENGTH_MS = 300000  # 5 minutes (300,000 ms)

# ══════════════════════════════════════════════════════════
# GENERATION — No need to edit below this line
# ══════════════════════════════════════════════════════════

OUT = ROOT / f"projects/{PROJECT_NAME}/audio"
OUT.mkdir(parents=True, exist_ok=True)


def generate_music():
    out_path = OUT / "music_bg.mp3"
    if out_path.exists():
        print(f"  SKIP music_bg.mp3 (exists)")
        return
    minutes = MUSIC_LENGTH_MS // 60000
    print(f"  Generating {minutes}-minute background music...")
    try:
        audio = client.music.compose(
            prompt=MUSIC_PROMPT,
            music_length_ms=MUSIC_LENGTH_MS,
            force_instrumental=True,
            model_id="music_v1",
        )
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        duration_seconds = MUSIC_LENGTH_MS / 1000
        cost = log_elevenlabs_cost(OUT.parent, "music", duration_seconds, "bg_music")
        print(f"    OK {out_path} (cost: ${cost:.4f})")
    except Exception as e:
        print(f"    FAIL: {e}")


if __name__ == "__main__":
    print(f"=== Generating background music for project: {PROJECT_NAME} ===")
    print(f"    Output: {OUT}\n")
    generate_music()
    print("\n=== Done! ===")
    music_file = OUT / "music_bg.mp3"
    if music_file.exists():
        size = music_file.stat().st_size
        print(f"  music_bg.mp3  ({size // 1024} KB)")
