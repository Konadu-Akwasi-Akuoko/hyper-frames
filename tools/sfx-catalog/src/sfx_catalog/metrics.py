"""Per-asset audio analysis: peak, LUFS, spectral, onset/attack/tail."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
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
