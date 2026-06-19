#!/usr/bin/env python3
"""Overlay a labeled coordinate grid on a thumbnail for exact replication.

When authoring a thumbnail by mimicking a reference, the hard part is matching
*where* things sit — the headline baseline, the face center, the stat chip, the
pointer endpoint. This tool stamps a readable measuring grid onto a reference
image so those positions can be read off in the SAME pixel space the thumbnail
templates place elements in (1280x720 for horizontal, 1080x1920 for vertical).

Three coordinate aids, all in one overlay:
  * a 4x4 (configurable) MAJOR grid of numbered cells (1..N, row-major) — the
    coarse "the face is in cell 8, the headline crosses cells 1-2" reference;
  * fine MINOR gridlines every --minor px for sub-cell precision;
  * pixel rulers along the top (x) and left (y) edges at every major line, so a
    position reads directly as (x, y) pixels you can paste into a template.

Deterministic: pure geometry from the image dimensions, no RNG/clock. Output is
written next to the input as ``<name>.grid.png`` unless --out is given.

Usage:
    python3 tools/thumbnail-inspo/grid.py REF.jpg [--out OUT.png]
            [--cols 4] [--rows 4] [--minor 80]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FONT = "/System/Library/Fonts/Monaco.ttf"  # single-file mono; magick-safe on this Mac
MAJOR_COLOR = "#00e5ff"   # cyan major lines / cell numbers
MINOR_COLOR = "#00e5ff55" # faint cyan minor lines
RULER_BG = "#000000cc"
LABEL_FILL = "#ffffff"
LABEL_HALO = "#000000"


def identify_dims(path: Path) -> tuple[int, int]:
    cp = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(path)],
        capture_output=True, text=True, check=True,
    )
    w, h = cp.stdout.strip().split()
    return int(w), int(h)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref", help="reference image to grid")
    ap.add_argument("--out", default="", help="output path (default <name>.grid.png)")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--minor", type=int, default=80,
                    help="minor gridline spacing in px (0 to disable)")
    args = ap.parse_args()

    ref = Path(args.ref)
    if not ref.exists():
        print(f"error: {ref} not found", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else ref.with_suffix(ref.suffix + ".grid.png")

    if not Path(FONT).exists():
        print(f"error: font {FONT} missing", file=sys.stderr)
        return 1

    w, h = identify_dims(ref)
    cols, rows = max(1, args.cols), max(1, args.rows)

    draw: list[str] = []

    # --- minor gridlines ---
    if args.minor > 0:
        draw += ["-strokewidth", "1", "-fill", "none", "-stroke", MINOR_COLOR]
        for x in range(args.minor, w, args.minor):
            draw += ["-draw", f"line {x},0 {x},{h}"]
        for y in range(args.minor, h, args.minor):
            draw += ["-draw", f"line 0,{y} {w},{y}"]

    # --- major gridlines ---
    major_xs = [round(i * w / cols) for i in range(cols + 1)]
    major_ys = [round(j * h / rows) for j in range(rows + 1)]
    draw += ["-strokewidth", "2", "-fill", "none", "-stroke", MAJOR_COLOR]
    for x in major_xs:
        draw += ["-draw", f"line {x},0 {x},{h}"]
    for y in major_ys:
        draw += ["-draw", f"line 0,{y} {w},{y}"]

    # --- numbered cells: bright cyan numeral with a black halo, top-left of each
    #     cell (centers collide with the busy artwork) ---
    cell_pt = max(22, round(min(w / cols, h / rows) * 0.26))
    draw += ["-font", FONT, "-pointsize", str(cell_pt), "-gravity", "NorthWest"]
    n = 0
    for r in range(rows):
        for c in range(cols):
            n += 1
            px = round(c * w / cols) + 8
            py = round(r * h / rows) + 6
            draw += ["-stroke", LABEL_HALO, "-strokewidth", "4", "-fill", LABEL_HALO,
                     "-annotate", f"+{px}+{py}", str(n)]
            draw += ["-stroke", "none", "-fill", MAJOR_COLOR,
                     "-annotate", f"+{px}+{py}", str(n)]

    # --- top ruler (x pixels) + left ruler (y pixels) ---
    draw += ["-font", FONT, "-pointsize", "17", "-gravity", "NorthWest"]

    def label(x: int, y: int, text: str) -> None:
        draw.extend(["-stroke", LABEL_HALO, "-strokewidth", "3", "-fill", LABEL_HALO,
                     "-annotate", f"+{x}+{y}", text])
        draw.extend(["-stroke", "none", "-fill", LABEL_FILL,
                     "-annotate", f"+{x}+{y}", text])

    for x in major_xs:
        lx = min(max(x + 3, 2), w - 46)
        label(lx, 3, f"x{x}")
    for y in major_ys:
        ly = min(max(y + 2, 2), h - 20)
        label(3, ly, f"y{y}")

    # translucent backing strips so rulers stay legible over busy art
    pre = ["magick", str(ref),
           "-fill", RULER_BG, "-stroke", "none",
           "-draw", f"rectangle 0,0 {w},22",
           "-draw", f"rectangle 0,0 46,{h}"]
    cmd = pre + draw + [str(out)]

    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        print(f"error: magick failed:\n{cp.stderr[-1500:]}", file=sys.stderr)
        return 1
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
