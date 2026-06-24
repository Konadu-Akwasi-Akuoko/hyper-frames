# youtube-studio-mcp — project notes

Python MCP server (FastMCP, stdio) wrapping the YouTube **Analytics API v2**,
**Reporting API v1**, and **Data API v3** for a single creator. Started by
Claude Code via the `.mcp.json` at the repo root.

## Scope (v2 — full write surface open)

Exposed write tools (all gated writes need `confirm=True`):
- Videos/Shorts: video_upload (resumable), video_update_metadata, video_set_thumbnail,
  video_delete, video_rate, video_schedule / video_cancel_schedule,
  video_set_localizations.
- Captions: caption_list, caption_insert (400u), caption_update (450u),
  caption_delete, caption_download.
- Playlists: playlist_create/update/delete, playlist_add_video,
  playlist_item_remove, playlist_set_image / playlist_delete_image.
- Channel: channel_update_branding, channel_section_create/update/delete,
  channel_set_banner, channel_set_watermark / channel_unset_watermark.
- Subscriptions: subscription_add / subscription_remove.

Gated (confirm=True): all deletes, video_rate, public/scheduled upload,
video_schedule, private->public, channel branding/banner/watermark,
subscriptions. captions insert/update are quota-guarded (cost gate).

Still NO API anywhere (do not attempt; no endpoint exists): A/B Test & Compare,
comment settings (allow/hold/disable), end screens, info cards, age restriction,
monetization, multi-language AUDIO dubs (only text localizations are writable),
recording location. Still deferred by choice: live streaming
(liveBroadcasts/liveStreams), CMS/content-owner, multi-channel.

OAuth: `youtube.force-ssl` (already granted) authorizes every write; we also
request `youtube.upload`. No re-consent required for existing tokens.

## YouTube API gaps (not our bugs)

- **No creator-heart on comments.** The heart icon in YouTube Studio is web-UI
  only. There is no `comments.rate` endpoint. Tell the user this if asked.
- **No comment pinning.** Same story. Studio UI only.
- **`comments.markAsSpam` is deprecated.** Use
  `comment_moderate(status="rejected", ban_author=True)` instead.
- **Ad performance dimensions are CMS-only** — not available for individual
  channel reports.

## Quota model — the most important constraint

The **Data API v3 daily quota is 10,000 units per project** and resets at
midnight Pacific Time. Analytics and Reporting APIs use separate, effectively
unbounded quotas for a single creator.

The local ledger lives at `~/.config/youtube-studio-mcp/quota.db` and is queried
by the `quota_status` tool. Cost per endpoint:

| Endpoint | Units |
|---|---|
| `channels.list`, `videos.list`, `playlistItems.list`, `playlists.list` | 1 |
| `commentThreads.list`, `comments.list` | 1 |
| `subscriptions.list` | **50** (cached 24h here) |
| `videos.update`, `thumbnails.set`, `comments.*` (insert/update/setModerationStatus/delete) | 50 |
| `captions.list`, `captions.delete` | 50 |
| `captions.download` | 200 |
| `captions.insert` | 400 |
| `captions.update` | 450 |
| `search.list` | **100** |

### Quota rules of thumb baked into the code

1. **Never `search.list` your own videos.** Use `list_uploads` (1 unit/page).
   The `search_external` tool refuses if `channel_id` resolves to the
   authenticated channel.
2. **Always batch `videos.list`.** Up to 50 IDs per call. The `videos_get` tool
   chunks automatically.
3. **Bulk comment mutations require `confirm=True`** beyond 5 IDs, and refuse
   if they would consume > 25% of remaining daily quota.
4. **`private → public` privacy transitions require `confirm_publish=True`.**

## File layout

```
src/youtube_studio_mcp/
├── server.py           # FastMCP entry — registers all tool/resource modules
├── cli.py              # argparse: auth, serve, sync
├── auth.py             # OAuth installed-app flow + token persistence
├── clients.py          # lazy-built googleapiclient services + retry
├── paths.py            # ~/.config/youtube-studio-mcp/ resolver
├── logging_setup.py    # stderr-only logging w/ credential redaction
├── channel.py          # process-cached my_channel_id, my_uploads_playlist_id
├── quota.py            # per-day Data API ledger + cost preview
├── cache.py            # SQLite (endpoint, params, day) result cache
├── warehouse.py        # Reporting API jobs + CSV → SQLite ingest + SQL validator
├── tools/
│   ├── meta.py         # auth_status, quota_status, cost_preview
│   ├── data.py         # Data API v3 reads
│   ├── analytics.py    # Analytics API reports.query wrappers + groups
│   ├── comments.py     # commentThreads + comments (read + write)
│   ├── edits.py        # videos.update + thumbnails.set
│   └── reporting.py    # Reporting API + warehouse_query
└── resources/
    └── workflows.py    # workflow://{recommendation-loop,comment-triage,weekly-review}
```

## State files

All under `~/.config/youtube-studio-mcp/` (mode `0700`):

- `client_secret.json` — Google OAuth desktop client (user-provided once)
- `token.json` — refresh token (mode `0600`)
- `quota.db` — Data API spend ledger
- `cache.db` — read-call result cache
- `warehouse.db` — Reporting API ingested rows

Path overrides via env: `YOUTUBE_STUDIO_MCP_CONFIG_DIR` (whole dir) or
`YOUTUBE_STUDIO_MCP_TOKEN_PATH` (token only).

## OAuth scopes requested

All four at first consent (avoids re-consent later):

- `yt-analytics.readonly`
- `yt-analytics-monetary.readonly`
- `youtube.readonly`
- `youtube.force-ssl`

`revenue_summary` is gated on the monetary scope and returns
`{available: false, reason: ...}` rather than crashing if it was denied.

## stdio rules

Logging goes to stderr only — writing to stdout corrupts the JSON-RPC stream
the client reads. Credential strings are redacted by a logging filter before
any record is emitted (matches `access_token`, `refresh_token`, `Bearer xxx`,
`ya29.*`, and OAuth JSON keys).

## Verification

```bash
uv sync
uv run youtube-studio-mcp auth          # one-time
uv run youtube-studio-mcp --help
npx @modelcontextprotocol/inspector \
  uv --directory tools/youtube-studio-mcp run youtube-studio-mcp serve
```

In the inspector: call `auth_status` first; expect `authorized: true` with the
channel ID. Then `quota_status`, `my_channel`, `list_uploads`, `top_videos`.
