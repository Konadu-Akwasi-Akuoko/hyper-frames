#!/usr/bin/env python3
"""Dependency-free color-signature analyzer.

Reads an image via ImageMagick `txt:` dump (sRGB 0-255), then reports per-channel
statistics split by luminance band (shadow / mid / highlight) plus overall
saturation. Used to characterize a reference look and the tone-mapped source so a
match grade can target real numbers instead of guesses.
"""
import subprocess
import sys
import re
from statistics import mean, pstdev

HEX = re.compile(r"#([0-9A-Fa-f]{6})")


def load_rgb(path: str, size: int = 120) -> list[tuple[int, int, int]]:
    out = subprocess.run(
        ["magick", path, "-resize", f"{size}x{size}", "-colorspace", "sRGB", "-depth", "8", "txt:-"],
        capture_output=True, text=True, check=True,
    ).stdout
    px = []
    for line in out.splitlines():
        m = HEX.search(line)
        if m:
            h = m.group(1)
            px.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))
    return px


def luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.4152 * p[2]


def stats(px):
    r = [p[0] for p in px]; g = [p[1] for p in px]; b = [p[2] for p in px]
    return (mean(r), mean(g), mean(b), pstdev(r), pstdev(g), pstdev(b))


def saturation(px):
    sats = []
    for rr, gg, bb in px:
        mx, mn = max(rr, gg, bb), min(rr, gg, bb)
        sats.append(0 if mx == 0 else (mx - mn) / mx)
    return mean(sats)


def report(path):
    px = load_rgb(path)
    lum = [(p, luma(p)) for p in px]
    lum.sort(key=lambda x: x[1])
    n = len(lum)
    sh = [p for p, _ in lum[: n // 3]]
    mid = [p for p, _ in lum[n // 3 : 2 * n // 3]]
    hi = [p for p, _ in lum[2 * n // 3 :]]
    allp = [p for p, _ in lum]
    print(f"\n=== {path} ===")
    print(f"pixels sampled: {n}")
    mr, mg, mb, sr, sg, sb = stats(allp)
    print(f"OVERALL  mean R{mr:6.1f} G{mg:6.1f} B{mb:6.1f}   std R{sr:5.1f} G{sg:5.1f} B{sb:5.1f}")
    print(f"saturation(mean): {saturation(allp):.3f}")
    for name, band in (("SHADOW", sh), ("MID   ", mid), ("HIGHL ", hi)):
        br, bg, bb_, *_ = stats(band)
        # tint = how far each channel sits from the band's gray average
        avg = (br + bg + bb_) / 3
        print(f"{name}  R{br:6.1f} G{bg:6.1f} B{bb_:6.1f}   tint dR{br-avg:+5.1f} dG{bg-avg:+5.1f} dB{bb_-avg:+5.1f}")
    # black / white points
    lo, hi_ = lum[0][1], lum[-1][1]
    print(f"black point luma ~{lo:.0f}/255   white point luma ~{hi_:.0f}/255")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
