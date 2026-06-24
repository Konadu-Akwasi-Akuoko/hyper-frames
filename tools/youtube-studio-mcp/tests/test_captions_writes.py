from unittest.mock import MagicMock

from youtube_studio_mcp.tools import captions


def _mf(path, mime):
    return MagicMock(name="media")


def test_insert_quota_gated(tmp_path):
    f = tmp_path / "en.srt"; f.write_text("1\n00:00,000 --> 00:01,000\nhi\n")
    svc = MagicMock()
    r = captions._caption_insert(svc, video_id="v1", file_path=str(f),
        language="en", name="English", is_draft=False, confirm=False,
        media_factory=_mf)
    assert r["error"] == "confirm_required"
    assert r["estimated_cost_units"] == 400
    svc.captions.return_value.insert.assert_not_called()


def test_insert_runs(tmp_path, isolated_config):
    f = tmp_path / "en.srt"; f.write_text("1\n00:00,000 --> 00:01,000\nhi\n")
    svc = MagicMock()
    svc.captions.return_value.insert.return_value.execute.return_value = {"id": "capN"}
    r = captions._caption_insert(svc, video_id="v1", file_path=str(f),
        language="en", name="English", is_draft=False, confirm=True,
        media_factory=_mf)
    assert r["caption_inserted"] == "capN"
    body = svc.captions.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["videoId"] == "v1"
    assert body["snippet"]["language"] == "en"


def test_insert_missing_file(tmp_path):
    svc = MagicMock()
    r = captions._caption_insert(svc, video_id="v1",
        file_path=str(tmp_path / "no.srt"), language="en", name="E",
        is_draft=False, confirm=True, media_factory=_mf)
    assert r["error"] == "file_not_found"


def test_delete_gated():
    svc = MagicMock()
    assert captions._caption_delete(svc, "capA", confirm=False)["error"] == "confirm_required"
    svc.captions.return_value.delete.assert_not_called()


def test_delete_runs(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.delete.return_value.execute.return_value = ""
    assert captions._caption_delete(svc, "capA", confirm=True)["caption_deleted"] == "capA"


def test_update_noop_returns_error():
    svc = MagicMock()
    r = captions._caption_update(svc, caption_id="capA", file_path=None,
                                 is_draft=None, confirm=True, media_factory=_mf)
    assert r["error"] == "no_changes_provided"
    svc.captions.return_value.update.assert_not_called()


def test_update_bad_file_returns_validate_error(tmp_path):
    svc = MagicMock()
    r = captions._caption_update(svc, caption_id="capA",
                                 file_path=str(tmp_path / "missing.srt"),
                                 is_draft=None, confirm=True, media_factory=_mf)
    assert r["error"] == "file_not_found"
    svc.captions.return_value.update.assert_not_called()
