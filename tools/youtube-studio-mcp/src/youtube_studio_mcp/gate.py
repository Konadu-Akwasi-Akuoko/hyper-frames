"""Confirmation interlocks for irreversible / public-facing / social writes.

A gated tool calls gate.require(...) (or gate.quota_guard(...)) first; if it
returns a dict, the tool returns it unchanged and performs no API call. Mirrors
the existing confirm_publish pattern and the bulk-comment guard.
"""

from __future__ import annotations

from typing import Any

from . import quota

DEFAULT_FRACTION_LIMIT = 0.25


def require(confirm: bool, *, effect: str, **extra: Any) -> dict | None:
    """Refusal dict when confirm is False, else None. `effect` is one sentence
    describing the action, e.g. 'This permanently deletes video abc123.'"""
    if confirm:
        return None
    out: dict[str, Any] = {
        "error": "confirm_required",
        "reason": f"{effect} Re-call with confirm=True after user approval.",
    }
    out.update(extra)
    return out


def quota_guard(endpoint: str, multiplier: int, confirm: bool, *,
                fraction_limit: float = DEFAULT_FRACTION_LIMIT) -> dict | None:
    """Gate an expensive write on confirmation AND remaining quota."""
    cost = quota.cost_of(endpoint) * multiplier
    if not confirm:
        return {"error": "confirm_required",
                "reason": (f"This costs {cost} quota units. Re-call with "
                           "confirm=True after user approval."),
                "estimated_cost_units": cost}
    rem = quota.remaining()
    if cost > rem * fraction_limit:
        return {"error": "quota_safety_refused",
                "reason": (f"This would cost {cost} units, more than "
                           f"{int(fraction_limit * 100)}% of the {rem} units "
                           "remaining today. Wait for reset or split the work."),
                "estimated_cost_units": cost, "remaining_quota_units": rem}
    return None
