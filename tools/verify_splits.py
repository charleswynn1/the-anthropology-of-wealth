#!/usr/bin/env python3
"""
verify_splits.py — Audio clip split validation.

Analyzes each audio clip's narration to detect potential topic changes that
were not split into separate audio files. Flags clips where adjacent sentences
share very few content words, suggesting a visual topic change that should
have its own audio clip.

Run after W3a (audio generation) but before W4 (timings).

Usage:
  python3 tools/verify_splits.py <project>
  python3 tools/verify_splits.py <project> <section_filter>

Exit codes:
  0 — no flags, or warnings only (non-blocking)
  1 — fatal parse error
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from alignment_utils import find_sentence_boundaries, get_text_in_range
except ImportError:
    sys.path.insert(0, str(ROOT / "tools"))
    from alignment_utils import find_sentence_boundaries, get_text_in_range

# Clips shorter than this are unlikely to benefit from splitting
MIN_CLIP_SECONDS = 20.0

# Adjacent sentences sharing fewer than this many content words are flagged
MIN_OVERLAP_WORDS = 2

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "of",
    "for", "is", "was", "are", "were", "it", "its", "this", "that", "with",
    "as", "by", "from", "had", "has", "have", "they", "their", "he", "his",
    "she", "her", "we", "our", "not", "be", "been", "being", "would", "could",
    "should", "will", "shall", "may", "might", "can", "do", "did", "does",
    "so", "if", "then", "than", "too", "very", "just", "about", "up", "out",
    "no", "now", "only", "also", "more", "most", "some", "any", "all", "each",
    "every", "into", "over", "after", "before", "between", "through", "during",
    "until", "while", "when", "where", "which", "who", "whom", "what", "how",
}


def content_words(text: str) -> set[str]:
    """Extract content words (lowercase, stopwords removed)."""
    words = set(re.sub(r"[^\w\s]", "", text.lower()).split())
    return words - STOPWORDS


def check_clip(json_path: Path, audio_file: str) -> list[dict]:
    """Check one audio clip for potential missed topic splits."""
    data = json.loads(json_path.read_text())
    ends = data.get("character_end_times_seconds", [])
    if not ends:
        return []

    total = ends[-1]
    if total < MIN_CLIP_SECONDS:
        return []

    boundaries = find_sentence_boundaries(json_path)
    if len(boundaries) < 3:
        return []

    # Get text for each sentence segment
    sentences = []
    for i in range(len(boundaries) - 1):
        text = get_text_in_range(json_path, boundaries[i], boundaries[i + 1])
        if text:
            sentences.append((boundaries[i], boundaries[i + 1], text))

    # Compare adjacent sentences for topic shifts
    flags = []
    for i in range(len(sentences) - 1):
        s1_start, s1_end, text1 = sentences[i]
        s2_start, s2_end, text2 = sentences[i + 1]

        words1 = content_words(text1)
        words2 = content_words(text2)
        overlap = words1 & words2

        if len(overlap) < MIN_OVERLAP_WORDS:
            flags.append({
                "boundary_time": s2_start,
                "before_time": f"{s1_start:.1f}s - {s1_end:.1f}s",
                "after_time": f"{s2_start:.1f}s - {s2_end:.1f}s",
                "before_text": text1[:120],
                "after_text": text2[:120],
                "overlap_count": len(overlap),
                "overlap_words": sorted(overlap),
            })

    return flags


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_splits.py <project> [section_filter]")
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
        sys.exit(1)

    matched = [
        f for f in json_files
        if not section_filter or section_filter in f.stem
    ]

    print(f"\n{'=' * 70}")
    print(f"SPLIT VALIDATION — {project}")
    print(f"Flags adjacent sentences with <{MIN_OVERLAP_WORDS} shared content words")
    print(f"in clips >{MIN_CLIP_SECONDS:.0f}s. These may need separate audio files.")
    print(f"{'=' * 70}\n")

    total_flags = 0
    total_clips = 0

    for json_path in matched:
        audio_file = json_path.stem
        flags = check_clip(json_path, audio_file)
        total_clips += 1

        if flags:
            data = json.loads(json_path.read_text())
            total_s = data["character_end_times_seconds"][-1]
            print(f"  [{audio_file}]  ({total_s:.1f}s)  {len(flags)} potential split point(s)")
            print(f"  {'─' * 60}")

            for f in flags:
                print(f"    at {f['boundary_time']:.1f}s  ({f['overlap_count']} shared words: {f['overlap_words']})")
                print(f"      BEFORE ({f['before_time']}): {f['before_text']}")
                print(f"      AFTER  ({f['after_time']}):  {f['after_text']}")
                print()

            total_flags += len(flags)
        else:
            data = json.loads(json_path.read_text())
            ends = data.get("character_end_times_seconds", [])
            total_s = ends[-1] if ends else 0
            if total_s < MIN_CLIP_SECONDS:
                print(f"  [{audio_file}]  ({total_s:.1f}s)  skipped (< {MIN_CLIP_SECONDS:.0f}s)")
            else:
                print(f"  [{audio_file}]  ({total_s:.1f}s)  OK")

    print(f"\n{'=' * 70}")
    if total_flags:
        print(f"FLAGS — {total_flags} potential split point(s) across {total_clips} clip(s).")
        print(f"Review each flag. If the topic genuinely changes, split the narration")
        print(f"in generate_audio.py into separate audio files at the flagged boundary.")
        print(f"If the flag is a false positive (same topic, different vocabulary), ignore it.")
    else:
        print(f"PASSED — {total_clips} clip(s) checked. No split issues detected.")

    # Non-blocking exit — flags are advisory
    sys.exit(0)


if __name__ == "__main__":
    main()
