"""Pure cli.py tests: subcommand shim, pace parser shape, and manifest assembly.

Binary-free by construction: importing ``inspo_ingest.cli`` pulls no third-party
deps (``cv2`` is lazy-imported inside the scan/pace feature passes only), and
nothing here spawns a subprocess.
"""
from __future__ import annotations

import json
from pathlib import Path

from inspo_ingest.cli import (
    _build_parser,
    _inject_clip_shim,
    _pace_aggregates_json,
    _pace_manifest,
    _pace_scene_record,
    _pace_video_json,
    _run_pace,
)
from inspo_ingest.scenes import SceneWindow
from inspo_ingest.transcript import SceneNarration

URL = "https://www.youtube.com/watch?v=VIDEO_ID"


# --- _inject_clip_shim ---


def test_shim_pace_is_not_rewritten():
    argv = ["pace", URL, "--slug", "x"]
    assert _inject_clip_shim(argv) == argv


def test_shim_scan_is_not_rewritten():
    argv = ["scan", URL, "--slug", "x"]
    assert _inject_clip_shim(argv) == argv


def test_shim_clip_is_not_rewritten():
    argv = ["clip", URL, "--slug", "x", "--section", "1:12-1:18"]
    assert _inject_clip_shim(argv) == argv


def test_shim_bare_url_still_gets_clip_injected():
    argv = [URL, "--slug", "x", "--section", "1:12-1:18"]
    assert _inject_clip_shim(argv) == ["clip", *argv]


def test_shim_help_and_empty_pass_through():
    assert _inject_clip_shim([]) == []
    assert _inject_clip_shim(["-h"]) == ["-h"]
    assert _inject_clip_shim(["--help"]) == ["--help"]


# --- pace parser ---


def test_pace_parser_defaults_match_plan():
    args = _build_parser().parse_args(["pace", URL, "--slug", "demo"])
    assert args.url == URL
    assert args.slug == "demo"
    assert args.out is None
    assert args.max_height == 1080
    assert args.sample_fps == 10.0
    assert args.hard_floor == 0.05
    assert args.hard_ratio == 6.0
    assert args.hard_window == 3.0
    assert args.min_gap == 0.3
    assert args.soft_wide_min == 0.12
    assert args.soft_adj_max == 0.10
    assert args.soft_plateau == 0.5
    assert args.dedupe == 0.2
    assert args.langs == "en-orig,en"
    assert args.no_frames is False
    assert args.thumb_width == 160
    assert args._handler is _run_pace


def test_pace_parser_accepts_overrides():
    args = _build_parser().parse_args(
        [
            "pace",
            URL,
            "--slug",
            "demo",
            "--out",
            "/tmp/pace-out",
            "--max-height",
            "720",
            "--sample-fps",
            "5",
            "--hard-floor",
            "0.2",
            "--langs",
            "de,en",
            "--no-frames",
            "--thumb-width",
            "240",
        ]
    )
    assert args.out == Path("/tmp/pace-out")
    assert args.max_height == 720
    assert args.sample_fps == 5.0
    assert args.hard_floor == 0.2
    assert args.langs == "de,en"
    assert args.no_frames is True
    assert args.thumb_width == 240


def test_scan_parser_from_proxy_defaults_to_none():
    args = _build_parser().parse_args(["scan", URL, "--slug", "demo"])
    assert args.from_proxy is None


def test_scan_parser_accepts_from_proxy():
    args = _build_parser().parse_args(
        ["scan", URL, "--slug", "demo", "--from-proxy", "/tmp/cache/proxy.mp4"]
    )
    assert args.from_proxy == Path("/tmp/cache/proxy.mp4")
    assert args.url == URL


# --- manifest assembly (frozen inspo-pace/1 field names) ---


def _scene(index: int = 2, start: float = 4.0, end: float = 9.5) -> SceneWindow:
    return SceneWindow(
        index=index,
        start_s=start,
        end_s=end,
        boundary_kind="cut",
        boundary_score=0.61239,
    )


def _narration() -> SceneNarration:
    return SceneNarration(
        word_count=11,
        words_per_s=2.123456,
        coverage=0.98765,
        first_word_offset_s=0.21,
        leading_silence_s=0.21,
        trailing_silence_s=-0.0,
        cut_in_pause=True,
        pause_before_cut_s=0.7,
        sentence_aligned=True,
        text="eleven words of narration | with a pipe inside the scene",
    )


def test_scene_record_frozen_field_names():
    record = _pace_scene_record(_scene(), _narration(), "demo-thumbs/scene-002.png")
    assert set(record) == {
        "index",
        "window",
        "duration_s",
        "boundary",
        "narration",
        "files",
    }
    assert set(record["window"]) == {"start_s", "end_s"}
    assert set(record["boundary"]) == {"kind", "score"}
    assert set(record["files"]) == {"thumb"}
    assert set(record["narration"]) == {
        "word_count",
        "words_per_s",
        "coverage",
        "first_word_offset_s",
        "leading_silence_s",
        "trailing_silence_s",
        "cut_in_pause",
        "pause_before_cut_s",
        "sentence_aligned",
        "text",
    }


