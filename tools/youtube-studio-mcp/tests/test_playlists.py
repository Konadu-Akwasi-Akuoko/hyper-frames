from unittest.mock import MagicMock

from youtube_studio_mcp.tools import playlists


def test_create(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.insert.return_value.execute.return_value = {"id": "PL1"}
    r = playlists._playlist_create(svc, title="Series", description="d", privacy="public")
    assert r["playlist_created"] == "PL1"
    body = svc.playlists.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "Series"
    assert body["status"]["privacyStatus"] == "public"


def test_update_merges(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "PL1", "snippet": {"title": "Old", "description": "keep"},
                   "status": {"privacyStatus": "private"}}]}
    svc.playlists.return_value.update.return_value.execute.return_value = {"id": "PL1"}
    r = playlists._playlist_update(svc, playlist_id="PL1", title="New",
                                   description=None, privacy=None)
    body = svc.playlists.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "New"
    assert body["snippet"]["description"] == "keep"
    assert r["playlist_updated"] == "PL1"


def test_delete_gated():
    svc = MagicMock()
    assert playlists._playlist_delete(svc, "PL1", confirm=False)["error"] == "confirm_required"


def test_delete_runs(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.delete.return_value.execute.return_value = ""
    assert playlists._playlist_delete(svc, "PL1", confirm=True)["playlist_deleted"] == "PL1"
