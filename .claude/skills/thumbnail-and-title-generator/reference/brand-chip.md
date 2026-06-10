# Brand chip — the optional per-topic stamp

In the Specimen signature the **face is the subject** and the headline names the
topic. The old large topic-icon — the line-icon that named the topic statically
on every variant — is **retired**: with a bled reaction still carrying the
emotion and a 2-tone headline carrying the claim, a second large topic glyph is
clutter, and the corpus's clearest losers were the busy icon-swarm pileups.

What remains is one small, optional element: a **brand chip** (`.chip`). It is
not the topic-namer the icon was — the headline does that. It is a small corner
stamp for the narrow case where the topic *is* a nameable brand. **Most
thumbnails need no chip.** Default to omitting it; add one only when it earns its
place.

## When to include a chip

Include a chip only when **the topic IS a nameable brand** — JS, React, Docker,
Postgres, Kubernetes, Python, Rust — and that brand is the explicit subject of
the video. The chip then doubles as a search-recognizable mark: a viewer scanning
the feed for "Postgres" registers the chip before they read the headline.

Omit the chip when:

- The topic is **generic or conceptual** ("compression," "rendering," "why text
  is hard"). There is no brand to stamp; a generic glyph would re-introduce the
  retired topic-icon clutter.
- The brand is **mentioned but not the subject** ("building CI pipelines" that
  happens to use Jenkins). The chip is for brand-as-subject, not brand-as-aside.
- The thumbnail is already busy — a strong face plus a long headline plus an
  annotation leaves no calm corner. The chip is the first thing to cut.

If you are unsure whether a topic qualifies, **leave the chip off.** The brand
identity lives in base + mono tell + layout + pointer; the chip is a nicety, not
a load-bearing part of the silhouette.

## Coloring the chip

The chip is the **only place native-color brand identity enters** the thumbnail.
Set its colors per topic by overriding two CSS variables on the `.chip` element:

| Variable | Role |
|---|---|
| `--chip-bg` | chip background fill |
| `--chip-ink` | glyph / label color on the chip |

Example — a JavaScript chip in JS yellow:

```html
<div class="chip" style="--chip-bg: #f7df1e; --chip-ink: #0b0d12">JS</div>
```

Common brand fills: JS `#f7df1e` (ink `#0b0d12`), React `#61dafb`, Docker
`#2496ed`, Postgres `#336791`, Python `#3776ab`, Rust `#dea584`. Use the brand's
canonical hue; the chip's whole value is recognition, so do not recolor it to the
accent.

### Keep the chip distinct from the accent

The chip must not fight `var(--accent)`. The navy/coral study scored an
amber-accent-on-yellow-chip pairing **3/10** — both hot yellows, so the accent
melted into the chip and neither read. Rule: when the chip fill is close in hue
to the variant's accent, **change the accent**, not the chip. Pick an `acc-*`
hue that contrasts the chip (e.g. a JS-yellow chip pairs cleanly with
`acc-violet`, `acc-cyan`, or `acc-slate`, never `acc-amber` or `acc-lime`).

## Keep it small and non-colliding

The chip is a stamp, never a headline element.

- **Small.** A corner badge, not a focal block. It confirms the topic; it does
  not compete with the face or the punch row for attention.
- **Placed via the coordinate grid, NOT inside a `thumbnail-row`.** The chip is
  absolutely positioned by its own `left`/`top` (read the numbered grid overlay
  via `?grid` to land it), or sits beside the headline in the layout. It is
  **never** a `<span class="thumbnail-row">` and never an inner span of a row —
  the headline rows are reserved for the 2-tone treatment and downstream skills
  parse them (create-srt `localize_thumbnails.py` reads `thumbnail-row`; the
  accent is a ROW class, never an inner span). A chip inside a row breaks both
  the layout and the contract.
- **Non-colliding.** Park it in a quiet corner or margin. It must not touch the
  face cutout, cross an annotation stroke, or sit under a headline row. Verify
  against the grid before rendering, the same as any annotation endpoint.

## The real-logo brand exception

For a chip that carries an actual brand mark instead of a text abbreviation, put
a small SVG logo **inside** the `.chip`. Use the `simple-icons` (monochrome
silhouettes) or `logos` (multi-color marks) Iconify sets, resolved through the
icon CLI:

```bash
node <repo-root>/tools/thumbnail-render/bin/icon.mjs simple-icons:postgresql
node <repo-root>/tools/thumbnail-render/bin/icon.mjs logos:postgresql
```

The CLI prints `{"body": "...", "viewBox": "..."}`; drop the `body` into the
chip's inline `<svg>` verbatim and set the `viewBox`. Color is **class-driven**,
not body-mutating — add one class to the `.chip`:

| Class | Source set | Effect |
|---|---|---|
| `.chip.brand-silhouette` | `simple-icons:*` | Renders the logo monochrome in `--chip-ink`. First choice — single fill, fits the minimal look. |
| `.chip.brand-color` | `logos:*` | Each path's own fill wins; the logo renders in its native brand colors. Use only when the brand collapses without its colors (Google wordmark, Slack hash, Firefox gradient). |

Rules:

- **Set preference:** `simple-icons` (silhouette) first, `logos` (multi-color)
  only when the brand needs its colors to read.
- **Never mutate the SVG body** to recolor it — use the class. For
  `brand-silhouette`, the chip's `--chip-ink` drives the fill; for
  `brand-color`, leave the native fills alone (tinting a multi-color mark
  destroys the recognition that justified using it).
- The logo sits **inside the chip**, on `--chip-bg`. The chip's contrast rules
  above still apply: keep the chip distinct from the accent.

## When to ask vs. decide yourself

Decide yourself: omit the chip (the default), or add a clear single-brand chip
(`JS`, `Docker`) when the topic is unambiguously that brand.

Ask the user when the brand mark is ambiguous (which of several tools is "the"
subject), or when adding the chip would crowd an already-busy composition and you
want their call on cutting it.
