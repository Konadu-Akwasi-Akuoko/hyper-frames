"""Image treatment for video-director asset boxes.

The video-director skill places real photos/clips as full-height side cutouts.
Raw sources clash; these functions normalize them — optional background removal
(rembg) plus VFX presets that read the project palette so a supplied photo lands
in `design.md`'s world. Deterministic: the grain uses a fixed seed, so the same
input always yields the same output (no `Math.random` equivalent leaks in).

The exported surface is `remove_background`, `fit_height`, the four VFX functions
(`grain`, `duotone`, `halftone`, `vintage`), and the `PRESETS` registry the CLI
applies by name.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageOps

# design.md tokens — overridable from the CLI.
BG_DEFAULT = "#0b0d12"
ACCENT_DEFAULT = "#f7df1e"

_GRAIN_SEED = 1729


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def _split_alpha(img: Image.Image) -> tuple[Image.Image, Image.Image | None]:
    if img.mode == "RGBA":
        return img.convert("RGB"), img.getchannel("A")
    return img.convert("RGB"), None


def _merge_alpha(rgb: Image.Image, alpha: Image.Image | None) -> Image.Image:
    if alpha is None:
        return rgb
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def remove_background(img: Image.Image) -> Image.Image:
    """Cut the subject out of its background, returning RGBA.

    Requires the optional `bg` extra (`uv sync --extra bg`), which pulls rembg +
    onnxruntime and downloads a model on first run. Imported lazily so VFX-only
    runs don't need it.
    """
    try:
        from rembg import remove
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "background removal needs the 'bg' extra: "
            "uv sync --project tools/image-prep --extra bg"
        ) from exc
    return remove(img.convert("RGBA"))


def fit_height(img: Image.Image, height: int) -> Image.Image:
    """Scale `img` to `height` pixels tall, preserving aspect ratio (0 = unchanged)."""
    if height <= 0 or img.height == height:
        return img
    width = round(img.width * height / img.height)
    return img.resize((width, height), Image.LANCZOS)


def grain(img: Image.Image, bg: str = BG_DEFAULT, accent: str = ACCENT_DEFAULT,
          amount: float = 0.10) -> Image.Image:
    """Overlay deterministic film grain. `amount` = noise std as a fraction of 255."""
    rgb, alpha = _split_alpha(img)
    arr = np.asarray(rgb).astype(np.float32)
    rng = np.random.default_rng(_GRAIN_SEED)
    noise = rng.normal(0.0, amount * 255.0, arr.shape[:2])[..., None]
    out = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return _merge_alpha(Image.fromarray(out, "RGB"), alpha)


def duotone(img: Image.Image, bg: str = BG_DEFAULT, accent: str = ACCENT_DEFAULT) -> Image.Image:
    """Map luminance onto a `bg`→`accent` gradient (two-tone grade)."""
    rgb, alpha = _split_alpha(img)
    lum = np.asarray(ImageOps.grayscale(rgb)).astype(np.float32) / 255.0
    dark = np.array(_hex_to_rgb(bg), np.float32)
    light = np.array(_hex_to_rgb(accent), np.float32)
    out = (dark + (light - dark) * lum[..., None]).clip(0, 255).astype(np.uint8)
    return _merge_alpha(Image.fromarray(out, "RGB"), alpha)


def halftone(img: Image.Image, bg: str = BG_DEFAULT, accent: str = ACCENT_DEFAULT,
             cell: int = 6) -> Image.Image:
    """Render the image as accent dots on the bg color, dot size ∝ local darkness."""
    rgb, alpha = _split_alpha(img)
    gray = np.asarray(ImageOps.grayscale(rgb)).astype(np.float32)
    h, w = gray.shape
    fg_rgb, bg_rgb = _hex_to_rgb(accent), _hex_to_rgb(bg)
    out = Image.new("RGB", (w, h), bg_rgb)
    draw = ImageDraw.Draw(out)
    half = cell / 2.0
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            block = gray[y : y + cell, x : x + cell]
            darkness = 1.0 - float(block.mean()) / 255.0
            r = darkness * half * 1.45
            if r > 0.25:
                cx, cy = x + half, y + half
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fg_rgb)
    return _merge_alpha(out, alpha)


def vintage(img: Image.Image, bg: str = BG_DEFAULT, accent: str = ACCENT_DEFAULT) -> Image.Image:
    """Warm two-tone + grain: an aged, faded-print look."""
    out = duotone(img, bg="#16110a", accent="#efe3c8")
    return grain(out, amount=0.08)


PRESETS: dict[str, Callable[..., Image.Image]] = {
    "grain": grain,
    "duotone": duotone,
    "halftone": halftone,
    "vintage": vintage,
}
