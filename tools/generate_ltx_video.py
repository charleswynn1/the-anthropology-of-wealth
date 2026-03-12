#!/usr/bin/env python3
"""
MoneyMath — LTX Image-to-Video Generator
Converts a still image into a short video clip using the LTX API.

Usage:
  python3 tools/generate_ltx_video.py <image_path_or_url> <output_path> [prompt] [duration] [resolution]

Examples:
  python3 tools/generate_ltx_video.py projects/my-project/images/H01.png projects/my-project/clips/H01.mp4
  python3 tools/generate_ltx_video.py projects/my-project/images/H01.png out.mp4 "Camera slowly zooms in" 8 1920x1080

Arguments:
  image_path_or_url  Local file path or public URL of the source image
  output_path        Where to save the generated MP4
  prompt             (optional) Motion description. Default: gentle cinematic camera drift
  duration           (optional) Clip length in seconds. Default: 8
  resolution         (optional) Output resolution. Default: 1920x1080

Supported models: ltx-2-3-pro (default), ltx-2-3
API key: LTX_API_KEY in .env
"""

import sys
import os
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("LTX_API_KEY")
if not API_KEY:
    print("ERROR: LTX_API_KEY not found in .env")
    sys.exit(1)

API_URL = "https://api.ltx.video/v1/image-to-video"
DEFAULT_MODEL = "ltx-2-3-pro"
DEFAULT_PROMPT = "Gentle cinematic camera drift, subtle parallax motion, smooth and atmospheric"
DEFAULT_DURATION = 8
DEFAULT_RESOLUTION = "1920x1080"


def image_to_data_uri(path: Path, max_bytes: int = 5 * 1024 * 1024) -> str:
    """Convert a local image file to a base64 data URI, resizing if over max_bytes."""
    from PIL import Image
    import io

    img = Image.open(path).convert("RGB")
    quality = 90
    scale = 1.0

    while True:
        w = int(img.width * scale)
        h = int(img.height * scale)
        resized = img.resize((w, h), Image.LANCZOS) if scale < 1.0 else img
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=quality)
        size = buf.tell()
        if size <= max_bytes:
            print(f"  Image: {w}x{h}, {size // 1024} KB (quality={quality}, scale={scale:.2f})")
            data = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/jpeg;base64,{data}"
        # Reduce quality first, then scale
        if quality > 60:
            quality -= 10
        else:
            scale -= 0.1
            quality = 85
        if scale < 0.1:
            raise ValueError(f"Cannot compress image below {max_bytes // 1024} KB")


def generate_video(
    image_source: str,
    output_path: Path,
    prompt: str = DEFAULT_PROMPT,
    duration: int = DEFAULT_DURATION,
    resolution: str = DEFAULT_RESOLUTION,
    model: str = DEFAULT_MODEL,
) -> None:
    import requests

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if output already exists
    if output_path.exists():
        print(f"SKIP {output_path} (already exists)")
        return

    # Resolve local file → data URI, or pass through URL as-is
    src = Path(image_source)
    if src.exists():
        print(f"Loading local image: {src} ({src.stat().st_size // 1024} KB)")
        image_uri = image_to_data_uri(src)
    else:
        image_uri = image_source
        print(f"Using image URL: {image_uri[:80]}...")

    payload = {
        "image_uri": image_uri,
        "prompt": prompt,
        "model": model,
        "duration": duration,
        "resolution": resolution,
        "generate_audio": False,
    }

    print(f"Sending request to LTX API...")
    print(f"  model:      {model}")
    print(f"  duration:   {duration}s")
    print(f"  resolution: {resolution}")
    print(f"  prompt:     {prompt[:80]}")

    resp = requests.post(
        API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=300,
        stream=True,
    )

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code} error: {resp.text[:500]}")
        sys.exit(1)

    content_type = resp.headers.get("Content-Type", "")
    request_id = resp.headers.get("x-request-id", "unknown")

    if "video" not in content_type:
        print(f"ERROR: Unexpected Content-Type '{content_type}'")
        print(f"Response: {resp.text[:500]}")
        sys.exit(1)

    video_bytes = resp.content
    output_path.write_bytes(video_bytes)
    size_kb = len(video_bytes) // 1024
    print(f"OK → {output_path} ({size_kb} KB)")
    print(f"   request-id: {request_id}")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)

    image_source = args[0]
    output_path = Path(args[1])
    prompt = args[2] if len(args) > 2 else DEFAULT_PROMPT
    duration = int(args[3]) if len(args) > 3 else DEFAULT_DURATION
    resolution = args[4] if len(args) > 4 else DEFAULT_RESOLUTION

    generate_video(image_source, output_path, prompt, duration, resolution)


if __name__ == "__main__":
    main()
