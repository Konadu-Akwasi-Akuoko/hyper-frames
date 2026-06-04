"""Signal-processing helpers: decode audio, RMS envelope, dBFS levels.

`decode_pcm` and `rms_envelope` are lifted verbatim from `tools/cut-snap`'s
`dsp.py` so the two tools measure loudness identically — the same numpy
short-time RMS, no librosa/pyloudnorm stack. All functions are deterministic.
"""

from __future__ import annotations

import math
import subprocess

import numpy as np
import numpy.typing as npt


def decode_pcm(path: str, sample_rate: int) -> npt.NDArray[np.float32]:
    """Decode an audio file to mono float32 PCM in [-1, 1] via ffmpeg."""
    proc = subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error",
            "-i", path,
            "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-",
        ],
        capture_output=True,
        check=True,
    )
    pcm = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32)
    return pcm / 32768.0


def rms_envelope(
    seg: npt.NDArray[np.float32], frame: int, hop: int
) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.int64]]:
    """Short-time RMS of `seg`. Returns (rms_per_frame, frame_center_sample)."""
    if seg.size < frame:
        return np.empty(0, np.float32), np.empty(0, np.int64)
    windows = np.lib.stride_tricks.sliding_window_view(seg, frame)[::hop]
    rms = np.sqrt(np.mean(windows.astype(np.float64) ** 2, axis=1)).astype(np.float32)
    centers = np.arange(rms.size, dtype=np.int64) * hop + frame // 2
    return rms, centers


def db(amplitude: float) -> float:
    """Linear amplitude (0..1) to dBFS, floored at -120 dB to avoid -inf."""
    if amplitude <= 1e-12:
        return -120.0
    return 20.0 * math.log10(amplitude)


def window_levels(
    pcm: npt.NDArray[np.float32], sample_rate: int, t: float, window_ms: float
) -> tuple[float, float]:
    """RMS dBFS and peak dBFS of the [t-window, t+window] slice of `pcm`."""
    half = window_ms / 1000.0
    lo = max(int((t - half) * sample_rate), 0)
    hi = min(int((t + half) * sample_rate), pcm.size)
    seg = pcm[lo:hi]
    if seg.size == 0:
        return -120.0, -120.0
    rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2)))
    peak = float(np.max(np.abs(seg)))
    return db(rms), db(peak)
