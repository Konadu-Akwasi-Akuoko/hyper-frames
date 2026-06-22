# studio — project notes

Unified idea aggregator (**The Wire**) + 12-stage production board (**The Desk**)
for the channel. Supersedes the root `kanban.html` and `tools/topic-pipeline/`.
Full design: `docs/superpowers/specs/2026-06-22-studio-idea-board-design.md`
(§10.1 = the locked "The Wire Desk" visual language). Plan:
`docs/superpowers/plans/2026-06-22-studio-implementation.md`.

## Dev server — do not start it

The user keeps `bun dev` running in a separate terminal (Vite on `:5273`, Hono
on `:3273`, `/api/*` proxied). After any code change, **tell the user to reload
the tab** — do not start, restart, or kill the dev server.

## Ports

Server `:3273`, client `:5273` — deliberately distinct from audio-editor
(`:3001`/`:5173`) so the two tools never collide.

## Store — local SQLite, no Docker

`studio.db` is a local SQLite file (gitignored, rebuildable). The Hono server
writes it via `bun:sqlite`; the Python discovery CLI writes `raw_signal` via
stdlib `sqlite3`. Both open the same file in WAL mode — no DB server, no Docker.
Inspect with the system `sqlite3 studio.db`.

## Architecture (where the intelligence lives)

- **server/** (Hono, `:3273`) — the only writer the UI talks to. Derives board
  state by scanning `videos/`, overlays manual fields, triggers discovery. Holds
  **no idea-judgment intelligence**.
- **src/** (React, `:5273`) — two views, `Wire` (ideas) and `Desk` (board).
- **discovery/** (Python, `studio-discover`) — zero-AI plumbing; fetches raw
  signal (yt-dlp channel videos + top comments; HN/Reddit/Lobsters/daily.dev)
  into `raw_signal` with `judged_at = NULL`. Serial + bounded (bot-wall safe).
- **The `studio-ideas` skill** (`.claude/skills/studio-ideas/`) — the
  intelligence. Reads only the unjudged delta, applies qualitative
  worth-pursuing judgment (keep/discard + one-line rationale, **never a grade**),
  inserts curated ideas.

## Hard rules

- **Aggregator, never a judge.** No numeric score / rank / rubric anywhere. The
  human decides make-or-not; the AI suggests format (long/short/series) and the
  human confirms/overrides.
- **Flat AI token cost.** The skill reads only `WHERE judged_at IS NULL`; never
  loads the whole store. Promote/reject leave the active view; prune trims old
  judged `raw_signal`.
- **Visual = §10.1.** Meter is the one signature (teal→red, one law both views).
  On-Air Red is rationed to the meter peak / ON-AIR / commit — never a wash.
  Mono (`.num`) is a scoped utility, never body. Namespace component classes.
  `design/mockup.html` is the visual source of truth.

## Verification

```bash
bunx tsc -b            # typecheck app + node + server
bun run lint
bun test server        # db / scan / dedup / promote
cd discovery && uv run pytest
```
