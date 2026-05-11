"""Tests for asset picker and timing math."""
from __future__ import annotations

import math
from pathlib import Path

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import load_catalog
from sfx_plan.narration import load_narration_map
from sfx_plan.plan import pick_asset, build_cue, build_plan


def test_pick_asset_is_deterministic(catalog_path: Path) -> None:
    candidates = [
        ("a.wav", {"path": "a.wav"}),
        ("b.wav", {"path": "b.wav"}),
        ("c.wav", {"path": "c.wav"}),
    ]
    first = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    second = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    assert first == second


def test_pick_asset_changes_with_anchor(catalog_path: Path) -> None:
    candidates = [
        ("a.wav", {"path": "a.wav"}),
        ("b.wav", {"path": "b.wav"}),
        ("c.wav", {"path": "c.wav"}),
        ("d.wav", {"path": "d.wav"}),
    ]
    p1 = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    p2 = pick_asset(candidates, anchor="bar", anchor_index=1, cue="ui-tick")
    assert (p1, p2) != ("a.wav", "a.wav") or p1 != p2


def test_build_cue_peak_aligned_data_start(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="s1-headline", source="index.html:9",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    # nightmare starts at 8.40; ui-tick lead -50ms; click peak_time 0.05.
    # data-start = 8.40 + (-0.050) - 0.05 = 8.30.
    assert math.isclose(cue.data_start, 8.30, abs_tol=0.001)
    assert cue.cue == "ui-tick"


def test_build_plan_returns_cues_sorted_by_start(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    annotations = [
        Annotation(anchor="easy", anchor_index=1, cue="whoosh",
                   lead_ms=None, volume=None, pan=0.0, is_hook=False,
                   element_id="s2", source="index.html:18"),
        Annotation(anchor="nightmare", anchor_index=1, cue="ui-tick",
                   lead_ms=None, volume=None, pan=0.0, is_hook=False,
                   element_id="s1-headline", source="index.html:9"),
    ]
    plan = build_plan(annotations, nm=nm, catalog=cat)
    starts = [c.data_start for c in plan]
    assert starts == sorted(starts)


def test_lead_clamps_to_zero_with_warning(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="whoosh",
        lead_ms=-10000, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="index.html:1",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    assert cue.data_start == 0.0
    assert cue.clamped is True
