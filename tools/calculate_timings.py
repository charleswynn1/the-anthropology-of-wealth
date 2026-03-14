#!/usr/bin/env python3
"""
MoneyMath — General Timing Calculator
Reads audio file durations and outputs VISUAL_TIMINGS for Remotion.

Usage:
  1. Set PROJECT_NAME and SECTIONS below
  2. Run: python3 calculate_timings.py
  3. Paste output into src/<project>/timing.ts
"""

import math
import subprocess
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Import sentence-boundary utilities (handles running from tools/ or projects/<project>/)
try:
    from alignment_utils import find_sentence_boundaries, group_boundaries_into_windows
except ImportError:
    sys.path.insert(0, str(ROOT / "tools"))
    from alignment_utils import find_sentence_boundaries, group_boundaries_into_windows

# ══════════════════════════════════════════════════════════
# CONFIGURATION — Edit these for each new video
# ══════════════════════════════════════════════════════════

PROJECT_NAME = "war-dollar"
FPS = 30

# Section structure: (section_name, [(audio_filename, num_visuals), ...])
# Each section can have one or more audio files.
# num_visuals = how many image components that audio file covers.
# NOTE: counts are placeholders — update after running once to get actual durations,
# then recompute: ceil(actual_seconds / 10)
SECTIONS = [
    ("hook",          [("s1_hook", 12)]),
    ("bretton",       [("s2_bretton_woods", 11)]),
    ("nixon_shock",   [("s3_nixon_shock", 13)]),
    ("dollar_crisis", [("s4_dollar_crisis", 12)]),
    ("the_deal",      [("s5_the_deal", 14)]),
    ("mechanics",     [("s6_mechanics", 13)]),
    ("embargo",       [("s7_embargo", 11)]),
    ("iran",          [("s7_iran", 5)]),
    ("carter",        [("s8_carter_doctrine", 14)]),
    ("gulf_war",      [("s9_gulf_war", 10)]),
    ("blowback",      [("s9_blowback", 7)]),
    ("euros",         [("s10_euros", 11)]),
    ("invasion",      [("s10_invasion", 4)]),
    ("iraq_war",      [("s11_iraq_war", 14)]),
    ("libya",         [("s12_libya", 15)]),
    ("the_cost",      [("s13_the_cost", 14)]),
    ("profiteering",  [("s14_profiteering", 15)]),
    ("cracks",        [("s15_cracks", 15)]),
    ("today",         [("s16_today", 16)]),
    ("close",         [("s17_close", 16)]),
]

# ══════════════════════════════════════════════════════════
# CALCULATION — No need to edit below this line
# ══════════════════════════════════════════════════════════

AUDIO_DIR = ROOT / f"projects/{PROJECT_NAME}/audio"


WARN_FRAMES_PER_VISUAL = 360   # 12s — warn if any single image shows longer than this
TARGET_FRAMES_PER_VISUAL = 300  # 10s — ideal target for narration pacing


def get_duration_frames(filepath: Path) -> int:
    """Get audio duration in frames using ffprobe (sample-accurate).

    Uses stream-level duration (decoded samples) for accuracy, falling back to
    format-level duration. Uses math.ceil so visual frames always accommodate
    the full audio clip — audio must never outlast its visual container.
    """
    # Stream duration is sample-accurate for MP3; format duration reads header metadata
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=duration", "-of", "json", str(filepath)],
        capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if streams and streams[0].get("duration") not in (None, "N/A"):
        seconds = float(streams[0]["duration"])
    else:
        # Fallback to format-level duration
        result2 = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(filepath)],
            capture_output=True, text=True,
        )
        data2 = json.loads(result2.stdout)
        seconds = float(data2["format"]["duration"])
    return math.ceil(seconds * FPS)


