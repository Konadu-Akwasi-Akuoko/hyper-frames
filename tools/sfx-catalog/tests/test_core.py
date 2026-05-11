"""Tests for sfx_catalog.core dataclasses."""
from __future__ import annotations

from sfx_catalog.core import CatalogEntry, CueRecipe, Catalog


def test_catalog_entry_roundtrips_to_dict():
    entry = CatalogEntry(
        path="Whooshes/swell-01.wav",
        library="Whooshes",
        category="Whooshes",
        duration_s=1.0,
        sample_rate=48000,
        channels=1,
        format="wav",
        bit_depth=24,
        sha256="abc",
        peak_dbfs=-4.4,
        peak_time_s=0.7,
        integrated_lufs=-18.2,
        rms_dbfs=-22.0,
        onset_time_s=0.0,
        attack_time_s=0.7,
        tail_time_s=0.25,
        spectral_centroid_hz=820.0,
        brightness="dark",
        low_energy_pct=70,
        mid_energy_pct=25,
        high_energy_pct=5,
        tags=("whoosh", "swell"),
        auto_role="transition",
    )
    d = entry.to_dict()
    assert d["path"] == "Whooshes/swell-01.wav"
    assert d["tags"] == ["whoosh", "swell"]
    assert d["auto_role"] == "transition"


def test_cue_recipe_filter_defaults_to_empty():
    cue = CueRecipe(name="boom", default_lead_ms=0, default_volume=1.0)
    assert cue.filter == {}


def test_catalog_holds_entries_keyed_by_path():
    entry = CatalogEntry(
        path="x.wav", library="X", category="X", duration_s=0.1,
        sample_rate=48000, channels=1, format="wav", bit_depth=24,
        sha256="z", peak_dbfs=-1.0, peak_time_s=0.05,
        integrated_lufs=-14.0, rms_dbfs=-18.0,
        onset_time_s=0.0, attack_time_s=0.05, tail_time_s=0.05,
        spectral_centroid_hz=3000.0, brightness="bright",
        low_energy_pct=10, mid_energy_pct=40, high_energy_pct=50,
        tags=(), auto_role="accent",
    )
    cat = Catalog(version=1, generated_at="2026-05-11T00:00:00Z",
                  library_sha="lib-sha", assets={"x.wav": entry}, cues={})
    assert cat.assets["x.wav"].path == "x.wav"
