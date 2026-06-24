from unittest.mock import MagicMock

from youtube_studio_mcp import uploadmedia


def test_validate_ok(tmp_path):
    f = tmp_path / "clip.mp4"; f.write_bytes(b"\x00" * 10)
    r = uploadmedia.validate(f, max_bytes=1000, allowed_mimes={"video/*"})
    assert r["ok"] and r["mime"] == "video/*" and r["size_bytes"] == 10


def test_validate_missing_file(tmp_path):
    r = uploadmedia.validate(tmp_path / "nope.mp4", max_bytes=1000, allowed_mimes={"video/*"})
    assert r["ok"] is False and r["error"] == "file_not_found"


def test_validate_too_large(tmp_path):
    f = tmp_path / "big.mp4"; f.write_bytes(b"\x00" * 100)
    r = uploadmedia.validate(f, max_bytes=10, allowed_mimes={"video/*"})
    assert r["error"] == "file_too_large"


def test_validate_unsupported(tmp_path):
    f = tmp_path / "doc.txt"; f.write_bytes(b"x")
    r = uploadmedia.validate(f, max_bytes=1000, allowed_mimes={"video/*"})
    assert r["error"] == "unsupported_format"


def test_execute_resumable_loops_until_done():
    request = MagicMock()
    request.next_chunk.side_effect = [
        (MagicMock(progress=lambda: 0.5), None), (None, {"id": "vid123"})]
    assert uploadmedia.execute_resumable(request) == {"id": "vid123"}
    assert request.next_chunk.call_count == 2
