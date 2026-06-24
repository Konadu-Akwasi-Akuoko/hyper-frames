from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def test_video_delete_gated():
    svc = MagicMock()
    assert edits._video_delete(svc, "vidX", confirm=False)["error"] == "confirm_required"
    svc.videos.return_value.delete.assert_not_called()


def test_video_delete_runs(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.delete.return_value.execute.return_value = ""
    assert edits._video_delete(svc, "vidX", confirm=True)["deleted"] == "vidX"
    svc.videos.return_value.delete.assert_called_once_with(id="vidX")


def test_video_rate_rejects_bad_rating():
    svc = MagicMock()
    assert edits._video_rate(svc, "vidX", "love", confirm=True)["error"].startswith("rating must be")


def test_video_rate_gated():
    svc = MagicMock()
    assert edits._video_rate(svc, "vidX", "like", confirm=False)["error"] == "confirm_required"


def test_video_rate_runs(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.rate.return_value.execute.return_value = ""
    r = edits._video_rate(svc, "vidX", "like", confirm=True)
    assert r["rated"] == "vidX" and r["rating"] == "like"
    svc.videos.return_value.rate.assert_called_once_with(id="vidX", rating="like")
