from studio_discovery.youtube import (
    channel_videos_argv,
    comments_argv,
    parse_channel_videos,
    parse_comments,
)


def test_channel_videos_argv_exact():
    assert channel_videos_argv("https://www.youtube.com/@Fireship/videos", 15) == [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        "--playlist-end",
        "15",
        "--ignore-errors",
        "--no-warnings",
        "https://www.youtube.com/@Fireship/videos",
    ]


def test_comments_argv_validated_shape():
    a = comments_argv("https://www.youtube.com/watch?v=z_NbVtbgBJw", 30)
    assert a[0] == "yt-dlp"
    assert "--write-comments" in a
    assert "--dump-single-json" in a
    extractor = a[a.index("--extractor-args") + 1]
    assert "comment_sort=top" in extractor
    assert "max_comments=30,all,30,0" in extractor
    assert a[-1].endswith("z_NbVtbgBJw")


def test_parse_channel_videos_normalizes():
    stdout = "\n".join(
        [
            '{"id":"vid1","title":"A","view_count":1000,"duration":60,"upload_date":"20260101","channel":"Fireship"}',
            "",  # blank line tolerated
            "not json",  # garbage tolerated
            '{"title":"no id, skipped"}',
        ]
    )
    rows = parse_channel_videos(stdout, "@Fireship")
    assert len(rows) == 1
    r = rows[0]
    assert r["source"] == "youtube:@Fireship"
    assert r["external_id"] == "vid1"
    assert r["url"] == "https://www.youtube.com/watch?v=vid1"
    assert r["payload"]["views"] == 1000
    assert r["payload"]["duration_s"] == 60


def test_parse_comments_aggregates_into_one_row():
    data = {
        "id": "vid1",
        "title": "Redis",
        "view_count": 104802,
        "comment_count": 24,
        "comments": [
            {"text": "What tool do you use for diagramming?", "like_count": 2, "author": "x"},
            {"text": "Redis-as-primary gang", "like_count": 8, "author": "y"},
        ],
    }
    row = parse_comments(data, "@ByteByteGo")
    assert row is not None
    assert row["source"] == "youtube-comments:@ByteByteGo"
    assert row["external_id"] == "vid1"
    assert row["payload"]["comment_count"] == 24
    assert len(row["payload"]["comments"]) == 2
    assert row["payload"]["comments"][0]["likes"] == 2
