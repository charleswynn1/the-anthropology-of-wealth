# Gemini Flash Image Prompting

Generate structured JSON prompts for the Gemini 3.1 Flash Image Preview model (`gemini-3.1-flash-image-preview`). Every prompt includes one or more reference images and a detailed JSON scene description. The JSON is sent as the text content alongside reference image(s) as `inline_data` parts.

This is a prompt engineering reference for the video pipeline's image generation step (W3b). The JSON format ensures every element (characters, objects, environment, lighting, narrative context) is explicitly specified, producing more consistent and accurate results than prose descriptions.

## JSON Prompt Schema

The core structure for every image prompt:

```json
{
  "image_description": {
    "metadata": {
      "art_style": "Boondocks-style animation, graphic novel illustration",
      "setting": "Description of location and time period",
      "mood": "Emotional tone of the scene",
      "color_palette": ["Color 1", "Color 2", "Color 3", "Color 4"]
    },
    "main_characters": [
      {
        "role": "Character's role in scene",
        "position": "Where in frame (Left/Right/Center, foreground/background)",
        "demographics": {
          "gender": "Male/Female",
          "race": "Ethnicity"
        },
        "appearance": {
          "hair": "Style, color, length",
          "facial_expression": "Specific expression with emotional detail",
          "clothing": "Period-accurate, scene-specific — NEVER generic"
        },
        "actions": [
          "Primary action",
          "Secondary action/posture",
          "What they're holding or interacting with"
        ]
      }
    ],
    "background_characters": [
      {
        "description": "Brief description of background figures",
        "clothing": "Period-appropriate attire",
        "actions": "What they're doing"
      }
    ],
    "key_objects": [
      {
        "item": "Object name",
        "location": "Where in the scene",
        "visible_text": ["Text rendered on the object (if any)"],
        "details": "Material, condition, size, distinguishing features"
      }
    ],
    "environment_details": {
      "architecture": "Walls, floors, structures, materials",
      "lighting": [
        "Primary light source and quality",
        "Secondary/accent lighting",
        "Ambient light description"
      ]
    },
    "narrative_context": "One sentence explaining what is happening in the story at this moment — what the narration is saying while this image is on screen."
  }
}
```

### Field-by-Field Guide

- **metadata.art_style** — Always starts with "Boondocks-style animation" (this is the only valid starting phrase). Additional descriptors follow after a comma (e.g., "Boondocks-style animation, graphic novel illustration"). NEVER use "photorealistic", "photography style", "documentary photography", or "macro photography". These photography terms override the animation instruction and produce hyper-realistic images.
- **metadata.setting** — Specific location and era. Examples: "Vintage bank interior, late 19th century", "Potosi silver mine entrance, 1590", "Modern suburban kitchen, present day". Vague settings produce vague images.
- **metadata.mood** — The emotional register of the scene: "Serious, dramatic, transactional", "Tense, claustrophobic", "Hopeful, warm". Drives character expressions and lighting choices.
- **metadata.color_palette** — 3-5 dominant colors. Drives visual consistency across the scene. Choose colors that support the mood and setting.
- **main_characters[].appearance.clothing** — MUST be period/scene-specific. Never leave undefined. A character in 1590 Potosi wears rough Andean clothing. A character in a modern bank wears a contemporary suit. A character in ancient Mesopotamia wears a linen tunic. Undefined clothing defaults to something inconsistent with the scene.
- **main_characters[].actions** — Array of 2-3 specific physical actions. Not vague ("standing there") but precise ("Handing a document to the teller with his right hand", "Leaning forward over the counter examining a ledger").
- **key_objects[].visible_text** — Any text that should appear rendered in the image (document titles, signs, labels, amounts on checks). Gemini 3.1 Flash excels at text rendering when explicitly requested.
- **environment_details.lighting** — Array of specific light sources. Not "well lit" but "Wall-mounted brass gas-style lamps with glass shades emitting warm light". Lighting drives the entire mood of the image.
- **narrative_context** — The bridge between image and narration. What story moment does this image illustrate? This field is checked during W8b visual sync review to verify the image matches the words being spoken.

