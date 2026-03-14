#!/usr/bin/env python3
"""
generate_prompt_windows.py — Narration-per-window brief for image prompt writing.

Reads ElevenLabs character-level alignment files and prints the exact narration
text for each image window. Windows are aligned to sentence boundaries so that
each image prompt covers coherent narration, not an arbitrary 10-second slice.

Requires SECTIONS in calculate_timings.py to know how many images each clip has.
Falls back to fixed 10-second windows if SECTIONS cannot be parsed.

Usage:
  python3 tools/generate_prompt_windows.py <project>
  python3 tools/generate_prompt_windows.py <project> <section_filter>

Examples:
  python3 tools/generate_prompt_windows.py war-dollar
  python3 tools/generate_prompt_windows.py war-dollar s2_bretton_woods
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from alignment_utils import (
        find_sentence_boundaries,
        group_boundaries_into_windows,
        get_text_in_range,
    )
except ImportError:
    sys.path.insert(0, str(ROOT / "tools"))
    from alignment_utils import (
        find_sentence_boundaries,
        group_boundaries_into_windows,
        get_text_in_range,
    )


FALLBACK_WINDOW_SECONDS = 10.0


# ── SECTIONS parsing (same pattern as verify_prompt_order.py) ─────────────────

def parse_sections(project: str) -> list[tuple[str, list[tuple[str, int]]]] | None:
    """Parse SECTIONS from calculate_timings.py → [(name, [(audio, n_images), ...]), ...]."""
    for candidate in [
        ROOT / f"projects/{project}/calculate_timings.py",
        ROOT / "tools/calculate_timings.py",
    ]:
        if candidate.exists():
            content = candidate.read_text()
            m = re.search(r"SECTIONS\s*=\s*\[(.*?)\]\s*\n", content, re.DOTALL)
            if not m:
                return None
            raw = m.group(1)
            blocks = re.findall(r'\(\s*"([^"]+)"\s*,\s*\[(.*?)\]\s*\)', raw, re.DOTALL)
            result = []
            for sec_name, audio_block in blocks:
                entries = re.findall(r'\(\s*"([^"]+)"\s*,\s*(\d+)\s*\)', audio_block)
                result.append((sec_name, [(af, int(n)) for af, n in entries]))
            return result
    return None


# ── Window display ────────────────────────────────────────────────────────────

def process_file_sentence_aware(json_path: Path, num_visuals: int, audio_file: str):
    """Print sentence-boundary-aware windows for one audio clip."""
    boundaries = find_sentence_boundaries(json_path)

    data = json.loads(json_path.read_text())
    ends = data.get("character_end_times_seconds", [])
    if not ends:
        print(f"  {audio_file}  — empty alignment, skipping\n")
        return
    total = ends[-1]

    if boundaries and len(boundaries) >= 3:
        windows = group_boundaries_into_windows(boundaries, num_visuals)
        mode = "sentence-aware"
    else:
        # Fallback: fixed windows
        n = int(total / FALLBACK_WINDOW_SECONDS) + (
            1 if total % FALLBACK_WINDOW_SECONDS else 0
        )
        dur = total / max(n, 1)
        windows = [(i * dur, min((i + 1) * dur, total)) for i in range(n)]
        mode = "fixed (no sentence data)"

    print(f"  {audio_file}  ({total:.1f}s -> {len(windows)} windows, {mode})")
    print()

    for i, (w_start, w_end) in enumerate(windows):
        text = get_text_in_range(json_path, w_start, w_end)
        dur = w_end - w_start
        label = f"{w_start:6.1f}s - {w_end:6.1f}s  ({dur:.1f}s)"
        print(f"    {i + 1:2}. [{label}]  {text}")

    print()


def process_file_fallback(json_path: Path):
    """Fallback: fixed 10-second windows (when SECTIONS not available)."""
    data = json.loads(json_path.read_text())
    chars = data.get("characters", [])
    starts = data.get("character_start_times_seconds", [])
    ends = data.get("character_end_times_seconds", [])

    if not chars or not ends:
        print(f"ERROR: {json_path.name} has no alignment data.")
        sys.exit(1)

    total = ends[-1]
    n_windows = int(total / FALLBACK_WINDOW_SECONDS) + (
        1 if total % FALLBACK_WINDOW_SECONDS else 0
    )

    print(f"  {json_path.stem}  ({total:.1f}s -> {n_windows} windows @ {FALLBACK_WINDOW_SECONDS:.0f}s each, fixed fallback)")
    print()

    for i in range(n_windows):
        w_start = i * FALLBACK_WINDOW_SECONDS
        w_end = min(w_start + FALLBACK_WINDOW_SECONDS, total)
        text = get_text_in_range(json_path, w_start, w_end)
        label = f"{w_start:6.1f}s - {w_end:6.1f}s  ({w_end - w_start:.1f}s)"
        print(f"    {i + 1:2}. [{label}]  {text}")

    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/generate_prompt_windows.py <project> [section_filter]")
        sys.exit(1)

    project = sys.argv[1]
    section_filter = sys.argv[2] if len(sys.argv) > 2 else None

    audio_dir = ROOT / f"projects/{project}/audio"
    if not audio_dir.exists():
        print(f"ERROR: audio directory not found: {audio_dir}")
        sys.exit(1)

    json_files = sorted(audio_dir.glob("*.json"))
    if not json_files:
        print(f"ERROR: No .json alignment files found in {audio_dir}")
        print("These are generated by generate_audio.py alongside each .mp3.")
        print("W3a must complete before W3b. Do not write prompts until alignment files exist.")
        sys.exit(1)

    # Check that every narration MP3 has a companion alignment JSON
    mp3_files = sorted([
        f for f in audio_dir.glob("*.mp3") if f.name != "music_bg.mp3"
    ])
    missing_json = [f for f in mp3_files if not (audio_dir / f"{f.stem}.json").exists()]
    if missing_json:
        print(f"ERROR: {len(missing_json)} MP3(s) are missing alignment JSON files:")
        for f in missing_json:
            print(f"  missing: {f.stem}.json")
        print("\nRe-run generate_audio.py for these clips before writing prompts.")
        sys.exit(1)

    print(f"\n{'=' * 70}")
    print(f"PROMPT WINDOWS — {project}")
    print(f"Windows are aligned to sentence boundaries. Each window shows the")
    print(f"exact narration text one image must depict. Write each prompt for")
    print(f"its window's words — not the section topic in general.")
    print(f"{'=' * 70}\n")

    sections = parse_sections(project)

    if sections:
        for sec_name, audio_groups in sections:
            for audio_file, num_visuals in audio_groups:
                if section_filter and section_filter not in audio_file and section_filter not in sec_name:
                    continue
                json_path = audio_dir / f"{audio_file}.json"
                if not json_path.exists():
                    print(f"  {audio_file}  — no alignment JSON, skipping\n")
                    continue
                process_file_sentence_aware(json_path, num_visuals, audio_file)
    else:
        print("  (SECTIONS not found in calculate_timings.py — using fixed 10s windows)\n")
        matched = [f for f in json_files if not section_filter or section_filter in f.stem]
        if not matched:
            print(f"No files matching '{section_filter}' in {audio_dir}")
            sys.exit(1)
        for f in matched:
            process_file_fallback(f)


if __name__ == "__main__":
    main()
