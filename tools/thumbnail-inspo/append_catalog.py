#!/usr/bin/env python3
"""Append agent-authored catalog entries into the per-channel catalog files.

The coverage-cataloging workflow returns judgment (one entry dict per harvested
thumbnail); this deterministic merge validates each against the catalog schema +
fixed enums and appends it to tools/thumbnail-inspo/catalog/<channel>-1.json,
deduped by slug. One writer per file, run after the workflow.

Usage:
    python3 tools/thumbnail-inspo/append_catalog.py <new_entries.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parent / "catalog"

REQUIRED = [
    "slug", "channel", "file", "archetype", "layout", "device", "face", "accent",
    "text", "reads_as", "layout_map", "why_it_works", "mimic_for", "watch_url",
    "title", "title_shape", "title_pattern",
]
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
TEXT = {"low", "med", "high"}


def _validate(e: dict) -> list[str]:
    errs = []
    for k in REQUIRED:
        if k not in e or e[k] in (None, ""):
            errs.append(f"{e.get('slug','?')}: missing {k}")
    if e.get("title_shape") not in TITLE_SHAPES:
        errs.append(f"{e.get('slug','?')}: bad title_shape {e.get('title_shape')!r}")
    if e.get("title_pattern") not in TITLE_PATTERNS:
        errs.append(f"{e.get('slug','?')}: bad title_pattern {e.get('title_pattern')!r}")
    if e.get("text") not in TEXT:
        errs.append(f"{e.get('slug','?')}: bad text {e.get('text')!r}")
    if not isinstance(e.get("device"), list):
        errs.append(f"{e.get('slug','?')}: device must be a list")
    return errs


def append(new_entries: list[dict], catalog_dir: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    valid: list[dict] = []
    for e in new_entries:
        errs = _validate(e)
        if errs:
            errors.extend(errs)
        else:
            valid.append(e)

    by_channel: dict[str, list[dict]] = {}
    for e in valid:
        by_channel.setdefault(e["channel"], []).append(e)

    added = 0
    for channel, entries in by_channel.items():
        fp = catalog_dir / f"{channel}-1.json"
        if not fp.exists():
            errors.append(f"{channel}: no catalog file {fp.name}")
            continue
        existing = json.loads(fp.read_text())
        seen = {x["slug"] for x in existing}
        for e in entries:
            if e["slug"] in seen:
                continue
            existing.append(e)
            seen.add(e["slug"])
            added += 1
        fp.write_text(json.dumps(existing, indent=2) + "\n")
    return added, errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: append_catalog.py <new_entries.json>", file=sys.stderr)
        return 2
    data = json.loads(Path(argv[1]).read_text())
    added, errors = append(data, CATALOG_DIR)
    print(f"appended {added} entries")
    for m in errors:
        print(f"  ! {m}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
