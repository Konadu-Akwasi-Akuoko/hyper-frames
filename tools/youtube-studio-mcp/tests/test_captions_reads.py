from unittest.mock import MagicMock

from youtube_studio_mcp.tools import captions


def test_caption_list(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "capA", "snippet": {"language": "en", "name": "English"}}]}
    r = captions._caption_list(svc, "vid1")
    assert r["items"][0]["id"] == "capA"
    svc.captions.return_value.list.assert_called_once()


def test_caption_download_rejects_bad_tfmt():
    svc = MagicMock()
    r = captions._caption_download(svc, "capA", tfmt="docx", tlang=None)
    assert r["error"].startswith("tfmt must be")


def test_caption_download_runs(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.download.return_value.execute.return_value = b"1\n00:00\nhi"
    r = captions._caption_download(svc, "capA", tfmt="srt", tlang=None)
    assert r["caption_id"] == "capA" and r["tfmt"] == "srt"
    assert "content" in r
