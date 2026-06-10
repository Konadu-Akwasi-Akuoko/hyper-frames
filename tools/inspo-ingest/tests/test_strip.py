"""Tests for the pure argv builders — assert the verified flag shape, run nothing."""
from __future__ import annotations

from pathlib import Path

import pytest

from inspo_ingest.strip import (
    contact_sheet_argvs,
    extract_frame_argv,
    ffmpeg_flow_decode_argv,
    ffprobe_dimensions_argv,
    filmstrip_argv,
    scene_detect_argv,
    ytdlp_download_argv,
)


def test_ytdlp_download_argv_uses_verified_section_and_format() -> None:
    argv = ytdlp_download_argv(
        url="https://www.youtube.com/watch?v=VIDEO_ID",
        start_s=72.0,
        end_s=78.0,
        out_template="/tmp/clip.%(ext)s",
    )
    assert argv[0] == "yt-dlp"
    # The `*` prefix is mandatory for a time-range (not a chapter regex).
    i = argv.index("--download-sections")
    assert argv[i + 1] == "*72-78"
    # Highest-resolution video-only selector — NOT mp4-constrained (mp4 caps at 1080p;
    # 4K lives only in vp9/av1 webm), with resolution-first sort to prefer 4K.
    f = argv.index("-f")
    assert argv[f + 1] == "bv*/b"
    assert argv[argv.index("-S") + 1] == "res,fps"
    # Audio is never used downstream, so no muxing/merge step.
    assert "--merge-output-format" not in argv
    # Throttle guard for repeated invocations.
    assert "--sleep-requests" in argv
    # URL is last, output template wired through -o.
    assert argv[-1] == "https://www.youtube.com/watch?v=VIDEO_ID"
    assert argv[argv.index("-o") + 1] == "/tmp/clip.%(ext)s"
    # Default: no forced re-encode.
    assert "--force-keyframes-at-cuts" not in argv


def test_ytdlp_download_argv_decimal_seconds() -> None:
    argv = ytdlp_download_argv(
        url="u", start_s=5.0, end_s=12.5, out_template="o"
    )
    section = argv[argv.index("--download-sections") + 1]
    assert section == "*5-12.5"


def test_ytdlp_force_keyframes_opt_in() -> None:
    argv = ytdlp_download_argv(
        url="u", start_s=1.0, end_s=2.0, out_template="o", force_keyframes=True
    )
    assert "--force-keyframes-at-cuts" in argv


def test_ytdlp_download_argv_max_height_bounds_format_and_keeps_sort() -> None:
    argv = ytdlp_download_argv(
        url="u",
        start_s=1.0,
        end_s=2.0,
        out_template="o",
        max_height=1080,
    )
    # The format selector bounds height to <=1080 (proxy cap for whole-video scan).
    fmt = argv[argv.index("-f") + 1]
    assert "height<=1080" in fmt
    assert fmt == "bv*[height<=1080]/b[height<=1080]"
    # Resolution-first sort is RETAINED so the best stream WITHIN the cap still wins.
    assert argv[argv.index("-S") + 1] == "res,fps"
    # Still no mp4 constraint / no merge — the cap reuses the webm-friendly reasoning.
    assert "--merge-output-format" not in argv


def test_ytdlp_download_argv_whole_video_omits_download_sections() -> None:
    # Whole-video proxy: no start/end window -> no --download-sections at all.
    argv = ytdlp_download_argv(
        url="u",
        out_template="o",
        max_height=1080,
    )
    assert "--download-sections" not in argv
    # The rest of the argv shape is intact.
    assert argv[0] == "yt-dlp"
    assert argv[-1] == "u"
    assert argv[argv.index("-o") + 1] == "o"


def test_ytdlp_download_argv_existing_call_shape_unchanged() -> None:
    # Regression guard: the today's call shape (no new kwargs) must reproduce the exact
    # byte-for-byte argv the motion-inspo-add skill relies on.
    argv = ytdlp_download_argv(
        url="https://www.youtube.com/watch?v=VIDEO_ID",
        start_s=72.0,
        end_s=78.0,
        out_template="/tmp/clip.%(ext)s",
    )
    assert argv == [
        "yt-dlp",
        "--download-sections",
        "*72-78",
        "-f",
        "bv*/b",
        "-S",
        "res,fps",
        "--sleep-requests",
        "1",
        "-o",
        "/tmp/clip.%(ext)s",
        "https://www.youtube.com/watch?v=VIDEO_ID",
    ]


