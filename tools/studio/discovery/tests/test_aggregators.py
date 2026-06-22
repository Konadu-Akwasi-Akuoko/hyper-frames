from studio_discovery.aggregators import (
    parse_dailydev,
    parse_hn,
    parse_lobsters,
    parse_reddit,
)


def test_parse_hn_skips_linkless_stories():
    data = {
        "hits": [
            {
                "objectID": "1",
                "title": "Real",
                "url": "https://example.com/a",
                "points": 100,
                "num_comments": 5,
                "created_at": "2026-06-20T00:00:00Z",
            },
            {"objectID": "2", "title": "Ask HN, no url", "points": 50},
        ]
    }
    rows = parse_hn(data)
    assert len(rows) == 1
    assert rows[0]["source"] == "hn"
    assert rows[0]["external_id"] == "1"
    assert rows[0]["payload"]["points"] == 100
    assert rows[0]["payload"]["comments_url"].endswith("id=1")


def test_parse_reddit_filters_self_low_and_internal():
    data = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "a",
                        "title": "Keep",
                        "url_overridden_by_dest": "https://ex.com/a",
                        "score": 100,
                        "num_comments": 3,
                        "permalink": "/r/programming/a",
                    }
                },
                {"data": {"id": "b", "is_self": True, "url": "https://ex.com/b", "score": 99}},
                {"data": {"id": "c", "url": "https://ex.com/c", "score": 5}},
                {"data": {"id": "d", "url": "https://reddit.com/d", "score": 200}},
            ]
        }
    }
    rows = parse_reddit(data, "programming", min_score=40)
    assert [r["external_id"] for r in rows] == ["a"]
    assert rows[0]["source"] == "reddit:r/programming"
    assert rows[0]["payload"]["points"] == 100


def test_parse_lobsters_rss():
    xml = """
    <rss><channel>
      <item><title>One &amp; Two</title><link>https://ex.com/1</link>
        <guid>g1</guid><pubDate>Mon</pubDate><comments>https://lobste.rs/c/1</comments>
        <category>rust</category><category>perf</category></item>
      <item><title>Internal</title><link>https://lobste.rs/s/x</link><guid>g2</guid></item>
    </channel></rss>
    """
    rows = parse_lobsters(xml)
    assert len(rows) == 1
    assert rows[0]["title"] == "One & Two"
    assert rows[0]["external_id"] == "g1"
    assert rows[0]["payload"]["tags"] == ["rust", "perf"]


def test_parse_dailydev_min_upvotes():
    data = {
        "data": {
            "anonymousFeed": {
                "edges": [
                    {
                        "node": {
                            "id": "1",
                            "title": "Hot",
                            "permalink": "https://ex.com/p",
                            "numUpvotes": 50,
                            "numComments": 2,
                            "commentsPermalink": "https://daily.dev/p",
                        }
                    },
                    {"node": {"id": "2", "title": "Cold", "permalink": "https://ex.com/l", "numUpvotes": 3}},
                ]
            }
        }
    }
    rows = parse_dailydev(data, min_upvotes=10)
    assert [r["external_id"] for r in rows] == ["1"]
    assert rows[0]["payload"]["points"] == 50
