"""Catalog loader + filter engine.

The filter engine is a small DSL over flat dict operators:
    <field>           → entry[field] == value
    <field>_min       → entry[field] >= value
    <field>_max       → entry[field] <= value
    <field>_in        → entry[field] in value (value is a list)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sfx_plan.errors import (
    CatalogMissingError,
    CatalogVersionMismatchError,
    EmptyCueFilterError,
    UnknownCueError,
)

EXPECTED_CATALOG_VERSION = 1

_OP_SUFFIXES = ("_min", "_max", "_in")


def load_catalog(path: Path) -> dict[str, Any]:
    """Load a catalog YAML, validating the version field. Raises on missing or mismatch."""
    if not path.exists():
        raise CatalogMissingError(path=str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    version = raw.get("version") if isinstance(raw, dict) else None
    if version != EXPECTED_CATALOG_VERSION:
        raise CatalogVersionMismatchError(
            found=int(version) if isinstance(version, int) else 0,
            expected=EXPECTED_CATALOG_VERSION,
        )
    return raw


def _matches_filter(entry: dict[str, Any], flt: dict[str, Any]) -> bool:
    for key, expected in flt.items():
        for suffix in _OP_SUFFIXES:
            if key.endswith(suffix):
                field = key[: -len(suffix)]
                actual = entry.get(field)
                if actual is None:
                    return False
                if suffix == "_min" and not (actual >= expected):
                    return False
                if suffix == "_max" and not (actual <= expected):
                    return False
                if suffix == "_in" and actual not in expected:
                    return False
                break
        else:
            if entry.get(key) != expected:
                return False
    return True


def get_cue(cat: dict[str, Any], *, name: str, source: str) -> dict[str, Any]:
    """Return the cue recipe by name. Raises UnknownCueError with the known list."""
    cues = cat.get("cues", {})
    if name not in cues:
        raise UnknownCueError(cue=name, known=list(cues.keys()), source=source)
    return cues[name]


def filter_assets(
    cat: dict[str, Any],
    *,
    cue_name: str,
) -> list[tuple[str, dict[str, Any]]]:
    """Return sorted (path, entry) pairs whose metadata matches the cue's filter."""
    cue = cat["cues"].get(cue_name)
    if cue is None:
        raise UnknownCueError(cue=cue_name, known=list(cat["cues"].keys()), source="(filter)")
    flt = cue.get("filter", {}) or {}
    matches = [
        (path, entry)
        for path, entry in cat.get("assets", {}).items()
        if _matches_filter(entry, flt)
    ]
    if not matches:
        raise EmptyCueFilterError(cue=cue_name)
    return sorted(matches, key=lambda item: item[0])
