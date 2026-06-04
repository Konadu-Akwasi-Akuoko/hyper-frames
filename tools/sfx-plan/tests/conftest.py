"""Fixtures: a miniature video folder and catalog.

SFX are triggered only by visual moments (`data-sfx-at-scene-ms`); there is no
spoken-word/anchor path, so the fixtures carry no narration-map.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
import yaml


@pytest.fixture
def video_dir(tmp_path: Path) -> Path:
    """A pretend video folder with an annotated index.html (at-scene-ms cues)."""
    root = tmp_path / "videos" / "demo-2026-05-11"
    root.mkdir(parents=True)
    (root / "compositions").mkdir()
    (root / "audio").mkdir()

    (root / "index.html").write_text(
        dedent('''\
        <!doctype html>
        <html>
        <body>
          <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="1920" data-height="1080">
            <audio id="vo" data-start="0" data-duration="60" data-track-index="9" src="audio/vo.mp3"></audio>

            <div id="s1" class="scene">
              <h1 id="s1-headline"
                  data-sfx-on-anchor="ui-tick"
                  data-sfx-at-scene-ms="8400">A mathematical nightmare.</h1>
            </div>

            <div id="s2" class="scene"
                 data-sfx-on-anchor="whoosh"
                 data-sfx-at-scene-ms="22000">
              <h1 id="s2-title"
                  data-sfx-on-anchor="ui-tick"
                  data-sfx-at-scene-ms="22000">Easy.</h1>
            </div>
          </div>
        </body>
        </html>
        '''),
        encoding="utf-8",
    )
    return root


@pytest.fixture
def catalog_path(tmp_path: Path) -> Path:
    """A tiny sfx-catalog.yml with two assets and a handful of cues.

    Cues exercise both alignment modes (ui-tick=onset, whoosh=peak) and the
    `default_asset` short-circuit (snap pins an asset and has a no-match filter).
    """
    p = tmp_path / "sound-effects" / "sfx-catalog.yml"
    p.parent.mkdir(parents=True)
    (p.parent / "Mister Horse" / "Click").mkdir(parents=True)
    (p.parent / "Whooshes").mkdir(parents=True)
    (p.parent / "Mister Horse" / "Click" / "click-bright-01.wav").write_bytes(b"\x00")
    (p.parent / "Whooshes" / "whoosh-mid-01.wav").write_bytes(b"\x00")

    data = {
        "version": 1,
        "generated_at": "2026-05-11T00:00:00Z",
        "library_sha": "test",
        "assets": {
            "Mister Horse/Click/click-bright-01.wav": {
                "library": "Mister Horse", "category": "Click",
                "duration_s": 0.30, "sample_rate": 48000, "channels": 2,
                "format": "wav", "bit_depth": 24, "sha256": "a" * 64,
                "peak_dbfs": -2.0, "peak_time_s": 0.05,
                "integrated_lufs": -14.0, "rms_dbfs": -18.0,
                "onset_time_s": 0.01, "attack_time_s": 0.04, "tail_time_s": 0.20,
                "spectral_centroid_hz": 5000.0, "brightness": "bright",
                "low_energy_pct": 5, "mid_energy_pct": 30, "high_energy_pct": 65,
                "tags": ["click", "ui", "bright"], "auto_role": "accent",
            },
            "Whooshes/whoosh-mid-01.wav": {
                "library": "Whooshes", "category": "Whooshes",
                "duration_s": 0.80, "sample_rate": 48000, "channels": 2,
                "format": "wav", "bit_depth": 24, "sha256": "b" * 64,
                "peak_dbfs": -1.5, "peak_time_s": 0.40,
                "integrated_lufs": -16.0, "rms_dbfs": -20.0,
                "onset_time_s": 0.05, "attack_time_s": 0.35, "tail_time_s": 0.30,
                "spectral_centroid_hz": 2500.0, "brightness": "warm",
                "low_energy_pct": 20, "mid_energy_pct": 50, "high_energy_pct": 30,
                "tags": ["whoosh", "warm"], "auto_role": "transition",
            },
        },
        "cues": {
            "ui-tick": {"filter": {"auto_role": "accent", "duration_s_max": 0.5,
                                    "brightness_in": ["bright", "airy"]},
                       "align": "onset", "default_lead_ms": -50, "default_volume": 0.8},
            "whoosh":  {"filter": {"auto_role": "transition", "duration_s_min": 0.4,
                                    "duration_s_max": 1.5, "attack_time_s_min": 0.1},
                       "align": "peak", "default_lead_ms": 0, "default_volume": 0.9},
            "boom":    {"filter": {"auto_role": "impact", "low_energy_pct_min": 50,
                                    "peak_time_s_max": 0.2},
                       "align": "onset", "default_lead_ms": 0, "default_volume": 1.0},
            "riser":   {"filter": {"auto_role": "riser", "duration_s_min": 1.5},
                       "align": "peak", "default_lead_ms": 0, "default_volume": 0.85},
            "pop":     {"filter": {"auto_role": "accent", "duration_s_max": 0.3,
                                    "brightness_in": ["warm", "bright"]},
                       "align": "onset", "default_lead_ms": 0, "default_volume": 0.8},
            "snap":    {"filter": {"auto_role": "no-such-role"},
                       "default_asset": "Mister Horse/Click/click-bright-01.wav",
                       "align": "onset", "default_lead_ms": 0, "default_volume": 0.7},
        },
    }
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return p
