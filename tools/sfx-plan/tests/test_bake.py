"""Tests for the ffmpeg SFX-mix builder (pure, no ffmpeg) + a guarded integration bake."""
from __future__ import annotations

import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path

import pytest

from sfx_plan import bake
from sfx_plan.bake import (
    build_bake_command,
    build_filter_complex,
    equal_power_pan_gains,
    ffmpeg_available,
)
from sfx_plan.errors import FfmpegNotFoundError
from sfx_plan.plan import Cue


def _cue(
    *,
    start: float = 1.0,
    src: str = "A/click.wav",
    volume: float = 0.8,
    pan: float = 0.0,
    cue: str = "ui-tick",
) -> Cue:
    return Cue(
        data_start=start, duration_s=0.4, volume=volume, pan=pan,
        track_index=20, src=src, cue=cue,
        source="index.html:9", clamped=False, at_scene_ms=1234,
    )


def _staged(*srcs: str) -> dict[str, str]:
    return {s: f"assets/sfx/{Path(s).name}" for s in srcs}


def test_equal_power_pan_center_is_root_half() -> None:
    gl, gr = equal_power_pan_gains(0.0)
    assert gl == pytest.approx(math.sqrt(0.5), abs=1e-6)
    assert gr == pytest.approx(math.sqrt(0.5), abs=1e-6)


def test_equal_power_pan_extremes_and_clamp() -> None:
    assert equal_power_pan_gains(-1.0) == pytest.approx((1.0, 0.0), abs=1e-6)
    assert equal_power_pan_gains(1.0) == pytest.approx((0.0, 1.0), abs=1e-6)
    # Out-of-range pans clamp rather than blow up.
    assert equal_power_pan_gains(-5.0) == pytest.approx((1.0, 0.0), abs=1e-6)
    assert equal_power_pan_gains(5.0) == pytest.approx((0.0, 1.0), abs=1e-6)


def test_one_input_per_unique_source_not_per_cue() -> None:
    # Three cues, two unique sources -> exactly two -i inputs.
    cues = [_cue(start=1.0, src="A/click.wav"), _cue(start=2.0, src="A/click.wav"),
            _cue(start=3.0, src="B/boom.wav")]
    staged = _staged("A/click.wav", "B/boom.wav")
    cmd = build_bake_command(
        cues=cues, staged=staged, video_dir=Path("/v"),
        out_rel="audio/sfx-mix.mp3", total_duration_s=60.0,
    )
    assert cmd.count("-i") == 2


def test_repeated_input_is_asplit_per_use() -> None:
    cues = [_cue(start=1.0, src="A/click.wav"), _cue(start=2.0, src="A/click.wav")]
    staged = _staged("A/click.wav")
    fc = build_filter_complex(
        sorted(cues, key=lambda c: c.data_start), staged,
        {staged["A/click.wav"]: 0},
    )
    assert "[0:a]asplit=2[u0_0][u0_1]" in fc


def test_each_cue_delayed_and_volume_scaled() -> None:
    cues = [_cue(start=1.5, volume=0.8), _cue(start=2.0, src="B/boom.wav", volume=0.5)]
    staged = _staged("A/click.wav", "B/boom.wav")
    fc = build_filter_complex(
        sorted(cues, key=lambda c: c.data_start), staged,
        {staged["A/click.wav"]: 0, staged["B/boom.wav"]: 1},
    )
    # data-start 1.5s -> 1500ms, :all=1 so both channels shift.
    assert "adelay=1500:all=1,volume=0.8" in fc
    assert "adelay=2000:all=1,volume=0.5" in fc


def test_amix_is_unity_normalize_zero() -> None:
    cues = [_cue(start=1.0), _cue(start=2.0, src="B/boom.wav")]
    staged = _staged("A/click.wav", "B/boom.wav")
    fc = build_filter_complex(
        sorted(cues, key=lambda c: c.data_start), staged,
        {staged["A/click.wav"]: 0, staged["B/boom.wav"]: 1},
    )
    assert "amix=inputs=2:normalize=0:dropout_transition=0" in fc
    assert "alimiter=limit=0.95" in fc
    assert "apad[mix]" in fc


