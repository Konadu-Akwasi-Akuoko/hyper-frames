"""image-prep CLI: background removal + house VFX for video-director asset boxes.

The video-director skill declares an asset box and lists what photo it wants; the
user supplies a raw file; this tool turns that raw file into a palette-consistent
cutout. Background removal makes a photo read as a cutout on the void; the VFX
presets give disparate sources one look.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from . import process


def main() -> None:
    p = argparse.ArgumentParser(prog="image-prep", description=__doc__)
    p.add_argument("input", type=Path, help="source image")
    p.add_argument("output", type=Path, help="treated PNG to write")
    p.add_argument("--remove-bg", action="store_true",
                   help="cut the subject out of its background (needs the 'bg' extra)")
    p.add_argument("--preset", action="append", default=[], metavar="NAME",
                   choices=list(process.PRESETS),
                   help=f"VFX preset, repeatable, applied in order: {', '.join(process.PRESETS)}")
    p.add_argument("--height", type=int, default=0,
                   help="scale to this pixel height (0 = keep source size)")
    p.add_argument("--bg", default=process.BG_DEFAULT, help="dark/background token (hex)")
    p.add_argument("--accent", default=process.ACCENT_DEFAULT, help="accent token (hex)")
    args = p.parse_args()

    img = Image.open(args.input)
    if args.remove_bg:
        img = process.remove_background(img)
    img = process.fit_height(img, args.height)
    for name in args.preset:
        img = process.PRESETS[name](img, bg=args.bg, accent=args.accent)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.output)
    print(f"wrote {args.output} ({img.width}x{img.height}, mode {img.mode})")


if __name__ == "__main__":
    main()
