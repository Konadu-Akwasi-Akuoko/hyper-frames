"""Scan design-catalog/*/meta.json, validate, and emit catalog.json."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_FIELDS = ("slug", "name", "description", "tags", "type", "dependencies", "files")
ALLOWED_TYPES = ("animated", "static")
REQUIRED_FILE_KEYS = ("preview", "snippet")


class ValidationError(Exception):
    """A meta.json failed schema validation; the message is per-file actionable."""


@dataclass
class Entry:
    path: str
    meta: dict[str, Any]


def _validate(meta_path: Path, meta: dict[str, Any]) -> None:
    rel = meta_path.parent.name
    where = f"{meta_path}"

    for field in REQUIRED_TOP_FIELDS:
        if field not in meta:
            raise ValidationError(f"{where}: missing required field '{field}'")

    if not isinstance(meta["slug"], str) or not meta["slug"]:
        raise ValidationError(f"{where}: 'slug' must be a non-empty string")
    if meta["slug"] != rel:
        raise ValidationError(
            f"{where}: slug '{meta['slug']}' does not match folder name '{rel}'"
        )

    if meta["type"] not in ALLOWED_TYPES:
        raise ValidationError(
            f"{where}: 'type' must be one of {ALLOWED_TYPES}, got {meta['type']!r}"
        )

    if not isinstance(meta["tags"], list) or not all(isinstance(t, str) for t in meta["tags"]):
        raise ValidationError(f"{where}: 'tags' must be a list of strings")

    if not isinstance(meta["dependencies"], list) or not all(
        isinstance(d, str) for d in meta["dependencies"]
    ):
        raise ValidationError(f"{where}: 'dependencies' must be a list of strings")

    files = meta["files"]
    if not isinstance(files, dict):
        raise ValidationError(f"{where}: 'files' must be an object")
    for key in REQUIRED_FILE_KEYS:
        if key not in files:
            raise ValidationError(f"{where}: 'files.{key}' is required")

    # Animated entries must declare a motion file; static entries must not.
    if meta["type"] == "animated" and "motion" not in files:
        raise ValidationError(
            f"{where}: type=animated requires 'files.motion' (set type=static if there is no motion kit)"
        )
    if meta["type"] == "static" and "motion" in files:
        raise ValidationError(
            f"{where}: type=static must not declare 'files.motion' (use type=animated)"
        )

    # Every referenced file must exist on disk.
    for key, rel_path in files.items():
        if not isinstance(rel_path, str):
            raise ValidationError(f"{where}: 'files.{key}' must be a string path")
        target = meta_path.parent / rel_path
        if not target.is_file():
            raise ValidationError(
                f"{where}: 'files.{key}' points to '{rel_path}' which does not exist"
            )


def build_catalog(root: Path) -> dict[str, Any]:
    """Scan `root` for `*/meta.json` files and return the catalog payload.

    Raises ValidationError on the first invalid entry — caller decides whether
    to swallow and continue or hard-fail (the CLI hard-fails).
    """
    entries: list[dict[str, Any]] = []
    meta_paths = sorted(root.glob("*/meta.json"))

    for mp in meta_paths:
        try:
            meta = json.loads(mp.read_text())
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{mp}: invalid JSON — {exc}") from exc
        if not isinstance(meta, dict):
            raise ValidationError(f"{mp}: top-level value must be an object")
        _validate(mp, meta)
        meta["path"] = mp.parent.name
        entries.append(meta)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entries": entries,
    }
