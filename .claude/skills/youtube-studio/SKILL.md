---
name: youtube-studio
description: Read YouTube channel analytics, moderate comments, edit video metadata, upload videos, schedule publishes, and insert/update captions via the youtube-studio MCP server. Use when the user asks "how is my channel doing", "what's working / what's not", "moderate my held comments", "rewrite this video's title/description/tags", "set a thumbnail on this video", "upload this video", "schedule this video", "add captions to this video", "what should I do next on YouTube", "weekly channel review", or anything that requires reading or acting on YouTube Studio data. The skill encodes the cheap-quota call orders and the write-gate rules — invoke it before reaching for any `mcp__youtube-studio__*` tool.
---

# youtube-studio

You have a local MCP server (`youtube-studio`) that wraps the YouTube
Analytics, Reporting, and Data API v3 surfaces. The full tool list and quota
costs are documented in `tools/youtube-studio-mcp/CLAUDE.md`. Read it once if
you haven't.

This skill encodes the things tool descriptions can't, and that you'll
otherwise get wrong:

## Always start with auth + quota

Before calling any YouTube tool, call these two:

1. `auth_status` — never errors. If `authorized: false`, tell the user to run
   `uv run youtube-studio-mcp auth` from inside `tools/youtube-studio-mcp/` and
   STOP. Don't try to continue.
2. `quota_status` — note the remaining Data API units. If < 1000, prefer
   `warehouse_query` for trend questions over live `analytics_query`.

## Cheap-path-first rules (these matter — quota is 10k/day)

| If the user asks for… | Use | Not |
|---|---|---|
| "List my videos" / "my uploads" | `list_uploads` (1 unit/page) | `search_external` (100 units) |
| "Get details on these video IDs" | `videos_get(ids=[...])` — batches 50/call (1 unit each) | one-at-a-time calls |
| "Top videos last month" | `top_videos` — already hydrates titles via batched `videos.list` | a custom `analytics_query` + manual hydration |
| "How have my views trended over 12 months" | `warehouse_query` (free) — if `warehouse_status` shows recent data | `analytics_query` (latency-bound) |
| "Subscribers I subscribe to" | `subscriptions_list` (cached 24h) | repeated calls |
| "Find external competitor videos about X" | `search_external` (100 units — this is its real use case) | — |

If `search_external` is called with `channel_id` equal to the authenticated
channel, the tool refuses and tells you to use `list_uploads`.

## Write gates — always preview, never bulk without consent

Every write tool is `youtube.force-ssl`-scoped and costs 50 units. The pattern
for every write:

1. Read first. `comments_inbox`, `videos_get`, etc.
2. Show the user the proposed change (the comment text, the new title, the
   thumbnail path) and the unit cost (`cost_preview`).
3. Wait for explicit approval — text approval like "yes" or "go ahead" is
   enough; you don't need formal confirmation, but you DO need an affirmative.
4. Then call the write tool with `confirm=True` or `confirm_publish=True`
   where required.

### The gate map — which writes need `confirm`, and why

Per-tool params (full signatures, exact costs) live in the tool descriptions —
fetch them when you call. This is the map the descriptions can't give you: which
writes are gated and the *reason*, so you know when to stop and ask.

| Tool(s) | Gate | Reason |
|---|---|---|
| `video_update_metadata` (tags/title/desc/category), `video_set_thumbnail`, `video_set_localizations`, `playlist_create`/`update`/`add_video`/`item_update`, `channel_section_create`/`update`, `caption_list`/`download` | **none** | trivially reversible edits — still *preview* user-visible changes per the generic gate above |
| `video_update_metadata(privacy_status="public")` from private/unlisted | `confirm_publish=True` | the audience sees it the instant it fires |
| `video_upload` | `confirm=True` **only if** `privacy="public"` or a `publish_at` is set; a private upload is **ungated** | a private draft is harmless; a public/scheduled one is a release |
| `video_schedule` | `confirm=True` | arms an autonomous public release at a future time |
| `caption_insert` (400u), `caption_update` (450u) | `confirm=True` + always `cost_preview` first | the two most expensive writes in the API |
| `video_delete`, `caption_delete`, `playlist_delete`, `playlist_item_remove`, `playlist_delete_image`, `channel_section_delete` | `confirm=True` | irreversible |
| `channel_update_branding`, `channel_set_banner`, `channel_set_watermark`/`unset`, `playlist_set_image` | `confirm=True` | channel-visible, public-facing |
| `subscription_add`/`remove`, `video_rate` | `confirm=True` | acts socially **as your channel** |
| `comment_moderate`/`comment_delete` (>5 ids) | `confirm=True` | bulk; also refuses if >25% of remaining quota |

