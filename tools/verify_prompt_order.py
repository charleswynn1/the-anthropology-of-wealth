#!/usr/bin/env python3
"""
verify_prompt_order.py — Pre-generation prompt order checker.

Reads the IMAGES list from generate_images.py and checks that each image's
narrative_context matches the narration window it will cover, using word overlap
scoring against ElevenLabs alignment data.

Run AFTER writing prompts into generate_images.py but BEFORE running it.
Any ⚠ flag means an image is likely in the wrong position — fix the order
in generate_images.py before calling the Gemini API.

Usage:
  python3 tools/verify_prompt_order.py <project>
  python3 tools/verify_prompt_order.py <project> <section_filter>

Exit codes:
  0 — all images match their assigned windows
  1 — one or more images appear out of order, or a fatal parse error occurred
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
# Flag if the best-matching window scores this many times better than the assigned window.
# 1.5 (tightened from 2.0) — improved scoring reduces false positives, allowing a
# stricter threshold that catches more genuine mismatches.
WARN_SCORE_RATIO = 1.5
# Images scoring below this on their assigned window get a LOW MATCH warning
# regardless of other windows — may indicate a content gap, not just wrong order.
LOW_MATCH_THRESHOLD = 0.15


# ── Scoring ───────────────────────────────────────────────────────────────────

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "of",
    "for", "is", "was", "are", "were", "it", "its", "this", "that", "with",
    "as", "by", "from", "had", "has", "have", "they", "their", "he", "his",
    "she", "her", "we", "our", "not", "be", "been", "being",
}


def _clean_words(text: str) -> list[str]:
    """Lowercase, strip punctuation, return word list."""
    return re.sub(r"[^\w\s]", "", text.lower()).split()


def _content_words(text: str) -> set[str]:
    return set(_clean_words(text)) - STOPWORDS


def _bigrams(words: list[str]) -> set[tuple[str, str]]:
    clean = [w for w in words if w not in STOPWORDS]
    return set(zip(clean[:-1], clean[1:])) if len(clean) >= 2 else set()


def _entities(text: str) -> set[str]:
    """Extract likely proper nouns (capitalized words not at sentence start)."""
    words = text.split()
    result = set()
    for i, word in enumerate(words):
        clean = re.sub(r"[^\w]", "", word)
        if clean and clean[0].isupper() and len(clean) > 1 and clean.lower() not in STOPWORDS:
            # Skip if it's after sentence-ending punctuation (likely sentence start)
            if i > 0 and not words[i - 1].rstrip()[-1:] in ".?!":
                result.add(clean.lower())
    return result


def combined_score(context: str, window_text: str) -> float:
    """Weighted score combining unigram overlap, bigram overlap, and entity match."""
    ctx_content = _content_words(context)
    win_content = _content_words(window_text)

    # Unigram overlap
    if not ctx_content:
        return 0.0
    unigram = len(ctx_content & win_content) / len(ctx_content)

    # Bigram overlap
    ctx_bg = _bigrams(_clean_words(context))
    win_bg = _bigrams(_clean_words(window_text))
    bigram = len(ctx_bg & win_bg) / len(ctx_bg) if ctx_bg else 0.0

    # Entity overlap
    ctx_ent = _entities(context)
    win_ent = _entities(window_text)
    entity = len(ctx_ent & win_ent) / len(ctx_ent) if ctx_ent else 0.0

    return 0.5 * unigram + 0.3 * bigram + 0.2 * entity


# ── Alignment parsing ─────────────────────────────────────────────────────────

def get_windows_sentence_aware(json_path: Path, num_visuals: int) -> list[str]:
    """Return sentence-boundary-aware window text strings."""
    boundaries = find_sentence_boundaries(json_path)

    if boundaries and len(boundaries) >= 3:
        windows_ranges = group_boundaries_into_windows(boundaries, num_visuals)
    else:
        # Fallback to fixed windows
        data = json.loads(json_path.read_text())
        ends = data.get("character_end_times_seconds", [])
        if not ends:
            return []
        total = ends[-1]
        n = int(total / FALLBACK_WINDOW_SECONDS) + (
            1 if total % FALLBACK_WINDOW_SECONDS else 0
        )
        dur = total / max(n, 1)
        windows_ranges = [(i * dur, min((i + 1) * dur, total)) for i in range(n)]

    return [get_text_in_range(json_path, s, e) for s, e in windows_ranges]


# ── generate_images.py parsing ────────────────────────────────────────────────

def parse_images(project: str) -> list[tuple[str, str]]:
    """
    Parse IMAGES from generate_images.py.
    Returns [(image_code, narrative_context), ...] in declaration order.
    """
    for candidate in [
        ROOT / f"projects/{project}/generate_images.py",
        ROOT / "tools/generate_images.py",
    ]:
        if candidate.exists():
            content = candidate.read_text()
            result  = []
            for m in re.finditer(r'\("([A-Z]+\d+)",', content):
                code = m.group(1)
                nc   = re.search(
                    r'"narrative_context":\s*"([^"]+)"',
                    content[m.start():m.start() + 3000],
                )
                result.append((code, nc.group(1) if nc else ""))
            if result:
                return result
    return []


# ── calculate_timings.py parsing ──────────────────────────────────────────────

def parse_sections(project: str) -> list[tuple[str, list[tuple[str, int]]]]:
    """
    Parse SECTIONS from calculate_timings.py.
    Returns [(section_name, [(audio_file, num_visuals), ...]), ...].
    """
    for candidate in [
        ROOT / f"projects/{project}/calculate_timings.py",
        ROOT / "tools/calculate_timings.py",
    ]:
        if candidate.exists():
            content        = candidate.read_text()
            sections_match = re.search(r"SECTIONS\s*=\s*\[(.*?)\]\s*\n", content, re.DOTALL)
            if not sections_match:
                print(f"ERROR: Could not parse SECTIONS from {candidate}")
                sys.exit(1)
            raw            = sections_match.group(1)
            section_blocks = re.findall(r'\(\s*"([^"]+)"\s*,\s*\[(.*?)\]\s*\)', raw, re.DOTALL)
            result         = []
            for sec_name, audio_block in section_blocks:
                audio_entries = re.findall(r'\(\s*"([^"]+)"\s*,\s*(\d+)\s*\)', audio_block)
                result.append((sec_name, [(af, int(n)) for af, n in audio_entries]))
            return result

    print("ERROR: No calculate_timings.py found for this project")
    sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_prompt_order.py <project> [section_filter]")
        sys.exit(1)

    project        = sys.argv[1]
    section_filter = sys.argv[2] if len(sys.argv) > 2 else None
    audio_dir      = ROOT / f"projects/{project}/audio"

    images   = parse_images(project)
    sections = parse_sections(project)

    if not images:
        print(f"ERROR: No images parsed from generate_images.py for '{project}'")
        print("Ensure IMAGES contains tuples of the form (\"CODE\", [...], json.dumps({{...}}))")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"PROMPT ORDER CHECK — {project}")
    print(f"Each image is scored against its assigned window (sentence-aware).")
    print(f"⚠ = another window scores {WARN_SCORE_RATIO:.1f}x better — likely wrong position.")
    print(f"?  = score below {LOW_MATCH_THRESHOLD:.2f} — possible content gap.")
    print(f"{'='*70}\n")

    img_iter      = iter(images)
    any_warnings  = False
    total_checked = 0
    total_warned  = 0
    total_low     = 0

    for sec_name, audio_groups in sections:
        skip = section_filter and section_filter not in sec_name

        for audio_file, num_visuals in audio_groups:
            # Always consume the correct number of images from the iterator
            clip_images = []
            for _ in range(num_visuals):
                try:
                    clip_images.append(next(img_iter))
                except StopIteration:
                    break

            if skip:
                continue

            json_path = audio_dir / f"{audio_file}.json"
            if not json_path.exists():
                print(f"  [{sec_name} / {audio_file}]  — no alignment JSON, skipping order check")
                print(f"  Run generate_prompt_windows.py after W3a to get window data.\n")
                continue

            windows = get_windows_sentence_aware(json_path, num_visuals)
            if not windows:
                print(f"  [{sec_name} / {audio_file}]  — alignment JSON has no data, skipping\n")
                continue

            n = min(len(clip_images), len(windows))

            print(f"  [{sec_name} / {audio_file}]  {len(clip_images)} images, {len(windows)} windows")

            if len(clip_images) != len(windows):
                print(f"  ⚠ COUNT MISMATCH: {len(clip_images)} images vs {len(windows)} windows")
                print(f"    Expected ceil(audio_seconds / 10) images. Re-check W4 output.\n")

            print(f"  {'─'*60}")

            section_warned = False
            for i in range(n):
                code, context  = clip_images[i]
                assigned_win   = windows[i]
                assigned_score = combined_score(context, assigned_win)

                # Score context against every window in this clip
                all_scores     = [(j, combined_score(context, windows[j]))
                                  for j in range(len(windows))]
                best_j, best_score = max(all_scores, key=lambda x: x[1])

                total_checked += 1

                out_of_order = (
                    best_j != i
                    and best_score > 0
                    and (assigned_score == 0 or best_score >= assigned_score * WARN_SCORE_RATIO)
                )

                low_match = assigned_score < LOW_MATCH_THRESHOLD and not out_of_order

                if out_of_order:
                    flag         = (f"⚠  best match window {best_j + 1} "
                                    f"(score {best_score:.2f} vs assigned {assigned_score:.2f})")
                    any_warnings = True
                    section_warned = True
                    total_warned  += 1
                elif low_match:
                    flag = f"?  LOW MATCH (score {assigned_score:.2f}) — may not depict this window's content"
                    any_warnings = True
                    total_low += 1
                else:
                    flag = f"✓  score {assigned_score:.2f}"

                print(f"  {i + 1:2}. {code:<8}  {flag}")
                print(f"       context: {context[:80]}")
                print(f"       window:  {assigned_win[:80]}")
                print()

            if section_warned:
                print(f"  ACTION: reorder images in this clip in generate_images.py "
                      f"to match the window sequence above.\n")
            else:
                print()

    print(f"{'='*70}")
    if any_warnings:
        parts = []
        if total_warned:
            parts.append(f"{total_warned} out-of-order")
        if total_low:
            parts.append(f"{total_low} low-match")
        print(f"WARNINGS — {' + '.join(parts)} of {total_checked} image(s) checked.")
        if total_warned:
            print(f"Fix order in generate_images.py before running the Gemini API.")
        if total_low:
            print(f"Low-match images may need rewritten prompts — check narrative_context.")
        sys.exit(1)
    else:
        print(f"PASSED — {total_checked} image(s) checked. All match assigned windows.")
        sys.exit(0)


if __name__ == "__main__":
    main()
