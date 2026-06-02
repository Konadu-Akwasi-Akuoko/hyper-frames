"""Signal-processing helpers: decode audio, RMS envelope, plateau-edge search.

All functions are deterministic (no randomness, no global state) so cut-snap
produces identical output for identical input — a hard requirement for the
render-safe pipeline.
"""

from __future__ import annotations

import subprocess

import numpy as np
import numpy.typing as npt


def decode_pcm(path: str, sample_rate: int) -> npt.NDArray[np.float32]:
    """Decode an audio file to mono float32 PCM in [-1, 1] via ffmpeg.

    Decodes the whole file once; windows are then indexed by sample offset.
    """
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


def plateau_edge(
    x: npt.NDArray[np.float32],
    sample_rate: int,
    lo_t: float,
    hi_t: float,
    anchor_t: float,
    direction: str,
    floor_db: float,
    frame_ms: float,
    hop_ms: float,
    sustain_ms: float,
) -> float | None:
    """Find the silence-plateau edge between two words.

    Scans the RMS envelope of `x[lo_t:hi_t]` for the boundary between the
    low-energy floor (room tone) and speech, calibrating the threshold
    `floor + floor_db` relative to the quietest frame in the window.

    - direction "forward"  (cut.start): first sustained sub-threshold frame at
      or after `anchor_t` — i.e. where the preceding kept word has decayed.
    - direction "backward" (cut.end): last sustained sub-threshold frame at or
      before `anchor_t` — i.e. just before the next kept word rises.

    Returns the edge time in seconds, or None if the window has no detectable
    floor (e.g. words run together with no real silence).
    """
    lo_s, hi_s = int(lo_t * sample_rate), int(hi_t * sample_rate)
    seg = x[max(lo_s, 0):hi_s]
    frame = max(int(frame_ms / 1000 * sample_rate), 1)
    hop = max(int(hop_ms / 1000 * sample_rate), 1)
    rms, centers = rms_envelope(seg, frame, hop)
    if rms.size == 0:
        return None

    floor = float(rms.min())
    thr = floor * (10.0 ** (floor_db / 20.0)) + 1e-4
    below = rms < thr
    if not below.any():
        return None

    sustain = max(int(sustain_ms / hop_ms), 1)
    times = (lo_s + centers) / sample_rate
    anchor_idx = int(np.searchsorted(times, anchor_t))

    def sustained(i: int) -> bool:
        return bool(below[i:i + sustain].all()) and i + sustain <= below.size

    if direction == "forward":
        for i in range(max(anchor_idx, 0), below.size):
            if sustained(i):
                return float(times[i])
        return None
    # backward
    for i in range(min(anchor_idx, below.size - 1), -1, -1):
        if i - sustain + 1 >= 0 and below[i - sustain + 1:i + 1].all():
            return float(times[i])
    return None


def nearest_zero_crossing(
    x: npt.NDArray[np.float32], sample_rate: int, t: float, window_ms: float
) -> float:
    """Snap `t` to the nearest zero-crossing within +/- window_ms (de-click)."""
    idx = int(t * sample_rate)
    w = max(int(window_ms / 1000 * sample_rate), 1)
    lo, hi = max(idx - w, 1), min(idx + w, x.size - 1)
    if lo >= hi:
        return t
    seg = x[lo - 1:hi]
    crossings = np.where(np.signbit(seg[:-1]) != np.signbit(seg[1:]))[0]
    if crossings.size == 0:
        return t
    cross_idx = lo + crossings
    nearest = cross_idx[np.argmin(np.abs(cross_idx - idx))]
    return float(nearest) / sample_rate