### Optional Fields

- **background_characters** — Omit if no background figures are needed. Include when the scene calls for crowds, bystanders, workers, etc.
- **key_objects[].visible_text** — Omit if no text should appear in the image. Include for documents, signs, currency, labels.

## Reference Image Integration

How reference images are sent alongside the JSON prompt in the pipeline:

**Python (current pipeline):**
```python
import json

contents = [
    types.Part.from_bytes(data=REF_IMAGE_BYTES, mime_type=REF_MIME),
    f"Using the attached image as a character reference, generate this scene in the EXACT same art style (Boondocks-style animation, bold linework, flat cel-shading). The character in every image must look like the man in the reference. Scene: {json.dumps(prompt_json)}"
]
```

**REST equivalent:**
```json
{
  "contents": [{
    "parts": [
      {"inline_data": {"mime_type": "image/png", "data": "<BASE64_REF_IMAGE>"}},
      {"text": "Using the attached image as a character reference, generate this scene in the EXACT same art style (Boondocks-style animation, bold linework, flat cel-shading). The character in every image must look like the man in the reference. Scene: {JSON}"}
    ]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE", "TEXT"],
    "temperature": 0.7,
    "imageConfig": {"imageSize": "4K", "aspectRatio": "16:9"}
  }
}
```

**Rules for reference images:**
- The project's character reference (`reference/character.png`) is ALWAYS included as the first content part
- Up to 14 reference images total (10 objects + 4 characters for Gemini 3.1 Flash)
- Additional reference images can be included for specific objects, settings, or style references that need high-fidelity reproduction
- Each reference image is a separate `inline_data` part before the text prompt
- MIME type must match the actual image format (image/png, image/jpeg, image/webp)

## Art Style Rules

Non-negotiable rules that override everything else.

### Banned Terms

These produce hyper-realistic output that breaks the animation style:

| Banned Term | Why | Replace With |
|---|---|---|
| photorealistic | Overrides animation style | (omit entirely — style is set by reference image) |
| photography style | Forces photo-real rendering | illustrated style |
| documentary photography | Photo-real documentary look | documentary illustration |
| macro photography | Photo-real close-up | extreme close-up illustration |
| photograph / photo | Implies camera-captured | illustration / scene |
| National Geographic quality | Photo-real nature style | cinematic illustrated quality |
| HDR | Photo processing term | dramatic lighting |
| bokeh | Camera lens effect | soft background blur |
| DSLR / mirrorless | Camera hardware reference | (omit) |

### Required in metadata.art_style

- Must always start with "Boondocks-style animation" — this is the only valid starting phrase, no alternatives
- Follow with scene-appropriate qualifiers after a comma: "graphic novel illustration", "bold linework", "dramatic warm tones", "flat cel-shading"
- Example: `"Boondocks-style animation, dramatic warm tones, bold linework"`
- Prompt endings for non-JSON legacy prompts must use language like "Bold illustrated style, warm dramatic lighting" or "Cinematic animated illustration" — never photography terms

## Character Presence Rules

- The reference character MUST appear in every image — no objects-only shots
- His role in `main_characters` specifies position, clothing, expression, and actions for THIS specific scene
- Clothing is NEVER generic or fixed — it matches the historical period, setting, and cultural context of the scene
- Character prominence depends on scene type:
  - **Personal/emotional moments** — foreground, center frame, large in composition
  - **Historical/data scenes** — background, peripheral, observing, examining
  - **Object/artifact scenes** — character interacts with the object (examining, holding, standing beside)
  - **Crowd/market scenes** — character as one figure among many, identifiable by reference features

## API Configuration

Default configuration used by the pipeline (`tools/generate_images.py`):

| Parameter | Value |
|---|---|
| **Model** | `gemini-3.1-flash-image-preview` |
| **Resolution** | 4K |
| **Aspect ratio** | 16:9 |
| **Temperature** | 0.7 |
| **Response modalities** | IMAGE, TEXT |
| **Google Search grounding** | Enabled (for historical accuracy) |
| **Thinking level** | Minimal (default) — set to "high" for complex multi-element scenes |
| **Cost** | ~$0.151 per 4K image |

