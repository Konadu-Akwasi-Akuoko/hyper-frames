"""Plain-assert tests for backfill_titles. Run: python3 tools/thumbnail-inspo/test_backfill_titles.py"""
import json
import tempfile
from pathlib import Path

import backfill_titles as bt


def test_inject_titles_joins_by_channel_and_file():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        catalog = root / "catalog"
        catalog.mkdir()
        lib = root / "lib"
        (lib / "fireship").mkdir(parents=True)

        (lib / "fireship" / "_manifest.json").write_text(json.dumps({
            "slug": "fireship",
            "items": [{"file": "06-U3aXWizDbQ4.jpg", "title": "C in 100 Seconds"}],
        }))
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06-U3aXWizDbQ4.jpg"},
        ]))

        updated = bt.inject_titles(catalog, lib)
        assert updated == 1, updated

        entry = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert entry["title"] == "C in 100 Seconds", entry

        # idempotent: a second run updates nothing
        assert bt.inject_titles(catalog, lib) == 0


def test_inject_titles_skips_unmatched_file():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        catalog = root / "catalog"
        catalog.mkdir()
        lib = root / "lib"
        (lib / "fireship").mkdir(parents=True)
        (lib / "fireship" / "_manifest.json").write_text(json.dumps({
            "slug": "fireship", "items": [{"file": "99-other.jpg", "title": "X"}],
        }))
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06-U3aXWizDbQ4.jpg"},
        ]))
        assert bt.inject_titles(catalog, lib) == 0
        entry = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert "title" not in entry


if __name__ == "__main__":
    test_inject_titles_joins_by_channel_and_file()
    test_inject_titles_skips_unmatched_file()
    print("ok")
