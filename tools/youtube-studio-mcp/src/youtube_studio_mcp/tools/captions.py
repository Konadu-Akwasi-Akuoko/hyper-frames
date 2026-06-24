"""Caption tracks: list/download (reads) + insert/update/delete (writes, Part C).

insert=400, update=450 units — quota-guarded. update/delete/download need the
caption id from caption_list. SRT uploads as application/octet-stream.
Sources: https://developers.google.com/youtube/v3/docs/captions
https://developers.google.com/youtube/v3/determine_quota_cost
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota, uploadmedia

CAPTION_TFMTS = {"sbv", "scc", "srt", "ttml", "vtt"}
CAPTION_MIMES = {"application/octet-stream", "text/vtt", "text/xml"}
MAX_CAPTION_BYTES = 100 * 1024 * 1024  # 100 MB


def _caption_list(svc: Any, video_id: str) -> dict:
    resp = clients.run(
        lambda y: y.captions().list(part="snippet", videoId=video_id), svc)
    quota.record("captions.list")
    return {"video_id": video_id, "items": resp.get("items") or []}


def _caption_download(svc: Any, caption_id: str, tfmt: str,
                      tlang: str | None) -> dict:
    if tfmt not in CAPTION_TFMTS:
        return {"error": f"tfmt must be one of {sorted(CAPTION_TFMTS)}"}
    kwargs: dict[str, Any] = {"id": caption_id, "tfmt": tfmt}
    if tlang:
        kwargs["tlang"] = tlang
    raw = clients.run(lambda y: y.captions().download(**kwargs), svc)
    quota.record("captions.download")
    content = raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    return {"caption_id": caption_id, "tfmt": tfmt, "tlang": tlang,
            "content": content}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def caption_list(video_id: str) -> dict:
        """List caption tracks for a video (ids needed by update/delete/download).
        Quota: 50 units. Ungated."""
        return _caption_list(clients.youtube_data(), video_id)

    @app.tool()
    @clients.http_safe
    def caption_download(caption_id: str, tfmt: str = "srt",
                         tlang: str | None = None) -> dict:
        """Download a caption track. Quota: 200 units. Ungated. tfmt is one of
        sbv/scc/srt/ttml/vtt; tlang requests a machine translation (ISO 639-1)."""
        return _caption_download(clients.youtube_data(), caption_id, tfmt, tlang)
