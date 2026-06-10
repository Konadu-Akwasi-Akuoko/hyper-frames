"""Pure argv builders for yt-dlp, ffmpeg, ffprobe, and ImageMagick (+append).

Every function returns a ``list[str]`` argv suitable for ``subprocess.run`` with no
shell. Keeping them pure means the exact verified flag shape is asserted in tests
without invoking any binary. cli.py owns the actual subprocess calls.
"""
from __future__ import annotations

from pathlib import Path

# Highest-resolution video stream available, falling back to the best muxed stream.
# Crucially NOT constrained to mp4: YouTube serves 4K/1440p only in vp9/av1 (webm),
# never in mp4 (which caps at 1080p), so an [ext=mp4] filter silently ceilings us at
# 1080p. Audio is never used downstream (scene detection runs with -an and frame
# extraction is video-only), so we pull a video-only stream and skip the merge step
# entirely. ffmpeg reads webm/av1/vp9 transparently for frame extraction.
_YTDLP_FORMAT = "bv*/b"
# Make resolution the dominant sort key so yt-dlp prefers a 4K webm over the 1080p mp4
# even when both satisfy the selector; fps breaks ties (smoother motion reads better
# in the keyframe strip).
_YTDLP_SORT = "res,fps"


def _fmt_timestamp(seconds: float) -> str:
    """Format clip-relative seconds for a --download-sections range (decimal seconds)."""
    # yt-dlp accepts decimal seconds directly; keep it simple and lossless-ish.
    return f"{seconds:g}"


def ytdlp_download_argv(
    *,
    url: str,
    start_s: float | None = None,
    end_s: float | None = None,
    out_template: str,
    force_keyframes: bool = False,
    sleep_requests: int = 1,
    max_height: int | None = None,
    prefer_avc: bool = False,
    subtitles_langs: tuple[str, ...] | None = None,
    write_info_json: bool = False,
) -> list[str]:
    """Build the yt-dlp argv that downloads a clip (or whole video) at the chosen resolution.

    Selects the highest-resolution video stream (4K when present) via ``_YTDLP_FORMAT``
    plus ``-S`` resolution-first sorting — no mp4 constraint, no audio, no merge, because
    the downstream pipeline only extracts video frames and a 4K source supersamples into
    crisper downscaled stills.

    ``start_s``/``end_s`` (the existing clip-window args) drive the verified time-range
    syntax ``--download-sections "*START-END"`` (the ``*`` prefix is mandatory for a time
    range, otherwise the arg is a chapter-name regex). When *both* are omitted the caller
    wants the whole video, so ``--download-sections`` is dropped entirely.

    ``max_height`` bounds the downloaded resolution to ``<=max_height`` for the proxy used
    by whole-video scan mode (a capped proxy is many GB smaller than 4K of a long video and
    buys nothing the model sees). It keeps the same no-mp4/webm-friendly reasoning — the
    height filter applies to the video-only and muxed fallbacks alike
    (``bv*[height<=H]/b[height<=H]``) and ``-S res,fps`` is retained so yt-dlp still prefers
    the highest stream *within* the cap. When unset, the default top-resolution selector is
    used unchanged.

    ``prefer_avc`` prepends an ``h264`` codec preference to the sort so yt-dlp picks the
    H.264/AVC rendition over an equally-sized AV1 or VP9 one. Whole-video scan mode sets
    this because it software-decodes the *entire* proxy: AV1 has no hardware decode path in
    most ffmpeg/OpenCV builds, so an AV1 proxy is ~5-10x slower to walk frame-by-frame than
    the same resolution in H.264. Single-window ``clip`` mode leaves it off — there the
    decode is a few seconds either way and the best codec gives the crispest still.

    ``--sleep-requests`` guards against YouTube's per-request throttle on repeated runs.

    ``subtitles_langs`` opts in to fetching subtitle tracks in the SAME invocation
    (bot-wall discipline: one yt-dlp call total for pace mode, never a separate subtitle
    fetch). It appends the verified flag group ``--write-auto-subs --write-subs
    --sub-langs <comma-joined> --sub-format json3/srv3/vtt --sleep-subtitles 2`` —
    json3 first because it is the only format carrying word-level ``tOffsetMs`` timing.
    ``write_info_json`` appends ``--write-info-json`` so video metadata (title, channel,
    upload date, duration) lands beside the proxy. Both default off, keeping the existing
    clip/scan argv byte-identical.
    """
    argv = ["yt-dlp"]
    if start_s is not None and end_s is not None:
        section = f"*{_fmt_timestamp(start_s)}-{_fmt_timestamp(end_s)}"
        argv += [
            "--download-sections",
            section,
        ]
    if force_keyframes:
        argv.append("--force-keyframes-at-cuts")
    fmt = (
        f"bv*[height<={max_height}]/b[height<={max_height}]"
        if max_height is not None
        else _YTDLP_FORMAT
    )
    sort = f"{_YTDLP_SORT},vcodec:h264" if prefer_avc else _YTDLP_SORT
    argv += [
        "-f",
        fmt,
        "-S",
        sort,
        "--sleep-requests",
        str(sleep_requests),
        "-o",
        out_template,
    ]
    if subtitles_langs is not None:
        argv += [
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs",
            ",".join(subtitles_langs),
            "--sub-format",
            "json3/srv3/vtt",
            "--sleep-subtitles",
            "2",
        ]
    if write_info_json:
        argv.append("--write-info-json")
    argv.append(url)
    return argv


