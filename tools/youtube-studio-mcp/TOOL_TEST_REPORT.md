# youtube-studio MCP — tool test report

> **Status (2026-05-19):** All 4 code bugs listed in § "Findings &
> recommended fixes" #1–#4 are resolved and re-verified end-to-end.
> See `FIX_ITERATIONS.md` for the per-iteration change log and
> `test_driver.py` for the in-process verification harness (run with
> `uv run python test_driver.py`).
> Findings #5–#7 are upstream / behavioural, not fixable in this MCP.

End-to-end smoke test of every tool exposed by `youtube-studio-mcp`.
Generated 2026-05-19 against the live `IRL Coder` channel
(`UCfWQCu9N56U5B_tPJ-nh0Ow`, 1 video, 3 subscribers, 34 lifetime views).

- **Auth state:** all 4 scopes granted (`yt-analytics.readonly`,
  `yt-analytics-monetary.readonly`, `youtube.readonly`,
  `youtube.force-ssl`); token at
  `~/.config/youtube-studio-mcp/token.json`.
- **Quota at start:** 9 998 / 10 000.
- **Quota at end:** 9 586 / 10 000 — **414 units spent** across the sweep.
- **Test video:** `0wimpfFJRvw` — "How a CAPTCHA decides you're human
  before you click", 6:28, public.
- **Window for analytics calls:** last 28 days (2026-04-21 → 2026-05-18).

## Summary table

| # | Tool | Status | Cost (units) | Notes |
|---|---|---|---|---|
| 1 | `auth_status` | OK | 0 | Returned full scope list + token path. |
| 2 | `quota_status` | OK | 0 | Local SQLite ledger, no API call. |
| 3 | `cost_preview` | OK | 0 | Tested known + unknown endpoints. Unknown → silent default `1 unit`. |
| 4 | `my_channel` | OK | 1 | Full snippet/branding/statistics. |
| 5 | `list_uploads` | OK | 1 | 1 video returned. |
| 6 | `videos_get` | OK | 1 | Hydrated `0wimpfFJRvw` with snippet+contentDetails+statistics+status. |
| 7 | `top_videos` | OK | 2 | Single row (lone video); includes `lifetime_views`. |
| 8 | `compare_videos` | OK ⚠️ | 1 | Accepts 1 ID despite docstring saying 2–50. |
| 9 | `retention_curve` | OK | 1 | 100 buckets (0.01 → 1.0). Sharp drop 0→0.25, flat at 14.81% after 0.32. |
| 10 | `traffic_sources` (detail=false) | OK | 1 | 8 source types broken out. |
| 10b | `traffic_sources` (detail=true) | **FAIL** | 1 | HTTP 400 — `insightTrafficSourceDetail` rejected without per-source filter. Tool builds an unsupported query. |
| 11 | `demographics` | OK (empty) | 1 | No data — channel too new for demographic threshold. |
| 12 | `device_breakdown` | OK | 1 | 7 device/OS combos. Mobile dominant (53% of views). |
| 13 | `geo_breakdown` | OK (empty) | 1 | No data at country level. |
| 14 | `subs_delta` | OK | 1 | 1 subscriber gained on 2026-05-13, otherwise flat. |
| 15 | `revenue_summary` | OK (empty) | 1 | Scope granted (`available: true`) but no rows — channel not monetised. |
| 16 | `analytics_query` (valid) | OK | 1 | Daily views/watch-time over 28d. |
| 16b | `analytics_query` (invalid metric) | **FAIL** | 1 | HTTP 400 raised as `HttpError`, not wrapped — call propagates the upstream exception. |
| 17 | `comments_inbox` (all) | OK | 1 | 2 threads, both already replied to. |
| 18 | `comments_search` | OK | 1 | Scanned 2, matched 0 (query `great`). |
| 19 | `comment_thread` | OK | 2 | Returned thread + 1 reply (include_replies=true). |
| 20 | `comment_replies` | OK | 1 | 1 reply under thread. |
| 21 | `playlists_list` | OK | 1 | 1 playlist (`IRLCoder Uploads`). |
| 22 | `playlist_items` | OK | 1 | 1 item — references deleted video `5h1DAfMOiy0`. |
| 23 | `subscriptions_list` | OK | 50 (cached 24h) | 1 sub (Zyger). |
| 24 | `warehouse_status` | OK | 0 | 11 jobs, last sync 03:31 UTC, `row_counts_by_table: {}`. |
| 25 | `warehouse_sync` | OK | 0 | `ingested_reports: 0` — Reporting CSVs not yet produced upstream (jobs <24h old). |
| 26 | `warehouse_query` (SELECT) | OK | 0 | Returned `_meta`, `_synced_reports` system tables. |
| 26b | `warehouse_query` (DROP) | OK (refused) | 0 | `{error: "sql_refused", reason: "only SELECT/WITH/UNION allowed, got Drop"}` — validator works. |
| 27 | `report_types_list` | OK | 0 | 20 report types exposed for this account (14 channel-level + 6 playlist-level). |
| 28 | `report_jobs_list` | OK | 0 | 11 active jobs. |
| 29 | `report_jobs_ensure_standard` | OK | 0 | Idempotent on first call (`created: []`); after a delete it recreated only the missing one. |
| 30 | `report_job_delete` | OK | 0 | Deleted `channel_subtitles_a3` job; recreated via ensure_standard with a fresh ID. |
| 31 | `group_create` | **FAIL** | 0 | HTTP 403 `caller does not have permission`. Analytics-groups API appears not enabled for this channel; not a tool bug. |
| 32 | `group_list` | OK (empty) | 0 | `items: []`. |
| 33 | `group_items` (fake ID) | **FAIL** | 0 | HTTP 404 raised as `HttpError` — no soft-error wrapping. |
| 34 | `group_delete` | **NOT EXERCISED** | – | No group existed to delete (create failed, list empty). |
| 35 | `search_external` | OK | 100 | 5 external CAPTCHA videos; response includes explicit `quota_units_spent: 100`. |
| 36 | `comment_reply` | OK | 50 | Posted reply on `UgxlhMDGBhjxQ32WndV4AaABAg`. New ID `UgxlhMDGBhjxQ32WndV4AaABAg.AWmIH5jPOo7AWyqz-Y7aCp`. |
| 37 | `comment_update` | OK | 50 | Edited the new reply to "Appreciate it.". |
| 38 | `comment_moderate` (1 ID, no confirm) | OK | 50 | `quota_units_spent: 50`. |
| 38b | `comment_moderate` (6 IDs, no confirm) | OK (gate fired) | 0 | Structured refusal: `bulk_confirm_required` with cost estimate. |
| 39 | `comment_delete` | **NOT EXERCISED** | – | Excluded per user (destructive on real audience comments). |
| 40 | `video_update_metadata` | OK ×2 | 100 | Added `mcp-test` tag, then removed it. `previous_privacy: public` reported on both. |
| 41 | `video_set_thumbnail` | **NOT EXERCISED** | – | Excluded per user (no thumbnail asset provided). |
| 42 | `ListMcpResourcesTool` | OK | 0 | 3 workflow resources listed. |
| 43 | `ReadMcpResourceTool` | OK ×3 | 0 | `workflow://recommendation-loop`, `comment-triage`, `weekly-review` — all rendered as markdown. |

