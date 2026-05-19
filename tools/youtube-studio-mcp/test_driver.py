"""Direct-invocation test driver for the youtube-studio MCP tools.

Bypasses the stdio JSON-RPC layer — imports the FastMCP app, looks up each
registered tool by name, and calls it with the supplied arguments. Used as
a verification harness after source edits when MCP server restart isn't
practical (e.g. autonomous fix loops while the user is asleep).

Run via `uv run python test_driver.py`.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from youtube_studio_mcp.server import app


def _summarise(result: Any) -> str:
    """Render a tool result as compact JSON, truncated for log readability."""
    try:
        if hasattr(result, "__iter__") and not isinstance(result, (str, bytes, dict)):
            # Sequence of ContentBlock — pull out text payloads.
            payloads: list[Any] = []
            for block in result:
                text = getattr(block, "text", None)
                if text is not None:
                    try:
                        payloads.append(json.loads(text))
                    except Exception:
                        payloads.append(text)
                else:
                    payloads.append(repr(block))
            blob = payloads if len(payloads) > 1 else (payloads[0] if payloads else result)
        else:
            blob = result
        s = json.dumps(blob, default=str, ensure_ascii=False)
    except Exception as e:
        s = f"<unrenderable: {e!r}>"
    return s if len(s) <= 1200 else s[:1200] + f"... [+{len(s) - 1200} chars]"


async def _call(name: str, args: dict[str, Any]) -> tuple[str, Any]:
    try:
        out = await app.call_tool(name, args)
        return ("OK", out)
    except Exception as e:
        return (f"RAISED {type(e).__name__}", e)


async def main() -> int:
    cases: list[tuple[str, str, dict[str, Any]]] = [
        # Bug 1 verification
        ("traffic_sources detail=True", "traffic_sources",
         {"days": 28, "detail": True}),
        # Bug 2 verification — single-ID call should succeed cleanly
        ("compare_videos single ID", "compare_videos",
         {"video_ids": ["0wimpfFJRvw"], "metrics": ["views"]}),
        # Bug 3 verification — structured error, not raise
        ("analytics_query bad metric", "analytics_query",
         {"metrics": "notARealMetric",
          "start_date": "2026-05-01", "end_date": "2026-05-18"}),
        ("group_items fake id", "group_items",
         {"group_id": "fake-group-id-for-error-test"}),
        # Bug 4 verification
        ("cost_preview unknown endpoint", "cost_preview",
         {"endpoint": "does.not.exist", "multiplier": 1}),
        ("cost_preview known endpoint", "cost_preview",
         {"endpoint": "comments.setModerationStatus", "multiplier": 10}),
        # Regression sanity reads
        ("quota_status", "quota_status", {}),
        ("auth_status", "auth_status", {}),
        ("my_channel", "my_channel", {}),
        ("top_videos", "top_videos",
         {"metric": "views", "days": 28, "n": 5}),
        ("comments_inbox all", "comments_inbox",
         {"filter": "all", "page_size": 5}),
        ("warehouse_query system tables", "warehouse_query",
         {"sql": "SELECT name FROM sqlite_master WHERE type='table'"}),
        # Extra: detail=false should still work
        ("traffic_sources detail=False", "traffic_sources",
         {"days": 28, "detail": False}),
    ]

    print(f"Running {len(cases)} test cases via direct FastMCP invocation...\n")
    failures: list[str] = []
    for label, name, args in cases:
        status, result = await _call(name, args)
        if status != "OK":
            failures.append(f"{label}: {status} — {result!r}")
            print(f"❌ {label}\n   {status}: {result!r}\n")
            continue
        # Even on OK, check the payload for structured errors.
        summary = _summarise(result)
        # `error` is allowed inside by_detail (per-source-type markers in
        # traffic_sources). Strip that nested map from the heuristic before
        # checking the top level.
        top_level_text = summary
        if '"by_detail":' in top_level_text:
            # Crude split — chops the by_detail object out for the
            # is_err scan. Good enough for test-driver heuristics.
            top_level_text = top_level_text.split('"by_detail":')[0]
        is_err = '"error"' in top_level_text
        marker = "⚠ " if is_err else "✓ "
        print(f"{marker}{label}\n   → {summary}\n")
        if is_err and label not in (
            "analytics_query bad metric",
            "group_items fake id",
        ):
            failures.append(f"{label}: unexpected error in payload — {summary}")
    print(f"\n{len(cases) - len(failures)}/{len(cases)} cases produced expected outcomes.")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