### Operating notes for the higher-friction writes

These three carry constraints the API enforces but the tool description states
only tersely — get them wrong and the call fails or surprises the user:

- **Upload (`video_upload`).** Defaults to `privacy="private"` — keep it there
  unless the user explicitly wants it public now. A Short is just a vertical
  video ≤3 min: same call, no special flag. Resumable, so large files are fine.
  Gate fires only for public/scheduled (see map).
- **Schedule (`video_schedule`).** Sets `publish_at` (ISO-8601) and forces the
  video to `private`; YouTube auto-flips it public at that time. **The video
  must be private and never previously published** — you can't schedule a video
  that has been public. Convert the user's local time to an explicit offset
  (e.g. `2026-06-26T09:00:00-04:00`), never a bare wall-clock. Reschedule by
  calling again with a new `publish_at`; cancel with `video_cancel_schedule`
  (ungated — it only ever makes the video *less* public).
- **Captions (`caption_insert` / `caption_update`).** Insert a new track with
  `caption_insert(video_id, file_path, language, name)` — an `.srt` uploads
  fine. To *replace* an existing track you need its id: call `caption_list(video_id)`
  first, then `caption_update(caption_id, file_path=...)`. Both are cost-gated
  (400/450u) — `cost_preview` and an affirmative before every call.

Playlists, channel branding, and subscriptions follow the same
preview→`confirm` pattern; lean on the gate map above for which need it.

## YouTube API gaps you'll hit

If the user asks for these, tell them up front — there is no endpoint, so don't
waste a turn searching or reaching for a write tool:

- **Heart a comment** — no API. Studio UI only.
- **Pin a comment** — no API. Studio UI only.
- **A/B "Test & Compare" titles/thumbnails** — no API. Studio UI only.
- **Schedule a livestream** (`liveBroadcasts`) — no API. Studio UI only.
- **Comment settings** (allow/hold/disable), **end screens**, **info cards**,
  **age restriction**, **monetization**, **multi-language *audio* dubs** — all
  Studio-only (only *text* localizations are writable, via `video_set_localizations`).

(Uploads, scheduling, and captions are NOT gaps anymore — see the write surface
and operating notes above.)

## Three canonical workflows

The MCP exposes them as resources (the host can surface them as slash
commands; you should also follow them when the user asks open-ended growth
questions):

- `workflow://recommendation-loop` — "what should I do next on the channel"
- `workflow://comment-triage` — "moderate my queue / clean up comments"
- `workflow://weekly-review` — "how did last week go"

When the user asks an open-ended question that fits one of these, read the
resource first and follow its call order. They're written terse and concrete
so the model doesn't have to invent the right sequence.

## Anti-patterns

- Calling 12 narrow analytics tools when one parameterised `analytics_query`
  would do. The tools we exposed are recipes for common shapes; the escape
  hatch exists for the rest. Don't write a third path.
- Asking the user for clarification when the answer is "look at the resource
  for this workflow". Read the resource, then ask only what's still ambiguous.
- Reading `transcript.json` style — i.e. dumping the full `videos.list` response
  for 200 videos into your context. Filter first; only surface what's relevant
  to the user's question.
- Treating "moderate my last 200 held comments" as something to do silently.
  It's $10k units in one shot. Always present, always wait, always batch.
