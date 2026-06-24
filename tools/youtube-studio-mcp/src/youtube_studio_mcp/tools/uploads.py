"""Upload tools (resumable): video_upload (videos.insert). Banner and watermark
uploads are added to this module in Part E.

videos.insert costs 1 unit from a separate 100/day Uploads bucket. A Short is
just a vertical video <=3 min uploaded through this same path.
Sources: https://developers.google.com/youtube/v3/docs/videos/insert
https://developers.google.com/youtube/v3/determine_quota_cost
"""

from __future__ import annotations

from typing import Any, Callable

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota, uploadmedia

MAX_VIDEO_BYTES = 256 * 1024 * 1024 * 1024  # 256 GB
VIDEO_MIMES = {"video/*"}
ALLOWED_PRIVACY = {"private", "unlisted", "public"}

MAX_BANNER_BYTES = 6 * 1024 * 1024  # 6 MB, 16:9, >=2048x1152
MAX_WATERMARK_BYTES = 10 * 1024 * 1024  # 10 MB
WATERMARK_TIMINGS = {"offsetFromStart", "offsetFromEnd"}


def _default_media_factory(path: str, mime: str) -> Any:
    return MediaFileUpload(path, mimetype=mime, resumable=True)


def _video_upload(svc: Any, *, path: str, title: str, description: str,
                  tags: list[str] | None, category_id: str, privacy: str,
                  publish_at: str | None, made_for_kids: bool,
                  contains_synthetic_media: bool | None, confirm: bool,
                  media_factory: Callable[[str, str], Any]) -> dict:
    """videos.insert via resumable upload. Gated only when public-facing."""
    if privacy not in ALLOWED_PRIVACY:
        return {"error": f"privacy must be one of {sorted(ALLOWED_PRIVACY)}"}
    pre = uploadmedia.validate(path, max_bytes=MAX_VIDEO_BYTES,
                               allowed_mimes=VIDEO_MIMES)
    if not pre["ok"]:
        return pre
    if privacy == "public" or publish_at is not None:
        effect = (f"This uploads and SCHEDULES the video to go public at "
                  f"{publish_at}." if publish_at
                  else "This uploads the video as PUBLIC immediately.")
        refusal = gate.require(confirm, effect=effect, title=title,
                               privacy=privacy, publish_at=publish_at)
        if refusal:
            return refusal
    status: dict[str, Any] = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": made_for_kids}
    if publish_at:
        status["publishAt"] = publish_at
    if contains_synthetic_media is not None:
        status["containsSyntheticMedia"] = contains_synthetic_media
    snippet: dict[str, Any] = {"title": title, "categoryId": category_id}
    if description:
        snippet["description"] = description
    if tags:
        snippet["tags"] = tags
    media = media_factory(pre["path"], pre["mime"])
    request = svc.videos().insert(part="snippet,status",
                                  body={"snippet": snippet, "status": status},
                                  media_body=media)
    resp = uploadmedia.execute_resumable(request)
    quota.record("videos.insert")
    return {"uploaded": resp.get("id"), "privacy": status["privacyStatus"],
            "publish_at": publish_at, "response": resp}


def _channel_set_banner(svc: Any, *, image_path: str, confirm: bool,
                        media_factory: Callable[[str, str], Any]) -> dict:
    """Two-step: channelBanners.insert (upload) -> channels.update
    brandingSettings.image.bannerExternalUrl."""
    refusal = gate.require(
        confirm, effect="This replaces your channel banner (visible channel-wide).")
    if refusal:
        return refusal
    pre = uploadmedia.validate(image_path, max_bytes=MAX_BANNER_BYTES,
                               allowed_mimes={"image/jpeg", "image/png"})
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    request = svc.channelBanners().insert(media_body=media)
    banner = uploadmedia.execute_resumable(request)
    quota.record("channelBanners.insert")
    url = banner.get("url")
    if not url:
        return {"error": "banner_upload_failed", "response": banner}
    current = clients.run(lambda y: y.channels().list(part="id", mine=True), svc)
    quota.record("channels.list")
    channel_id = (current.get("items") or [{}])[0].get("id")
    body = {"id": channel_id,
            "brandingSettings": {"image": {"bannerExternalUrl": url}}}
    resp = clients.run(
        lambda y: y.channels().update(part="brandingSettings", body=body), svc)
    quota.record("channels.update")
    return {"banner_set": True, "channel_id": channel_id, "banner_url": url,
            "response": resp}


