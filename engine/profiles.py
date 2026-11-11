"""Load and validate the bottle profile definitions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = PROJECT_ROOT / "profiles"


def load_profile(profile_id: str) -> dict[str, Any]:
    """Load a profile by its JSON filename stem."""
    path = PROFILE_DIR / f"{profile_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Unknown bottle profile: {profile_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_profile(data)
    return data


def validate_profile(profile: dict[str, Any]) -> None:
    """Raise ValueError when dimensions or metadata are inconsistent."""
    required = ("id", "width_px", "height_px", "dpi", "physical_width_mm", "physical_height_mm")
    missing = [key for key in required if key not in profile]
    if missing:
        raise ValueError(f"Profile missing required fields: {', '.join(missing)}")

    for key in ("width_px", "height_px", "dpi"):
        if not isinstance(profile[key], int) or profile[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")

    expected_width = profile["width_px"] / profile["dpi"] * 25.4
    expected_height = profile["height_px"] / profile["dpi"] * 25.4
    if abs(expected_width - profile["physical_width_mm"]) > 0.02:
        raise ValueError("physical_width_mm does not match pixel dimensions and DPI")
    if abs(expected_height - profile["physical_height_mm"]) > 0.02:
        raise ValueError("physical_height_mm does not match pixel dimensions and DPI")


def list_profiles() -> list[dict[str, Any]]:
    """Return all valid profiles, sorted by profile ID."""
    profiles = []
    for path in sorted(PROFILE_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_profile(data)
        profiles.append(data)
    return profiles
