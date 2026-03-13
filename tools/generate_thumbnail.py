#!/usr/bin/env python3
"""
Generate 3 thumbnail variations for A/B testing via YouTube's Test & Compare.

Usage:
    python generate_thumbnail.py <project-slug>

Output:
    projects/<project>/thumbnail-1.png  — "The Hook" (primary, uploaded via API)
    projects/<project>/thumbnail-2.png  — "The Lesson" (Test & Compare)
    projects/<project>/thumbnail-3.png  — "The Impact" (Test & Compare)

Each variation sends the reference character image to Gemini and lets the model
generate the full thumbnail: character, scene, and on-screen text — all in one pass.

Reads thumbnail metadata from projects/<project>/script.md:
    [THUMBNAIL]
    title: The $100K Trap
    subtitle: Most people never see it coming
    titles:
      - Title variation 1
      - Title variation 2
      - Title variation 3
    subtitles:
      - Subtitle variation 1
      - Subtitle variation 2
      - Subtitle variation 3
    scenes:
      - Scene description 1
      - Scene description 2
      - Scene description 3
"""

import base64
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from cost_tracker import log_gemini_image_cost

PRIMARY_MODEL = "gemini-3.1-flash-image-preview"
FALLBACK_MODEL = "gemini-3-pro-image-preview"
MAX_RETRIES = 3

# Round-robin API keys
API_KEYS = [v for k, v in sorted(os.environ.items())
            if k.startswith("GEMINI_KEY_") and v.strip()]
if not API_KEYS:
    fallback = os.environ.get("GEMINI_API_KEY", "")
    if fallback:
        API_KEYS = [fallback]

# Reference character image — sent as multimodal input
REF_IMAGE_PATH = ROOT / "reference" / "character.png"
REF_IMAGE_BYTES = REF_IMAGE_PATH.read_bytes()
_ext = REF_IMAGE_PATH.suffix.lower()
REF_MIME = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(_ext.lstrip("."), "image/png")

# Base character identity — clothing/dress is specified per scene in the [THUMBNAIL] block
CHAR_BASE = ("a muscular Black man animated in the exact same Boondocks-style art as "
             "the reference image — bold clean linework, flat cel-shading, sharp angular "
             "features, short cropped hair")

# Visual style for thumbnails
THUMB_STYLE = ("Dark background (#0d1117). 1920x1080 landscape YouTube thumbnail. "
               "Boondocks-style animation matching the reference image. "
               "Cinematic lighting, dramatic composition, eye-catching for YouTube. "
               "CLEAN and SIMPLE — the character and text only. No clutter.")


def find_project(slug: str) -> Path:
    project_dir = ROOT / "projects" / slug
    if not project_dir.is_dir():
        print(f"ERROR: Project directory not found: {project_dir}")
        sys.exit(1)
    return project_dir


def read_script(project_dir: Path) -> str:
    script_path = project_dir / "script.md"
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        sys.exit(1)
    return script_path.read_text()


def extract_thumbnail_texts(script: str) -> list[str]:
    """Extract all thumbnail text options from script. Returns up to 3 short, punchy options."""
    # Try [THUMBNAIL] block first
    thumb_match = re.search(
        r"\[THUMBNAIL\]\s*\n\s*title:\s*(.+)", script, re.IGNORECASE)
    if thumb_match:
        return [thumb_match.group(1).strip()]

    # Pull all THUMBNAIL TEXT options
    # Handles ## THUMBNAIL TEXT, ## 2. THUMBNAIL TEXT, **2. THUMBNAIL TEXT**, etc.
    thumb_section = re.search(
        r"(?:\*\*\d*\.?\s*THUMBNAIL TEXT\*\*|##\s*\d*\.?\s*THUMBNAIL TEXT[^\n]*)(.*?)(?=\*\*\d|##\s|\Z)",
        script, re.DOTALL | re.IGNORECASE)
    if thumb_section:
        raw = re.findall(r"(?:[-•*]|\d+\.)\s*(.+)", thumb_section.group(1))
        items = [x.strip().strip('"').strip("'") for x in raw
                 if x.strip() and not re.match(r"^-+$", x.strip())]
        if items:
            # Score each option: prefer shocking/intriguing hooks over plain titles
            # Arrows, question marks, equations, contrasts = more hook-like
            def hook_score(text: str) -> int:
                score = 0
                if "→" in text or "->" in text:
                    score += 3  # transformation/contrast = great hook
                if "?" in text and not text.lower().startswith(("why", "how", "what")):
                    score += 2  # surprising question
                if "=" in text:
                    score += 2  # equation/reveal
                if any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
                    score += 1  # mix of numbers and words = intriguing
                # Penalize if it reads like a plain title (starts with common title words)
                lower = text.lower()
                if lower.startswith(("just ", "why ", "how ", "what ", "the ")):
                    score -= 2
                return score

            sorted_items = sorted(items, key=lambda x: (-hook_score(x), len(x)))
            return sorted_items[:3] if len(sorted_items) >= 3 else sorted_items

    return ["Money Math"]


