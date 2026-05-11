"""CLI entry point for sfx-catalog."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

from sfx_catalog.catalog import build_catalog, dump_yaml, load_yaml
from sfx_catalog.core import Catalog


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-catalog",
        description=(
            "Scan a sound-effects library and emit sfx-catalog.yml — per-asset "
            "metadata + named cue recipes for the HyperFrames SFX pipeline."
        ),
    )
    p.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("sound-effects"),
        help="Path to the sound-effects/ library root (default: ./sound-effects).",
    )
    p.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output path for sfx-catalog.yml (default: <root>/sfx-catalog.yml).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Ignore sha cache; re-measure every asset.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Measure everything but do not write the output file.",
    )
    p.add_argument(
        "--report",
        action="store_true",
        help="Print a per-role / per-brightness asset count.",
    )
    return p


def _report(cat: Catalog) -> str:
    role_counter: Counter[str] = Counter(e.auto_role for e in cat.assets.values())
    brightness_counter: Counter[str] = Counter(e.brightness for e in cat.assets.values())
    lib_counter: Counter[str] = Counter(e.library for e in cat.assets.values())
    lines = ["By role:"]
    for k, v in role_counter.most_common():
        lines.append(f"  {k:<12} {v}")
    lines.append("By brightness:")
    for k, v in brightness_counter.most_common():
        lines.append(f"  {k:<12} {v}")
    lines.append("By library:")
    for k, v in lib_counter.most_common():
        lines.append(f"  {k:<24} {v}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root: Path = args.root
    out: Path = args.output or (root / "sfx-catalog.yml")

    previous: Catalog | None = None
    if out.exists() and not args.force:
        try:
            previous = load_yaml(out)
        except (ValueError, KeyError) as exc:
            print(f"warning: ignoring existing catalog ({exc}); rebuilding from scratch.", file=sys.stderr)

    cat = build_catalog(root, previous=previous)
    print(f"{len(cat.assets)} assets, {len(cat.cues)} cues  (library_sha={cat.library_sha[:12]})")
    if args.report:
        print(_report(cat))
    if not args.dry_run:
        dump_yaml(cat, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
