from studio_discovery.ids import raw_signal_id


def test_known_vectors_match_the_typescript_writer():
    # These exact values are also asserted in server/lib/db.test.ts, guaranteeing
    # the Python and TS writers dedup against the same keyspace.
    assert raw_signal_id("hn", "abc123") == "2e7b7faaccf5c9f4"
    assert raw_signal_id("youtube:@Fireship", "Sntj4HmuykI") == "dd759ac2d09788e3"


def test_separator_disambiguates_boundaries():
    assert raw_signal_id("ab", "c") != raw_signal_id("a", "bc")
