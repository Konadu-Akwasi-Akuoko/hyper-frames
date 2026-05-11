"""Tests for sfx_catalog.tagging — auto tag and auto_role derivation."""
from __future__ import annotations

from sfx_catalog.tagging import derive_tags, derive_auto_role


def test_tags_include_folder_lineage() -> None:
    tags = derive_tags(
        rel_path="Mister Horse Free SFX/Click/click-bright-01.wav",
        duration_s=0.4,
        attack_time_s=0.04,
        brightness="bright",
    )
    assert "click" in tags
    assert "mister-horse" in tags
    assert "bright" in tags
    assert "short" in tags


def test_tags_include_snappy_for_fast_attack() -> None:
    tags = derive_tags(
        rel_path="Whooshes/snap.wav",
        duration_s=0.2,
        attack_time_s=0.01,
        brightness="bright",
    )
    assert "snappy" in tags


def test_auto_role_transition_for_whoosh_swell() -> None:
    role = derive_auto_role(
        category="Whooshes",
        duration_s=0.8,
        attack_time_s=0.2,
        low_energy_pct=20,
        peak_time_s=0.5,
    )
    assert role == "transition"


def test_auto_role_impact_for_short_bass_hit() -> None:
    role = derive_auto_role(
        category="Bass",
        duration_s=0.4,
        attack_time_s=0.05,
        low_energy_pct=70,
        peak_time_s=0.1,
    )
    assert role == "impact"


def test_auto_role_accent_for_short_click() -> None:
    role = derive_auto_role(
        category="Click",
        duration_s=0.3,
        attack_time_s=0.02,
        low_energy_pct=10,
        peak_time_s=0.05,
    )
    assert role == "accent"


def test_auto_role_riser_for_long_swell() -> None:
    role = derive_auto_role(
        category="Drone",
        duration_s=2.5,
        attack_time_s=1.8,
        low_energy_pct=40,
        peak_time_s=2.0,
    )
    assert role == "riser"


def test_auto_role_ambience_for_long_low_energy() -> None:
    role = derive_auto_role(
        category="Drone",
        duration_s=8.0,
        attack_time_s=0.2,
        low_energy_pct=60,
        peak_time_s=4.0,
    )
    assert role == "ambience"
