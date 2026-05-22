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
- **`addRegion()` before `ready` permanently clamps start/end to 0.** The
  `Region` constructor runs `clampPosition` against `getDuration()` *at
  construction time*; pre-`ready` that is `0`, so every region collapses to
  `start===end===0` — a zero-width `part="marker"` pinned at `left:0%`. The
  plugin's `once("ready")` deferral only calls `_setTotalDuration` +
  `renderPosition`, which never re-derives the bounds, so they stay at 0. Gate
  the cuts→regions sync on a non-zero duration (Waveform's `isReady` state) so
  regions are built with real bounds. Symptom: all cut labels stack at the
  waveform's left edge while the sidebar shows correct times.
- **The waveform + region content render inside a ShadowRoot — `globals.css`
  cannot reach it.** `.region-chrome__*` rules in the document stylesheet never
  apply to region content; the label silently renders as unstyled 16px wrapping
  text. Style region chrome by injecting a `<style>` into the shadow root after
  `WaveSurfer.create` (`ws.getWrapper().getRootNode()` → `REGION_SHADOW_CSS` in
  `Waveform.tsx`). CSS custom properties (`--color-*`, `--font-*`) inherit
  through the shadow boundary, so tokens still resolve. Also: the band's `part`
  is multi-token (`"region <id>"`), so hover selectors must use `[part~="region"]`,
  not `[part="region"]` (the latter never matches).
