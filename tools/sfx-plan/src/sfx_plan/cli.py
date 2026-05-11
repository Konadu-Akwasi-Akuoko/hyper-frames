"""CLI entry point for sfx-plan."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sfx_plan.annotations import scan_annotations
from sfx_plan.catalog import load_catalog
from sfx_plan.emit import ensure_mount, render_sfx_html
from sfx_plan.errors import SfxPlanError
from sfx_plan.narration import load_narration_map
from sfx_plan.plan import Cue, build_plan
from sfx_plan.validate import validate_plan


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-plan",
        description=(
            "Scan a HyperFrames video folder for data-sfx-* annotations, resolve "
            "via narration-map and sfx-catalog, and emit compositions/sfx.html."
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
    return p


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
        print(f"  {c.data_start:>7.2f}s  anchor={c.anchor!r:<20} cue={c.cue:<8} "
              f"vol={c.volume:.2f}  src={c.src}{clamp}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    video_dir: Path = args.video_dir

    catalog_path = _resolve_catalog_path(video_dir, args.catalog)
    sound_effects_root = args.sound_effects_root or catalog_path.parent

    try:
        catalog = load_catalog(catalog_path)
        nm_path = video_dir / "narration-map.json"
        nm = load_narration_map(nm_path)

        annotations = list(scan_annotations(video_dir))
        if not annotations:
            print("no data-sfx-* annotations found; nothing to emit.")
            return 0

        cues = build_plan(annotations, nm=nm, catalog=catalog)
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
    sfx_html_path.write_text(
        render_sfx_html(
            cues=cues,
            sfx_html_path=sfx_html_path,
            sound_effects_root=sound_effects_root,
            catalog_sha=catalog.get("library_sha", ""),
            total_duration_s=total_duration_s,
        ),
        encoding="utf-8",
    )
    mounted = ensure_mount(video_dir / "index.html")
    note = " (mounted sfx-layer in index.html)" if mounted else ""
    print(f"{len(cues)} cues placed, {len(warnings)} warnings, wrote {sfx_html_path}{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