**Counts:** 38 of 41 tools directly exercised; 3 deferred (1 blocked by
upstream permission, 2 skipped per user). 4 expected-failure / error-path
tests run alongside the happy paths. Zero unrecoverable state changes
left on the channel beyond the one extra public reply noted below.

---

## Per-tool detail

### Meta tier (`tools/meta.py`)

#### `auth_status`
- **Quota:** 0. Never raises.
- **Result:** `authorized: true`, all 4 scopes, channel
  `IRL Coder / UCfWQCu9N56U5B_tPJ-nh0Ow`.
- **Token expiry returned:** 2026-05-19T04:23:13 (refresh handled
  transparently by `clients.py`).

#### `quota_status`
- **Quota:** 0. Reads `~/.config/youtube-studio-mcp/quota.db`.
- **At start:** `2 / 10 000` (some prior reads from earlier today).
- **At end:** `414 / 10 000`. Reset at `2026-05-19T08:00:00+00:00`
  (midnight PT).

#### `cost_preview`
- **Quota:** 0. Pure dictionary lookup.
- Tested two endpoints:
  - `comments.setModerationStatus × 10` → 500 units, `would_exceed_cap: false`.
  - `search.list × 1` → 100 units.
  - `does.not.exist × 1` → **silently defaults to 1 unit**. Worth knowing —
    typo in the endpoint name will under-report cost rather than error.

---

### Data API tier (`tools/data.py`)

#### `my_channel`
- **Quota:** 1 unit. Cached.
- Returns full `channels.list?mine=true` payload with
  `snippet,contentDetails,statistics,status,brandingSettings,topicDetails`.
