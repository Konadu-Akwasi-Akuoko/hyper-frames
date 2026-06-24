from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc(privacy="private", publish_at=None):
    svc = MagicMock()
    status = {"privacyStatus": privacy}
    if publish_at:
        status["publishAt"] = publish_at
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidS", "snippet": {"title": "T", "categoryId": "22"},
                   "status": status}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidS"}
    return svc


def test_schedule_gated():
    svc = _svc()
    assert edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", False)["error"] == "confirm_required"
    svc.videos.return_value.update.assert_not_called()


def test_schedule_sets_publishat_and_forces_private(isolated_config):
    svc = _svc()
    r = edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", True)
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r["scheduled"] == "vidS"


def test_cancel_is_ungated_and_clears(isolated_config):
    svc = _svc(publish_at="2026-07-01T12:00:00Z")
    r = edits._video_cancel_schedule(svc, "vidS")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"].get("publishAt") is None
    assert r["schedule_cancelled"] == "vidS"
