"""Tests for asset picker and timing math."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import load_catalog
from sfx_plan.errors import UnknownAssetError, UnknownMountError
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


def test_pinned_asset_bypasses_picker(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="index.html:9",
        asset="Whooshes/whoosh-mid-01.wav",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    assert cue.src == "Whooshes/whoosh-mid-01.wav"


def test_pinned_asset_still_uses_cue_defaults(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="index.html:9",
        asset="Whooshes/whoosh-mid-01.wav",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    # ui-tick default volume is 0.8, track index is 20
    assert cue.volume == 0.8
    assert cue.track_index == 20


def test_pinned_asset_not_in_catalog_raises(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="index.html:9",
        asset="No/Such/File.wav",
    )
    with pytest.raises(UnknownAssetError):
        build_cue(ann, nm=nm, catalog=cat)


def test_at_scene_ms_adds_mount_offset(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 10.0}
    ann = Annotation(
        anchor=None, anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="compositions/scene-01-open.html:42",
        at_scene_ms=2500,
    )
    cue = build_cue(ann, nm=nm, catalog=cat, mount_offsets=mount_offsets)
    # offset 10.0 + 2.5 - peak_time_s(0.05) + lead 0 = 12.45
    assert math.isclose(cue.data_start, 12.45, abs_tol=0.001)
    assert cue.at_scene_ms == 2500


def test_at_scene_ms_defaults_lead_to_zero(video_dir: Path, catalog_path: Path) -> None:
    """The cue's default_lead_ms must NOT be applied to at-scene-ms cues."""
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 0.0}
    ann = Annotation(
        anchor=None, anchor_index=1, cue="ui-tick",  # default_lead_ms=-50
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="compositions/scene-01-open.html:42",
        at_scene_ms=1000,
    )
    cue = build_cue(ann, nm=nm, catalog=cat, mount_offsets=mount_offsets)
    # 0 + 1.0 - peak_time_s(0.05) + lead 0 = 0.95 (NOT 0.90 from default lead)
    assert math.isclose(cue.data_start, 0.95, abs_tol=0.001)


def test_at_scene_ms_explicit_lead_is_respected(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 0.0}
    ann = Annotation(
        anchor=None, anchor_index=1, cue="ui-tick",
        lead_ms=-30, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="compositions/scene-01-open.html:42",
        at_scene_ms=1000,
    )
    cue = build_cue(ann, nm=nm, catalog=cat, mount_offsets=mount_offsets)
    # 0 + 1.0 + (-0.03) - 0.05 = 0.92
    assert math.isclose(cue.data_start, 0.92, abs_tol=0.001)


def test_at_scene_ms_unknown_mount_raises(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor=None, anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="compositions/missing.html:1",
        at_scene_ms=1000,
    )
    with pytest.raises(UnknownMountError):
        build_cue(ann, nm=nm, catalog=cat, mount_offsets={})