def test_pan_filter_only_when_nonzero() -> None:
    staged = _staged("A/click.wav", "B/boom.wav")
    no_pan = build_filter_complex(
        [_cue(start=1.0, pan=0.0)], staged, {staged["A/click.wav"]: 0},
    )
    assert "pan=stereo" not in no_pan

    with_pan = build_filter_complex(
        [_cue(start=1.0, src="B/boom.wav", pan=1.0)], staged, {staged["B/boom.wav"]: 0},
    )
    # Hard right -> c0 gain ~0, c1 gain ~1.
    assert "pan=stereo|c0=0.000000*c0|c1=1.000000*c1" in with_pan


def test_command_codec_rate_channels_and_trim() -> None:
    cues = [_cue(start=1.0)]
    staged = _staged("A/click.wav")
    cmd = build_bake_command(
        cues=cues, staged=staged, video_dir=Path("/v"),
        out_rel="audio/sfx-mix.mp3", total_duration_s=42.0,
    )
    joined = " ".join(cmd)
    assert "-ar 48000" in joined
    assert "-ac 2" in joined
    assert "-c:a libmp3lame" in joined
    assert "-b:a 320k" in joined
    assert "-t 42.000000" in joined
    assert cmd[-1] == "/v/audio/sfx-mix.mp3"
    assert "-map" in cmd and cmd[cmd.index("-map") + 1] == "[mix]"


def test_command_wav_uses_pcm() -> None:
    cmd = build_bake_command(
        cues=[_cue(start=1.0)], staged=_staged("A/click.wav"),
        video_dir=Path("/v"), out_rel="audio/sfx-mix.wav",
        total_duration_s=10.0, fmt="wav",
    )
    assert "-c:a" in cmd and cmd[cmd.index("-c:a") + 1] == "pcm_s16le"
    assert "libmp3lame" not in cmd


def test_empty_cues_raises() -> None:
    with pytest.raises(ValueError):
        build_bake_command(
            cues=[], staged={}, video_dir=Path("/v"),
            out_rel="audio/sfx-mix.mp3", total_duration_s=1.0,
        )


def test_bake_without_ffmpeg_raises(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(bake.shutil, "which", lambda _name: None)
    with pytest.raises(FfmpegNotFoundError):
        bake.bake_sfx_mix(
            cues=[_cue(start=1.0)], staged=_staged("A/click.wav"),
            video_dir=tmp_path, out_rel="audio/sfx-mix.mp3", total_duration_s=10.0,
        )


def _write_sine_wav(path: Path, *, seconds: float = 0.2, freq: float = 440.0, rate: int = 48000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for n in range(frames):
            val = int(0.3 * 32767 * math.sin(2 * math.pi * freq * n / rate))
            buf += struct.pack("<hh", val, val)
        w.writeframes(bytes(buf))


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")
def test_integration_bake_produces_full_length_file(tmp_path: Path) -> None:
    video = tmp_path / "video"
    (video / "assets" / "sfx").mkdir(parents=True)
    _write_sine_wav(video / "assets" / "sfx" / "click.wav", freq=440.0)
    _write_sine_wav(video / "assets" / "sfx" / "boom.wav", freq=120.0)
    staged = {"A/click.wav": "assets/sfx/click.wav", "B/boom.wav": "assets/sfx/boom.wav"}
    cues = [
        _cue(start=0.5, src="A/click.wav", pan=-0.5),
        _cue(start=3.0, src="B/boom.wav", volume=0.6),
        _cue(start=4.0, src="A/click.wav"),
    ]
    out = bake.bake_sfx_mix(
        cues=cues, staged=staged, video_dir=video,
        out_rel="audio/sfx-mix.mp3", total_duration_s=6.0,
    )
    assert out.exists() and out.stat().st_size > 0
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(out)],
        capture_output=True, text=True, check=True,
    )
    duration = float(probe.stdout.strip())
    # Padded/trimmed to the full 6.0s mount duration (mp3 frame granularity ~0.05s).
    assert duration == pytest.approx(6.0, abs=0.2)


def test_ffmpeg_available_matches_which() -> None:
    assert ffmpeg_available() == (shutil.which("ffmpeg") is not None)
