#!/usr/bin/env python3
"""
MoneyMath — Timing Verification Gate
Runs before Remotion preview launch to catch sync issues early.

Checks:
  1. timing.ts exists and is well-formed
  2. All narration audio files exist
  3. Total visual frames (timing.ts) match total audio frames within tolerance
  4. No single visual exceeds the max pacing threshold (12s / 360 frames)
  5. Per-section frame drift (each section's visual frames vs its audio duration)
  6. Stale dur values in AUDIO_SECTIONS (composition TSX vs actual MP3 durations)

Usage:
  python3 tools/verify_timings.py <project>

Exit codes:
  0 — all checks passed
  1 — one or more checks failed (do not launch preview until fixed)
"""

import sys
import re
import math
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FPS = 30
WARN_FRAMES_PER_VISUAL = 360   # 12s — hard warning threshold
TARGET_FRAMES_PER_VISUAL = 300  # 10s — ideal target
FRAME_TOLERANCE = 30           # 1s — acceptable total drift between audio and visual


def get_duration_frames(filepath: Path) -> int:
    """Sample-accurate frame count via stream duration (math.ceil)."""
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
        result2 = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(filepath)],
            capture_output=True, text=True,
        )
        data2 = json.loads(result2.stdout)
        seconds = float(data2["format"]["duration"])
    return math.ceil(seconds * FPS)


def parse_timing_ts(path: Path) -> list[list[int]]:
    """Extract all number arrays from timing.ts."""
    text = path.read_text()
    # Match arrays like [325, 325, 325, 325]
    arrays = re.findall(r'\[\s*([0-9][0-9,\s]*)\s*\]', text)
    result = []
    for arr in arrays:
        nums = [int(x.strip()) for x in arr.split(',') if x.strip().isdigit()]
        if nums:
            result.append(nums)
    return result


def parse_sections_config(project: str) -> list[tuple[str, list[str]]] | None:
    """Return [(section_name, [audio_file, ...]), ...] from calculate_timings.py."""
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
            section_blocks = re.findall(r'\(\s*"([^"]+)"\s*,\s*\[(.*?)\]\s*\)', raw, re.DOTALL)
            result = []
            for sec_name, audio_block in section_blocks:
                audio_files = re.findall(r'\(\s*"([^"]+)"\s*,\s*\d+\s*\)', audio_block)
                result.append((sec_name, audio_files))
            return result
    return None


def find_composition_tsx(project: str) -> Path | None:
    """Find the composition TSX file (not visuals.tsx) in src/<project>/."""
    src_dir = ROOT / "src" / project
    if not src_dir.exists():
        return None
    for f in src_dir.glob("*.tsx"):
        if f.name != "visuals.tsx":
            return f
    return None


