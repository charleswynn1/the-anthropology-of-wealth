#!/usr/bin/env python3
"""
verify_visual_sync.py — Visual-Narration Sync Checker

For each image in the video, shows the image description alongside the
approximate narration playing at that moment. Claude reads this report
and flags any mismatches before the Remotion preview launches.

Usage: python3 tools/verify_visual_sync.py <project>
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30


def parse_visual_timings(project: str) -> list[list[int]]:
    timing_file = ROOT / f"src/{project}/timing.ts"
    content = timing_file.read_text()
    match = re.search(r"VISUAL_TIMINGS.*?=\s*\[(.*?)\];", content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse VISUAL_TIMINGS from {timing_file}")
    rows = re.findall(r"\[([^\]]+)\]", match.group(1))
    return [[int(n.strip()) for n in row.split(",") if n.strip().isdigit()] for row in rows]


def parse_visuals_order(project: str) -> dict[str, list[str]]:
    visuals_file = ROOT / f"src/{project}/visuals.tsx"
    content = visuals_file.read_text()
    section_names = [
        "hookVisuals", "setupVisuals", "lydiaVisuals", "athensVisuals",
        "alexanderVisuals", "romeVisuals", "modernVisuals", "closingVisuals",
    ]
    result = {}
    for name in section_names:
        m = re.search(rf"export const {name}\s*=\s*\[(.*?)\];", content, re.DOTALL)
        if m:
            result[name] = re.findall(r"\b([A-Z]+\d+)\b", m.group(1))
    return result


def parse_image_descriptions(project: str) -> dict[str, str]:
    for candidate in [
        ROOT / f"projects/{project}/generate_images.py",
        ROOT / "tools/generate_images.py",
    ]:
        if candidate.exists():
            content = candidate.read_text()
            return {img: desc for img, desc in re.findall(r'\("([A-Z]+\d+)",\s*"([^"]+)"', content)}
    return {}


def parse_narration(project: str) -> dict[str, str]:
    script_file = ROOT / f"projects/{project}/script.md"
    content = script_file.read_text()
    parts = re.split(r"\[s(\d+)_([^\]]+)\]", content)
    sections = {}
    i = 1
    while i + 2 < len(parts):
        tag = f"s{parts[i]}_{parts[i+1]}"
        text = parts[i + 2].split("---")[0].strip()
        sections[tag] = text
        i += 3
    return sections


def load_alignment(project: str, audio_file: str) -> dict | None:
    """Load character-level alignment JSON saved by generate_audio.py, if present."""
    json_path = ROOT / f"projects/{project}/audio/{audio_file}.json"
    if json_path.exists():
        return json.loads(json_path.read_text())
    return None


def get_narration_at_second_precise(alignment: dict, target_sec: float, window: float = 3.5) -> str:
    """Return the words spoken during [target_sec, target_sec + window] using alignment data."""
    chars       = alignment["characters"]
    start_times = alignment["character_start_times_seconds"]
    end_times   = alignment["character_end_times_seconds"]

    # Collect characters whose window overlaps [target_sec, target_sec + window]
    window_end = target_sec + window
    in_window = []
    for i, char in enumerate(chars):
        if start_times[i] <= window_end and end_times[i] >= target_sec:
            in_window.append(char)

    text = "".join(in_window).strip()
    # Trim to reasonable length
    words = text.split()
    return " ".join(words[:16]) + ("..." if len(words) > 16 else "")


def get_narration_at_second_estimated(text: str, target_sec: float, total_sec: float) -> str:
    """Fallback: estimate narration position by word count when no alignment data exists."""
    words = text.split()
    if not words or total_sec <= 0:
        return ""
    idx = int((target_sec / total_sec) * len(words))
    idx = max(0, min(idx, len(words) - 1))
    start = max(0, idx - 4)
    end = min(len(words), idx + 12)
    excerpt = " ".join(words[start:end])
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(words):
        excerpt += "..."
    return excerpt


def fmt_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:05.2f}"


SECTION_KEYS = [
    ("hookVisuals",     "s1_hook",      "hook"),
    ("setupVisuals",    "s2_setup",     "setup"),
    ("lydiaVisuals",    "s3_lydia",     "lydia"),
    ("athensVisuals",   "s4_athens",    "athens"),
    ("alexanderVisuals","s5_alexander", "alexander"),
    ("romeVisuals",     "s6_rome",      "rome"),
    ("modernVisuals",   "s7_modern",    "modern"),
    ("closingVisuals",  "s8_closing",   "closing"),
]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_visual_sync.py <project>")
        sys.exit(1)

    project = sys.argv[1]

    timings      = parse_visual_timings(project)
    visuals      = parse_visuals_order(project)
    descriptions = parse_image_descriptions(project)
    narrations   = parse_narration(project)

    # Compute global section start frames
    section_starts = []
    running = 0
    for row in timings:
        section_starts.append(running)
        running += sum(row)

    print(f"\n{'='*80}")
    print(f"VISUAL SYNC REPORT — {project}")
    print(f"Total: {running}f  ({running/FPS:.1f}s)")
    print(f"{'='*80}")
    print("For each image: timestamp | image description | narration at that moment")
    print("Review every line. If what the image shows doesn't match what the narration")
    print("is saying, the image order in visuals.tsx needs to be fixed.")
    print(f"{'='*80}\n")

    all_ok = True

    # Map section index to audio filename (nar_key → audio file stem)
    audio_file_map = {
        "s1_hook": "s1_hook", "s2_setup": "s2_setup", "s3_lydia": "s3_lydia",
        "s4_athens": "s4_athens", "s5_alexander": "s5_alexander",
        "s6_rome": "s6_rome", "s7_modern": "s7_modern", "s8_closing": "s8_closing",
    }

    for sec_idx, (vis_key, nar_key, label) in enumerate(SECTION_KEYS):
        images     = visuals.get(vis_key, [])
        timing_row = timings[sec_idx] if sec_idx < len(timings) else []
        narration  = narrations.get(nar_key, "")
        alignment  = load_alignment(project, audio_file_map.get(nar_key, nar_key))

        sec_start_f = section_starts[sec_idx]
        sec_total_f = sum(timing_row)
        sec_total_s = sec_total_f / FPS
        precision   = "character-level" if alignment else "estimated"

        print(f"{'─'*80}")
        print(f"[{label.upper()}]  {fmt_time(sec_start_f/FPS)}  |  {len(images)} images  |  {sec_total_s:.1f}s  |  narration: {precision}")
        print(f"{'─'*80}")

        if len(images) != len(timing_row):
            print(f"  ⚠  COUNT MISMATCH: {len(images)} in visuals.tsx vs {len(timing_row)} in timing.ts\n")
            all_ok = False
            continue

        local_offset = 0
        for i, (img_id, dur) in enumerate(zip(images, timing_row)):
            img_start_s = (sec_start_f + local_offset) / FPS
            img_end_s   = (sec_start_f + local_offset + dur) / FPS
            local_s     = local_offset / FPS

            desc = descriptions.get(img_id, "[no description]")

            if alignment:
                nar = get_narration_at_second_precise(alignment, local_s, window=dur / FPS)
            else:
                nar = get_narration_at_second_estimated(narration, local_s, sec_total_s)

            local_offset += dur

            print(f"  {i+1:2d}. {img_id:<8}  {fmt_time(img_start_s)} – {fmt_time(img_end_s)}")
            print(f"      IMG: {desc[:90]}")
            print(f"      NAR: {nar[:90]}")
            print()

    print(f"{'='*80}")
    if all_ok:
        print("✓ All section image counts match timing.ts.")
    print("Review IMG vs NAR for each entry above.")
    print("If any pair is clearly misaligned, fix visuals.tsx before launching preview.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
