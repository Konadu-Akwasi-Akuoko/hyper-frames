"""CLI entry point for inspo-ingest.

Orchestration only: this module owns every subprocess call (yt-dlp, ffmpeg, ffprobe,
magick +append) and is the *sole* owner of ``cv2``. All parsing, ranking, argv
construction, and the pure motion-graphics detection math live in the ``frames``,
``strip``, and ``motion`` modules so the decision logic stays testable without binaries.

Three subcommands:

* ``clip`` — the original per-window capture (full-resolution download, scene-detect,
  rank, film-strip + hero, print a stub). Unchanged behavior.
* ``scan`` — the whole-video motion-graphics auto-scan: download ONE capped proxy,
  stream it through DIS optical flow into a ``FlowFingerprint`` time series, segment
  genuine animation beats (``motion.segment``), and for each beat run the existing
  capture pipeline against the one proxy, then write per-beat files + a deterministic
  ``<slug>-scan.json`` manifest.
* ``pace`` — the whole-video scene-change + narration pacing ingest: download ONE
  capped proxy (subtitles + info JSON in the SAME yt-dlp call), detect every hard cut
  (adaptive threshold over the full-fps scene-score series, ``scenes.detect_hard_cuts``)
  and soft transition (wide-baseline HSV plateaus, ``scenes.detect_soft_transitions``),
  align the json3 transcript to the resulting scene windows (``transcript``), and emit
  a deterministic ``<slug>-pace.json`` manifest + mechanical ``<slug>-pacing.md`` report
  + per-scene thumbs/contact sheets. Candidates only: never writes any library or prose.

``cv2`` is **lazy-imported inside the scan/pace codepaths only** (never at module top),
so importing this module for ``clip`` mode or for the pure test suite pulls zero
third-party deps.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path

from inspo_ingest.frames import (
    SceneCut,
    hero_cut,
    parse_scene_scores,
    parse_section,
    rank_cuts,
)
from inspo_ingest.motion import (
    CONCENTRATION_MIN,
    EASED_SHARE_MIN,
    MOV_TEXTURE_MAX,
    SPARSITY_MIN,
    BeatWindow,
    FlowFingerprint,
    adaptive_floor,
    describe,
    segment,
)
from inspo_ingest.scenes import (
    FeatureRow,
    SceneWindow,
    build_scenes,
    detect_hard_cuts,
    detect_soft_transitions,
    merge_boundaries,
)
from inspo_ingest.strip import (
    contact_sheet_argvs,
    extract_frame_argv,
    ffmpeg_flow_decode_argv,
    ffprobe_dimensions_argv,
    filmstrip_argv,
    scene_detect_argv,
    ytdlp_download_argv,
)
from inspo_ingest.transcript import (
    PUNCTUATED_MIN_FRACTION,
    SceneNarration,
    aggregates,
    align_scenes,
    filter_non_speech,
    parse_json3,
    punctuated_fraction,
)

DEFAULT_OUT = Path("/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/motionGraphicsInspo")
# pace-mode candidates land under scratch/ (never a library dir); the per-slug
# subfolder doubles as the proxy/subtitle/info-json cache for re-runs.
DEFAULT_PACE_OUT_BASE = Path("/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/scratch/pacing")

# (binary on PATH, brew formula hint)
_REQUIRED_BINARIES: tuple[tuple[str, str], ...] = (
    ("yt-dlp", "yt-dlp"),
    ("ffmpeg", "ffmpeg"),
    ("ffprobe", "ffmpeg"),
    ("magick", "imagemagick"),
)

# Hero frame is rendered at a fuller resolution than the film-strip tiles. 1600px sits
# just above Anthropic vision's ~1568px long-edge ceiling, so a 4K source downsamples to
# the crispest still the model will actually use without wasting bytes past that cap.
_HERO_WIDTH = 1600

# --- Flow-decode constants (ported from scratch/mg_probe_v3.py, validated on 16 clips) ---
# Streaming proxy width for the flow pass; everything is reduced at this 256px scale so the
# energy/texture thresholds in motion.py (calibrated at this scale) stay valid.
_PROC_WIDTH = 256
# Flow magnitude (px) below which a pixel counts as "still" -> drives sparsity.
_ZERO_EPS = 0.3
# Block grid the per-frame gini (spatial concentration) is computed over.
_GRID = 16
# Appearance mask: a pixel is "moving" above this flow magnitude (px).
_MASK_THRESH = 0.5
# Need at least this fraction of the frame moving to score appearance (else nan).
_MIN_MOVING_FRAC = 0.01
# Local-std window for the moving-region texture measure.
_TEX_K = 7
# Only the orientation of the strongest gradients counts toward axis_aligned.
_GRAD_STRONG_PCTILE = 70
# Axis-alignment tolerance in degrees (kept as degrees; converted to radians lazily with numpy).
_AXIS_TOL_DEG = 15.0

# DIS optical-flow tuning (explicit, not preset defaults) — recorded in the manifest.
_DIS_PRESET_NAME = "DISOPTICAL_FLOW_PRESET_MEDIUM"
_DIS_FINEST_SCALE = 1
_DIS_GRAD_ITERS = 12
_DIS_VAR_ITERS = 5

# Rounding tolerances applied to fingerprint reductions before segmentation so tiny
# cross-platform flow jitter cannot flip a beat boundary or a manifest byte.
_FP_TIME_DECIMALS = 3
_FP_VALUE_DECIMALS = 4
# Manifest float formatting: enough precision to be useful, few enough to stay stable.
_MANIFEST_DECIMALS = 4

# --- pace-mode constants ---
# Soft-transition candidates within this of a hard cut are dropped (the cut already
# explains the change); paired with detect_soft_transitions' suppress_s.
_SOFT_SUPPRESS_S = 1.0
# Contact-sheet geometry: row-major tiles, 10 per row, max 10 rows per sheet.
_SHEET_ROW_LEN = 10
_SHEET_MAX_ROWS = 10
# Per-scene thumbnail sample point: start + min(inset, duration/2) — never AT the
# boundary, where a fast_seek frame grab can land on the wrong side of the cut.
_THUMB_INSET_S = 0.3


def _build_clip_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(
        "clip",
        help="Capture a single bounded window (original behavior, full-res download).",
        description=(
            "Download a bounded YouTube section, scene-detect and rank the most "
            "significant cut frames, tile them into a film-strip PNG plus a fuller-res "
            "hero frame, and print a motion-inspo index-entry stub."
        ),
    )
    p.add_argument("url", help="YouTube URL to ingest a section from.")
    p.add_argument(
        "--slug",
        required=True,
        help="Kebab-case name for the output files (<slug>-strip.png, <slug>.png).",
    )
    p.add_argument(
        "--section",
        required=True,
        help='Time window as "MM:SS-MM:SS" (or "HH:MM:SS-HH:MM:SS"), e.g. "1:12-1:18".',
    )
    p.add_argument(
        "--scene-threshold",
        type=float,
        default=0.4,
        help="Scene-score threshold (0-1) recorded in the stub; ranking is top-N by score.",
    )
    p.add_argument(
        "--max-frames",
        type=int,
        default=6,
        help="Maximum number of frames in the film strip (top-N by scene score).",
    )
    p.add_argument(
        "--min-frames",
        type=int,
        default=3,
        help="Minimum frames; if fewer candidates, fall back to even spacing.",
    )
    p.add_argument(
        "--frame-width",
        type=int,
        default=480,
        help="Per-tile width in px for the film strip (height auto, 16:9).",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output directory (default: {DEFAULT_OUT}).",
    )
    p.add_argument(
        "--keep-clip",
        action="store_true",
        help="Keep the downloaded clip and intermediate frames instead of deleting them.",
    )
    p.set_defaults(_handler=_run_clip)
    return p


def _build_scan_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(
        "scan",
        help="Whole-video motion-graphics auto-scan (DIS optical flow -> per-beat captures).",
        description=(
            "Download one capped proxy of a whole video, stream it through DIS optical "
            "flow, auto-segment genuine motion-graphics beats, and emit a hero still + "
            "keyframe strip (+ optional flow heatmap) and objective motion descriptors "
            "per beat, plus a deterministic <slug>-scan.json manifest. Candidates only: "
            "never appends to the motion library."
        ),
    )
    p.add_argument("url", help="YouTube URL of the whole video to scan.")
    p.add_argument(
        "--slug",
        required=True,
        help="Kebab-case filename prefix/namespace for the N emitted beats.",
    )
    p.add_argument(
        "--max-height",
        type=int,
        default=1080,
        help="Cap the downloaded proxy resolution (default: 1080).",
    )
    p.add_argument(
        "--max-beats",
        type=int,
        default=12,
        help="Maximum number of beats to emit (top-N by motion-graphics score).",
    )
    p.add_argument(
        "--min-beat",
        type=float,
        default=1.2,
        help="Minimum beat duration in seconds; shorter candidates are dropped.",
    )
    p.add_argument(
        "--merge-gap",
        type=float,
        default=0.6,
        help="Maximum time gap (s) between gated neighbors that still merges them.",
    )
    p.add_argument(
        "--pad",
        type=float,
        default=0.4,
        help="Padding (s) added to each side of a beat window before clamping.",
    )
    p.add_argument(
        "--flow-fps",
        type=float,
        default=10.0,
        help="Target sampling rate (fps) for the flow pass.",
    )
    p.add_argument(
        "--max-frames",
        type=int,
        default=6,
        help="Maximum frames per beat film strip (top-N by scene score).",
    )
    p.add_argument(
        "--min-frames",
        type=int,
        default=3,
        help="Minimum frames per beat; if fewer candidates, fall back to even spacing.",
    )
    p.add_argument(
        "--frame-width",
        type=int,
        default=480,
        help="Per-tile width in px for each beat's film strip (height auto).",
    )
    p.add_argument(
        "--heatmap",
        action="store_true",
        help="Also write a per-beat flow heatmap PNG (turbo colormap).",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output directory (default: {DEFAULT_OUT}).",
    )
    p.add_argument(
        "--keep-proxy",
        action="store_true",
        help="Keep the downloaded proxy and intermediate frames instead of deleting them.",
    )
    p.add_argument(
        "--from-proxy",
        type=Path,
        default=None,
        help=(
            "Analyze this existing proxy file instead of downloading one (skips "
            "yt-dlp entirely; --max-height is ignored). The positional URL is still "
            "recorded as the manifest's source_url. Use with the proxy that a prior "
            "'pace' run cached, e.g. scratch/pacing/<slug>/proxy.mp4."
        ),
    )
    p.set_defaults(_handler=_run_scan)
    return p


def _build_pace_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(
        "pace",
        help="Whole-video scene-change + narration pacing ingest (cuts, transitions, transcript).",
        description=(
            "Download one capped proxy of a whole video (subtitles + info JSON in the "
            "same yt-dlp call), detect every hard cut and soft transition, align the "
            "transcript to the resulting scenes, and emit a deterministic "
            "<slug>-pace.json manifest, a mechanical <slug>-pacing.md report, and "
            "per-scene thumbnails + contact sheets. Candidates only: never writes any "
            "library or prose."
        ),
    )
    p.add_argument("url", help="YouTube URL of the whole video to analyze.")
    p.add_argument(
        "--slug",
        required=True,
        help="Kebab-case filename prefix for the emitted artifacts.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"Output directory (default: {DEFAULT_PACE_OUT_BASE}/<slug>).",
    )
    p.add_argument(
        "--max-height",
        type=int,
        default=1080,
        help="Cap the downloaded proxy resolution (default: 1080).",
    )
    p.add_argument(
        "--sample-fps",
        type=float,
        default=10.0,
        help="Sampling rate (fps) for the soft-transition feature pass.",
    )
    p.add_argument(
        "--hard-floor",
        type=float,
        default=0.05,
        help="Absolute scene-score floor a hard cut must always clear.",
    )
    p.add_argument(
        "--hard-ratio",
        type=float,
        default=6.0,
        help="Adaptive multiplier on the rolling-median scene score.",
    )
    p.add_argument(
        "--hard-window",
        type=float,
        default=3.0,
        help="Full width (s) of the centered rolling-median window.",
    )
    p.add_argument(
        "--min-gap",
        type=float,
        default=0.3,
        help="Debounce gap (s); qualifying cut frames closer than this cluster.",
    )
    p.add_argument(
        "--soft-wide-min",
        type=float,
        default=0.12,
        help="Minimum wide-baseline HSV delta for a soft-transition plateau row.",
    )
    p.add_argument(
        "--soft-adj-max",
        type=float,
        default=0.10,
        help="Maximum adjacent HSV delta for a soft-transition plateau row.",
    )
    p.add_argument(
        "--soft-plateau",
        type=float,
        default=0.5,
        help="Minimum plateau time span (s) for a soft transition.",
    )
    p.add_argument(
        "--dedupe",
        type=float,
        default=0.2,
        help="Boundaries within this (s) of each other collapse to one (hard wins).",
    )
    p.add_argument(
        "--langs",
        default="en-orig,en",
        help="Comma-separated subtitle language preference order.",
    )
    p.add_argument(
        "--no-frames",
        action="store_true",
        help="Skip per-scene thumbnails and contact sheets.",
    )
    p.add_argument(
        "--thumb-width",
        type=int,
        default=160,
        help="Per-scene thumbnail width in px (height auto).",
    )
    p.set_defaults(_handler=_run_pace)
    return p


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="inspo-ingest",
        description=(
            "Ingest motion-graphics reference from YouTube. 'clip' captures a single "
            "window; 'scan' auto-detects animation beats across a whole video via "
            "DIS optical flow; 'pace' detects every scene change and aligns the "
            "transcript to it."
        ),
    )
    sub = p.add_subparsers(dest="command")
    _build_clip_parser(sub)
    _build_scan_parser(sub)
    _build_pace_parser(sub)
    return p


_KNOWN_SUBCOMMANDS = frozenset({"clip", "scan", "pace"})


def _inject_clip_shim(argv: list[str]) -> list[str]:
    """Inject ``clip`` when the first token isn't a known subcommand (back-compat).

    The original shipped form is positional-URL-first (``inspo-ingest <url> --slug ...``),
    used verbatim by the ``motion-inspo-add`` skill. Subcommands would break those calls,
    so when ``argv[0]`` is neither a known subcommand nor a bare help/empty token, we
    prepend ``clip`` to preserve today's exact invocation. This is an argv rewrite, not
    parser config (argparse required-subparsers can't express "default subcommand").
    """
    if not argv:
        return argv
    first = argv[0]
    if first in _KNOWN_SUBCOMMANDS:
        return argv
    if first in ("-h", "--help"):
        return argv
    return ["clip", *argv]


def _preflight() -> str | None:
    """Return an error message if any required binary is missing, else ``None``."""
    for binary, brew in _REQUIRED_BINARIES:
        if shutil.which(binary) is None:
            return (
                f"required binary {binary!r} not found on PATH. "
                f"Install it (macOS: brew install {brew}) and retry."
            )
    return None


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def _ffprobe_duration(clip_path: Path) -> float:
    """Return the clip duration in seconds via ffprobe (0.0 if it can't be read)."""
    argv = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(clip_path),
    ]
    proc = _run(argv)
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def _find_clip(work_dir: Path) -> Path | None:
    candidates = sorted(work_dir.glob("clip.*"))
    return candidates[0] if candidates else None


def _print_stub(
    *,
    url: str,
    section: str,
    scene_threshold: float,
    cuts: list[SceneCut],
    start_s: float,
    strip_path: Path,
    hero_path: Path,
) -> None:
    """Print the two-part index stub: a Quick-index row + a full Entries block.

    The README is a two-tier index (a compact ``## Quick index`` scan table over full
    ``## Entries`` blocks), so every reference contributes *both* a table row and a detail
    block, kept in sync. This tool never authors prose: the Tags / Use when / Motion fields
    (and the row's archetype/motion/energy/mood/use-when cells) are intentionally left blank
    for ``motion-inspo-add`` to fill from reading the strip. Hero/Strip are emitted as bare
    filenames (they live beside the README), matching the entry schema; the absolute paths
    and chosen frame timestamps are printed separately as an author aside, not as part of
    the entry.
    """
    slug = hero_path.stem
    frame_times = ", ".join(f"{start_s + c.time_s:.2f}s" for c in cuts)
    print()
    print("Add BOTH of the following to motionGraphicsInspo/README.md "
          "(fill the blank judgment fields from the strip):")
    print()
    print('--- Quick-index row (append under "## Quick index") ---')
    print(f"| [{slug}](#{slug}) | <archetype> | <motion-verbs> | <energy> | <mood> | <use-when> |")
    print()
    print('--- Entries block (append under "## Entries") ---')
    print(f"### {slug}")
    print(f"- Hero: `{hero_path.name}` · Strip: `{strip_path.name}`")
    print("- Tags: motion=[] · archetype= · energy= · mood=")
    print("- Use when:")
    print("- Motion:")
    print(f"- Source: {url} @ {section}")
    print()
    print("(mechanical, for your reference — not part of the entry:)")
    print(f"- Chosen frame timestamps (absolute): {frame_times}")
    print(f"- Scene threshold: {scene_threshold:g}")
    print(f"- Strip file: {strip_path}")
    print(f"- Hero file: {hero_path}")
    print()


def _run_clip(args: argparse.Namespace) -> int:
    """The original per-window capture workflow (unchanged behavior)."""
    try:
        start_s, end_s = parse_section(args.section)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.min_frames < 1 or args.max_frames < args.min_frames:
        print(
            "error: require 1 <= --min-frames <= --max-frames "
            f"(got min={args.min_frames}, max={args.max_frames}).",
            file=sys.stderr,
        )
        return 2

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    strip_path = out_dir / f"{args.slug}-strip.png"
    hero_path = out_dir / f"{args.slug}.png"

    work_dir = Path(tempfile.mkdtemp(prefix="inspo-ingest-"))
    cleanup = not args.keep_clip
    try:
        # 1. Download the bounded section as a single highest-resolution video clip.
        dl = _run(
            ytdlp_download_argv(
                url=args.url,
                start_s=start_s,
                end_s=end_s,
                out_template=str(work_dir / "clip.%(ext)s"),
            )
        )
        if dl.returncode != 0:
            print(f"error: yt-dlp failed:\n{dl.stderr.strip()[-2000:]}", file=sys.stderr)
            return 1

        clip_path = _find_clip(work_dir)
        if clip_path is None:
            print("error: yt-dlp produced no clip file.", file=sys.stderr)
            return 1

        # 2. Scene-detect: score every frame to a metadata file.
        meta_path = work_dir / "scene-meta.txt"
        det = _run(
            scene_detect_argv(
                clip_path=clip_path,
                meta_path=meta_path,
            )
        )
        if det.returncode != 0:
            print(f"error: ffmpeg scene detection failed:\n{det.stderr.strip()[-2000:]}", file=sys.stderr)
            return 1

        meta_text = meta_path.read_text(encoding="utf-8") if meta_path.exists() else ""
        # The metadata file carries per-frame scores; stderr carries scdet log lines.
        all_cuts = parse_scene_scores(meta_text + "\n" + det.stderr)

        clip_duration = _ffprobe_duration(clip_path) or (end_s - start_s)
        chosen = rank_cuts(
            all_cuts,
            clip_duration_s=clip_duration,
            max_frames=args.max_frames,
            min_frames=args.min_frames,
        )

        # 3. Extract the strip frames.
        frame_paths: list[Path] = []
        for i, cut in enumerate(chosen):
            frame_path = work_dir / f"frame_{i:03d}.png"
            ext = _run(
                extract_frame_argv(
                    clip_path=clip_path,
                    time_s=cut.time_s,
                    frame_width=args.frame_width,
                    out_path=frame_path,
                )
            )
            if ext.returncode != 0 or not frame_path.exists():
                print(
                    f"error: ffmpeg frame extraction failed at {cut.time_s:g}s:\n"
                    f"{ext.stderr.strip()[-1000:]}",
                    file=sys.stderr,
                )
                return 1
            frame_paths.append(frame_path)

        # 4. Tile horizontally into the film strip.
        strip = _run(
            filmstrip_argv(frame_paths=frame_paths, out_path=strip_path, frame_width=args.frame_width)
        )
        if strip.returncode != 0:
            print(f"error: film strip (magick +append) failed:\n{strip.stderr.strip()[-2000:]}", file=sys.stderr)
            return 1

        # 5. Extract the hero frame (highest score, fuller res).
        hero = hero_cut(chosen)
        hero_extract = _run(
            extract_frame_argv(
                clip_path=clip_path,
                time_s=hero.time_s,
                frame_width=_HERO_WIDTH,
                out_path=hero_path,
            )
        )
        if hero_extract.returncode != 0 or not hero_path.exists():
            print(f"error: hero frame extraction failed:\n{hero_extract.stderr.strip()[-1000:]}", file=sys.stderr)
            return 1

    finally:
        if cleanup:
            shutil.rmtree(work_dir, ignore_errors=True)

    if not cleanup:
        print(f"kept clip + intermediate frames in {work_dir}", file=sys.stderr)

    _print_stub(
        url=args.url,
        section=args.section,
        scene_threshold=args.scene_threshold,
        cuts=chosen,
        start_s=start_s,
        strip_path=strip_path,
        hero_path=hero_path,
    )
    return 0


# --- scan-mode helpers (cv2 is lazy-imported inside _compute_fingerprints only) ---


def _fmt_mmss(seconds: float) -> str:
    """Format absolute seconds as ``MmSs`` for a beat filename (e.g. 72.4 -> ``1m12s``)."""
    total = int(round(seconds))
    return f"{total // 60}m{total % 60}s"


def _round_value(x: float) -> float:
    """Round a fingerprint reduction to a fixed tolerance (nan passes through)."""
    if x != x:  # nan
        return x
    return round(float(x), _FP_VALUE_DECIMALS)


def _q(x: float | None) -> float | None:
    """Round a manifest float to a fixed tolerance, normalizing -0.0 and passing nan/None."""
    if x is None:
        return None
    if isinstance(x, float) and x != x:  # nan -> null in JSON
        return None
    r = round(float(x), _MANIFEST_DECIMALS)
    return r + 0.0  # normalize -0.0 -> 0.0


def _probe_dims(path: Path) -> tuple[int, int]:
    """Return the proxy's first video stream ``(width, height)`` via ffprobe."""
    out = _run(ffprobe_dimensions_argv(clip_path=path))
    text = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
    try:
        w_str, h_str = text.split("x")
        return int(w_str), int(h_str)
    except ValueError as exc:
        raise RuntimeError(
            f"ffprobe could not read proxy dimensions (got {text!r}):\n"
            f"{out.stderr.strip()[-1000:]}"
        ) from exc


def _read_exact(stream, n: int) -> bytes | None:
    """Read exactly ``n`` bytes from a binary stream; ``None`` at clean EOF / short tail.

    A pipe ``read(n)`` may return fewer bytes than requested, so loop until the full frame
    is assembled. A short final read (truncated trailing frame) returns ``None`` to end the
    decode loop cleanly.
    """
    chunks: list[bytes] = []
    remaining = n
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _compute_fingerprints(
    proxy_path: Path,
    *,
    flow_fps: float,
    keep_mag_fields: bool = False,
) -> tuple[list[FlowFingerprint], str, list]:
    """Stream the proxy through DIS optical flow into a ``FlowFingerprint`` time series.

    LAZY-imports ``cv2`` (with an ImportError preflight + install hint) so importing this
    module for clip mode or the pure test suite pulls zero third-party deps. Holds only the
    previous gray + current gray/bgr frame (never accumulates all frames — fatal on a long
    video). Each sampled pair is reduced to one ``FlowFingerprint`` keyed by ABSOLUTE proxy
    seconds.

    Returns ``(fingerprints, cv2_version, mag_fields)``. When ``keep_mag_fields`` is True the
    raw per-sample numpy flow-magnitude arrays are retained (aligned to ``fingerprints``) for
    the optional ``--heatmap`` output; otherwise ``mag_fields`` stays empty so a long scan
    doesn't accumulate gigabytes of magnitude arrays nobody reads.

    Raises:
        ImportError: If ``cv2`` (opencv-python-headless) is not installed.
    """
    try:
        import cv2  # noqa: PLC0415  (lazy by design — keeps clip mode dep-free)
    except ImportError as exc:
        raise ImportError(
            "scan mode requires OpenCV. Install it with: "
            "uv pip install opencv-python-headless"
        ) from exc
    import numpy as np

    from inspo_ingest.motion import gini

    # Pin OpenCV to a single thread for the flow pass. It is no slower here (multi-thread
    # contention on small 256px frames cancels the parallelism) and it (a) holds the work to
    # one core instead of pinning all of them — much cooler and gentler on a laptop battery —
    # and (b) removes any thread-scheduling nondeterminism, so a re-scan is byte-identical.
    cv2.setNumThreads(1)

    axis_tol = float(np.deg2rad(_AXIS_TOL_DEG))

    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    dis.setFinestScale(_DIS_FINEST_SCALE)
    dis.setGradientDescentIterations(_DIS_GRAD_ITERS)
    dis.setVariationalRefinementIterations(_DIS_VAR_ITERS)

    # Geometry of the downscaled flow frames, computed up front so the raw-video pipe can
    # be read in fixed-size chunks. Height is forced even (some scalers require it).
    src_w, src_h = _probe_dims(proxy_path)
    proc_w = _PROC_WIDTH
    proc_h = max(2, int(round(src_h * proc_w / src_w)))
    if proc_h % 2:
        proc_h += 1
    frame_bytes = proc_w * proc_h * 3

    def _appearance(bgr, mask):
        """(texture, saturation, axis_aligned) over the moving region, or None if too small."""
        if mask.sum() < _MIN_MOVING_FRAC * mask.size:
            return None
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        mu = cv2.boxFilter(gray, -1, (_TEX_K, _TEX_K))
        mu2 = cv2.boxFilter(gray * gray, -1, (_TEX_K, _TEX_K))
        std = np.sqrt(np.clip(mu2 - mu * mu, 0, None))
        texture = float(std[mask].mean())

        sat_chan = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[..., 1].astype(np.float32) / 255.0
        saturation = float(sat_chan[mask].mean())

        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        gm = np.hypot(gx, gy)
        strong = mask & (gm > np.percentile(gm[mask], _GRAD_STRONG_PCTILE))
        if strong.sum() < 20:
            axis = 0.0
        else:
            ori = np.arctan2(gy[strong], gx[strong]) % np.pi
            d0 = np.minimum(ori, np.pi - ori)
            d90 = np.abs(ori - np.pi / 2)
            axis = float(np.mean(np.minimum(d0, d90) < axis_tol))
        return texture, saturation, axis

    fingerprints: list[FlowFingerprint] = []
    mag_fields: list = []

    # Decode through ffmpeg (decode + fps-decimate + downscale to 256px, all in C / libdav1d)
    # and read raw BGR frames off the pipe. This keeps AV1/HEVC decode on ffmpeg's fast path
    # and hands Python only tiny 256px frames at the flow rate — vs a VideoCapture loop that
    # decodes every full-resolution source frame (~100x slower on a long AV1 proxy, and it
    # pins every CPU core). The fps= filter spaces output frames exactly 1/flow_fps apart, so
    # absolute time is simply idx/flow_fps (no source-fps rounding to drift the boundaries).
    proc = subprocess.Popen(
        ffmpeg_flow_decode_argv(
            clip_path=proxy_path, fps=flow_fps, width=proc_w, height=proc_h
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None

    prev_gray = None
    idx = -1
    try:
        while True:
            buf = _read_exact(proc.stdout, frame_bytes)
            if buf is None:
                break
            idx += 1
            small_bgr = np.frombuffer(buf, dtype=np.uint8).reshape(proc_h, proc_w, 3)
            gray = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2GRAY)
            if prev_gray is None:
                prev_gray = gray
                continue

            t_s = idx / flow_fps
            flow = dis.calc(prev_gray, gray, None)
            mag = np.hypot(flow[..., 0], flow[..., 1])

            motion_energy = float(mag.mean())
            sparsity = float((mag < _ZERO_EPS).mean())
            block = cv2.resize(mag, (_GRID, _GRID), interpolation=cv2.INTER_AREA)
            concentration = gini(block)

            ap = _appearance(small_bgr, mag >= _MASK_THRESH)
            if ap is None:
                mov_texture = float("nan")
                mov_sat = float("nan")
                axis_aligned = float("nan")
            else:
                mov_texture, mov_sat, axis_aligned = ap

            fingerprints.append(
                FlowFingerprint(
                    t_s=round(t_s, _FP_TIME_DECIMALS),
                    motion_energy=_round_value(motion_energy),
                    sparsity=_round_value(sparsity),
                    spatial_concentration=_round_value(concentration),
                    mov_texture=_round_value(mov_texture),
                    mov_sat=_round_value(mov_sat),
                    axis_aligned=_round_value(axis_aligned),
                )
            )
            if keep_mag_fields:
                mag_fields.append(mag)
            prev_gray = gray
    finally:
        proc.stdout.close()
        err = proc.stderr.read() if proc.stderr else b""
        rc = proc.wait()

    if not fingerprints and rc != 0:
        raise RuntimeError(
            "ffmpeg flow decode failed:\n" + err.decode("utf-8", "replace")[-2000:]
        )
    return fingerprints, str(cv2.__version__), mag_fields


def _write_heatmap(mag_field, out_path: Path) -> bool:
    """Write a turbo-colormap flow heatmap PNG for one beat's representative flow field.

    Normalizes the magnitude field to 0-255 and applies ``cv2.COLORMAP_TURBO`` (matching the
    prototype's heatmap), upscaling to the hero width for legibility. Returns True on success.
    """
    try:
        import cv2  # noqa: PLC0415
        import numpy as np
    except ImportError:
        return False
    m = np.asarray(mag_field, dtype=np.float32)
    peak = float(m.max())
    if peak <= 1e-9:
        norm = np.zeros_like(m, dtype=np.uint8)
    else:
        norm = np.clip(m / peak * 255.0, 0, 255).astype(np.uint8)
    colored = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
    h, w = colored.shape[:2]
    nh = max(1, round(h * _HERO_WIDTH / w))
    colored = cv2.resize(colored, (_HERO_WIDTH, nh), interpolation=cv2.INTER_NEAREST)
    return bool(cv2.imwrite(str(out_path), colored))


def _partition_cuts(
    cuts: list[SceneCut],
    *,
    start_s: float,
    end_s: float,
) -> list[SceneCut]:
    """Return the proxy-wide cuts that fall inside ``[start_s, end_s)``, retimed to the beat.

    ``parse_scene_scores`` gives absolute proxy ``time_s`` (the scene-detect ran over the
    whole proxy once). For one beat we keep the cuts inside its window and re-base their
    ``time_s`` to be beat-relative, so the downstream ``rank_cuts``/``hero_cut`` contract
    (clip-relative times) is preserved and ``extract_frame_argv`` is fed ``start_s + cut.time_s``.
    """
    out: list[SceneCut] = []
    for c in cuts:
        if start_s <= c.time_s < end_s:
            out.append(SceneCut(time_s=c.time_s - start_s, score=c.score))
    return out


def _metrics_to_json(metrics) -> dict:
    return {
        "axis_aligned": _q(metrics.axis_aligned),
        "eased_energy_share": _q(metrics.eased_energy_share),
        "eased_events": int(metrics.eased_events),
        "motion_energy": _q(metrics.motion_energy),
        "mov_sat": _q(metrics.mov_sat),
        "mov_texture": _q(metrics.mov_texture),
        "n_frames": int(metrics.n_frames),
        "sparsity": _q(metrics.sparsity),
        "spatial_concentration": _q(metrics.spatial_concentration),
    }


def _capture_beat(
    *,
    proxy_path: Path,
    beat: BeatWindow,
    index: int,
    slug: str,
    out_dir: Path,
    work_dir: Path,
    proxy_cuts: list[SceneCut],
    max_frames: int,
    min_frames: int,
    frame_width: int,
    write_heatmap: bool,
    mag_field,
) -> dict | None:
    """Run the existing capture pipeline for one beat against the whole proxy.

    Partitions the proxy-wide scene cuts into the beat window, ranks them, extracts the
    hero + strip frames at absolute ``beat.start_s + cut.time_s``, optionally writes a flow
    heatmap, and returns the manifest record for the beat (or ``None`` on a capture failure,
    after printing the error to stderr).
    """
    beat_label = f"beat-{index:03d}-{_fmt_mmss(beat.start_s)}"
    hero_path = out_dir / f"{slug}-{beat_label}.png"
    strip_path = out_dir / f"{slug}-{beat_label}-strip.png"
    flow_path = out_dir / f"{slug}-{beat_label}-flow.png"

    window_cuts = _partition_cuts(proxy_cuts, start_s=beat.start_s, end_s=beat.end_s)
    beat_duration = max(beat.end_s - beat.start_s, 1e-3)
    chosen = rank_cuts(
        window_cuts,
        clip_duration_s=beat_duration,
        max_frames=max_frames,
        min_frames=min_frames,
    )

    frame_paths: list[Path] = []
    for i, cut in enumerate(chosen):
        frame_path = work_dir / f"{beat_label}_frame_{i:03d}.png"
        ext = _run(
            extract_frame_argv(
                clip_path=proxy_path,
                time_s=beat.start_s + cut.time_s,
                frame_width=frame_width,
                out_path=frame_path,
                fast_seek=True,
            )
        )
        if ext.returncode != 0 or not frame_path.exists():
            print(
                f"error: {beat_label}: frame extraction failed at "
                f"{beat.start_s + cut.time_s:g}s:\n{ext.stderr.strip()[-800:]}",
                file=sys.stderr,
            )
            return None
        frame_paths.append(frame_path)

    strip = _run(
        filmstrip_argv(frame_paths=frame_paths, out_path=strip_path, frame_width=frame_width)
    )
    if strip.returncode != 0:
        print(
            f"error: {beat_label}: film strip failed:\n{strip.stderr.strip()[-800:]}",
            file=sys.stderr,
        )
        return None

    hero = hero_cut(chosen)
    hero_extract = _run(
        extract_frame_argv(
            clip_path=proxy_path,
            time_s=beat.start_s + hero.time_s,
            frame_width=_HERO_WIDTH,
            out_path=hero_path,
            fast_seek=True,
        )
    )
    if hero_extract.returncode != 0 or not hero_path.exists():
        print(
            f"error: {beat_label}: hero frame failed:\n{hero_extract.stderr.strip()[-800:]}",
            file=sys.stderr,
        )
        return None

    flow_written = False
    if write_heatmap and mag_field is not None:
        flow_written = _write_heatmap(mag_field, flow_path)

    descriptor = describe(beat.metrics)
    record = {
        "index": index,
        "window": {
            "start_s": _q(beat.start_s),
            "end_s": _q(beat.end_s),
        },
        "gate_kind": beat.gate_kind,
        "score": _q(beat.score),
        "files": {
            "hero": hero_path.name,
            "strip": strip_path.name,
            "flow": flow_path.name if flow_written else None,
        },
        "metrics": _metrics_to_json(beat.metrics),
        "descriptor": {
            "energy": descriptor.energy,
            "cadence": descriptor.cadence,
            "spatial": descriptor.spatial,
        },
        "frame_times_abs_s": [_q(beat.start_s + c.time_s) for c in chosen],
    }
    return record


def _run_scan(args: argparse.Namespace) -> int:
    """The whole-video motion-graphics auto-scan workflow."""
    if args.min_frames < 1 or args.max_frames < args.min_frames:
        print(
            "error: require 1 <= --min-frames <= --max-frames "
            f"(got min={args.min_frames}, max={args.max_frames}).",
            file=sys.stderr,
        )
        return 2
    if args.flow_fps <= 0:
        print("error: --flow-fps must be > 0.", file=sys.stderr)
        return 2

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{args.slug}-scan.json"

    work_dir = Path(tempfile.mkdtemp(prefix="inspo-scan-"))
    cleanup = not args.keep_proxy
    try:
        # 1. Acquire ONE capped proxy of the WHOLE video: either reuse an existing
        # file (--from-proxy, e.g. the one a prior pace run cached) or download it
        # (no --download-sections).
        if args.from_proxy is not None:
            proxy_path = args.from_proxy
            if not proxy_path.is_file():
                print(
                    f"error: --from-proxy file not found: {proxy_path}",
                    file=sys.stderr,
                )
                return 2
            print(f"scan: reusing existing proxy {proxy_path} ...", file=sys.stderr)
        else:
            print(
                f"scan: downloading proxy (<= {args.max_height}p) ...", file=sys.stderr
            )
            dl = _run(
                ytdlp_download_argv(
                    url=args.url,
                    out_template=str(work_dir / "clip.%(ext)s"),
                    max_height=args.max_height,
                    prefer_avc=True,
                )
            )
            if dl.returncode != 0:
                print(
                    f"error: yt-dlp failed:\n{dl.stderr.strip()[-2000:]}",
                    file=sys.stderr,
                )
                return 1

            proxy_path = _find_clip(work_dir)
            if proxy_path is None:
                print("error: yt-dlp produced no proxy file.", file=sys.stderr)
                return 1

        proxy_duration = _ffprobe_duration(proxy_path)
        print(
            f"scan: proxy {proxy_path.name} ({proxy_duration:g}s); "
            f"computing DIS flow @ ~{args.flow_fps:g}fps ...",
            file=sys.stderr,
        )

        # 2. Stream the proxy through DIS optical flow (cv2 lazy-imported inside).
        try:
            fingerprints, cv2_version, mag_fields = _compute_fingerprints(
                proxy_path, flow_fps=args.flow_fps, keep_mag_fields=args.heatmap
            )
        except ImportError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        if proxy_duration <= 0.0 and fingerprints:
            proxy_duration = fingerprints[-1].t_s

        print(
            f"scan: {len(fingerprints)} flow samples; segmenting beats ...",
            file=sys.stderr,
        )

        # 3. Segment genuine motion-graphics beats (pure).
        beats = segment(
            fingerprints,
            min_beat_s=args.min_beat,
            merge_gap_s=args.merge_gap,
            pad_s=args.pad,
            max_beats=args.max_beats,
            floor_fn=adaptive_floor,
            video_duration_s=proxy_duration,
        )

        # 4. Scene-detect the WHOLE proxy once; cuts are partitioned per beat.
        proxy_cuts: list[SceneCut] = []
        if beats:
            print(
                f"scan: {len(beats)} beat(s); scene-detecting proxy ...",
                file=sys.stderr,
            )
            meta_path = work_dir / "scene-meta.txt"
            det = _run(scene_detect_argv(clip_path=proxy_path, meta_path=meta_path))
            if det.returncode != 0:
                print(
                    f"error: ffmpeg scene detection failed:\n{det.stderr.strip()[-2000:]}",
                    file=sys.stderr,
                )
                return 1
            meta_text = meta_path.read_text(encoding="utf-8") if meta_path.exists() else ""
            proxy_cuts = parse_scene_scores(meta_text + "\n" + det.stderr)

        # 5. Per-beat capture against the one proxy.
        #    Map each beat to a representative flow field (sample nearest its midpoint).
        beat_records: list[dict] = []
        for idx, beat in enumerate(beats, start=1):
            print(
                f"scan: capturing beat {idx}/{len(beats)} "
                f"@ {beat.start_s:g}-{beat.end_s:g}s ...",
                file=sys.stderr,
            )
            mag_field = None
            if args.heatmap and fingerprints:
                mid = (beat.start_s + beat.end_s) / 2.0
                best = min(
                    range(len(fingerprints)),
                    key=lambda i: abs(fingerprints[i].t_s - mid),
                )
                if best < len(mag_fields):
                    mag_field = mag_fields[best]
            record = _capture_beat(
                proxy_path=proxy_path,
                beat=beat,
                index=idx,
                slug=args.slug,
                out_dir=out_dir,
                work_dir=work_dir,
                proxy_cuts=proxy_cuts,
                max_frames=args.max_frames,
                min_frames=args.min_frames,
                frame_width=args.frame_width,
                write_heatmap=args.heatmap,
                mag_field=mag_field,
            )
            if record is None:
                return 1
            beat_records.append(record)

    finally:
        if cleanup:
            shutil.rmtree(work_dir, ignore_errors=True)

    if not cleanup:
        print(f"kept proxy + intermediate frames in {work_dir}", file=sys.stderr)

    # 6. Write the deterministic manifest (time-ordered beats; sorted keys; fixed floats).
    manifest = {
        "schema": "inspo-scan/1",
        "source_url": args.url,
        "slug": args.slug,
        "proxy_max_height": int(args.max_height),
        "proxy_duration_s": _q(proxy_duration),
        "flow": {
            "proc_width": _PROC_WIDTH,
            "flow_fps": _q(args.flow_fps),
            "opencv_version": cv2_version,
            "dis_preset": _DIS_PRESET_NAME,
            "dis_finest_scale": _DIS_FINEST_SCALE,
            "dis_gradient_iterations": _DIS_GRAD_ITERS,
            "dis_variational_iterations": _DIS_VAR_ITERS,
            "zero_eps": _ZERO_EPS,
            "mask_thresh": _MASK_THRESH,
            "grid": _GRID,
        },
        "gate_thresholds": {
            "eased_share_min": EASED_SHARE_MIN,
            "sparsity_min": SPARSITY_MIN,
            "concentration_min": CONCENTRATION_MIN,
            "mov_texture_max": MOV_TEXTURE_MAX,
        },
        "segmentation": {
            "min_beat_s": _q(args.min_beat),
            "merge_gap_s": _q(args.merge_gap),
            "pad_s": _q(args.pad),
            "max_beats": int(args.max_beats),
        },
        "n_flow_samples": len(fingerprints),
        "beats": beat_records,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"scan: wrote {len(beat_records)} beat(s) -> {manifest_path}",
        file=sys.stderr,
    )
    if not beat_records:
        print(
            "scan: no motion-graphics beats detected (manifest beats: []).",
            file=sys.stderr,
        )
    return 0


# --- pace-mode helpers (cv2 is lazy-imported inside _compute_scene_features only) ---


def _compute_scene_features(proxy_path: Path, *, sample_fps: float) -> list[FeatureRow]:
    """Stream the proxy through the low-fps HSV-delta pipe pass into ``FeatureRow``s.

    Same decode pattern as ``_compute_fingerprints`` (ffmpeg pipe, fixed-size 256px
    BGR frames, ``cv2.setNumThreads(1)``) but WITHOUT DIS flow — the soft-transition
    detector only needs two mean-abs HSV deltas per sample: vs the previous sample
    (``adj_delta``) and vs the sample ~1s earlier (``wide_delta``, a ring buffer of
    ``round(sample_fps)`` frames; ``0.0`` while it warms up). Deltas are normalized
    to 0-1 by /255 and pre-rounded (t to 3dp, values to 4dp) so platform jitter
    cannot flip a boundary downstream.

    Raises:
        ImportError: If ``cv2`` (opencv-python-headless) is not installed.
    """
    try:
        import cv2  # noqa: PLC0415  (lazy by design — keeps clip mode dep-free)
    except ImportError as exc:
        raise ImportError(
            "pace mode requires OpenCV. Install it with: "
            "uv pip install opencv-python-headless"
        ) from exc
    import numpy as np

    cv2.setNumThreads(1)

    src_w, src_h = _probe_dims(proxy_path)
    proc_w = _PROC_WIDTH
    proc_h = max(2, int(round(src_h * proc_w / src_w)))
    if proc_h % 2:
        proc_h += 1
    frame_bytes = proc_w * proc_h * 3

    wide_lag = max(1, round(sample_fps))

    proc = subprocess.Popen(
        ffmpeg_flow_decode_argv(
            clip_path=proxy_path, fps=sample_fps, width=proc_w, height=proc_h
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None

    rows: list[FeatureRow] = []
    history: deque = deque(maxlen=wide_lag)  # last wide_lag HSV frames, oldest first
    prev_hsv = None
    idx = -1
    try:
        while True:
            buf = _read_exact(proc.stdout, frame_bytes)
            if buf is None:
                break
            idx += 1
            small_bgr = np.frombuffer(buf, dtype=np.uint8).reshape(proc_h, proc_w, 3)
            hsv = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2HSV).astype(np.int16)
            if prev_hsv is None:
                history.append(hsv)
                prev_hsv = hsv
                continue

            t_s = idx / sample_fps
            adj = float(np.abs(hsv - prev_hsv).mean()) / 255.0
            if len(history) == wide_lag:
                wide = float(np.abs(hsv - history[0]).mean()) / 255.0
            else:
                wide = 0.0
            rows.append(
                FeatureRow(
                    t_s=round(t_s, _FP_TIME_DECIMALS),
                    adj_delta=_round_value(adj),
                    wide_delta=_round_value(wide),
                )
            )
            history.append(hsv)
            prev_hsv = hsv
    finally:
        proc.stdout.close()
        err = proc.stderr.read() if proc.stderr else b""
        rc = proc.wait()

    if not rows and rc != 0:
        raise RuntimeError(
            "ffmpeg feature decode failed:\n" + err.decode("utf-8", "replace")[-2000:]
        )
    return rows


def _find_pace_proxy(out_dir: Path) -> Path | None:
    """Return the cached proxy video in ``out_dir``, skipping subtitle/info sidecars."""
    sidecar_suffixes = {".json", ".json3", ".srv3", ".vtt"}
    candidates = sorted(
        p for p in out_dir.glob("proxy.*") if p.suffix not in sidecar_suffixes
    )
    return candidates[0] if candidates else None


def _pick_subtitle_track(
    out_dir: Path, *, langs: tuple[str, ...]
) -> tuple[Path, str] | None:
    """Pick the json3 subtitle track to analyze: preferred langs in order, else any.

    Only ``.json3`` qualifies — it is the sole format carrying word-level
    ``tOffsetMs`` timing; srv3/vtt fallbacks are left on disk unanalyzed. The
    "any" fallback is sorted-first for determinism.
    """
    for lang in langs:
        p = out_dir / f"proxy.{lang}.json3"
        if p.exists():
            return p, lang
    others = sorted(out_dir.glob("proxy.*.json3"))
    if others:
        p = others[0]
        return p, p.name[len("proxy.") : -len(".json3")]
    return None


def _load_info_json(path: Path) -> dict | None:
    """Read the yt-dlp info JSON; ``None`` when missing or unparseable (non-fatal)."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _pace_video_json(info: dict | None) -> dict:
    """Build the manifest's ``video`` block from the info JSON (all-null when absent)."""
    if info is None:
        return {"title": None, "channel": None, "upload_date": None, "duration_s": None}
    duration = info.get("duration")
    return {
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration_s": _q(float(duration)) if duration is not None else None,
    }


def _pace_scene_record(
    scene: SceneWindow, narration: SceneNarration | None, thumb: str | None
) -> dict:
    """Build one manifest scene record from already-computed values.

    The field names are the frozen ``inspo-pace/1`` contract — downstream copies
    them mechanically by exact name. Every float goes through ``_q``.
    """
    if narration is None:
        narration_json = None
    else:
        narration_json = {
            "word_count": int(narration.word_count),
            "words_per_s": _q(narration.words_per_s),
            "coverage": _q(narration.coverage),
            "first_word_offset_s": _q(narration.first_word_offset_s),
            "leading_silence_s": _q(narration.leading_silence_s),
            "trailing_silence_s": _q(narration.trailing_silence_s),
            "cut_in_pause": bool(narration.cut_in_pause),
            "pause_before_cut_s": _q(narration.pause_before_cut_s),
            "sentence_aligned": narration.sentence_aligned,
            "text": narration.text,
        }
    return {
        "index": int(scene.index),
        "window": {"start_s": _q(scene.start_s), "end_s": _q(scene.end_s)},
        "duration_s": _q(scene.end_s - scene.start_s),
        "boundary": {"kind": scene.boundary_kind, "score": _q(scene.boundary_score)},
        "narration": narration_json,
        "files": {"thumb": thumb},
    }


def _pace_aggregates_json(agg: dict) -> dict:
    """Quantize the ``transcript.aggregates`` dict for the manifest (frozen names)."""
    sd = agg["scene_duration_s"]
    return {
        "scene_count": int(agg["scene_count"]),
        "cuts_per_minute": _q(agg["cuts_per_minute"]),
        "soft_transition_count": int(agg["soft_transition_count"]),
        "scene_duration_s": {
            "median": _q(sd["median"]),
            "p25": _q(sd["p25"]),
            "p75": _q(sd["p75"]),
            "min": _q(sd["min"]),
            "max": _q(sd["max"]),
        },
        "longest_hold_s": _q(agg["longest_hold_s"]),
        "words_per_s_mean": _q(agg["words_per_s_mean"]),
        "pct_cuts_in_pause": _q(agg["pct_cuts_in_pause"]),
        "pct_sentence_aligned": _q(agg["pct_sentence_aligned"]),
    }


def _pace_manifest(
    *,
    url: str,
    slug: str,
    video: dict,
    max_height: int,
    proxy_duration_s: float,
    sample_fps: float,
    hard_floor: float,
    hard_ratio: float,
    hard_window: float,
    min_gap: float,
    soft_wide_min: float,
    soft_adj_max: float,
    soft_plateau: float,
    dedupe: float,
    subtitles: dict | None,
    scenes: list[SceneWindow],
    narrations: list[SceneNarration | None],
    thumbs: list[str | None],
    agg: dict,
) -> dict:
    """Assemble the full ``inspo-pace/1`` manifest from already-computed values.

    Pure assembly (no I/O) so the frozen field-name contract is testable without
    subprocesses. ``wide_baseline_s`` records the soft pass's actual ring-buffer
    lag in seconds (``round(sample_fps) / sample_fps``).
    """
    wide_lag = max(1, round(sample_fps))
    return {
        "schema": "inspo-pace/1",
        "source_url": url,
        "slug": slug,
        "video": video,
        "proxy": {"max_height": int(max_height), "duration_s": _q(proxy_duration_s)},
        "scene_detect": {
            "hard": {
                "abs_floor": _q(hard_floor),
                "ratio": _q(hard_ratio),
                "window_s": _q(hard_window),
                "min_gap_s": _q(min_gap),
            },
            "soft": {
                "sample_fps": _q(sample_fps),
                "proc_width": _PROC_WIDTH,
                "wide_baseline_s": _q(wide_lag / sample_fps),
                "wide_min": _q(soft_wide_min),
                "adj_max": _q(soft_adj_max),
                "min_plateau_s": _q(soft_plateau),
                "suppress_s": _q(_SOFT_SUPPRESS_S),
            },
            "dedupe_s": _q(dedupe),
        },
        "subtitles": subtitles,
        "scenes": [
            _pace_scene_record(scene, narration, thumb)
            for scene, narration, thumb in zip(scenes, narrations, thumbs, strict=True)
        ],
        "aggregates": _pace_aggregates_json(agg),
    }


def _fmt_md(value: float | None, decimals: int = 2) -> str:
    """Format an already-quantized manifest number for the md report (``-`` for null)."""
    if value is None:
        return "-"
    return f"{value:.{decimals}f}"


def _excerpt(text: str, max_words: int = 12) -> str:
    """First ``max_words`` words of a scene's text, pipe-escaped, for the md table."""
    words = text.split()
    if not words:
        return "-"
    head = " ".join(words[:max_words]).replace("|", "\\|")
    return head + ("…" if len(words) > max_words else "")


def _pace_markdown_report(manifest: dict) -> str:
    """Render the mechanical ``<slug>-pacing.md`` report from the manifest.

    Numbers only — no judgment prose. The Pacing: note is authored by a human (or
    Claude) at curation time, never by the tool.
    """
    video = manifest["video"]
    subs = manifest["subtitles"]
    agg = manifest["aggregates"]
    sd = agg["scene_duration_s"]

    lines = [
        f"# {manifest['slug']} — pacing report (mechanical)",
        "",
        f"- Source: {manifest['source_url']}",
        f"- Title: {video['title'] or '-'}",
        f"- Channel: {video['channel'] or '-'}",
        f"- Upload date: {video['upload_date'] or '-'}",
        f"- Proxy: <={manifest['proxy']['max_height']}p, "
        f"{_fmt_md(manifest['proxy']['duration_s'])}s",
    ]
    if subs is None:
        lines.append("- Subtitles: none")
    else:
        lines.append(
            f"- Subtitles: {subs['lang']} ({subs['track_kind']}, "
            f"word_level={subs['word_level']}, punctuated={subs['punctuated']}, "
            f"{subs['word_count']} words)"
        )
    lines += [
        "",
        "## Aggregates",
        "",
        f"- scene_count: {agg['scene_count']}",
        f"- cuts_per_minute: {_fmt_md(agg['cuts_per_minute'])}",
        f"- soft_transition_count: {agg['soft_transition_count']}",
        f"- scene_duration_s: median {_fmt_md(sd['median'])} · "
        f"p25 {_fmt_md(sd['p25'])} · p75 {_fmt_md(sd['p75'])} · "
        f"min {_fmt_md(sd['min'])} · max {_fmt_md(sd['max'])}",
        f"- longest_hold_s: {_fmt_md(agg['longest_hold_s'])}",
        f"- words_per_s_mean: {_fmt_md(agg['words_per_s_mean'])}",
        f"- pct_cuts_in_pause: {_fmt_md(agg['pct_cuts_in_pause'])}",
        f"- pct_sentence_aligned: {_fmt_md(agg['pct_sentence_aligned'])}",
        "",
        "## Scenes",
        "",
        f"Contact-sheet tiles are row-major, {_SHEET_ROW_LEN} per row, in the table's "
        "scene order (no on-image labels).",
        "",
        "| # | start | end | dur_s | boundary | score | words | wps | "
        "pause_before_s | ¶ | text |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for rec in manifest["scenes"]:
        nar = rec["narration"]
        if nar is None:
            words = wps = pause = para = text = "-"
        else:
            words = str(nar["word_count"])
            wps = _fmt_md(nar["words_per_s"])
            pause = _fmt_md(nar["pause_before_cut_s"])
            if nar["sentence_aligned"] is None:
                para = "-"
            else:
                para = "y" if nar["sentence_aligned"] else "n"
            text = _excerpt(nar["text"])
        score = rec["boundary"]["score"]
        lines.append(
            f"| {rec['index']} | {_fmt_md(rec['window']['start_s'])} | "
            f"{_fmt_md(rec['window']['end_s'])} | {_fmt_md(rec['duration_s'])} | "
            f"{rec['boundary']['kind']} | "
            f"{'-' if score is None else f'{score:.3f}'} | "
            f"{words} | {wps} | {pause} | {para} | {text} |"
        )
    return "\n".join(lines) + "\n"


def _run_pace(args: argparse.Namespace) -> int:
    """The whole-video scene-change + narration pacing workflow."""
    if args.sample_fps <= 0:
        print("error: --sample-fps must be > 0.", file=sys.stderr)
        return 2
    if args.thumb_width < 1:
        print("error: --thumb-width must be >= 1.", file=sys.stderr)
        return 2

    langs = tuple(lang for lang in args.langs.split(",") if lang)
    if not langs:
        print("error: --langs must name at least one language.", file=sys.stderr)
        return 2

    out_dir: Path = args.out if args.out is not None else DEFAULT_PACE_OUT_BASE / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{args.slug}-pace.json"
    report_path = out_dir / f"{args.slug}-pacing.md"
    info_path = out_dir / "proxy.info.json"

    work_dir = Path(tempfile.mkdtemp(prefix="inspo-pace-"))
    try:
        # 1. ONE yt-dlp call total (proxy + subtitles + info JSON together — bot-wall
        #    discipline), skipped entirely when the out-dir cache already has them.
        proxy_path = _find_pace_proxy(out_dir)
        cached = (
            proxy_path is not None
            and info_path.exists()
            and any(out_dir.glob("proxy.*.json3"))
        )
        if cached:
            print(
                f"pace: using cached proxy + subtitles + info in {out_dir} "
                "(skipping download)",
                file=sys.stderr,
            )
        else:
            print(f"pace: downloading proxy (<= {args.max_height}p) ...", file=sys.stderr)
            dl = _run(
                ytdlp_download_argv(
                    url=args.url,
                    out_template=str(out_dir / "proxy.%(ext)s"),
                    max_height=args.max_height,
                    prefer_avc=True,
                    subtitles_langs=langs,
                    write_info_json=True,
                )
            )
            if dl.returncode != 0:
                print(f"error: yt-dlp failed:\n{dl.stderr.strip()[-2000:]}", file=sys.stderr)
                return 1
            proxy_path = _find_pace_proxy(out_dir)
        if proxy_path is None:
            print("error: yt-dlp produced no proxy file.", file=sys.stderr)
            return 1

        # 2. Proxy duration anchors the scene tiling.
        proxy_duration = _ffprobe_duration(proxy_path)
        if proxy_duration <= 0.0:
            print(f"error: ffprobe read no duration from {proxy_path}.", file=sys.stderr)
            return 1

        # 3. Hard cuts: full-fps scene-score pass -> adaptive threshold.
        print(
            f"pace: proxy {proxy_path.name} ({proxy_duration:g}s); scene-scoring ...",
            file=sys.stderr,
        )
        meta_path = work_dir / "scene-meta.txt"
        det = _run(scene_detect_argv(clip_path=proxy_path, meta_path=meta_path))
        if det.returncode != 0:
            print(
                f"error: ffmpeg scene detection failed:\n{det.stderr.strip()[-2000:]}",
                file=sys.stderr,
            )
            return 1
        meta_text = meta_path.read_text(encoding="utf-8") if meta_path.exists() else ""
        score_series = [
            SceneCut(
                time_s=round(c.time_s, _FP_TIME_DECIMALS),
                score=_round_value(c.score),
            )
            for c in parse_scene_scores(meta_text + "\n" + det.stderr)
        ]
        hard = detect_hard_cuts(
            score_series,
            abs_floor=args.hard_floor,
            ratio=args.hard_ratio,
            window_s=args.hard_window,
            min_gap_s=args.min_gap,
        )

        # 4. Soft transitions: low-fps HSV pipe pass -> plateau detection.
        print(
            f"pace: {len(hard)} hard cut(s); HSV feature pass @ ~{args.sample_fps:g}fps ...",
            file=sys.stderr,
        )
        try:
            feature_rows = _compute_scene_features(proxy_path, sample_fps=args.sample_fps)
        except ImportError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        soft = detect_soft_transitions(
            feature_rows,
            wide_min=args.soft_wide_min,
            adj_max=args.soft_adj_max,
            min_plateau_s=args.soft_plateau,
            hard_cuts=hard,
            suppress_s=_SOFT_SUPPRESS_S,
        )

        # 5. Merge + tile the proxy into scenes.
        boundaries = merge_boundaries(
            hard, soft, dedupe_s=args.dedupe, duration_s=proxy_duration
        )
        scenes = build_scenes(boundaries, duration_s=proxy_duration)

        # 6. Transcript alignment (missing/unparseable subtitles degrade, never fail).
        info = _load_info_json(info_path)
        subtitles_json: dict | None = None
        narrations: list[SceneNarration | None] = [None] * len(scenes)
        subs_label = "none"
        track = _pick_subtitle_track(out_dir, langs=langs)
        if track is None:
            print("pace: no json3 subtitle track found; narration is null.", file=sys.stderr)
        else:
            track_path, lang = track
            text = track_path.read_text(encoding="utf-8")
            try:
                words = filter_non_speech(parse_json3(text))
            except ValueError as exc:
                print(
                    f"pace: warning: {track_path.name} is not parseable json3 ({exc}); "
                    "narration is null.",
                    file=sys.stderr,
                )
            else:
                manual_langs = info.get("subtitles") or {} if info else {}
                track_kind = "manual" if lang in manual_langs else "auto"
                subtitles_json = {
                    "lang": lang,
                    "track_kind": track_kind,
                    "source_format": "json3",
                    # Word-level timing shows up as per-seg tOffsetMs keys; cue-level
                    # (manual) tracks carry none at all.
                    "word_level": '"tOffsetMs"' in text,
                    "punctuated": punctuated_fraction(words) >= PUNCTUATED_MIN_FRACTION,
                    "word_count": len(words),
                }
                narrations = align_scenes(scenes, words)
                subs_label = f"{lang} ({track_kind})"

        agg = aggregates(scenes, narrations, duration_s=proxy_duration)

        # 7. Per-scene thumbnails + contact sheets (row-major, no on-image text).
        thumbs: list[str | None] = [None] * len(scenes)
        sheet_count = 0
        if not args.no_frames:
            print(f"pace: extracting {len(scenes)} scene thumb(s) ...", file=sys.stderr)
            thumb_dir = out_dir / f"{args.slug}-thumbs"
            thumb_dir.mkdir(parents=True, exist_ok=True)
            thumb_paths: list[Path] = []
            for scene in scenes:
                t = scene.start_s + min(_THUMB_INSET_S, (scene.end_s - scene.start_s) / 2)
                name = f"scene-{scene.index:03d}.png"
                thumb_path = thumb_dir / name
                ext = _run(
                    extract_frame_argv(
                        clip_path=proxy_path,
                        time_s=t,
                        frame_width=args.thumb_width,
                        out_path=thumb_path,
                        fast_seek=True,
                    )
                )
                if ext.returncode != 0 or not thumb_path.exists():
                    print(
                        f"error: scene {scene.index}: thumb extraction failed at "
                        f"{t:g}s:\n{ext.stderr.strip()[-800:]}",
                        file=sys.stderr,
                    )
                    return 1
                thumb_paths.append(thumb_path)
                thumbs[scene.index - 1] = f"{thumb_dir.name}/{name}"

            per_sheet = _SHEET_ROW_LEN * _SHEET_MAX_ROWS
            chunks = [
                thumb_paths[i : i + per_sheet]
                for i in range(0, len(thumb_paths), per_sheet)
            ]
            for sheet_idx, chunk in enumerate(chunks, start=1):
                sheet_path = out_dir / f"{args.slug}-scenes-sheet-{sheet_idx:03d}.png"
                sheet_tmp = work_dir / f"sheet-{sheet_idx:03d}"
                sheet_tmp.mkdir(parents=True, exist_ok=True)
                argvs, row_paths = contact_sheet_argvs(
                    frame_paths=chunk,
                    out_path=sheet_path,
                    row_len=_SHEET_ROW_LEN,
                    tmp_dir=sheet_tmp,
                )
                for argv in argvs:
                    sheet = _run(argv)
                    if sheet.returncode != 0:
                        print(
                            f"error: contact sheet {sheet_idx} (magick append) failed:\n"
                            f"{sheet.stderr.strip()[-800:]}",
                            file=sys.stderr,
                        )
                        return 1
                for row_path in row_paths:
                    Path(row_path).unlink(missing_ok=True)
                sheet_count += 1
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    # 8. Deterministic manifest + mechanical markdown report.
    manifest = _pace_manifest(
        url=args.url,
        slug=args.slug,
        video=_pace_video_json(info),
        max_height=args.max_height,
        proxy_duration_s=proxy_duration,
        sample_fps=args.sample_fps,
        hard_floor=args.hard_floor,
        hard_ratio=args.hard_ratio,
        hard_window=args.hard_window,
        min_gap=args.min_gap,
        soft_wide_min=args.soft_wide_min,
        soft_adj_max=args.soft_adj_max,
        soft_plateau=args.soft_plateau,
        dedupe=args.dedupe,
        subtitles=subtitles_json,
        scenes=scenes,
        narrations=narrations,
        thumbs=thumbs,
        agg=agg,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.write_text(_pace_markdown_report(manifest), encoding="utf-8")

    # 9. Mechanical stdout summary.
    agg_json = manifest["aggregates"]
    print(
        f"pace: {agg_json['scene_count']} scene(s), "
        f"{_fmt_md(agg_json['cuts_per_minute'])} cuts/min, "
        f"{agg_json['soft_transition_count']} soft transition(s) "
        f"over {_fmt_md(manifest['proxy']['duration_s'])}s"
    )
    print(f"pace: subtitles: {subs_label}")
    print(f"pace: manifest: {manifest_path}")
    print(f"pace: report: {report_path}")
    if args.no_frames:
        print("pace: frames skipped (--no-frames)")
    else:
        print(f"pace: thumbs: {out_dir / f'{args.slug}-thumbs'} ({sheet_count} sheet(s))")
    return 0


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    raw = _inject_clip_shim(raw)

    parser = _build_parser()
    args = parser.parse_args(raw)

    if not getattr(args, "_handler", None):
        parser.print_help(file=sys.stderr)
        return 2

    missing = _preflight()
    if missing:
        print(f"error: {missing}", file=sys.stderr)
        return 2

    handler = args._handler
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