def ffprobe_dimensions_argv(*, clip_path: Path) -> list[str]:
    """Build the ffprobe argv that prints the first video stream's ``WIDTHxHEIGHT``.

    Used by scan mode to compute the exact pixel geometry of the downscaled flow frames
    *before* decoding, so the raw-video pipe can be read in fixed-size frame chunks.
    ``-of csv=p=0:s=x`` yields a bare ``1920x1080`` (no keys, ``x`` separator).
    """
    return [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(clip_path),
    ]


def ffmpeg_flow_decode_argv(
    *, clip_path: Path, fps: float, width: int, height: int
) -> list[str]:
    """Build the ffmpeg argv that streams a proxy as raw BGR frames for the flow pass.

    Does the three expensive steps in ffmpeg's optimized C (and on libdav1d's fast path for
    AV1) rather than in a Python ``VideoCapture`` loop: decimate to ``fps`` (``fps=`` filter),
    downscale to ``width x height`` (``scale=...:flags=area``, area-averaging like the
    prototype's ``INTER_AREA``), and emit packed ``bgr24`` ``rawvideo`` to stdout. The caller
    reads exact ``width*height*3``-byte frames off the pipe — so Python only ever touches tiny
    256px frames at the flow rate, never a full-resolution decode of every source frame.
    ``-an`` drops audio; ``-loglevel error`` keeps the pipe clean for binary framing.
    """
    vf = f"fps={fps:g},scale={width}:{height}:flags=area"
    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(clip_path),
        "-an",
        "-vf",
        vf,
        "-pix_fmt",
        "bgr24",
        "-f",
        "rawvideo",
        "-",
    ]


def scene_detect_argv(*, clip_path: Path, meta_path: Path) -> list[str]:
    """Build the ffmpeg argv that scores every frame's scene probability to ``meta_path``.

    Uses the verified ``select=gte(scene,0)`` approach with ``metadata=print:file=`` so
    every frame's ``lavfi.scene_score`` (0-1) lands in the metadata file. The score
    threshold is applied later by the ranker (``frames.rank_cuts``), not here, so a single
    detection pass can be re-thresholded without re-decoding. In subprocess list form the
    comma inside the filter expression needs no shell escaping.
    """
    vf = f"select=gte(scene\\,0),metadata=print:file={meta_path}"
    return [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(clip_path),
        "-vf",
        vf,
        "-an",
        "-f",
        "null",
        "-",
    ]


_FAST_SEEK_PREROLL_S = 1.0


