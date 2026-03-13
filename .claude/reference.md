# Project Reference

## Project Structure
```
MoneyMath/
├── .env                          # API keys (ElevenLabs + Gemini + GOOGLE_SHEET_ID)
├── client_secrets.json           # Google OAuth client credentials
├── token.pickle                  # YouTube API auth token
├── sheets_token.pickle           # Google Sheets API auth token
├── youtube_titles.md             # Permanent log of all uploaded titles + URLs
├── tools/
│   ├── generate_audio.py         # TTS pipeline (set PROJECT_NAME + SECTIONS)
│   ├── generate_images.py        # Image pipeline (set PROJECT_NAME + IMAGES)
│   ├── generate_music.py         # Background music pipeline (set PROJECT_NAME + MUSIC_PROMPT)
│   ├── calculate_timings.py      # Timing calculator (set PROJECT_NAME + SECTIONS)
│   ├── generate_thumbnail.py     # AI thumbnail generator (3 variations for A/B)
│   ├── cost_tracker.py           # Shared cost logging (auto-called by generators)
│   ├── upload_costs.py           # Push costs.json to Google Sheets
│   ├── youtube_auth.py           # Auth script (--check, --youtube, --sheets)
│   └── youtube_upload.py         # YouTube upload with playlist + scheduling
├── reference/
│   └── character.png             # Shared Boondocks-style character reference
├── src/
│   ├── index.ts, Root.tsx        # Remotion entry + composition registry
│   ├── helpers.tsx, motion.tsx   # Shared components + animation primitives
│   └── <project>/               # Project-specific Remotion source
├── public/
│   └── <project>/               # Symlinks only (audio/ + images/ → projects/)
└── projects/
    ├── <project>/               # Active project files live here
    │   ├── script.md
    │   ├── generate_audio.py, generate_images.py, generate_music.py, calculate_timings.py
    │   ├── generate_thumbnail.py
    │   ├── audio/, images/
    │   ├── thumbnail-1.png, thumbnail-2.png, thumbnail-3.png
    │   ├── costs.json
    │   └── reference/ (optional)
    └── completed/               # Finished projects moved here after YouTube upload
        └── <project>/           # Same structure as active projects
```

**Rule: Every file produced for a project must live in `projects/<project>/`.** The `public/<project>/` directory contains only symlinks.

---

## Script Reference — What Each Script Contains

### `generate_audio.py` — TTS Narration
Generates spoken narration MP3s from script text using ElevenLabs TTS.
- **Configure**: `PROJECT_NAME`, `SECTIONS` (list of `(filename, narration_text)` tuples)
- **Defaults**: Voice `qI0RnYbkDdDRolu3NKE2`, model `eleven_multilingual_v2`, speed 1.1
- **Voice settings**: stability 0.50, similarity_boost 0.65, style 0.10, speaker_boost on
- **Output**: `projects/<project>/audio/s1_hook.mp3`, `s2_setup.mp3`, etc.
- **Skip logic**: Existing files are skipped automatically — safe to re-run

### `generate_images.py` — AI Image Generation
Generates visual images using Google Gemini with a reference character.
- **Configure**: `PROJECT_NAME`, `IMAGES` (list of `(filename, prompt)` tuples), `CHAR`, `STYLE`
- **Model**: `gemini-3.1-flash-image-preview`
- **Reference image**: `USE_REF_IMAGE = True` by default — sends `reference/character.png` as multimodal input for character consistency
- **Character dress rule**: `CHAR` describes only the character's base identity (face, skin tone, body type) — no fixed clothing. Each individual image prompt must specify scene-appropriate attire. The character must dress and appear consistent with the scene's historical period, setting, and cultural context. A character in an ancient Mesopotamian scene wears period-accurate clothing. A character in a modern office scene wears contemporary clothes. Never leave the character's clothing undefined — it will default to something inconsistent with the scene.
- **Character presence rule**: The character must appear in every image. No image should be objects-only. When the scene is a document, storefront, chart, artifact, or historical setting, the character is present in the frame — reacting to it, examining it, standing near it, or observing it. His position and prominence still depend on the scene: background observer, peripheral figure, member of a crowd, leaning over a document, walking past a storefront. He is always present but not always the centerpiece.
- **API keys**: Round-robin across multiple Gemini keys with 15s batch delays
- **Output**: `projects/<project>/images/H01.png`, `S01.png`, etc.
- **Skip logic**: Existing files are skipped automatically — safe to re-run

### `generate_music.py` — Background Music
Generates instrumental background music using ElevenLabs Music API.
- **Configure**: `PROJECT_NAME`, `MUSIC_PROMPT` (text description of desired music), `MUSIC_LENGTH_MS` (duration in ms, default 300000 = 5 min)
- **Model**: `music_v1`, forced instrumental (no vocals)
- **Output**: `projects/<project>/audio/music_bg.mp3`
- **Skip logic**: Existing file is skipped automatically — safe to re-run
- **Channel standard prompt**: Lo-fi hip-hop neo-soul, warm muted Rhodes piano, soft boom-bap drums, subtle deep bass, light vinyl crackle. Contemplative and intimate with forward momentum. Minor key that opens to hopeful. 98 BPM. No vocals. Use this as the default unless the topic calls for a different vibe.
- **Important**: Do NOT reference specific artist names in the prompt — ElevenLabs content filter will reject it. Use genre/style descriptions instead.
- **After generation**: Always kill and restart Remotion Studio to clear audio cache (`pkill -f remotion` then `npm start`)

### `calculate_timings.py` — Visual Timing Calculator
Reads audio file durations and distributes frames across visuals per section.
- **Configure**: `PROJECT_NAME`, `SECTIONS` (maps section names to audio files and visual counts)
- **Input**: Reads MP3 durations from `projects/<project>/audio/`
- **Output**: Prints `VISUAL_TIMINGS` array, `AUDIO_SECTIONS` config, and `TOTAL_FRAMES` — paste these into Remotion source files
- **Depends on**: Audio files must exist first (run `generate_audio.py` before this)

### `generate_thumbnail.py` — AI Thumbnail Generator
Generates 3 YouTube thumbnail variations using Gemini with the reference character.
- **Input**: `projects/<project>/script.md` (reads THUMBNAIL TEXT and [THUMBNAIL] scenes block)
- **Model**: `gemini-3.1-flash-image-preview` (fallback: `gemini-3-pro-image-preview`)
- **Reference image**: Sends `reference/character.png` as multimodal input
- **Output**: `projects/<project>/thumbnail-{1,2,3}.png` (4K, 16:9)
- **Design**: Load the `/youtube-thumbnails` skill before writing the `[THUMBNAIL]` block. The skill's 6-step process drives all text selection, scene direction, character expression, and composition decisions. Do not write scenes without it.
- **Character dress**: Specified per scene. Clothing must be appropriate to the historical period or context of the video — ancient robes for ancient history, period dress for historical topics, modern clothes for contemporary topics. Never defaults to grey suit unless the topic is explicitly modern/corporate.
- **Rules**: No charts, arrows, math equations, or floating icons beyond what the scene requires.
- **Cost**: $0.24 per image ($0.72 total for 3 thumbnails)

---

## Defaults
| Setting | Value |
|---------|-------|
| Voice ID | `qI0RnYbkDdDRolu3NKE2` |
| Voice Model | `eleven_multilingual_v2` |
| Voice Speed | 1.1 |
| Image Model | `gemini-3.1-flash-image-preview` |
| Reference Image | `reference/character.png` |
| Resolution | 1920x1080 @ 30fps |
