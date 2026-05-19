"""Comment moderation and replies.

Reads are cheap (1 unit/page). Writes are 50 units each — a single
``comment_moderate`` on 200 IDs would cost 10,000 units (a full day's quota)
which is why we gate bulk operations behind an explicit ``confirm=True`` and
refuse anything that would consume more than ``BULK_QUOTA_FRACTION_LIMIT`` of
remaining daily quota.

The YouTube Data API does NOT expose comment-heart or pin-by-creator; those
remain Studio-UI-only.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import channel, clients, quota

BULK_THRESHOLD = 5
BULK_QUOTA_FRACTION_LIMIT = 0.25  # refuse if a bulk op would burn >25% of remaining

_MOD_STATUS = {"heldForReview", "published", "rejected"}


def _bulk_guard(n: int, confirm: bool) -> dict | None:
    """Return a refusal payload if the caller failed the bulk gate, else None."""
    if n <= BULK_THRESHOLD:
        return None
    if not confirm:
        return {
            "error": "bulk_confirm_required",
            "reason": (f"This operation affects {n} comments ({n} × 50 = "
                       f"{n * 50} quota units). Re-call with confirm=True "
                       "after presenting the list to the user for approval."),
            "estimated_cost_units": n * 50,
        }
    cost = n * 50
    rem = quota.remaining()
    if rem > 0 and cost > rem * BULK_QUOTA_FRACTION_LIMIT:
        return {
            "error": "quota_safety_refused",
            "reason": (f"This operation would cost {cost} units, which is more "
                       f"than {int(BULK_QUOTA_FRACTION_LIMIT * 100)}% of the "
                       f"{rem} units remaining today. Split into smaller batches."),
            "estimated_cost_units": cost,
            "remaining_quota_units": rem,
        }
    return None


def register(app: FastMCP) -> None:
    # -------- reads --------------------------------------------------------

    @app.tool()
    @clients.http_safe
    def comments_inbox(filter: str = "published", video_id: str | None = None,
                       page_token: str | None = None,
                       page_size: int = 50) -> dict:
        """List comment threads on the channel or one video.

        Quota: 1 unit per page.

        Args:
            filter: ``heldForReview``, ``likelySpam``, ``published``, or ``all``.
            video_id: Restrict to one video; otherwise all channel threads.
            page_token: Pagination token.
            page_size: 1-100.
        """
        params: dict[str, Any] = {
            "part": "snippet,replies",
            "maxResults": max(1, min(100, page_size)),
            "textFormat": "plainText",
        }
        if video_id:
            params["videoId"] = video_id
        else:
            params["allThreadsRelatedToChannelId"] = channel.my_channel_id()
        if filter != "all":
            if filter not in {"heldForReview", "likelySpam", "published"}:
                return {"error": "filter must be heldForReview, likelySpam, published, or all"}
            params["moderationStatus"] = filter
        if page_token:
            params["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.commentThreads().list(**params),
            clients.youtube_data(),
        )
        quota.record("commentThreads.list")
        return {
            "filter": filter,
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
        }

    @app.tool()
    @clients.http_safe
    def comment_thread(thread_id: str, include_replies: bool = True) -> dict:
        """Fetch one comment thread by ID, optionally with replies.

        Quota: 1 unit (plus 1 if ``include_replies`` triggers a comments.list).
        """
        parts = "snippet,replies" if include_replies else "snippet"
        resp = clients.run(
            lambda y: y.commentThreads().list(part=parts, id=thread_id,
                                              textFormat="plainText"),
            clients.youtube_data(),
        )
        quota.record("commentThreads.list")
        items = resp.get("items") or []
        return {"item": items[0] if items else None}

    @app.tool()
    @clients.http_safe
    def comment_replies(parent_id: str, page_token: str | None = None) -> dict:
        """List replies under a given parent comment.

        Quota: 1 unit per page.
        """
        kwargs: dict[str, Any] = {"part": "snippet", "parentId": parent_id,
                                  "textFormat": "plainText", "maxResults": 100}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.comments().list(**kwargs),
            clients.youtube_data(),
        )
        quota.record("comments.list")
        return {"items": resp.get("items") or [],
                "nextPageToken": resp.get("nextPageToken")}

    @app.tool()
    @clients.http_safe
    def comments_search(query: str, video_id: str | None = None,
                        max_pages: int = 4) -> dict:
        """Paginate the inbox and filter client-side by case-insensitive substring.

        Use sparingly — every page costs 1 unit. Caps at ``max_pages`` * 100
        comments scanned.

        Args:
            query: Substring to match (case-insensitive).
            video_id: Restrict to one video.
            max_pages: 1-10.
        """
        q = query.lower()
        matched: list[dict] = []
        token: str | None = None
        scanned = 0
        for _ in range(max(1, min(10, max_pages))):
            params: dict[str, Any] = {
                "part": "snippet,replies",
                "maxResults": 100,
                "textFormat": "plainText",
            }
            if video_id:
                params["videoId"] = video_id
            else:
                params["allThreadsRelatedToChannelId"] = channel.my_channel_id()
            if token:
                params["pageToken"] = token
            resp = clients.run(
                lambda y: y.commentThreads().list(**params),
                clients.youtube_data(),
            )
            quota.record("commentThreads.list")
            for item in resp.get("items") or []:
                scanned += 1
                text = (item.get("snippet", {})
                            .get("topLevelComment", {})
                            .get("snippet", {})
                            .get("textOriginal", "") or "").lower()
                if q in text:
                    matched.append(item)
            token = resp.get("nextPageToken")
            if not token:
                break
        return {"query": query, "scanned": scanned, "matched": matched}

    # -------- writes -------------------------------------------------------

    @app.tool()
    @clients.http_safe
    def comment_reply(parent_id: str, text: str) -> dict:
        """Post a reply under an existing comment thread.

        Quota: 50 units.
        """
        resp = clients.run(
            lambda y: y.comments().insert(
                part="snippet",
                body={"snippet": {"parentId": parent_id, "textOriginal": text}},
            ),
            clients.youtube_data(),
        )
        quota.record("comments.insert")
        return resp

    @app.tool()
    @clients.http_safe
    def comment_update(comment_id: str, text: str) -> dict:
        """Edit one of your own comments.

        Quota: 50 units.
        """
        resp = clients.run(
            lambda y: y.comments().update(
                part="snippet",
                body={"id": comment_id, "snippet": {"textOriginal": text}},
            ),
            clients.youtube_data(),
        )
        quota.record("comments.update")
        return resp

    @app.tool()
    @clients.http_safe
    def comment_moderate(comment_ids: list[str], status: str,
                         ban_author: bool = False,
                         confirm: bool = False) -> dict:
        """Set moderation status on one or more comments.

        Quota: 50 units **per comment**.

        Bulk safety: more than 5 IDs requires ``confirm=True``. The tool refuses
        any batch that would consume more than 25% of remaining daily quota
        (split into smaller batches instead).

        Args:
            comment_ids: IDs to moderate.
            status: ``heldForReview``, ``published``, or ``rejected``.
            ban_author: Only valid when status=``rejected``. Bans the author
                from commenting on your channel going forward.
            confirm: Required if more than 5 IDs are supplied.
        """
        if status not in _MOD_STATUS:
            return {"error": f"status must be one of {sorted(_MOD_STATUS)}"}
        if ban_author and status != "rejected":
            return {"error": "ban_author is only valid when status=rejected"}
        if not comment_ids:
            return {"error": "comment_ids is empty"}
        guard = _bulk_guard(len(comment_ids), confirm)
        if guard:
            return guard
        kwargs: dict[str, Any] = {"id": ",".join(comment_ids),
                                  "moderationStatus": status}
        if ban_author:
            kwargs["banAuthor"] = True
        clients.run(
            lambda y: y.comments().setModerationStatus(**kwargs),
            clients.youtube_data(),
        )
        # Cost is one unit per comment regardless of single API call.
        quota.record("comments.setModerationStatus", multiplier=len(comment_ids))
        return {"moderated": len(comment_ids), "status": status,
                "ban_author": ban_author,
                "quota_units_spent": len(comment_ids) * 50}

    @app.tool()
    @clients.http_safe
    def comment_delete(comment_ids: list[str], confirm: bool = False) -> dict:
        """Permanently delete comments.

        Quota: 50 units per comment. Bulk safety: same gate as
        ``comment_moderate``.
        """
        if not comment_ids:
            return {"error": "comment_ids is empty"}
        guard = _bulk_guard(len(comment_ids), confirm)
        if guard:
            return guard
        clients.run(
            lambda y: y.comments().delete(id=",".join(comment_ids)),
            clients.youtube_data(),
        )
        quota.record("comments.delete", multiplier=len(comment_ids))
        return {"deleted": len(comment_ids),
                "quota_units_spent": len(comment_ids) * 50}
