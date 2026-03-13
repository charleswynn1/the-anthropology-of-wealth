#!/usr/bin/env python3
"""
Generate 3 new thumbnail variations (thumbnail-4/5/6) without overwriting existing ones.
Uses same infrastructure as generate_thumbnail.py.
"""

import base64
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from cost_tracker import log_gemini_image_cost

PRIMARY_MODEL = "gemini-3.1-flash-image-preview"
FALLBACK_MODEL = "gemini-3-pro-image-preview"
MAX_RETRIES = 3

API_KEYS = [v for k, v in sorted(os.environ.items())
            if k.startswith("GEMINI_KEY_") and v.strip()]
if not API_KEYS:
    fallback = os.environ.get("GEMINI_API_KEY", "")
    if fallback:
        API_KEYS = [fallback]

REF_IMAGE_PATH = ROOT / "reference" / "character.png"
REF_IMAGE_BYTES = REF_IMAGE_PATH.read_bytes()
REF_MIME = "image/png"

CHAR_BASE = (
    "a muscular Black man animated in the exact same Boondocks-style art as "
    "the reference image — bold clean linework, flat cel-shading, sharp angular "
    "features, short cropped hair"
)

THUMB_STYLE = (
    "Dark background (#0d1117). 1920x1080 landscape YouTube thumbnail. "
    "Boondocks-style animation matching the reference image. "
    "Cinematic lighting, dramatic composition, eye-catching for YouTube. "
    "CLEAN and SIMPLE — the character and text only. No clutter."
)

VARIATIONS = [
    {
        "index": 4,
        "label": "Curiosity + Conflict",
        "title": "They Said Gold Was Dead",
        "scene": (
            "The character in a modern business suit, standing in a massive underground "
            "central bank vault, stumbling upon a classified ledger held open in both hands — "
            "its pages showing a bar chart of gold reserves spiking to a record high in 2024. "
            "His expression: jaw slightly open, eyes wide and disbelieving, brow furrowed — "
            "the exact face of someone who found proof of something they suspected but could not "
            "believe. Behind him, floor-to-ceiling shelves of gold bars recede into darkness. "
            "The character is small against the massive vault interior, lit by a single overhead "
            "light. Close-medium shot on face and upper body, gold bars glinting warmly in the "
            "deep shadow behind. Boondocks animated illustration, warm gold contrasted with cold "
            "steel, cinematic dramatic lighting."
        ),
    },
    {
        "index": 5,
        "label": "Emotion + Reward",
        "title": "79 Elements Eliminated",
        "scene": (
            "The character in ancient Lydian merchant clothing — simple off-white linen tunic, "
            "leather sandals, a small coin purse at his belt — standing before a massive glowing "
            "stone tablet carved with a periodic table. One hundred and seventeen elements are "
            "crossed out in red chalk, leaving only element 79 (Au — Gold) glowing warm amber. "
            "His expression: the specific look of sudden, quiet revelation — slightly open mouth, "
            "eyebrows raised, eyes fixed on that single glowing square, one hand resting on the "
            "stone. Medium shot so both his face and the full table are visible. The gold glow "
            "illuminates his face from the front, throwing dramatic shadow behind him. "
            "Boondocks animated illustration, warm amber gold light, ancient stone setting."
        ),
    },
    {
        "index": 6,
        "label": "Contrast + Curiosity",
        "scene": (
            "Split-frame composition. Left half: dark, shadowed, desaturated — a Boondocks-style "
            "animated Nixon figure at a podium, 1971, a banner behind him reading 'GOLD WINDOW "
            "CLOSED'. Right half: warm gold light — a suited central banker figure from behind, "
            "pushing a massive cart loaded with stacked gold bars through an open vault door. "
            "Our character (the reference figure) stands at the exact center seam between the two "
            "halves, facing the viewer, arms slightly out — expression: slow, wry, knowing "
            "disbelief, the half-smile of someone who has just understood the joke. The contrast "
            "between the dark political left side and the glowing gold right side is stark and "
            "clean. Minimal composition, no clutter, one clear focal point at the center. "
            "Boondocks animated illustration, high contrast lighting."
        ),
        "title": "Closed the Window. Kept the Gold.",
    },
]


def generate_thumbnail(project_dir: Path, variation: dict, api_key: str) -> bool:
    from google import genai
    from google.genai import types

    idx = variation["index"]
    out_path = project_dir / f"thumbnail-{idx}.png"
    title = variation["title"]
    scene = variation["scene"]
    label = variation["label"]

    prompt = (
        f"Using the attached image as a character reference, generate a YouTube "
        f"thumbnail in the EXACT same art style (Boondocks-style animation, bold "
        f"linework, flat cel-shading). The character must look like the man in the "
        f"reference image: {CHAR_BASE}.\n\n"
        f"SCENE — the character's appearance, clothing, action, and surroundings:\n"
        f"{scene}\n\n"
        f"The character's clothing and dress must match the scene description above, "
        f"appropriate to the video topic and historical context described.\n\n"
        f"TEXT — render this short, bold, attention-grabbing hook text prominently "
        f"in the image: \"{title}\"\n\n"
        f"RULES:\n"
        f"- Character appearance, dress, pose, and expression must match the scene description exactly\n"
        f"- The hook text must be large, bold, and legible — placed to complement the composition\n"
        f"- No charts, no graphs, no floating icons, no captions, no watermarks\n"
        f"- No extra text beyond the hook text above\n"
        f"- Character expression must match the scene description exactly — do not override\n\n"
        f"{THUMB_STYLE}"
    )

    print(f"\nGenerating thumbnail #{idx} ({label})...")
    print(f"  Title: \"{title}\"")

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
                        img_bytes = base64.b64decode(img_data) if isinstance(img_data, str) else img_data
                        out_path.write_bytes(img_bytes)
                        cost = log_gemini_image_cost(project_dir, 1, f"thumbnail_{idx}")
                        print(f"  ✓ {out_path.name} ({len(img_bytes) // 1024} KB, cost: ${cost:.4f})")
                        return True

                print(f"  No image data in response")

            except Exception as e:
                print(f"  ERROR: {e}")

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

        if model == PRIMARY_MODEL:
            print(f"  Primary failed — trying fallback...")

    print(f"  FAILED: thumbnail-{idx}")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_thumbnails_new.py <project>")
        sys.exit(1)

    project = sys.argv[1]
    project_dir = ROOT / "projects" / project

    if not project_dir.is_dir():
        print(f"ERROR: {project_dir} not found")
        sys.exit(1)

    if not API_KEYS:
        print("ERROR: No Gemini API keys found")
        sys.exit(1)

    print(f"Project: {project}")
    print(f"Generating thumbnails 4, 5, 6 (existing 1-3 untouched)...")

    results = []
    for i, variation in enumerate(VARIATIONS):
        api_key = API_KEYS[i % len(API_KEYS)]
        ok = generate_thumbnail(project_dir, variation, api_key)
        if ok:
            results.append(variation["index"])
        if i < len(VARIATIONS) - 1:
            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Done — {len(results)}/3 generated: {results}")


if __name__ == "__main__":
    main()
