#!/usr/bin/env python3
"""Inject each catalog entry's real YouTube title from the per-channel manifest.

Deterministic, idempotent join: for every entry in tools/thumbnail-inspo/catalog/*.json,
look up thumbnailInspo/<channel>/_manifest.json and copy the matching item's `title`
(keyed by `file`). fetch.py already harvests the title into the manifest, so this
never touches the network. Re-run any time the catalog changes.

Usage:
    python3 tools/thumbnail-inspo/backfill_titles.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = Path(__file__).resolve().parent / "catalog"
LIB_DIR = ROOT / "thumbnailInspo"


def _manifest_titles(lib_dir: Path, channel: str) -> dict[str, str]:
    man = lib_dir / channel / "_manifest.json"
    if not man.exists():
        return {}
    data = json.loads(man.read_text())
    return {i["file"]: i.get("title", "") for i in data.get("items", []) if i.get("file")}


def inject_titles(catalog_dir: Path, lib_dir: Path) -> int:
    updated = 0
    cache: dict[str, dict[str, str]] = {}
    for fp in sorted(catalog_dir.glob("*.json")):
        entries = json.loads(fp.read_text())
        if not isinstance(entries, list):
            continue
        changed = False
        for e in entries:
            ch, fn = e.get("channel"), e.get("file")
            if not ch or not fn:
                continue
            titles = cache.setdefault(ch, _manifest_titles(lib_dir, ch))
            title = titles.get(fn)
            if title and e.get("title") != title:
                e["title"] = title
                updated += 1
                changed = True
        if changed:
            fp.write_text(json.dumps(entries, indent=2) + "\n")
    return updated


def main() -> int:
    n = inject_titles(CATALOG_DIR, LIB_DIR)
    print(f"injected/updated {n} titles across catalog entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
