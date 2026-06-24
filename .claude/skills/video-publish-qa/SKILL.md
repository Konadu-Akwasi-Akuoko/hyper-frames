---
name: video-publish-qa
description: Post-publish packaging QA for an uploaded YouTube video. Reads the live metadata via the youtube-studio MCP, checks title / tags / description / captions against the channel's packaging rules (docs/creator-patterns.md §5–§6), and FIXES what the MCP allows — title, description, tags, thumbnail, and captions — under a strict preview-then-confirm gate. Use after a video is uploaded, or when the user says "QA my upload", "check this video's packaging/metadata", "audit my latest upload", "did I publish that right", "run the publish checklist", "check the tags/title/description/captions on <video>". Takes an explicit video ID or defaults to the channel's latest upload.
---

# video-publish-qa

Publish-time packaging QA for a single uploaded YouTube video. The point is to
catch the silent regressions the flagship hit — captions OFF, three thin tags, a
flat title that doesn't restate the hook — *before* they cost a week of bad
indexing. Read the live metadata, grade title / tags / description / captions
against the corpus packaging rules, fix what the MCP can write, and hand off what
it can't.

This skill builds **on top of** the `youtube-studio` skill. Follow that skill's
conventions verbatim — auth + quota first, cheap reads, and the preview→confirm
write-gate. This file is only the packaging-specific checklist that rides on it.

## MCP write surface

`video_update_metadata` (50u) can WRITE title, description, tags, category, and
privacy. `video_set_thumbnail` (50u) can write the thumbnail. `caption_insert`
(400u) adds a new caption track; `caption_update` (450u) *replaces* an existing
track and needs that track's id from a prior `caption_list(video_id)` (1u) — both
are cost-gated, confirm before calling. `video_upload` / `video_schedule` exist
too but are upload-time, not part of post-publish QA.

## Step 1 — Auth, quota, and resolve the video

1. Per the `youtube-studio` skill: call `auth_status` (stop and tell the user to
   run `uv run youtube-studio-mcp auth` if unauthorized), then `quota_status`.
   Each metadata write is 50u — budget before proposing fixes.
2. Resolve the target:
   - An explicit video ID the user gave, or
   - "my latest upload" → `list_uploads(page_size=1)` and take the top item.
   Confirm the title back to the user so you're QA-ing the right video.
3. If a local `videos/<slug>-<date>/` folder for this video is on disk, note
   `script.md`, `seo/research.json`, and `description.md` — they sharpen the
   checks below. They're optional; degrade gracefully when absent (skip the
   check and say it was skipped, don't guess).

## Step 2 — Read once, grade each field

Read with `videos_get(video_ids=[id], parts=["snippet","contentDetails","status"])`
(1u). Then evaluate each check below and **collect** proposed fixes — write
nothing yet. Each rule traces to `docs/creator-patterns.md` §6 WS3 (and §5 for
titles).

