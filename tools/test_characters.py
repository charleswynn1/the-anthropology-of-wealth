#!/usr/bin/env python3
"""
Test script — generates 4 images to validate multi-character reference system.
Outputs to /Users/charleswynn/Desktop/Youtube Videos/

Test cases:
  T01: Joseph only (solo male — ancient craftsman)
  T02: Joseph + Jess (couple at 1930s bank)
  T03: Joseph + Sola + Brayden (father with children at market)
  T04: Joseph + Jess + Sola + Brayden (full family — 1970s living room)
"""

import os
import sys
import json
import base64
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ── API Keys ──
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_KEY_1"),
    os.getenv("GEMINI_KEY_2"),
    os.getenv("GEMINI_KEY_3"),
]
API_KEYS = [k for k in API_KEYS if k]
if not API_KEYS:
    print("ERROR: No GEMINI API keys found in .env")
    sys.exit(1)
print(f"Loaded {len(API_KEYS)} API keys")

MODEL = "gemini-3.1-flash-image-preview"
OUT_DIR = Path("/Users/charleswynn/Desktop/Youtube Videos")

# ── Character References ──
_MIME_MAP = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}

_CHARACTER_FILES = {
    "joseph":  "reference/joseph.png",
    "jess":    "reference/jessw.png",
    "sola":    "reference/solaw.png",
    "brayden": "reference/braydenw.png",
}

_CHARACTER_LABELS = {
    "joseph":  "the main male character (Joseph)",
    "jess":    "the main female character (Jess)",
    "sola":    "the girl child (Sola)",
    "brayden": "the boy child (Brayden)",
}

REF_IMAGES = {}
for _char_name, _char_file in _CHARACTER_FILES.items():
    _char_path = ROOT / _char_file
    if _char_path.exists():
        _ext = _char_path.suffix.lower().lstrip(".")
        REF_IMAGES[_char_name] = {
            "bytes": _char_path.read_bytes(),
            "mime": _MIME_MAP.get(_ext, "image/png"),
        }
        print(f"Loaded reference: {_char_name} → {_char_path} ({len(REF_IMAGES[_char_name]['bytes']) // 1024} KB)")
    else:
        print(f"WARNING: Reference image not found: {_char_path}")

