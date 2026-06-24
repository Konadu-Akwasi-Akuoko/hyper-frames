#!/usr/bin/env python3
"""Apply title_shape/title_pattern classifications (from the workflow) to the catalog.

The classification workflow returns judgment only; this deterministic merge does the
file mutation — one writer, validated against the fixed enums, keyed by slug. This
keeps 54 parallel agents from hand-editing JSON.

Usage:
    python3 tools/thumbnail-inspo/apply_classifications.py <classifications.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parent / "catalog"

TITLE_SHAPES = {
    "speed-primer", "x-explained", "every-x-explained", "comparison-vs",
    "what-is-x", "open-why-how", "listicle-n", "assumption-flip",
    "panic-threat", "curiosity-reversal", "scale-story", "first-person-feat",
    "identity-advice", "meme-skit",
}
TITLE_PATTERNS = {
    "concrete-noun-verb", "curiosity-gap-reversal", "open-what-why-how",
    "assumption-flip", "identity-status",
}


def apply(classifications: list[dict], catalog_dir: Path) -> tuple[int, list[str]]:
    by_slug: dict[str, dict] = {}
    errors: list[str] = []
    for c in classifications:
        slug = c.get("slug")
        shape = c.get("title_shape")
        pattern = c.get("title_pattern")
        if not slug:
            errors.append(f"{c!r}: missing slug")
            continue
        if shape not in TITLE_SHAPES:
            errors.append(f"{slug}: bad title_shape {shape!r}")
            continue
        if pattern not in TITLE_PATTERNS:
            errors.append(f"{slug}: bad title_pattern {pattern!r}")
            continue
        by_slug[slug] = c

    applied = 0
    seen: set[str] = set()
    for fp in sorted(catalog_dir.glob("*.json")):
        entries = json.loads(fp.read_text())
        if not isinstance(entries, list):
            continue
        changed = False
        for e in entries:
            c = by_slug.get(e.get("slug"))
            if not c:
                continue
            e["title_shape"] = c["title_shape"]
            e["title_pattern"] = c["title_pattern"]
            seen.add(e["slug"])
            applied += 1
            changed = True
        if changed:
            fp.write_text(json.dumps(entries, indent=2) + "\n")

    for slug in by_slug:
        if slug not in seen:
            errors.append(f"{slug}: slug not found in catalog")
    return applied, errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: apply_classifications.py <classifications.json>", file=sys.stderr)
        return 2
    data = json.loads(Path(argv[1]).read_text())
    applied, errors = apply(data, CATALOG_DIR)
    print(f"applied {applied} classifications")
    for msg in errors:
        print(f"  ! {msg}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
