"""Tests for the index.html mount-offset reader."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from sfx_plan.mounts import load_mount_offsets


def _index(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "index.html"
    p.write_text(f"<html><body>{body}</body></html>", encoding="utf-8")
    return p


def test_parses_data_start_per_mount(tmp_path: Path) -> None:
    p = _index(tmp_path, dedent("""\
        <div data-composition-src="compositions/scene-01-open.html" data-start="0"></div>
        <div data-composition-src="compositions/scene-02-subversion.html" data-start="13.64"></div>
    """))
    offsets = load_mount_offsets(p)
    assert offsets == {
        "compositions/scene-01-open.html": 0.0,
        "compositions/scene-02-subversion.html": 13.64,
    }


def test_elements_without_composition_src_are_skipped(tmp_path: Path) -> None:
    p = _index(tmp_path, dedent("""\
        <div id="vo" data-start="0"></div>
        <div data-composition-src="compositions/scene-01-open.html" data-start="1.5"></div>
    """))
    offsets = load_mount_offsets(p)
    assert offsets == {"compositions/scene-01-open.html": 1.5}


def test_non_numeric_data_start_raises(tmp_path: Path) -> None:
    p = _index(tmp_path, '<div data-composition-src="x.html" data-start="abc"></div>')
    with pytest.raises(ValueError):
        load_mount_offsets(p)


def test_missing_data_start_defaults_to_zero(tmp_path: Path) -> None:
    p = _index(tmp_path, '<div data-composition-src="x.html"></div>')
    assert load_mount_offsets(p) == {"x.html": 0.0}
