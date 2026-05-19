---
name: youtube-studio
description: Read YouTube channel analytics, moderate comments, and edit video metadata via the youtube-studio MCP server. Use when the user asks "how is my channel doing", "what's working / what's not", "moderate my held comments", "rewrite this video's title/description/tags", "set a thumbnail on this video", "what should I do next on YouTube", "weekly channel review", or anything that requires reading or acting on YouTube Studio data. The skill encodes the cheap-quota call orders and the write-gate rules — invoke it before reaching for any `mcp__youtube-studio__*` tool.
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

### Specific gates baked into the tools

- `comment_moderate(comment_ids=[>5 ids])` → requires `confirm=True`. The tool
  also refuses any batch that would cost > 25% of remaining daily quota.
- `comment_delete(comment_ids=[>5 ids])` → same gate.
- `video_update_metadata(privacy_status="public")` when previous status was
  `private` or `unlisted` → requires `confirm_publish=True`. Treat going-public
  as a higher-friction action than any other edit.

## YouTube API gaps you'll hit

If the user asks for these, tell them up front — don't waste a turn searching:

- **Heart a comment** — no API. Studio UI only.
- **Pin a comment** — no API. Studio UI only.
- **Upload a video** — deferred to v2 of this MCP. Studio/desktop only for now.
- **Edit / upload captions** — deferred to v2.
- **Schedule a livestream** — deferred to v2.

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
