"""Pure motion-graphics detection math over a dense-optical-flow time series.

This module is the deterministic heart of the whole-video ``scan`` workflow. It
holds the per-frame flow descriptor (``FlowFingerprint``), the named threshold
constants that encode the validated two-axis motion-graphics gate, and the pure
functions that turn a time series of fingerprints into auto-segmented animation
beats with objective motion descriptors.

Module boundary (authoritative): this file is PURE. The only third-party import is
``numpy``. It performs no file, network, or subprocess I/O and never imports
``cv2``. ``cli.py`` owns ``cv2`` (lazily imported inside the scan codepath only):
it decodes the proxy, computes the DIS optical-flow field per sampled frame pair,
reduces that field plus the bgr frame into one ``FlowFingerprint`` (using
``cv2`` for ``boxFilter``/``Sobel``/``cvtColor``/``resize`` and this module's
``gini`` on the 16x16 block-energy grid), and hands the resulting
``list[FlowFingerprint]`` to ``segment``. Pure tests import this module (numpy)
plus the stdlib-only ``frames``/``strip`` helpers; they must not import ``cv2``.

The math is ported from ``scratch/mg_probe_v3.py`` (validated on 16 clips) and
generalized from a single fixed window to an arbitrary-length time series:

* ``detect_events`` / ``gini`` are ported verbatim in behavior, with the energy
  floor lifted to a parameter.
* ``adaptive_floor`` is new: it replaces the prototype's fixed ``0.20`` floor,
  which a slow growth-map animation fell below, with a median-relative floor that
  still keeps an absolute ``ABS_FLOOR_MIN`` so sensor noise is never "detected."
* ``spatial_concentration_over_top`` fixes the prototype's ``else 0.0`` bug:
  spatial concentration is computed over the top-energy frames even when nothing
  clears the floor, so a real-but-subtle beat is never assigned a spurious 0.
* ``gate`` exposes the validated thresholds as greppable named constants.
* ``segment`` runs the full beat pipeline (active runs -> split on hard cuts ->
  gate -> merge sub-gap neighbors -> drop sub-min-beat blips -> pad -> score ->
  cap top-N -> re-sort by time), mirroring ``frames.rank_cuts``' rank-then-retime.
* ``describe`` maps the aggregated metrics to objective descriptor fields only.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# --- Gate thresholds (validated on 16 clips; the two-axis motion-graphics separator) ---

# Eased-energy axis: a window whose energy is dominated by punctuated, unimodal
# ease-in/ease-out events (kinetic type, transitions) is motion graphics.
EASED_SHARE_MIN: float = 0.30

# Continuous axis: a window of small, smooth, localized motion against a still
# background (bar-chart race, data-viz) is motion graphics *only if* its moving
# region is also flat (low texture) — that appearance axis cracks the bar-race /
# talking-head twin, which is statistically identical on motion alone.
SPARSITY_MIN: float = 0.6
CONCENTRATION_MIN: float = 0.6
MOV_TEXTURE_MAX: float = 18.0

# --- Adaptive energy floor (replaces the prototype's fixed EVENT_FLOOR = 0.20) ---

# Absolute floor below which mean flow magnitude is treated as sensor/codec noise,
# never as motion. The adaptive floor never drops below this even on a quiet clip.
ABS_FLOOR_MIN: float = 0.20

# Multiplier on the median of the nonzero energy series; the adaptive floor is the
# larger of ABS_FLOOR_MIN and this fraction of the typical active energy.
ADAPTIVE_FLOOR_K: float = 0.5

# --- Energy -> 4-level descriptor thresholds (calibrated from the 16-clip data) ---
# Mean flow magnitude (px) at the proxy's 256px scale. Boundaries are inclusive
# upper edges: energy < calm-max -> "calm", < measured-max -> "measured",
# < punchy-max -> "punchy", else "frenetic".
ENERGY_CALM_MAX: float = 0.5
ENERGY_MEASURED_MAX: float = 1.5
ENERGY_PUNCHY_MAX: float = 3.5

# --- Event-shape constants (ported from mg_probe_v3, used by detect_events) ---

# A short, tall energy burst is a hard scene cut, not an eased move.
SPIKE_MAXLEN: int = 2
SPIKE_PEAK: float = 3.0

# A genuine ease has a sustained, unimodal (single rise-then-fall) energy hump.
EASED_MINLEN: int = 3
EASED_MAXLEN: int = 30
EASED_MIN_PEAK: float = 0.5
UNIMODAL_MIN: float = 0.65

# Below this peak a long active run is slow background drift, not a designed move.
DRIFT_MAX_PEAK: float = 1.0

# Default number of top-energy frames spatial concentration falls back to when no
# frame clears the floor (see spatial_concentration_over_top).
TOP_K_DEFAULT: int = 5

# Quantization tolerance (seconds) applied to fingerprint timestamps before
# segmentation so sub-millisecond flow/decode jitter cannot flip a beat boundary
# on a different platform. Boundaries are derived from these quantized times.
TIME_QUANTIZE_S: float = 0.001


@dataclass(frozen=True)
class FlowFingerprint:
    """One sampled frame pair's reduced optical-flow descriptor, keyed by absolute time.

    ``cli.py`` computes one of these per sampled DIS-flow frame pair from the flow
    field plus the current bgr frame. All fields are scalar per-frame reductions so
    the segmentation math stays a pure numpy time series with no flow arrays.

    Values are quantized/rounded to a fixed tolerance by ``cli.py`` before being
    handed to ``segment`` so cross-platform flow jitter cannot flip a beat boundary.

    Attributes:
        t_s: Absolute time of this sample within the proxy, in seconds. The series
            is keyed by absolute time (not frame index) because flow fps differs
            from proxy fps; this avoids an off-by-fps beat-boundary bug.
        motion_energy: Mean flow magnitude over the frame (px at proxy scale).
        sparsity: Fraction of pixels whose flow magnitude is below the zero
            epsilon (high -> motion is confined to a small region).
        spatial_concentration: Gini coefficient of the 16x16 block-energy grid for
            this frame (high -> motion concentrated in few blocks). Per-frame; the
            window-level value is taken over active/top frames in aggregation.
        mov_texture: Median local pixel std inside the moving region (the appearance
            axis: flat designed fills -> low, textured skin -> high).
        mov_sat: Mean HSV saturation of the moving region (designed fills are often
            more saturated). Carried for descriptor/diagnostics; not in the gate.
        axis_aligned: Fraction of strong moving-region edges within the axis
            tolerance of horizontal/vertical (bars/UI high). Diagnostic; not gated.
    """

    t_s: float
    motion_energy: float
    sparsity: float
    spatial_concentration: float
    mov_texture: float
    mov_sat: float
    axis_aligned: float


@dataclass(frozen=True)
class MotionEvent:
    """One contiguous above-floor energy run, classified by its temporal shape.

    Produced by ``detect_events`` over the energy series. Indices are positions in
    the energy array passed to ``detect_events`` (frame-sample indices, not seconds).

    Attributes:
        start_idx: Index of the first above-floor sample in the run.
        length: Number of samples in the run.
        peak: Maximum energy value within the run.
        energy: Sum of energy over the run (used for eased_energy_share).
        kind: One of ``"cut"`` (short spike), ``"eased"`` (sustained unimodal hump),
            ``"drift"`` (long low background drift), or ``"other"``.
    """

    start_idx: int
    length: int
    peak: float
    energy: float
    kind: str


@dataclass(frozen=True)
class BeatWindow:
    """A finalized, padded animation-beat window in absolute proxy seconds.

    The unit ``segment`` emits and ``cli.py`` captures: scene-detect the proxy once,
    partition cuts into this window, and extract the hero/strip frames at
    ``start_s + cut.time_s``.

    Attributes:
        start_s: Absolute start time of the beat in the proxy, in seconds (padded
            and clamped to ``[0, video_duration_s]``).
        end_s: Absolute end time of the beat in the proxy, in seconds (padded and
            clamped). Always strictly greater than ``start_s``.
        gate_kind: The gate verdict that accepted this window: ``"eased"`` or
            ``"continuous"``.
        score: The motion-graphics ranking score used to cap to the top-N beats.
        metrics: The aggregated window metrics this window was gated and scored on.
    """

    start_s: float
    end_s: float
    gate_kind: str
    score: float
    metrics: "BeatMetrics"


@dataclass(frozen=True)
class BeatMetrics:
    """Window-level aggregate of per-frame fingerprints, the unit the gate consumes.

    Produced by ``aggregate_window_metrics`` over a contiguous slice of fingerprints
    and carried on each ``BeatWindow``. All fields are objective reductions.

    Attributes:
        motion_energy: Median motion energy over the window (drives the energy level
            and the ranking score).
        sparsity: Median sparsity over the window (continuous-axis input).
        spatial_concentration: Median per-frame gini over the window's active (or
            top-energy fallback) frames (continuous-axis input).
        eased_energy_share: Fraction of total window energy carried by ``"eased"``
            events (eased-axis input and cadence descriptor input).
        eased_events: Count of ``"eased"`` events in the window.
        mov_texture: Median moving-region texture over frames that had enough moving
            pixels to score appearance; ``nan`` if none did (appearance-axis input).
        mov_sat: Median moving-region saturation, or ``nan`` if unscored.
        axis_aligned: Median moving-region axis-alignment fraction, or ``nan``.
        n_frames: Number of fingerprints aggregated into this window.
    """

    motion_energy: float
    sparsity: float
    spatial_concentration: float
    eased_energy_share: float
    eased_events: int
    mov_texture: float
    mov_sat: float
    axis_aligned: float
    n_frames: int


@dataclass(frozen=True)
class BeatDescriptor:
    """Objective, human-review-ready descriptor of a beat's motion character.

    Produced by ``describe`` from ``BeatMetrics``. Carries ONLY objective fields
    derived from the flow statistics. It never auto-fills the subjective fields the
    human author owns: ``motion=`` verbs, ``archetype``, ``mood``, ``Use when``, or
    the prose ``Motion:`` note.

    Attributes:
        energy: One of ``"calm"``, ``"measured"``, ``"punchy"``, ``"frenetic"``,
            from the energy 4-level thresholds.
        cadence: ``"punctuated"`` when eased events dominate the window's energy
            (``eased_energy_share >= EASED_SHARE_MIN``), else ``"continuous"``.
        spatial: ``"localized"`` when motion is sparse and concentrated
            (``sparsity >= SPARSITY_MIN and spatial_concentration >=
            CONCENTRATION_MIN``), else ``"full-frame"``.
    """

    energy: str
    cadence: str
    spatial: str


def gini(values: np.ndarray) -> float:
    """Return the Gini coefficient of a nonnegative value array (ported verbatim).

    Flattens and sorts ``values`` ascending, then computes the standard Gini
    formula ``(2 * sum(i * v_i)) / (n * sum(v)) - (n + 1) / n`` over 1-based ranks.
    Returns ``0.0`` for an empty array or one whose sum is effectively zero (a
    perfectly uniform / all-zero distribution has no concentration). Used on a
    frame's 16x16 block-energy grid to measure spatial concentration.

    Args:
        values: Nonnegative values (e.g. a flattened 16x16 block-energy grid).

    Returns:
        Gini coefficient in ``[0.0, 1.0]``.
    """
    v = np.sort(np.asarray(values, dtype=np.float64).ravel())
    n = v.size
    s = v.sum()
    if n == 0 or s <= 1e-9:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2.0 * (idx * v).sum()) / (n * s) - (n + 1) / n)


def adaptive_floor(energy: np.ndarray) -> float:
    """Return the median-relative energy floor for one clip's energy series.

    Replaces the prototype's fixed ``EVENT_FLOOR = 0.20`` (which a slow growth-map
    animation fell below) with ``max(ABS_FLOOR_MIN, ADAPTIVE_FLOOR_K * median(nonzero
    energy))``. Taking the median over nonzero samples keeps long still stretches
    from dragging the floor to zero, and the ``ABS_FLOOR_MIN`` clamp keeps sensor
    and codec noise from ever being "detected" as motion. Returns ``ABS_FLOOR_MIN``
    when the series is empty or all-zero.

    Args:
        energy: Per-frame mean-flow-magnitude series.

    Returns:
        The energy floor in the same units as ``energy``.
    """
    e = np.asarray(energy, dtype=np.float64).ravel()
    nonzero = e[e > 0.0]
    if nonzero.size == 0:
        return ABS_FLOOR_MIN
    return float(max(ABS_FLOOR_MIN, ADAPTIVE_FLOOR_K * float(np.median(nonzero))))


def detect_events(energy: np.ndarray, *, floor: float) -> list[MotionEvent]:
    """Segment an energy series into classified above-floor runs (ported from v3).

    Walks the series, and for each maximal run of samples with ``energy > floor``
    measures its length, peak, summed energy, peak position, and unimodality (the
    mean of "rise is non-decreasing up to the peak" and "fall is non-increasing
    after the peak"). It then classifies the run:

    * ``"cut"`` if ``length <= SPIKE_MAXLEN`` and ``peak >= SPIKE_PEAK`` (a short,
      tall spike — a hard scene cut).
    * ``"eased"`` if ``EASED_MINLEN <= length <= EASED_MAXLEN`` and
      ``peak >= EASED_MIN_PEAK`` and ``unimodal >= UNIMODAL_MIN`` (a sustained,
      single-humped ease — the motion-graphics signature).
    * ``"drift"`` if ``length > EASED_MAXLEN`` and ``peak < DRIFT_MAX_PEAK`` (a long,
      low background drift — a slow pan, not a designed move).
    * ``"other"`` otherwise.

    The ``floor`` is now a parameter (callers pass ``adaptive_floor(energy)``)
    rather than the prototype's module constant.

    Args:
        energy: Per-frame mean-flow-magnitude series.
        floor: Energy threshold above which a sample is "active".

    Returns:
        Events in source (time) order; empty when no sample clears the floor.
    """
    e = np.asarray(energy, dtype=np.float64).ravel()
    above = e > floor
    events: list[MotionEvent] = []
    i, n = 0, e.size
    while i < n:
        if not above[i]:
            i += 1
            continue
        j = i
        while j < n and above[j]:
            j += 1
        seg = e[i:j]
        length = int(seg.size)
        peak = float(seg.max())
        peak_idx = int(seg.argmax())
        rise = seg[: peak_idx + 1]
        fall = seg[peak_idx:]
        rise_ok = float(np.mean(np.diff(rise) >= -1e-6)) if rise.size > 1 else 1.0
        fall_ok = float(np.mean(np.diff(fall) <= 1e-6)) if fall.size > 1 else 1.0
        unimodal = (rise_ok + fall_ok) / 2.0
        if length <= SPIKE_MAXLEN and peak >= SPIKE_PEAK:
            kind = "cut"
        elif (
            EASED_MINLEN <= length <= EASED_MAXLEN
            and peak >= EASED_MIN_PEAK
            and unimodal >= UNIMODAL_MIN
        ):
            kind = "eased"
        elif length > EASED_MAXLEN and peak < DRIFT_MAX_PEAK:
            kind = "drift"
        else:
            kind = "other"
        events.append(
            MotionEvent(
                start_idx=i,
                length=length,
                peak=peak,
                energy=float(seg.sum()),
                kind=kind,
            )
        )
        i = j
    return events


def spatial_concentration_over_top(
    ginis: np.ndarray,
    energy: np.ndarray,
    *,
    floor: float,
    top_k: int = TOP_K_DEFAULT,
) -> float:
    """Return window spatial concentration, robust to no frame clearing the floor.

    The prototype took ``median(ginis[energy > floor])`` and returned ``0.0`` when
    no frame was active — spuriously labeling a real-but-subtle beat as having no
    spatial structure. This computes the median per-frame gini over the active
    frames when any clear the floor, and otherwise falls back to the median gini
    over the ``top_k`` highest-energy frames (so concentration always reflects where
    the motion actually is). Returns ``0.0`` only for an empty input.

    Args:
        ginis: Per-frame spatial-concentration (gini) series.
        energy: Per-frame energy series, aligned to ``ginis``.
        floor: Energy threshold defining "active" frames.
        top_k: Number of highest-energy frames used for the no-active fallback.

    Returns:
        Median spatial concentration over the chosen frame subset.
    """
    g = np.asarray(ginis, dtype=np.float64).ravel()
    e = np.asarray(energy, dtype=np.float64).ravel()
    if g.size == 0:
        return 0.0
    active = e > floor
    if active.any():
        return float(np.median(g[active]))
    k = max(1, min(int(top_k), g.size))
    top_idx = np.argsort(e)[-k:]
    return float(np.median(g[top_idx]))


def aggregate_window_metrics(fingerprints_slice: list[FlowFingerprint]) -> BeatMetrics:
    """Reduce a contiguous slice of fingerprints into window-level ``BeatMetrics``.

    Builds the per-frame energy / sparsity / gini / texture / saturation /
    axis-alignment series from the slice, derives the window's adaptive floor from
    its energy, runs ``detect_events`` to compute ``eased_energy_share`` (summed
    ``"eased"`` energy over total window energy) and ``eased_events``, takes
    ``spatial_concentration`` via ``spatial_concentration_over_top``, and medians the
    remaining fields. Appearance medians (``mov_texture``/``mov_sat``/``axis_aligned``)
    are taken only over frames whose moving region was large enough for ``cli.py`` to
    score them; they are ``nan`` when no frame qualified.

    Args:
        fingerprints_slice: Contiguous, time-ordered fingerprints for one window.

    Returns:
        The aggregated window metrics.

    Raises:
        ValueError: If ``fingerprints_slice`` is empty.
    """
    if not fingerprints_slice:
        raise ValueError("aggregate_window_metrics requires a non-empty slice")

    energy = np.array([fp.motion_energy for fp in fingerprints_slice], dtype=np.float64)
    sparsity = np.array([fp.sparsity for fp in fingerprints_slice], dtype=np.float64)
    ginis = np.array(
        [fp.spatial_concentration for fp in fingerprints_slice], dtype=np.float64
    )
    texture = np.array([fp.mov_texture for fp in fingerprints_slice], dtype=np.float64)
    saturation = np.array([fp.mov_sat for fp in fingerprints_slice], dtype=np.float64)
    axis = np.array([fp.axis_aligned for fp in fingerprints_slice], dtype=np.float64)

    floor = adaptive_floor(energy)
    events = detect_events(energy, floor=floor)
    eased = [ev for ev in events if ev.kind == "eased"]
    total = float(energy.sum()) or 1.0
    eased_energy_share = float(sum(ev.energy for ev in eased) / total)

    concentration = spatial_concentration_over_top(ginis, energy, floor=floor)

    def med_scored(values: np.ndarray) -> float:
        scored = values[~np.isnan(values)]
        return float(np.median(scored)) if scored.size else float("nan")

    return BeatMetrics(
        motion_energy=float(np.median(energy)),
        sparsity=float(np.median(sparsity)),
        spatial_concentration=concentration,
        eased_energy_share=eased_energy_share,
        eased_events=len(eased),
        mov_texture=med_scored(texture),
        mov_sat=med_scored(saturation),
        axis_aligned=med_scored(axis),
        n_frames=len(fingerprints_slice),
    )


def gate(metrics: BeatMetrics) -> str | None:
    """Apply the validated two-axis motion-graphics gate to one window's metrics.

    Returns:

    * ``"eased"`` if ``eased_energy_share >= EASED_SHARE_MIN`` (punctuated motion
      graphics: kinetic type, transitions); else
    * ``"continuous"`` if ``sparsity >= SPARSITY_MIN`` and ``spatial_concentration
      >= CONCENTRATION_MIN`` and ``mov_texture <= MOV_TEXTURE_MAX`` (continuous
      designed motion graphics: bar race, data-viz — the appearance axis rejects a
      textured talking head that is otherwise a motion twin); else
    * ``None`` (not motion graphics).

    A ``nan`` ``mov_texture`` (no frame had enough moving pixels to score
    appearance) fails the ``<=`` comparison and cannot pass the continuous axis.

    Args:
        metrics: The aggregated window metrics.

    Returns:
        ``"eased"``, ``"continuous"``, or ``None``.
    """
    if metrics.eased_energy_share >= EASED_SHARE_MIN:
        return "eased"
    if (
        metrics.sparsity >= SPARSITY_MIN
        and metrics.spatial_concentration >= CONCENTRATION_MIN
        and metrics.mov_texture <= MOV_TEXTURE_MAX
    ):
        return "continuous"
    return None


def describe(metrics: BeatMetrics) -> BeatDescriptor:
    """Map aggregated metrics to a beat's objective descriptor.

    Derives only objective fields:

    * ``energy``: ``motion_energy`` bucketed by the 4-level thresholds
      (``< ENERGY_CALM_MAX`` -> ``"calm"``, ``< ENERGY_MEASURED_MAX`` ->
      ``"measured"``, ``< ENERGY_PUNCHY_MAX`` -> ``"punchy"``, else ``"frenetic"``).
    * ``cadence``: ``"punctuated"`` when ``eased_energy_share >= EASED_SHARE_MIN``,
      else ``"continuous"``.
    * ``spatial``: ``"localized"`` when ``sparsity >= SPARSITY_MIN`` and
      ``spatial_concentration >= CONCENTRATION_MIN``, else ``"full-frame"``.

    Never fills the human-owned subjective fields (``motion=`` verbs, ``archetype``,
    ``mood``, ``Use when``, the prose ``Motion:`` note).

    Args:
        metrics: The aggregated window metrics.

    Returns:
        The objective beat descriptor.
    """
    e = metrics.motion_energy
    if e < ENERGY_CALM_MAX:
        energy = "calm"
    elif e < ENERGY_MEASURED_MAX:
        energy = "measured"
    elif e < ENERGY_PUNCHY_MAX:
        energy = "punchy"
    else:
        energy = "frenetic"

    cadence = (
        "punctuated" if metrics.eased_energy_share >= EASED_SHARE_MIN else "continuous"
    )

    spatial = (
        "localized"
        if metrics.sparsity >= SPARSITY_MIN
        and metrics.spatial_concentration >= CONCENTRATION_MIN
        else "full-frame"
    )

    return BeatDescriptor(energy=energy, cadence=cadence, spatial=spatial)


def segment(
    fingerprints: list[FlowFingerprint],
    *,
    min_beat_s: float,
    merge_gap_s: float,
    pad_s: float,
    max_beats: int,
    floor_fn,
    video_duration_s: float,
) -> list[BeatWindow]:
    """Auto-segment a fingerprint time series into the top-N motion-graphics beats.

    Mirrors ``frames.rank_cuts``' rank-then-retime discipline, lifted to a whole
    video:

    1. Build the energy series and derive the global active floor via ``floor_fn``
       (e.g. ``adaptive_floor``).
    2. Find maximal contiguous active runs (``energy > floor``).
    3. Split each run on hard cuts (``"cut"`` events from ``detect_events``) so two
       distinct animations separated by a transition don't fuse into one beat.
    4. Gate each candidate run via ``aggregate_window_metrics`` + ``gate``; drop
       runs the gate rejects (``None``).
    5. Merge gated neighbors whose time gap is ``<= merge_gap_s`` (re-aggregating the
       fused slice) so a flicker between sub-beats doesn't fragment one animation.
    6. Drop blips shorter than ``min_beat_s``.
    7. Pad each surviving window by ``pad_s`` on both sides, clamped to
       ``[0.0, video_duration_s]``.
    8. Score each window (``mg_score``: energy- and share-weighted) and keep the top
       ``max_beats`` by score (ties broken by earlier start), then re-sort the
       survivors by ``start_s`` so the emitted beats are time-ordered.

    All window times are absolute proxy seconds taken from ``FlowFingerprint.t_s``.

    Args:
        fingerprints: Time-ordered per-frame fingerprints spanning the proxy.
        min_beat_s: Minimum beat duration; shorter candidates are dropped.
        merge_gap_s: Maximum gap between gated neighbors that still merges them.
        pad_s: Padding added to each side of a window before clamping.
        max_beats: Maximum number of beats to emit (top-N by score).
        floor_fn: Callable mapping the energy series to an active floor (e.g.
            ``adaptive_floor``).
        video_duration_s: Proxy duration, the clamp bound for padded windows.

    Returns:
        Up to ``max_beats`` time-ordered ``BeatWindow`` objects; empty when no run
        passes the gate (a no-motion-graphics video yields ``[]``).
    """
    n = len(fingerprints)
    if n == 0:
        return []

    energy = np.array([fp.motion_energy for fp in fingerprints], dtype=np.float64)
    floor = float(floor_fn(energy))

    # Quantize timestamps to a fixed tolerance so tiny jitter can't move a boundary.
    times = np.array(
        [round(fp.t_s / TIME_QUANTIZE_S) * TIME_QUANTIZE_S for fp in fingerprints],
        dtype=np.float64,
    )

    above = energy > floor

    # 1-2. Maximal contiguous active runs as [start, end) index ranges.
    raw_runs: list[tuple[int, int]] = []
    i = 0
    while i < n:
        if not above[i]:
            i += 1
            continue
        j = i
        while j < n and above[j]:
            j += 1
        raw_runs.append((i, j))
        i = j

    # 3. Split each active run on hard cuts so a transition doesn't fuse two beats.
    split_runs: list[tuple[int, int]] = []
    for start, end in raw_runs:
        seg_energy = energy[start:end]
        cut_starts = [
            ev.start_idx
            for ev in detect_events(seg_energy, floor=floor)
            if ev.kind == "cut"
        ]
        boundaries = [start]
        for cs in cut_starts:
            local = start + cs
            if start < local < end and local not in boundaries:
                boundaries.append(local)
        boundaries.append(end)
        boundaries = sorted(set(boundaries))
        for a, b in zip(boundaries[:-1], boundaries[1:]):
            if b > a:
                split_runs.append((a, b))

    # 4. Gate each candidate; carry index range + gate verdict + metrics.
    gated: list[tuple[int, int, str, BeatMetrics]] = []
    for start, end in split_runs:
        metrics = aggregate_window_metrics(list(fingerprints[start:end]))
        verdict = gate(metrics)
        if verdict is not None:
            gated.append((start, end, verdict, metrics))

    if not gated:
        return []

    # 5. Merge gated neighbors whose time gap is <= merge_gap_s, re-aggregating.
    merged: list[tuple[int, int]] = []
    cur_start, cur_end = gated[0][0], gated[0][1]
    for start, end, _verdict, _metrics in gated[1:]:
        gap = times[start] - times[cur_end - 1]
        if gap <= merge_gap_s:
            cur_end = end
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
    merged.append((cur_start, cur_end))

    # Re-gate merged ranges; drop any fused run the gate now rejects.
    candidates: list[tuple[int, int, str, BeatMetrics]] = []
    for start, end in merged:
        metrics = aggregate_window_metrics(list(fingerprints[start:end]))
        verdict = gate(metrics)
        if verdict is not None:
            candidates.append((start, end, verdict, metrics))

    # 6. Drop blips shorter than min_beat_s (measured on unpadded span).
    kept: list[tuple[int, int, str, BeatMetrics]] = []
    for start, end, verdict, metrics in candidates:
        span = times[end - 1] - times[start]
        if span >= min_beat_s:
            kept.append((start, end, verdict, metrics))

    if not kept:
        return []

    # 7. Pad each surviving window, clamped to [0, video_duration_s].
    # 8. Score, cap to top-N by score (ties -> earlier start), re-sort by time.
    windows: list[BeatWindow] = []
    for start, end, verdict, metrics in kept:
        s = max(0.0, float(times[start]) - pad_s)
        e = min(video_duration_s, float(times[end - 1]) + pad_s)
        if e <= s:
            e = min(video_duration_s, s + TIME_QUANTIZE_S)
        windows.append(
            BeatWindow(
                start_s=s,
                end_s=e,
                gate_kind=verdict,
                score=_mg_score(metrics),
                metrics=metrics,
            )
        )

    windows.sort(key=lambda w: (-w.score, w.start_s))
    windows = windows[:max_beats]
    windows.sort(key=lambda w: w.start_s)
    return windows


def _mg_score(metrics: BeatMetrics) -> float:
    """Energy- and eased-share-weighted ranking score used to cap to the top-N beats.

    Higher is more strongly motion-graphics: it rewards windows that carry real
    motion energy and whose energy is dominated by punctuated eased events, while
    folding in sparse/concentrated structure. Pure of side effects; used only to
    rank candidates that already passed the gate.
    """
    energy = metrics.motion_energy if np.isfinite(metrics.motion_energy) else 0.0
    share = metrics.eased_energy_share if np.isfinite(metrics.eased_energy_share) else 0.0
    sparsity = metrics.sparsity if np.isfinite(metrics.sparsity) else 0.0
    concentration = (
        metrics.spatial_concentration
        if np.isfinite(metrics.spatial_concentration)
        else 0.0
    )
    return float(energy * (1.0 + share) + 0.5 * sparsity * concentration)