def extract_subtitle(script: str) -> str:
    thumb_match = re.search(
        r"\[THUMBNAIL\]\s*\n\s*(?:title:\s*.+\n\s*)?subtitle:\s*(.+)",
        script, re.IGNORECASE)
    if thumb_match:
        return thumb_match.group(1).strip()

    core = re.search(r"(?:\*\*\d*\.?\s*CORE IDEA\*\*|##\s*\d*\.?\s*CORE IDEA[^\n]*)\s*\n+(.+)", script, re.IGNORECASE)
    if core:
        text = core.group(1).strip()
        end = re.search(r'[.!?]', text)
        if end:
            return text[:end.end()].strip()
        return text[:80].strip()

    return "The math behind the money"


def extract_titles(script: str) -> list[str]:
    """Return 3 different thumbnail text options for the 3 variations."""
    # Try [THUMBNAIL] block titles: list first
    thumb_match = re.search(
        r"\[THUMBNAIL\].*?(?=\n\[|\Z)", script, re.DOTALL | re.IGNORECASE)
    if thumb_match:
        block = thumb_match.group(0)
        titles_match = re.search(r"titles:\s*\n((?:\s*-\s*.+\n?)+)", block, re.IGNORECASE)
        if titles_match:
            lines = titles_match.group(1).strip().splitlines()
            items = [re.sub(r"^\s*-\s*", "", line).strip() for line in lines if line.strip()]
            if len(items) >= 3:
                return items[:3]

    # Fall back to THUMBNAIL TEXT section — pick 3 different options
    # Prefer shocking/intriguing text, not video-title-like text
    texts = extract_thumbnail_texts(script)
    if len(texts) >= 3:
        return texts[:3]
    # Pad to 3 by cycling
    return [texts[i % len(texts)] for i in range(3)]


def extract_subtitles(script: str) -> list[str]:
    thumb_match = re.search(
        r"\[THUMBNAIL\].*?(?=\n\[|\Z)", script, re.DOTALL | re.IGNORECASE)
    if thumb_match:
        block = thumb_match.group(0)
        subs_match = re.search(r"subtitles:\s*\n((?:\s*-\s*.+\n?)+)", block, re.IGNORECASE)
        if subs_match:
            lines = subs_match.group(1).strip().splitlines()
            items = [re.sub(r"^\s*-\s*", "", line).strip() for line in lines if line.strip()]
            if len(items) >= 3:
                return items[:3]
    return [extract_subtitle(script)] * 3


def extract_thumbnail_hints(script: str) -> list[str]:
    thumb_match = re.search(
        r"\[THUMBNAIL\].*?(?=\n\[|\Z)", script, re.DOTALL | re.IGNORECASE)
    if not thumb_match:
        return []
    block = thumb_match.group(0)
    scenes_match = re.search(r"scenes:\s*\n((?:\s*-\s*.+\n?)+)", block, re.IGNORECASE)
    if not scenes_match:
        return []
    lines = scenes_match.group(1).strip().splitlines()
    return [re.sub(r"^\s*-\s*", "", line).strip() for line in lines if line.strip()]


def extract_hook_text(script: str) -> str:
    hook_match = re.search(
        r"(?:s1_hook|HOOK).*?\n(.+?)(?=\n##|\n\*\*\d|\Z)",
        script, re.DOTALL | re.IGNORECASE)
    if hook_match:
        text = hook_match.group(1).strip()
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        return text[:300]
    return script[:300]


# ── Default fallback angles (used only when script has no [THUMBNAIL] block) ──

DEFAULT_VARIATION_LABELS = ["The Hook", "The Lesson", "The Impact"]


def build_variation_prompts(
    hook_text: str, titles: list[str], subtitles: list[str], scene_hints: list[str],
) -> list[str]:
    """Build 3 prompts — scene_hints from [THUMBNAIL] block drive character action and setting."""

    prompts = []
    for i in range(3):
        title = titles[i] if i < len(titles) else titles[0]

        # Scene description from script drives what the character IS DOING and WHERE
        if i < len(scene_hints) and scene_hints[i].strip():
            scene_desc = scene_hints[i].strip()
        else:
            # Generic fallback only if no scene hints — still references topic via hook text
            topic_context = hook_text[:200].strip()
            scene_desc = (
                f"The character reacting with intense, knowing gravity to the following "
                f"topic: {topic_context}. Dark cinematic background."
            )

        prompt = (
            f"Using the attached image as a character reference, generate a YouTube "
            f"thumbnail in the EXACT same art style (Boondocks-style animation, bold "
            f"linework, flat cel-shading). The character must look like the man in the "
            f"reference image: {CHAR_BASE}.\n\n"
            f"SCENE — the character's appearance, clothing, action, and surroundings:\n"
            f"{scene_desc}\n\n"
            f"The character's clothing and dress must match the scene description above, "
            f"appropriate to the video topic and historical context described.\n\n"
            f"TEXT — render this short, bold, attention-grabbing hook text prominently "
            f"in the image: \"{title}\"\n\n"
            f"RULES:\n"
            f"- Character appearance, dress, pose, and expression must match the scene description exactly\n"
            f"- The hook text must be large, bold, and legible — placed to complement the composition\n"
            f"- No charts, no graphs, no floating icons, no captions, no watermarks\n"
            f"- No extra text beyond the hook text above\n"
            f"- Character expression must match the scene description exactly — do not override with a default expression\n\n"
            f"{THUMB_STYLE}"
        )
        prompts.append(prompt)

    return prompts


