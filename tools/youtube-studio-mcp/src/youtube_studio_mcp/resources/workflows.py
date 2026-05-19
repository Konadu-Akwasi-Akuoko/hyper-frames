"""MCP resources documenting call-order patterns for common workflows.

Resources are not callable endpoints — they're documents the host (Claude Code)
can surface to the model as guidance. We expose three workflows here:
``recommendation-loop``, ``comment-triage``, and ``weekly-review``.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


RECOMMENDATION_LOOP = """\
# Recommendation loop

Use when the user asks "what should I do next" / "what's working" / "review my
channel" / similar open-ended growth question.

## Call order

1. `auth_status()` — verify scopes; if `authorized=false`, tell the user to run
   `youtube-studio-mcp auth` and stop.
2. `quota_status()` — note remaining Data API units. If < 1000, prefer
   `warehouse_query` over live `analytics_query` where possible.
3. `my_channel()` — anchor on identity (handle, subscriber count, total views).
4. **Long-range trend baseline** — `warehouse_query` against the SQLite
   warehouse if it's been populated by `warehouse_sync`; otherwise
   `analytics_query` over the last 90 days.
5. `top_videos(metric="estimatedMinutesWatched", days=28, n=10)` — the
   current-attention list. Use the returned `lifetime_views` and `publishedAt`
   to spot recent hits.
6. For each outlier (top 1-3 and any surprise), call `retention_curve(video_id)`
   to find drop-off points.
7. `traffic_sources(days=28, detail=True)` — where the watch time is coming
   from. Browse features dominance is a discovery problem; suggested/related
   dominance is a thumbnail/title problem.
8. `subs_delta(days=28)` — net subs trajectory.
9. Synthesize: name the 1-2 most actionable changes (rename, re-thumbnail,
   double-down on a topic) and stop. Don't list every metric — name the move.

## Anti-patterns

- Don't reach for `search_external` to enumerate the creator's own videos
  (uses 100 units; `list_uploads` costs 1).
- Don't run `analytics_query` over an 18-month window when a single
  `warehouse_query` returns the same data without quota.
"""


COMMENT_TRIAGE = """\
# Comment triage

Use when the user asks "moderate my held-for-review queue" / "clean up my
comments" / "what's in the spam folder".

## Call order

1. `auth_status()` — confirm `youtube.force-ssl` scope is granted.
2. `comments_inbox(filter="heldForReview", page_size=50)` — the actual queue.
3. Show the user a numbered list of comments with author, text, and video.
   **Stop and wait for explicit selection.** Do not bulk-moderate without
   approval — the API costs 50 units per comment.
4. After approval: `cost_preview(endpoint="comments.setModerationStatus",
   multiplier=N)` and show the units that will be spent.
5. Then: `comment_moderate(comment_ids=[...], status="published"|"rejected",
   ban_author=False|True, confirm=True)`.
6. For obvious spam (links to non-YouTube domains, repeated copy-pasted text),
   default `status="rejected"` with `ban_author=True`.
7. For genuine comments worth a reply: `comment_reply(parent_id, text)` —
   the reply itself does not require approval since the user has explicitly
   asked for it, but show the proposed reply text first.

## Anti-patterns

- Don't call `comment_moderate` with more than 5 IDs without `confirm=True` —
  the tool will refuse.
- Don't moderate the entire queue in one shot if it would exceed 25% of
  remaining quota — split into batches.
- `comments.markAsSpam` is NOT a tool here (deprecated upstream). Use
  `status="rejected"` with `ban_author=True` instead.
- There is NO `comment_heart` / `comment_pin` — the YouTube API does not
  expose these. If the user asks, tell them and point at Studio UI.
"""


WEEKLY_REVIEW = """\
# Weekly review

Use when the user asks for a "weekly summary" / "how was last week" /
"compare this week to last week". Cron-able.

## Call order

1. `auth_status()`, `quota_status()`.
2. `analytics_query(metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
   dimensions="day", start_date=<7 days ago>, end_date=<yesterday>)` — current
   week daily.
3. Same query for the previous 7 days. Diff the totals.
4. `top_videos(metric="estimatedMinutesWatched", days=7, n=5)` — what carried
   the week.
5. `traffic_sources(days=7)` — where it came from.
6. `comments_inbox(filter="heldForReview")` — anything that needs triage.
7. Summarise:
   - WoW: views, watch time, net subs (+/- vs previous week).
   - Top performer: title, watch time, publish age.
   - Surprise: any video > 7 days old that climbed.
   - Action items: 1-3 named, none if numbers are stable.

## Anti-patterns

- Don't include every metric. The point is the WoW delta + one named
  performer + one action.
"""


def register(app: FastMCP) -> None:
    @app.resource("workflow://recommendation-loop", mime_type="text/markdown")
    def _recommendation_loop() -> str:
        return RECOMMENDATION_LOOP

    @app.resource("workflow://comment-triage", mime_type="text/markdown")
    def _comment_triage() -> str:
        return COMMENT_TRIAGE

    @app.resource("workflow://weekly-review", mime_type="text/markdown")
    def _weekly_review() -> str:
        return WEEKLY_REVIEW
