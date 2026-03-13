# The Anthropology of Wealth — Automated Video Pipeline

When the user gives a topic, execute the ENTIRE pipeline below from start to finish with ZERO human input. Stop after launching Remotion preview. NEVER render the final video without explicit user permission.

**MEMORY RULE: Never use the memory system. If a rule or preference needs to be remembered, add it to this CLAUDE.md file instead.**

**VISUAL SYNC RULE: Images must match the narration playing beneath them. Do NOT assign one audio file per section and distribute images evenly — that guarantees mismatches. Instead, split each section's narration into clips at every visual topic change. Each clip is its own audio file (e.g., `s7_potosi`, `s7_seigniorage`, `s7_loans`) and gets its own image set. Images are only distributed evenly within a single clip, so they stay locked to the right words. A "visual topic change" is any moment where the scene, subject, time period, or concept shifts enough that the current images would look wrong.**

**IMAGE COUNT RULE: Never guess image counts. Images are generated AFTER audio — W3b does not start until W4 is complete and exact clip durations are known from ElevenLabs. For each clip, images = ceil(actual_seconds / 7). Update `generate_images.py` with the final image counts after running `calculate_timings.py`, then run W3b.**


**MEASUREMENTS RULE: All measurements in narration must use US units — Fahrenheit (not Celsius), feet/miles (not meters/kilometers), ounces/pounds (not grams/kilograms). Convert at the time of writing: e.g., "1768°C" → "thirty two hundred and fourteen degrees Fahrenheit", "3.5 grams" → "about an eighth of an ounce".**

**DATE FORMAT RULE: Never write BC, AD, BCE, or CE in narration. For ancient dates, write the full phrase: "630 BC" → "six hundred thirty years before Christ", "300 AD" → "three hundred years after Christ's death". For years from roughly 1000 AD onward, just say the year naturally with no era suffix: "1600" → "sixteen hundred", "1776" → "seventeen seventy six", "2008" → "two thousand eight".**

**IMAGE STYLE RULE: Never write "photorealistic", "photography style", "documentary photography", or "macro photography" in image prompts. All images must be in the Boondocks-style animation art style. Photography-style keywords override the animation instruction and produce hyper-realistic images.**

**IMAGE PROMPT FORMAT RULE: All image prompts MUST use the structured JSON format defined in the `/gemini-flash-image-prompting` skill. Load the skill before writing any image prompts. Every prompt is a `json.dumps()` call wrapping the `image_description` JSON object — never flat prose strings. The JSON schema ensures every element (characters, objects, environment, lighting, narrative context) is explicitly specified. Run every prompt through the skill's Prompt Quality Checklist before finalizing.**

**GOD NOT UNIVERSE RULE: Never personify "the universe" as an agent or decision-maker in narration. When attributing design, intention, or constraint to a higher power, use "God" instead. For example: "The universe constrained the choice" → "God constrained the choice".**

**CHARACTER CASTING RULE: The project has four reference characters. Joseph (`reference/joseph.png`) is the main male character and MUST appear in most or all images. Jess (`reference/jessw.png`) is the main female character — use her whenever a scene involves a woman or female figure. Sola (`reference/solaw.png`) represents girl children and Brayden (`reference/braydenw.png`) represents boy children — use them whenever a scene calls for kids. Use all four together ONLY when the scene explicitly calls for a family. Each image prompt's `ref_characters` array controls which reference images are sent to Gemini for that image. Joseph always wears a simple gold wedding band on his left ring finger. Jess always wears a modest diamond engagement ring on her left ring finger. The rings should be subtle and understated — not shiny, not sparkling, not a focal point. They are just there, part of who the characters are.**

**API CALL RULE: NEVER call the ElevenLabs or Gemini APIs more than once per file.** Audio and image generation scripts must only run once. If a file already exists, the scripts skip it automatically. Do NOT re-run generation scripts unless an API error occurred or the user explicitly asks to regenerate. These API calls cost money — treat every call as final.