def generate_thumbnail(
    project_dir: Path, prompt: str, variation_index: int, api_key: str,
) -> Path | None:
    """Generate a full thumbnail (character + scene + text) via Gemini."""
    from google import genai
    from google.genai import types

    out_path = project_dir / f"thumbnail-{variation_index}.png"

    label = DEFAULT_VARIATION_LABELS[variation_index - 1] if variation_index - 1 < len(DEFAULT_VARIATION_LABELS) else f"Variation {variation_index}"
    print(f"\nGenerating thumbnail #{variation_index} ({label})...")
    print(f"  Prompt: {prompt[:120]}...")

    # Try primary model with retries, then fallback
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        client = genai.Client(api_key=api_key)

        retries = MAX_RETRIES if model == PRIMARY_MODEL else 1
        for attempt in range(retries):
            print(f"  Trying {model} (attempt {attempt + 1}/{retries})...")
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(data=REF_IMAGE_BYTES, mime_type=REF_MIME),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        temperature=0.7,
                        image_config=types.ImageConfig(
                            image_size="4K",
                            aspect_ratio="16:9",
                        ),
                    ),
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        img_data = part.inline_data.data
                        if isinstance(img_data, str):
                            img_bytes = base64.b64decode(img_data)
                        else:
                            img_bytes = img_data
                        out_path.write_bytes(img_bytes)
                        cost = log_gemini_image_cost(project_dir, 1, f"thumbnail_{variation_index}")
                        print(f"  OK ({model}): {out_path} ({len(img_bytes) // 1024} KB, cost: ${cost:.4f})")
                        return out_path

                print(f"  No image data in response")

            except Exception as e:
                print(f"  ERROR: {e}")

            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)

        if model == PRIMARY_MODEL:
            print(f"  Primary model failed — falling back to {FALLBACK_MODEL}...")

    print(f"  ERROR: All models failed to generate thumbnail")
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_thumbnail.py <project-slug>")
        sys.exit(1)

    slug = sys.argv[1]
    project_dir = find_project(slug)
    script = read_script(project_dir)

    titles = extract_titles(script)
    subtitles = extract_subtitles(script)
    hook_text = extract_hook_text(script)
    scene_hints = extract_thumbnail_hints(script)

    print(f"Project: {slug}")
    unique_titles = len(set(titles)) > 1
    if unique_titles:
        for i in range(3):
            print(f"  Variation {i+1}: \"{titles[i]}\" / \"{subtitles[i]}\"")
    else:
        print(f"  Title: {titles[0]}")
        print(f"  Subtitle: {subtitles[0]}")
    if scene_hints:
        print(f"  Scene hints: {len(scene_hints)} from [THUMBNAIL] block")

    prompts = build_variation_prompts(hook_text, titles, subtitles, scene_hints)

    if not API_KEYS:
        print("ERROR: No Gemini API keys found")
        sys.exit(1)

    results = []

    for i, prompt in enumerate(prompts, start=1):
        label = DEFAULT_VARIATION_LABELS[i - 1] if i - 1 < len(DEFAULT_VARIATION_LABELS) else f"Variation {i}"
        api_key = API_KEYS[(i - 1) % len(API_KEYS)]

        result = generate_thumbnail(project_dir, prompt, i, api_key)
        if result:
            results.append((i, label, result))
        else:
            print(f"  SKIP: Variation {i} ({label}) — generation failed")

        if i < len(prompts):
            time.sleep(2)

    # Summary
    print(f"\n{'='*50}")
    print(f"Thumbnail generation complete — {len(results)}/3 variations:")
    for idx, label, path in results:
        primary = " (primary)" if idx == 1 else ""
        print(f"  [{idx}] {label}{primary}: \"{titles[idx-1]}\" / \"{subtitles[idx-1]}\"")
        print(f"       {path}")
    if not results:
        print("  No thumbnails generated — check errors above")
    else:
        print(f"\nUpload primary with:")
        print(f"  python youtube_upload.py out/{slug}.mp4 --thumbnail {results[0][2]}")
        print(f"Add thumbnail-2.png and thumbnail-3.png via YouTube Studio > Test & Compare")


if __name__ == "__main__":
    main()