- Surfaced `customUrl: @irlcoder`, `country: GH`, monetisation off,
  uploads playlist `UUfWQCu9N56U5B_tPJ-nh0Ow`.

#### `list_uploads`
- **Quota:** 1 unit per page. `page_size=5` returned the single existing
  video plus a `null` `nextPageToken`.

#### `videos_get`
- **Quota:** 1 unit per ≤50 IDs. Called with `["0wimpfFJRvw"]`.
- Includes default parts
  `snippet,contentDetails,statistics,status`. Statistics on the test
  video: 34 views, 1 like, 1 dislike, 4 comments.

#### `search_external`
- **Quota:** 100 units (the response also reports
  `quota_units_spent: 100`).
- Query `"how captchas work"` → 5 results (Techquickie, ABC iview,
  Oxylabs, WSJ, Tech Fury). Pagination token present.
- Refusal-on-self-channel guard not exercised (separate code path,
  documented in `data.py`).

---

### Playlists & subscriptions (`tools/data.py`)

#### `playlists_list`
- **Quota:** 1. Returned the lone playlist `IRLCoder Uploads`
  (`PLRnHKMkLUpuMevY1e86Gx1InpFGhximHh`).

#### `playlist_items`
- **Quota:** 1. Returned 1 item — note: its `videoId` `5h1DAfMOiy0`
  resolves to a deleted video; tool surfaces it verbatim with title
  `"Deleted video"`. No filtering. (Likely worth a TODO in the MCP, but
  it correctly reflects upstream state.)

#### `subscriptions_list`
- **Quota:** 50 units, but cached 24h. Returned the channel's single
  subscription (`Zyger`, `UCvYUyKg7wDj760PippmWhig`). Subsequent calls
  today should be free.

---

### Analytics tier (`tools/analytics.py`)

#### `top_videos`
- **Quota:** 2 units (1 × analytics.reports.query + 1 × videos.list).
- Returned 1 row with hydrated `title`, `thumbnail`, `duration`,
  `lifetime_views`. Useful even for a 1-video channel because it
  attaches lifetime context the analytics query alone lacks.

#### `compare_videos`
- **Quota:** 1 unit.
- **Observation:** the docstring claims "2-50 video IDs"; the tool
  accepted a single ID without complaint. Either tighten the guard or
  drop the constraint from the doc.

#### `retention_curve`
- **Quota:** 1 unit.
- Returned 100 buckets. Useful shape on this video: 92.6% retain past
  the first second, drops to ~30% by the 20% mark, flattens at 14.81%
  from the 32% mark to the end. Relative retention performance peaks
  at 0.49 around the 50% bucket — a known "midpoint anchor" pattern.

#### `traffic_sources`
- `detail=false` → OK. 8 source types, ranked: `EXT_URL` 9 views,
  `YT_SEARCH` 7, `RELATED_VIDEO` 5, `SUBSCRIBER` 2, etc.
- **`detail=true` failed** with HTTP 400:
  `"The query is not supported"`. The Analytics API's
  `insightTrafficSourceDetail` dimension requires a filter on
  `insightTrafficSourceType==<one of EXT_URL|YT_SEARCH|...>`. The tool
  currently sends the dimension with only `sort=-views` and no per-type
  filter, which Google rejects. **Bug to fix in `tools/analytics.py`**:
  detail mode should iterate over the by-type rows and issue one
  filtered query per source.

#### `demographics`
- 1 unit. Returned `rows: []` — no surprise, channel has 34 lifetime
  views and YouTube suppresses demographic data below a privacy
  threshold (~100 distinct viewers).

#### `device_breakdown`
- 1 unit. 7 rows. Mobile iOS dominant (12 views, 9 min watched), then
  Mobile Android, Desktop Windows/Mac, plus TV (RokuOS, WebOS) and one
  iPad. Clean output.

#### `geo_breakdown`
- 1 unit. Empty at country level (same privacy threshold). Tool itself
  worked.

#### `subs_delta`
- 1 unit. Daily granularity over 28d. Sole gain on 2026-05-13. No
  losses.

#### `revenue_summary`
- 1 unit. `available: true` (monetary scope present) but
  `rows: []` — channel monetisation not enabled, so no revenue rows.
  The graceful `{available, reason}` shape was not exercised; if the
  monetary scope had been denied, the tool would have returned that
  shape instead of erroring.