## Pipeline Overview
```
         W1a name → W1b dirs → W1c research (Ph1→Ph2→Ph3) → W2 script → W2b check_script.py → W2c qualitative review
                                                                    │
                                                    ┌───────────────┴──────────────┐
                                                    ▼                              ▼
                                               W3a audio                     W3c music*
                                                    │                         (async)
                                                    ▼
                                               W4 timings  ← exact durations known here
                                                    │
                              ┌─────────────────────┴──────────────────────┐
                              ▼                                             ▼
                         W5a timing.ts                               W3b images  ← generated NOW with real counts
                              │                                             │
                              └──────────────────┬──────────────────────────┘
                                                 ▼
                                          W5b visuals.tsx
                                                 │
                                        W6a Composition.tsx ◄── W3d thumbnails
                                        W6b save scripts  (parallel with W6a)
                                                 │
                                          W7 Root.tsx → W8a verify → W8b preview ⏸
```
*Music (W3c) starts after Research Phase 3 — does not wait for the full script.

**PARALLEL EXECUTION RULE:** Steps within the same wave run simultaneously. Do not wait for one track to finish before starting another track in the same wave. Each track proceeds independently as soon as its own dependency is met.

## Automation Steps

When a new topic is given, execute the full pipeline below. Run parallel tracks simultaneously. Do not stop, do not ask questions, do not wait for confirmation between steps.

---

### WAVE 1 — Foundation (sequential)

**W1a: Choose a project name**
Convert the topic into a short kebab-case slug (e.g., "car-note-trap", "hidden-cost-of-debt"). This becomes `<project>` in all paths below.

**W1b: Create directories and symlinks**
```bash
cd /Users/charleswynn/Desktop/The Anthropology of Wealth
mkdir -p projects/<project>/audio projects/<project>/images
mkdir -p public/<project>
ln -s ../../projects/<project>/audio public/<project>/audio
ln -s ../../projects/<project>/images public/<project>/images
mkdir -p src/<project>
```

**W1c: Research the topic (Phase 1 → Phase 2 → Phase 3, sequential within)**

Read `research.md` in the project root. It contains all three research prompts. Execute them in order.

**Phase 1:** Copy the Phase 1 prompt, replace `[INSERT TOPIC]` with the actual topic, and execute it. Search the internet exhaustively across all 22 sections. Save the full output to `projects/<project>/topic_research.md`.

**Phase 2:** Once Phase 1 is saved, copy the Phase 2 prompt, replace `[INSERT TOPIC]`, and execute it using the Phase 1 output as context. Merge expansions into `projects/<project>/topic_research.md` — integrate under corresponding sections and replace the "WHAT I WOULD EMPHASIZE" section with the updated version. Do not create a separate file.

**Phase 3:** Once Phase 2 is merged, copy the Phase 3 prompt, replace `[INSERT TOPIC]`, and execute it using the full combined research as context. This phase makes an editorial decision — it does not add new facts. Append the output to `projects/<project>/topic_research.md` as `## PHASE 3: ANGLE SELECTION`. Do not modify earlier sections.

Every number in the script must be grounded in reality. Do not guess.

---

### WAVE 2 — Script (sequential, depends on W1c)

**W2: Write the script**

Read `script_writer.md` in the project root. Copy the prompt, replace all `[INSERT ...]` placeholders, and execute it.

The inputs map as follows:
- **RESEARCH DOSSIER** — Phase 1 + Phase 2 content from `topic_research.md`
- **CHOSEN VIDEO ANGLE** — the `## PHASE 3: ANGLE SELECTION` section from `topic_research.md`
- **STORY-FIRST VIDEO OUTLINE** — the Narrative Arc from Phase 3

The output must include:
1. Full script (voiceover-ready prose)
2. Suggested visuals by section
3. Chapter breakdown
4. 5 short-form clip moments
5. 3 alternate intros

Also include:
- TITLE (5 options — load the `/youtube-titles` skill and follow its process before writing these)
- THUMBNAIL TEXT (3-5 options)
- CORE IDEA
- KEY MONEY LESSON
- VIEWER TAKEAWAY
- IMAGE PROMPTS (Python tuples with structured JSON prompts ready for generate_images.py — use `/gemini-flash-image-prompting` schema)

Save the complete output to `projects/<project>/script.md`.

---

### W2b: Script Quality Check (runs immediately after W2, before launching Wave 3)

```bash
python3 tools/check_script.py <project>
```

