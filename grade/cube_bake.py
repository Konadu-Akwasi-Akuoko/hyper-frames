#!/usr/bin/env python3
"""Bake an ffmpeg color-filter chain into an exact .cube 3D LUT.

Generates a neutral identity LUT grid as a 16-bit PPM, pipes it through the exact
ffmpeg `-vf` chain used at render time, reads the result back, and writes a
standard .cube file. Because ffmpeg itself applies the grade to the identity grid,
the LUT reproduces the grade with no math reimplementation.

Usage: cube_bake.py "<ffmpeg -vf string>" <out.cube> [grid_size]
"""
import subprocess
import sys
import struct

VF = sys.argv[1]
OUT = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 33

# Identity grid: red fastest, then green, then blue (the .cube ordering).
maxv = 65535
header = f"P6\n{N*N*N} 1\n{maxv}\n".encode()
body = bytearray()
for b in range(N):
    for g in range(N):
        for r in range(N):
            for c in (r, g, b):
                body += struct.pack(">H", round(c * maxv / (N - 1)))
identity = header + bytes(body)

# Pipe identity PPM through the grade chain; read back 16-bit RGB.
proc = subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error",
     "-f", "image2pipe", "-c:v", "ppm", "-i", "pipe:0",
     "-vf", VF, "-pix_fmt", "rgb48be", "-f", "rawvideo", "pipe:1"],
    input=identity, capture_output=True, check=True,
)
raw = proc.stdout
count = N * N * N
vals = struct.unpack(f">{count*3}H", raw[: count * 6])

with open(OUT, "w") as f:
    f.write(f"# Baked from ffmpeg chain by cube_bake.py\nLUT_3D_SIZE {N}\n")
    for i in range(count):
        r, g, b = vals[3 * i] / maxv, vals[3 * i + 1] / maxv, vals[3 * i + 2] / maxv
        f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")
print(f"wrote {OUT}  (LUT_3D_SIZE {N}, {count} entries)")
