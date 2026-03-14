#!/usr/bin/env python3
"""
verify_post_reorder.py — Post-reorder visual sync verification gate.

After W8b reordering, checks that every image's narrative_context still matches
the narration at its final playback position. Catches cases where reordering
introduced new mismatches, or where the original alignment was wrong and
reordering didn't fix it.

Usage:
  python3 tools/verify_post_reorder.py <project>

Exit codes:
  0 — all images pass (ready for preview)
  1 — one or more images are misaligned at their final positions
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from alignment_utils import get_text_in_range
except ImportError:
    sys.path.insert(0, str(ROOT / "tools"))
    from alignment_utils import get_text_in_range

FPS = 30

# Images scoring below this threshold against their playback narration are flagged
LOW_SCORE_THRESHOLD = 0.10

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "of",
    "for", "is", "was", "are", "were", "it", "its", "this", "that", "with",
    "as", "by", "from", "had", "has", "have", "they", "their", "he", "his",
    "she", "her", "we", "our", "not", "be", "been", "being",
}


def word_overlap_score(context: str, window_text: str) -> float:
    """Fraction of context content words that appear in window_text."""
    ctx_words = set(re.sub(r"[^\w\s]", "", context.lower()).split()) - STOPWORDS
    win_words = set(re.sub(r"[^\w\s]", "", window_text.lower()).split()) - STOPWORDS
    if not ctx_words:
        return 0.0
    return len(ctx_words & win_words) / len(ctx_words)


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_visual_timings(project: str) -> list[list[int]]:
    """Extract VISUAL_TIMINGS from timing.ts."""
    path = ROOT / f"src/{project}/timing.ts"
    content = path.read_text()
    match = re.search(r"VISUAL_TIMINGS.*?=\s*\[(.*?)\];", content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse VISUAL_TIMINGS from {path}")
    rows = re.findall(r"\[([^\]]+)\]", match.group(1))
    return [[int(n.strip()) for n in row.split(",") if n.strip().isdigit()] for row in rows]


def parse_visuals_order(project: str) -> list[list[str]]:
    """Return image codes in playback order, per section, from visuals.tsx."""
    path = ROOT / f"src/{project}/visuals.tsx"
    content = path.read_text()
    section_names = re.findall(r"export const (\w+Visuals)\s*=", content)
    result = []
    for name in section_names:
        m = re.search(rf"export const {name}\s*=\s*\[(.*?)\];", content, re.DOTALL)
        if m:
            array_content = re.sub(r"//[^\n]*", "", m.group(1))
            codes = re.findall(r"\b([A-Z]+\d+)\b", array_content)
            result.append(codes)
    return result


def parse_image_descriptions(project: str) -> dict[str, str]:
    """Map image code -> narrative_context from generate_images.py."""
    for candidate in [
        ROOT / f"projects/{project}/generate_images.py",
        ROOT / "tools/generate_images.py",
    ]:
        if candidate.exists():
            content = candidate.read_text()
            result = {}
            for m in re.finditer(r'\("([A-Z]+\d+)",', content):
                code = m.group(1)
                nc = re.search(
                    r'"narrative_context":\s*"([^"]+)"',
                    content[m.start() : m.start() + 3000],
                )
                if nc:
                    result[code] = nc.group(1)
            return result
    return {}


def parse_sections_config(project: str) -> list[tuple[str, list[str]]]:
    """Return [(section_name, [audio_file, ...]), ...] from calculate_timings.py."""
    for candidate in [
        ROOT / f"projects/{project}/calculate_timings.py",
        ROOT / "tools/calculate_timings.py",
    ]:
        if candidate.exists():
            content = candidate.read_text()
            m = re.search(r"SECTIONS\s*=\s*\[(.*?)\]\s*\n", content, re.DOTALL)
            if not m:
                return []
            raw = m.group(1)
            blocks = re.findall(r'\(\s*"([^"]+)"\s*,\s*\[(.*?)\]\s*\)', raw, re.DOTALL)
            result = []
            for sec_name, audio_block in blocks:
                audio_files = re.findall(r'\(\s*"([^"]+)"\s*,\s*\d+\s*\)', audio_block)
                result.append((sec_name, audio_files))
            return result
    return []


def fmt_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:05.2f}"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_post_reorder.py <project>")
        sys.exit(1)

    project = sys.argv[1]
    audio_dir = ROOT / f"projects/{project}/audio"

    timings = parse_visual_timings(project)
    visuals = parse_visuals_order(project)
    descriptions = parse_image_descriptions(project)
    sections = parse_sections_config(project)

    if not timings or not visuals:
        print("ERROR: Could not parse timing.ts or visuals.tsx")
        sys.exit(1)

    # Build global frame offsets per section
    section_starts = []
    running = 0
    for row in timings:
        section_starts.append(running)
        running += sum(row)

    print(f"\n{'=' * 70}")
    print(f"POST-REORDER VERIFICATION — {project}")
    print(f"Checks that each image's narrative_context matches the narration")
    print(f"at its final playback position. Flags scores below {LOW_SCORE_THRESHOLD:.2f}.")
    print(f"{'=' * 70}\n")

    errors = []
    total_checked = 0

    for sec_idx in range(min(len(visuals), len(timings), len(sections))):
        sec_name, audio_files = sections[sec_idx]
        images = visuals[sec_idx]
        timing_row = timings[sec_idx]

        if len(images) != len(timing_row):
            print(f"  [{sec_name}]  COUNT MISMATCH: {len(images)} images vs {len(timing_row)} timings\n")
            continue

        # Determine which audio file covers this section
        audio_file = audio_files[0] if audio_files else None
        json_path = audio_dir / f"{audio_file}.json" if audio_file else None

        sec_start_f = section_starts[sec_idx]
        local_offset = 0
        sec_ok = True

        for i, (img_id, dur) in enumerate(zip(images, timing_row)):
            desc = descriptions.get(img_id, "")
            if not desc:
                local_offset += dur
                continue

            # Get narration at this image's playback position
            local_s = local_offset / FPS
            dur_s = dur / FPS
            global_s = (sec_start_f + local_offset) / FPS

            if json_path and json_path.exists():
                nar = get_text_in_range(json_path, local_s, local_s + dur_s)
            else:
                nar = ""

            if nar:
                score = word_overlap_score(desc, nar)
                total_checked += 1

                if score < LOW_SCORE_THRESHOLD:
                    errors.append((sec_name, img_id, global_s, dur_s, desc, nar, score))
                    sec_ok = False
                    print(f"  {img_id:<8}  {fmt_time(global_s)} - {fmt_time(global_s + dur_s)}  FAIL (score {score:.2f})")
                    print(f"      IMG: {desc[:90]}")
                    print(f"      NAR: {nar[:90]}")
                    print()

            local_offset += dur

        if sec_ok:
            print(f"  [{sec_name}]  {len(images)} images  OK")

    print(f"\n{'=' * 70}")
    if errors:
        print(f"FAILED — {len(errors)} image(s) have very low alignment scores.")
        print(f"These images may not match the narration at their playback positions.")
        print(f"Fix by reordering in visuals.tsx or generating replacement images.")
        for sec_name, img_id, t, dur_s, desc, nar, score in errors:
            print(f"\n  {img_id} in [{sec_name}] at {fmt_time(t)} (score {score:.2f})")
            print(f"    IMG: {desc[:100]}")
            print(f"    NAR: {nar[:100]}")
        sys.exit(1)
    else:
        print(f"PASSED — {total_checked} image(s) checked. All above threshold ({LOW_SCORE_THRESHOLD:.2f}).")
        sys.exit(0)


if __name__ == "__main__":
    main()
