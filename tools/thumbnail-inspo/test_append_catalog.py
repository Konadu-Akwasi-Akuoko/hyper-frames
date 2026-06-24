"""Plain-assert tests. Run: python3 tools/thumbnail-inspo/test_append_catalog.py"""
import json
import tempfile
from pathlib import Path

import append_catalog as ap


def _entry(slug, channel="aaron-jack", file="06-x.jpg"):
    return {
        "slug": slug, "channel": channel, "file": file,
        "archetype": "big-text", "layout": "centered-stack", "device": ["big-text"],
        "face": False, "accent": "blue", "text": "low",
        "reads_as": "x", "layout_map": "x", "why_it_works": "x", "mimic_for": "x",
        "watch_url": "https://yt/x", "title": "T", "title_shape": "speed-primer",
        "title_pattern": "concrete-noun-verb",
    }


def test_append_adds_to_channel_file_and_dedups():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "aaron-jack-1.json").write_text(json.dumps([_entry("existing")]))
        added, errors = ap.append([_entry("new-one"), _entry("existing")], catalog)
        assert errors == [], errors
        assert added == 1, added  # "existing" deduped
        slugs = [e["slug"] for e in json.loads((catalog / "aaron-jack-1.json").read_text())]
        assert slugs == ["existing", "new-one"], slugs


def test_append_rejects_bad_enum_and_missing_field():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "aaron-jack-1.json").write_text(json.dumps([]))
        bad_enum = _entry("a"); bad_enum["title_shape"] = "nope"
        missing = _entry("b"); del missing["layout_map"]
        added, errors = ap.append([bad_enum, missing], catalog)
        assert added == 0, added
        assert any("title_shape" in m for m in errors), errors
        assert any("layout_map" in m for m in errors), errors


if __name__ == "__main__":
    test_append_adds_to_channel_file_and_dedups()
    test_append_rejects_bad_enum_and_missing_field()
    print("ok")
