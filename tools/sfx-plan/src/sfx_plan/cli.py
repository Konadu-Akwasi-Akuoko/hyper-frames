"""CLI entry point for sfx-plan."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from sfx_plan.annotations import scan_annotations
from sfx_plan.bake import bake_sfx_mix
from sfx_plan.catalog import apply_overrides, load_catalog
from sfx_plan.emit import (
    CUE_MANIFEST_NAME,
    SFX_MIX_REL,
    ensure_mount,
    render_sfx_html,
    render_sfx_html_baked,
    stage_assets,
    write_cue_manifest,
)
from sfx_plan.errors import SfxPlanError
from sfx_plan.mounts import load_mount_offsets
from sfx_plan.plan import Cue, build_plan
from sfx_plan.validate import validate_plan


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-plan",
        description=(
            "Scan a HyperFrames video folder for data-sfx-* annotations, resolve "
            "via sfx-catalog, and emit compositions/sfx.html."
        ),
    )
    p.add_argument(
        "video_dir",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Path to the video folder (default: current directory).",
    )
    p.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Path to sfx-catalog.yml (default: walk up looking for sound-effects/sfx-catalog.yml).",
    )
    p.add_argument(
        "--sound-effects-root",
        type=Path,
        default=None,
        help="Path to the sound-effects/ folder (defaults to the catalog's parent).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Resolve and validate everything, but don't write sfx.html.",
    )
    p.add_argument(
        "--report", action="store_true",
        help="Print a per-cue plan table on stdout.",
    )
    p.add_argument(
        "--bake", action="store_true",
        help=(
            "FINALIZE: mix every cue into one audio/sfx-mix.mp3 (via ffmpeg) and emit "
            "a single <audio>, instead of the per-cue editing layer. Run LAST — a plain "
            "sfx-plan run reverts it. Requires ffmpeg."
        ),
    )
    p.add_argument(
        "--bake-format", choices=("mp3", "wav"), default="mp3",
        help="Baked mix codec (default mp3 @ 320k; wav = pcm_s16le).",
    )
    return p


_ROOT_TAG_RE = re.compile(r'<[a-zA-Z]+\b[^>]*\b(?:id|data-composition-id)="root"[^>]*>')


def _video_full_duration(video_dir: Path, *, fallback: float) -> float:
    """Full voiceover runtime for the sfx-layer mount, so late cues aren't clipped.

    Prefers transcript.json's `audio_duration_secs`, then the #root composition's
    `data-duration` in index.html; never returns less than `fallback` (the last
    cue's end), so the mount always spans every cue.
    """
    candidates: list[float] = [fallback]

    transcript = video_dir / "transcript.json"
    if transcript.exists():
        try:
            data = json.loads(transcript.read_text(encoding="utf-8"))
            dur = data.get("audio_duration_secs")
            if isinstance(dur, (int, float)) and dur > 0:
                candidates.append(float(dur))
        except (ValueError, OSError):
            pass

    index_html = video_dir / "index.html"
    if index_html.exists():
        try:
            tag = _ROOT_TAG_RE.search(index_html.read_text(encoding="utf-8"))
            if tag:
                dur_match = re.search(r'data-duration="([0-9.]+)"', tag.group(0))
                if dur_match:
                    candidates.append(float(dur_match.group(1)))
        except OSError:
            pass

    return max(candidates)


def _resolve_catalog_path(video_dir: Path, override: Path | None) -> Path:
    if override is not None:
        return override
    cur = video_dir.resolve()
    for _ in range(6):
        candidate = cur / "sound-effects" / "sfx-catalog.yml"
        if candidate.exists():
            return candidate
        cur = cur.parent
    return video_dir.resolve() / "sound-effects" / "sfx-catalog.yml"


def _print_report(cues: list[Cue], video_dir: Path) -> None:
    print(f"\nSFX PLAN — {video_dir.name}   {len(cues)} cues\n")
    for c in cues:
        clamp = " ⚠clamped" if c.clamped else ""
        mode = f"at-scene-ms({c.at_scene_ms})"
        print(f"  {c.data_start:>7.2f}s  mode={mode:<26} cue={c.cue:<10} "
              f"vol={c.volume:.2f}  src={c.src}{clamp}")


def _emit_baked(
    *,
    cues: list[Cue],
    sfx_html_path: Path,
    video_dir: Path,
    staged: dict[str, str],
    catalog: dict,
    mount_duration_s: float,
    bake_format: str,
) -> str:
    """Bake the mix, write the single-element sfx.html, and drop the cue manifest.

    Both the baked file and its single `<audio>` span `mount_duration_s` so late
    cues (and trailing silence) survive; the per-cue timing is preserved in
    `sfx.cues.json` for sfx-level and other per-cue consumers.
    """
    out_rel = f"audio/sfx-mix.{bake_format}"
    bake_sfx_mix(
        cues=cues,
        staged=staged,
        video_dir=video_dir,
        out_rel=out_rel,
        total_duration_s=mount_duration_s,
        fmt=bake_format,
    )
    mix_rel = SFX_MIX_REL if bake_format == "mp3" else f"../audio/sfx-mix.{bake_format}"
    sfx_html_path.write_text(
        render_sfx_html_baked(
            mix_rel=mix_rel,
            total_duration_s=mount_duration_s,
            catalog_sha=catalog.get("library_sha", ""),
            cue_count=len(cues),
        ),
        encoding="utf-8",
    )
    write_cue_manifest(
        cues=cues,
        path=sfx_html_path.parent / CUE_MANIFEST_NAME,
        total_duration_s=mount_duration_s,
    )
    return f"baked {out_rel} (1 element, {len(cues)} cues)"


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    video_dir: Path = args.video_dir

    catalog_path = _resolve_catalog_path(video_dir, args.catalog)
    sound_effects_root = args.sound_effects_root or catalog_path.parent

    try:
        catalog = load_catalog(catalog_path)
        overrides_path = video_dir / "sfx-overrides.yml"
        catalog, touched = apply_overrides(catalog, overrides_path)
        if touched:
            print(
                f"applied per-video overrides from sfx-overrides.yml "
                f"({touched} cue{'s' if touched != 1 else ''} touched)"
            )
        mount_offsets = load_mount_offsets(video_dir / "index.html")

        annotations = list(scan_annotations(video_dir))
        if not annotations:
            print("no data-sfx-* annotations found; nothing to emit.")
            return 0

        cues = build_plan(annotations, catalog=catalog, mount_offsets=mount_offsets)
        total_duration_s = float(max((c.data_start + c.duration_s for c in cues), default=0.0))
        warnings = validate_plan(cues, total_duration_s=total_duration_s)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)

    except SfxPlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.report:
        _print_report(cues, video_dir)

    if args.dry_run:
        print(f"dry-run: would write {len(cues)} cues to {video_dir / 'compositions' / 'sfx.html'}")
        return 0

    sfx_html_path = video_dir / "compositions" / "sfx.html"
    sfx_html_path.parent.mkdir(exist_ok=True)
    staged = stage_assets(cues, sound_effects_root=sound_effects_root, video_dir=video_dir)
    mount_duration_s = _video_full_duration(video_dir, fallback=total_duration_s)

    try:
        if args.bake:
            written = _emit_baked(
                cues=cues,
                sfx_html_path=sfx_html_path,
                video_dir=video_dir,
                staged=staged,
                catalog=catalog,
                mount_duration_s=mount_duration_s,
                bake_format=args.bake_format,
            )
        else:
            sfx_html_path.write_text(
                render_sfx_html(
                    cues=cues,
                    sfx_html_path=sfx_html_path,
                    video_dir=video_dir,
                    staged=staged,
                    catalog_sha=catalog.get("library_sha", ""),
                    total_duration_s=total_duration_s,
                ),
                encoding="utf-8",
            )
            written = f"{len(cues)} per-cue elements"
    except SfxPlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    mounted = ensure_mount(video_dir / "index.html", total_duration_s=mount_duration_s)
    note = " (mounted sfx-layer in index.html)" if mounted else ""
    print(f"{len(cues)} cues placed, {len(warnings)} warnings, wrote {sfx_html_path} [{written}]{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
