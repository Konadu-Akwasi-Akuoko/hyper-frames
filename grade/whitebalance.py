#!/usr/bin/env python3
"""Estimate effective scene white balance from near-neutral pixels.

iPhone bakes WB into video, so there is no Kelvin tag to read. Instead: collect
the genuinely low-saturation pixels (surfaces that *should* be gray), average them
across mid luminance, and report the cast. A warm cast -> R>B; green/magenta tint
-> G vs (R+B)/2. Also prints the per-channel gain needed to neutralize it.
"""
import subprocess
import sys
import re
from statistics import mean

HEX = re.compile(r"#([0-9A-Fa-f]{6})")


def load(path, size=200):
    out = subprocess.run(
        ["magick", path, "-resize", f"{size}x{size}", "-colorspace", "sRGB", "-depth", "8", "txt:-"],
        capture_output=True, text=True, check=True).stdout
    px = []
    for line in out.splitlines():
        m = HEX.search(line)
        if m:
            h = m.group(1)
            px.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))
    return px


def sat(p):
    mx, mn = max(p), min(p)
    return 0 if mx == 0 else (mx - mn) / mx


px = load(sys.argv[1])
# near-neutral mid-tones: low saturation, mid luminance (avoid blown/black)
neutral = [p for p in px if sat(p) < 0.12 and 40 < (0.299*p[0]+0.587*p[1]+0.114*p[2]) < 220]
if len(neutral) < 20:
    neutral = [p for p in px if sat(p) < 0.18 and 30 < (0.299*p[0]+0.587*p[1]+0.114*p[2]) < 230]
r = mean(p[0] for p in neutral); g = mean(p[1] for p in neutral); b = mean(p[2] for p in neutral)
gray = (r + g + b) / 3
print(f"neutral pixels found: {len(neutral)} / {len(px)}")
print(f"avg neutral RGB:  R{r:.1f}  G{g:.1f}  B{b:.1f}   (gray={gray:.1f})")
print(f"cast:  warm/cool (R-B) = {r-b:+.1f}   green/magenta (G-(R+B)/2) = {g-(r+b)/2:+.1f}")
wb = "WARM (orange)" if r - b > 4 else ("COOL (blue)" if r - b < -4 else "neutral")
tint = "GREEN" if g - (r+b)/2 > 3 else ("MAGENTA" if g - (r+b)/2 < -3 else "neutral")
print(f"=> temperature cast: {wb}   tint cast: {tint}")
print(f"to neutralize, multiply channels by:  R*{gray/r:.3f}  G*{gray/g:.3f}  B*{gray/b:.3f}")