**If FAILED: fix every violation before proceeding. Do not start Wave 3 until this passes.**

The checker catches all mechanically verifiable violations in narration text:
- Em dashes, en dashes, hyphens between words
- Digits instead of spelled-out numbers (`42` → `forty two`)
- Percent symbols or dollar signs (`%`, `$`)
- Missing fillers — warns if any section has no Okay/Hmm/Alright/Yeah

Setup transitions and staccato fragment stacks are not checked programmatically — they are caught in W2c below.

---

### W2c: Qualitative Script Review (runs after W2b passes, before launching Wave 3)

Read every narration section in `projects/<project>/script.md` and manually review for these two rules. Do not rely on pattern matching — read the text as a human reader would.

**Rule 1 — No setup transitions.** Flag any sentence whose only job is to announce that the next sentence will be important. Examples of violations:
- "Here is where this gets interesting." → delete it, start with the point
- "Now we come to the part that hits closest to home." → delete it, start the story
- "I want you to understand what this means." → delete it, state what it means
- "Here is the gut punch." → delete it, just deliver the gut punch
- "Let me bring you back to the beginning." → delete it, just go back
- "Here is what I want you to take from this." → delete it, state the takeaway

The test: if the sentence were deleted, would the paragraph lose any meaning? If no, delete it.

**Rule 2 — No staccato fragment stacks and no contrasting pairs.** This covers two related constructions:

*Staccato stacks* — three or more very short sentences stacked for rhetorical punch:
- "Natural. Compounding. Relentless." → rewrite as full prose: "The debt grew the same way, built into the structure, whether the harvest came in or not."
- "Same trap. Different century. Different name." → rewrite as a sentence

*Contrasting pairs* — two short sentences where the second reframes the first as a contrast, especially the "Not X. Y." construction:
- "Not an accident. A design." → banned in any form, including the merged version "This was not an accident. It was a deliberate design." The construction itself is a writing tic. Rewrite as a direct statement: "This was designed to work exactly this way."
- "Not your fault. A system." → "You did not build this system."
- "Same building. Different century." → "The building changed but the math did not."
- "Not bad luck. Bad math." → "The math was the problem, not the luck."

The test: is the sentence doing rhetorical work (setting up a contrast for effect) rather than conveying information? If yes, rewrite it as a direct statement that carries the same meaning without the performance.

**Process:**
1. Read each narration section top to bottom
2. List every violation found (section name, the offending text)
3. Fix each one in `script.md` before proceeding
4. If no violations found, state that explicitly and proceed to Wave 3

Do not start Wave 3 until W2c is complete and clean.

---

### WAVE 3 — Audio + Music (W3a and W3c run in parallel; W3b and W3d wait until after W4)

**W3b (images) and W3d (thumbnails) do NOT start here. Only audio and music run in Wave 3.**

---

**W3a: Generate audio** *(depends on W2 — needs narration text)*

Edit `tools/generate_audio.py`:
- Set `PROJECT_NAME = "<project>"`
- Replace `SECTIONS` with narration tuples from the script: `("s1_hook", """text...""")`
- **Split at every visual topic change** — any shift in scene, subject, time period, or concept gets its own audio file (e.g., `s7_potosi`, `s7_seigniorage`, `s7_loans`, `s7_milled_edges`). Never lump unrelated visuals under one audio file. The clip boundary is what keeps images in sync with words.

```bash
python3 tools/generate_audio.py
```
Outputs MP3s to `projects/<project>/audio/`. Verify all files were created.

**As soon as W3a finishes → immediately start W4.**

---

**W3c: Generate music** *(depends on W1c Phase 3 — tone and angle are known; does not require full script)*

Edit `tools/generate_music.py`:
- Set `PROJECT_NAME = "<project>"`
- Set `MUSIC_PROMPT` based on the topic's emotional tone and vibe from Phase 3 angle selection

```bash
python3 tools/generate_music.py
```
Outputs `music_bg.mp3` to `projects/<project>/audio/`. Runs in parallel — does not block any other track.

---

### WAVE 4 — Timings (starts when W3a finishes)

**W4: Calculate timings** *(depends on W3a — reads actual MP3 durations from ElevenLabs output)*

This is the source of truth for all image counts. Do not use estimates. Do not use word count. Use only the real file durations measured here.

