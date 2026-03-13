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

PROJECT_NAME = "gold-became-money"  # Folder name under projects/

MUSIC_PROMPT = (
    "Ancient-modern documentary instrumental: deep resonant low brass and slowly pulsing "
    "bass drones beneath sparse, deliberate piano notes — each note weighted, like a gold "
    "coin placed on a scale. Subtle metallic shimmer in the high frequencies evoking "
    "ancient forges and molten metal. The arc moves from reverent and timeless in the "
    "opening, through mounting tension in the middle, to a cool investigative unease at "
    "the close — the feeling of discovering something powerful that has never actually "
    "stopped. Steady 70 to 80 BPM. No vocals. Cinematic, atmospheric, and historically "
    "grounded — suitable for narration spanning from ancient Lydia and Potosi to Nixon's "
    "Camp David and modern central bank gold buying."
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
