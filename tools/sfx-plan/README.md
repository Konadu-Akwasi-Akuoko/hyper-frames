# sfx-plan

Scan a HyperFrames video folder for `data-sfx-*` annotations, resolve anchor words via `narration-map.json`, pick files deterministically from `sound-effects/sfx-catalog.yml`, and emit `compositions/sfx.html` as a native HyperFrames audio sub-composition.

## Usage

From inside a video folder (after the `sfx-author` skill has annotated the HTML):

```bash
uv run --project ../../tools/sfx-plan sfx-plan
```

Flags: `--dry-run` (don't write), `--report` (print a plan table).

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` for the data contract.
