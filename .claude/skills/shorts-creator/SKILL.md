---
name: shorts-creator
description: Turn a finished long-form hyper-frames video into ~5 (up to 10) vertical 9:16 Shorts that funnel back to it, each ending on a Cleo-Abram-style subscribe CTA. Two-phase and human-in-the-loop — Phase 1 selects self-contained beats from the parent and drafts each clip's script + a staggered upload plan for review; Phase 2 builds one approved Short at a time (voiceover → portrait HyperFrames composition → vertical cover → 1080×1920 render). Publishing fans the finished render out to TikTok / Instagram / X / LinkedIn / YouTube by driving the `opusclip` plugin skill (`project create --skip-curate` → `post schedule`), or YouTube-only via the `youtube-studio` MCP / manual Studio. Use when the user says "make shorts from this video", "cut this into shorts", "generate the shorts", "create vertical clips", "turn this into reels/tiktoks", "schedule/post the shorts", or names a finished `videos/<slug>-<date>/` folder and asks for Shorts. Runs after a long-form video's script.md + transcript.json exist (ideally after it's rendered).
---

# shorts-creator

You turn a finished long-form video into a small batch of **vertical 1080×1920
Shorts** that each funnel a viewer back to the parent, ending on a subscribe CTA
fused to a fresh cliffhanger (the Cleo Abram shape). This is the channel's
strongest discovery path — a companion Short pulled **2.7× the flagship's
views** — so the engine matters.

Like `video-director`, this is an **orchestrator**: it sequences and wires the
other skills rather than reimplementing them. Two phases, both gated on the
human.

## What you own vs. delegate

- **You own:** picking the ~5 beats from the parent; the **Shorts script shape**
  (hook / counter-twist / pivot chain / Cleo CTA — this is *not* `script-writer`,
  see below); the per-Short folder scaffold; the staggered upload plan; and the
  **publish hand-off** (via MCP or manually in Studio).
- **You delegate:** voiceover + transcript (`voiceover-elevenlabs-v2` /
  `transcribe-and-plan-cuts`), the **portrait composition build**
  (`video-director` — now dimension-aware; it authors any root declared
  1080×1920), the **vertical cover** (`thumbnail-and-title-generator` in vertical mode), and
  the CLI render (`hyperframes-cli`).

## Hard constraints

1. **Publishing: multi-platform via OpusClip, or YouTube via the MCP/Studio.**
   This skill renders the MP4s and writes a stagger plan + per-Short copy; the
   actual posting then runs through one of two paths:
   - **Cross-platform distribution (TikTok / Instagram / X / LinkedIn / YouTube)**
     drives the **`opusclip` plugin skill** — do NOT reimplement OpusClip here, it
     owns its own CLI. Upload the finished render with `project create --file
     <out/mp4> --skip-curate` (so OpusClip ingests it as one clip without
     re-clipping), then `post schedule` it to each connected account at its plan
     date. See **"Cross-platform distribution"** below.
   - **YouTube-only** can instead use the `youtube-studio` MCP (`video_upload`
     private + `video_schedule`) for richer control (captions, metadata QA), or a
     manual Studio upload. Either YouTube path is valid.

   **NEVER post to the "IRL Coder" YouTube channel** (OpusClip
   `post_account_id` `694a97bfb945edd75645afc4` / channel `UCfWQCu9N56U5B_tPJ-nh0Ow`).
   The Shorts YouTube destination is **"Akwasi Konadu Akuoko"** (OpusClip
   `post_account_id` `69352002d409efbfe42cab42` / channel
   `UCYKFy3oPn2b6gbjAzmgNgJg`). Both channels are linked in OpusClip, so the
   account is selected explicitly — never let the IRL Coder account into the
   fan-out.
2. **Shorts scripts are NOT written by `script-writer`.** That skill is the
   long-form house voice and deliberately carries **no CTA**. A Short is a
   different artifact — single-idea, ~130–260 words, a 5–9-word hook, and it
   **ends on a CTA**. This skill owns the Shorts script shape, grounded in
   `docs/creator-patterns.md` §4.2 (the Cleo CTA) and §6 WS4 (the hook spec).

## Folder layout

Shorts are derivative of one parent video, so they live under it:

```
videos/<parent-slug>-<date>/
└── shorts/
    ├── PLAN.md                      ← Phase 1: the 5-beat selection + stagger schedule
    └── <NN>-<hook-slug>/            ← each Short = a full portrait mini-project
        ├── index.html  hyperframes.json
        ├── script.md                ← the clip script (with CTA)
        ├── design.md                ← inherits the parent's palette/type (portrait)
        ├── audio/                   ← raw.mp3 → voiceover.mp3
        ├── transcript.json
        ├── compositions/  assets/
        ├── thumbnails/              ← vertical 1080×1920 cover
        ├── out/                     ← rendered 1080×1920 MP4
        └── publish.md               ← title / description / hashtags / scheduled date
```

All CLI commands (`init`, `lint`, `inspect`, `preview`, `render`) run from
inside each `<NN>-<hook-slug>/` folder, never from the parent.

## Phase 1 — Selection + clip scripts (gate before any build)

**Step 1 — Resolve the parent.** An explicit `videos/<slug>-<date>/` path, or
the current folder if it's one. Confirm `script.md` and `transcript.json` exist
(ideally a rendered `out/` MP4 too — Shorts are usually cut after the parent
ships). Note the parent's working title and its one master loop.

**Step 2 — Read the parent.** `script.md` (full), `captions.srt` if present, and
the parent's `design.md` (palette/type the Shorts inherit). **Never `Read`
`transcript.json` directly** — filter it with `python3 -c` like `video-director`
does (`video-director/reference/transcript-timing.md`) when you need word
timings for a beat boundary.

**Step 3 — Pick the beats.** Choose ~5 (configurable up to 10) **self-contained**
moments, each orbiting **ONE counterintuitive question** — a beat that lands
without the rest of the video. Prefer the parent's most surprising reveals,
shock numbers, and "wait, what?" pivots. Refuse scope creep: one idea per Short.

**Step 4 — Draft each clip script** in the Shorts shape (spec below). ~130–260
spoken words (~25–55s at 170 wpm). Each is `script.md` in its Short folder.

**Step 5 — Draft the stagger plan.** One Short every **~3 days**. For each:
working title (a §5 formula, often a curiosity-question), a one-line
description, 3–5 hashtags, and the target publish date (count forward 3 days
each from a start date the user gives — never invent "today").

**Step 6 — Write `shorts/PLAN.md`** (the table: NN, hook slug, the one question,
word count, suggested parent-block reuse, title, publish date) and each Short's
`script.md`. **Gate:** present PLAN.md and stop. The user approves / edits the
selection before any build. Do not enter Phase 2 unprompted.

## The Shorts script shape (the spec — §6 WS4 + §4.2)

Each clip script is built as:

1. **Hook in the first 5–9 words**, present tense, no name / branding / "in this
   video." Use a provocative why/what, a shock number, or a reframe ("X has an
   evil twin"). The first on-screen visual shows the literal subject so words and
   image confirm each other.
2. **Counter-twist in sentence 2–3** — invalidate the expectation just set ("By a
   lot." / "Turns out, insanely hard." / "But then, how do we even know…").
3. **Body = a chain of "but / then / turns out" pivots**, each overturning the
   prior beat; the on-screen frame changes every 1–2 sentences. A numbered or
   zoom scaffold adds countdown tension.
4. **One mid-Short meta-reward at peak surprise only** (optional): "Subscribe if
   this is already blowing your mind." Use at most once, and only at the genuine
   peak.
5. **The CTA = the final sentence, fused to a fresh loop** (the Cleo shape):
   `[solve the headline question] → [open a NEW bigger loop in one sentence] →
   [subscribe as the way to close THAT loop]`. Verbatim templates: "But [new
   mystery]. So, where's it going? **To find out, subscribe.**" / "**To see it,
   subscribe.**" / "**For more [tagline], subscribe.**" Defer **all** branding to
   this final line. **Never end on resolution** — end on the next mystery handed
   to the subscribe button.

## Phase 2 — Build one approved Short (repeat per Short)

Build **one at a time**, fully, before the next — each is a self-contained
mini-project and the loop survives a fresh session.

**Step A — Scaffold the portrait folder.** From `videos/<parent>/shorts/`, run
`npx hyperframes init <NN>-<hook-slug> --example vignelli` (a 1080×1920 portrait
start; or `--example blank` then set the root `#root` to `data-width="1080"
data-height="1920"`). Write a portrait `design.md` inheriting the parent's
palette/type. Confirm the root host, the `html,body`/`.scene` CSS, and the
viewport meta are all **1080×1920** (`video-director/reference/portrait-mode.md`).

**Step B — Voiceover + transcript.** Hand off to the project's voiceover path
(same as the parent): the user records → `audio/raw.mp3` →
`transcribe-and-plan-cuts`, or TTS via `voiceover-elevenlabs-v2`. The user does
the voice work, signals done, and the skill produces `audio/voiceover.mp3` +
`transcript.json`. Don't author the composition before the transcript exists —
timing is anchored to real word timestamps.

**Step C — Portrait composition.** Hand off to **`video-director`** on the Short
folder. Because the root declares 1080×1920, the director detects portrait in
its Step A, reads `reference/portrait-mode.md`, and authors vertical — reusing
parent composition blocks **reflowed to 9:16** where they fit (split → stacked,
side-cutout → full-height, etc.). The **final scene is the CTA beat**: adapt a
native portrait subscribe block (`npx hyperframes catalog --type block` →
`tiktok-follow` / `instagram-follow` / `spotify-card`), land the "Subscribe" cue
upper-middle (never over the phone's real button), on the VO's "subscribe" word.
The director runs its own visual-QA + SFX passes; you don't re-run them here.

**Step D — Vertical cover.** Hand off to **`thumbnail-and-title-generator`** with a vertical
trigger word (e.g. "make a **vertical** Shorts cover") so it renders 1080×1920.
The cover carries the subject or the shock number; the title carries the
question — they shouldn't say the same thing twice.

**Step E — Render.** From the Short folder, `npx hyperframes render` (reads the
root's 1080×1920). Confirm the output MP4 is **1080×1920** before moving on (the
one technical thing worth eyeballing per Short). Save under `out/`.

**Step F — Publish hand-off.** Write `publish.md` for this Short: title,
description (lead with the hook, link the parent video, comment-bait sequel
offer), 3–5 hashtags (`#Shorts` + topic nouns), the scheduled date from the
stagger plan, and the **target platforms**. Then run the distribution (see
"Cross-platform distribution" below) or hand off the YouTube-only path —
`video_upload(path="out/<mp4>", privacy_status="private")` + `video_schedule(...)`
under the write-gate, or the manual Studio path (`Studio → Create → Upload
videos → … → Schedule`). Optionally run `video-publish-qa` against the YouTube
Short once it's live to catch thin tags / captions.

## Cross-platform distribution (via the `opusclip` skill)

To fan a finished Short out to TikTok / Instagram / X / LinkedIn (and YouTube,
if not using the MCP path), drive the **`opusclip` plugin skill** — it owns the
CLI and auth; this skill only sequences it. The render is already a finished
1080×1920 MP4, so OpusClip must **not** re-clip it:

1. **Confirm destinations.** `opusclip post account list`. The connected
   accounts (this channel's): Instagram Business, LinkedIn, TikTok Business, X
   (TWITTER, 1 credit/post), and YouTube **"Akwasi Konadu Akuoko"**. **Exclude
   "IRL Coder"** — see Hard constraint #1.
2. **Ingest the render as one clip.** `opusclip project create --file out/<mp4>
   --skip-curate --aspect portrait --title "<Short title>"`, then
   `opusclip clip list --project <PID>` to get the single `clip_id`.
3. **Schedule per platform.** For each chosen account, `opusclip post schedule
   --project <PID> --clip <CID> --account <ACCOUNT_ID> --title "<title>" --at
   <plan-date as UTC ISO, e.g. 2026-06-27T14:00:00Z>`. Convert the stagger
   plan's local date to UTC. Optionally `post copy create` first for
   per-platform captions.

**Gate (outward-facing):** scheduling posts to the user's real accounts is a
publish action — preview the exact platforms + UTC times + the per-account
command and get an explicit yes **before** the first `post schedule`. Never loop
`post schedule` across platforms without that confirmation; OpusClip's own skill
also gates batches >5. Each X post costs 1 credit.

## Publish — the stagger plan

Default **5 Shorts, one every ~3 days** (configurable up to 10). The plan
staggers them so the channel gets a sustained drip feeding the parent, not a
single-day dump. Each Short's `publish.md` carries its own copy; `PLAN.md`
carries the schedule table. Uploading and scheduling run through the `opusclip`
skill's `post schedule` per platform (see "Cross-platform distribution"), or — for
YouTube only — the `youtube-studio` MCP (`video_upload` + `video_schedule` under
the write-gate) or a manual Studio upload. The same stagger date drives every
platform's `--at` time (converted to UTC).

## This skill does NOT
- A/B test titles or thumbnails (no YouTube API support — Studio UI only).
- Write Shorts scripts with `script-writer` (wrong shape — no CTA, too long).
- Re-run the visual-QA or SFX loop — that's `video-director`'s job on the Short.
- Author the parent long-form video, its voiceover, or its music bed.

## Files / skills referenced
- `docs/creator-patterns.md` §4.2 (the Cleo CTA), §6 WS4 (the hook spec), §5
  (title formulas for the per-Short titles).
- `video-director` (+ `reference/portrait-mode.md`) — the portrait composition
  build; `reference/transcript-timing.md` for filtering the parent transcript.
- `voiceover-elevenlabs-v2` / `transcribe-and-plan-cuts` — VO + transcript.
- `thumbnail-and-title-generator` — the vertical 1080×1920 cover.
- `hyperframes-cli` — `init` / `lint` / `render` from inside each Short folder.
- `opusclip` (plugin skill) — the cross-platform distributor: `post account
  list` / `project create --file --skip-curate` / `post schedule`. Never post to
  the IRL Coder channel (Hard constraint #1).
- `video-publish-qa` — optional post-upload metadata QA per Short.
