#!/usr/bin/env python3
"""
alignment_utils.py — Shared sentence-boundary detection and window grouping.

Used by calculate_timings.py, generate_prompt_windows.py, verify_prompt_order.py,
verify_splits.py, and verify_post_reorder.py to produce sentence-aware timing
windows instead of fixed even-duration or fixed 10-second windows.
"""

import json
from pathlib import Path

# Filler words used as verbal transitions between topics.
# When a filler sits between two close sentence boundaries, the visual cut
# should happen AFTER the filler (grouping it with the preceding content)
# rather than before it.
_FILLER_WORDS = {"hmm", "alright", "yeah", "okay", "ok"}

# Boundaries closer than this are merged.
_MIN_BOUNDARY_GAP = 2.0


def find_sentence_boundaries(json_path: Path) -> list[float]:
    """
    Read ElevenLabs character-level alignment JSON and detect sentence boundaries.

    A sentence boundary is detected when sentence-ending punctuation (. ? !)
    is followed by a space or newline. Returns a sorted list of timestamps
    [0.0, t1, t2, ..., total] where each interior value is the start time
    of a new sentence.

    Boundaries closer than 2 seconds apart are merged. When the short segment
    between two close boundaries contains only a filler word (Hmm, Alright,
    Yeah, Okay), the later boundary is kept instead of the earlier one — this
    groups the filler with the preceding content so the visual cut lands after
    the filler, right when the new idea begins.

    Returns an empty list if the file cannot be read or has no alignment data.
    """
    try:
        data = json.loads(json_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    chars = data.get("characters", [])
    starts = data.get("character_start_times_seconds", [])
    ends = data.get("character_end_times_seconds", [])

    if not chars or not ends:
        return []

    total = ends[-1]
    boundaries = [0.0]

    n = len(chars)
    i = 0
    while i < n:
        if chars[i] in ".?!" and i + 1 < n and chars[i + 1] in " \n":
            # Sentence-ending punctuation followed by space or newline.
            # Skip all whitespace (spaces + newlines from paragraph breaks)
            # to find the start of the next sentence.
            j = i + 2
            while j < n and chars[j] in " \n":
                j += 1
            if j < n:
                boundary = starts[j]
                gap = boundary - boundaries[-1]

                if gap >= _MIN_BOUNDARY_GAP:
                    boundaries.append(boundary)
                elif gap >= 0.3:
                    # Close to previous boundary — check if the text between
                    # them is a filler word. If so, shift the boundary forward
                    # so the filler is grouped with the preceding content.
                    between = "".join(
                        c for c, s in zip(chars, starts)
                        if boundaries[-1] <= s < boundary
                    ).strip().rstrip(".!?").strip()
                    if between.lower() in _FILLER_WORDS:
                        boundaries[-1] = boundary
                    # else: keep the earlier boundary (default behavior)
            i = j
        else:
            i += 1

    if boundaries[-1] < total:
        boundaries.append(total)

    return boundaries


def group_boundaries_into_windows(
    boundaries: list[float],
    num_images: int,
) -> list[tuple[float, float]]:
    """
    Partition sentences (defined by boundary timestamps) into num_images
    contiguous windows, snapping splits to sentence boundaries.

    The algorithm selects (num_images - 1) interior boundaries as split points,
    choosing the boundary nearest each ideal equal-duration split while
    preserving order and ensuring each window gets at least one segment.

    Args:
        boundaries: sorted [0.0, t1, t2, ..., total] from find_sentence_boundaries()
        num_images: number of windows to produce

    Returns:
        [(start_s, end_s), ...] — exactly num_images windows whose durations
        sum to total. Durations are variable, snapped to sentence breaks.
        Returns empty list if boundaries are invalid.
    """
    if not boundaries or len(boundaries) < 2:
        return []

    total = boundaries[-1]
    n_segments = len(boundaries) - 1  # sentence segments

    if num_images <= 1 or n_segments <= 1:
        return [(0.0, total)]

    if num_images >= n_segments:
        # At least one image per sentence. If more images than sentences,
        # split the longest window in half until we have enough.
        windows = [(boundaries[i], boundaries[i + 1]) for i in range(n_segments)]
        while len(windows) < num_images:
            idx = max(range(len(windows)), key=lambda j: windows[j][1] - windows[j][0])
            s, e = windows[idx]
            mid = (s + e) / 2.0
            windows[idx : idx + 1] = [(s, mid), (mid, e)]
        return windows

    # More sentences than images — group into num_images contiguous windows.
    # Pick (num_images - 1) interior boundaries as split points, each closest
    # to its ideal equal-duration position.
    ideal_dur = total / num_images
    interior = boundaries[1:-1]  # exclude 0.0 and total

    chosen: list[float] = []
    remaining = list(interior)

    for split_idx in range(1, num_images):
        target = split_idx * ideal_dur
        splits_left = (num_images - 1) - len(chosen) - 1

        # Must leave enough candidates for remaining splits
        if splits_left > 0 and len(remaining) > splits_left:
            choosable = remaining[: len(remaining) - splits_left]
        elif remaining:
            choosable = remaining[:1]
        else:
            break

        best = min(choosable, key=lambda b: abs(b - target))
        chosen.append(best)

        # Remove chosen and everything before it from remaining candidates
        cut = remaining.index(best)
        remaining = remaining[cut + 1 :]

    all_splits = [0.0] + chosen + [total]
    return [(all_splits[i], all_splits[i + 1]) for i in range(len(all_splits) - 1)]


def get_text_in_range(json_path: Path, start_s: float, end_s: float) -> str:
    """Return the narration text spoken between start_s and end_s."""
    try:
        data = json.loads(json_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

    chars = data.get("characters", [])
    starts = data.get("character_start_times_seconds", [])

    return "".join(c for c, s in zip(chars, starts) if start_s <= s < end_s).strip()
