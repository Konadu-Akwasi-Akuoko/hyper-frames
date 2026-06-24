"""Tests for default cue recipes (curated, video-first palette)."""
from __future__ import annotations

from sfx_catalog.cues import default_cues


def test_default_cues_includes_core_palette() -> None:
    names = set(default_cues().keys())
    # Core motion-graphics vocabulary plus the snap cue.
    assert {"ui-tick", "whoosh", "boom", "riser", "pop", "msg-ding", "snap"} <= names


def test_every_cue_pins_a_default_asset_and_align() -> None:
    for name, cue in default_cues().items():
        assert cue.default_asset, f"{name} must pin a default_asset"
        assert cue.align in ("onset", "peak"), f"{name} align must be onset|peak"
        # 0.4 is the fixed house level; sfx-plan hard-pegs every cue's volume there.
        assert cue.default_volume == 0.4
        assert cue.default_lead_ms == 0


def test_punctuation_cues_are_onset_aligned() -> None:
    cues = default_cues()
    for name in ("ui-tick", "pop", "msg-ding", "boom", "snap", "card-tap"):
        assert cues[name].align == "onset", f"{name} should be onset-aligned"


def test_anticipatory_cues_are_peak_aligned() -> None:
    cues = default_cues()
    assert cues["whoosh"].align == "peak"
    assert cues["riser"].align == "peak"
    assert cues["whoosh"].filter.get("auto_role") == "transition"
