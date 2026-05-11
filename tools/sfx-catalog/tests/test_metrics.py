"""Tests for sfx_catalog.metrics — audio analysis primitives."""
from __future__ import annotations

import math
from pathlib import Path

from sfx_catalog.metrics import (
    basic_metadata,
    measure_envelope_times,
    measure_lufs,
    measure_peak,
    measure_rms,
)


def test_basic_metadata_reports_duration_and_format(sine_1k_wav: Path) -> None:
    m = basic_metadata(sine_1k_wav)
    assert math.isclose(m["duration_s"], 3.0, rel_tol=0.01)
    assert m["sample_rate"] == 48000
    assert m["channels"] == 1
    assert m["format"] == "wav"
    assert m["bit_depth"] == 24


def test_peak_detection_locates_known_impulse(impulse_wav: Path) -> None:
    peak_dbfs, peak_time_s = measure_peak(impulse_wav)
    assert math.isclose(peak_time_s, 0.083, abs_tol=0.001)
    assert math.isclose(peak_dbfs, -1.94, abs_tol=0.05)


def test_rms_of_sine_at_neg20_dbfs(sine_1k_wav: Path) -> None:
    rms_dbfs = measure_rms(sine_1k_wav)
    assert math.isclose(rms_dbfs, -23.0, abs_tol=0.1)


def test_lufs_of_known_sine(sine_1k_wav: Path) -> None:
    lufs = measure_lufs(sine_1k_wav)
    assert math.isclose(lufs, -23.0, abs_tol=1.0)


def test_envelope_times_on_impulse(impulse_wav: Path) -> None:
    onset, attack, tail = measure_envelope_times(impulse_wav)
    assert math.isclose(onset, 0.083, abs_tol=0.02)
    assert attack < 0.01
    assert tail < 0.05


def test_envelope_times_on_swell(swell_wav: Path) -> None:
    onset, attack, tail = measure_envelope_times(swell_wav)
    assert 0.4 < attack < 0.9
    assert tail > 0.05
