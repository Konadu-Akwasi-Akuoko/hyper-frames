"""Probe is advisory-only: it reports VO loudness + classification, no volume rec.

SFX volume is a fixed 0.4 hard peg in tools/sfx-plan, so sfx-level no longer
recommends a duck level — it only tells you whether a cue lands in a gap or over
a spoken word.
"""
from __future__ import annotations

import numpy as np

from sfx_level.cli import SAMPLE_RATE, FloorRef, probe


def test_probe_reports_classification_without_volume_recommendation() -> None:
    pcm = np.zeros(SAMPLE_RATE, dtype=np.float32)  # one second of silence — a gap
    ref = FloorRef(pcm, SAMPLE_RATE)
    result = probe(pcm, ref, 0.5, 120.0)
    assert result["classification"] in ("gap", "active-speech")
    assert "rms_dbfs" in result and "peak_dbfs" in result
    # Volume is pegged at 0.4 in sfx-plan; sfx-level recommends no level.
    assert "recommended_volume" not in result
