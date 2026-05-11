"""Tests for sfx_catalog.metrics — audio analysis primitives."""
from __future__ import annotations

import math
from pathlib import Path

from sfx_catalog.metrics import basic_metadata


def test_basic_metadata_reports_duration_and_format(sine_1k_wav: Path) -> None:
    m = basic_metadata(sine_1k_wav)
    assert math.isclose(m["duration_s"], 3.0, rel_tol=0.01)
    assert m["sample_rate"] == 48000
    assert m["channels"] == 1
    assert m["format"] == "wav"
    assert m["bit_depth"] == 24
