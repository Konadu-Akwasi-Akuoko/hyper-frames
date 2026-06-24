"""Plain-assert tests for the renderer. Run: python3 tools/thumbnail-inspo/test_build_readme.py"""
import build_readme as br

ENTRY = {
    "slug": "fireship-c", "channel": "fireship", "file": "06-x.jpg",
    "archetype": "big-text", "layout": "centered-stack", "device": ["big-text"],
    "face": False, "accent": "blue", "text": "low",
    "reads_as": "one giant C", "layout_map": "C centered", "why_it_works": "minimal",
    "mimic_for": "a quick primer", "watch_url": "https://yt/x",
    "title": "C in 100 Seconds", "title_shape": "speed-primer",
    "title_pattern": "concrete-noun-verb",
}


def test_quick_index_has_title_shape_column():
    out = br.render([ENTRY])
    header = [l for l in out.splitlines() if l.startswith("| slug |")][0]
    assert "title_shape" in header, header
    row = [l for l in out.splitlines() if l.startswith("| [fireship-c]")][0]
    assert "speed-primer" in row, row


def test_entry_block_has_original_title_labeled_not_copy():
    out = br.render([ENTRY])
    assert "C in 100 Seconds" in out
    assert "shape to mimic, not copy" in out
    assert "title_shape=speed-primer" in out


if __name__ == "__main__":
    test_quick_index_has_title_shape_column()
    test_entry_block_has_original_title_labeled_not_copy()
    print("ok")
