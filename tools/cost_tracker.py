"""Shared API cost tracker for MoneyMath pipeline.

Logs per-call costs to a `costs.json` ledger inside each project directory.
Use `upload_costs.py` to aggregate and push to Google Sheets.

Pricing defaults are defined here and can be updated as rates change.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Pricing defaults (USD) — update these when provider pricing changes
# ---------------------------------------------------------------------------

PRICING = {
    # Gemini 3.1 Pro Preview (text generation)
    "gemini_input_per_1m_tokens": 2.00,
    "gemini_output_per_1m_tokens": 12.00,
    # Gemini 3 Flash Preview (text generation)
    "gemini_flash_input_per_1m_tokens": 0.50,
    "gemini_flash_output_per_1m_tokens": 3.00,
    # Gemini 3 Pro Image / Nano Banana Pro (4K)
    "gemini_image_4k_per_image": 0.24,
    # ElevenLabs TTS (multilingual_v2, 1 credit = 1 char)
    "elevenlabs_tts_per_1k_chars": 0.30,
    # ElevenLabs Music (music_v1)
    "elevenlabs_music_per_second": 0.04,
    # ElevenLabs SFX
    "elevenlabs_sfx_per_second": 0.04,
}


def _ledger_path(project_dir: Path) -> Path:
    """Return the costs.json path for a project directory."""
    return project_dir / "costs.json"


def _append_entry(project_dir: Path, entry: dict) -> None:
    """Append a cost entry to the project's costs.json ledger."""
    if not project_dir.is_dir():
        return

    ledger = _ledger_path(project_dir)
    entries: list[dict] = []
    if ledger.exists():
        try:
            entries = json.loads(ledger.read_text())
        except (json.JSONDecodeError, OSError):
            entries = []

    entry["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entries.append(entry)
    ledger.write_text(json.dumps(entries, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_gemini_cost(
    project_dir: Path,
    input_tokens: int,
    output_tokens: int,
    phase_label: str,
) -> float:
    """Log a Gemini text generation API call cost."""
    is_flash = os.environ.get("GEMINI_MODEL", "").lower().find("flash") >= 0

    if is_flash:
        input_rate = PRICING["gemini_flash_input_per_1m_tokens"]
        output_rate = PRICING["gemini_flash_output_per_1m_tokens"]
    else:
        input_rate = PRICING["gemini_input_per_1m_tokens"]
        output_rate = PRICING["gemini_output_per_1m_tokens"]

    cost = (
        (input_tokens / 1_000_000) * input_rate
        + (output_tokens / 1_000_000) * output_rate
    )
    _append_entry(project_dir, {
        "provider": "gemini",
        "phase": phase_label,
        "service": "text_gen",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
    })
    return cost


def log_gemini_image_cost(
    project_dir: Path,
    num_images: int,
    phase_label: str,
) -> float:
    """Log a Gemini image generation call cost."""
    cost = num_images * PRICING["gemini_image_4k_per_image"]
    _append_entry(project_dir, {
        "provider": "gemini",
        "phase": phase_label,
        "service": "image_gen",
        "units": num_images,
        "unit_type": "images_4k",
        "cost_usd": round(cost, 6),
    })
    return cost


def log_elevenlabs_cost(
    project_dir: Path,
    service: str,
    units: float,
    phase_label: str,
) -> float:
    """Log an ElevenLabs API call cost.

    Args:
        service: One of "tts", "music", "sfx"
        units: Characters (for tts) or seconds (for music/sfx)
        phase_label: Human-readable label (e.g. "narration", "bg_music")
    """
    if service == "tts":
        cost = (units / 1000) * PRICING["elevenlabs_tts_per_1k_chars"]
        unit_type = "characters"
    elif service == "music":
        cost = units * PRICING["elevenlabs_music_per_second"]
        unit_type = "seconds"
    elif service == "sfx":
        cost = units * PRICING["elevenlabs_sfx_per_second"]
        unit_type = "seconds"
    else:
        cost = 0.0
        unit_type = "unknown"

    _append_entry(project_dir, {
        "provider": "elevenlabs",
        "phase": phase_label,
        "service": service,
        "units": units,
        "unit_type": unit_type,
        "cost_usd": round(cost, 6),
    })
    return cost


def get_total_cost(project_dir: Path) -> float:
    """Read costs.json and return the aggregated total USD cost."""
    ledger = _ledger_path(project_dir)
    if not ledger.exists():
        return 0.0
    try:
        entries = json.loads(ledger.read_text())
        return sum(e.get("cost_usd", 0.0) for e in entries)
    except (json.JSONDecodeError, OSError):
        return 0.0


def get_cost_breakdown(project_dir: Path) -> dict:
    """Read costs.json and return a breakdown by provider and service.

    Returns dict like:
        {"gemini_text_gen": 0.05, "gemini_image_gen": 0.72,
         "elevenlabs_tts": 1.50, "elevenlabs_music": 7.20, ...}
    """
    ledger = _ledger_path(project_dir)
    if not ledger.exists():
        return {}
    try:
        entries = json.loads(ledger.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

    breakdown: dict[str, float] = {}
    for e in entries:
        key = f"{e.get('provider', 'unknown')}_{e.get('service', 'unknown')}"
        breakdown[key] = breakdown.get(key, 0.0) + e.get("cost_usd", 0.0)
    return breakdown
