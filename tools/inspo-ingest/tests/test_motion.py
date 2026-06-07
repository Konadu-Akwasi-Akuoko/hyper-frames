"""Pure unit tests for the motion-graphics detection math — synthetic series only.

Imports only ``inspo_ingest.motion`` (numpy) — never ``cv2``, never a real video.
Every assertion pins the module's exact logic against a hand-built numpy time series
or list of ``FlowFingerprint`` rows, mirroring the assert-exact-logic style of
``test_frames.py`` / ``test_strip.py``.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from inspo_ingest.motion import (
    ABS_FLOOR_MIN,
    ADAPTIVE_FLOOR_K,
    CONCENTRATION_MIN,
    EASED_SHARE_MIN,
    MOV_TEXTURE_MAX,
    SPARSITY_MIN,
    BeatMetrics,
    FlowFingerprint,
    adaptive_floor,
    aggregate_window_metrics,
    describe,
    detect_events,
    gate,
    gini,
    segment,
    spatial_concentration_over_top,
)


# --- fixtures / builders -----------------------------------------------------

def make_fp(
    t_s: float,
    motion_energy: float,
    *,
    sparsity: float = 0.0,
    spatial_concentration: float = 0.0,
    mov_texture: float = float("nan"),
    mov_sat: float = float("nan"),
    axis_aligned: float = float("nan"),
) -> FlowFingerprint:
    """Build one FlowFingerprint, defaulting the non-relevant fields out of the way."""
    return FlowFingerprint(
        t_s=t_s,
        motion_energy=motion_energy,
        sparsity=sparsity,
        spatial_concentration=spatial_concentration,
        mov_texture=mov_texture,
        mov_sat=mov_sat,
        axis_aligned=axis_aligned,
    )


def make_metrics(
    *,
    motion_energy: float = 1.0,
    sparsity: float = 0.0,
    spatial_concentration: float = 0.0,
    eased_energy_share: float = 0.0,
    eased_events: int = 0,
    mov_texture: float = float("nan"),
    mov_sat: float = float("nan"),
    axis_aligned: float = float("nan"),
    n_frames: int = 1,
) -> BeatMetrics:
    """Build a BeatMetrics directly so gate/describe can be exercised in isolation."""
    return BeatMetrics(
        motion_energy=motion_energy,
        sparsity=sparsity,
        spatial_concentration=spatial_concentration,
        eased_energy_share=eased_energy_share,
        eased_events=eased_events,
        mov_texture=mov_texture,
        mov_sat=mov_sat,
        axis_aligned=axis_aligned,
        n_frames=n_frames,
    )


def fps_at(
    times: list[float],
    energies: list[float],
    *,
    sparsity: float = 0.0,
    concentration: float = 0.0,
    texture: float = float("nan"),
) -> list[FlowFingerprint]:
    """Build a time-ordered fingerprint series from parallel time/energy lists."""
    return [
        make_fp(
            t,
            e,
            sparsity=sparsity,
            spatial_concentration=concentration,
            mov_texture=texture,
        )
        for t, e in zip(times, energies)
    ]


# --- gini --------------------------------------------------------------------

def test_gini_uniform_is_zero() -> None:
    # A perfectly uniform distribution has no concentration.
    assert gini(np.ones(16)) == pytest.approx(0.0, abs=1e-9)


def test_gini_single_spike_approaches_one() -> None:
    # All energy in one of n cells: gini -> (n - 1) / n, approaches 1 as n grows.
    values = np.zeros(256)
    values[0] = 1.0
    expected = (256 - 1) / 256
    assert gini(values) == pytest.approx(expected, abs=1e-9)
    assert gini(values) > 0.99


def test_gini_empty_is_zero() -> None:
    assert gini(np.array([])) == 0.0


def test_gini_all_zero_is_zero() -> None:
    assert gini(np.zeros(16)) == 0.0


# --- adaptive_floor ----------------------------------------------------------

def test_adaptive_floor_slow_monotone_drops_below_fixed_020() -> None:
    # The bug the adaptive floor fixes: a slow growth-map whose typical active energy
    # sits below 0.40 yields a floor BELOW the old fixed 0.20, so its motion is seen.
    energy = np.linspace(0.05, 0.40, 50)
    floor = adaptive_floor(energy)
    nonzero = energy[energy > 0.0]
    expected = max(ABS_FLOOR_MIN, ADAPTIVE_FLOOR_K * float(np.median(nonzero)))
    assert floor == pytest.approx(expected)
    # median ~= 0.225 -> 0.5 * 0.225 ~= 0.1125 < ABS_FLOOR_MIN, so it clamps to the
    # absolute floor here; the point: it never EXCEEDS the old fixed 0.20 on slow data.
    assert floor < 0.20 or floor == pytest.approx(ABS_FLOOR_MIN)


def test_adaptive_floor_high_energy_lifts_above_abs_floor() -> None:
    # When typical active energy is high, k * median dominates ABS_FLOOR_MIN.
    energy = np.full(20, 2.0)
    floor = adaptive_floor(energy)
    assert floor == pytest.approx(ADAPTIVE_FLOOR_K * 2.0)
    assert floor > ABS_FLOOR_MIN


def test_adaptive_floor_noise_only_stays_at_abs_floor_min() -> None:
    # Tiny noise (median well below ABS_FLOOR_MIN/k) clamps to the absolute floor,
    # so sensor/codec noise is never "detected" as motion.
    rng = np.random.default_rng(0)
    energy = rng.uniform(0.001, 0.02, size=100)
    assert adaptive_floor(energy) == pytest.approx(ABS_FLOOR_MIN)


def test_adaptive_floor_empty_returns_abs_floor_min() -> None:
    assert adaptive_floor(np.array([])) == ABS_FLOOR_MIN


def test_adaptive_floor_all_zero_returns_abs_floor_min() -> None:
    # Zeros are excluded by the nonzero filter; nothing left -> ABS_FLOOR_MIN.
    assert adaptive_floor(np.zeros(40)) == ABS_FLOOR_MIN


# --- spatial_concentration_over_top ------------------------------------------

def test_spatial_concentration_uses_active_frames_when_any_clear_floor() -> None:
    ginis = np.array([0.1, 0.9, 0.8, 0.2])
    energy = np.array([0.0, 1.0, 1.0, 0.0])  # frames 1,2 are active above floor 0.2
    val = spatial_concentration_over_top(ginis, energy, floor=0.2)
    assert val == pytest.approx(np.median([0.9, 0.8]))


def test_spatial_concentration_all_sub_floor_falls_back_to_top_k_never_zero() -> None:
    # No frame clears the floor: the prototype's else-0.0 bug. Here we return the
    # median gini over the top-k highest-energy frames — a real value, never 0.0.
    ginis = np.array([0.10, 0.70, 0.50, 0.60, 0.40])
    energy = np.array([0.01, 0.05, 0.02, 0.04, 0.03])  # all below floor 0.2
    val = spatial_concentration_over_top(ginis, energy, floor=0.2, top_k=3)
    # top-3 energies are at idx 1 (0.05), 3 (0.04), 4 (0.03) -> ginis 0.70,0.60,0.40
    assert val == pytest.approx(np.median([0.70, 0.60, 0.40]))
    assert val != 0.0


def test_spatial_concentration_empty_is_zero() -> None:
    assert spatial_concentration_over_top(np.array([]), np.array([]), floor=0.2) == 0.0


def test_spatial_concentration_top_k_capped_to_size() -> None:
    # top_k larger than the array still works (clamped to size).
    ginis = np.array([0.3, 0.5])
    energy = np.array([0.01, 0.02])
    val = spatial_concentration_over_top(ginis, energy, floor=0.2, top_k=10)
    assert val == pytest.approx(np.median([0.3, 0.5]))


# --- detect_events -----------------------------------------------------------

def test_detect_events_rise_peak_fall_is_eased() -> None:
    # A sustained, single-humped ease over >= EASED_MINLEN samples, peak >= 0.5.
    energy = np.array([0.0, 0.6, 1.2, 2.0, 1.4, 0.7, 0.0])
    events = detect_events(energy, floor=0.2)
    assert len(events) == 1
    ev = events[0]
    assert ev.kind == "eased"
    assert ev.start_idx == 1
    assert ev.length == 5
    assert ev.peak == pytest.approx(2.0)


def test_detect_events_one_frame_tall_spike_is_cut() -> None:
    # A short (<= SPIKE_MAXLEN), tall (>= SPIKE_PEAK) burst is a hard scene cut.
    energy = np.array([0.0, 0.0, 5.0, 0.0, 0.0])
    events = detect_events(energy, floor=0.2)
    assert len(events) == 1
    assert events[0].kind == "cut"
    assert events[0].length == 1
    assert events[0].peak == pytest.approx(5.0)


def test_detect_events_long_flat_low_is_drift() -> None:
    # A long active run (> EASED_MAXLEN) whose peak stays under DRIFT_MAX_PEAK is
    # slow background drift, not a designed move.
    energy = np.full(35, 0.5)  # length 35 > 30, peak 0.5 < 1.0
    events = detect_events(energy, floor=0.2)
    assert len(events) == 1
    assert events[0].kind == "drift"
    assert events[0].length == 35


def test_detect_events_empty_when_nothing_clears_floor() -> None:
    energy = np.array([0.1, 0.05, 0.0, 0.19])
    assert detect_events(energy, floor=0.2) == []


def test_detect_events_floor_is_a_parameter() -> None:
    # Same series, two floors: a higher floor suppresses a low run entirely.
    energy = np.array([0.0, 0.3, 0.4, 0.3, 0.0])
    assert len(detect_events(energy, floor=0.2)) == 1
    assert detect_events(energy, floor=0.5) == []


# --- gate truth table --------------------------------------------------------

def test_gate_eased_axis_accepts_on_share() -> None:
    # eased_energy_share at the >= threshold -> "eased", regardless of other axes.
    m = make_metrics(eased_energy_share=EASED_SHARE_MIN)
    assert gate(m) == "eased"


def test_gate_eased_axis_just_below_threshold_rejects() -> None:
    m = make_metrics(eased_energy_share=EASED_SHARE_MIN - 0.01)
    assert gate(m) is None


def test_gate_continuous_axis_accepts_when_flat_and_localized() -> None:
    m = make_metrics(
        eased_energy_share=0.0,
        sparsity=SPARSITY_MIN,
        spatial_concentration=CONCENTRATION_MIN,
        mov_texture=MOV_TEXTURE_MAX,  # exactly at the inclusive max
    )
    assert gate(m) == "continuous"


def test_gate_continuous_rejects_when_not_sparse() -> None:
    m = make_metrics(
        sparsity=SPARSITY_MIN - 0.01,
        spatial_concentration=0.9,
        mov_texture=5.0,
    )
    assert gate(m) is None


def test_gate_continuous_rejects_when_not_concentrated() -> None:
    m = make_metrics(
        sparsity=0.9,
        spatial_concentration=CONCENTRATION_MIN - 0.01,
        mov_texture=5.0,
    )
    assert gate(m) is None


def test_gate_nan_texture_cannot_pass_continuous_axis() -> None:
    # nan mov_texture (no frame had enough moving pixels) fails the <= comparison.
    m = make_metrics(sparsity=0.9, spatial_concentration=0.9, mov_texture=float("nan"))
    assert gate(m) is None


def test_gate_bar_chart_vs_talking_head_twin() -> None:
    # The headline case: identical motion stats (sparse, concentrated, no eased
    # energy) — ONLY mov_texture differs. The flat bar chart (11) is accepted as
    # continuous motion graphics; the textured talking head (25) is rejected.
    bar_chart = make_metrics(
        mov_texture=11.0, eased_energy_share=0.0, sparsity=0.75, spatial_concentration=0.72
    )
    talking_head = make_metrics(
        mov_texture=25.0, eased_energy_share=0.0, sparsity=0.75, spatial_concentration=0.72
    )
    assert gate(bar_chart) == "continuous"
    assert gate(talking_head) is None


# --- segment -----------------------------------------------------------------

# A single eased hump (rise-peak-fall) at ~10 fps. Its endpoints sit above the
# slice's adaptive floor (median 1.4 -> floor 0.7), so the whole run is active and
# eased_energy_share -> 1.0; the gate accepts it as "eased". Reused for multi-bump series.
_BUMP = [0.8, 1.4, 2.2, 1.6, 0.9]


def _bump_at(t0: float, dt: float = 0.1) -> tuple[list[float], list[float]]:
    times = [round(t0 + i * dt, 3) for i in range(len(_BUMP))]
    return times, list(_BUMP)


def test_segment_two_bumps_split_by_hard_cut_yield_two_windows() -> None:
    # Two eased bumps with a tall 1-frame spike (a hard scene cut) between them. The
    # cut is its own short active run flanked by still frames; detect_events labels it
    # "cut", the gate rejects that bare-cut window, and the two bumps stay distinct
    # beats — the cut never fuses them. merge_gap_s=0 keeps them separate.
    t1, e1 = _bump_at(0.0)
    still1 = [round(t1[-1] + 0.1, 3)]
    spike_t = [round(still1[-1] + 0.1, 3)]
    spike_e = [6.0]  # SPIKE: isolated len-1 run, peak 6 >= SPIKE_PEAK -> "cut"
    still2 = [round(spike_t[-1] + 0.1, 3)]
    t2, e2 = _bump_at(still2[-1] + 0.1)
    times = t1 + still1 + spike_t + still2 + t2
    energies = e1 + [0.0] + spike_e + [0.0] + e2
    fps = fps_at(times, energies)
    beats = segment(
        fps,
        min_beat_s=0.2,
        merge_gap_s=0.0,  # do not merge across the cut gap
        pad_s=0.0,
        max_beats=12,
        floor_fn=adaptive_floor,
        video_duration_s=times[-1] + 1.0,
    )
    assert len(beats) == 2
    assert [b.gate_kind for b in beats] == ["eased", "eased"]
    # Time-ordered output; the bare-cut window between them was gate-rejected.
    assert beats[0].start_s < beats[1].start_s


def test_segment_sub_merge_gap_bumps_are_merged() -> None:
    # Two eased bumps separated by a short still gap (no hard cut). With a generous
    # merge_gap they fuse into ONE beat.
    t1, e1 = _bump_at(0.0)
    gap_t = [round(t1[-1] + 0.1, 3), round(t1[-1] + 0.2, 3)]  # two still frames
    gap_e = [0.0, 0.0]
    t2, e2 = _bump_at(gap_t[-1] + 0.1)
    times = t1 + gap_t + t2
    energies = e1 + gap_e + e2
    fps = fps_at(times, energies)
    beats = segment(
        fps,
        min_beat_s=0.2,
        merge_gap_s=0.5,  # gap (~0.3s) <= merge_gap -> fuse
        pad_s=0.0,
        max_beats=12,
        floor_fn=adaptive_floor,
        video_duration_s=times[-1] + 1.0,
    )
    assert len(beats) == 1
    assert beats[0].start_s == pytest.approx(t1[0])
    assert beats[0].end_s == pytest.approx(t2[-1])


def test_segment_sub_min_beat_blip_is_dropped() -> None:
    # One real eased bump plus a tiny isolated 2-frame blip whose span is below
    # min_beat_s. The blip is dropped; only the real beat survives.
    t1, e1 = _bump_at(0.0)
    blip_t = [round(t1[-1] + 1.0, 3), round(t1[-1] + 1.1, 3)]  # span 0.1s
    blip_e = [0.6, 0.7]
    times = t1 + blip_t
    energies = e1 + blip_e
    fps = fps_at(times, energies)
    beats = segment(
        fps,
        min_beat_s=0.25,  # blip span 0.1 < 0.25 -> dropped
        merge_gap_s=0.0,
        pad_s=0.0,
        max_beats=12,
        floor_fn=adaptive_floor,
        video_duration_s=times[-1] + 1.0,
    )
    assert len(beats) == 1
    assert beats[0].start_s == pytest.approx(t1[0])


def test_segment_caps_to_top_n_and_resorts_by_time() -> None:
    # Five eased bumps separated by still frames (distinct active runs), with
    # increasing energy. Cap to top-3 by score, then re-sort by start time. The
    # strongest three (the later, higher-energy bumps) win and come back time-ordered.
    scale = [1.0, 1.2, 1.4, 1.6, 1.8]  # later bumps carry more energy -> higher score
    times: list[float] = []
    energies: list[float] = []
    t = 0.0
    for sc in scale:
        for v in _BUMP:
            times.append(round(t, 3))
            energies.append(v * sc)
            t = round(t + 0.1, 3)
        for _ in range(2):  # two still frames separate consecutive bumps
            times.append(round(t, 3))
            energies.append(0.0)
            t = round(t + 0.1, 3)
    fps = fps_at(times, energies)
    beats = segment(
        fps,
        min_beat_s=0.2,
        merge_gap_s=0.0,
        pad_s=0.0,
        max_beats=3,
        floor_fn=adaptive_floor,
        video_duration_s=times[-1] + 1.0,
    )
    assert len(beats) == 3
    starts = [b.start_s for b in beats]
    assert starts == sorted(starts)  # re-sorted by time after the top-N cap
    # Scores strictly increase with bump energy, so the kept beats are the last three;
    # the earliest two (weakest) bumps are dropped, so every kept start is >= 1.4s.
    assert all(s >= 1.4 - 1e-6 for s in starts)


def test_segment_no_motion_graphics_yields_empty_list() -> None:
    # A textured, full-frame, slow-drift series (a talking head / slow pan): a long
    # flat active run (> EASED_MAXLEN frames, peak < DRIFT_MAX_PEAK) classifies as
    # "drift" not "eased", so eased_energy_share is 0; and the frames are neither
    # sparse nor concentrated, so the continuous axis also rejects. -> no beats.
    n = 40  # > EASED_MAXLEN (30) -> the active run is "drift", never "eased"
    times = [round(i * 0.1, 3) for i in range(n)]
    energies = [0.8] * n  # flat, peak 0.8 < 1.0 -> drift; eased_energy_share 0
    fps = [
        make_fp(
            t,
            e,
            sparsity=0.1,  # full-frame (not sparse)
            spatial_concentration=0.1,  # not concentrated
            mov_texture=25.0,  # textured -> fails appearance axis too
        )
        for t, e in zip(times, energies)
    ]
    beats = segment(
        fps,
        min_beat_s=0.2,
        merge_gap_s=0.0,
        pad_s=0.0,
        max_beats=12,
        floor_fn=adaptive_floor,
        video_duration_s=times[-1] + 1.0,
    )
    assert beats == []


def test_segment_empty_input_yields_empty_list() -> None:
    assert (
        segment(
            [],
            min_beat_s=0.2,
            merge_gap_s=0.0,
            pad_s=0.0,
            max_beats=12,
            floor_fn=adaptive_floor,
            video_duration_s=10.0,
        )
        == []
    )


def test_segment_padding_is_clamped_to_video_bounds() -> None:
    # One bump near t=0; pad would push start below 0 and is clamped to 0.0.
    t1, e1 = _bump_at(0.0)
    fps = fps_at(t1, e1)
    beats = segment(
        fps,
        min_beat_s=0.2,
        merge_gap_s=0.0,
        pad_s=5.0,  # huge pad
        max_beats=12,
        floor_fn=adaptive_floor,
        video_duration_s=t1[-1] + 0.05,  # tight upper bound
    )
    assert len(beats) == 1
    assert beats[0].start_s == 0.0
    assert beats[0].end_s == pytest.approx(t1[-1] + 0.05)


# --- aggregate_window_metrics ------------------------------------------------

def test_aggregate_window_metrics_empty_raises() -> None:
    with pytest.raises(ValueError):
        aggregate_window_metrics([])


def test_aggregate_window_metrics_eased_share_and_nan_appearance() -> None:
    # A clean eased hump with no scored appearance frames (all-nan texture) ->
    # eased_energy_share == 1.0, eased_events == 1, mov_texture stays nan.
    t1, e1 = _bump_at(0.0)
    fps = fps_at(t1, e1, sparsity=0.7, concentration=0.7)  # texture defaults to nan
    m = aggregate_window_metrics(fps)
    assert m.n_frames == len(fps)
    assert m.eased_events == 1
    assert m.eased_energy_share == pytest.approx(1.0)
    assert math.isnan(m.mov_texture)
    assert m.motion_energy == pytest.approx(float(np.median(e1)))


# --- describe ----------------------------------------------------------------

@pytest.mark.parametrize(
    "energy_val,expected",
    [
        (0.0, "calm"),
        (0.49, "calm"),
        (0.5, "measured"),  # inclusive lower edge of the next bucket
        (1.49, "measured"),
        (1.5, "punchy"),
        (3.49, "punchy"),
        (3.5, "frenetic"),
        (10.0, "frenetic"),
    ],
)
def test_describe_energy_threshold_table(energy_val: float, expected: str) -> None:
    assert describe(make_metrics(motion_energy=energy_val)).energy == expected


def test_describe_cadence_punctuated_at_threshold() -> None:
    assert describe(make_metrics(eased_energy_share=EASED_SHARE_MIN)).cadence == "punctuated"


def test_describe_cadence_continuous_below_threshold() -> None:
    d = describe(make_metrics(eased_energy_share=EASED_SHARE_MIN - 0.01))
    assert d.cadence == "continuous"


def test_describe_spatial_localized_when_sparse_and_concentrated() -> None:
    d = describe(
        make_metrics(
            sparsity=SPARSITY_MIN,
            spatial_concentration=CONCENTRATION_MIN,
        )
    )
    assert d.spatial == "localized"


def test_describe_spatial_full_frame_when_not_concentrated() -> None:
    d = describe(
        make_metrics(
            sparsity=0.9,
            spatial_concentration=CONCENTRATION_MIN - 0.01,
        )
    )
    assert d.spatial == "full-frame"
