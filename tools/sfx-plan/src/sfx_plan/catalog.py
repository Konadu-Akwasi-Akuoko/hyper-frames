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
    OverridesShapeError,
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


def apply_overrides(catalog: dict[str, Any], overrides_path: Path) -> tuple[dict[str, Any], int]:
    """Apply per-video cue overrides to `catalog` (mutating, returning it).

    Returns (catalog, touched_count). Missing file is a no-op (touched=0).

    Per cue:
      - Existing cue → shallow-replace each top-level field set in the override.
        `filter` is replaced wholesale, not deep-merged.
      - New cue → register the override as a new cue. Must include a non-empty
        `filter`; `default_lead_ms` / `default_volume` are optional.

    Validation: every resulting cue must still have a non-empty filter.
    """
    if not overrides_path.exists():
        return catalog, 0
    raw = yaml.safe_load(overrides_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise OverridesShapeError(message=f"top-level must be a mapping, got {type(raw).__name__}")
    cues_in = raw.get("cues")
    if cues_in is None:
        return catalog, 0
    if not isinstance(cues_in, dict):
        raise OverridesShapeError(
            message=f"`cues` must be a mapping, got {type(cues_in).__name__}",
        )

    cues = catalog.setdefault("cues", {})
    touched = 0
    for name, override in cues_in.items():
        if not isinstance(override, dict):
            raise OverridesShapeError(
                message=f"cue {name!r} override must be a mapping, got {type(override).__name__}",
            )
        existing = cues.get(name)
        if existing is None:
            if "filter" not in override or not isinstance(override["filter"], dict) or not override["filter"]:
                raise EmptyCueFilterError(cue=name)
            new_cue = dict(override)
            new_cue["filter"] = dict(override["filter"])
            new_cue.setdefault("default_volume", 1.0)
            cues[name] = new_cue
        else:
            for key, value in override.items():
                if key == "filter":
                    if not isinstance(value, dict) or not value:
                        raise EmptyCueFilterError(cue=name)
                    existing["filter"] = dict(value)
                else:
                    existing[key] = value
            if not existing.get("filter"):
                raise EmptyCueFilterError(cue=name)
        touched += 1
    return catalog, touched


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