def test_ytdlp_prefer_avc_adds_h264_tiebreak_after_res() -> None:
    # Scan mode software-decodes the whole proxy, so it prefers H.264 over AV1/VP9. The
    # codec preference is a TIEBREAK appended after res,fps — resolution must still dominate
    # (we want 1080p H.264, never 720p H.264 over 1080p AV1).
    argv = ytdlp_download_argv(
        url="u", out_template="o", max_height=1080, prefer_avc=True
    )
    assert argv[argv.index("-S") + 1] == "res,fps,vcodec:h264"


def test_ytdlp_prefer_avc_defaults_off() -> None:
    # clip mode (and every existing caller) leaves the sort untouched.
    argv = ytdlp_download_argv(url="u", start_s=1.0, end_s=2.0, out_template="o")
    assert argv[argv.index("-S") + 1] == "res,fps"


def test_ytdlp_subtitles_langs_appends_verified_flag_group_before_url() -> None:
    # pace mode fetches subtitles in the SAME yt-dlp call (one invocation total — this
    # IP has tripped the bot-wall before). The flag group is contiguous, after the fixed
    # block, before the URL.
    argv = ytdlp_download_argv(
        url="https://www.youtube.com/watch?v=VIDEO_ID",
        out_template="/tmp/proxy.%(ext)s",
        max_height=1080,
        prefer_avc=True,
        subtitles_langs=("en-orig", "en"),
    )
    i = argv.index("--write-auto-subs")
    assert argv[i : i + 8] == [
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "en-orig,en",
        "--sub-format",
        "json3/srv3/vtt",
        "--sleep-subtitles",
        "2",
    ]
    # After the fixed block (the -o pair), immediately before the URL.
    assert i > argv.index("-o") + 1
    assert argv[-1] == "https://www.youtube.com/watch?v=VIDEO_ID"
    assert argv[-2] == "2"
    # info-json not requested here.
    assert "--write-info-json" not in argv


def test_ytdlp_write_info_json_appends_single_flag_before_url() -> None:
    argv = ytdlp_download_argv(
        url="u", out_template="o", max_height=1080, write_info_json=True
    )
    assert argv[-2:] == ["--write-info-json", "u"]
    # No subtitle flags without subtitles_langs.
    assert "--write-auto-subs" not in argv
    assert "--sub-langs" not in argv


def test_ytdlp_subtitles_and_info_json_combined_order() -> None:
    # Exact tail shape when both opt-ins are set: subtitle group, then info-json, then URL.
    argv = ytdlp_download_argv(
        url="u",
        out_template="o",
        max_height=1080,
        subtitles_langs=("en-orig", "en"),
        write_info_json=True,
    )
    assert argv == [
        "yt-dlp",
        "-f",
        "bv*[height<=1080]/b[height<=1080]",
        "-S",
        "res,fps",
        "--sleep-requests",
        "1",
        "-o",
        "o",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "en-orig,en",
        "--sub-format",
        "json3/srv3/vtt",
        "--sleep-subtitles",
        "2",
        "--write-info-json",
        "u",
    ]


def test_ytdlp_subtitles_defaults_off_keeps_argv_clean() -> None:
    argv = ytdlp_download_argv(url="u", start_s=1.0, end_s=2.0, out_template="o")
    for flag in (
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "--sub-format",
        "--sleep-subtitles",
        "--write-info-json",
    ):
        assert flag not in argv


def test_ffprobe_dimensions_argv_emits_bare_wxh() -> None:
    argv = ffprobe_dimensions_argv(clip_path=Path("/tmp/clip.mp4"))
    assert argv[0] == "ffprobe"
    assert argv[argv.index("-select_streams") + 1] == "v:0"
    assert argv[argv.index("-show_entries") + 1] == "stream=width,height"
    # csv=p=0:s=x -> a bare "1920x1080" with no keys, 'x' separator (parsed by _probe_dims).
    assert argv[argv.index("-of") + 1] == "csv=p=0:s=x"
    assert argv[-1] == "/tmp/clip.mp4"


def test_ffmpeg_flow_decode_argv_decimates_scales_and_emits_rawvideo() -> None:
    argv = ffmpeg_flow_decode_argv(
        clip_path=Path("/tmp/clip.mp4"), fps=10.0, width=256, height=144
    )
    assert argv[0] == "ffmpeg"
    assert argv[argv.index("-i") + 1] == "/tmp/clip.mp4"
    # One filter chain: fps-decimate THEN area-downscale to the exact pipe geometry.
    assert argv[argv.index("-vf") + 1] == "fps=10,scale=256:144:flags=area"
    # Packed BGR rawvideo to stdout so the caller reads fixed-size width*height*3 frames.
    assert argv[argv.index("-pix_fmt") + 1] == "bgr24"
    assert argv[argv.index("-f") + 1] == "rawvideo"
    assert "-an" in argv
    assert argv[-1] == "-"


