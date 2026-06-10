"""Pure scene-boundary detection math for the whole-video ``pace`` workflow.

This module turns two precomputed time series — the full-fps ffmpeg scene-score
series (``frames.SceneCut``) and the low-fps HSV-delta feature series
(``FeatureRow``, computed by ``cli.py``'s pipe pass) — into a merged, deduped
boundary list and the scene windows that tile the proxy.

Hard cuts use an adaptive threshold (rolling-median ratio + absolute floor +
min-gap debounce) instead of a fixed ffmpeg threshold: a fixed threshold cannot
serve motion-graphics content (false positives during animation at low T,
missed subtle talking-head cuts at high T). Soft transitions (crossfades,
wipes) — which adjacent-frame metrics are structurally blind to — are detected
as sustained wide-baseline plateaus with moderate adjacent deltas.

Module boundary (authoritative): this file is PURE. It performs no file,
network, or subprocess I/O and never imports ``cv2``. ``cli.py`` owns the
ffmpeg/yt-dlp subprocesses and all ``cv2`` work, pre-rounds every series
(``t`` to 3dp, values to 4dp) before handing it here so platform jitter cannot
flip a boundary, and consumes the resulting ``SceneWindow`` list. Every
tie-break is explicit and deterministic (earlier time wins).
"""
from __future__ import annotations

from bisect import bisect_left, insort
from dataclasses import dataclass

from .frames import SceneCut


@dataclass(frozen=True)
class FeatureRow:
    """One sampled frame-pair's HSV-delta features from the low-fps pipe pass.

    Attributes:
        t_s: Absolute proxy time of the sample, in seconds (pre-rounded to 3dp).
        adj_delta: Mean absolute HSV delta vs the previous sample, normalized to
            0-1 (pre-rounded to 4dp).
        wide_delta: Mean absolute HSV delta vs the sample ~1s earlier, normalized
            to 0-1 (pre-rounded to 4dp); ``0.0`` while the ring buffer warms up.
    """

    t_s: float
    adj_delta: float
    wide_delta: float


@dataclass(frozen=True)
class Boundary:
    """One detected scene boundary: its absolute proxy time, kind, and evidence score.

    Attributes:
        t_s: Absolute proxy time of the boundary, in seconds.
        kind: ``"cut"`` (hard cut from the scene-score series) or ``"soft"``
            (crossfade/wipe from the wide-baseline plateau detector).
        score: The ffmpeg scene score for cuts; the plateau's peak ``wide_delta``
            for soft transitions.
    """

    t_s: float
    kind: str
    score: float


@dataclass(frozen=True)
class SceneWindow:
    """One scene as a half-open window of the proxy timeline.

    Attributes:
        index: 1-based scene index in time order.
        start_s: Absolute start time in seconds (scene 1 starts at ``0.0``).
        end_s: Absolute end time in seconds (the next boundary, or the proxy
            duration for the last scene).
        boundary_kind: The kind of the boundary that OPENS this scene:
            ``"start"`` for scene 1, else ``"cut"`` or ``"soft"``.
        boundary_score: The opening boundary's score; ``None`` for scene 1.
    """

    index: int
    start_s: float
    end_s: float
    boundary_kind: str
    boundary_score: float | None