def main():
    print(f"=== Audio Durations for {PROJECT_NAME} ===\n")

    all_timings = []
    total_frames = 0

    for section_name, audio_groups in SECTIONS:
        section_timings = []
        section_frames = 0

        for audio_file, num_visuals in audio_groups:
            path = AUDIO_DIR / f"{audio_file}.mp3"
            if not path.exists():
                print(f"  MISSING: {path}")
                section_timings.extend([0] * num_visuals)
                continue

            frames = get_duration_frames(path)
            seconds = frames / FPS
            print(f"  {audio_file}: {seconds:.2f}s = {frames}f ({num_visuals} visuals)")

            # ── Sentence-boundary-aware timing ──────────────────────
            # Uses character-level alignment from ElevenLabs to snap image
            # durations to actual sentence boundaries instead of dividing
            # evenly.  Falls back to even distribution when no alignment
            # JSON is available.
            alignment_json = AUDIO_DIR / f"{audio_file}.json"
            boundaries = find_sentence_boundaries(alignment_json)

            if boundaries and len(boundaries) >= 3:
                # Enough sentence data — use variable durations
                windows = group_boundaries_into_windows(boundaries, num_visuals)
                timings = [math.ceil((end - start) * FPS) for start, end in windows]

                # Rounding correction: timings must sum to exactly `frames`
                diff = sum(timings) - frames
                if diff > 0:
                    for _ in range(diff):
                        idx = timings.index(max(timings))
                        timings[idx] -= 1
                elif diff < 0:
                    for _ in range(-diff):
                        idx = timings.index(min(timings))
                        timings[idx] += 1

                mode = "sentence-aware"
            else:
                # Fallback: even distribution
                per_visual = frames // num_visuals
                remainder = frames - (per_visual * num_visuals)
                timings = [per_visual] * num_visuals
                for i in range(remainder):
                    timings[i] += 1
                mode = "even (no alignment data)"

            print(f"    mode: {mode}  |  durations: {timings}")
            section_timings.extend(timings)
            section_frames += frames

        all_timings.append(section_timings)
        total_frames += section_frames
        print(f"  → {section_name}: {section_frames}f\n")

    print(f"TOTAL: {total_frames}f ({total_frames / FPS:.1f}s)\n")

    # TypeScript output
    print("=== Paste into src/<project>/timing.ts ===\n")
    print("export const VISUAL_TIMINGS: number[][] = [")
    section_names = [s[0] for s in SECTIONS]
    for i, (timings, name) in enumerate(zip(all_timings, section_names)):
        s = sum(timings)
        print(f"  // ── s{i}: {name} ({s}f) ──")
        print(f"  [{', '.join(str(t) for t in timings)}],\n")
    print("];")

    # Audio section config
    print(f"\n=== Audio sections for <Composition>.tsx ===\n")
    sec_idx = 0
    for section_name, audio_groups in SECTIONS:
        local_offset = 0
        for audio_file, _ in audio_groups:
            path = AUDIO_DIR / f"{audio_file}.mp3"
            if path.exists():
                frames = get_duration_frames(path)
                offset_str = f" + {local_offset}" if local_offset > 0 else ""
                print(f'  {{ file: "{audio_file}", start: SECTION_STARTS[{sec_idx}]{offset_str}, dur: {frames} }},')
                local_offset += frames
        sec_idx += 1

    print(f"\n=== Update Root.tsx durationInFrames to {total_frames} ===")

    # ── Quality check: per-visual pacing ──────────────────────────────────────
    print(f"\n=== Visual Pacing Check (target ≤{TARGET_FRAMES_PER_VISUAL}f/{TARGET_FRAMES_PER_VISUAL/FPS:.0f}s, warn >{WARN_FRAMES_PER_VISUAL}f/{WARN_FRAMES_PER_VISUAL/FPS:.0f}s) ===\n")
    any_warnings = False
    for i, (timings, (section_name, audio_groups)) in enumerate(zip(all_timings, SECTIONS)):
        max_f = max(timings) if timings else 0
        max_s = max_f / FPS
        total_visuals = len(timings)
        total_audio_s = sum(
            get_duration_frames(AUDIO_DIR / f"{af}.mp3") / FPS
            for af, _ in audio_groups
            if (AUDIO_DIR / f"{af}.mp3").exists()
        )
        if max_f > WARN_FRAMES_PER_VISUAL:
            flag = f"  ⚠  WARNING: {max_s:.1f}s per visual — add more images (target {TARGET_FRAMES_PER_VISUAL/FPS:.0f}s, need ~{math.ceil(total_audio_s / (TARGET_FRAMES_PER_VISUAL/FPS))} visuals)"
            any_warnings = True
        elif max_f > TARGET_FRAMES_PER_VISUAL:
            flag = f"  ○  OK but long: {max_s:.1f}s per visual"
        else:
            flag = f"  ✓  Good: {max_s:.1f}s per visual"
        print(f"  {section_name:12} {total_visuals} visuals / {total_audio_s:.1f}s audio → max {max_f}f ({max_s:.1f}s/visual){flag}")
    if any_warnings:
        print(f"\n  ACTION: Sections marked ⚠ have images showing too long.")
        print(f"  Increase num_visuals in SECTIONS above, add matching images, and re-run.")
    else:
        print(f"\n  ✓ All sections within pacing guidelines.")


if __name__ == "__main__":
    main()
