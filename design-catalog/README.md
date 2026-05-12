# design-catalog

Browsable library of reusable CSS + motion effects extracted from the videos
in this repo. Sibling to `sound-effects/` and `tools/` — same shape: an
asset library at the root, a Python uv tool for the generated index, and a
Claude skill for guided authoring.

## Layout

```
design-catalog/
├── index.html              viewer entry (static)
├── viewer/
│   ├── styles.css
│   └── app.js              fetches catalog.json, renders grid + detail
├── catalog.json            GENERATED — never hand-edit
└── <slug>/
    ├── meta.json           name, tags, deps, source pointer
    ├── snippet.html        copy-paste payload (markup + <style>)
    ├── motion.js           companion motion kit (optional)
    └── preview.html        self-contained iframe demo
```

## Browse

The viewer uses `fetch()`, so it needs a real server (not `file://`):

```bash
cd design-catalog && npm start    # wraps `python3 -m http.server 8000`
# open http://localhost:8000/
```

(`npm start` is a thin alias — running `python3 -m http.server 8000` from
inside `design-catalog/` does exactly the same thing.)

Search the input, toggle tag chips, click a card to open the detail drawer
with a live preview and copy buttons:

- **Copy snippet** — raw `snippet.html` (or `motion.js` when on the Motion tab)
  to the clipboard.
- **Copy AI prompt** — a one-line directive to paste into a Claude session,
  e.g. `Reuse the rotating border beam from design-catalog/border-beam/. …`.

## Add an entry

The fastest path is the Claude skill:

> "add this to the design catalog" / "catalog this effect" — see
> `.claude/skills/design-catalog-add/SKILL.md`.

Manually:

1. Create `design-catalog/<kebab-slug>/`.
2. Drop in `meta.json`, `snippet.html`, optional `motion.js`, and a
   self-contained `preview.html`.
3. Regenerate the index:
   ```bash
   uv run --project tools/design-catalog design-catalog
   ```
4. Open the viewer and confirm the new card appears.

## meta.json schema

```json
{
  "slug": "border-beam",
  "name": "Rotating border beam",
  "description": "One-line summary.",
  "tags": ["border", "glow", "gradient"],
  "type": "animated",
  "dependencies": ["gsap"],
  "files": {
    "preview": "preview.html",
    "snippet": "snippet.html",
    "motion": "motion.js"
  },
  "source": {
    "video": "<video-folder-name>",
    "file": "<path within the video folder>",
    "css_lines": "393-429",
    "motion_lines": "984"
  },
  "created_at": "YYYY-MM-DD"
}
```

`type: "static"` is allowed for entries with no motion kit — omit
`files.motion` and set `dependencies: []`.

## Generator

`tools/design-catalog/` scans every `meta.json`, validates it, and writes
`catalog.json` next to this README. Validation errors are blocking — fix them
before browsing.
