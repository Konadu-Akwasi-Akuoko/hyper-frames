---
name: studio-ideas
description: Curate the studio idea backlog — read ONLY the unjudged raw_signal delta in tools/studio/studio.db, apply qualitative worth-pursuing judgment (keep or discard with a one-line rationale, NEVER a grade or score), insert keepers into the ideas table, and mark every raw row judged. Use when the user says "curate the wire", "curate studio ideas", "process the raw signal", "what's new on the wire", "turn discovery into ideas", "run the studio-ideas skill", or after a studio discovery run. This skill is the intelligence for tools/studio — the server and CLI decide nothing.
---

# studio-ideas

The intelligence layer for `tools/studio`. The discovery CLI fills `raw_signal`
with unjudged rows; this skill turns that raw signal into a curated idea backlog
on **The Wire**. The full design is
`docs/superpowers/specs/2026-06-22-studio-idea-board-design.md` §7.

## Hard rules (non-negotiable)

- **Aggregator, never a judge.** NEVER assign a number, score, rank, percentage,
  or rubric to an idea. The verdict is binary qualitative: **keep** or
  **discard**, with a one-line *why-pursue* rationale. The human decides
  make-or-not.
- **Flat token cost — read only the delta.** Only ever
  `SELECT ... WHERE judged_at IS NULL`. NEVER read the whole `raw_signal` or
  `ideas` table into context. This is the entire reason the store is
  server-owned SQLite.
- **Suggest a format.** Set `kind` to your best guess (long / short / series),
  `kind_source='ai'`, and a one-line `kind_why`. This is a *suggestion*, not a
  verdict — the human confirms it with one tap on The Wire (which flips
  provenance to `human`) or overrides to any value. It is still qualitative:
  **never a grade, rank, or score** — same bar as the keep/discard rationale.
- **Discarded rows stay.** Mark them `judged_verdict='discarded'` — they remain
  in `raw_signal` as an audit trail and are never resurfaced or re-judged.
- **Mark everything you read.** Every row you pull this pass MUST end with a
  non-null `judged_at`, kept or discarded, or it will be re-read next time.

The store is `tools/studio/studio.db` (system `sqlite3`, WAL). All commands below
run from the repo root.

## Step 1 — (optional) trigger a discovery run

Only if the user asks, or `raw-counts` is empty/stale. Serial and bounded:

```bash
cd tools/studio/discovery && uv run studio-discover --db ../studio.db \
  --videos-per-channel 12 --comments-from-top 4 --comments-per-video 25
```

(Or, if the dev server is up, the user can press **Run discovery** on The Wire.)

## Step 2 — read ONLY the unjudged delta

First the shape, so you can batch:

```bash
sqlite3 tools/studio/studio.db \
  "SELECT source, count(*) FROM raw_signal WHERE judged_at IS NULL GROUP BY source;"
```

Then pull compact rows (process per source; cap each batch so context stays
flat). For aggregator/video rows you need title + a few payload numbers:

```bash
sqlite3 -json tools/studio/studio.db \
  "SELECT id, source, external_id, title, url, payload_json
   FROM raw_signal WHERE judged_at IS NULL AND source NOT LIKE 'youtube-comments%'
   ORDER BY source LIMIT 120;"
```

Comment rows carry the demand signal — read them separately and cluster:

```bash
sqlite3 -json tools/studio/studio.db \
  "SELECT id, source, external_id, title, payload_json
   FROM raw_signal WHERE judged_at IS NULL AND source LIKE 'youtube-comments%'
   LIMIT 40;"
```

If a batch is large, judge it, mark it, then pull the next batch — never hold the
whole backlog at once.

## Step 3 — establish what's already covered (novelty guard)

So you don't resurface a topic that's an existing idea or a made video:

```bash
sqlite3 tools/studio/studio.db "SELECT title FROM ideas WHERE status IN ('new','keep','promoted');"
ls videos/    # made/in-progress slugs
```

## Step 4 — judge each row (qualitative, no number)

For every unjudged row decide **keep** or **discard** on three lenses:

- **Fit** — is there a real computing / system-design / dev-tools angle that is
  on-brand for this channel? (Off-topic, listicle-bait, pure news → discard.)
- **Novelty** — not already an idea (Step 3) and not already a made video. A
  near-duplicate of covered ground → discard (or keep as a deliberately fresh
  angle, said so in the rationale).
