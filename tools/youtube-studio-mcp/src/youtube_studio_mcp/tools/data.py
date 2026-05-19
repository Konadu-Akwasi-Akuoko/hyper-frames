"""YouTube Data API v3 read tools.

Designed for the cheap path: channel + uploads enumeration always goes through
``channels.list`` → uploads playlist → ``playlistItems.list`` (2 units total
plus 1/page) instead of ``search.list`` (100 units/call).
"""

from __future__ import annotations

import math
from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import cache, channel, clients, quota

_DEFAULT_CHANNEL_PARTS = (
    "id,snippet,contentDetails,statistics,status,brandingSettings,topicDetails"
)
_DEFAULT_VIDEO_PARTS = ["snippet", "contentDetails", "statistics", "status"]


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def my_channel() -> dict:
        """Fetch the authenticated channel's full profile.

        Quota: 1 unit (channels.list, cached).

        Returns:
            The first item from ``channels.list?mine=true`` with parts
            ``snippet,contentDetails,statistics,status,brandingSettings,topicDetails``.
        """
        params = {"part": _DEFAULT_CHANNEL_PARTS, "mine": True}
        cached = cache.get("channels.list:mine_full", params)
        if cached is not None:
            return cached
        resp = clients.run(
            lambda y: y.channels().list(part=_DEFAULT_CHANNEL_PARTS, mine=True),
            clients.youtube_data(),
        )
        quota.record("channels.list")
        items = resp.get("items") or []
        out = items[0] if items else {}
        cache.put("channels.list:mine_full", params, out)
        return out

    @app.tool()
    @clients.http_safe
    def list_uploads(page_token: str | None = None, page_size: int = 50) -> dict:
        """Enumerate the authenticated channel's uploaded videos.

        Always uses the uploads-playlist path (cheap: 1 unit per page).
        NEVER use ``search_external`` for self-channel enumeration (100 units/call).

        Quota: 1 unit per page.

        Args:
            page_token: Pagination token from a previous response.
            page_size: 1-50; defaults to 50.

        Returns:
            ``{ items: [...], nextPageToken?, totalResults }``. Each item is a
            ``playlistItem`` with ``snippet`` and ``contentDetails`` (use
            ``videos_get`` for full stats).
        """
        playlist_id = channel.my_uploads_playlist_id()
        params: dict[str, Any] = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max(1, min(50, page_size)),
        }
        if page_token:
            params["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.playlistItems().list(**params),
            clients.youtube_data(),
        )
        quota.record("playlistItems.list")
        return {
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
            "totalResults": (resp.get("pageInfo") or {}).get("totalResults"),
        }

    @app.tool()
    @clients.http_safe
    def videos_get(video_ids: list[str], parts: list[str] | None = None) -> dict:
        """Batched ``videos.list`` for one or more video IDs.

        Use this to hydrate any list of video IDs returned by an Analytics tool
        with titles, thumbnails, durations, and statistics.

        Quota: 1 unit per call of up to 50 IDs (so 200 IDs = 4 units).

        Args:
            video_ids: Up to 1,000 IDs (chunked into 50s internally).
            parts: One or more of ``snippet, contentDetails, statistics, status,
                topicDetails, recordingDetails, fileDetails, liveStreamingDetails,
                localizations, player, processingDetails, suggestions``.
                Defaults to ``snippet,contentDetails,statistics,status``.
        """
        if not video_ids:
            return {"items": []}
        parts_str = ",".join(parts or _DEFAULT_VIDEO_PARTS)
        all_items: list[dict] = []
        chunks = math.ceil(len(video_ids) / 50)
        for i in range(chunks):
            chunk = video_ids[i * 50:(i + 1) * 50]
            resp = clients.run(
                lambda y, c=chunk: y.videos().list(part=parts_str, id=",".join(c)),
                clients.youtube_data(),
            )
            quota.record("videos.list")
            all_items.extend(resp.get("items") or [])
        return {"items": all_items}

    @app.tool()
    @clients.http_safe
    def playlists_list(page_token: str | None = None) -> dict:
        """List the authenticated channel's playlists (50/page).

        Quota: 1 unit per page.
        """
        params: dict[str, Any] = {
            "part": "snippet,contentDetails,status",
            "mine": True,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.playlists().list(**params),
            clients.youtube_data(),
        )
        quota.record("playlists.list")
        return {
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
        }

    @app.tool()
    @clients.http_safe
    def playlist_items(playlist_id: str, page_token: str | None = None,
                       page_size: int = 50) -> dict:
        """List items in a playlist.

        Quota: 1 unit per page.

        Args:
            playlist_id: Any playlist ID (yours or external).
            page_token: Pagination token.
            page_size: 1-50.
        """
        params: dict[str, Any] = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max(1, min(50, page_size)),
        }
        if page_token:
            params["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.playlistItems().list(**params),
            clients.youtube_data(),
        )
        quota.record("playlistItems.list")
        return {
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
        }

    @app.tool()
    @clients.http_safe
    def subscriptions_list(page_token: str | None = None) -> dict:
        """List channels the authenticated user subscribes to.

        Quota: **50 units** per page (this endpoint is expensive). Cached for
        24h — repeated calls in the same day are free.
        """
        params = {"part": "snippet,contentDetails", "mine": True,
                  "maxResults": 50, "pageToken": page_token}
        cached = cache.get("subscriptions.list", params)
        if cached is not None:
            return cached
        kwargs: dict[str, Any] = {"part": "snippet,contentDetails", "mine": True,
                                  "maxResults": 50}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = clients.run(
            lambda y: y.subscriptions().list(**kwargs),
            clients.youtube_data(),
        )
        quota.record("subscriptions.list")
        out = {
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
        }
        cache.put("subscriptions.list", params, out)
        return out

    @app.tool()
    @clients.http_safe
    def search_external(query: str, type: str = "video", max_results: int = 10,
                        channel_id: str | None = None,
                        published_after: str | None = None,
                        order: str = "relevance") -> dict:
        """Search YouTube for external content. **Expensive: 100 units per call.**

        For enumerating your OWN channel's videos, use ``list_uploads`` (1 unit)
        instead. This tool refuses to run if ``channel_id`` resolves to the
        authenticated channel.

        Quota: 100 units (this is 1% of the daily Data API budget per call).

        Args:
            query: Free-text search.
            type: ``video``, ``channel``, or ``playlist``.
            max_results: 1-50.
            channel_id: Restrict to a specific channel (must not be your own).
            published_after: RFC 3339 timestamp (e.g. ``2026-01-01T00:00:00Z``).
            order: ``relevance``, ``date``, ``rating``, ``title``, ``viewCount``,
                ``videoCount``.
        """
        if channel_id:
            try:
                mine = channel.my_channel_id()
                if channel_id == mine:
                    return {
                        "error": "search_external refused",
                        "reason": ("channel_id equals the authenticated channel. "
                                   "Use list_uploads (1 unit) instead of "
                                   "search.list (100 units) for self-enumeration."),
                    }
            except Exception:
                pass
        params: dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "type": type,
            "maxResults": max(1, min(50, max_results)),
            "order": order,
        }
        if channel_id:
            params["channelId"] = channel_id
        if published_after:
            params["publishedAfter"] = published_after
        resp = clients.run(
            lambda y: y.search().list(**params),
            clients.youtube_data(),
        )
        quota.record("search.list")
        return {
            "items": resp.get("items") or [],
            "nextPageToken": resp.get("nextPageToken"),
            "totalResults": (resp.get("pageInfo") or {}).get("totalResults"),
            "quota_units_spent": 100,
        }
