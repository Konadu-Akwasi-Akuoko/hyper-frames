"""Synthetic-WAV fixtures for sfx-catalog tests."""
from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pytest
import soundfile as sf

SR = 48000


def _write_wav(path: Path, samples: np.ndarray, sr: int = SR) -> Path:
    sf.write(path, samples.astype(np.float32), sr, subtype="PCM_24")
    return path


@pytest.fixture
def impulse_wav(tmp_path: Path) -> Path:
    """0.5s of silence with a single +0.8 spike at t=0.083s."""
    n = int(0.5 * SR)
    samples = np.zeros(n, dtype=np.float32)
    spike_idx = int(0.083 * SR)
    samples[spike_idx] = 0.8
    return _write_wav(tmp_path / "impulse.wav", samples)


@pytest.fixture
def sine_1k_wav(tmp_path: Path) -> Path:
    """3s of 1kHz sine at -20 dBFS peak, mono."""
    duration_s = 3.0
    t = np.arange(int(duration_s * SR)) / SR
    samples = 0.1 * np.sin(2 * math.pi * 1000 * t)
    return _write_wav(tmp_path / "sine_1k.wav", samples)


@pytest.fixture
def sine_4k_wav(tmp_path: Path) -> Path:
    """3s of 4kHz sine at -20 dBFS peak."""
    duration_s = 3.0
    t = np.arange(int(duration_s * SR)) / SR
    samples = 0.1 * np.sin(2 * math.pi * 4000 * t)
    return _write_wav(tmp_path / "sine_4k.wav", samples)


@pytest.fixture
def swell_wav(tmp_path: Path) -> Path:
    """1s tone with a slow attack — peaks at t=0.7s. Used for attack-time tests."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    envelope = np.minimum(t / 0.7, 1.0) * np.exp(-3.0 * np.maximum(t - 0.7, 0))
    samples = (0.6 * envelope * np.sin(2 * math.pi * 800 * t)).astype(np.float32)
    return _write_wav(tmp_path / "swell.wav", samples)


@pytest.fixture
def library_dir(tmp_path: Path, impulse_wav, sine_1k_wav, swell_wav) -> Path:
    """A miniature sound-effects/ tree with three categorized files."""
    root = tmp_path / "lib"
    (root / "Whooshes").mkdir(parents=True)
    (root / "Mister Horse / Click").mkdir(parents=True)
    (root / "Mister Horse / Click" / "click-01.wav").write_bytes(impulse_wav.read_bytes())
    (root / "Whooshes" / "swell-01.wav").write_bytes(swell_wav.read_bytes())
    (root / "Whooshes" / "tone-01.wav").write_bytes(sine_1k_wav.read_bytes())
    return root
