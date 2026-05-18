# audio-editor — project notes

Local tool for fine-tuning voiceover cuts in `videos/<slug>/`. Repo-root
`CLAUDE.md` covers the broader pipeline; this file is only what's specific to
this package.

## Dev server — do not start it

The user keeps `bun dev` running in a separate terminal (Vite on `:5173`, Hono
on `:3001`, `/api/*` proxied). After any code change, **tell the user to
reload the tab** — do not start, restart, or kill the dev server.

## Verification

```bash
bunx tsc -b      # typecheck all 3 projects
bun run lint
```

**No test suite.** Verify behaviour by reloading the editor; for visuals use
`agent-browser` against `http://localhost:5173/#/<slug>` when explicitly asked.

## Tailwind v4

No `tailwind.config.js` — tokens live in the `@theme` block of
`src/styles/globals.css`. Reference them with `bg-[color:var(--color-panel)]`,
not Tailwind palette names.

## Transcripts

**Never `Read` `transcript.json` directly** — ~1500+ entries per video will
flood context. Use the python-filter pattern from the repo-root `CLAUDE.md`.

## Wavesurfer gotchas (load-bearing)

Not in the docs; costly to rediscover.

- **`region-update-start` / `update-end` do not exist.** Only `region-update`
  (per-mousemove during drag) and `region-updated` (mouseup + every
  programmatic `setOptions`).
- **`region.updatingSide`** is set only during user drags, null for
  programmatic changes — gate drag-coalescing on this.
- **`addRegion()` fires `region-created` synchronously.** Pre-tag the new id in
  `ownIdsRef` before calling, consume the tag in the handler, or our own
  commits get mistaken for user drag-paint and re-enter the sync loop.
- **`addRegion({content})` with an `HTMLElement`** tags **your root** with
  `part="region-content"` — it does not wrap your element in a content div.
- **Shift is overloaded** — both `enableDragSelection` and shift+wheel zoom.
  Arm/disarm drag-selection on `keydown`/`keyup`; clear on `window.blur`.
