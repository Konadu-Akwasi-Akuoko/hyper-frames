"""CLI entry point for design-catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from design_catalog.core import ValidationError, build_catalog


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="design-catalog",
        description=(
            "Scan design-catalog/*/meta.json, validate every entry, "
            "and emit design-catalog/catalog.json."
        ),
    )
    p.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("design-catalog"),
        help="Path to the design-catalog/ library root (default: ./design-catalog).",
    )
    p.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output path for catalog.json (default: <root>/catalog.json).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate everything but do not write the output file.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root: Path = args.root
    out: Path = args.output or (root / "catalog.json")

    if not root.is_dir():
        print(f"error: catalog root '{root}' does not exist or is not a directory", file=sys.stderr)
        return 2

    try:
        catalog = build_catalog(root)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    n = len(catalog["entries"])
    print(f"{n} {'entry' if n == 1 else 'entries'} validated.")

    if not args.dry_run:
        out.write_text(json.dumps(catalog, indent=2) + "\n")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