def detect_hard_cuts(
    cuts: list[SceneCut],
    *,
    abs_floor: float,
    ratio: float,
    window_s: float,
    min_gap_s: float,
) -> list[Boundary]:
    """Detect hard cuts in a full-fps scene-score series via an adaptive threshold.

    A frame qualifies as a cut iff ``score >= max(abs_floor, ratio *
    rolling_median)``, where ``rolling_median`` is the median of the scores in
    ``[t - window_s/2, t + window_s/2]`` EXCLUDING the frame itself (an empty
    window yields ``0.0``). The rolling window slides with two pointers and a
    bisect-sorted score list, so the pass stays near O(n * w) list shifts with a
    small w rather than a full per-frame window scan.

    Qualifying frames are then debounced: within any run of qualifying frames
    where each is closer than ``min_gap_s`` to the previous, only the
    highest-score frame survives (ties broken by earlier time).

    Args:
        cuts: Scored frames from ``frames.parse_scene_scores``, any order.
        abs_floor: Absolute score floor a cut must always clear.
        ratio: Multiplier on the rolling median forming the adaptive threshold.
        window_s: Full width of the centered rolling-median window, in seconds.
        min_gap_s: Debounce gap; qualifying frames closer than this cluster.

    Returns:
        Time-ordered ``Boundary`` objects with ``kind="cut"``.
    """
    if not cuts:
        return []

    ordered = sorted(cuts, key=lambda c: c.time_s)
    times = [c.time_s for c in ordered]
    half = window_s / 2.0

    window: list[float] = []
    lo = 0
    hi = 0
    qualifying: list[SceneCut] = []
    for cut in ordered:
        while hi < len(ordered) and times[hi] <= cut.time_s + half:
            insort(window, ordered[hi].score)
            hi += 1
        while lo < hi and times[lo] < cut.time_s - half:
            window.pop(bisect_left(window, ordered[lo].score))
            lo += 1
        # The frame's own score is always inside its centered window; remove one
        # instance so the median reflects only its neighbors, then restore it.
        self_idx = bisect_left(window, cut.score)
        window.pop(self_idx)
        median = _median_of_sorted(window)
        window.insert(self_idx, cut.score)

        if cut.score >= max(abs_floor, ratio * median):
            qualifying.append(cut)

    boundaries: list[Boundary] = []
    run: list[SceneCut] = []
    for cut in qualifying:
        if run and cut.time_s - run[-1].time_s < min_gap_s:
            run.append(cut)
        else:
            if run:
                boundaries.append(_best_of_run(run))
            run = [cut]
    if run:
        boundaries.append(_best_of_run(run))
    return boundaries


def _best_of_run(run: list[SceneCut]) -> Boundary:
    best = min(run, key=lambda c: (-c.score, c.time_s))
    return Boundary(t_s=best.time_s, kind="cut", score=best.score)


def _median_of_sorted(values: list[float]) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2 == 1:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def detect_soft_transitions(
    rows: list[FeatureRow],
    *,
    wide_min: float,
    adj_max: float,
    min_plateau_s: float,
    hard_cuts: list[Boundary],
    suppress_s: float,
) -> list[Boundary]:
    """Detect soft transitions (crossfades/wipes) as wide-baseline plateaus.

    A plateau is a maximal run of consecutive rows with ``wide_delta >=
    wide_min`` AND ``adj_delta <= adj_max`` whose time span is at least
    ``min_plateau_s``: the frame keeps drifting far from where it was ~1s ago
    while no single adjacent step is large — the signature adjacent-frame
    metrics are blind to. The boundary lands on the row with the maximum
    ``wide_delta`` in the plateau (ties broken by earlier time). Candidates
    within ``suppress_s`` of any hard cut are dropped (the cut already explains
    the change).

    Args:
        rows: Time-ordered feature rows from the low-fps pipe pass.
        wide_min: Minimum ``wide_delta`` for a row to belong to a plateau.
        adj_max: Maximum ``adj_delta`` for a row to belong to a plateau.
        min_plateau_s: Minimum plateau time span (first to last row).
        hard_cuts: Detected hard-cut boundaries used for suppression.
        suppress_s: Drop a candidate whose time is within this of a hard cut.

    Returns:
        Time-ordered ``Boundary`` objects with ``kind="soft"``.
    """
    cut_times = sorted(b.t_s for b in hard_cuts)

    def near_hard_cut(t: float) -> bool:
        idx = bisect_left(cut_times, t)
        for j in (idx - 1, idx):
            if 0 <= j < len(cut_times) and abs(cut_times[j] - t) <= suppress_s:
                return True
        return False

    boundaries: list[Boundary] = []
    n = len(rows)
    i = 0
    while i < n:
        if not (rows[i].wide_delta >= wide_min and rows[i].adj_delta <= adj_max):
            i += 1
            continue
        j = i
        while j < n and rows[j].wide_delta >= wide_min and rows[j].adj_delta <= adj_max:
            j += 1
        plateau = rows[i:j]
        if plateau[-1].t_s - plateau[0].t_s >= min_plateau_s:
            peak = min(plateau, key=lambda r: (-r.wide_delta, r.t_s))
            if not near_hard_cut(peak.t_s):
                boundaries.append(
                    Boundary(t_s=peak.t_s, kind="soft", score=peak.wide_delta)
                )
        i = j
    return boundaries


