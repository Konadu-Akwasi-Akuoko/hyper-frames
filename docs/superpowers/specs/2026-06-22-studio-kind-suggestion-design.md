# Studio — AI-suggested video format (kind) on The Wire → The Desk

**Date:** 2026-06-22
**Status:** Approved (brainstorm complete)
**Touches:** `tools/studio/` (server + client + db), `.claude/skills/studio-ideas/`,
the studio design spec, both `CLAUDE.md` files.
**Parent spec:** `docs/superpowers/specs/2026-06-22-studio-idea-board-design.md`
(this amends its hard rule **D4**).

## 1. Problem

Two gaps in the studio idea→production flow:

1. **The Wire** lets the human set a format (`kind`: long / short / series), but the
   `studio-ideas` skill is forbidden from suggesting one — every idea lands as
   `unset`, so the human format-triages cold with no AI input.
2. **The Desk** drops `kind` entirely on promote (`board_overlay` has no `kind`
   column, `BoardCard` has no `kind` field, `LaneCard` never renders it), so during
   research you can't see whether a card is a Short, a long-form, or a series.

## 2. Decision summary

- **AI proposes, human disposes.** The skill writes its best-guess `kind` plus a
  one-line reason, marked as AI-originated. The human confirms with one tap (which
  re-stamps it as theirs and clears the mark) or overrides to any value. The
  committed format is therefore always traceable to who chose it.
- **Reason on hover.** The skill writes a one-line "why this format"; it surfaces as
  a tooltip on the format chip, not as card-body text.
- **Carry through to the Desk.** `kind` + provenance snapshot copied into
  `board_overlay` at promote time; the Desk card shows a format chip (with the `·ai`
  marker when still AI-suggested). **Display-only on the Desk in v1** — the format
  decision lives on The Wire.

### Hard-rule amendment (deliberate)

Parent spec **D4** and both `CLAUDE.md` files currently read *"the human decides
make-or-not and long/short/series."* This feature changes that to:

> The human decides make-or-not. The AI **suggests** a format (long / short /
> series) with a one-line reason; the human confirms or overrides. Still **no
> numeric grade, rank, percentage, or rubric anywhere** — the format suggestion is
> qualitative, exactly like the keep/discard rationale.

The "aggregator, never a judge" identity (no scoring) is **unchanged**. Only the
"human alone picks the format" clause relaxes to "AI suggests, human decides."

## 3. Interface contract (exact names — agents MUST use these verbatim)

### 3.1 Database columns (new)

`ideas` table — two new nullable columns:

| column | type | meaning |
|---|---|---|
| `kind_source` | `TEXT` | `'ai'` \| `'human'` \| `NULL`. Provenance of the current `kind`. `NULL` = no provenance (legacy rows, or `kind='unset'`). |
| `kind_why` | `TEXT` | One-line reason for an AI format pick. Only meaningful (and only rendered) when `kind_source='ai'`. |

`board_overlay` table — two new nullable columns (promote-time snapshot):

| column | type | meaning |
|---|---|---|
| `kind` | `TEXT` | `'unset'` \| `'long'` \| `'short'` \| `'series'` \| `NULL`. |
| `kind_source` | `TEXT` | `'ai'` \| `'human'` \| `NULL`. |

Add to `SCHEMA` (for fresh DBs) **and** apply via idempotent
`ALTER TABLE ... ADD COLUMN` guards in `migrate()` (for existing DBs). The guard
helper checks `PRAGMA table_info(<table>)` before adding.

### 3.2 Provenance rule (single source of truth)

Provenance is **inferred by write channel**, never sent in a request body:

- The **skill** writes directly to SQLite → it sets `kind`, `kind_source='ai'`,
  `kind_why='<reason>'`.
- The **server `PATCH /api/ideas/:id`** is only ever called by the human UI → when
  `body.kind` is present it sets `kind_source = body.kind === 'unset' ? NULL :
  'human'` and `kind_why = NULL`. The `IdeaTriageBody` Zod schema is **unchanged**
  (no new request field).

### 3.3 Server JSON shapes

`mapIdeaRow` (and the client `Idea` type) gain:

```ts
kind_source: "ai" | "human" | null;
kind_why: string | null;
```

`BoardCard` (client type) and the object pushed by `buildBoard()` gain:

```ts
kind: IdeaKind;          // "unset" when no overlay kind
kindSource: "ai" | "human" | null;
```

`buildBoard()` maps `kind: (o?.kind as IdeaKind) ?? "unset"` and
`kindSource: (o?.kind_source as "ai" | "human" | null) ?? null`. The `OverlayRow`
interface in `board.ts` gains `kind` and `kind_source` fields.

### 3.4 Promote carry-through

`POST /api/ideas/:id/promote` — the `board_overlay` INSERT now also writes `kind`
and `kind_source`, copied from the promoted idea row.

## 4. Server changes (`tools/studio/server/`)

- **`lib/db.ts`** — add the four columns to `SCHEMA`; add an `ensureColumns(db)`
  helper that runs the idempotent ALTER guards; call it from `migrate()` after
  `db.exec(SCHEMA)`.
- **`lib/util.ts`** — `IdeaRow` interface + `mapIdeaRow` gain `kind_source`,
  `kind_why`.
- **`routes/ideas.ts`**
  - `PATCH /:id`: split the update so a `kind` change stamps provenance per §3.2
    (kind + kind_source + `kind_why=NULL`), while `status`/`notes` update as today.
    A request with no `kind` must NOT touch `kind_source`/`kind_why`.
  - `POST /:id/promote`: extend the `board_overlay` INSERT to carry `kind` +
    `kind_source` (§3.4).
