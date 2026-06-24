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


def _caption_insert(svc: Any, *, video_id: str, file_path: str, language: str,
                    name: str, is_draft: bool, confirm: bool,
                    media_factory) -> dict:
    """captions.insert — 400 units, quota-guarded. Media body = caption file."""
    refusal = gate.quota_guard("captions.insert", 1, confirm)
    if refusal:
        return refusal
    pre = uploadmedia.validate(file_path, max_bytes=MAX_CAPTION_BYTES,
                               allowed_mimes=CAPTION_MIMES)
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    body = {"snippet": {"videoId": video_id, "language": language,
                        "name": name, "isDraft": is_draft}}
    resp = clients.run(
        lambda y: y.captions().insert(part="snippet", body=body, media_body=media),
        svc)
    quota.record("captions.insert")
    return {"caption_inserted": resp.get("id"), "response": resp}


def _caption_update(svc: Any, *, caption_id: str, file_path: str | None,
                    is_draft: bool | None, confirm: bool, media_factory) -> dict:
    """captions.update — 450 units, quota-guarded. Replace file and/or draft."""
    if file_path is None and is_draft is None:
        return {"error": "no_changes_provided",
                "reason": "Pass file_path and/or is_draft to update a caption."}
    refusal = gate.quota_guard("captions.update", 1, confirm)
    if refusal:
        return refusal
    body: dict[str, Any] = {"id": caption_id}
    if is_draft is not None:
        body["snippet"] = {"isDraft": is_draft}
    media = None
    if file_path is not None:
        pre = uploadmedia.validate(file_path, max_bytes=MAX_CAPTION_BYTES,
                                   allowed_mimes=CAPTION_MIMES)
        if not pre["ok"]:
            return pre
        media = media_factory(pre["path"], pre["mime"])
    part = "snippet" if "snippet" in body else "id"
    resp = clients.run(
        lambda y: y.captions().update(part=part, body=body, media_body=media),
        svc)
    quota.record("captions.update")
    return {"caption_updated": caption_id, "response": resp}


def _caption_delete(svc: Any, caption_id: str, confirm: bool) -> dict:
    """captions.delete — gated, irreversible."""
    refusal = gate.require(
        confirm, effect=f"This permanently deletes caption track {caption_id}.",
        caption_id=caption_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.captions().delete(id=caption_id), svc)
    quota.record("captions.delete")
    return {"caption_deleted": caption_id, "quota_units_spent": 50}


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

    @app.tool()
    @clients.http_safe
    def caption_insert(video_id: str, file_path: str, language: str,
                       name: str = "", is_draft: bool = False,
                       confirm: bool = False) -> dict:
        """Upload a caption track (e.g. your SRT) for a video. Quota: 400 units —
        gated on cost. language is BCP-47 (e.g. "en"); name is the viewer-facing
        label. Accepts .srt/.sbv/.vtt/.xml."""
        from googleapiclient.http import MediaFileUpload
        return _caption_insert(
            clients.youtube_data(), video_id=video_id, file_path=file_path,
            language=language, name=name or language, is_draft=is_draft,
            confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def caption_update(caption_id: str, file_path: str | None = None,
                       is_draft: bool | None = None, confirm: bool = False) -> dict:
        """Replace a caption track's file and/or draft status. Quota: 450 units —
        gated on cost. Get caption_id from caption_list."""
        from googleapiclient.http import MediaFileUpload
        return _caption_update(
            clients.youtube_data(), caption_id=caption_id, file_path=file_path,
            is_draft=is_draft, confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def caption_delete(caption_id: str, confirm: bool = False) -> dict:
        """Delete a caption track. Quota: 50 units. Gated: irreversible."""
        return _caption_delete(clients.youtube_data(), caption_id, confirm)
