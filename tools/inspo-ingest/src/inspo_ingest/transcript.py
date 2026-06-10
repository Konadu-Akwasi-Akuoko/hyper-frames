"""Pure transcript math for the ``pace`` workflow: json3 parsing + scene alignment.

Turns a YouTube ``json3`` subtitle track into a word-onset time series and aligns
that series to scene windows (words-per-second, silence, boundary-pause and
sentence-alignment facts), then reduces per-scene narration into whole-video
aggregates. Module boundary (authoritative): this file is PURE and stdlib-only —
no file, network, or subprocess I/O, no ``cv2``, no ``numpy``. ``cli.py`` reads
the subtitle file off disk and hands the text here.

json3 structural facts this parser encodes (verified empirically on live
auto-caption tracks; a parser that ignores any of them miscounts):

* A word's onset is ``event.tStartMs + seg.tOffsetMs`` in milliseconds, and the
  FIRST seg of an event legitimately omits ``tOffsetMs`` (~15-20% of words) —
  it defaults to 0, never to "skip".
* Events with ``aAppend: 1`` re-emit the previous window's text for the
  scrolling display and must be skipped, as must events without ``segs`` (pure
  window-definition events) and whitespace-only segs.
* NO per-word end time exists anywhere (``dDurationMs`` is window display
  time), so a word's end is approximated by the next word's onset; the last
  word gets ``start + LAST_WORD_TAIL_S``. Pauses therefore surface only where
  tokens were removed (e.g. ``filter_non_speech``) or after the final word.
* Bracketed non-speech tokens (``[Music]``, ``[Applause]``, ``[♪...]``) are
  real segs with real onsets; ``filter_non_speech`` drops them AFTER end times
  are baked, which is exactly what turns a music stretch into a visible gap.

Scene windows are duck-typed so this module stays independent of ``scenes.py``:
``align_scenes`` accepts any objects exposing ``start_s``/``end_s`` attributes
(``SceneWindowLike``); ``aggregates`` additionally reads ``boundary_kind``
(``BoundarySceneWindowLike``). No float is rounded here — ``cli.py`` owns
quantization via ``_q`` when it writes the manifest.
"""
from __future__ import annotations

import json
import math
import re
from bisect import bisect_left
from dataclasses import dataclass
from typing import Protocol, Sequence

# Minimum fraction of words carrying trailing punctuation for a track to count
# as punctuated; below it sentence-boundary alignment is null everywhere
# (the 2026 auto `en` tracks sit around 13%, unpunctuated legacy tracks near 0%).
PUNCTUATED_MIN_FRACTION: float = 0.02

# Synthetic duration granted to the final word, which has no next onset.
LAST_WORD_TAIL_S: float = 0.5

_NON_SPEECH_RE = re.compile(r"\[[^\]]*\]\Z")
_SENTENCE_END_RE = re.compile(r"[.!?][\"'”’)\]]*\Z")
_PUNCTUATED_RE = re.compile(r"[.,!?][\"'”’)\]]*\Z")


@dataclass(frozen=True)
class Word:
    """One transcript word keyed by absolute proxy seconds.

    Attributes:
        text: The seg's stripped utf8 token (may carry trailing punctuation).
        start_s: Word onset in seconds (``tStartMs + tOffsetMs`` of its seg).
        end_s: The next word's onset, or ``start_s + LAST_WORD_TAIL_S`` for the
            final word — an approximation, since json3 carries no per-word end.
    """

    text: str
    start_s: float
    end_s: float


class SceneWindowLike(Protocol):
    """Duck type for a scene window: anything exposing ``start_s``/``end_s``.

    Satisfied by ``scenes.SceneWindow`` without importing it, keeping the
    transcript and scene-detection modules independent.
    """

    @property
    def start_s(self) -> float: ...

    @property
    def end_s(self) -> float: ...


class BoundarySceneWindowLike(SceneWindowLike, Protocol):
    """A scene window that also names its opening boundary kind.

    ``boundary_kind`` is ``"start"`` for the first scene, else ``"cut"`` or
    ``"soft"`` — the values ``scenes.build_scenes`` emits.
    """

    @property
    def boundary_kind(self) -> str: ...


