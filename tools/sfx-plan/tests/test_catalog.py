"""Tests for catalog loading + filter engine."""
from __future__ import annotations

from pathlib import Path

import pytest

from sfx_plan.catalog import load_catalog, filter_assets, get_cue
from sfx_plan.errors import (
    CatalogMissingError,
    CatalogVersionMismatchError,
    UnknownCueError,
    EmptyCueFilterError,
)


def test_load_returns_dict_with_assets_and_cues(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    assert cat["version"] == 1
    assert "Mister Horse/Click/click-bright-01.wav" in cat["assets"]
    assert "ui-tick" in cat["cues"]


def test_missing_catalog_raises(tmp_path: Path) -> None:
    with pytest.raises(CatalogMissingError):
        load_catalog(tmp_path / "missing.yml")


def test_version_mismatch_raises(tmp_path: Path) -> None:
    p = tmp_path / "future.yml"
    p.write_text("version: 99\ngenerated_at: x\nlibrary_sha: y\nassets: {}\ncues: {}\n")
    with pytest.raises(CatalogVersionMismatchError):
        load_catalog(p)


def test_get_cue_returns_recipe(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    cue = get_cue(cat, name="ui-tick", source="x:1")
    assert cue["default_lead_ms"] == -50


def test_get_cue_unknown_raises(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    with pytest.raises(UnknownCueError):
        get_cue(cat, name="boom-sub", source="x:1")


def test_filter_assets_applies_filter_operators(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    matches = filter_assets(cat, cue_name="ui-tick")
    paths = [p for p, _ in matches]
    assert "Mister Horse/Click/click-bright-01.wav" in paths
    assert "Whooshes/whoosh-mid-01.wav" not in paths


def test_filter_assets_empty_match_raises(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    with pytest.raises(EmptyCueFilterError):
        filter_assets(cat, cue_name="boom")
