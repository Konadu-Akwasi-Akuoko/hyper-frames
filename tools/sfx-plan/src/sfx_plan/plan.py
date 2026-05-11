"""Plan-building: asset picking + timing math."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import filter_assets, get_cue
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
    anchor: str
    anchor_index: int
    source: str
    clamped: bool


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


def build_cue(
    ann: Annotation,
    *,
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
) -> Cue:
    """Resolve a single annotation into a fully scheduled Cue."""
    recipe = get_cue(catalog, name=ann.cue, source=ann.source)
    candidates = filter_assets(catalog, cue_name=ann.cue)
    asset_path = pick_asset(
        candidates, anchor=ann.anchor, anchor_index=ann.anchor_index, cue=ann.cue,
    )
    asset = catalog["assets"][asset_path]

    t_anchor = resolve_anchor(nm, anchor=ann.anchor, index=ann.anchor_index, source=ann.source)

    if ann.lead_ms is not None:
        lead_ms = ann.lead_ms
    elif recipe.get("default_lead_ms") is not None:
        lead_ms = recipe["default_lead_ms"]
    else:
        lead_ms = -int(asset["duration_s"] * 1000)

    raw_start = t_anchor + (lead_ms / 1000.0) - float(asset["peak_time_s"])
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
    )


def build_plan(
    annotations: list[Annotation],
    *,
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
) -> list[Cue]:
    """Resolve every annotation, sort by data_start, return the timed plan."""
    cues = [build_cue(a, nm=nm, catalog=catalog) for a in annotations]
    cues.sort(key=lambda c: c.data_start)
    return cues
