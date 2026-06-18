"""Best-effort integration: synth a tiny H.264+PCM master, derive both streams.

Skipped when ffmpeg/ffprobe are not on PATH. Asserts the muted picture has 0
audio + 1 video, the voiceover has 1 audio, and the durations match within a
frame.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys

import pytest

from derive_streams import argv as argvmod

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe not on PATH",
)

DUR = 2.0
FPS = 25
FRAME = 1.0 / FPS


def _probe_counts(path: str) -> tuple[int, int]:
    proc = subprocess.run(
        [
            "ffprobe", "-loglevel", "error",
            "-show_entries", "stream=codec_type", "-of", "json", path,
        ],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(proc.stdout or "{}").get("streams", [])
    v = sum(1 for s in streams if s.get("codec_type") == "video")
    a = sum(1 for s in streams if s.get("codec_type") == "audio")
    return v, a


def _probe_duration(path: str) -> float:
    proc = subprocess.run(
        [
            "ffprobe", "-loglevel", "error",
            "-show_entries", "format=duration", "-of", "json", path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(proc.stdout or "{}")["format"]["duration"])


def test_derive_two_streams(tmp_path):
    master = tmp_path / "master.mov"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"testsrc=size=320x240:rate={FPS}:duration={DUR}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={DUR}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le",
            "-shortest", str(master),
        ],
        check=True,
    )
    assert _probe_counts(str(master)) == (1, 1)

    video_out = tmp_path / "talking-head.mp4"
    audio_out = tmp_path / "voiceover.mp3"
    subprocess.run(
        argvmod.video_argv(str(master), str(video_out)), check=True
    )
    subprocess.run(
        argvmod.audio_argv(str(master), str(audio_out)), check=True
    )

    assert _probe_counts(str(video_out)) == (1, 0)
    v_audio = _probe_counts(str(audio_out))[1]
    assert v_audio == 1

    vdur = _probe_duration(str(video_out))
    adur = _probe_duration(str(audio_out))
    assert abs(vdur - adur) <= FRAME


def _synth_master(path: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i",
            f"testsrc=size=320x240:rate={FPS}:duration={DUR}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={DUR}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", "-shortest", path,
        ],
        check=True,
    )


def _sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def test_muted_picture_is_byte_identical_across_runs(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    out_a = tmp_path / "a.mp4"
    out_b = tmp_path / "b.mp4"
    subprocess.run(argvmod.video_argv(str(master), str(out_a)), check=True)
    subprocess.run(argvmod.video_argv(str(master), str(out_b)), check=True)
    assert _probe_counts(str(out_a)) == (1, 0)
    assert _sha256(str(out_a)) == _sha256(str(out_b))


def test_cli_dry_run_emits_both_argv(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    proc = subprocess.run(
        [
            sys.executable, "-m", "derive_streams.cli", str(master),
            "--video-out", str(tmp_path / "v.mp4"),
            "--audio-out", str(tmp_path / "a.mp3"),
            "--dry-run",
        ],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "-an" in proc.stdout and "libx264" in proc.stdout
    assert "-vn" in proc.stdout and "libmp3lame" in proc.stdout
    assert not (tmp_path / "v.mp4").exists()


def test_cli_rejects_master_missing_a_stream(tmp_path):
    # A video-only master (no audio) must fail the 1v+1a assertion.
    vonly = tmp_path / "vonly.mp4"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i",
            f"testsrc=size=160x120:rate={FPS}:duration=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vonly),
        ],
        check=True,
    )
    proc = subprocess.run(
        [
            sys.executable, "-m", "derive_streams.cli", str(vonly),
            "--video-out", str(tmp_path / "v.mp4"),
            "--audio-out", str(tmp_path / "a.mp3"),
        ],
        capture_output=True, text=True,
    )
    assert proc.returncode != 0
    assert "1 video + 1 audio" in proc.stderr or "1 video + 1 audio" in proc.stdout
