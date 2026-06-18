"""Best-effort integration: synth a tiny H.264+PCM master, derive both streams.

Skipped when ffmpeg/ffprobe are not on PATH. Asserts the muted picture has 0
audio + 1 video, the voiceover has 1 audio, and the durations match within a
frame.
"""

from __future__ import annotations

import json
import shutil
import subprocess

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