- **`routes/board.ts`** — `OverlayRow` + `buildBoard()` per §3.3. `POST /` (manual
  add) and `PATCH /:name` are unchanged (no `kind` on the Desk in v1).

## 5. Client changes (`tools/studio/src/`)

- **`types.ts`** — `Idea` gains `kind_source` + `kind_why`; `BoardCard` gains `kind`
  + `kindSource`.
- **`components/Dispatch.tsx`** (The Wire card)
  - Format chip label unchanged (`kind` or `set kind`), but when
    `idea.kind_source === 'ai'` append a muted `·ai` marker span and set
    `title={idea.kind_why ?? undefined}` for the hover reason.
  - **Chip click**: when `kind_source === 'ai'` → **accept** (set the same kind,
    which the server re-stamps as `human`); otherwise → **cycle** (existing
    `KIND_NEXT` behavior). Wire this by passing both an `onAcceptKind` and the
    existing `onCycleKind`, and choosing inside `Dispatch` based on `kind_source`.
  - The `long · short · series` action button and the `1`/`2`/`3` keys are
    unchanged (always an explicit human set).
- **`views/Wire.tsx`** — add `onAcceptKind={() => setKind(idea.id, idea.kind)}` to
  the `Dispatch` props. No other logic change (`setKind`/`cycleKind` already PATCH).
- **`components/LaneCard.tsx`** (The Desk card) — render a compact `.c-kind` chip
  when `card.kind && card.kind !== 'unset'`, with the `·ai` marker when
  `card.kindSource === 'ai'`. Place it on the title row / just under the title to
  match the approved mock. Display-only (no click handler).
- **`styles/globals.css`** — style the `·ai` marker (`.chip.kind .ai`) and the Desk
  `.c-kind` chip + its `.ai` marker. The marker is muted (`var(--graphite)`,
  small, mono); the chip reuses the existing pill vocabulary
  (`var(--card-sunk)` / `var(--press-ink)`). **Respect the visual law**: On-Air Red
  (`--meter-hot`) stays rationed to the meter peak / ON-AIR — the format chip and
  marker are graphite/sunk, never red.

## 6. Skill changes (`.claude/skills/studio-ideas/SKILL.md`)

- Replace the **"Leave `kind` unset"** hard rule with **"Suggest a format"**: set
  `kind` to the best guess, `kind_source='ai'`, plus a one-line `kind_why`. The
  human confirms/overrides on The Wire (which flips provenance to `human`). Keep
  **"never a grade/score"** verbatim.
- Add a 4th judgment lens, **Format fit**, with heuristics:
  - **short** — a single tight mechanism / broad-appeal "how it works" quick hit
    (Cleo-style; e.g. *"what happens when you tap your card"*, a ~1–2 min mirror).
  - **long** — a full system-design / deep explainer that needs build-up (e.g.
    *"How Google Docs lets everyone type at once (CRDTs)"*, an 8-min ByteByteGo-lane
    topic).
  - **series** — a topic too big for one video / naturally multi-part (e.g.
    *"How LLMs actually work"* as a multi-parter).
  - When genuinely ambiguous, pick the safer single-video format and say so in
    `kind_why`.
- Update the Step 5 `INSERT` example to include `kind`, `kind_source='ai'`,
  `kind_why`. Update Step 7 hand-off wording (the human now confirms/overrides a
  suggestion rather than picking cold).

## 7. Docs changes

- **Parent spec** `2026-06-22-studio-idea-board-design.md`: amend **D4** and **D5**
  language per §2; update the §6 schema block (`ideas` + `board_overlay` columns);
  update §7 (skill now suggests `kind`); note the chip `·ai` treatment near §10.1 if
  a visual line is warranted.
- **`tools/studio/CLAUDE.md`**: the "Aggregator, never a judge" hard rule line about
  "The human decides ... long/short/series" → "The human decides make-or-not; the
  AI suggests format and the human confirms/overrides."
- **Root `CLAUDE.md`**: the `tools/studio` paragraph that describes studio-ideas
  curation ("qualitative keep/discard + a one-line rationale, never a grade") →
  add that it also **suggests a format (long/short/series) the human confirms**.

## 8. Verification

```bash
cd tools/studio
bunx tsc -b            # typecheck app + node + server
bun run lint
bun test server        # db / scan / dedup / promote
```

New / adjusted tests (`server/lib/db.test.ts` + a route test):

- `ideas` has `kind_source` + `kind_why` columns; `board_overlay` has `kind` +
  `kind_source`. (The existing "NO score column" test stays green.)
- `ensureColumns` is idempotent — running `migrate()` twice does not throw.
- Promote carries `kind` + `kind_source` from the idea into `board_overlay`.
- PATCH `kind` stamps `kind_source='human'` and clears `kind_why`; PATCH
  `kind='unset'` sets `kind_source=NULL`; a PATCH with only `status`/`notes` leaves
  `kind_source`/`kind_why` untouched.

`discovery/` pytest is unaffected.

## 9. Out of scope (v1)

- Editing the format from the Desk (display-only; future: the `DetailPanel` could
  gain a kind control + carry `kind_why` for a Desk tooltip).
- Bulk "accept all AI suggestions" on The Wire.
- Re-suggesting a format after a human override.
