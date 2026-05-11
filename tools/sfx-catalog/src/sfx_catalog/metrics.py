"""Per-asset audio analysis: peak, LUFS, spectral, onset/attack/tail."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pyloudnorm as pyln
import soundfile as sf

_SUBTYPE_BIT_DEPTH: dict[str, int | None] = {
    "PCM_S8": 8, "PCM_16": 16, "PCM_24": 24, "PCM_32": 32,
    "PCM_U8": 8, "FLOAT": None, "DOUBLE": None,
    "ALAW": None, "ULAW": None,
}


def basic_metadata(path: Path) -> dict[str, Any]:
    """Return {duration_s, sample_rate, channels, format, bit_depth} for `path`.

    Uses soundfile.info() for wav (cheap header read). For mp3, soundfile lacks
    header-only access on some platforms — fall back to loading samples via
    soundfile.read() if needed.
    """
    suffix = path.suffix.lower().lstrip(".")
    try:
        info = sf.info(path)
        duration_s = info.duration
        sample_rate = info.samplerate
        channels = info.channels
        bit_depth = _SUBTYPE_BIT_DEPTH.get(info.subtype)
    except RuntimeError:
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        duration_s = data.shape[0] / sr
        sample_rate = sr
        channels = data.shape[1]
        bit_depth = None
    return {
        "duration_s": float(duration_s),
        "sample_rate": int(sample_rate),
        "channels": int(channels),
        "format": suffix,
        "bit_depth": bit_depth,
    }


def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    """Load audio as float32 mono, downmixing if needed."""
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    mono = data.mean(axis=1)
    return mono, int(sr)


def measure_peak(path: Path) -> tuple[float, float]:
    """Return (peak_dbfs, peak_time_s) — the absolute peak and its time."""
    mono, sr = _load_mono(path)
    if mono.size == 0:
        return -math.inf, 0.0
    peak_idx = int(np.argmax(np.abs(mono)))
    peak_sample = float(abs(mono[peak_idx]))
    peak_dbfs = 20.0 * math.log10(max(peak_sample, 1e-9))
    peak_time_s = peak_idx / sr
    return peak_dbfs, peak_time_s


def measure_rms(path: Path) -> float:
    """Return integrated RMS in dBFS over the whole file (mono-summed)."""
    mono, _sr = _load_mono(path)
    if mono.size == 0:
        return -math.inf
    rms = float(np.sqrt(np.mean(np.square(mono))))
    return 20.0 * math.log10(max(rms, 1e-9))


def measure_lufs(path: Path) -> float:
    """Integrated loudness in LUFS (EBU R128) of the whole file.

    Returns -inf for clips shorter than ~400ms (BS.1770 gating window).
    """
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    if data.shape[0] < int(0.4 * sr):
        return -math.inf
    audio = data[:, 0] if data.shape[1] == 1 else data
    meter = pyln.Meter(sr)
    return float(meter.integrated_loudness(audio))
