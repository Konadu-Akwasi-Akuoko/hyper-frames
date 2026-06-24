"""Plan-building: asset picking + timing math.

Every cue is triggered by a *visual* moment (`data-sfx-at-scene-ms`, scene-local
ms of the element's impact frame). There is no spoken-word path. Cues are
independent and element-bound: a cue is placed solely because its own visual
event warrants a sound — never suppressed, delayed, or merged because of any
neighbouring cue.
"""
from __future__ import annotations

import dataclasses
import difflib
import hashlib
from dataclasses import dataclass
from typing import Any

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import filter_assets, get_cue
from sfx_plan.errors import UnknownAssetError, UnknownMountError


# A small late bias (ms) applied to onset-aligned (punctuation) cues so the
# transient lands ON — never before — the visual impact frame. Audio leading
# video is perceived as wrong far sooner than audio lagging (EBU R37, ITU-R
# BT.1359, ATSC all tolerate lag >> lead), so a few ms late is free insurance.
SYNC_BIAS_MS = 12

# Punctuation cues land their audible ONSET on the impact frame; anticipatory
# cues (whoosh, riser) land their PEAK there so the swell leads in. A cue's
# recipe sets `align`; default is onset.
_DEFAULT_ALIGN = "onset"

# Cue lanes start here. build_plan lane-packs concurrent cues onto distinct
# track-indices (they layer in playback either way — distinct lanes only keep
# the editing timeline tidy and mean the overlap note never trips).
_TRACK_BASE = 20

# Every SFX cue plays at this fixed gain — a hard peg, identical "no matter the
# sfx." It is applied uniformly in `build_cue`, so the catalog's per-cue
# `default_volume` and any `data-sfx-volume` override no longer affect loudness;
# SFX level is uniform by design. The baked layer then mounts at unity
# (`data-volume="1"` in emit.py), so each cue's 0.4 gain is the net level.
PEG_VOLUME = 0.4


@dataclass(frozen=True)
class Cue:
    """One scheduled audio event, ready to emit as an HTML <audio> tag."""

    data_start: float
    duration_s: float
    volume: float
    pan: float
    track_index: int
    src: str
    cue: str
    source: str
    clamped: bool
    at_scene_ms: int
    lead_ms: int = 0
    # Seconds the cue's audible onset precedes its impact frame (>0 only for
    # peak-aligned cues; ≤0 for onset-aligned ones). Used for the per-cue
    # pre-roll note in validate.py — never for suppression.
    preroll_s: float = 0.0


def pick_asset(
    candidates: list[tuple[str, dict[str, Any]]],
    *,
    cue: str,
    at_scene_ms: int,
    source: str,
) -> str:
    """Deterministic fallback pick when a cue pins no asset and has no default.

    Seeded by cue + scene-ms + source so the choice is reproducible. The curated
    catalog pins a `default_asset` per cue, so this is only a safety net.
    """
    seed = f"{cue}|{at_scene_ms}|{source}".encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    idx = int.from_bytes(digest[:8], "big") % len(candidates)
    return candidates[idx][0]


def _comp_path_from_source(source: str) -> str:
    """Strip the ':<line>' suffix off Annotation.source."""
    return source.rsplit(":", 1)[0]


def _nearest_assets(asset_path: str, assets: dict[str, Any]) -> list[str]:
    basename = asset_path.rsplit("/", 1)[-1].lower()
    near = difflib.get_close_matches(
        basename,
        [p.rsplit("/", 1)[-1].lower() for p in assets.keys()],
        n=5,
        cutoff=0.5,
    )
    return [p for p in assets.keys() if p.rsplit("/", 1)[-1].lower() in near][:5]


def _require_asset(asset_path: str, *, source: str, assets: dict[str, Any]) -> str:
    """Return `asset_path` if it exists in the catalog, else raise with near-matches."""
    if asset_path in assets:
        return asset_path
    raise UnknownAssetError(asset=asset_path, source=source, near=_nearest_assets(asset_path, assets))


