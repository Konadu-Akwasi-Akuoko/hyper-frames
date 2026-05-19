"""YouTube Analytics API v2 tools — interactive reports.query wrappers.

All wrap a single endpoint (``reports.query`` on
``youtubeanalytics.googleapis.com``). The Analytics quota is per-project and
effectively unbounded for a single creator; we cache responses keyed on the
full parameter set so re-asking the same question within a turn is free.

Also exposed: a ``groups`` CRUD surface so the model can define reusable
cohorts (\"my Shorts\", \"my tutorials\") that fit cleanly into the
``filters=group==ID`` parameter of any other tool.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import auth, cache, clients


def _ids() -> str:
    return "channel==MINE"


def _date_window(days: int) -> tuple[str, str]:
    end = dt.date.today() - dt.timedelta(days=1)  # yesterday — today is incomplete
    start = end - dt.timedelta(days=max(1, days) - 1)
    return start.isoformat(), end.isoformat()


def _query(*, metrics: str, dimensions: str | None = None,
           filters: str | None = None, start: str, end: str,
           sort: str | None = None, max_results: int | None = None,
           currency: str | None = None) -> dict:
    cache_key_params = {
        "ids": _ids(),
        "metrics": metrics, "dimensions": dimensions, "filters": filters,
        "start": start, "end": end, "sort": sort,
        "max_results": max_results, "currency": currency,
    }
    cached = cache.get("youtubeAnalytics.reports.query", cache_key_params,
                       day_bucket=end)
    if cached is not None:
        return cached
    kwargs: dict[str, Any] = {
        "ids": _ids(),
        "startDate": start,
        "endDate": end,
        "metrics": metrics,
    }
    if dimensions:
        kwargs["dimensions"] = dimensions
    if filters:
        kwargs["filters"] = filters
    if sort:
        kwargs["sort"] = sort
    if max_results:
        kwargs["maxResults"] = max_results
    if currency:
        kwargs["currency"] = currency
    resp = clients.run(
        lambda a: a.reports().query(**kwargs),
        clients.youtube_analytics(),
    )
    cache.put("youtubeAnalytics.reports.query", cache_key_params, resp,
              day_bucket=end)
    return resp


def _rows_with_headers(resp: dict) -> list[dict]:
    headers = [h["name"] for h in resp.get("columnHeaders") or []]
    return [dict(zip(headers, row)) for row in resp.get("rows") or []]


def register(app: FastMCP) -> None:
    @app.tool()
    def analytics_query(metrics: str, start_date: str, end_date: str,
                        dimensions: str | None = None,
                        filters: str | None = None,
                        sort: str | None = None,
                        max_results: int | None = None,
                        currency: str | None = None) -> dict:
        """Generic ``reports.query`` escape hatch.

        Use this when no named tool matches the shape you need. See
        <https://developers.google.com/youtube/analytics/channel_reports> for
        the legal dimension × metric combinations.

        Args:
            metrics: Comma-separated metric names (e.g. ``views,estimatedMinutesWatched``).
            start_date: ISO ``YYYY-MM-DD`` inclusive.
            end_date: ISO ``YYYY-MM-DD`` inclusive.
            dimensions: Optional comma-separated dimensions.
            filters: Optional filter expression (e.g. ``video==VID1,VID2;country==US``).
            sort: Optional sort spec (prefix ``-`` for descending).
            max_results: Optional row cap.
            currency: ISO 4217 (required for revenue metrics).

        Returns:
            ``{ headers: [str], rows: [dict], raw: { ...full API response... } }``
        """
        resp = _query(metrics=metrics, dimensions=dimensions, filters=filters,
                      start=start_date, end=end_date, sort=sort,
                      max_results=max_results, currency=currency)
        return {
            "headers": [h["name"] for h in resp.get("columnHeaders") or []],
            "rows": _rows_with_headers(resp),
            "raw": resp,
        }

    @app.tool()
    def top_videos(metric: str = "estimatedMinutesWatched", days: int = 28,
                   n: int = 10) -> dict:
        """Top N videos for the channel by a chosen metric, hydrated with titles.

        Runs one ``reports.query`` then one ``videos.list`` (1 Data API unit) to
        attach titles, thumbnails, and durations to the analytics rows.

        Args:
            metric: Sort metric — typically ``estimatedMinutesWatched``,
                ``views``, ``subscribersGained``, ``averageViewDuration``.
            days: Window size (last N completed days).
            n: 1-200.
        """
        from .. import quota
        start, end = _date_window(days)
        resp = _query(
            metrics=f"views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,{metric}",
            dimensions="video",
            start=start, end=end,
            sort=f"-{metric}",
            max_results=max(1, min(200, n)),
        )
        rows = _rows_with_headers(resp)
        video_ids = [r["video"] for r in rows if r.get("video")]
        hydrated: dict[str, dict] = {}
        if video_ids:
            yt = clients.youtube_data()
            chunk = video_ids[:50]
            videos_resp = clients.run(
                lambda y, c=chunk: y.videos().list(
                    part="snippet,contentDetails,statistics", id=",".join(c)),
                yt,
            )
            quota.record("videos.list")
            for item in videos_resp.get("items") or []:
                hydrated[item["id"]] = {
                    "title": item["snippet"]["title"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "duration": item["contentDetails"]["duration"],
                    "lifetime_views": int(item["statistics"].get("viewCount", 0)),
                }
        for r in rows:
            vid = r.get("video")
            if vid in hydrated:
                r.update(hydrated[vid])
        return {"window": {"start": start, "end": end, "days": days},
                "metric": metric, "rows": rows}

    @app.tool()
    def retention_curve(video_id: str) -> dict:
        """Audience-retention curve for one video (lifetime).

        Returns watch ratio and relative retention performance at each
        ``elapsedVideoTimeRatio`` bucket (0.0 → 1.0). The shape that tells you
        where viewers drop off and where you out- or under-perform similar
        videos.

        Args:
            video_id: 11-char YouTube video ID.
        """
        start, end = _date_window(365)
        resp = _query(
            metrics="audienceWatchRatio,relativeRetentionPerformance",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id};audienceType==ORGANIC",
            start=start, end=end,
        )
        return {"video_id": video_id, "rows": _rows_with_headers(resp)}

    @app.tool()
    def traffic_sources(days: int = 28, video_id: str | None = None,
                        detail: bool = False) -> dict:
        """Traffic-source breakdown for the channel or one video.

        Args:
            days: Window size.
            video_id: Optional — restrict to one video.
            detail: If True, also returns the per-source detail breakdown
                (capped 25, sort required).
        """
        start, end = _date_window(days)
        filt = f"video=={video_id}" if video_id else None
        top = _query(
            metrics="views,estimatedMinutesWatched",
            dimensions="insightTrafficSourceType",
            filters=filt,
            start=start, end=end,
        )
        out: dict[str, Any] = {
            "window": {"start": start, "end": end, "days": days},
            "video_id": video_id,
            "by_type": _rows_with_headers(top),
        }
        if detail:
            det = _query(
                metrics="views,estimatedMinutesWatched",
                dimensions="insightTrafficSourceDetail",
                filters=filt,
                start=start, end=end,
                sort="-views",
                max_results=25,
            )
            out["by_detail"] = _rows_with_headers(det)
        return out

    @app.tool()
    def geo_breakdown(metric: str = "views", days: int = 28,
                      level: str = "country") -> dict:
        """Geographic breakdown by country, province, or city.

        Args:
            metric: Single metric to slice by location.
            days: Window size.
            level: ``country``, ``province``, or ``city``.
        """
        if level not in ("country", "province", "city"):
            return {"error": "level must be country, province, or city"}
        start, end = _date_window(days)
        resp = _query(
            metrics=f"{metric},estimatedMinutesWatched",
            dimensions=level,
            start=start, end=end,
            sort=f"-{metric}",
            max_results=250,
        )
        return {"level": level, "metric": metric,
                "window": {"start": start, "end": end},
                "rows": _rows_with_headers(resp)}

    @app.tool()
    def device_breakdown(days: int = 28) -> dict:
        """Views + watch time split by device type and operating system."""
        start, end = _date_window(days)
        resp = _query(
            metrics="views,estimatedMinutesWatched",
            dimensions="deviceType,operatingSystem",
            start=start, end=end,
            sort="-views",
        )
        return {"window": {"start": start, "end": end},
                "rows": _rows_with_headers(resp)}

    @app.tool()
    def demographics(days: int = 28) -> dict:
        """Viewer percentage by age group × gender."""
        start, end = _date_window(days)
        resp = _query(
            metrics="viewerPercentage",
            dimensions="ageGroup,gender",
            start=start, end=end,
        )
        return {"window": {"start": start, "end": end},
                "rows": _rows_with_headers(resp)}

    @app.tool()
    def subs_delta(days: int = 28, granularity: str = "day") -> dict:
        """Subscribers gained vs lost over time.

        Args:
            days: Window size.
            granularity: ``day`` or ``month``.
        """
        if granularity not in ("day", "month"):
            return {"error": "granularity must be day or month"}
        start, end = _date_window(days)
        resp = _query(
            metrics="subscribersGained,subscribersLost",
            dimensions=granularity,
            start=start, end=end,
        )
        return {"window": {"start": start, "end": end},
                "granularity": granularity,
                "rows": _rows_with_headers(resp)}

    @app.tool()
    def revenue_summary(days: int = 28, currency: str = "USD") -> dict:
        """Estimated revenue, ad impressions, CPM for the window.

        Gated on the ``yt-analytics-monetary.readonly`` scope. Returns
        ``{available: false, reason}`` instead of erroring if the scope is
        not granted.
        """
        if not auth.has_monetary_scope():
            return {"available": False,
                    "reason": ("yt-analytics-monetary.readonly scope not granted. "
                               "Re-run `youtube-studio-mcp auth` to add it.")}
        start, end = _date_window(days)
        resp = _query(
            metrics=("estimatedRevenue,estimatedAdRevenue,grossRevenue,"
                     "cpm,playbackBasedCpm,adImpressions,monetizedPlaybacks"),
            start=start, end=end,
            currency=currency,
        )
        return {"available": True, "currency": currency,
                "window": {"start": start, "end": end},
                "rows": _rows_with_headers(resp)}

    @app.tool()
    def compare_videos(video_ids: list[str], metrics: list[str],
                       days: int = 28) -> dict:
        """Compare a small set of videos on chosen metrics over a window.

        Args:
            video_ids: 2-50 video IDs.
            metrics: List of metric names.
            days: Window size.
        """
        if not video_ids or len(video_ids) > 200:
            return {"error": "video_ids must be 1..200"}
        start, end = _date_window(days)
        resp = _query(
            metrics=",".join(metrics),
            dimensions="video",
            filters=f"video=={','.join(video_ids)}",
            start=start, end=end,
        )
        return {"window": {"start": start, "end": end},
                "rows": _rows_with_headers(resp)}

    # ---- groups CRUD -------------------------------------------------------

    @app.tool()
    def group_list() -> dict:
        """List Analytics groups defined for the channel.

        Groups are reusable cohorts (up to 500 items) of videos, playlists,
        channels, or assets. They can be passed as ``filters=group==ID`` into
        any other analytics query.
        """
        resp = clients.run(
            lambda a: a.groups().list(mine=True),
            clients.youtube_analytics(),
        )
        return {"items": resp.get("items") or []}

    @app.tool()
    def group_create(name: str, item_ids: list[str],
                     item_type: str = "video") -> dict:
        """Create a new Analytics group and populate it with items.

        Args:
            name: Human-readable group name.
            item_ids: Up to 500 IDs.
            item_type: ``youtube#video``, ``youtube#channel``,
                ``youtube#playlist``, or ``youtubePartner#asset``. The short
                names ``video``, ``channel``, ``playlist``, ``asset`` are
                accepted and expanded.
        """
        kind_map = {
            "video": "youtube#video",
            "channel": "youtube#channel",
            "playlist": "youtube#playlist",
            "asset": "youtubePartner#asset",
        }
        kind = kind_map.get(item_type, item_type)
        ya = clients.youtube_analytics()
        group = clients.run(
            lambda a: a.groups().insert(body={
                "snippet": {"title": name},
                "contentDetails": {"itemType": kind},
            }),
            ya,
        )
        gid = group["id"]
        added: list[dict] = []
        for iid in item_ids[:500]:
            item = clients.run(
                lambda a, _gid=gid, _iid=iid: a.groupItems().insert(body={
                    "groupId": _gid,
                    "resource": {"kind": kind, "id": _iid},
                }),
                ya,
            )
            added.append(item)
        return {"group": group, "items_added": len(added)}

    @app.tool()
    def group_items(group_id: str) -> dict:
        """List items in an Analytics group."""
        resp = clients.run(
            lambda a: a.groupItems().list(groupId=group_id),
            clients.youtube_analytics(),
        )
        return {"items": resp.get("items") or []}

    @app.tool()
    def group_delete(group_id: str) -> dict:
        """Delete an Analytics group (does not affect the videos themselves)."""
        clients.run(
            lambda a: a.groups().delete(id=group_id),
            clients.youtube_analytics(),
        )
        return {"deleted": group_id}
