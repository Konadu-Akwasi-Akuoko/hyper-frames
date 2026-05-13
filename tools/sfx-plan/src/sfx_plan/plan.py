"""Plan-building: asset picking + timing math."""
from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from typing import Any

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import filter_assets, get_cue
from sfx_plan.errors import UnknownAssetError, UnknownMountError
from sfx_plan.narration import resolve_anchor


_TRACK_BY_CUE: dict[str, int] = {
    "ui-tick": 20,
    "whoosh":  21,
    "boom":    22,
    "riser":   23,
    "pop":     24,
}
_DEFAULT_TRACK = 29


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
    anchor: str | None
    anchor_index: int
    source: str
    clamped: bool
    at_scene_ms: int | None = None
    lead_ms: int = 0


def pick_asset(
    candidates: list[tuple[str, dict[str, Any]]],
    *,
    anchor: str,
    anchor_index: int,
    cue: str,
) -> str:
    """Pick one asset path deterministically from the candidate list."""
    seed = f"{anchor.lower()}|{anchor_index}|{cue}".encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    idx = int.from_bytes(digest[:8], "big") % len(candidates)
    return candidates[idx][0]


def _comp_path_from_source(source: str) -> str:
    """Strip the ':<line>' suffix off Annotation.source."""
    return source.rsplit(":", 1)[0]


def _validate_pinned_asset(
    ann: Annotation,
    catalog: dict[str, Any],
) -> str:
    """Return the pinned asset path if it exists in the catalog, else raise."""
    assert ann.asset is not None
    assets = catalog.get("assets", {})
    if ann.asset in assets:
        return ann.asset
    basename = ann.asset.rsplit("/", 1)[-1].lower()
    near = difflib.get_close_matches(
        basename,
        [p.rsplit("/", 1)[-1].lower() for p in assets.keys()],
        n=5,
        cutoff=0.5,
    )
    near_paths = [p for p in assets.keys() if p.rsplit("/", 1)[-1].lower() in near][:5]
    raise UnknownAssetError(asset=ann.asset, source=ann.source, near=near_paths)


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
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
    mount_offsets: dict[str, float] | None = None,
) -> Cue:
    """Resolve a single annotation into a fully scheduled Cue."""
    recipe = get_cue(catalog, name=ann.cue, source=ann.source)

    if ann.asset is not None:
        asset_path = _validate_pinned_asset(ann, catalog)
    else:
        candidates = filter_assets(catalog, cue_name=ann.cue)
        asset_path = pick_asset(
            candidates,
            anchor=ann.anchor or "",
            anchor_index=ann.anchor_index,
            cue=ann.cue,
        )
    asset = catalog["assets"][asset_path]

    if ann.at_scene_ms is not None:
        offsets = mount_offsets or {}
        t_ref = _resolve_mount_offset(ann, offsets) + (ann.at_scene_ms / 1000.0)
        lead_ms = ann.lead_ms if ann.lead_ms is not None else 0
    else:
        assert ann.anchor is not None  # enforced at scan time
        t_ref = resolve_anchor(nm, anchor=ann.anchor, index=ann.anchor_index, source=ann.source)
        if ann.lead_ms is not None:
            lead_ms = ann.lead_ms
        elif recipe.get("default_lead_ms") is not None:
            lead_ms = recipe["default_lead_ms"]
        else:
            lead_ms = -int(asset["duration_s"] * 1000)

    raw_start = t_ref + (lead_ms / 1000.0) - float(asset["peak_time_s"])
    clamped = raw_start < 0.0
    data_start = max(raw_start, 0.0)

    volume = ann.volume if ann.volume is not None else float(recipe.get("default_volume", 1.0))

    return Cue(
        data_start=round(data_start, 4),
        duration_s=float(asset["duration_s"]),
        volume=volume,
        pan=ann.pan,
        track_index=_TRACK_BY_CUE.get(ann.cue, _DEFAULT_TRACK),
        src=asset_path,
        cue=ann.cue,
        anchor=ann.anchor,
        anchor_index=ann.anchor_index,
        source=ann.source,
        clamped=clamped,
        at_scene_ms=ann.at_scene_ms,
        lead_ms=lead_ms,
    )


def build_plan(
    annotations: list[Annotation],
    *,
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
    mount_offsets: dict[str, float] | None = None,
) -> list[Cue]:
    """Resolve every annotation, sort by data_start, return the timed plan."""
    cues = [
        build_cue(a, nm=nm, catalog=catalog, mount_offsets=mount_offsets)
        for a in annotations
    ]
    cues.sort(key=lambda c: c.data_start)
    return cues