def extract_frame_argv(
    *,
    clip_path: Path,
    time_s: float,
    frame_width: int,
    out_path: Path,
    fast_seek: bool = False,
) -> list[str]:
    """Build the ffmpeg argv that extracts one frame at ``time_s``, downscaled to width.

    Default (``fast_seek=False``): output-side ``-ss`` (after ``-i``) for frame accuracy —
    correct for ``clip`` mode, where the downloaded window is only a few seconds long so
    decoding from its start to ``time_s`` is cheap.

    ``fast_seek=True`` (whole-video scan): output-side seek would decode the *entire* proxy
    from zero to each absolute timestamp — for beats late in a 10-minute video that is ~13s
    of wasted decode per frame (minutes across all beats). Instead, input-side ``-ss`` jumps
    near the target keyframe (near-instant) and a small output-side ``-ss`` of
    ``_FAST_SEEK_PREROLL_S`` then decodes the last second to land on the exact frame —
    measured frame-identical (SSIM 1.0) to the output-side result at ~0.18s vs ~13s.

    ``scale=W:-1`` preserves aspect ratio. ``-y`` overwrites silently.
    """
    if fast_seek and time_s > _FAST_SEEK_PREROLL_S:
        seek = [
            "-ss",
            f"{time_s - _FAST_SEEK_PREROLL_S:g}",
            "-i",
            str(clip_path),
            "-ss",
            f"{_FAST_SEEK_PREROLL_S:g}",
        ]
    else:
        seek = ["-i", str(clip_path), "-ss", f"{time_s:g}"]
    return [
        "ffmpeg",
        "-hide_banner",
        "-y",
        *seek,
        "-frames:v",
        "1",
        "-vf",
        f"scale={frame_width}:-1",
        str(out_path),
    ]


def filmstrip_argv(*, frame_paths: list[Path], out_path: Path, frame_width: int) -> list[str]:
    """Build the ImageMagick argv that tiles frames into a single-row film strip.

    Uses ``magick … +append`` (horizontal concatenation), *not* ``magick montage``:
    montage prints a per-tile filename label that needs a configured font, and some
    ImageMagick builds (Homebrew without a default type config) abort with "unable to
    read font" before producing usable output. ``+append`` never touches the font
    machinery, so the strip renders deterministically in every environment. Each frame is
    resized to ``frame_width`` (height auto, aspect preserved — all frames share the
    source clip's aspect, so they line up) and given a thin separator border so tile
    boundaries stay legible. Frame paths are passed explicitly (already version-sorted by
    the caller) so ordering is deterministic.
    """
    argv = ["magick"]
    argv += [str(p) for p in frame_paths]
    argv += [
        "-resize",
        f"{frame_width}x",
        "-bordercolor",
        "#1a1a1a",
        "-border",
        "3",
        "-background",
        "none",
        "+append",
        str(out_path),
    ]
    return argv


def contact_sheet_argvs(
    *,
    frame_paths: list[Path],
    out_path: Path,
    row_len: int,
    tmp_dir: Path,
) -> tuple[list[list[str]], list[str]]:
    """Build the ImageMagick argvs that tile thumbnails into a row-major contact sheet.

    Returns ``(argvs, row_paths)``: the argv lists to run in order, plus the intermediate
    row PNG paths for the caller to delete afterwards. Rows are built with
    ``magick … +append`` (horizontal) and stacked with ``magick … -append`` (vertical) —
    NEVER ``magick montage`` and never ``-annotate``, both of which need a configured font
    that Homebrew ImageMagick builds can lack ("unable to read font" abort). Ordering is
    row-major by the caller-supplied ``frame_paths``; the accompanying report documents
    which scene each tile is, so no text is drawn on the sheet itself.

    A single row needs no stacking step: one ``+append`` writes straight to ``out_path``
    and ``row_paths`` is empty. A short final row is padded by ``-append``'s transparent
    ``-background none`` so the stack stays rectangular.
    """
    if not frame_paths:
        raise ValueError("frame_paths must be non-empty")
    if row_len < 1:
        raise ValueError("row_len must be >= 1")
    rows = [frame_paths[i : i + row_len] for i in range(0, len(frame_paths), row_len)]
    if len(rows) == 1:
        argv = ["magick", *(str(p) for p in rows[0]), "+append", str(out_path)]
        return [argv], []
    row_paths = [str(tmp_dir / f"row-{i:03d}.png") for i in range(len(rows))]
    argvs = [
        ["magick", *(str(p) for p in row), "+append", row_path]
        for row, row_path in zip(rows, row_paths)
    ]
    argvs.append(
        ["magick", *row_paths, "-background", "none", "-append", str(out_path)]
    )
    return argvs, row_paths
