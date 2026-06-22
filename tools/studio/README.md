# studio

A unified **idea aggregator** + **production board** for the channel — two views
of one app:

- **The Wire** (Ideas) — an aggregator backlog. A zero-AI discovery CLI collects
  raw signal from a fixed set of YouTube channels (recent videos + top comments)
  and the text aggregators (Hacker News, Reddit, Lobsters, daily.dev). The
  `studio-ideas` skill applies qualitative *worth-pursuing* judgment — keep or
  discard, with a one-line rationale, **never a grade** — and the keepers land in
  a backlog you triage.
- **The Desk** (Pipeline) — the 12-stage production board, tracking each
  committed video Idea → Published → Shorts, with progress derived by scanning
  the `videos/` folder.

Promoting an idea on The Wire lands a card on The Desk and removes the idea from
the backlog, so the backlog stays small.

## Run

```bash
bun install
bun dev            # Vite :5273  +  Hono :3273  (/api proxied)
```

Open http://localhost:5273.

## Discovery

```bash
cd discovery
uv sync
uv run studio-discover --db ../studio.db          # serial, bounded, bot-wall safe
```

Then ask the **`studio-ideas`** skill to curate the new raw signal into ideas.

## Store

`studio.db` is a local SQLite file (gitignored, rebuildable). The server writes
it via `bun:sqlite`; discovery writes `raw_signal` via Python stdlib `sqlite3`.
No DB server, no Docker. Inspect with `sqlite3 studio.db`.

## Layout

```
server/      Hono API (:3273) — board scan + overlay, ideas triage/promote, channels, discovery trigger
src/         React client (:5273) — Wire (ideas) + Desk (board)
discovery/   Python studio-discover CLI — yt-dlp + aggregator fetchers → raw_signal
design/      mockup.html — the locked visual reference (The Wire Desk)
```

See `CLAUDE.md` for the authoring rules and `docs/superpowers/specs/2026-06-22-studio-idea-board-design.md` for the full design.