@dataclass(frozen=True)
class SceneNarration:
    """Narration facts for one scene window, all derived from word onsets.

    "In the scene" means a word whose ONSET falls in ``[start_s, end_s)``;
    straddling words contribute to ``coverage`` only. Boundary fields
    (``cut_in_pause``, ``pause_before_cut_s``, ``sentence_aligned``) describe
    the scene's START boundary; for the first scene they describe time 0.

    Attributes:
        word_count: Number of words whose onset falls in the window.
        words_per_s: ``word_count`` over the window duration.
        coverage: Summed word spans clipped to the window over its duration,
            capped at 1.0.
        first_word_offset_s: Onset of the first in-scene word minus the scene
            start; ``None`` when no word starts in the scene.
        leading_silence_s: ``first_word_offset_s``, or the full duration when
            no word starts in the scene.
        trailing_silence_s: Scene end minus the last in-scene word's end,
            clipped to >= 0; the full duration when no word starts in the scene.
        cut_in_pause: Whether the speech gap spanning the scene's start
            boundary is at least ``pause_min_s``.
        pause_before_cut_s: Size of that spanning gap — previous word end (or
            0.0 at the start of audio) to next word onset (or the end of the
            last window when speech never resumes); 0.0 when a word straddles
            the boundary.
        sentence_aligned: Whether the last word ending within ``lookback_s``
            before the start boundary is sentence-ending; ``False`` when no
            word ends in that lookback; ``None`` when the track is
            unpunctuated (``punctuated_fraction < PUNCTUATED_MIN_FRACTION``).
        text: The in-scene words, space-joined in onset order.
    """

    word_count: int
    words_per_s: float
    coverage: float
    first_word_offset_s: float | None
    leading_silence_s: float
    trailing_silence_s: float
    cut_in_pause: bool
    pause_before_cut_s: float
    sentence_aligned: bool | None
    text: str


