from youtube_studio_mcp import gate, quota


def test_require_blocks_without_confirm():
    r = gate.require(False, effect="This deletes video abc.", video_id="abc")
    assert r["error"] == "confirm_required"
    assert "deletes video abc" in r["reason"]
    assert r["video_id"] == "abc"


def test_require_passes_with_confirm():
    assert gate.require(True, effect="x") is None


def test_quota_guard_blocks_without_confirm():
    r = gate.quota_guard("captions.insert", 1, confirm=False)
    assert r["error"] == "confirm_required"
    assert r["estimated_cost_units"] == 400


def test_quota_guard_refuses_when_over_fraction(isolated_config):
    quota.record("search.list", multiplier=99)  # 9900 spent, 100 remaining
    r = gate.quota_guard("captions.insert", 1, confirm=True)
    assert r["error"] == "quota_safety_refused"


def test_quota_guard_allows_when_affordable(isolated_config):
    assert gate.quota_guard("videos.update", 1, confirm=True) is None


def test_quota_guard_refuses_when_quota_exhausted(isolated_config):
    quota.record("search.list", multiplier=100)  # 100 * 100 = 10000 spent, 0 remaining
    r = gate.quota_guard("videos.update", 1, confirm=True)
    assert r["error"] == "quota_safety_refused"
    assert r["remaining_quota_units"] == 0
