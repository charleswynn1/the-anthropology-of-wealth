#!/usr/bin/env python3
"""
MoneyMath — Hedra Lip-Sync Generator
Takes a still image + narration audio and returns a talking-head video
where the character's mouth moves in sync with the audio.

Usage:
  python3 tools/generate_lipsync.py <image_path> <audio_path> <output_path> [prompt]

Examples:
  python3 tools/generate_lipsync.py \
    projects/budget-at-any-income/images/H01.png \
    projects/budget-at-any-income/audio/s1_hook.mp3 \
    projects/budget-at-any-income/clips/H01_lipsync.mp4

  python3 tools/generate_lipsync.py \
    projects/budget-at-any-income/images/H01.png \
    projects/budget-at-any-income/audio/s1_hook.mp3 \
    projects/budget-at-any-income/clips/H01_lipsync.mp4 \
    "An animated character speaking directly to camera, expressive and engaging"

Model: Hedra Avatar (26f0fc66-152b-40ab-abed-76c43df99bc8) — lip-sync, up to 10 min
API key: HEDRA_API_KEY in .env
"""

import sys
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("HEDRA_API_KEY")
if not API_KEY:
    print("ERROR: HEDRA_API_KEY not found in .env")
    sys.exit(1)

BASE_URL = "https://api.hedra.com/web-app/public"
AVATAR_MODEL_ID = "26f0fc66-152b-40ab-abed-76c43df99bc8"
DEFAULT_PROMPT = "An animated character speaking directly to camera, expressive and engaging"

HEADERS = {"X-API-Key": API_KEY}


def upload_asset(file_path: Path, asset_type: str) -> str:
    """Upload a file to Hedra and return the asset_id."""
    # Step 1: Create asset record
    resp = requests.post(
        f"{BASE_URL}/assets",
        headers=HEADERS,
        json={"name": file_path.name, "type": asset_type},
    )
    if resp.status_code not in (200, 201):
        print(f"ERROR creating {asset_type} asset: {resp.status_code} {resp.text[:300]}")
        sys.exit(1)
    asset_id = resp.json()["id"]
    print(f"  Created {asset_type} asset: {asset_id}")

    # Step 2: Upload file
    with open(file_path, "rb") as f:
        upload_resp = requests.post(
            f"{BASE_URL}/assets/{asset_id}/upload",
            headers=HEADERS,
            files={"file": (file_path.name, f)},
        )
    if upload_resp.status_code not in (200, 201, 204):
        print(f"ERROR uploading {asset_type}: {upload_resp.status_code} {upload_resp.text[:300]}")
        sys.exit(1)
    print(f"  Uploaded {asset_type}: {file_path.name} ({file_path.stat().st_size // 1024} KB)")
    return asset_id


def get_audio_duration_ms(audio_path: Path) -> int:
    """Get audio duration in milliseconds using mutagen, with fallback to 10 min max."""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(str(audio_path))
        duration_ms = int(audio.info.length * 1000)
        print(f"  Audio duration: {audio.info.length:.1f}s ({duration_ms} ms)")
        return duration_ms
    except ImportError:
        pass
    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
            capture_output=True, text=True
        )
        duration_ms = int(float(result.stdout.strip()) * 1000)
        print(f"  Audio duration: {duration_ms / 1000:.1f}s ({duration_ms} ms)")
        return duration_ms
    except Exception:
        pass
    print("  WARNING: Could not read audio duration, defaulting to 600000ms (10 min)")
    return 600_000


def generate_avatar_video(
    image_asset_id: str,
    audio_asset_id: str,
    duration_ms: int,
    prompt: str,
) -> str:
    """Submit a generation job and return the generation_id."""
    payload = {
        "type": "video",
        "ai_model_id": AVATAR_MODEL_ID,
        "start_keyframe_id": image_asset_id,
        "audio_id": audio_asset_id,
        "generated_video_inputs": {
            "text_prompt": prompt,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "duration_ms": duration_ms,
        },
    }
    resp = requests.post(
        f"{BASE_URL}/generations",
        headers=HEADERS,
        json=payload,
    )
    if resp.status_code not in (200, 201):
        print(f"ERROR submitting generation: {resp.status_code} {resp.text[:300]}")
        sys.exit(1)
    generation_id = resp.json()["id"]
    print(f"  Generation submitted: {generation_id}")
    return generation_id


def poll_until_complete(generation_id: str, poll_interval: int = 5) -> str:
    """Poll generation status until complete. Returns the download_url."""
    print(f"  Polling for completion (every {poll_interval}s)...")
    while True:
        resp = requests.get(
            f"{BASE_URL}/generations/{generation_id}/status",
            headers=HEADERS,
        )
        if resp.status_code != 200:
            print(f"ERROR polling status: {resp.status_code} {resp.text[:300]}")
            sys.exit(1)

        data = resp.json()
        status = data.get("status", "unknown")
        progress = data.get("progress", 0)
        eta = data.get("eta_sec")

        eta_str = f", ETA {eta:.0f}s" if eta else ""
        print(f"  Status: {status} ({progress * 100:.0f}%{eta_str})")

        if status == "complete":
            download_url = data.get("download_url") or data.get("url")
            if not download_url:
                print(f"ERROR: Generation complete but no download_url in response: {data}")
                sys.exit(1)
            return download_url
        elif status in ("failed", "error"):
            print(f"ERROR: Generation failed: {data}")
            sys.exit(1)

        time.sleep(poll_interval)


def download_asset(download_url: str, output_path: Path) -> None:
    """Download a completed video from its signed URL."""
    resp = requests.get(download_url, stream=True)
    if resp.status_code != 200:
        print(f"ERROR downloading video: {resp.status_code}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_kb = output_path.stat().st_size // 1024
    print(f"  Downloaded → {output_path} ({size_kb} KB)")


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print(__doc__)
        sys.exit(1)

    image_path = Path(args[0])
    audio_path = Path(args[1])
    output_path = Path(args[2])
    prompt = args[3] if len(args) > 3 else DEFAULT_PROMPT

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)
    if not audio_path.exists():
        print(f"ERROR: Audio not found: {audio_path}")
        sys.exit(1)
    if output_path.exists():
        print(f"SKIP {output_path} (already exists)")
        return

    print(f"\n=== Hedra Lip-Sync ===")
    print(f"  Image: {image_path}")
    print(f"  Audio: {audio_path}")
    print(f"  Output: {output_path}")
    print(f"  Prompt: {prompt[:80]}")

    print(f"\n[1/4] Uploading audio...")
    audio_asset_id = upload_asset(audio_path, "audio")

    print(f"\n[2/4] Uploading image...")
    image_asset_id = upload_asset(image_path, "image")

    print(f"\n[3/4] Submitting generation...")
    duration_ms = get_audio_duration_ms(audio_path)
    generation_id = generate_avatar_video(image_asset_id, audio_asset_id, duration_ms, prompt)

    print(f"\n[4/4] Waiting for generation to complete...")
    output_asset_id = poll_until_complete(generation_id)

    print(f"\nDownloading result...")
    download_asset(output_asset_id, output_path)

    print(f"\nDone! → {output_path}")


if __name__ == "__main__":
    main()
