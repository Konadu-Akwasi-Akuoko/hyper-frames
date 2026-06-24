"""Plain-assert tests. Run: python3 tools/thumbnail-inspo/test_apply_classifications.py"""
import json
import tempfile
from pathlib import Path

import apply_classifications as ac


def test_apply_writes_fields_by_slug():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06.jpg", "title": "C in 100 Seconds"},
        ]))
        applied, errors = ac.apply(
            [{"slug": "fireship-c", "title_shape": "speed-primer",
              "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 1, applied
        assert errors == [], errors
        e = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert e["title_shape"] == "speed-primer"
        assert e["title_pattern"] == "concrete-noun-verb"


def test_apply_rejects_unknown_enum_value():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "x.json").write_text(json.dumps([{"slug": "a", "channel": "c", "file": "1.jpg"}]))
        applied, errors = ac.apply(
            [{"slug": "a", "title_shape": "made-up", "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 0, applied
        assert any("made-up" in msg for msg in errors), errors


def test_apply_reports_missing_slug():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "x.json").write_text(json.dumps([{"slug": "a", "channel": "c", "file": "1.jpg"}]))
        applied, errors = ac.apply(
            [{"slug": "ghost", "title_shape": "speed-primer", "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 0
        assert any("ghost" in msg for msg in errors), errors


if __name__ == "__main__":
    test_apply_writes_fields_by_slug()
    test_apply_rejects_unknown_enum_value()
    test_apply_reports_missing_slug()
    print("ok")
