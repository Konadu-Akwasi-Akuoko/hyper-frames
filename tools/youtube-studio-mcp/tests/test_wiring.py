import asyncio


def test_upload_scope_present():
    from youtube_studio_mcp import auth
    assert "https://www.googleapis.com/auth/youtube.upload" in auth.SCOPES


def test_all_new_tools_registered():
    from youtube_studio_mcp.server import app
    names = set(asyncio.run(_names(app)))
    for t in ("video_upload", "video_delete", "video_rate", "video_schedule",
              "video_cancel_schedule", "video_set_localizations",
              "caption_list", "caption_insert", "caption_update", "caption_delete",
              "caption_download", "playlist_create", "playlist_update",
              "playlist_delete", "playlist_add_video", "playlist_item_remove",
              "playlist_set_image", "playlist_delete_image",
              "channel_update_branding", "channel_section_create",
              "channel_section_update", "channel_section_delete",
              "channel_set_banner", "channel_set_watermark",
              "channel_unset_watermark", "subscription_add",
              "subscription_remove"):
        assert t in names, f"{t} not registered"


async def _names(app):
    return [t.name for t in await app.list_tools()]
