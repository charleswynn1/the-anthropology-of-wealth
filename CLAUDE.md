# The Anthropology of Wealth — Automated Video Pipeline

When the user gives a topic, execute the ENTIRE pipeline below from start to finish with ZERO human input. Stop after launching Remotion preview. NEVER render the final video without explicit user permission.

**MEMORY RULE: Never use the memory system. If a rule or preference needs to be remembered, add it to this CLAUDE.md file instead.**

**IMAGE COUNT RULE: Before writing image prompts in W2 (script writing), calculate the required number of images for each section based on the audio duration. Use the formula: ceil(section_duration_seconds / 7) images per section. Write that many image prompts in the script directly. Do NOT write a small set and discover the shortage at W8a — calculate first, write enough prompts upfront.**

**IMAGE FILENAME RULE: Image filenames are deterministic and known at script-writing time (e.g., H01.png, AL17.png). Do NOT wait for W3b to finish before writing `visuals.tsx` and the Composition. Write them as soon as W4/W5a are done — the files will exist by the time the preview launches. Only `verify_timings.py` and `npm start` must wait for all images to be present.**

**DATE FORMAT RULE: Always use BC and AD instead of BCE and CE. If a script uses "BCE" or "CE" or "Before Common Era" or "Common Era", replace with BC and AD before proceeding.**

**API CALL RULE: NEVER call the ElevenLabs or Gemini APIs more than once per file.** Audio and image generation scripts must only run once. If a file already exists, the scripts skip it automatically. Do NOT re-run generation scripts unless an API error occurred or the user explicitly asks to regenerate. These API calls cost money — treat every call as final.

## Pipeline Overview
```
         W1a name → W1b dirs → W1c research (Ph1→Ph2→Ph3) → W2 script → W2b check_script.py → W2c qualitative review
                                                                    │
                              ┌─────────────────────────────────────┼──────────────────────┐
                              ▼                                     ▼                      ▼
                         W3a audio                            W3b images            W3c music*
                              │                                     │                      │
                              ▼                                     │               (done async)
                         W4 timings                                 │
                              │                                     ▼
                         W5a timing.ts ──────────────────► W5b visuals.tsx
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
- TITLE (5 options)
- THUMBNAIL TEXT (3-5 options)
- CORE IDEA
- KEY MONEY LESSON
- VIEWER TAKEAWAY
- IMAGE PROMPTS (Python tuples ready for generate_images.py)

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

### WAVE 3 — Parallel Generation (W3a, W3b, W3c, W3d all run simultaneously)

**Start all four tracks at once as soon as W2 is complete. Do not run them sequentially.**

---

**W3a: Generate audio** *(depends on W2 — needs narration text)*

Edit `tools/generate_audio.py`:
- Set `PROJECT_NAME = "<project>"`
- Replace `SECTIONS` with narration tuples from the script: `("s1_hook", """text...""")`
- Split long sections into parts for visual sync (e.g., `s3_data_pt1`, `s3_data_pt2`)

```bash
python3 tools/generate_audio.py
```
Outputs MP3s to `projects/<project>/audio/`. Verify all files were created.

**As soon as W3a finishes → immediately start W4 (do not wait for W3b, W3c, or W3d).**

---

**W3b: Generate images** *(depends on W2 — needs image prompts)*

Edit `tools/generate_images.py`:
- Set `PROJECT_NAME = "<project>"`
- Replace `IMAGES` with the image prompt tuples from the script

```bash
python3 tools/generate_images.py
```
Outputs PNGs to `projects/<project>/images/`. Uses round-robin API keys with 15s batch delays. Verify all files were created.

**As soon as W3b finishes → immediately start W5b (do not wait for W4 or W5a).**

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

**W3d: Generate thumbnails** *(depends on W2 — needs THUMBNAIL TEXT and [THUMBNAIL] block from script.md)*

```bash
python3 tools/generate_thumbnail.py <project>
```
Outputs 3 thumbnail variations to `projects/<project>/`. Runs in parallel — does not block any other track.

**Before running:** Verify script.md contains a `[THUMBNAIL]` block with 3 `scenes:` entries. These scenes drive what the character is doing and what surrounds them — they must visually reflect the video topic, not generic poses. If missing, add it before generating.

**Thumbnail text rule:** Thumbnail text must come from the THUMBNAIL TEXT options in `script.md` — never the YouTube channel name, never a generic placeholder, never the video title. The text must reflect the specific project content (e.g., "FREEDOM = DEBT GONE", "THE OLDEST TRAP →"). If you see "Money Math" or "The math behind the money" in thumbnail output, that means `generate_thumbnail.py` failed to read `script.md` and fell through to its defaults. Stop and fix the regex before proceeding.

---

### WAVE 4 — Timings (starts when W3a finishes, independent of W3b/W3c/W3d)

**W4: Calculate timings** *(depends on W3a — reads actual MP3 durations)*

Edit `tools/calculate_timings.py`:
- Set `PROJECT_NAME = "<project>"`
- Update `SECTIONS` to map each audio file to its visual count:
```python
SECTIONS = [
    ("hook",     [("s1_hook", 5)]),
    ("setup",    [("s2_setup", 5)]),
    ("data",     [("s3_data_pt1", 4), ("s3_data_pt2", 4)]),
    # ... match your actual audio files and image counts
]
```

```bash
python3 tools/calculate_timings.py
```
Capture the VISUAL_TIMINGS array, AUDIO_SECTIONS config, and TOTAL_FRAMES from the output.

**As soon as W4 finishes → immediately start W5a.**

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

**W5b: Create `src/<project>/visuals.tsx`** *(depends on W3b — starts as soon as images exist, independent of W4/W5a)*

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

**W8b: Launch preview**
```bash
cd /Users/charleswynn/Desktop/The Anthropology of Wealth && npm start
```
**STOP HERE.** Tell the user the video is ready for preview. Do NOT render unless the user explicitly says to.

---

## Post-Approval Pipeline

When the user approves the video (says "render", "publish", "ship it", "looks good", etc.), read `.claude/pipeline_post_approval.md` and execute Waves 9–12 in full. Do not stop between steps. Do not wait for confirmation.

---

## Important Rules
- NEVER render without explicit user permission
- NEVER use SVGs for visuals — all visuals must be Gemini-generated images
- Always send `reference/character.png` as multimodal input to Gemini (`USE_REF_IMAGE = True`)
- Character dress and appearance in every image must match the scene's historical period, setting, and cultural context — specify clothing explicitly in each prompt
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

## Current Projects

### ten-dollar-day
"$10/Day Investing" — `TenDollarDay` — 8148 frames, ~271.6s, 45 images, 10 audio clips

### hundred-k-tipping-point
"The $100K Tipping Point" — in progress — 45 images, 7 audio clips

---

*Reference: `.claude/reference.md` — project structure, per-script config, defaults*
*Reference: `script_writer.md` — full channel style guide and output format*
*Reference: `.claude/pipeline_post_approval.md` — Waves 9–12 (render, upload, archive)*