def test_ffmpeg_flow_decode_argv_formats_fractional_fps() -> None:
    argv = ffmpeg_flow_decode_argv(
        clip_path=Path("c"), fps=7.5, width=256, height=146
    )
    assert argv[argv.index("-vf") + 1] == "fps=7.5,scale=256:146:flags=area"


def test_scene_detect_argv_uses_select_metadata_print() -> None:
    argv = scene_detect_argv(
        clip_path=Path("/tmp/clip.mp4"),
        meta_path=Path("/tmp/meta.txt"),
    )
    assert argv[0] == "ffmpeg"
    vf = argv[argv.index("-vf") + 1]
    # Verified: select=gte(scene\,0) so ALL frames score; comma escaped in the filter.
    assert vf == "select=gte(scene\\,0),metadata=print:file=/tmp/meta.txt"
    assert argv[argv.index("-i") + 1] == "/tmp/clip.mp4"
    # Null muxer, no audio decode.
    assert "-an" in argv
    assert argv[argv.index("-f") + 1] == "null"
    assert argv[-1] == "-"


def test_extract_frame_argv_output_side_seek_and_scale() -> None:
    argv = extract_frame_argv(
        clip_path=Path("/tmp/clip.mp4"),
        time_s=3.337,
        frame_width=480,
        out_path=Path("/tmp/frame_000.png"),
    )
    assert argv[0] == "ffmpeg"
    # Output-side seek: -i precedes -ss (frame-accurate on short clips).
    assert argv.index("-i") < argv.index("-ss")
    assert argv[argv.index("-ss") + 1] == "3.337"
    assert argv[argv.index("-frames:v") + 1] == "1"
    assert argv[argv.index("-vf") + 1] == "scale=480:-1"
    assert argv[-1] == "/tmp/frame_000.png"


def test_extract_frame_argv_fast_seek_uses_input_then_output_ss() -> None:
    # Scan mode extracts from a whole-video proxy at absolute timestamps. fast_seek jumps
    # near the target keyframe with an input-side -ss (before -i), then decodes the last
    # second with an output-side -ss to land on the exact frame — near-instant vs decoding
    # the whole proxy from zero (which output-side-only would do at a late timestamp).
    argv = extract_frame_argv(
        clip_path=Path("/tmp/proxy.mp4"),
        time_s=529.0,
        frame_width=480,
        out_path=Path("/tmp/f.png"),
        fast_seek=True,
    )
    i_input = argv.index("-i")
    ss_positions = [k for k, a in enumerate(argv) if a == "-ss"]
    # Two seeks straddling -i: input-side (529 - 1 = 528) before, preroll (1) after.
    assert len(ss_positions) == 2
    assert ss_positions[0] < i_input < ss_positions[1]
    assert argv[ss_positions[0] + 1] == "528"
    assert argv[ss_positions[1] + 1] == "1"


def test_extract_frame_argv_fast_seek_near_start_stays_output_side() -> None:
    # A timestamp inside the preroll window can't fast-seek before zero, so it falls back to
    # the plain output-side form (decoding from start is trivially cheap there anyway).
    argv = extract_frame_argv(
        clip_path=Path("/tmp/proxy.mp4"),
        time_s=0.5,
        frame_width=480,
        out_path=Path("/tmp/f.png"),
        fast_seek=True,
    )
    assert argv.index("-i") < argv.index("-ss")
    assert argv[argv.index("-ss") + 1] == "0.5"


def test_filmstrip_argv_uses_append_not_montage() -> None:
    frames = [Path(f"/tmp/frame_{i:03d}.png") for i in range(3)]
    argv = filmstrip_argv(frame_paths=frames, out_path=Path("/tmp/out-strip.png"), frame_width=480)
    # `magick … +append`, NOT `magick montage` — montage needs a font this build lacks.
    assert argv[0] == "magick"
    assert "montage" not in argv
    assert "+append" in argv
    # Frames passed explicitly (deterministic order), before the flags.
    assert argv[1:4] == [str(f) for f in frames]
    # Per-tile resize to the requested width (height auto, aspect preserved).
    assert argv[argv.index("-resize") + 1] == "480x"
    # Thin separator border so tile boundaries stay legible.
    assert argv[argv.index("-border") + 1] == "3"
    assert argv[-1] == "/tmp/out-strip.png"


def test_filmstrip_argv_resize_scales_with_width() -> None:
    argv = filmstrip_argv(frame_paths=[Path("a.png")], out_path=Path("o.png"), frame_width=320)
    assert argv[argv.index("-resize") + 1] == "320x"


