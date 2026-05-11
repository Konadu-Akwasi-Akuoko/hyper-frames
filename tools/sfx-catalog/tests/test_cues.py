"""Tests for default cue recipes."""
from __future__ import annotations

from sfx_catalog.cues import default_cues


def test_default_cues_includes_required_set() -> None:
    cues = default_cues()
    names = set(cues.keys())
    assert names == {"ui-tick", "whoosh", "boom", "riser", "pop"}


def test_ui_tick_filter_prefers_short_bright_accents() -> None:
    cue = default_cues()["ui-tick"]
    assert cue.filter.get("auto_role") == "accent"
    assert cue.filter.get("duration_s_max") == 0.5
    assert "bright" in cue.filter.get("brightness_in", [])
    assert cue.default_lead_ms == -50


def test_whoosh_filter_targets_transitions() -> None:
    cue = default_cues()["whoosh"]
    assert cue.filter.get("auto_role") == "transition"
    assert cue.default_lead_ms == -150
