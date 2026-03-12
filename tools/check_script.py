#!/usr/bin/env python3
"""
MoneyMath — Script Quality Checker
Validates narration text against all banned patterns before audio generation.

Usage:
    python3 tools/check_script.py <project-slug>

Exit codes:
    0 — all checks passed
    1 — one or more violations found (do not proceed to Wave 3)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── Narration extraction ────────────────────────────────────────────────────

def extract_narration_lines(script: str) -> list[tuple[int, str]]:
    """Return (line_number, text) for every line inside [sN_*] sections only."""
    results = []
    in_section = False
    for i, line in enumerate(script.splitlines(), start=1):
        if re.match(r"^\[s\d+_\w+\]", line.strip()):
            in_section = True
            continue
        if line.strip() == "---":
            in_section = False
            continue
        # Stop at non-narration headers
        if re.match(r"^#{1,3} ", line) or re.match(r"^\[THUMBNAIL\]", line):
            in_section = False
            continue
        if in_section and line.strip():
            results.append((i, line))
    return results


# ── Check definitions ───────────────────────────────────────────────────────

CHECKS = [

    # ── Dashes ──
    {
        "name": "Em dash / en dash",
        "pattern": re.compile(r"[—–]"),
        "message": "Replace — or – with a comma or period.",
    },
    {
        "name": "Hyphen in word",
        "pattern": re.compile(r"[a-z]-[a-z]"),
        "message": "Remove hyphen: 'sixty-five' → 'sixty five', 'boot-blacking' → 'boot blacking'.",
    },

    # ── Digits / symbols ──
    {
        "name": "Digit in narration",
        "pattern": re.compile(r"\b\d+\b"),
        "message": "Spell out all numbers: '42' → 'forty two', '1958' → 'nineteen fifty eight'.",
    },
    {
        "name": "Percent symbol",
        "pattern": re.compile(r"\d+%|%"),
        "message": "Spell out: '4%' → 'four percent'.",
    },
    {
        "name": "Dollar sign",
        "pattern": re.compile(r"\$\d|\$[A-Z]"),
        "message": "Spell out: '$420' → 'four hundred twenty dollars'.",
    },

    # ── Filler check (warning, not error) ──
]

FILLER_PATTERN = re.compile(r"\b(Okay|Hmm|Alright|Yeah)\b", re.IGNORECASE)


# ── Runner ──────────────────────────────────────────────────────────────────

def run(project: str) -> bool:
    script_path = ROOT / "projects" / project / "script.md"
    if not script_path.exists():
        print(f"ERROR: {script_path} not found")
        return False

    script = script_path.read_text()
    narration_lines = extract_narration_lines(script)

    if not narration_lines:
        print("ERROR: No narration sections found (looking for [s1_hook], [s2_*], etc.)")
        return False

    print(f"Checking {project}/script.md — {len(narration_lines)} narration lines\n")

    errors: list[tuple[str, int, str, str]] = []  # (check_name, line_num, text, message)

    for check in CHECKS:
        for line_num, text in narration_lines:
            if check["pattern"].search(text):
                errors.append((check["name"], line_num, text.strip(), check["message"]))

    # ── Filler presence check (one warning per section) ──
    sections = re.findall(r"\[(s\d+_\w+)\](.*?)(?=\[s\d+|\Z)", script, re.DOTALL)
    filler_warnings = []
    for sec_name, sec_text in sections:
        if not FILLER_PATTERN.search(sec_text):
            filler_warnings.append(sec_name)

    # ── Report ──────────────────────────────────────────────────────────────
    if errors:
        print(f"  ERRORS — {len(errors)} violation(s) found:\n")
        last_check = None
        for check_name, line_num, text, message in errors:
            if check_name != last_check:
                print(f"  ── {check_name} ──")
                last_check = check_name
            # Truncate long lines for readability
            display = text if len(text) <= 100 else text[:97] + "..."
            print(f"    Line {line_num}: {display}")
            print(f"    Fix: {message}\n")
    else:
        print("  ✓ No errors found\n")

    if filler_warnings:
        print(f"  WARNINGS — missing fillers (Okay/Hmm/Alright/Yeah) in:")
        for sec in filler_warnings:
            print(f"    {sec}")
        print()
    else:
        print("  ✓ Fillers present in all sections\n")

    passed = len(errors) == 0
    if passed:
        print("PASSED — script is clean. Proceed to Wave 3.")
    else:
        print("FAILED — fix all errors above before generating audio or images.")

    return passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/check_script.py <project-slug>")
        sys.exit(1)
    ok = run(sys.argv[1])
    sys.exit(0 if ok else 1)
