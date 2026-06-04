"""Catalog data shapes."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


Brightness = str  # one of: "dark", "warm", "bright", "airy"
AutoRole = str    # one of: "transition", "accent", "impact", "riser", "ambience", "foley"


@dataclass(frozen=True)
class CatalogEntry:
    """One audio asset's full metadata, as stored under `assets:` in sfx-catalog.yml."""

    path: str
    library: str
    category: str
    duration_s: float
    sample_rate: int
    channels: int
    format: str
    bit_depth: int | None
    sha256: str
    peak_dbfs: float
    peak_time_s: float
    integrated_lufs: float
    rms_dbfs: float
    onset_time_s: float
    attack_time_s: float
    tail_time_s: float
    spectral_centroid_hz: float
    brightness: Brightness
    low_energy_pct: int
    mid_energy_pct: int
    high_energy_pct: int
    tags: tuple[str, ...]
    auto_role: AutoRole

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(self.tags)
        return d


@dataclass(frozen=True)
class CueRecipe:
    """Named cue, with a filter applied against catalog entries to find candidates.

    `align` chooses the timing reference the SFX lands on: "onset" (punctuation
    cues — the audible transient lands on the visual impact frame, never early)
    or "peak" (anticipatory cues like whoosh/riser — the swell leads in and the
    peak lands on arrival). `default_asset` pins the one handpicked file the cue
    reuses across the whole video (its signature sound); the filter is only a
    fallback when no asset is pinned.
    """

    name: str
    default_lead_ms: int | None
    default_volume: float
    align: str = "onset"
    default_asset: str | None = None
    filter: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "filter": dict(self.filter),
            "align": self.align,
            "default_asset": self.default_asset,
            "default_lead_ms": self.default_lead_ms,
            "default_volume": self.default_volume,
        }


@dataclass(frozen=True)
class Catalog:
    """Top-level catalog: metadata + assets + cues."""

    version: int
    generated_at: str
    library_sha: str
    assets: dict[str, CatalogEntry]
    cues: dict[str, CueRecipe]