def parse_json3(text: str) -> list[Word]:
    """Parse a YouTube json3 subtitle document into onset-ordered ``Word`` objects.

    Skips ``aAppend`` events, events without ``segs`` (window definitions), and
    whitespace-only segs. Each kept seg's onset is ``tStartMs +
    seg.get("tOffsetMs", 0)`` milliseconds — the first seg of an event
    legitimately lacks ``tOffsetMs``. Words are sorted by onset (stable, so
    equal onsets keep source order); each word's end is the next word's onset
    and the final word gets ``start + LAST_WORD_TAIL_S``.

    Args:
        text: The raw json3 file contents.

    Returns:
        Onset-ordered words; empty when the track carries no speech segs.

    Raises:
        ValueError: If ``text`` is not JSON, has no top-level ``events`` list,
            or declares a ``wireMagic`` other than ``"pb3"``.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not json3: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("not json3: missing top-level 'events' list")
    magic = data.get("wireMagic")
    if magic is not None and magic != "pb3":
        raise ValueError(f"not json3: unexpected wireMagic {magic!r}")

    onsets: list[tuple[float, str]] = []
    for event in data["events"]:
        if not isinstance(event, dict) or event.get("aAppend"):
            continue
        segs = event.get("segs")
        if not isinstance(segs, list) or not segs:
            continue
        t_start_ms = event.get("tStartMs", 0)
        for seg in segs:
            if not isinstance(seg, dict):
                continue
            token = str(seg.get("utf8", "")).strip()
            if not token:
                continue
            onset_ms = t_start_ms + seg.get("tOffsetMs", 0)
            onsets.append((onset_ms / 1000.0, token))

    onsets.sort(key=lambda item: item[0])
    words: list[Word] = []
    for i, (start_s, token) in enumerate(onsets):
        if i + 1 < len(onsets):
            end_s = onsets[i + 1][0]
        else:
            end_s = start_s + LAST_WORD_TAIL_S
        words.append(Word(text=token, start_s=start_s, end_s=end_s))
    return words


def filter_non_speech(words: list[Word]) -> list[Word]:
    """Drop bracketed non-speech tokens (``[Music]``, ``[Applause]``, ``[♪...]``).

    Applied AFTER ``parse_json3`` bakes end times, so the word preceding a
    dropped token keeps the token's onset as its end — which is what exposes
    the non-speech stretch as a gap to the pause analysis.

    Args:
        words: Parsed words in onset order.

    Returns:
        The words whose text is not fully bracketed, in the same order.
    """
    return [w for w in words if not _NON_SPEECH_RE.match(w.text)]


def is_sentence_end(word: Word) -> bool:
    """Return whether a word ends a sentence.

    True when the text ends with ``.``, ``!``, or ``?``, optionally followed by
    closing quotes/brackets (``."``, ``?)``, ``!]``).

    Args:
        word: The word to test.

    Returns:
        Whether the word is sentence-ending.
    """
    return _SENTENCE_END_RE.search(word.text) is not None


def punctuated_fraction(words: list[Word]) -> float:
    """Return the fraction of words carrying trailing ``.,!?`` punctuation.

    The track-level punctuation signal: compare against
    ``PUNCTUATED_MIN_FRACTION`` to decide whether sentence-boundary alignment
    is meaningful. Returns 0.0 for an empty list.

    Args:
        words: Parsed (ideally speech-filtered) words.

    Returns:
        Fraction in ``[0.0, 1.0]``.
    """
    if not words:
        return 0.0
    punctuated = sum(1 for w in words if _PUNCTUATED_RE.search(w.text))
    return punctuated / len(words)


def align_scenes(
    scene_windows: Sequence[SceneWindowLike],
    words: list[Word],
    *,
    pause_min_s: float = 0.5,
    lookback_s: float = 1.0,
) -> list[SceneNarration | None]:
    """Align a word series to scene windows, one ``SceneNarration`` per window.

    Windows are duck-typed (``start_s``/``end_s`` attributes only) so callers
    can pass ``scenes.SceneWindow`` objects without coupling the modules. An
    empty word list yields all ``None`` (no narration data, the "no subtitles"
    degradation). Sentence alignment is ``None`` everywhere when the track is
    unpunctuated. Boundary-gap edges are deterministic: speech is assumed
    absent before the first word (gap floor 0.0) and after the last word (gap
    ceiling at the last window's end).

    Args:
        scene_windows: Time-ordered windows exposing ``start_s``/``end_s``.
        words: Parsed, speech-filtered words.
        pause_min_s: Minimum boundary-spanning gap that counts as a pause.
        lookback_s: How far before a boundary the sentence-alignment check
            looks for the last word end.

    Returns:
        One ``SceneNarration`` (or ``None``) per window, in window order.
    """
    windows = list(scene_windows)
    if not windows:
        return []
    if not words:
        return [None] * len(windows)

    ws = sorted(words, key=lambda w: w.start_s)
    starts = [w.start_s for w in ws]
    # prefix_max_end[i] = max end over ws[:i]; [0] is 0.0, the start-of-audio
    # floor the boundary gap opens from when no word precedes the boundary.
    prefix_max_end = [0.0]
    for w in ws:
        prefix_max_end.append(max(prefix_max_end[-1], w.end_s))

    total_end = max(win.end_s for win in windows)
    punctuated = punctuated_fraction(ws) >= PUNCTUATED_MIN_FRACTION

    narrations: list[SceneNarration | None] = []
    for win in windows:
        b, e = win.start_s, win.end_s
        dur = e - b
        j = bisect_left(starts, b)
        k = bisect_left(starts, e)
        in_scene = ws[j:k]

        word_count = len(in_scene)
        words_per_s = word_count / dur if dur > 0 else 0.0

        overlap = sum(
            max(0.0, min(w.end_s, e) - max(w.start_s, b)) for w in ws[:k]
        )
        coverage = min(1.0, overlap / dur) if dur > 0 else 0.0

        if in_scene:
            first_word_offset_s: float | None = in_scene[0].start_s - b
            leading_silence_s = in_scene[0].start_s - b
            trailing_silence_s = max(0.0, e - max(w.end_s for w in in_scene))
        else:
            first_word_offset_s = None
            leading_silence_s = dur
            trailing_silence_s = dur

        straddled = prefix_max_end[j] > b
        if straddled:
            pause_before_cut_s = 0.0
        else:
            prev_end = prefix_max_end[j]
            next_onset = starts[j] if j < len(ws) else total_end
            pause_before_cut_s = max(0.0, next_onset - prev_end)
        cut_in_pause = pause_before_cut_s >= pause_min_s

        if not punctuated:
            sentence_aligned: bool | None = None
        else:
            last_ending = None
            for w in ws[:j]:
                if b - lookback_s <= w.end_s <= b and (
                    last_ending is None
                    or (w.end_s, w.start_s) > (last_ending.end_s, last_ending.start_s)
                ):
                    last_ending = w
            sentence_aligned = (
                is_sentence_end(last_ending) if last_ending is not None else False
            )

        narrations.append(
            SceneNarration(
                word_count=word_count,
                words_per_s=words_per_s,
                coverage=coverage,
                first_word_offset_s=first_word_offset_s,
                leading_silence_s=leading_silence_s,
                trailing_silence_s=trailing_silence_s,
                cut_in_pause=cut_in_pause,
                pause_before_cut_s=pause_before_cut_s,
                sentence_aligned=sentence_aligned,
                text=" ".join(w.text for w in in_scene),
            )
        )
    return narrations


def aggregates(
    scene_windows: Sequence[BoundarySceneWindowLike],
    narrations: Sequence[SceneNarration | None],
    *,
    duration_s: float,
) -> dict[str, object]:
    """Reduce per-scene windows + narrations into the manifest's aggregates dict.

    ``cuts_per_minute`` counts hard cuts only (``boundary_kind == "cut"``);
    soft transitions are reported separately. The boundary percentages
    (``pct_cuts_in_pause``, ``pct_sentence_aligned``) are taken over scenes
    that have narration and a real opening boundary (``boundary_kind !=
    "start"``); each is ``None`` when no scene qualifies, and
    ``pct_sentence_aligned`` is also ``None`` for an unpunctuated track (all
    per-scene values ``None``). No float is rounded here — ``cli.py`` routes
    every value through ``_q`` when writing the manifest.

    Args:
        scene_windows: Time-ordered windows exposing ``start_s``/``end_s``/
            ``boundary_kind``.
        narrations: Output of ``align_scenes``, aligned to ``scene_windows``.
        duration_s: Proxy duration in seconds (the cuts-per-minute base).

    Returns:
        The ``inspo-pace/1`` aggregates dict: ``scene_count``,
        ``cuts_per_minute``, ``soft_transition_count``, ``scene_duration_s``
        (``median``/``p25``/``p75``/``min``/``max``), ``longest_hold_s``,
        ``words_per_s_mean``, ``pct_cuts_in_pause``, ``pct_sentence_aligned``.
    """
    windows = list(scene_windows)
    narration_list = list(narrations)
    kinds = [win.boundary_kind for win in windows]
    durations = sorted(win.end_s - win.start_s for win in windows)

    cut_count = kinds.count("cut")
    cuts_per_minute = cut_count * 60.0 / duration_s if duration_s > 0 else 0.0

    if durations:
        scene_duration_s: dict[str, float | None] = {
            "median": _quantile(durations, 0.5),
            "p25": _quantile(durations, 0.25),
            "p75": _quantile(durations, 0.75),
            "min": durations[0],
            "max": durations[-1],
        }
        longest_hold_s: float | None = durations[-1]
    else:
        scene_duration_s = {
            "median": None,
            "p25": None,
            "p75": None,
            "min": None,
            "max": None,
        }
        longest_hold_s = None

    narrated = [nar for nar in narration_list if nar is not None]
    words_per_s_mean = (
        sum(nar.words_per_s for nar in narrated) / len(narrated) if narrated else None
    )

    eligible = [
        nar
        for win, nar in zip(windows, narration_list, strict=True)
        if nar is not None and win.boundary_kind != "start"
    ]
    pct_cuts_in_pause = (
        sum(1 for nar in eligible if nar.cut_in_pause) / len(eligible)
        if eligible
        else None
    )
    aligned_known = [
        nar.sentence_aligned for nar in eligible if nar.sentence_aligned is not None
    ]
    pct_sentence_aligned = (
        sum(1 for aligned in aligned_known if aligned) / len(aligned_known)
        if aligned_known
        else None
    )

    return {
        "scene_count": len(windows),
        "cuts_per_minute": cuts_per_minute,
        "soft_transition_count": kinds.count("soft"),
        "scene_duration_s": scene_duration_s,
        "longest_hold_s": longest_hold_s,
        "words_per_s_mean": words_per_s_mean,
        "pct_cuts_in_pause": pct_cuts_in_pause,
        "pct_sentence_aligned": pct_sentence_aligned,
    }


def _quantile(sorted_values: list[float], p: float) -> float:
    h = (len(sorted_values) - 1) * p
    lo = math.floor(h)
    hi = math.ceil(h)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (h - lo)
