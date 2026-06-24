from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidU",
                   "snippet": {"title": "Old", "categoryId": "22",
                               "description": "keep", "tags": ["t1"]},
                   "status": {"privacyStatus": "private"}}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidU"}
    return svc


def test_update_title_preserves_other_fields(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU", title="New")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "New"
    assert body["snippet"]["description"] == "keep"
    assert body["snippet"]["tags"] == ["t1"]
    assert out["updated"] == "vidU"


def test_private_to_public_still_gated(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU",
        privacy_status="public", confirm_publish=False)
    assert out["error"] == "confirm_publish_required"
    svc.videos.return_value.update.assert_not_called()
