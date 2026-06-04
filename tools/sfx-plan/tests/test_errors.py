"""Tests for the sfx-plan error hierarchy."""
from __future__ import annotations

from sfx_plan.errors import (
    SfxPlanError,
    MissingTimeReferenceError,
    UnknownCueError,
    EmptyCueFilterError,
    CatalogMissingError,
    CatalogVersionMismatchError,
)


def test_all_errors_inherit_from_base() -> None:
    for cls in (
        MissingTimeReferenceError, UnknownCueError,
        EmptyCueFilterError, CatalogMissingError, CatalogVersionMismatchError,
    ):
        assert issubclass(cls, SfxPlanError)


def test_missing_time_reference_points_at_at_scene_ms() -> None:
    err = MissingTimeReferenceError(source="index.html:127")
    msg = str(err)
    assert "index.html:127" in msg
    assert "data-sfx-at-scene-ms" in msg


def test_unknown_cue_lists_known_cues() -> None:
    err = UnknownCueError(cue="boom-sub", known=["ui-tick", "whoosh", "boom"], source="index.html:99")
    msg = str(err)
    assert "boom-sub" in msg
    assert "ui-tick" in msg


def test_empty_cue_filter_names_cue() -> None:
    err = EmptyCueFilterError(cue="riser")
    assert "riser" in str(err)
