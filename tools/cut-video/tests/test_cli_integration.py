"""End-to-end CLI integration: synth a tiny clip, cut it, assert determinism.

Skipped when ffmpeg/ffprobe are not on PATH. Exercises the real subprocess
path — extract-audio, video mode, audio mode, --dry-run — and the hard
determinism guarantee (two cut runs are byte-identical).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe not on PATH",
)

DUR = 4.0
FPS = 25


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


def _sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


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


def _cli(*cli_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cut_video.cli", *cli_args],
        capture_output=True, text=True,
    )


def _write_cuts(path: str, cuts: list[tuple[float, float]]) -> None:
    payload = {"version": 1, "cuts": [{"start": s, "end": e} for s, e in cuts]}
    with open(path, "w") as fh:
        json.dump(payload, fh)


def test_dry_run_prints_filtergraph_and_runs_no_ffmpeg(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(1.0, 2.0)])

    out = tmp_path / "out.mp4"
    proc = _cli(str(cuts), str(master), "-o", str(out), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert "concat=n=2:v=1:a=1[v][a]" in proc.stdout
    assert "[0:v]trim=start=0.000000:end=1.000000" in proc.stdout
    assert not out.exists()


def test_video_cut_is_byte_identical_across_runs(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(1.0, 2.0)])

    out_a = tmp_path / "a.mp4"
    out_b = tmp_path / "b.mp4"
    pa = _cli(str(cuts), str(master), "-o", str(out_a))
    pb = _cli(str(cuts), str(master), "-o", str(out_b))
    assert pa.returncode == 0, pa.stderr
    assert pb.returncode == 0, pb.stderr

    assert _probe_counts(str(out_a)) == (1, 1)
    # 4s source minus a 1s cut -> ~3s master.
    assert abs(_probe_duration(str(out_a)) - 3.0) < 0.2
    assert _sha256(str(out_a)) == _sha256(str(out_b))


def test_audio_mode_cut(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(1.0, 2.0)])

    out = tmp_path / "voice.mp3"
    proc = _cli(str(cuts), str(master), "-o", str(out), "--mode", "audio")
    assert proc.returncode == 0, proc.stderr
    assert _probe_counts(str(out)) == (0, 1)


def test_extract_audio_subcommand(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    out = tmp_path / "raw.mp3"
    proc = _cli(
        "extract-audio", str(master), "-o", str(out),
        "--mono", "--ar", "16000",
    )
    assert proc.returncode == 0, proc.stderr
    assert _probe_counts(str(out)) == (0, 1)


def test_whole_duration_removed_fails_loud(tmp_path):
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(0.0, DUR)])

    out = tmp_path / "out.mp4"
    proc = _cli(str(cuts), str(master), "-o", str(out), "--dry-run")
    assert proc.returncode != 0
    assert "error" in proc.stderr.lower()
    assert not out.exists()


def test_error_prefix_is_not_doubled(tmp_path):
    # main() owns the single "cut-video: error:" prefix; raised exceptions must
    # not embed their own, or the message reads "cut-video: error: cut-video:".
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    with open(cuts, "w") as fh:
        json.dump({"version": 99, "cuts": []}, fh)

    out = tmp_path / "out.mp4"
    proc = _cli(str(cuts), str(master), "-o", str(out))
    assert proc.returncode != 0
    assert "cut-video: error: cut-video:" not in proc.stderr
    assert "unsupported cuts.json version" in proc.stderr


def test_extract_audio_on_video_only_source_fails_loud(tmp_path):
    vonly = tmp_path / "vonly.mp4"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"testsrc=size=160x120:rate={FPS}:duration=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vonly),
        ],
        check=True,
    )
    out = tmp_path / "none.mp3"
    proc = _cli("extract-audio", str(vonly), "-o", str(out))
    assert proc.returncode != 0
    assert "no audio stream" in proc.stderr
    assert "cut-video: error: cut-video:" not in proc.stderr
    assert not out.exists()


def test_two_audio_stream_master_fails_loud_in_video_mode(tmp_path):
    # The talking-head invariant: a 1v+2a master must be rejected, not silently
    # mapped to one audio track.
    master = tmp_path / "two_audio.mov"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"testsrc=size=160x120:rate={FPS}:duration=2",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            "-f", "lavfi", "-i", "sine=frequency=880:duration=2",
            "-map", "0:v", "-map", "1:a", "-map", "2:a",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-shortest", str(master),
        ],
        check=True,
    )
    assert _probe_counts(str(master)) == (1, 2)
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(0.5, 1.0)])
    out = tmp_path / "out.mp4"
    proc = _cli(str(cuts), str(master), "-o", str(out), "--dry-run")
    assert proc.returncode != 0
    assert "1 video / 2 audio" in proc.stderr
    assert not out.exists()


def test_audio_only_source_infers_audio_mode(tmp_path):
    # No --mode flag: an audio-only source must infer audio mode and emit 0v/1a.
    raw = tmp_path / "raw.mp3"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={DUR}",
            "-c:a", "libmp3lame", str(raw),
        ],
        check=True,
    )
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(1.0, 1.5)])
    out = tmp_path / "voice.mp3"
    proc = _cli(str(cuts), str(raw), "-o", str(out))
    assert proc.returncode == 0, proc.stderr
    assert "mode audio" in proc.stdout
    assert _probe_counts(str(out)) == (0, 1)


def test_many_tiny_cuts_is_byte_identical(tmp_path):
    # Several sub-second cuts must still produce a byte-identical re-encode.
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(
        str(cuts), [(0.5, 0.6), (1.2, 1.35), (2.0, 2.1), (3.0, 3.05)]
    )
    out_a = tmp_path / "a.mp4"
    out_b = tmp_path / "b.mp4"
    pa = _cli(str(cuts), str(master), "-o", str(out_a))
    pb = _cli(str(cuts), str(master), "-o", str(out_b))
    assert pa.returncode == 0, pa.stderr
    assert pb.returncode == 0, pb.stderr
    assert _sha256(str(out_a)) == _sha256(str(out_b))


def test_video_and_audio_cut_share_same_keep_windows(tmp_path):
    # The whole point: picture and audio cut on identical absolute timestamps.
    master = tmp_path / "master.mov"
    _synth_master(str(master))
    cuts = tmp_path / "cuts.json"
    _write_cuts(str(cuts), [(1.0, 2.5)])

    proc = _cli(str(cuts), str(master), "-o", "/dev/null", "--dry-run")
    assert proc.returncode == 0, proc.stderr
    lines = [ln for ln in proc.stdout.splitlines() if "trim=" in ln]
    v_bounds = [ln for ln in lines if ln.startswith("[0:v]")]
    a_bounds = [
        ln.replace("[0:a]atrim", "").replace("asetpts", "setpts")
        for ln in lines
        if ln.startswith("[0:a]")
    ]
    v_norm = [ln.replace("[0:v]trim", "") for ln in v_bounds]
    # Strip the trailing [vN]/[aN] labels; the start/end pairs must match.
    v_se = [ln.split(",")[0] for ln in v_norm]
    a_se = [ln.split(",")[0] for ln in a_bounds]
    assert v_se == a_se
