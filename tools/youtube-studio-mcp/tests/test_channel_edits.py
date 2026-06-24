from unittest.mock import MagicMock

from youtube_studio_mcp.tools import channel_edits


def _svc():
    svc = MagicMock()
    svc.channels.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "UC1", "brandingSettings": {
            "channel": {"title": "Chan", "description": "old", "keywords": "a b"}}}]}
    svc.channels.return_value.update.return_value.execute.return_value = {"id": "UC1"}
    return svc


def test_branding_gated():
    svc = _svc()
    r = channel_edits._channel_update_branding(svc, channel_id="UC1",
        description="new", keywords=None, country=None, default_language=None,
        confirm=False)
    assert r["error"] == "confirm_required"
    svc.channels.return_value.update.assert_not_called()


def test_branding_merges_and_keeps_title(isolated_config):
    svc = _svc()
    r = channel_edits._channel_update_branding(svc, channel_id="UC1",
        description="new", keywords=None, country=None, default_language=None,
        confirm=True)
    body = svc.channels.return_value.update.call_args.kwargs["body"]
    assert body["brandingSettings"]["channel"]["description"] == "new"
    assert body["brandingSettings"]["channel"]["title"] == "Chan"  # preserved
    assert body["brandingSettings"]["channel"]["keywords"] == "a b"  # preserved
    assert r["branding_updated"] == "UC1"


def test_section_delete_gated():
    svc = MagicMock()
    assert channel_edits._channel_section_delete(svc, "S1", confirm=False)["error"] == "confirm_required"


def test_section_create(isolated_config):
    svc = MagicMock()
    svc.channelSections.return_value.insert.return_value.execute.return_value = {"id": "S1"}
    r = channel_edits._channel_section_create(svc, section_type="multiplePlaylists",
        title="Best", playlist_ids=["PL1"])
    assert r["section_created"] == "S1"
    body = svc.channelSections.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["type"] == "multiplePlaylists"
