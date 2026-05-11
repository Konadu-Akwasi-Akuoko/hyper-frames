"""Exception hierarchy. One class per spec failure mode."""
from __future__ import annotations


class SfxPlanError(Exception):
    """Base for all sfx-plan failures."""


class UnresolvedAnchorError(SfxPlanError):
    def __init__(self, *, anchor: str, source: str) -> None:
        super().__init__(
            f'unresolved anchor "{anchor}" at {source} — not present in narration-map. '
            f"Did the script change? Re-run tools/narration-map or fix the data-sfx-anchor attribute."
        )
        self.anchor = anchor
        self.source = source


class AnchorIndexOutOfRangeError(SfxPlanError):
    def __init__(self, *, anchor: str, requested: int, available: int, source: str) -> None:
        super().__init__(
            f'anchor "{anchor}" requested index {requested} at {source}, '
            f"only {available} occurrence(s) in narration-map. "
            f"Drop the data-sfx-anchor-index attribute or fix the value."
        )
        self.anchor = anchor
        self.requested = requested
        self.available = available
        self.source = source


class UnknownCueError(SfxPlanError):
    def __init__(self, *, cue: str, known: list[str], source: str) -> None:
        known_str = ", ".join(sorted(known))
        super().__init__(
            f'unknown cue "{cue}" at {source}. Known cues: {known_str}. '
            f"Add the cue to sfx-catalog.yml or fix the data-sfx-on-anchor attribute."
        )
        self.cue = cue
        self.known = known
        self.source = source


class EmptyCueFilterError(SfxPlanError):
    def __init__(self, *, cue: str) -> None:
        super().__init__(
            f'cue "{cue}" filter matched 0 assets. '
            f"Relax the recipe in sfx-catalog.yml or add files to sound-effects/."
        )
        self.cue = cue


class CatalogMissingError(SfxPlanError):
    def __init__(self, *, path: str) -> None:
        super().__init__(
            f"sfx-catalog.yml not found at {path}. "
            f"Build it first: uv run --project tools/sfx-catalog sfx-catalog"
        )
        self.path = path


class CatalogVersionMismatchError(SfxPlanError):
    def __init__(self, *, found: int, expected: int) -> None:
        super().__init__(
            f"sfx-catalog.yml version {found} does not match sfx-plan's expected version {expected}. "
            f"Upgrade tools/sfx-plan or rebuild the catalog."
        )
        self.found = found
        self.expected = expected
