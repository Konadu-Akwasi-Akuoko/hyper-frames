from unittest.mock import MagicMock

from youtube_studio_mcp.tools import uploads


def _mf(path, mime):
    return MagicMock(name="media")


def test_missing_file(tmp_path):
    r = uploads._video_upload(MagicMock(), path=str(tmp_path / "nope.mp4"),
        title="T", description="", tags=None, category_id="22",
        privacy="private", publish_at=None, made_for_kids=False,
        contains_synthetic_media=None, confirm=False, media_factory=_mf)
    assert r["error"] == "file_not_found"


def test_public_upload_gated(tmp_path):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._video_upload(svc, path=str(f), title="T", description="",
        tags=None, category_id="22", privacy="public", publish_at=None,
        made_for_kids=False, contains_synthetic_media=None, confirm=False,
        media_factory=_mf)
    assert r["error"] == "confirm_required"
    svc.videos.return_value.insert.assert_not_called()


def test_private_upload_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "newVid"})
    r = uploads._video_upload(svc, path=str(f), title="My Title",
        description="desc", tags=["a", "b"], category_id="28", privacy="private",
        publish_at=None, made_for_kids=False, contains_synthetic_media=True,
        confirm=False, media_factory=_mf)
    assert r["uploaded"] == "newVid"
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "My Title"
    assert body["snippet"]["tags"] == ["a", "b"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["containsSyntheticMedia"] is True


def test_scheduled_upload_gated_then_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "schVid"})
    base = dict(path=str(f), title="T", description="", tags=None,
        category_id="22", privacy="private", publish_at="2026-07-01T12:00:00Z",
        made_for_kids=False, contains_synthetic_media=None, media_factory=_mf)
    assert uploads._video_upload(svc, confirm=False, **base)["error"] == "confirm_required"
    r = uploads._video_upload(svc, confirm=True, **base)
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r["uploaded"] == "schVid"