def test_scene_record_quantizes_and_normalizes_floats():
    record = _pace_scene_record(_scene(), _narration(), None)
    assert record["narration"]["words_per_s"] == 2.1235
    assert record["narration"]["coverage"] == 0.9877
    # -0.0 normalizes to 0.0 (json would otherwise print "-0.0").
    assert str(record["narration"]["trailing_silence_s"]) == "0.0"
    assert record["boundary"]["score"] == 0.6124
    assert record["duration_s"] == 5.5
    assert record["files"]["thumb"] is None


def test_scene_record_no_narration_and_start_boundary():
    scene = SceneWindow(
        index=1, start_s=0.0, end_s=4.0, boundary_kind="start", boundary_score=None
    )
    record = _pace_scene_record(scene, None, None)
    assert record["narration"] is None
    assert record["boundary"] == {"kind": "start", "score": None}
    assert record["narration"] is None


def test_aggregates_json_frozen_field_names_and_null_passthrough():
    agg = {
        "scene_count": 3,
        "cuts_per_minute": 8.123456,
        "soft_transition_count": 1,
        "scene_duration_s": {
            "median": 2.0,
            "p25": 1.5,
            "p75": 3.25,
            "min": 1.0,
            "max": 4.0,
        },
        "longest_hold_s": 4.0,
        "words_per_s_mean": None,
        "pct_cuts_in_pause": None,
        "pct_sentence_aligned": None,
    }
    out = _pace_aggregates_json(agg)
    assert set(out) == {
        "scene_count",
        "cuts_per_minute",
        "soft_transition_count",
        "scene_duration_s",
        "longest_hold_s",
        "words_per_s_mean",
        "pct_cuts_in_pause",
        "pct_sentence_aligned",
    }
    assert set(out["scene_duration_s"]) == {"median", "p25", "p75", "min", "max"}
    assert out["cuts_per_minute"] == 8.1235
    assert out["words_per_s_mean"] is None
    assert out["pct_cuts_in_pause"] is None
    assert out["pct_sentence_aligned"] is None


def test_pace_manifest_frozen_top_level_shape():
    scenes = [
        SceneWindow(
            index=1, start_s=0.0, end_s=10.0, boundary_kind="start", boundary_score=None
        )
    ]
    agg = {
        "scene_count": 1,
        "cuts_per_minute": 0.0,
        "soft_transition_count": 0,
        "scene_duration_s": {
            "median": 10.0,
            "p25": 10.0,
            "p75": 10.0,
            "min": 10.0,
            "max": 10.0,
        },
        "longest_hold_s": 10.0,
        "words_per_s_mean": None,
        "pct_cuts_in_pause": None,
        "pct_sentence_aligned": None,
    }
    manifest = _pace_manifest(
        url=URL,
        slug="demo",
        video=_pace_video_json(None),
        max_height=1080,
        proxy_duration_s=10.0,
        sample_fps=10.0,
        hard_floor=0.12,
        hard_ratio=6.0,
        hard_window=3.0,
        min_gap=0.3,
        soft_wide_min=0.22,
        soft_adj_max=0.10,
        soft_plateau=0.5,
        dedupe=0.2,
        subtitles=None,
        scenes=scenes,
        narrations=[None],
        thumbs=[None],
        agg=agg,
    )
    assert set(manifest) == {
        "schema",
        "source_url",
        "slug",
        "video",
        "proxy",
        "scene_detect",
        "subtitles",
        "scenes",
        "aggregates",
    }
    assert manifest["schema"] == "inspo-pace/1"
    assert set(manifest["video"]) == {"title", "channel", "upload_date", "duration_s"}
    assert manifest["video"]["title"] is None
    assert set(manifest["proxy"]) == {"max_height", "duration_s"}
    assert set(manifest["scene_detect"]) == {"hard", "soft", "dedupe_s"}
    assert set(manifest["scene_detect"]["hard"]) == {
        "abs_floor",
        "ratio",
        "window_s",
        "min_gap_s",
    }
    assert set(manifest["scene_detect"]["soft"]) == {
        "sample_fps",
        "proc_width",
        "wide_baseline_s",
        "wide_min",
        "adj_max",
        "min_plateau_s",
        "suppress_s",
    }
    assert manifest["scene_detect"]["soft"]["proc_width"] == 256
    assert manifest["scene_detect"]["soft"]["wide_baseline_s"] == 1.0
    assert manifest["subtitles"] is None
    assert len(manifest["scenes"]) == 1
    # The whole manifest must serialize the way _run_pace writes it.
    json.dumps(manifest, indent=2, sort_keys=True)


def test_pace_video_json_from_info():
    info = {
        "title": "A Video",
        "channel": "A Channel",
        "upload_date": "20260101",
        "duration": 612,
    }
    assert _pace_video_json(info) == {
        "title": "A Video",
        "channel": "A Channel",
        "upload_date": "20260101",
        "duration_s": 612.0,
    }


def test_pace_video_json_falls_back_to_uploader():
    assert _pace_video_json({"uploader": "Someone"})["channel"] == "Someone"