Run `calculate_timings.py` with placeholder image counts first to get actual durations:
```python
SECTIONS = [
    ("hook",     [("s1_hook", 1)]),       # placeholder count — will update
    ("setup",    [("s2_setup", 1)]),
    # ... one entry per audio clip
]
```

```bash
python3 tools/calculate_timings.py
```

Read the actual seconds per clip from the output. Then compute final image count for each clip: `ceil(actual_seconds / 7)`. Update `SECTIONS` with the real counts and re-run:

```bash
python3 tools/calculate_timings.py
```

Capture the final VISUAL_TIMINGS array, AUDIO_SECTIONS config, and TOTAL_FRAMES.

**As soon as W4 finishes → immediately start W3b and W5a in parallel.**

---

**W3b: Generate images** *(depends on W4 — image counts come from actual audio durations)*

Now that exact clip durations are known, write the image prompts into `generate_images.py`. Each clip's images must depict only what that clip's narration describes — not other parts of the video.

**Before writing any prompts:** Load the `/gemini-flash-image-prompting` skill. All prompts must use the structured JSON format — `json.dumps({"image_description": {...}})` — never flat prose strings. Follow the skill's JSON Prompt Schema for every field and run each prompt through the Prompt Quality Checklist.

Edit `tools/generate_images.py`:
- Add `import json` at the top of the IMAGES section
- Set `PROJECT_NAME = "<project>"`
- Replace `IMAGES` with image prompt tuples grouped by clip: `("H01", ["joseph"], json.dumps({...}))`. The second element is the `ref_characters` list — which character references to send for this image (e.g., `["joseph"]`, `["joseph", "jess"]`, `["joseph", "sola", "brayden"]`, or `["joseph", "jess", "sola", "brayden"]` for family scenes). The number of prompts per clip = the count computed in W4. Write prompts in narration order — the order of prompts in the list determines the order images appear in the video. Do NOT order by filename or any other convention; order by the sequence of scenes in the narration.

```bash
python3 tools/generate_images.py
```
Outputs PNGs to `projects/<project>/images/`. Verify all files were created.

**As soon as W3b finishes → immediately start W5b.**

---

**W3d: Generate thumbnails** *(runs in parallel with W3b — depends on W4 being done so script is finalized)*

**Before running:** Load the `/youtube-thumbnails` skill and follow its full 6-step design process to create the `[THUMBNAIL]` block in `script.md`. The skill ensures every thumbnail makes a promise rather than describing the video, executes on 2-3 psychological constants (Curiosity, Contrast, Emotion, Conflict, Reward), and uses varied emotions and compositions across the 3 variations. Do not write the `[THUMBNAIL]` block without the skill.

```bash
python3 tools/generate_thumbnail.py <project>
```
Outputs 3 thumbnail variations to `projects/<project>/`. Does not block any other track.

**Thumbnail text rule:** Text must come from the THUMBNAIL TEXT options in `script.md` — never the channel name, never a generic placeholder. If you see "Money Math" or "The math behind the money", the script regex failed — fix it before proceeding.

---

### WAVE 5 — Source Files (W5a and W5b run on separate tracks, start independently)

**W5a: Create `src/<project>/timing.ts`** *(depends on W4)*

```ts
export const VISUAL_TIMINGS: number[][] = [
  // ── s0: hook (Xf) ──
  [N, N, N, ...],
  // ... one array per section
];
```

---

**W5b: Create `src/<project>/visuals.tsx`** *(depends on W3b — starts as soon as images are generated)*

Create one component per generated image, one export array per section:
```tsx
import React from "react";
import { Img, staticFile, AbsoluteFill } from "remotion";

const I: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill>
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
  </AbsoluteFill>
);

const P = "<project>/images/";

const H01 = () => <I src={`${P}H01.png`} />;
// ... one per image ...

export const hookVisuals = [H01, H02, ...];
export const setupVisuals = [S01, S02, ...];
// ... one export per section ...
```

---

### WAVE 6 — Assembly (W6a and W6b run in parallel)

**W6a: Create `src/<project>/<Composition>.tsx`** *(depends on W5a AND W5b — wait for both)*

