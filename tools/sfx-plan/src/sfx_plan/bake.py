"""Bake every resolved SFX cue into a single mixed audio file via ffmpeg.

The HyperFrames preview player force-loads every mounted `<audio>` element, so a
per-cue `sfx.html` with ~162 elements exhausts Chrome's WebMediaPlayer budget,
evicts the voiceover into `MEDIA_ERR_DECODE`, and freezes preview Play (scrub
still works). Baking mixes every cue — delayed to its `data-start`, scaled by its
volume, optionally panned — into ONE file so the SFX layer mounts a single
`<audio>`.

This is a one-shot FINALIZE step (`sfx-plan --bake`), never the per-cue editing
default: re-baking 530s of mp3 on every annotation tweak would wreck the fast
edit loop. Render is unaffected either way (it muxes audio offline).

Only this module imports `subprocess`/`shutil`; the rest of sfx-plan stays
side-effect-light. The filtergraph is built with one `-i` per UNIQUE staged file
(~7), not one per cue (162) — far below ffmpeg's input/arg limits — then each
unique input is `asplit` into as many taps as cues reference it.
"""
from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from sfx_plan.errors import FfmpegBakeError, FfmpegNotFoundError
from sfx_plan.plan import Cue


def ffmpeg_available() -> bool:
    """True if an `ffmpeg` binary is resolvable on PATH."""
    return shutil.which("ffmpeg") is not None


def equal_power_pan_gains(pan: float) -> tuple[float, float]:
    """Equal-power stereo gains for a pan position in [-1, 1].

    Center (0.0) -> (~0.707, ~0.707); hard left (-1) -> (1.0, ~0.0); hard right
    (+1) -> (~0.0, 1.0). Equal-power keeps perceived loudness constant across the
    pan sweep (constant sum of squares), unlike a linear balance.
    """
    p = max(-1.0, min(1.0, pan))
    angle = (p + 1.0) * (math.pi / 4.0)  # [-1, 1] -> [0, pi/2]
    return (math.cos(angle), math.sin(angle))


def _fmt_seconds(seconds: float) -> str:
    """Deterministic fixed-precision seconds for ffmpeg `-t` / trims."""
    return f"{seconds:.6f}"


def _unique_inputs(ordered: list[Cue], staged: dict[str, str]) -> tuple[list[str], dict[str, int]]:
    """Staged paths in first-seen (data-start) order + a path -> input-index map."""
    unique_paths: list[str] = []
    index_map: dict[str, int] = {}
    for cue in ordered:
        rel = staged[cue.src]
        if rel not in index_map:
            index_map[rel] = len(unique_paths)
            unique_paths.append(rel)
    return unique_paths, index_map


def build_filter_complex(
    ordered: list[Cue],
    staged: dict[str, str],
    index_map: dict[str, int],
) -> str:
    """Assemble the ffmpeg `-filter_complex` string.

    `ordered` must already be sorted by `data_start`. `index_map` maps each staged
    relative path to its ffmpeg input index. Cues sharing one input are fanned out
    with `asplit`; each cue is delayed (`adelay=...:all=1` so BOTH channels shift),
    volume-scaled, optionally panned, then summed with `amix` at unity
    (`normalize=0`, else amix divides by N), limited, and `apad`-extended (the
    caller's `-t` then trims to the full mount duration).
    """
    use_counts: dict[int, int] = {}
    for cue in ordered:
        idx = index_map[staged[cue.src]]
        use_counts[idx] = use_counts.get(idx, 0) + 1

    parts: list[str] = []
    taps: dict[int, list[str]] = {}
    for idx in sorted(use_counts):
        count = use_counts[idx]
        if count <= 1:
            taps[idx] = [f"{idx}:a"]
        else:
            labels = [f"u{idx}_{k}" for k in range(count)]
            parts.append(f"[{idx}:a]asplit={count}" + "".join(f"[{label}]" for label in labels))
            taps[idx] = labels

    ptr: dict[int, int] = {}
    cue_labels: list[str] = []
    for j, cue in enumerate(ordered):
        idx = index_map[staged[cue.src]]
        tap = taps[idx][ptr.get(idx, 0)]
        ptr[idx] = ptr.get(idx, 0) + 1
        delay_ms = round(cue.data_start * 1000)
        chain = f"[{tap}]adelay={delay_ms}:all=1,volume={cue.volume}"
        if cue.pan != 0.0:
            gain_l, gain_r = equal_power_pan_gains(cue.pan)
            chain += f",pan=stereo|c0={gain_l:.6f}*c0|c1={gain_r:.6f}*c1"
        out = f"a{j}"
        chain += f"[{out}]"
        parts.append(chain)
        cue_labels.append(out)

    mix_inputs = "".join(f"[{label}]" for label in cue_labels)
    parts.append(
        f"{mix_inputs}amix=inputs={len(cue_labels)}:normalize=0:dropout_transition=0,"
        f"alimiter=limit=0.95,apad[mix]"
    )
    return ";".join(parts)


def build_bake_command(
    *,
    cues: list[Cue],
    staged: dict[str, str],
    video_dir: Path,
    out_rel: str,
    total_duration_s: float,
    fmt: str = "mp3",
) -> list[str]:
    """Full ffmpeg argv to bake `cues` into `video_dir / out_rel`.

    Raises ValueError on empty `cues`. `-t total_duration_s` trims the
    `apad`-extended mix to the full mount duration so late silence is preserved
    and nothing is clipped.
    """
    if not cues:
        raise ValueError("no cues to bake")

    ordered = sorted(cues, key=lambda c: c.data_start)
    unique_paths, index_map = _unique_inputs(ordered, staged)
    filter_complex = build_filter_complex(ordered, staged, index_map)

    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
    for rel in unique_paths:
        cmd += ["-i", str(video_dir / rel)]
    cmd += ["-filter_complex", filter_complex, "-map", "[mix]", "-ar", "48000", "-ac", "2"]
    if fmt == "wav":
        cmd += ["-c:a", "pcm_s16le"]
    else:
        cmd += ["-c:a", "libmp3lame", "-b:a", "320k"]
    cmd += ["-t", _fmt_seconds(total_duration_s), str(video_dir / out_rel)]
    return cmd


def bake_sfx_mix(
    *,
    cues: list[Cue],
    staged: dict[str, str],
    video_dir: Path,
    out_rel: str,
    total_duration_s: float,
    fmt: str = "mp3",
) -> Path:
    """Run ffmpeg to produce the single mixed SFX file. Returns its path.

    Raises FfmpegNotFoundError if ffmpeg is absent and FfmpegBakeError (wrapping
    the stderr tail) if the mux fails.
    """
    if not ffmpeg_available():
        raise FfmpegNotFoundError()
    out_path = video_dir / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_bake_command(
        cues=cues,
        staged=staged,
        video_dir=video_dir,
        out_rel=out_rel,
        total_duration_s=total_duration_s,
        fmt=fmt,
    )
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        tail = "\n".join((exc.stderr or "").strip().splitlines()[-5:])
        raise FfmpegBakeError(stderr_tail=tail) from exc
    return out_path
