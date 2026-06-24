import pytest

from youtube_studio_mcp import quota
from youtube_studio_mcp.quota import _cost_of

EXPECTED = {
    "videos.insert": 1, "videos.delete": 50,
    "playlists.insert": 50, "playlists.update": 50, "playlists.delete": 50,
    "playlistItems.insert": 50, "playlistItems.update": 50, "playlistItems.delete": 50,
    "playlistImages.insert": 50, "playlistImages.update": 50, "playlistImages.delete": 50,
    "channels.update": 50,
    "channelSections.insert": 50, "channelSections.update": 50, "channelSections.delete": 50,
    "channelBanners.insert": 50, "watermarks.set": 50, "watermarks.unset": 50,
}


@pytest.mark.parametrize("endpoint,units", EXPECTED.items())
def test_cost_known(endpoint, units):
    assert quota.cost_of(endpoint) == units
    assert _cost_of(endpoint)[1] is False
