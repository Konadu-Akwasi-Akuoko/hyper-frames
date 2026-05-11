"""Tests for the sfx-plan error hierarchy."""
from __future__ import annotations

from sfx_plan.errors import (
    SfxPlanError,
    UnresolvedAnchorError,
    AnchorIndexOutOfRangeError,
    UnknownCueError,
    EmptyCueFilterError,
    CatalogMissingError,
    CatalogVersionMismatchError,
)


def test_all_errors_inherit_from_base() -> None:
    for cls in (
        UnresolvedAnchorError, AnchorIndexOutOfRangeError, UnknownCueError,
        EmptyCueFilterError, CatalogMissingError, CatalogVersionMismatchError,
    ):
        assert issubclass(cls, SfxPlanError)


def test_unresolved_anchor_message_includes_anchor_and_source() -> None:
    err = UnresolvedAnchorError(anchor="Bezier", source="index.html:127")
    assert "Bezier" in str(err)
    assert "index.html:127" in str(err)
    assert "narration-map" in str(err).lower()


def test_anchor_index_out_of_range_lists_available() -> None:
    err = AnchorIndexOutOfRangeError(anchor="easy", requested=3, available=2, source="index.html:45")
    msg = str(err)
    assert "easy" in msg and "3" in msg and "2" in msg


def test_unknown_cue_lists_known_cues() -> None:
    err = UnknownCueError(cue="boom-sub", known=["ui-tick", "whoosh", "boom"], source="index.html:99")
    msg = str(err)
    assert "boom-sub" in msg
    assert "ui-tick" in msg


def test_empty_cue_filter_names_cue() -> None:
    err = EmptyCueFilterError(cue="riser")
    assert "riser" in str(err)
