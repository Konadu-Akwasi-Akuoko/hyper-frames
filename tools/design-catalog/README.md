# tools/design-catalog

Scans `design-catalog/*/meta.json`, validates each entry against the schema,
and writes `design-catalog/catalog.json` (the index consumed by the static
viewer at `design-catalog/index.html`).

Single-responsibility CLI — no asset processing, no thumbnail generation.

## Run

From the repo root:

```bash
uv run --project tools/design-catalog design-catalog
```

Options:

```bash
uv run --project tools/design-catalog design-catalog --dry-run     # validate only
uv run --project tools/design-catalog design-catalog -o /tmp/cat.json
uv run --project tools/design-catalog design-catalog path/to/library
```

Validation errors are blocking and reported per-file. Fix them and re-run
before opening the viewer.

## Schema

See `design-catalog/README.md` for the `meta.json` shape. The validator checks:

- All required top-level fields are present (`slug`, `name`, `description`,
  `tags`, `type`, `dependencies`, `files`).
- `slug` matches the folder name.
- `type` is one of `animated` | `static`.
- `tags` and `dependencies` are lists of strings.
- `files.preview` and `files.snippet` exist on disk.
- `type=animated` entries declare `files.motion`; `type=static` entries do not.
- Every path under `files.*` resolves to an actual file.