def parse_audio_section_durs(tsx_path: Path) -> list[tuple[str, int]]:
    """Parse { file: "...", ..., dur: N } entries from AUDIO_SECTIONS in composition."""
    content = tsx_path.read_text()
    entries = re.findall(r'file:\s*"([^"]+)".*?dur:\s*(\d+)', content, re.DOTALL)
    return [(f, int(d)) for f, d in entries]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/verify_timings.py <project>")
        sys.exit(1)

    project = sys.argv[1]
    audio_dir = ROOT / "projects" / project / "audio"
    timing_ts = ROOT / "src" / project / "timing.ts"

    print(f"=== Timing Verification: {project} ===\n")
    errors = []
    warnings = []

    # ── Check 1: timing.ts exists ─────────────────────────────────────────────
    if not timing_ts.exists():
        errors.append(f"timing.ts not found at {timing_ts}")
        print(f"  ✗  timing.ts missing")
    else:
        print(f"  ✓  timing.ts found")

    # ── Check 2: audio dir exists ─────────────────────────────────────────────
    if not audio_dir.exists():
        errors.append(f"Audio directory not found: {audio_dir}")
        print(f"  ✗  Audio directory missing")
    else:
        print(f"  ✓  Audio directory found")

    if errors:
        print(f"\n{'='*50}")
        print(f"FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  ✗  {e}")
        sys.exit(1)

    # ── Check 3: narration audio files exist ──────────────────────────────────
    mp3_files = sorted([
        f for f in audio_dir.glob("*.mp3")
        if f.name != "music_bg.mp3"
    ])
    if not mp3_files:
        errors.append("No narration audio files found (excluding music_bg.mp3)")
    else:
        print(f"  ✓  {len(mp3_files)} narration audio file(s) found")

    # ── Check 3b: background music exists ─────────────────────────────────────
    music_file = audio_dir / "music_bg.mp3"
    if not music_file.exists():
        errors.append("music_bg.mp3 missing — run generate_music.py before preview")
        print(f"  ✗  music_bg.mp3 missing")
    else:
        print(f"  ✓  music_bg.mp3 found")

    # ── Check 4: parse timing.ts ──────────────────────────────────────────────
    visual_timings = parse_timing_ts(timing_ts)
    if not visual_timings:
        errors.append("Could not parse VISUAL_TIMINGS from timing.ts")
    else:
        print(f"  ✓  timing.ts parsed: {len(visual_timings)} section(s)")

    if errors:
        print(f"\n{'='*50}")
        print(f"FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  ✗  {e}")
        sys.exit(1)

    # ── Check 5: per-visual pacing ────────────────────────────────────────────
    print(f"\n  Visual pacing (target ≤{TARGET_FRAMES_PER_VISUAL/FPS:.0f}s, warn >{WARN_FRAMES_PER_VISUAL/FPS:.0f}s):")
    pacing_ok = True
    for i, section in enumerate(visual_timings):
        max_f = max(section)
        max_s = max_f / FPS
        n = len(section)
        total_s = sum(section) / FPS
        if max_f > WARN_FRAMES_PER_VISUAL:
            flag = f"⚠  {max_s:.1f}s/visual — TOO LONG, add more images (need ~{math.ceil(total_s / (TARGET_FRAMES_PER_VISUAL / FPS))} visuals)"
            warnings.append(f"Section {i}: max {max_s:.1f}s per visual exceeds {WARN_FRAMES_PER_VISUAL/FPS:.0f}s threshold")
            pacing_ok = False
        elif max_f > TARGET_FRAMES_PER_VISUAL:
            flag = f"○  {max_s:.1f}s/visual — slightly long"
        else:
            flag = f"✓  {max_s:.1f}s/visual"
        print(f"    s{i} ({n} visuals, {total_s:.1f}s): {flag}")

    # ── Check 6: total frames match ───────────────────────────────────────────
    total_visual_frames = sum(sum(s) for s in visual_timings)
    total_audio_frames = sum(get_duration_frames(f) for f in mp3_files)
    drift = total_visual_frames - total_audio_frames

    print(f"\n  Frame totals:")
    print(f"    Visual (timing.ts): {total_visual_frames}f ({total_visual_frames/FPS:.1f}s)")
    print(f"    Audio (measured):   {total_audio_frames}f ({total_audio_frames/FPS:.1f}s)")
    print(f"    Drift:              {drift:+d}f ({drift/FPS*1000:.0f}ms)")

    if abs(drift) > FRAME_TOLERANCE:
        errors.append(f"Total frame drift {drift:+d}f exceeds tolerance ±{FRAME_TOLERANCE}f — re-run calculate_timings.py")
    elif drift < 0:
        warnings.append(f"Visual frames ({total_visual_frames}) < audio frames ({total_audio_frames}) — audio may be clipped at section ends")

    # ── Check 7: per-section frame drift ─────────────────────────────────────
    sections_config = parse_sections_config(project)
    if sections_config:
        print(f"\n  Per-section drift (visual frames vs audio frames):")
        section_drift_ok = True
        for i, (sec_name, audio_files) in enumerate(sections_config):
            if i >= len(visual_timings):
                break
            section_visual_f = sum(visual_timings[i])
            section_audio_f  = sum(
                get_duration_frames(audio_dir / f"{af}.mp3")
                for af in audio_files
                if (audio_dir / f"{af}.mp3").exists()
            )
            sec_drift = section_visual_f - section_audio_f
            if sec_drift != 0:
                errors.append(
                    f"Section {i} ({sec_name}): visual {section_visual_f}f vs "
                    f"audio {section_audio_f}f (drift {sec_drift:+d}f) — re-run calculate_timings.py"
                )
                section_drift_ok = False
                print(f"    s{i} {sec_name:<15} ⚠  drift {sec_drift:+d}f — timing.ts may have been manually edited")
            else:
                print(f"    s{i} {sec_name:<15} ✓  {section_visual_f}f")
        if section_drift_ok:
            print(f"    All sections matched exactly.")
    else:
        print(f"\n  Per-section drift: skipped (could not parse SECTIONS config)")

    # ── Check 8: stale dur values in composition ──────────────────────────────
    comp_tsx = find_composition_tsx(project)
    if comp_tsx:
        audio_durs = parse_audio_section_durs(comp_tsx)
        if audio_durs:
            print(f"\n  AUDIO_SECTIONS dur check ({comp_tsx.name}):")
            stale_ok = True
            for af, coded_dur in audio_durs:
                mp3 = audio_dir / f"{af}.mp3"
                if not mp3.exists():
                    print(f"    {af:<28} ⚠  MP3 not found — skipping")
                    continue
                actual_dur = get_duration_frames(mp3)
                dur_drift  = coded_dur - actual_dur
                if dur_drift != 0:
                    errors.append(
                        f"AUDIO_SECTIONS dur stale for '{af}': "
                        f"{coded_dur}f coded vs {actual_dur}f actual (drift {dur_drift:+d}f) — "
                        f"update AUDIO_SECTIONS in {comp_tsx.name}"
                    )
                    stale_ok = False
                    print(f"    {af:<28} ⚠  STALE: coded {coded_dur}f, actual {actual_dur}f (drift {dur_drift:+d}f)")
                else:
                    print(f"    {af:<28} ✓  {coded_dur}f")
            if stale_ok:
                print(f"    All dur values match actual MP3 durations.")
        else:
            print(f"\n  AUDIO_SECTIONS dur check: no entries found in {comp_tsx.name}")
    else:
        print(f"\n  AUDIO_SECTIONS dur check: skipped (no composition TSX in src/{project}/)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    if errors:
        print(f"FAILED — {len(errors)} error(s), {len(warnings)} warning(s):")
        for e in errors:
            print(f"  ✗  {e}")
        for w in warnings:
            print(f"  ⚠  {w}")
        print(f"\n  Fix the errors above before launching Remotion preview.")
        sys.exit(1)
    elif warnings:
        print(f"WARNINGS — {len(warnings)} issue(s) (preview will work but quality may suffer):")
        for w in warnings:
            print(f"  ⚠  {w}")
        print(f"\n  Consider adding more images to flagged sections before launch.")
        sys.exit(0)
    else:
        print(f"PASSED — all checks OK. Ready to launch preview.")
        sys.exit(0)


if __name__ == "__main__":
    main()