def merge_boundaries(
    hard: list[Boundary],
    soft: list[Boundary],
    *,
    dedupe_s: float,
    duration_s: float,
) -> list[Boundary]:
    """Merge hard and soft boundaries into one deduped, time-ordered list.

    Boundaries at ``t <= 0`` or ``t >= duration_s`` are dropped, the rest are
    sorted by time, and any chain of boundaries where each is within
    ``dedupe_s`` of the previous collapses to a single winner: hard beats soft,
    then higher score, then earlier time.

    Args:
        hard: Hard-cut boundaries.
        soft: Soft-transition boundaries.
        dedupe_s: Boundaries within this of each other collapse to one.
        duration_s: Proxy duration; bounds the valid open interval for boundaries.

    Returns:
        Time-ordered, deduped boundaries strictly inside ``(0, duration_s)``.
    """
    pool = [b for b in [*hard, *soft] if 0.0 < b.t_s < duration_s]
    pool.sort(key=lambda b: (b.t_s, b.kind != "cut", -b.score))

    merged: list[Boundary] = []
    cluster: list[Boundary] = []
    for b in pool:
        if cluster and b.t_s - cluster[-1].t_s <= dedupe_s:
            cluster.append(b)
        else:
            if cluster:
                merged.append(_cluster_winner(cluster))
            cluster = [b]
    if cluster:
        merged.append(_cluster_winner(cluster))
    return merged


def _cluster_winner(cluster: list[Boundary]) -> Boundary:
    return min(cluster, key=lambda b: (b.kind != "cut", -b.score, b.t_s))


def build_scenes(boundaries: list[Boundary], *, duration_s: float) -> list[SceneWindow]:
    """Turn a boundary list into scene windows tiling ``[0, duration_s]`` exactly.

    Scene 1 starts at ``0.0`` with ``boundary_kind="start"`` and
    ``boundary_score=None``; each subsequent scene opens at one boundary and
    closes at the next (the last closes at ``duration_s``). Boundaries outside
    ``(0, duration_s)`` are ignored so the tiling invariant (no gaps, no
    overlaps, no zero-width windows from edge boundaries) always holds.

    Args:
        boundaries: Detected boundaries, any order.
        duration_s: Proxy duration; must be positive.

    Returns:
        1-based-indexed scene windows in time order.

    Raises:
        ValueError: If ``duration_s`` is not positive.
    """
    if duration_s <= 0.0:
        raise ValueError("duration_s must be positive")

    inside = sorted(
        (b for b in boundaries if 0.0 < b.t_s < duration_s), key=lambda b: b.t_s
    )
    openers: list[tuple[float, str, float | None]] = [(0.0, "start", None)]
    openers.extend((b.t_s, b.kind, b.score) for b in inside)

    scenes: list[SceneWindow] = []
    for idx, (start, kind, score) in enumerate(openers, start=1):
        end = openers[idx][0] if idx < len(openers) else duration_s
        scenes.append(
            SceneWindow(
                index=idx,
                start_s=start,
                end_s=end,
                boundary_kind=kind,
                boundary_score=score,
            )
        )
    return scenes