### A. Title — `snippet.title`
- Present, ≤100 chars.
- Matches a §5 template; for this channel's lane prefer the quiet-dominance /
  untold-origin family ("How [Tech] Quietly Took Over…", "The [Tech] That Runs
  the World", "Why [Tech] Refuses to Die").
- Carries a specific number / date / duration where the topic allows.
- ALL-CAPS limited to 1–2 charged words, never the whole line.
- Most curiosity-loaded element (the famous subject, the shock number, the
  question word) **front-loaded** so it survives truncation.
- FAIL → propose 2–3 rewrites; let the user pick.

### B. Title ↔ first spoken line
- Only if local `script.md` is available: the title's core promise must be
  restated in sentence one (the cold open). Diff them; FAIL if the open doesn't
  confirm the title (§6 WS3.1). No `script.md` → skip, and say it was skipped.

### C. Tags — `snippet.tags`
- ≥ ~6 relevant tags. The **first** tag = the exact target keyword (cross-ref the
  top noun in `seo/research.json` if present).
- Flag the three-generic-tags smell (the flagship's "JavaScript, Programming,
  WebDevelopment" failure) — a thin or off-topic set.
- FAIL → propose an ordered ~8–12 tag list: first = the keyword, then the
  searchable nouns the video is actually about.

### D. Description — `snippet.description`
- Leads with a one-paragraph restatement of the hook (the withheld-dependency
  framing), not a dry summary (§6 WS3.3).
- Has chapters/timestamps marking the major reset boundaries, sources, the fixed
  sign-off identity, and a comment-bait sequel offer ("want a part two on X?").
- FAIL/missing → offer to run the `description-writer` skill (it reads
  `script.md` / `transcript.json` / `seo/research.json` and writes
  `description.md`), then propose pasting the result.

### E. Captions — `contentDetails.caption` ("true" / "false")
- Must be **"true"**. If "false" → FLAG (this was the flagship's regression).
  - Offer to run `create-srt-and-translate` (English only) to produce
    `captions.srt` if it doesn't already exist.
  - Then call `caption_insert(video_id, file_path="captions.srt", language="en", name="English")`
    (400u — show `cost_preview` and wait for explicit approval before calling).
  - If the user prefers the manual path: `Studio → Subtitles → Add language →
    English → Upload file → With timing`.
  - Note the payoff: English captions also unlock YouTube auto-translate and the
    Hindi auto-dub the channel's India-heavy audience benefits from.
- If `caption` is already **"true"** but the track is wrong (wrong language, still
  a draft, or garbled timing): don't insert a duplicate. Call `caption_list(video_id)`
  (1u) to get the track id, then **replace** it with `caption_update(caption_id,
  file_path="captions.srt")` (450u — same cost gate as insert). Inserting a second
  same-language track instead of updating is the common mistake here.

## Step 3 — The write gate (title / tags / description / thumbnail / captions)

For every fix the MCP *can* apply, follow the `youtube-studio` write-gate —
**preview-then-confirm, no standing auto-apply:**

1. Show a clear BEFORE → AFTER diff for each field you propose to change.
2. Show `cost_preview(endpoint="videos.update")` (50u) and remaining quota.
3. Wait for an explicit affirmative ("yes", "go ahead"). One affirmative can
   cover a batched metadata write across several fields.
4. Call `video_update_metadata(video_id, title=…, description=…, tags=[…])` with
   only the changed fields. **`tags` is a full-list replacement** — pass the
   complete intended list, not a delta.
   - Going private/unlisted → public requires `confirm_publish=True`. Treat
     publishing as higher-friction; confirm it on its own.
5. A thumbnail swap, if proposed, → `video_set_thumbnail(video_id, path)` after
   its own preview.
6. Caption writes (`caption_insert` / `caption_update`) — always gate behind
   `cost_preview` + explicit user approval; each call costs 400–450 units.

Never auto-apply. Never bulk-write across multiple videos without a per-video
affirmative.

## Step 4 — Report

Summarize three buckets:
- **Passed** — checks that were already good.
- **Fixed** — the diff applied and the units spent.
- **Manual** — anything the user chose to handle in Studio themselves (e.g. preferred not to spend the 400u on caption_insert), with the exact click path so they can finish it now.

## This skill does NOT
- A/B test titles or thumbnails (no YouTube API support — Studio UI only).
- Auto-apply any metadata change without an explicit affirmative.
- Triage comments (that's the `youtube-studio` comment-triage workflow).
- Author titles/descriptions from scratch beyond proposing fixes — for a full
  description, defer to `description-writer`.

## Files / skills referenced
- `docs/creator-patterns.md` §5 (title formulas), §6 WS3 (packaging rules).
- `youtube-studio` skill — auth/quota + write-gate conventions; the MCP tools and
  their costs.
- `description-writer` skill — for description (re)generation.
- `create-srt-and-translate` skill — English `captions.srt` for the caption
  hand-off.