def _channel_set_watermark(svc: Any, *, image_path: str, timing_type: str,
                           offset_ms: int, duration_ms: int, confirm: bool,
                           media_factory: Callable[[str, str], Any]) -> dict:
    """watermarks.set — branding watermark overlay (topRight). Gated."""
    if timing_type not in WATERMARK_TIMINGS:
        return {"error": f"timing_type must be one of {sorted(WATERMARK_TIMINGS)}"}
    refusal = gate.require(
        confirm, effect="This sets a channel watermark on all your videos.")
    if refusal:
        return refusal
    pre = uploadmedia.validate(image_path, max_bytes=MAX_WATERMARK_BYTES,
                               allowed_mimes={"image/jpeg", "image/png"})
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    current = clients.run(lambda y: y.channels().list(part="id", mine=True), svc)
    quota.record("channels.list")
    channel_id = (current.get("items") or [{}])[0].get("id")
    body = {"timing": {"type": timing_type, "offsetMs": offset_ms,
                       "durationMs": duration_ms},
            "position": {"type": "corner", "cornerPosition": "topRight"}}
    request = svc.watermarks().set(channelId=channel_id, body=body,
                                   media_body=media)
    uploadmedia.execute_resumable(request)
    quota.record("watermarks.set")
    return {"watermark_set": channel_id}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def video_upload(path: str, title: str, description: str = "",
                     tags: list[str] | None = None, category_id: str = "22",
                     privacy: str = "private", publish_at: str | None = None,
                     made_for_kids: bool = False,
                     contains_synthetic_media: bool | None = None,
                     confirm: bool = False) -> dict:
        """Upload a video or Short (resumable). Quota: 1 unit (100/day Uploads
        bucket). A Short is just a vertical video <=3 min — same call.

        Gated ONLY when public-facing: privacy="public" or a publish_at is set.
        Private uploads run ungated. When publish_at is set, privacy is forced to
        private (API requirement) and the video auto-publishes at that time.

        Args: path (mp4/mov/m4v/webm, <=256GB), title (<=100), description
        (<=5000 bytes), tags (<=500 chars total), category_id (e.g. "22"/"28"),
        privacy (private|unlisted|public), publish_at (ISO-8601 to schedule),
        made_for_kids (COPPA flag), contains_synthetic_media (AI disclosure),
        confirm (required for public/scheduled)."""
        return _video_upload(
            clients.youtube_data(), path=path, title=title,
            description=description, tags=tags, category_id=category_id,
            privacy=privacy, publish_at=publish_at, made_for_kids=made_for_kids,
            contains_synthetic_media=contains_synthetic_media, confirm=confirm,
            media_factory=_default_media_factory)

    @app.tool()
    @clients.http_safe
    def channel_set_banner(image_path: str, confirm: bool = False) -> dict:
        """Set the channel banner (JPEG/PNG, 16:9, >=2048x1152, <=6 MB). Quota:
        ~101 units (upload + channels.update). Gated (channel-wide)."""
        return _channel_set_banner(
            clients.youtube_data(), image_path=image_path, confirm=confirm,
            media_factory=_default_media_factory)

    @app.tool()
    @clients.http_safe
    def channel_set_watermark(image_path: str, timing_type: str = "offsetFromEnd",
                              offset_ms: int = 0, duration_ms: int = 15000,
                              confirm: bool = False) -> dict:
        """Set the channel branding watermark (JPEG/PNG <=10 MB, shown topRight).
        Quota: ~51 units. Gated. timing_type is offsetFromStart or offsetFromEnd."""
        return _channel_set_watermark(
            clients.youtube_data(), image_path=image_path, timing_type=timing_type,
            offset_ms=offset_ms, duration_ms=duration_ms, confirm=confirm,
            media_factory=_default_media_factory)
