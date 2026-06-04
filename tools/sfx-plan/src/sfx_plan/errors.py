"""Exception hierarchy. One class per spec failure mode."""
from __future__ import annotations


class SfxPlanError(Exception):
    """Base for all sfx-plan failures."""


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


class UnknownAssetError(SfxPlanError):
    def __init__(self, *, asset: str, source: str, near: list[str] | None = None) -> None:
        hint = ""
        if near:
            hint = " Did you mean one of: " + ", ".join(f'"{p}"' for p in near) + "?"
        super().__init__(
            f'unknown asset "{asset}" pinned via data-sfx-asset at {source}.{hint} '
            f"The asset must be a path that exists in sfx-catalog.yml's assets section."
        )
        self.asset = asset
        self.source = source
        self.near = near or []


class MissingTimeReferenceError(SfxPlanError):
    def __init__(self, *, source: str) -> None:
        super().__init__(
            f"element at {source} has data-sfx-on-anchor but no data-sfx-at-scene-ms. "
            f"Set data-sfx-at-scene-ms to the scene-local ms of the element's visual impact frame."
        )
        self.source = source


class UnknownMountError(SfxPlanError):
    def __init__(self, *, comp_path: str, source: str, known_mounts: list[str]) -> None:
        known_str = ", ".join(sorted(known_mounts)) if known_mounts else "(none)"
        super().__init__(
            f'composition "{comp_path}" (containing the annotation at {source}) is not mounted in index.html. '
            f"Known mounts: {known_str}. "
            f"Add a [data-composition-src] in index.html or move the annotation to a mounted composition."
        )
        self.comp_path = comp_path
        self.source = source
        self.known_mounts = known_mounts


class OverridesShapeError(SfxPlanError):
    def __init__(self, *, message: str) -> None:
        super().__init__(f"sfx-overrides.yml is malformed: {message}")


class FfmpegNotFoundError(SfxPlanError):
    def __init__(self) -> None:
        super().__init__(
            "ffmpeg not found on PATH — required for --bake. "
            "Install it (macOS: brew install ffmpeg) and retry."
        )


class FfmpegBakeError(SfxPlanError):
    def __init__(self, *, stderr_tail: str) -> None:
        super().__init__(
            "ffmpeg failed to bake the SFX mix:\n" + stderr_tail
        )
        self.stderr_tail = stderr_tail