#### `analytics_query`
- 1 unit. Daily `views,estimatedMinutesWatched,averageViewDuration`
  over 28d returned 4 rows.
- **Bad-metric path:** `metrics="notARealMetric"` raised an
  uncaught `HttpError 400` — `"Unknown identifier (notARealMetric)
  given in field parameters.metrics"`. Not a soft error; callers must
  try/except. Consistent with most analytics tools — the MCP server
  prefers to pass upstream errors through.

---

### Groups (`tools/analytics.py`)

#### `group_create` — **FAIL (upstream)**
- HTTP 403 `caller does not have permission`. The YouTube Analytics
  Groups API is gated on a separate enrollment that this channel does
  not have. The tool itself fired correctly; this is upstream config.
- Note: skill description says groups can be reused as
  `filters=group==ID` across other analytics queries. Without
  group_create, that workflow is currently unavailable for this
  account.

#### `group_list`
- 0 units. Returned `items: []` (consistent with create failing).

#### `group_items` (with fake ID)
- HTTP 404 raised as `HttpError`. Same pattern as
  `analytics_query` — no soft-error wrapping.

#### `group_delete` — **NOT EXERCISED**
- Would have nothing to act on; create blocked, list empty.

---

### Comments tier (`tools/comments.py`)

#### `comments_inbox`
- 1 unit. `filter="all"` returned 2 threads (both with replies from
  `@IRLCoder`). Snippet, author, like count, and reply preview all
  present.

#### `comments_search`
- 1 unit. `query="great"` scanned 2 comments, matched 0. Returns
  `{scanned, matched}` not raw API payload — useful summary shape.

#### `comment_thread`
- 1 unit base + 1 unit when `include_replies=true`. Returned the
  exact same thread `comments_inbox` did, plus the reply.

#### `comment_replies`
- 1 unit. Returned 1 reply under the queried parent.

#### `comment_reply`
- 50 units. Posted a real reply on the
  `UgxlhMDGBhjxQ32WndV4AaABAg` thread (under
  `@CoolDogeIsCool1030`'s comment, sibling to the existing
  `@IRLCoder` reply). New comment ID
  `UgxlhMDGBhjxQ32WndV4AaABAg.AWmIH5jPOo7AWyqz-Y7aCp`,
  initial text `"Appreciate it — more videos in this format on the way."`.

#### `comment_update`
- 50 units. Edited the new reply text to `"Appreciate it."`.
  `updatedAt` advanced.

#### `comment_moderate`
- **1 ID, no confirm:** OK. `{moderated: 1, status: "published",
  ban_author: false, quota_units_spent: 50}`. Idempotent on
  already-published comments.
- **6 IDs, no confirm:** structured refusal,
  `{error: "bulk_confirm_required", reason: "...300 quota units...",
  estimated_cost_units: 300}`. Gate works exactly as documented.

#### `comment_delete` — **NOT EXERCISED**
- Skipped per user direction. Same bulk gates as `comment_moderate`
  per the schema.

---

### Edits tier (`tools/edits.py`)

#### `video_update_metadata`
- Called twice on `0wimpfFJRvw`:
  1. Added `mcp-test` to the tag list (4 tags total) — 50 units.
  2. Removed it, restoring original 3 tags — 50 units.
- Response includes `previous_privacy: public`, so the privacy guard
  (`private → public` requires `confirm_publish=True`) was not
  triggered. The `confirm_publish` path is documented but not
  exercised here (would need a private video).
- Snippet was patched atomically; `categoryId` was preserved
  automatically (the tool fetches and re-uses existing `categoryId`
  when only other snippet fields are changed).

#### `video_set_thumbnail` — **NOT EXERCISED**
- Skipped per user direction. Schema documents: ≤2 MB JPEG/PNG,
  warning (not error) on non-1280×720 dimensions, 50 units.

---

### Reporting / warehouse tier (`tools/reporting.py`)

#### `report_types_list`
- 0 units (Reporting API, separate quota). Returned 20 report types
  (14 `channel_*` + 6 `playlist_*`).

#### `report_jobs_list`
- 0 units. 11 jobs already exist from a prior
  `report_jobs_ensure_standard` run at 03:31 UTC today.

#### `report_jobs_ensure_standard`
- **First call:** `created: []`, `created_count: 0` — idempotent.
- **After `report_job_delete`:** correctly identified the single
  missing job (`channel_subtitles_a3`) and recreated it with a fresh
  UUID. New `id: e724f92a-4e4c-4a3e-9dc9-7504260872da`.

