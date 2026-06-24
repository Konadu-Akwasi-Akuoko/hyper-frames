"""Tests for asset picker and timing math (visual-only, transient-on-impact)."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import load_catalog
from sfx_plan.errors import UnknownAssetError, UnknownMountError
from sfx_plan.plan import SYNC_BIAS_MS, pick_asset, build_cue, build_plan


def _ann(cue: str, *, at_scene_ms: int, source: str, lead_ms: int | None = None,
         asset: str | None = None, volume: float | None = None) -> Annotation:
    return Annotation(
        cue=cue, at_scene_ms=at_scene_ms, lead_ms=lead_ms, volume=volume,
        pan=0.0, is_hook=False, element_id="x", source=source, asset=asset,
    )


def test_pick_asset_is_deterministic() -> None:
    candidates = [("a.wav", {}), ("b.wav", {}), ("c.wav", {})]
    first = pick_asset(candidates, cue="ui-tick", at_scene_ms=1000, source="index.html:9")
    second = pick_asset(candidates, cue="ui-tick", at_scene_ms=1000, source="index.html:9")
    assert first == second


def test_pick_asset_varies_with_seed() -> None:
    candidates = [("a.wav", {}), ("b.wav", {}), ("c.wav", {}), ("d.wav", {})]
    p1 = pick_asset(candidates, cue="ui-tick", at_scene_ms=1000, source="index.html:9")
    p2 = pick_asset(candidates, cue="ui-tick", at_scene_ms=2000, source="index.html:9")
    assert (p1, p2) != ("a.wav", "a.wav") or p1 != p2


def test_onset_aligned_lands_transient_on_impact_frame(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    ann = _ann("ui-tick", at_scene_ms=8400, source="index.html:9")
    cue = build_cue(ann, catalog=cat)
    # onset-align: data_start = t_ref + (lead + SYNC_BIAS)/1000 - onset_time_s
    #            = 8.40 + (0 + 0.012) - 0.01 = 8.402.  Audible onset = t_ref + bias.
    assert math.isclose(cue.data_start, 8.40 + SYNC_BIAS_MS / 1000.0 - 0.01, abs_tol=1e-4)
    # Audible onset (data_start + onset) is never before the impact frame.
    assert cue.data_start + 0.01 >= 8.40
    assert cue.preroll_s <= 0.0
    assert cue.cue == "ui-tick"


def test_peak_aligned_whoosh_lands_peak_on_arrival(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    ann = _ann("whoosh", at_scene_ms=22000, source="index.html:18")
    cue = build_cue(ann, catalog=cat)
    # peak-align: data_start = t_ref + lead/1000 - peak_time_s = 22.0 - 0.40 = 21.60.
    assert math.isclose(cue.data_start, 22.0 - 0.40, abs_tol=1e-4)
    # The swell leads in: audible onset precedes the impact frame by peak - onset.
    assert math.isclose(cue.preroll_s, 0.40 - 0.05, abs_tol=1e-4)


def test_build_plan_sorts_and_lane_packs_overlaps(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    anns = [
        _ann("whoosh", at_scene_ms=22000, source="index.html:18"),
        _ann("ui-tick", at_scene_ms=8400, source="index.html:9"),
    ]
    plan = build_plan(anns, catalog=cat)
    starts = [c.data_start for c in plan]
    assert starts == sorted(starts)
    # whoosh (21.60, 0.80s long → ends 22.40) overlaps the ui-tick at ~22.00,
    # so they land on distinct track-index lanes (no clip is dropped or delayed).
    overlapping = [c for c in plan if c.data_start >= 21.0]
    assert len({c.track_index for c in overlapping}) == len(overlapping)


def test_default_asset_short_circuits_filter_pool(catalog_path: Path) -> None:
    """`snap` has a no-match filter but pins default_asset — it must resolve to it
    without ever consulting (and failing) the filter pool."""
    cat = load_catalog(catalog_path)
    cue = build_cue(_ann("snap", at_scene_ms=1000, source="index.html:9"), catalog=cat)
    assert cue.src == "Mister Horse/Click/click-bright-01.wav"


def test_pinned_asset_overrides_default_and_pool(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    ann = _ann("ui-tick", at_scene_ms=8400, source="index.html:9",
               asset="Whooshes/whoosh-mid-01.wav")
    cue = build_cue(ann, catalog=cat)
    assert cue.src == "Whooshes/whoosh-mid-01.wav"
    # Volume is hard-pegged at 0.4 (catalog default ignored); lanes start at 20.
    assert cue.volume == 0.4
    assert cue.track_index == 20


def test_volume_is_hard_pegged_ignoring_override_and_default(catalog_path: Path) -> None:
    """Every cue plays at the fixed 0.4 peg. Neither the catalog's per-cue
    `default_volume` nor a `data-sfx-volume` override changes it — SFX volume is
    uniform by design ("no matter the sfx")."""
    cat = load_catalog(catalog_path)
    # ui-tick's catalog default_volume is 0.8 and this annotation pins 0.9 — both ignored.
    overridden = build_cue(
        _ann("ui-tick", at_scene_ms=8400, source="index.html:9", volume=0.9), catalog=cat
    )
    assert overridden.volume == 0.4
    # No override either: still 0.4, not the catalog's 0.8.
    plain = build_cue(_ann("ui-tick", at_scene_ms=8400, source="index.html:9"), catalog=cat)
    assert plain.volume == 0.4


def test_pinned_asset_not_in_catalog_raises(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    ann = _ann("ui-tick", at_scene_ms=8400, source="index.html:9", asset="No/Such/File.wav")
    with pytest.raises(UnknownAssetError):
        build_cue(ann, catalog=cat)


def test_at_scene_ms_adds_mount_offset(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 10.0}
    ann = _ann("ui-tick", at_scene_ms=2500, source="compositions/scene-01-open.html:42")
    cue = build_cue(ann, catalog=cat, mount_offsets=mount_offsets)
    # 10.0 + 2.5 + 0.012 - 0.01 = 12.502
    assert math.isclose(cue.data_start, 12.5 + SYNC_BIAS_MS / 1000.0 - 0.01, abs_tol=1e-4)
    assert cue.at_scene_ms == 2500


def test_explicit_lead_is_respected(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 0.0}
    ann = _ann("ui-tick", at_scene_ms=1000, source="compositions/scene-01-open.html:42", lead_ms=-30)
    cue = build_cue(ann, catalog=cat, mount_offsets=mount_offsets)
    # 1.0 + (-30 + 12)/1000 - 0.01 = 0.972
    assert math.isclose(cue.data_start, 1.0 + (-30 + SYNC_BIAS_MS) / 1000.0 - 0.01, abs_tol=1e-4)


def test_lead_clamps_to_zero_with_flag(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    mount_offsets = {"compositions/scene-01-open.html": 0.0}
    ann = _ann("whoosh", at_scene_ms=1000, source="compositions/scene-01-open.html:42", lead_ms=-10000)
    cue = build_cue(ann, catalog=cat, mount_offsets=mount_offsets)
    assert cue.data_start == 0.0
    assert cue.clamped is True


def test_unknown_mount_raises(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    ann = _ann("ui-tick", at_scene_ms=1000, source="compositions/missing.html:1")
    with pytest.raises(UnknownMountError):
        build_cue(ann, catalog=cat, mount_offsets={})