def _resolve_mount_offset(
    ann: Annotation,
    mount_offsets: dict[str, float],
) -> float:
    """Return the global offset for an at-scene-ms annotation's host composition."""
    comp_path = _comp_path_from_source(ann.source)
    if comp_path == "index.html":
        return 0.0
    if comp_path in mount_offsets:
        return mount_offsets[comp_path]
    raise UnknownMountError(
        comp_path=comp_path,
        source=ann.source,
        known_mounts=list(mount_offsets.keys()),
    )


def build_cue(
    ann: Annotation,
    *,
    catalog: dict[str, Any],
    mount_offsets: dict[str, float] | None = None,
) -> Cue:
    """Resolve a single annotation into a fully scheduled Cue.

    Asset resolution order: (1) the element's `data-sfx-asset` pin, (2) the cue
    recipe's `default_asset`, (3) the filter pool + deterministic hash fallback.
    """
    recipe = get_cue(catalog, name=ann.cue, source=ann.source)
    assets = catalog.get("assets", {})

    if ann.asset is not None:
        asset_path = _require_asset(ann.asset, source=ann.source, assets=assets)
    elif recipe.get("default_asset"):
        asset_path = _require_asset(
            recipe["default_asset"], source=f"catalog:cue:{ann.cue}", assets=assets
        )
    else:
        candidates = filter_assets(catalog, cue_name=ann.cue)
        asset_path = pick_asset(
            candidates, cue=ann.cue, at_scene_ms=ann.at_scene_ms, source=ann.source
        )
    asset = assets[asset_path]

    offsets = mount_offsets or {}
    t_ref = _resolve_mount_offset(ann, offsets) + (ann.at_scene_ms / 1000.0)
    lead_ms = ann.lead_ms if ann.lead_ms is not None else 0

    onset_s = float(asset.get("onset_time_s") or 0.0)
    align = recipe.get("align") or _DEFAULT_ALIGN
    if align == "peak":
        # Anticipatory cue: land the PEAK on the impact frame; the swell leads in.
        raw_start = t_ref + (lead_ms / 1000.0) - float(asset["peak_time_s"])
    else:
        # Punctuation cue: land the audible ONSET on the impact frame, biased a
        # hair late so it is never early.
        raw_start = t_ref + ((lead_ms + SYNC_BIAS_MS) / 1000.0) - onset_s

    clamped = raw_start < 0.0
    data_start = max(raw_start, 0.0)
    # How far the audible onset sits before the impact frame (peak cues only).
    preroll_s = t_ref - (raw_start + onset_s)

    # Hard peg: every cue at the same fixed level, regardless of the catalog's
    # `default_volume` or a `data-sfx-volume` override. See PEG_VOLUME.
    volume = PEG_VOLUME

    return Cue(
        data_start=round(data_start, 4),
        duration_s=float(asset["duration_s"]),
        volume=volume,
        pan=ann.pan,
        track_index=_TRACK_BASE,  # reassigned by lane-packing in build_plan
        src=asset_path,
        cue=ann.cue,
        source=ann.source,
        clamped=clamped,
        at_scene_ms=ann.at_scene_ms,
        lead_ms=lead_ms,
        preroll_s=round(preroll_s, 4),
    )


def _assign_lanes(cues: list[Cue]) -> list[Cue]:
    """Lane-pack cues so no two clips on one track-index overlap in time.

    Concurrent cues layer fine in playback; distinct lanes only keep the editing
    timeline legible and mean the overlap note never trips. Cues are never
    dropped, delayed, or merged here — only their track-index is chosen.
    """
    lane_ends: list[float] = []
    out: list[Cue] = []
    for c in cues:
        lane = next((i for i, end in enumerate(lane_ends) if c.data_start >= end), None)
        if lane is None:
            lane = len(lane_ends)
            lane_ends.append(0.0)
        lane_ends[lane] = c.data_start + c.duration_s
        out.append(dataclasses.replace(c, track_index=_TRACK_BASE + lane))
    return out


def build_plan(
    annotations: list[Annotation],
    *,
    catalog: dict[str, Any],
    mount_offsets: dict[str, float] | None = None,
) -> list[Cue]:
    """Resolve every annotation, sort by data_start, lane-pack, return the plan."""
    cues = [build_cue(a, catalog=catalog, mount_offsets=mount_offsets) for a in annotations]
    cues.sort(key=lambda c: c.data_start)
    return _assign_lanes(cues)
