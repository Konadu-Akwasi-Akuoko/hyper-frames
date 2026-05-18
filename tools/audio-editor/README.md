# audio-editor

Local web tool for fine-tuning voiceover cuts after the `cut-decider` agent
generates an initial `cuts.json`. Reads `videos/<slug>-<date>/audio/voiceover.mp3`
+ `transcript.json` + `cuts.json`, lets the user scrub / zoom / drag region
edges with snap-to-word, then writes the updated `cuts.json` back.

## Quickstart

```bash
bun install
bun dev
```

Open <http://localhost:5173>. Vite serves the frontend on `:5173`, Hono serves
the backend on `:3001`, and Vite proxies `/api/*` to Hono.

## Stack

- **Vite 8** + **React 19.2** + **TypeScript** (strict) — frontend
- **@vitejs/plugin-react** v6 (uses Oxc under the hood)
- **Tailwind CSS v4** — styling, via `@tailwindcss/vite`
- **Hono 4** — backend, runs natively on Bun
- **wavesurfer.js v7** — waveform + regions plugin (used in follow-up plans)
- **zod 4** — schema validation (used in follow-up plans)

## File tree

```
audio-editor/
├── src/
│   ├── App.tsx            # hash-router shell: #/ → PickerPage, #/edit/<slug> → EditorPage
│   ├── main.tsx
│   ├── pages/
│   │   ├── PickerPage.tsx
│   │   └── EditorPage.tsx
│   ├── styles/
│   │   └── globals.css    # @import "tailwindcss"; + theme tokens
│   └── ... (components/, hooks/, api.ts, types/, utils/ — added in follow-ups)
├── server/
│   ├── index.ts           # Hono entry, port 3001
│   └── routes/
│       ├── session.ts     # stub
│       └── videos.ts      # stub
├── vite.config.ts
├── tsconfig.json          # references app, node, server
└── package.json
```

## Scope

This package currently contains only the project scaffold — page navigation,
backend wiring, dev tooling. Stub routes return `"hello from <name>"` to verify
the proxy works.

Follow-up plans add:

- Real backend routes (path-safe `videos/<slug>/` loader, Zod-validated
  transcript/cuts parsing, save endpoint, audio file serving)
- The cut-decider Claude agent at `.claude/agents/cut-decider.md`
- The splice CLI (`tools/audio-splice/`)
- The actual editor UI (waveform with regions plugin, drag handles,
  snap-to-word, karaoke highlight, zoom)

For the design rationale, see `playgrounds/audio-editor-pipeline.html` at the
repo root.