def _thumbs(n: int) -> list[Path]:
    return [Path(f"/tmp/thumbs/scene-{i:03d}.png") for i in range(1, n + 1)]


def test_contact_sheet_argvs_single_row_appends_straight_to_out_path() -> None:
    # Fewer thumbs than row_len -> one +append directly to out_path, no -append step,
    # no intermediate row files to clean up.
    argvs, row_paths = contact_sheet_argvs(
        frame_paths=_thumbs(4),
        out_path=Path("/tmp/sheet-000.png"),
        row_len=10,
        tmp_dir=Path("/tmp/rows"),
    )
    assert row_paths == []
    assert argvs == [
        [
            "magick",
            "/tmp/thumbs/scene-001.png",
            "/tmp/thumbs/scene-002.png",
            "/tmp/thumbs/scene-003.png",
            "/tmp/thumbs/scene-004.png",
            "+append",
            "/tmp/sheet-000.png",
        ]
    ]


def test_contact_sheet_argvs_exact_multiple_rows_then_vertical_stack() -> None:
    # 6 thumbs at row_len=3 -> exactly 2 full rows, then one -append stacking them.
    argvs, row_paths = contact_sheet_argvs(
        frame_paths=_thumbs(6),
        out_path=Path("/tmp/sheet-000.png"),
        row_len=3,
        tmp_dir=Path("/tmp/rows"),
    )
    assert row_paths == ["/tmp/rows/row-000.png", "/tmp/rows/row-001.png"]
    assert argvs == [
        [
            "magick",
            "/tmp/thumbs/scene-001.png",
            "/tmp/thumbs/scene-002.png",
            "/tmp/thumbs/scene-003.png",
            "+append",
            "/tmp/rows/row-000.png",
        ],
        [
            "magick",
            "/tmp/thumbs/scene-004.png",
            "/tmp/thumbs/scene-005.png",
            "/tmp/thumbs/scene-006.png",
            "+append",
            "/tmp/rows/row-001.png",
        ],
        [
            "magick",
            "/tmp/rows/row-000.png",
            "/tmp/rows/row-001.png",
            "-background",
            "none",
            "-append",
            "/tmp/sheet-000.png",
        ],
    ]


def test_contact_sheet_argvs_remainder_row_is_shorter() -> None:
    # 7 thumbs at row_len=3 -> rows of 3, 3, 1; the short final row is padded by the
    # -append step's -background none, so no filler tiles are synthesized.
    argvs, row_paths = contact_sheet_argvs(
        frame_paths=_thumbs(7),
        out_path=Path("/tmp/sheet-000.png"),
        row_len=3,
        tmp_dir=Path("/tmp/rows"),
    )
    assert row_paths == [
        "/tmp/rows/row-000.png",
        "/tmp/rows/row-001.png",
        "/tmp/rows/row-002.png",
    ]
    assert len(argvs) == 4
    # Last row argv carries only the single remainder thumb.
    assert argvs[2] == [
        "magick",
        "/tmp/thumbs/scene-007.png",
        "+append",
        "/tmp/rows/row-002.png",
    ]
    # Final stack consumes the row PNGs in order, transparent padding, -append.
    assert argvs[3] == [
        "magick",
        "/tmp/rows/row-000.png",
        "/tmp/rows/row-001.png",
        "/tmp/rows/row-002.png",
        "-background",
        "none",
        "-append",
        "/tmp/sheet-000.png",
    ]


def test_contact_sheet_argvs_never_montage_never_annotate() -> None:
    # montage and -annotate both need a configured font; Homebrew builds abort with
    # "unable to read font" (project memory). Neither may ever appear.
    for n in (1, 3, 7):
        argvs, _ = contact_sheet_argvs(
            frame_paths=_thumbs(n),
            out_path=Path("/tmp/sheet.png"),
            row_len=3,
            tmp_dir=Path("/tmp/rows"),
        )
        for argv in argvs:
            assert argv[0] == "magick"
            assert "montage" not in argv
            assert "-annotate" not in argv


def test_contact_sheet_argvs_rejects_empty_and_bad_row_len() -> None:
    with pytest.raises(ValueError):
        contact_sheet_argvs(
            frame_paths=[],
            out_path=Path("o.png"),
            row_len=3,
            tmp_dir=Path("/tmp/rows"),
        )
    with pytest.raises(ValueError):
        contact_sheet_argvs(
            frame_paths=_thumbs(2),
            out_path=Path("o.png"),
            row_len=0,
            tmp_dir=Path("/tmp/rows"),
        )