#### `report_job_delete`
- 0 units. Deleted the original `channel_subtitles_a3` job. Returned
  `{deleted_job_id: ...}`. Previously-ingested rows would have
  remained in `warehouse.db` per the docstring (none existed here, so
  nothing to verify).

#### `warehouse_status`
- 0 units. 11 jobs listed, `last_sync_at: 2026-05-19T03:31:40+00:00`,
  `row_counts_by_table: {}`. Reporting CSVs take ~24h to appear after
  a job is created; jobs are <12h old, so no data has been ingested
  yet.

#### `warehouse_sync`
- 0 units. `ingested_reports: 0` — consistent with the above. Will
  start ingesting once Google produces the first CSVs.

#### `warehouse_query`
- **`SELECT name FROM sqlite_master ...`** → returned `_meta` and
  `_synced_reports` (the two bookkeeping tables; no data tables yet).
- **`DROP TABLE _meta`** → structured refusal:
  `{error: "sql_refused", reason: "only SELECT/WITH/UNION allowed,
  got Drop"}`. Validator confirmed.

---

### Resources

#### `ListMcpResourcesTool` / `ReadMcpResourceTool`
- 3 workflow resources discoverable:
  - `workflow://recommendation-loop`
  - `workflow://comment-triage`
  - `workflow://weekly-review`
- All readable as `text/markdown`. Contents match the
  `tools/youtube-studio-mcp/src/youtube_studio_mcp/resources/workflows.py`
  templates.

---

## Findings & recommended fixes

1. **`traffic_sources(detail=true)` is broken.** The
   `insightTrafficSourceDetail` dimension cannot be queried without a
   `insightTrafficSourceType==…` filter. Fix in `tools/analytics.py`
   should iterate over the `by_type` result rows and issue one filtered
   query per non-trivial source, then merge.
2. **`compare_videos` accepts 1 video** despite the docstring saying
   "2–50". Either enforce the lower bound or drop the constraint from
   the doc.
3. **HTTP errors from Analytics, Data, and Groups APIs propagate raw.**
   `analytics_query` (bad metric), `group_items` (bad ID), and
   `traffic_sources(detail=true)` all surface `googleapiclient.errors.HttpError`
   to the MCP client unwrapped. The comments and warehouse tiers wrap
   errors in structured `{error, reason}` payloads. The inconsistency
   makes higher-level code harder to write — consider standardising on
   the structured shape, at least for known 4xx classes (400 invalid,
   403 forbidden, 404 not found).
4. **`cost_preview` defaults unknown endpoints to 1 unit silently.** A
   typo in the endpoint name will under-report. Either raise on
   unknown endpoints or surface `"endpoint_unknown": true` in the
   response.
5. **`group_create` 403** is upstream — this channel doesn't have
   Analytics Groups enabled. Tools downstream of groups
   (`group_items`, `group_delete`, `filters=group==…`) are effectively
   inert here until that's fixed in YouTube Studio.
6. **`playlist_items` surfaces deleted videos verbatim** (`"Deleted
   video"` title, no thumbnails). Faithful to the API, but consumers
   may want a filter flag.
7. **Reporting pipeline cold-start lag.** New jobs need ~24h before
   the first CSV exists. Until then `warehouse_sync` returns
   `ingested_reports: 0` and `warehouse_query` against any data table
   would fail (no tables exist yet). Document this so the first run
   isn't misread as a bug.

---

## State changes left on the channel

| Change | Restored? |
|---|---|
| Posted reply `UgxlhMDGBhjxQ32WndV4AaABAg.AWmIH5jPOo7AWyqz-Y7aCp` ("Appreciate it.") | **No** — `comment_delete` was excluded from the sweep. The reply is public under `@CoolDogeIsCool1030`'s thread on the CAPTCHA video. |
| Added `mcp-test` tag to `0wimpfFJRvw` | Yes — removed in a follow-up `video_update_metadata` call. Final tag list matches the pre-test state: `["captcha", "recaptcha", "cybersecurity"]`. |
| Deleted reporting job `channel_subtitles_a3` (`5960b1ae-…`) | Yes — recreated by `report_jobs_ensure_standard` with a new ID `e724f92a-4e4c-4a3e-9dc9-7504260872da`. Functionally equivalent; the old UUID is permanently gone. |

To clean up the lingering reply later, call
`comment_delete(comment_ids=["UgxlhMDGBhjxQ32WndV4AaABAg.AWmIH5jPOo7AWyqz-Y7aCp"])`.
