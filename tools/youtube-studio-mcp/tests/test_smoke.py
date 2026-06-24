def test_quota_records(isolated_config):
    from youtube_studio_mcp import quota
    assert quota.record("videos.update") == 50
    assert quota.spent_today() == 50
