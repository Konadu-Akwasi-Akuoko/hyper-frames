"""Pure argv contract tests — no ffmpeg, no filesystem."""

from __future__ import annotations

from derive_streams import argv as argvmod


def _pairs(a: list[str]) -> list[tuple[str, str]]:
    """Adjacent (flag, value) pairs, for asserting `-flag value` adjacency."""
    return list(zip(a, a[1:]))


def test_video_argv_pinned_flags():
    a = argvmod.video_argv("master.mov", "out.mp4")
    assert "-an" in a
    assert ("-c:v", "libx264") in _pairs(a)
    assert ("-crf", "18") in _pairs(a)
    assert ("-preset", "slow") in _pairs(a)
    assert ("-pix_fmt", "yuv420p") in _pairs(a)
    assert ("-movflags", "+faststart") in _pairs(a)
    assert a[0] == "ffmpeg"
    assert a[-1] == "out.mp4"


def test_video_argv_has_no_scale_filter():
    a = argvmod.video_argv("master.mov", "out.mp4")
    assert "-vf" not in a
    assert "-filter:v" not in a
    assert not any("scale" in tok for tok in a)


def test_video_argv_is_muted():
    a = argvmod.video_argv("master.mov", "out.mp4")
    assert "-an" in a
    assert "-c:a" not in a


def test_audio_argv_pinned_flags():
    a = argvmod.audio_argv("master.mov", "out.mp3")
    assert "-vn" in a
    assert ("-c:a", "libmp3lame") in _pairs(a)
    assert ("-q:a", "2") in _pairs(a)
    assert a[0] == "ffmpeg"
    assert a[-1] == "out.mp3"


def test_audio_argv_has_no_video():
    a = argvmod.audio_argv("master.mov", "out.mp3")
    assert "-vn" in a
    assert "-c:v" not in a


def test_argv_byte_identical_across_runs():
    v1 = argvmod.video_argv("m.mov", "v.mp4", 18, "slow")
    v2 = argvmod.video_argv("m.mov", "v.mp4", 18, "slow")
    assert v1 == v2
    a1 = argvmod.audio_argv("m.mov", "a.mp3", 2)
    a2 = argvmod.audio_argv("m.mov", "a.mp3", 2)
    assert a1 == a2


def test_float_knobs_round_to_int_string():
    # 18.0 (float) and 18 (int) must bake to the same "18" token.
    vi = argvmod.video_argv("m.mov", "v.mp4", 18, "slow")
    vf = argvmod.video_argv("m.mov", "v.mp4", 18.0, "slow")
    assert vi == vf
    assert ("-crf", "18") in _pairs(vf)
    af = argvmod.audio_argv("m.mov", "a.mp3", 2.0)
    assert ("-q:a", "2") in _pairs(af)


def test_float_knobs_round_to_six_decimals():
    a = argvmod.video_argv("m.mov", "v.mp4", 18.1234567, "slow")
    assert ("-crf", "18.123457") in _pairs(a)


def test_both_invocations_share_the_same_master():
    v = argvmod.video_argv("the-master.mov", "v.mp4")
    a = argvmod.audio_argv("the-master.mov", "a.mp3")
    assert v[v.index("-i") + 1] == "the-master.mov"
    assert a[a.index("-i") + 1] == "the-master.mov"
