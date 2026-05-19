"""Cached helpers for repeatedly-needed channel facts.

``my_channel_id()`` and ``my_uploads_playlist_id()`` are called by many tools
(to scope queries, to compare against arbitrary channel IDs passed in, etc.).
They're cached for the process lifetime because they don't change.
"""

from __future__ import annotations

from . import cache, clients, quota

_PROCESS_CACHE: dict[str, str] = {}


def _fetch_mine_channel() -> dict:
    cached = cache.get("channels.list:mine", {"part": "id,contentDetails"})
    if cached is not None:
        return cached
    resp = clients.run(
        lambda y: y.channels().list(part="id,contentDetails", mine=True),
        clients.youtube_data(),
    )
    quota.record("channels.list")
    cache.put("channels.list:mine", {"part": "id,contentDetails"}, resp)
    return resp


def my_channel_id() -> str:
    if "channel_id" in _PROCESS_CACHE:
        return _PROCESS_CACHE["channel_id"]
    resp = _fetch_mine_channel()
    items = resp.get("items") or []
    if not items:
        raise RuntimeError("channels.list?mine=true returned no items")
    cid = items[0]["id"]
    _PROCESS_CACHE["channel_id"] = cid
    return cid


def my_uploads_playlist_id() -> str:
    if "uploads" in _PROCESS_CACHE:
        return _PROCESS_CACHE["uploads"]
    resp = _fetch_mine_channel()
    items = resp.get("items") or []
    if not items:
        raise RuntimeError("channels.list?mine=true returned no items")
    pid = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    _PROCESS_CACHE["uploads"] = pid
    return pid