# ── Test Image Prompts ──
IMAGES = [
    # T01: Joseph only — ancient craftsman at forge
    ("T01_joseph_solo", ["joseph"], json.dumps({
        "image_description": {
            "ref_characters": ["joseph"],
            "metadata": {
                "art_style": "Boondocks-style animation, graphic novel illustration, bold linework",
                "setting": "Ancient Copper Age workshop, circa 4400 BCE, Balkans",
                "mood": "Focused, industrious, quiet mastery",
                "color_palette": ["Warm amber", "Deep bronze", "Charcoal black", "Burnt orange", "Clay brown"]
            },
            "main_characters": [{
                "role": "Ancient metalsmith shaping a gold ornament",
                "position": "Center, foreground, three-quarter view facing right",
                "demographics": {"gender": "Male", "race": "Black"},
                "appearance": {
                    "hair": "Short, close-cropped black hair",
                    "facial_expression": "Deeply focused, brow slightly furrowed, lips pressed together in concentration",
                    "clothing": "Rough woven wool tunic cinched with a thick leather belt, bare muscular forearms visible, leather wrist wraps for heat protection, a simple gold wedding band on left ring finger"
                },
                "actions": [
                    "Hammering a small gold disc on a flat stone anvil with a bone tool in his right hand",
                    "Left hand steadying the gold piece with a wooden clamp",
                    "Leaning slightly forward over the workbench toward the firelight"
                ]
            }],
            "key_objects": [
                {
                    "item": "Gold ornamental disc",
                    "location": "On the stone anvil under the character's tools",
                    "details": "Small, roughly circular, gleaming warm yellow against the dark stone, partially shaped with spiral pattern emerging"
                },
                {
                    "item": "Clay hearth",
                    "location": "To the right of the workbench",
                    "details": "Low clay furnace with glowing orange coals, providing the only major light source in the dim workshop"
                }
            ],
            "environment_details": {
                "architecture": "Simple timber and thatch workshop, rough stone floor, animal skins hanging on walls, clay pots in corners",
                "lighting": [
                    "Warm orange glow from the clay hearth casting strong shadows across the character's face and arms",
                    "Faint cool daylight filtering through a gap in the thatch roof above",
                    "Deep shadows in the corners of the workshop"
                ]
            },
            "narrative_context": "The ancient metalsmith works gold with primitive tools — the oldest craft in human metalworking, requiring no smelting."
        }
    })),

    # T02: Joseph + Jess — couple at a 1930s bank
    ("T02_joseph_jess", ["joseph", "jess"], json.dumps({
        "image_description": {
            "ref_characters": ["joseph", "jess"],
            "metadata": {
                "art_style": "Boondocks-style animation, graphic novel illustration, dramatic warm tones",
                "setting": "Small-town American bank interior, 1930s Great Depression era",
                "mood": "Tense, anxious, financially desperate but dignified",
                "color_palette": ["Dusty brown", "Faded cream", "Dark wood", "Warm amber", "Muted olive"]
            },
            "main_characters": [
                {
                    "role": "Husband making mortgage payment at bank counter",
                    "position": "Center-left, foreground",
                    "demographics": {"gender": "Male", "race": "Black"},
                    "appearance": {
                        "hair": "Short, close-cropped black hair",
                        "facial_expression": "Worried but composed, jaw set with quiet determination, eyes looking down at the counter",
                        "clothing": "Worn brown wool suit jacket over a faded white collared shirt buttoned to the top, no tie, patched at the elbows, a simple gold wedding band on left ring finger"
                    },
                    "actions": [
                        "Sliding a small stack of coins across the wooden bank counter with his right hand",
                        "Left hand resting protectively on a folded mortgage document",
                        "Standing upright with squared shoulders despite the anxiety"
                    ]
                },
                {
                    "role": "Wife standing beside her husband at the bank counter",
                    "position": "Center-right, slightly behind the male character",
                    "demographics": {"gender": "Female", "race": "Black"},
                    "appearance": {
                        "hair": "Natural curly black hair pulled back under a simple cloth headwrap",
                        "facial_expression": "Quiet concern, lips pressed together, eyes watching the teller's reaction",
                        "clothing": "Simple 1930s cotton print dress with small floral pattern, a worn cardigan sweater over it, practical lace-up shoes, a modest diamond engagement ring on left ring finger"
                    },
                    "actions": [
                        "Standing close to her husband with her hand resting lightly on his left arm",
                        "Holding a small cloth purse in her other hand",
                        "Slight forward lean as if trying to read the teller's expression"
                    ]
                }
            ],
            "background_characters": [{
                "description": "Bank teller behind the counter, older white man",
                "clothing": "White dress shirt with rolled sleeves, dark suspenders, wire-rimmed glasses",
                "actions": "Looking down at the small stack of coins on the counter with a neutral bureaucratic expression"
            }],
            "key_objects": [{
                "item": "Mortgage document",
                "location": "On counter under the husband's left hand",
                "visible_text": ["MORTGAGE", "PAST DUE"],
                "details": "Yellowed paper with typed text and a red stamp mark, edges worn from handling"
            }],
            "environment_details": {
                "architecture": "Small-town bank with dark wood paneling, teller cage with brass bars, scuffed wooden floor, a single ceiling fan",
                "lighting": [
                    "Single overhead pendant lamp casting a warm cone of light directly on the counter",
                    "Dim natural light from a frosted window to the right",
                    "Deep shadows in the far corners emphasizing the claustrophobic atmosphere"
                ]
            },
            "narrative_context": "A couple brings their savings to the bank during the Depression, trying to keep their farm from foreclosure."
        }
    })),

    # T03: Joseph + Sola + Brayden — father with children at a market
    ("T03_joseph_kids", ["joseph", "sola", "brayden"], json.dumps({
        "image_description": {
            "ref_characters": ["joseph", "sola", "brayden"],
            "metadata": {
                "art_style": "Boondocks-style animation, graphic novel illustration, bold linework",
                "setting": "Bustling open-air gold market, ancient Mediterranean city circa 600 BCE",
                "mood": "Warm, educational, a father teaching his children about the world",
                "color_palette": ["Warm gold", "Terracotta red", "Sandy beige", "Deep teal", "Sun-bleached white"]
            },
            "main_characters": [
                {
                    "role": "Father showing his children a gold coin at the market",
                    "position": "Center, foreground, standing tall",
                    "demographics": {"gender": "Male", "race": "Black"},
                    "appearance": {
                        "hair": "Short, close-cropped black hair",
                        "facial_expression": "Warm, patient, a slight knowing smile as he teaches",
                        "clothing": "Ancient Mediterranean linen tunic dyed deep blue, leather sandals, a woven rope belt with a small leather coin pouch, a simple gold wedding band on left ring finger"
                    },
                    "actions": [
                        "Holding a small gold coin between his right thumb and forefinger, angled so the children can see it catch the sunlight",
                        "Left hand resting on his son's shoulder",
                        "Looking down at the children with an encouraging expression"
                    ]
                },
                {
                    "role": "Daughter looking up at the gold coin with curiosity",
                    "position": "Left of center, foreground, standing beside her father",
                    "demographics": {"gender": "Female", "race": "Black"},
                    "appearance": {
                        "hair": "Dark curly hair pulled up in a high bun with a thin cloth ribbon",
                        "facial_expression": "Wide-eyed fascination, mouth slightly open in wonder, leaning forward on her toes",
                        "clothing": "Simple child-sized linen tunic in a warm terracotta color, rope sandals, a small beaded necklace"
                    },
                    "actions": [
                        "Reaching one hand up toward the coin her father is holding",
                        "Standing on her toes to get a better look",
                        "Other hand holding a small clay toy"
                    ]
                },
                {
                    "role": "Son standing beside his father, studying the coin seriously",
                    "position": "Right of center, foreground, under his father's arm",
                    "demographics": {"gender": "Male", "race": "Black"},
                    "appearance": {
                        "hair": "Short close-cropped black hair",
                        "facial_expression": "Serious and thoughtful for his age, brow slightly furrowed in concentration, studying the coin intently",
                        "clothing": "Simple child-sized linen tunic in off-white, leather sandals, a small leather pouch on a cord around his neck"
                    },
                    "actions": [
                        "Looking up at the gold coin with focused attention",
                        "One hand on his father's belt for stability",
                        "Slight lean forward, mimicking his father's posture"
                    ]
                }
            ],
            "background_characters": [{
                "description": "Market vendors and shoppers in ancient Mediterranean clothing",
                "clothing": "Various colored linen tunics, leather sandals, head wraps",
                "actions": "Trading goods, carrying baskets, animated conversations at stalls"
            }],
            "key_objects": [{
                "item": "Gold coin",
                "location": "Held between the father's right thumb and forefinger, catching sunlight",
                "details": "Small, round, stamped with an ancient lion-head design, gleaming warm yellow in the sun"
            }],
            "environment_details": {
                "architecture": "Open-air market with cloth awnings over wooden stalls, stone-paved ground, clay jars and baskets of goods visible, distant temple columns",
                "lighting": [
                    "Bright Mediterranean midday sunlight casting sharp shadows under the awnings",
                    "Warm reflected light bouncing off the sandy stone pavement",
                    "The gold coin catching a bright highlight from direct sun"
                ]
            },
            "narrative_context": "A father teaches his children about the value of gold at an ancient marketplace — the next generation learning the meaning of money."
        }
    })),

    # T04: Full family — Joseph + Jess + Sola + Brayden — 1970s living room
    ("T04_full_family", ["joseph", "jess", "sola", "brayden"], json.dumps({
        "image_description": {
            "ref_characters": ["joseph", "jess", "sola", "brayden"],
            "metadata": {
                "art_style": "Boondocks-style animation, graphic novel illustration, warm domestic tones",
                "setting": "American family living room, 1971, evening",
                "mood": "Warm, intimate, a quiet family moment with undercurrent of historic gravity",
                "color_palette": ["Warm brown", "Mustard yellow", "Avocado green", "Burnt orange", "Cream white"]
            },
            "main_characters": [
                {
                    "role": "Father sitting in an armchair watching the television broadcast",
                    "position": "Right of center, middle ground, seated in armchair facing slightly left toward TV",
                    "demographics": {"gender": "Male", "race": "Black"},
                    "appearance": {
                        "hair": "Short, close-cropped black hair",
                        "facial_expression": "Attentive and serious, brow slightly raised, processing what he is hearing on the broadcast",
                        "clothing": "1970s casual home attire — short-sleeve collared shirt in a muted olive color, brown slacks, house slippers, a simple gold wedding band on left ring finger"
                    },
                    "actions": [
                        "Sitting forward in his armchair with elbows on his knees",
                        "Right hand holding a folded newspaper that he has stopped reading to watch the TV",
                        "Eyes locked on the television screen"
                    ]
                },
                {
                    "role": "Mother sitting on the couch beside the children",
                    "position": "Left of center, middle ground, seated on a couch facing the TV",
                    "demographics": {"gender": "Female", "race": "Black"},
                    "appearance": {
                        "hair": "Natural curly black afro, medium length, styled in a 1970s natural",
                        "facial_expression": "Politely attentive but slightly confused, head tilted, trying to understand the broadcast",
                        "clothing": "1970s house dress in a warm mustard yellow with a subtle pattern, comfortable house shoes, a modest diamond engagement ring on left ring finger"
                    },
                    "actions": [
                        "Sitting on the couch with her daughter leaning against her side",
                        "One arm around her daughter's shoulders",
                        "Other hand resting on the couch arm, watching the TV with quiet attention"
                    ]
                },
                {
                    "role": "Daughter leaning against her mother on the couch",
                    "position": "Left, middle ground, curled up against her mother on the couch",
                    "demographics": {"gender": "Female", "race": "Black"},
                    "appearance": {
                        "hair": "Dark curly hair in two puff ponytails with colorful barrettes",
                        "facial_expression": "Sleepy and bored, eyes half-closed, not interested in the broadcast",
                        "clothing": "1970s children's pajamas with a simple floral print, bare feet tucked under her"
                    },
                    "actions": [
                        "Leaning against her mother's side with her head on her mother's arm",
                        "Holding a small stuffed animal in her lap",
                        "Eyes drifting closed, nearly asleep"
                    ]
                },
                {
                    "role": "Son sitting on the floor between his parents, watching TV",
                    "position": "Center foreground, sitting cross-legged on the carpet facing the TV",
                    "demographics": {"gender": "Male", "race": "Black"},
                    "appearance": {
                        "hair": "Short close-cropped black hair",
                        "facial_expression": "Curious but restless, glancing between the TV and a toy in his hands",
                        "clothing": "1970s children's clothing — striped t-shirt in brown and orange, corduroy pants, white socks"
                    },
                    "actions": [
                        "Sitting cross-legged on the shag carpet between his father's armchair and the couch",
                        "Holding a small toy car in one hand but looking up at the TV",
                        "Fidgeting slightly, restless energy of a child told to sit still"
                    ]
                }
            ],
            "key_objects": [
                {
                    "item": "1970s television set",
                    "location": "Left foreground, partially visible, the screen glowing toward the family",
                    "details": "Bulky wood-cabinet console TV with dials, screen showing a blurry image of a man at a podium, warm cathode glow illuminating the room"
                },
                {
                    "item": "Living room decor",
                    "location": "Background walls and surfaces",
                    "details": "Wood-paneled walls, a framed family photo, a table lamp with an orange shade, a potted plant on a side table"
                }
            ],
            "environment_details": {
                "architecture": "1970s American middle-class living room with wood paneling, shag carpet in avocado green, a doorway to a kitchen visible in background",
                "lighting": [
                    "Warm glow from the television screen illuminating all four family members' faces",
                    "A table lamp with an orange shade casting warm ambient light from the right",
                    "Dim evening light suggesting drawn curtains, the room is cozy and enclosed"
                ]
            },
            "narrative_context": "A family watches Nixon announce the end of the gold standard on television in 1971 — a historic moment experienced as an ordinary evening at home."
        }
    })),
]