Follow the exact pattern from `src/ten-dollar-day/TenDollarDay.tsx`:
**NO FADES RULE: Images cut hard — no fade-in, no fade-out, no opacity transitions between visuals.**

```tsx
import React from "react";
import { AbsoluteFill, Sequence, Audio, staticFile } from "remotion";
import { hookVisuals, setupVisuals, /* ... */ } from "./visuals";
import { VISUAL_TIMINGS } from "./timing";

const A = "<project>/audio/";

const ALL_VISUALS = [hookVisuals, setupVisuals, /* ... all section arrays */];

const SECTION_DURATIONS_F = VISUAL_TIMINGS.map((t) => t.reduce((s, v) => s + v, 0));
const SECTION_STARTS: number[] = [];
let runningFrame = 0;
for (const dur of SECTION_DURATIONS_F) { SECTION_STARTS.push(runningFrame); runningFrame += dur; }
const TOTAL_FRAMES = runningFrame;

const AUDIO_SECTIONS = [
  { file: "s1_hook", start: SECTION_STARTS[0], dur: N },
  // ... use exact frame durations from calculate_timings.py output
  // For split sections: { file: "s3_data_pt2", start: SECTION_STARTS[2] + prev_dur, dur: N }
];

export const CompositionName: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
    {ALL_VISUALS.map((visuals, secIdx) => {
      const timings = VISUAL_TIMINGS[secIdx];
      let localOffset = 0;
      return visuals.map((Visual, vIdx) => {
        const dur = timings[vIdx];
        const from = SECTION_STARTS[secIdx] + localOffset;
        localOffset += dur;
        return <Sequence key={`vis-${secIdx}-${vIdx}`} from={from} durationInFrames={dur}><AbsoluteFill><Visual /></AbsoluteFill></Sequence>;
      });
    })}
    {AUDIO_SECTIONS.map(({ file, start, dur }, i) => (
      <Sequence key={`nar-${i}`} from={start} durationInFrames={dur}>
        <Audio src={staticFile(`${A}${file}.mp3`)} volume={1} />
      </Sequence>
    ))}
    <Sequence from={0} durationInFrames={TOTAL_FRAMES}>
      <Audio src={staticFile(`${A}music_bg.mp3`)} volume={0.12} loop />
    </Sequence>
  </AbsoluteFill>
);
```

Key rules:
- Each audio Sequence must use exact clip duration (not TOTAL_FRAMES - start) to prevent double audio
- For split audio sections (e.g., data with multiple parts), offset the start by the sum of previous part durations
- Background music is optional — only include if `music_bg.mp3` exists

---

**W6b: Save project-specific scripts** *(depends on W3a + W3b + W3c + W4 — all scripts must be populated; runs parallel with W6a)*

```bash
cp tools/generate_audio.py projects/<project>/generate_audio.py
cp tools/generate_images.py projects/<project>/generate_images.py
cp tools/generate_music.py projects/<project>/generate_music.py
cp tools/calculate_timings.py projects/<project>/calculate_timings.py
```

---

### WAVE 7 — Registration (depends on W6a)

**W7: Register in `src/Root.tsx`**

```tsx
import { CompositionName } from "./<project>/<Composition>";

<Composition
  id="CompositionId"
  component={CompositionName}
  durationInFrames={TOTAL_FRAMES}
  fps={30}
  width={1920}
  height={1080}
/>
```

---

### WAVE 8 — Quality Gate + Preview (depends on W7)

**W8a: Verify timings**
```bash
python3 tools/verify_timings.py <project>
```
Checks that `timing.ts` is correct before launching the preview:
- Confirms total frames match actual audio file durations (within 1s tolerance)
- Flags any section where images show for more than 8 seconds — a sign there are too few visuals

**If warnings (images showing too long):** generate additional images for those sections, add them to `visuals.tsx`, update `SECTIONS` in `calculate_timings.py` with the new image counts, re-run `calculate_timings.py`, update `timing.ts` and `AUDIO_SECTIONS`, then re-run `verify_timings.py`.

**If errors (frame drift > 1s):** re-run `calculate_timings.py` and update `timing.ts` before proceeding.

**W8b: Visual sync review (qualitative — must be done by Claude, not a script)**

