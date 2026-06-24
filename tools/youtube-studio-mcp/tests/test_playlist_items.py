from unittest.mock import MagicMock

from youtube_studio_mcp.tools import playlists


def _mf(path, mime):
    return MagicMock(name="media")


def test_add_video(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.insert.return_value.execute.return_value = {"id": "PLI1"}
    r = playlists._playlist_add_video(svc, playlist_id="PL1", video_id="vidA", position=None)
    body = svc.playlistItems.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["playlistId"] == "PL1"
    assert body["snippet"]["resourceId"] == {"kind": "youtube#video", "videoId": "vidA"}
    assert r["item_added"] == "PLI1"


def test_add_video_with_position(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.insert.return_value.execute.return_value = {"id": "PLI1"}
    playlists._playlist_add_video(svc, playlist_id="PL1", video_id="vidA", position=0)
    body = svc.playlistItems.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["position"] == 0


def test_item_remove_gated():
    svc = MagicMock()
    assert playlists._playlist_item_remove(svc, "PLI1", confirm=False)["error"] == "confirm_required"


def test_item_remove_runs(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.delete.return_value.execute.return_value = ""
    assert playlists._playlist_item_remove(svc, "PLI1", confirm=True)["item_removed"] == "PLI1"


def test_set_image_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "cover.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(playlists.uploadmedia, "execute_resumable",
                        lambda req: {"id": "IMG1"})
    r = playlists._playlist_set_image(svc, playlist_id="PL1", file_path=str(f),
                                      confirm=True, media_factory=_mf)
    assert r["image_set"] == "IMG1"


def test_set_image_gated(tmp_path):
    f = tmp_path / "cover.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = playlists._playlist_set_image(svc, playlist_id="PL1",
                                      file_path=str(f), confirm=False,
                                      media_factory=_mf)
    assert r["error"] == "confirm_required"
    svc.playlistImages.return_value.insert.assert_not_called()


def test_delete_image_gated():
    svc = MagicMock()
    assert playlists._playlist_delete_image(svc, "IMG1", confirm=False)["error"] == "confirm_required"
