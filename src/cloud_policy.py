"""Read-only, versioned cloud recommendations. No credentials and no API calls."""
from __future__ import annotations

import hashlib
import math
from datetime import date
from pathlib import Path

import yaml

from validation import validate_data

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "cloud-tiers.yaml"
SCHEMAS = REPO_ROOT / "schemas"
TIERS = ("preparation", "tests", "production")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_cloud_policy(path: Path = DEFAULT_CONFIG) -> dict:
    policy = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    validate_data(policy, SCHEMAS / "cloud-tiers.schema.yaml")
    for tier in policy["tiers"].values():
        for medium in ("text", "image", "video", "audio"):
            entry = tier[medium]
            required = {
                "text": {"input_per_million", "output_per_million"},
                "image": {"output_per_image", "input_per_reference"},
                "video": {"output_per_second"},
                "audio": {"output_per_second"},
            }[medium]
            if not required <= entry["pricing"].keys():
                raise ValueError(f"Incomplete pricing for {medium}")
            if any(not math.isfinite(value) for value in entry["pricing"].values()):
                raise ValueError(f"Non-finite pricing for {medium}")
            resolution = entry.get("defaults", {}).get("resolution")
            if resolution and resolution not in entry["capabilities"].get("resolutions", []):
                raise ValueError(f"Unsupported default resolution for {medium}")
    return policy


def pricing_is_current(policy: dict, as_of: date | None = None) -> bool:
    age = ((as_of or date.today()) - date.fromisoformat(policy["pricing_checked_at"])).days
    return 0 <= age <= policy["pricing_max_age_days"]
