# image-prep

Background removal + house VFX presets for the `video-director` skill's **asset
boxes**. The skill places a full-height side cutout as a labeled placeholder and
lists the photo it wants; the user supplies a raw file; this tool turns that raw
file into a palette-consistent cutout that sits in `design.md`'s world.

It is the image analogue of `tools/cut-snap` — a small, deterministic uv project
the skill shells out to. See `.claude/skills/video-director/reference/assets-and-media.md`.

## Install

```bash
uv sync --project tools/image-prep            # VFX presets only (pillow + numpy)
uv sync --project tools/image-prep --extra bg # + background removal (rembg, ~larger)
```

Background removal pulls `rembg`/`onnxruntime` and downloads a model on first run,
so it is an optional extra; the VFX presets need only Pillow + NumPy.

## Usage

```bash
uv run --project tools/image-prep image-prep <input> <output.png> [options]
```

Options:

- `--remove-bg` — cut the subject out of its background (needs `--extra bg`). This
  is what makes a photo read as a cutout on the void rather than a pasted rectangle.
- `--preset NAME` — a VFX preset, **repeatable**, applied in order:
  - `grain` — deterministic film grain.
  - `duotone` — luminance mapped onto the `--bg`→`--accent` gradient (two-tone).
  - `halftone` — accent dots on the bg color, dot size ∝ local darkness.
  - `vintage` — warm two-tone + grain, an aged-print look.
- `--height N` — scale to N px tall, preserving aspect (0 = keep source).
- `--bg HEX` / `--accent HEX` — palette tokens (default `#0b0d12` / `#f7df1e` from
  `design.md`); override per-video.

### Example — a full-height emotion cutout

```bash
uv run --project tools/image-prep image-prep \
  videos/<slug>/assets/images/_raw/surprised-celebrity.jpg \
  videos/<slug>/assets/images/surprised-celebrity.png \
  --remove-bg --preset duotone --height 1080
```

The treated PNG is what the asset box swaps to.

## Layout

```
tools/image-prep/
├── README.md
├── pyproject.toml          # pillow + numpy; rembg behind the [bg] extra
└── src/image_prep/
    ├── __init__.py
    ├── cli.py              # arg parsing → process
    └── process.py          # remove_background, fit_height, grain/duotone/halftone/vintage, PRESETS
```

Determinism: grain uses a fixed seed, so the same input + flags always produce the
same output.