def generate_image(name, characters, prompt, api_key):
    """Generate a single image using Gemini with multi-character references."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    try:
        contents = []
        for char in characters:
            if char in REF_IMAGES:
                contents.append(types.Part.from_bytes(
                    data=REF_IMAGES[char]["bytes"],
                    mime_type=REF_IMAGES[char]["mime"],
                ))
        if contents:
            ref_desc = ", ".join(_CHARACTER_LABELS[c] for c in characters if c in _CHARACTER_LABELS)
            ring_note = ""
            if "joseph" in characters or "jess" in characters:
                ring_note = " Note: Joseph wears a simple gold wedding band on his left ring finger. Jess wears a modest diamond ring on her left ring finger. The rings are subtle, not shiny or sparkly — just there."
            contents.append(
                f"Using the attached images as character references ({ref_desc}), "
                f"generate this scene in the EXACT same art style (Boondocks-style animation, "
                f"bold linework, flat cel-shading). Each character must look like their reference.{ring_note} "
                f"Scene: {prompt}"
            )
        else:
            contents = [f"Generate this scene: {prompt}"]

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                temperature=0.7,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                image_config=types.ImageConfig(
                    image_size="4K",
                    aspect_ratio="16:9",
                ),
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_data = part.inline_data.data
                mime = part.inline_data.mime_type
                ext = "png" if "png" in mime else "jpg"
                out_path = OUT_DIR / f"{name}.{ext}"
                if isinstance(img_data, str):
                    img_bytes = base64.b64decode(img_data)
                else:
                    img_bytes = img_data
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  OK {name} → {out_path} ({len(img_bytes) // 1024} KB)")
                return name, str(out_path), ext
        return name, None, "No image in response"
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        return name, None, str(e)


def main():
    print(f"\n=== Generating {len(IMAGES)} test images using {MODEL} ===\n")
    print(f"Output directory: {OUT_DIR}\n")

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(IMAGES), len(API_KEYS))) as executor:
        futures = {}
        for i, (name, characters, prompt) in enumerate(IMAGES):
            key = API_KEYS[i % len(API_KEYS)]
            print(f"  Launching {name} with refs: {characters}")
            futures[executor.submit(generate_image, name, characters, prompt, key)] = name

        for future in concurrent.futures.as_completed(futures):
            name, path, info = future.result()
            results[name] = (path, info)

    print(f"\n=== Summary ===")
    ok = sum(1 for p, _ in results.values() if p)
    print(f"  Generated: {ok}/{len(IMAGES)}")
    for name, (path, info) in sorted(results.items()):
        status = f"OK → {path}" if path else f"FAIL: {info}"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
