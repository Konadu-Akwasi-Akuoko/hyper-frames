"""cut-video CLI: apply cuts.json removed-spans to a video/audio source.

cuts.json lists REMOVED [start, end] spans in seconds; the keep-windows are the
complement. Picture and audio are cut on the SAME absolute-source-time windows
(keeping phone HEVC audio lead/lag aligned) and the source is RE-ENCODED — never
stream-copied, since -c copy is keyframe-bound and would drift on sub-frame cut
boundaries. The keep math + filtergraph live in the zero-I/O `segments` module;
this CLI and `ffmpeg` own the single subprocess.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from . import ffmpeg, segments

TOOL = "cut-video"


def _load_cuts(path: str) -> list[tuple[float, float]]:
    data: dict[str, Any] = json.loads(Path(path).read_text())
    if data.get("version") != 1:
        raise ValueError(
            f"unsupported cuts.json version {data.get('version')!r} "
            "(expected 1)"
        )
    out: list[tuple[float, float]] = []
    for c in data.get("cuts", []):
        out.append((float(c["start"]), float(c["end"])))
    return out


def _print_summary(
    src: str,
    duration: float,
    keeps: list[segments.Keep],
    mode: str,
) -> None:
    kept, removed, count = segments.summarize(keeps, duration)
    print(f"{TOOL}: source {src}")
    print(f"{TOOL}: mode {mode}  source-dur {duration:.6f}s")
    print(
        f"{TOOL}: kept {kept:.6f}s  removed {removed:.6f}s  segments {count}"
    )
    print(f"{TOOL}: keep-windows:")
    for i, k in enumerate(keeps):
        print(f"{TOOL}:   [{i}] {k.start:.6f} -> {k.end:.6f}  ({k.duration:.6f}s)")


def _cut(args: argparse.Namespace) -> int:
    cuts = _load_cuts(args.cuts)
    p = ffmpeg.probe(args.source)

    mode = args.mode or ffmpeg.infer_mode(p)
    ffmpeg.assert_streams(p, mode)

    fps = p.fps if (mode == "video" and p.fps > 0) else 1000.0
    keeps = segments.keep_windows(
        cuts,
        duration=p.duration,
        fps=fps,
        epsilon_frames=args.epsilon_frames,
        snap=args.snap,
    )

    want_video = mode == "video"
    graph = segments.filter_complex_script(
        keeps, audio=True, video=want_video
    )

    _print_summary(args.source, p.duration, keeps, mode)

    if args.dry_run:
        print(f"{TOOL}: --dry-run; generated filtergraph:")
        print(graph, end="")
        return 0

    with tempfile.NamedTemporaryFile(
        "w", suffix=".filtergraph", delete=False
    ) as fh:
        fh.write(graph)
        graph_path = fh.name
    try:
        argv = ffmpeg.build_argv(
            args.source, graph_path, args.out, mode, args.crf, args.preset
        )
        ffmpeg.run_cut(argv)
    finally:
        Path(graph_path).unlink(missing_ok=True)

    print(f"{TOOL}: wrote {args.out}")
    return 0


def _extract_audio(args: argparse.Namespace) -> int:
    p = ffmpeg.probe(args.source)
    if p.n_audio < 1:
        raise ffmpeg.StreamError(
            "source has no audio stream to extract"
        )
    argv = ffmpeg.extract_audio_argv(
        args.source, args.out, args.bitrate, args.mono, args.ar
    )
    ffmpeg.run_extract_audio(argv)
    print(f"{TOOL}: wrote {args.out}")
    return 0


def _cut_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog=TOOL,
        description=(
            "Apply cuts.json removed-spans to a video/audio source, cutting "
            "picture and audio on identical keep-windows. "
            "Sub-command: 'extract-audio'."
        ),
    )
    ap.add_argument("cuts", help="cuts.json (removed spans, seconds)")
    ap.add_argument("source", help="source video or audio")
    ap.add_argument("-o", "--out", help="output cut-master path")
    ap.add_argument(
        "--mode", choices=["video", "audio"], default=None,
        help="override the inferred mode (default: inferred from stream set)",
    )
    ap.add_argument("--crf", type=int, default=12)
    ap.add_argument("--preset", default="medium")
    ap.add_argument(
        "--epsilon-frames", type=float, default=1.0,
        help="drop keeps shorter than this many frames",
    )
    ap.add_argument(
        "--snap", action="store_true",
        help="snap keep boundaries to the nearest integer frame time",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.set_defaults(func=_cut)
    return ap


def _extract_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog=f"{TOOL} extract-audio",
        description="Extract the audio track of a source video to an mp3.",
    )
    ap.add_argument("source", help="source video")
    ap.add_argument("-o", "--out", required=True, help="output audio path")
    ap.add_argument("--bitrate", default="64k")
    ap.add_argument("--mono", action="store_true")
    ap.add_argument("--ar", type=int, default=None, help="output sample rate")
    ap.set_defaults(func=_extract_audio)
    return ap


def main() -> None:
    # Route on the leading token so cuts.json/source paths are never mistaken
    # for a subcommand name (argparse subparsers reject path-shaped positionals).
    argv = sys.argv[1:]
    if argv and argv[0] == "extract-audio":
        ap = _extract_parser()
        args = ap.parse_args(argv[1:])
    else:
        ap = _cut_parser()
        args = ap.parse_args(argv)
        if not args.out and not args.dry_run:
            ap.error("cut requires -o/--out (unless --dry-run)")

    try:
        sys.exit(args.func(args))
    except (
        segments.WholeDurationRemovedError,
        ffmpeg.StreamError,
        ValueError,
    ) as exc:
        sys.exit(f"{TOOL}: error: {exc}")


if __name__ == "__main__":
    main()
