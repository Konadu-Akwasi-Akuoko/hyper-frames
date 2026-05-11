"""Auto-tagging + auto_role derivation.

These are heuristics — they get the catalog 90% of the way and leave headroom
for hand overrides via per-video sfx-overrides.yml (planned, not built here).
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    return _NON_ALNUM.sub("-", s.lower()).strip("-")


def derive_tags(
    rel_path: str,
    duration_s: float,
    attack_time_s: float,
    brightness: str,
) -> tuple[str, ...]:
    """Build a tag tuple from folder lineage + duration + attack + brightness."""
    parts = PurePosixPath(rel_path).parts
    folder_tags: list[str] = []
    if len(parts) >= 2:
        lib = _slugify(parts[0]).replace("-free-sfx", "").replace("-sfx", "")
        if lib:
            folder_tags.append(lib)
    if len(parts) >= 3:
        cat = _slugify(parts[-2])
        if cat:
            folder_tags.append(cat)

    duration_tag = "short" if duration_s < 0.5 else "long" if duration_s > 1.5 else "medium"
    attack_tag = "snappy" if attack_time_s < 0.05 else "swelling" if attack_time_s > 0.2 else None

    tags = list(dict.fromkeys(folder_tags + [duration_tag, brightness]))
    if attack_tag:
        tags.append(attack_tag)
    return tuple(tags)


def derive_auto_role(
    category: str,
    duration_s: float,
    attack_time_s: float,
    low_energy_pct: int,
    peak_time_s: float,
) -> str:
    """Derive an auto_role from category + envelope + spectral data.

    Priority order:
      ambience > riser > impact > transition > accent > foley
    """
    cat = category.lower()

    if duration_s >= 5.0:
        return "ambience"

    if duration_s >= 1.5 and attack_time_s >= 1.0:
        return "riser"

    if duration_s <= 0.6 and low_energy_pct >= 50 and peak_time_s <= 0.2:
        return "impact"

    if 0.3 <= duration_s <= 2.0 and attack_time_s >= 0.1:
        return "transition"

    if duration_s < 0.6 and attack_time_s < 0.1:
        return "accent"

    if any(k in cat for k in ("rustle", "paper", "foley", "crumple")):
        return "foley"

    return "accent"
