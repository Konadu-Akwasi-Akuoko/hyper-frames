"""CLI entry point for inspo-ingest.

Orchestration only: this module owns every subprocess call (yt-dlp, ffmpeg, ffprobe,
magick +append) and is the *sole* owner of ``cv2``. All parsing, ranking, argv
construction, and the pure motion-graphics detection math live in the ``frames``,
``strip``, and ``motion`` modules so the decision logic stays testable without binaries.

Two subcommands:

* ``clip`` — the original per-window capture (full-resolution download, scene-detect,
  rank, film-strip + hero, print a stub). Unchanged behavior.
* ``scan`` — the whole-video motion-graphics auto-scan: download ONE capped proxy,
  stream it through DIS optical flow into a ``FlowFingerprint`` time series, segment
  genuine animation beats (``motion.segment``), and for each beat run the existing
  capture pipeline against the one proxy, then write per-beat files + a deterministic
  ``<slug>-scan.json`` manifest.

``cv2`` is **lazy-imported inside the scan codepath only** (never at module top), so
importing this module for ``clip`` mode or for the pure test suite pulls zero
third-party deps.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
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
from inspo_ingest.strip import (
    extract_frame_argv,
    ffmpeg_flow_decode_argv,
    ffprobe_dimensions_argv,
    filmstrip_argv,
    scene_detect_argv,
    ytdlp_download_argv,
)

DEFAULT_OUT = Path("/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/motionGraphicsInspo")

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
    p.set_defaults(_handler=_run_scan)
    return p


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="inspo-ingest",
        description=(
            "Ingest motion-graphics reference from YouTube. 'clip' captures a single "
            "window; 'scan' auto-detects animation beats across a whole video via "
            "DIS optical flow."
        ),
    )
    sub = p.add_subparsers(dest="command")
    _build_clip_parser(sub)
    _build_scan_parser(sub)
    return p


_KNOWN_SUBCOMMANDS = frozenset({"clip", "scan"})


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
        # 1. Download ONE capped proxy of the WHOLE video (no --download-sections).
        print(f"scan: downloading proxy (<= {args.max_height}p) ...", file=sys.stderr)
        dl = _run(
            ytdlp_download_argv(
                url=args.url,
                out_template=str(work_dir / "clip.%(ext)s"),
                max_height=args.max_height,
                prefer_avc=True,
            )
        )
        if dl.returncode != 0:
            print(f"error: yt-dlp failed:\n{dl.stderr.strip()[-2000:]}", file=sys.stderr)
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