This is a manual, semantic review. Run the report tool to get a side-by-side view:
```bash
python3 tools/verify_visual_sync.py <project>
```

Then do the actual review using the report output — do not read `script.md` manually:

1. Run `verify_visual_sync.py` and read its output section by section
2. For each image entry, the report shows the exact words being spoken during that image (character-level if `.json` alignment files exist, estimated otherwise) alongside the image description
3. Judge whether what the image shows matches what the narrator is saying at that moment
4. Flag every mismatch: "narration is talking about X but the image shows Y"
5. Fix by reordering the export array in `visuals.tsx` — move images to the position that matches their narration moment. Do NOT regenerate images to fix sync issues.
6. Re-run `verify_visual_sync.py` after edits to confirm the fix

This cannot be automated. The report gives you the raw material — the judgment of whether image and narration belong together is yours to make. Do not skip it or summarize it. Go section by section, image by image.

If there are narration moments with no suitable image — sections where the words describe something not depicted by any available image — flag those specifically and generate additional images to cover them. Do not reorder your way out of a content gap. If the narration needs an image that doesn't exist, add it.

**Do not launch the preview until every section has been reviewed and all mismatches fixed.**

**W8c: Launch preview**
```bash
cd /Users/charleswynn/Desktop/The Anthropology of Wealth && npm start
```
**STOP HERE.** Tell the user the video is ready for preview. Do NOT render unless the user explicitly says to.

---

## Post-Approval Pipeline

When the user approves the video (says "render", "publish", "ship it", "looks good", "approved", "confirmed", "complete project", or any clear signal of approval), read `.claude/pipeline_post_approval.md` and execute Waves 9–12 in full. Do not stop between steps. Do not wait for confirmation.

---

## Important Rules
- NEVER render without explicit user permission
- NEVER use SVGs for visuals — all visuals must be Gemini-generated images
- Always send `reference/joseph.png` as the primary character reference to Gemini; add `jessw.png`, `solaw.png`, `braydenw.png` based on scene cast (see CHARACTER CASTING RULE)
- All image prompts must use structured JSON format from `/gemini-flash-image-prompting` — never flat prose strings
- Character dress and appearance in every image must match the scene's historical period, setting, and cultural context — specified in `main_characters[].appearance.clothing` in the JSON prompt
- Audio durations drive visual timings — each audio Sequence uses exact clip duration
- All numbers in scripts must be fully spelled out for TTS
- Root scripts use `Path(__file__)` for paths — runnable from any working directory

## Script Writing Rules (TTS-critical — no exceptions)
Full guide in `script_writer.md`. These rules apply to every narration line:
- **Numbers**: all spelled out — "twenty one dollars" not "$21", "ten percent" not "10%"
- **No hyphens/dashes**: no `-`, `—`, or `–` anywhere in narration text
- **No setup transitions**: delete sentences that only announce the next sentence ("Here is where this gets interesting." → cut it)
- **No staccato stacks**: no three-or-more short punchy fragments in a row ("Natural. Compounding. Relentless." → rewrite as prose)
- **No contrasting pairs**: no "Not X. Y." constructions in any form — rewrite as a direct statement
- **Fillers**: mix Okay/Hmm/Alright/Yeah into every section, 1–3 per section, start of sentence only
- **"Check this out"**: use exactly once per video, at the most interesting or surprising moment — this is the only permitted exception to the no-setup-transitions rule
- **"That's crazy"**: use exactly once per video, immediately after delivering a genuinely shocking fact
- **"That's crazy, right?"**: use exactly once per video, immediately after delivering a genuinely shocking fact — distinct moment from "that's crazy", not back to back

## Current Projects

### ten-dollar-day
"$10/Day Investing" — `TenDollarDay` — 8148 frames, ~271.6s, 45 images, 10 audio clips

### hundred-k-tipping-point
"The $100K Tipping Point" — in progress — 45 images, 7 audio clips

---

*Reference: `.claude/reference.md` — project structure, per-script config, defaults*
*Reference: `script_writer.md` — full channel style guide and output format*
*Reference: `.claude/pipeline_post_approval.md` — Waves 9–12 (render, upload, archive)*
*Skill: `/gemini-flash-image-prompting` — structured JSON prompt schema, art style rules, character presence rules, API config*
