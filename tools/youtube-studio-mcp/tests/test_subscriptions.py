from unittest.mock import MagicMock

from youtube_studio_mcp.tools import subscriptions


def test_add_gated():
    svc = MagicMock()
    assert subscriptions._subscription_add(svc, "UCabc", confirm=False)["error"] == "confirm_required"
    svc.subscriptions.return_value.insert.assert_not_called()


def test_add_runs(isolated_config):
    svc = MagicMock()
    svc.subscriptions.return_value.insert.return_value.execute.return_value = {"id": "SUB1"}
    r = subscriptions._subscription_add(svc, "UCabc", confirm=True)
    body = svc.subscriptions.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["resourceId"] == {"kind": "youtube#channel", "channelId": "UCabc"}
    assert r["subscribed"] == "SUB1"


def test_remove_gated():
    svc = MagicMock()
    assert subscriptions._subscription_remove(svc, "SUB1", confirm=False)["error"] == "confirm_required"


def test_remove_runs(isolated_config):
    svc = MagicMock()
    svc.subscriptions.return_value.delete.return_value.execute.return_value = ""
    assert subscriptions._subscription_remove(svc, "SUB1", confirm=True)["unsubscribed"] == "SUB1"