**Available aspect ratios:** 1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9

**Available resolutions:** 512, 1K, 2K, 4K

**Cost rule:** Prompts must be precise the first time. The API CALL RULE states: never call more than once per file. These API calls cost money — treat every call as final.

## Pipeline Integration

The JSON prompts are stored as the prompt value in Python tuples inside `generate_images.py`:

```python
import json

IMAGES = [
    # ── s1_hook (H01-H03) ──
    # Narration: farmer takes mortgage to bank, pays with wheat sale coins

    ("H01", json.dumps({
        "image_description": {
            "metadata": {
                "art_style": "Boondocks-style animation, graphic novel illustration",
                "setting": "Rural bank interior, 1930s Oklahoma",
                "mood": "Tense, anxious, financially desperate",
                "color_palette": ["Dusty brown", "Faded cream", "Dark wood", "Warm amber"]
            },
            "main_characters": [{
                "role": "Farmer making mortgage payment",
                "position": "Center-left, foreground",
                "demographics": {"gender": "Male", "race": "Black"},
                "appearance": {
                    "hair": "Short, close-cropped black hair",
                    "facial_expression": "Worried, tight-lipped, brow furrowed",
                    "clothing": "Worn denim overalls over a faded cotton work shirt, dusty boots"
                },
                "actions": [
                    "Placing a small stack of coins on the bank counter",
                    "Left hand resting flat on a folded mortgage document",
                    "Slight forward lean toward the teller window"
                ]
            }],
            "background_characters": [{
                "description": "Bank teller, older white man",
                "clothing": "White dress shirt with rolled sleeves, suspenders",
                "actions": "Looking down at the coins with a skeptical expression"
            }],
            "key_objects": [{
                "item": "Mortgage document",
                "location": "On counter under character's left hand",
                "visible_text": ["MORTGAGE", "PAST DUE"],
                "details": "Yellowed paper with typed text, red stamp mark"
            }],
            "environment_details": {
                "architecture": "Small-town bank with dark wood paneling, teller cage with brass bars, scuffed wooden floor",
                "lighting": [
                    "Single overhead pendant lamp casting a warm cone of light on the counter",
                    "Dim ambient light from a frosted window to the right",
                    "Deep shadows in the corners of the room"
                ]
            },
            "narrative_context": "The farmer brings his wheat sale earnings to the bank to make his mortgage payment."
        }
    })),

    ("H02", json.dumps({...})),
]
```

### Naming Convention

- Section prefix + 2-digit number: H=hook, S=setup, D=data, etc.
- Prefix letters are project-specific — derive from section names in the script
- Order in the IMAGES list = order images appear in the video (narration sequence)

### Image Count Per Clip

`ceil(actual_audio_seconds / 7)` — computed in W4 from real MP3 durations. Never guess image counts before audio is generated.

### Narrative Context Verification

The `narrative_context` field must match the exact narration words spoken during this image's display time. This is verified during W8b visual sync review by `tools/verify_visual_sync.py`.

## Prompt Quality Checklist

Before finalizing each JSON prompt, verify:

1. **metadata.art_style** — Starts with "Boondocks-style animation". Zero photography terms anywhere in the entire prompt.
2. **main_characters** — Reference character is present with period-specific clothing and 2-3 specific actions.
3. **main_characters[].appearance.clothing** — Explicitly described, historically accurate, not generic. Never "casual clothes" or "normal outfit".
4. **key_objects** — Every important object named, located, and detailed. `visible_text` specified if text should appear in the image.
5. **environment_details.lighting** — At least one specific light source described (not just "well lit" or "bright").
6. **narrative_context** — Matches the exact narration moment this image covers. Verified during W8b.
7. **No duplicate compositions** — This image looks distinct from the previous and next image in sequence. Vary camera angle, character position, or environment.
8. **No anachronisms** — Clothing, architecture, objects, and technology match the stated time period.
9. **metadata.color_palette** — 3-5 colors that support the mood and setting. No palette should repeat identically across consecutive images.