- **Demand shape** (comment rows) — cluster the comments into themes. A
  *recurring* ask ("keeps asking X", "when full tutorial") is a strong keep;
  capture 1-2 representative quotes and the count. One-off praise → not demand.
- **Format fit** (keepers only) — suggest a `kind` from the shape of the topic:
  - **short** — a single tight mechanism / broad-appeal "how it works" quick hit
    (Cleo-style; e.g. *"what happens when you tap your card"*, a ~1–2 min mirror).
  - **long** — a full system-design / deep explainer that needs build-up (e.g.
    *"How Google Docs lets everyone type at once (CRDTs)"*, an 8-min
    ByteByteGo-lane topic).
  - **series** — a topic too big for one video / naturally multi-part (e.g.
    *"How LLMs actually work"* as a multi-parter).

  When genuinely ambiguous, pick the safer single-video format and say so in
  `kind_why`. This is a suggestion the human confirms — not a grade.

Keep the bar honest: the backlog is small on purpose. When unsure, discard — it
stays in the audit trail and costs nothing to skip.

## Step 5 — insert keepers

Pick `type` from the source:

| raw source | idea `type` |
|---|---|
| `youtube-comments:*` (a recurring viewer ask) | `comment_demand` |
| `youtube:*` (a competitor video worth *your* take) | `mirror` |
| `hn` / `reddit:*` / `lobsters` / `dailydev` | `trend` |

Build `evidence_json` from the raw payload, and include a **categorical lean**
(`hold` | `lean` | `strong`) — a 3-state notch reflecting how strongly the
rationale leans toward pursuing. **This is not a number, not a grade** — it only
drives the wire meter's fill height.

- `trend`: `{"lean":"strong","points":5200,"comments":312}`
- `mirror`: `{"lean":"lean","views":2400000,"duration_s":102}`
- `comment_demand`: `{"lean":"strong","count":37,"quotes":[{"text":"…why is it off by a second?"}]}`

Insert (id = random hex; `status='new'`; one-line rationale; suggested `kind`
with `kind_source='ai'` + a one-line `kind_why`):

```bash
sqlite3 tools/studio/studio.db "INSERT INTO ideas
 (id,type,kind,kind_source,kind_why,status,title,rationale,source,source_url,source_title,evidence_json,raw_signal_id,first_seen)
 VALUES (lower(hex(randomblob(8))),'trend','long','ai',
  'a full system-design build-up — single-point-of-failure → anycast → blast radius.',
  'new',
  'Cloudflare: one company, 20% of the web',
  'the single-point-of-failure frenzy lands square in your system-design lane — strong fit.',
  'hn','https://news.ycombinator.com/item?id=123', NULL,
  json('{\"lean\":\"strong\",\"points\":5200,\"comments\":312}'),
  '<raw_signal.id>', datetime('now'));"
```

Use `json('...')` so `evidence_json` is valid JSON. The `title` is the *idea*
title (your framing of the video), not necessarily the raw item's title.

## Step 6 — mark every judged row

Kept rows (link is already captured via `raw_signal_id`):

```bash
sqlite3 tools/studio/studio.db "UPDATE raw_signal
 SET judged_at=datetime('now'), judged_verdict='kept' WHERE id IN ('<id1>','<id2>');"
```

Discarded rows (the rest of this batch):

```bash
sqlite3 tools/studio/studio.db "UPDATE raw_signal
 SET judged_at=datetime('now'), judged_verdict='discarded'
 WHERE judged_at IS NULL AND id IN ('<id3>','<id4>', ...);"
```

A safe catch-all once a batch is fully decided — mark anything still unjudged in
that source as discarded so nothing is re-read:

```bash
sqlite3 tools/studio/studio.db "UPDATE raw_signal
 SET judged_at=datetime('now'), judged_verdict='discarded'
 WHERE judged_at IS NULL AND source='hn';"
```

## Step 7 — report and hand off

Tell the user a compact summary: kept N (by type), discarded M, with the new idea
titles and your suggested `kind` for each. Then they triage on **The Wire**
(keep/reject, confirm or override the suggested kind, promote). You suggest the
format; do not promote, do not score — the make-or-not call, the final format,
and the promote are the human's.

## Prune (housekeeping, optional)

`raw_signal` is the only growing table. When asked to prune, delete judged rows
past the retention window (the server also exposes `POST /api/ideas/prune`):

```bash
sqlite3 tools/studio/studio.db "DELETE FROM raw_signal
 WHERE judged_at IS NOT NULL AND fetched_at < datetime('now','-90 days');"
```
