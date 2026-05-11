"""Tests for narration-map loading and anchor resolution."""
from __future__ import annotations

from pathlib import Path

import pytest

from sfx_plan.errors import UnresolvedAnchorError, AnchorIndexOutOfRangeError
from sfx_plan.narration import load_narration_map, resolve_anchor


def test_load_returns_map_keyed_by_normalized_phrase(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    assert "nightmare" in nm
    assert "easy" in nm


def test_resolve_anchor_returns_correct_start_time(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    start = resolve_anchor(nm, anchor="nightmare", index=1, source="x:1")
    assert start == 8.40


def test_resolve_is_case_and_whitespace_insensitive(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    assert resolve_anchor(nm, anchor="  Nightmare  ", index=1, source="x:1") == 8.40


def test_unresolved_anchor_raises(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    with pytest.raises(UnresolvedAnchorError):
        resolve_anchor(nm, anchor="Bezier", index=1, source="index.html:127")


def test_anchor_index_out_of_range_raises(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    with pytest.raises(AnchorIndexOutOfRangeError) as exc_info:
        resolve_anchor(nm, anchor="easy", index=3, source="index.html:45")
    assert exc_info.value.available == 1
