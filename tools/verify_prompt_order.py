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
WINDOW_SECONDS = 10.0
# Flag if the best-matching window scores this many times better than the assigned window.
# 2.0 means "best match is at least twice as strong" — reduces false positives on
# short or abstract narrative_context strings.
WARN_SCORE_RATIO = 2.0


# ── Scoring ───────────────────────────────────────────────────────────────────

def word_overlap_score(context: str, window_text: str) -> float:
    """Fraction of context words that appear in window_text (case-insensitive)."""
    # Strip punctuation for fairer matching
    ctx_words  = set(re.sub(r"[^\w\s]", "", context.lower()).split())
    win_words  = set(re.sub(r"[^\w\s]", "", window_text.lower()).split())
    # Ignore very common words that appear everywhere and add noise
    stopwords  = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
                  "of", "for", "is", "was", "are", "were", "it", "its", "this",
                  "that", "with", "as", "by", "from", "had", "has", "have",
                  "they", "their", "he", "his", "she", "her", "we", "our"}
    ctx_words -= stopwords
    if not ctx_words:
        return 0.0
    return len(ctx_words & win_words) / len(ctx_words)


# ── Alignment parsing ─────────────────────────────────────────────────────────

def get_windows(json_path: Path) -> list[str]:
    """Return 10-second window text strings from an ElevenLabs alignment JSON."""
    data   = json.loads(json_path.read_text())
    chars  = data.get("characters", [])
    starts = data.get("character_start_times_seconds", [])
    ends   = data.get("character_end_times_seconds", [])

    if not chars or not ends:
        return []

    total     = ends[-1]
    n_windows = int(total / WINDOW_SECONDS) + (1 if total % WINDOW_SECONDS else 0)

    windows = []
    for i in range(n_windows):
        w_start = i * WINDOW_SECONDS
        w_end   = min(w_start + WINDOW_SECONDS, total)
        text    = "".join(
            c for c, s in zip(chars, starts) if w_start <= s < w_end
        ).strip()
        windows.append(text)
    return windows


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
    print(f"Each image is scored against its assigned {WINDOW_SECONDS:.0f}s window.")
    print(f"⚠ = another window scores {WARN_SCORE_RATIO:.0f}× better — likely wrong position.")
    print(f"{'='*70}\n")

    img_iter      = iter(images)
    any_warnings  = False
    total_checked = 0
    total_warned  = 0

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

            windows = get_windows(json_path)
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
                assigned_score = word_overlap_score(context, assigned_win)

                # Score context against every window in this clip
                all_scores     = [(j, word_overlap_score(context, windows[j]))
                                  for j in range(len(windows))]
                best_j, best_score = max(all_scores, key=lambda x: x[1])

                total_checked += 1

                out_of_order = (
                    best_j != i
                    and best_score > 0
                    and (assigned_score == 0 or best_score >= assigned_score * WARN_SCORE_RATIO)
                )

                if out_of_order:
                    flag         = (f"⚠  best match window {best_j + 1} "
                                    f"(score {best_score:.2f} vs assigned {assigned_score:.2f})")
                    any_warnings = True
                    section_warned = True
                    total_warned  += 1
                else:
                    flag = f"✓  score {assigned_score:.2f}"

                w_start = int(i * WINDOW_SECONDS)
                w_end   = int((i + 1) * WINDOW_SECONDS)
                print(f"  {i + 1:2}. {code:<8} [{w_start:3}s\u2013{w_end:3}s]  {flag}")
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
        print(f"WARNINGS — {total_warned} of {total_checked} image(s) appear out of order.")
        print(f"Fix generate_images.py before running the Gemini API.")
        sys.exit(1)
    else:
        print(f"PASSED — {total_checked} image(s) checked. All match assigned windows.")
        sys.exit(0)


if __name__ == "__main__":
    main()
