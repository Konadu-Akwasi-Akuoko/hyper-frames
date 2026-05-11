# sfx-catalog

Scan `sound-effects/` and emit `sound-effects/sfx-catalog.yml` — per-asset metadata (duration, peak, LUFS, spectral character) and named cue recipes (`ui-tick`, `whoosh`, `boom`, `riser`, `pop`) used by `tools/sfx-plan`.

## Usage

```bash
uv run --project tools/sfx-catalog sfx-catalog
```

Flags: `--force` (ignore sha cache), `--dry-run`, `--report`.

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` for the schema.
