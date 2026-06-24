from unittest.mock import MagicMock

from youtube_studio_mcp.tools import uploads, channel_edits


def _mf(path, mime):
    return MagicMock(name="media")


def test_set_banner_gated(tmp_path):
    f = tmp_path / "banner.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._channel_set_banner(svc, image_path=str(f), confirm=False,
                                    media_factory=_mf)
    assert r["error"] == "confirm_required"


def test_set_banner_two_step(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "banner.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"url": "http://banner/url"})
    svc.channels.return_value.update.return_value.execute.return_value = {"id": "UC1"}
    r = uploads._channel_set_banner(svc, image_path=str(f), confirm=True,
                                    media_factory=_mf)
    body = svc.channels.return_value.update.call_args.kwargs["body"]
    assert body["brandingSettings"]["image"]["bannerExternalUrl"] == "http://banner/url"
    assert r["banner_set"] is True


def test_set_watermark_gated(tmp_path):
    f = tmp_path / "wm.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._channel_set_watermark(svc, image_path=str(f),
        timing_type="offsetFromEnd", offset_ms=0, duration_ms=15000,
        confirm=False, media_factory=_mf)
    assert r["error"] == "confirm_required"


def test_unset_watermark_gated():
    svc = MagicMock()
    assert channel_edits._channel_unset_watermark(svc, "UC1", confirm=False)["error"] == "confirm_required"


def test_unset_watermark_runs(isolated_config):
    svc = MagicMock()
    svc.watermarks.return_value.unset.return_value.execute.return_value = ""
    assert channel_edits._channel_unset_watermark(svc, "UC1", confirm=True)["watermark_unset"] == "UC1"
