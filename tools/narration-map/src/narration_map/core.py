"""Narration-map core logic.

Reads a HyperFrames word-level transcript (ElevenLabs Scribe shape) and derives:
  - anchor-word lookups (first start time of each phrase, plus all later occurrences)
  - pause windows (gaps between consecutive words above a threshold)
  - scene boundaries (pauses that follow sentence-ending punctuation)
  - emphatic words (top-N words ranked by spoken duration)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Sequence
import json

PUNCT_STRIP = ',.!?":;\'()[]{}'
SENTENCE_END = '.!?'
DEFAULT_PAUSE_THRESHOLD_SECS = 0.4
DEFAULT_SCENE_PAUSE_THRESHOLD_SECS = 0.6
DEFAULT_EMPHATIC_TOP_N = 15


@dataclass(frozen=True)
class Word:
    """A single spoken word with its position in the filtered word stream."""

    index: int
    text: str
    start: float
    end: float

    @property
    def duration_secs(self) -> float:
        return self.end - self.start

    @property
    def normalized(self) -> str:
        return self.text.lower().strip(PUNCT_STRIP).strip()


@dataclass(frozen=True)
class AnchorMatch:
    word_index: int
    start: float
    end: float
    matched_text: str


@dataclass(frozen=True)
class AnchorResult:
    phrase: str
    matches: list[AnchorMatch]


@dataclass(frozen=True)
class PauseWindow:
    after_word_index: int
    after_word_text: str
    gap_secs: float
    start_secs: float
    end_secs: float


@dataclass(frozen=True)
class EmphaticWord:
    word_index: int
    text: str
    start: float
    end: float
    duration_secs: float


@dataclass
class NarrationMap:
    source: str
    audio_duration_secs: float | None
    language_code: str | None
    word_count: int
    config: dict[str, Any]
    anchors: list[AnchorResult] = field(default_factory=list)
    pauses: list[PauseWindow] = field(default_factory=list)
    scene_boundaries: list[PauseWindow] = field(default_factory=list)
    emphatic_words: list[EmphaticWord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "audio_duration_secs": self.audio_duration_secs,
            "language_code": self.language_code,
            "word_count": self.word_count,
            "config": self.config,
            "anchors": [
                {
                    "phrase": a.phrase,
                    "matches": [asdict(m) for m in a.matches],
                }
                for a in self.anchors
            ],
            "pauses": [asdict(p) for p in self.pauses],
            "scene_boundaries": [asdict(p) for p in self.scene_boundaries],
            "emphatic_words": [asdict(w) for w in self.emphatic_words],
        }


def load_transcript(path: Path) -> dict[str, Any]:
    """Load a transcript JSON file. Raises on missing file or invalid JSON."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def word_entries(transcript: dict[str, Any]) -> list[Word]:
    """Filter `words[]` to spoken words and assign positional indices."""
    raw = transcript.get("words", [])
    out: list[Word] = []
    idx = 0
    for entry in raw:
        if entry.get("type") != "word":
            continue
        out.append(
            Word(
                index=idx,
                text=str(entry["text"]),
                start=float(entry["start"]),
                end=float(entry["end"]),
            )
        )
        idx += 1
    return out


def _normalize_phrase(phrase: str) -> list[str]:
    return [tok.lower().strip(PUNCT_STRIP).strip() for tok in phrase.split()]


def find_anchors(words: Sequence[Word], phrases: Iterable[str]) -> list[AnchorResult]:
    """For each phrase, return every contiguous match in `words` (case- and punctuation-insensitive)."""
    results: list[AnchorResult] = []
    for phrase in phrases:
        toks = _normalize_phrase(phrase)
        if not toks:
            continue
        matches: list[AnchorMatch] = []
        i = 0
        while i <= len(words) - len(toks):
            window = words[i : i + len(toks)]
            if all(w.normalized == t for w, t in zip(window, toks)):
                matches.append(
                    AnchorMatch(
                        word_index=window[0].index,
                        start=window[0].start,
                        end=window[-1].end,
                        matched_text=" ".join(w.text for w in window),
                    )
                )
                i += len(toks)
            else:
                i += 1
        results.append(AnchorResult(phrase=phrase, matches=matches))
    return results


def find_pauses(words: Sequence[Word], threshold_secs: float) -> list[PauseWindow]:
    """Return every gap between consecutive words larger than `threshold_secs`."""
    pauses: list[PauseWindow] = []
    for prev, nxt in zip(words, words[1:]):
        gap = nxt.start - prev.end
        if gap > threshold_secs:
            pauses.append(
                PauseWindow(
                    after_word_index=prev.index,
                    after_word_text=prev.text,
                    gap_secs=round(gap, 4),
                    start_secs=prev.end,
                    end_secs=nxt.start,
                )
            )
    return pauses


def find_scene_boundaries(
    words: Sequence[Word], threshold_secs: float
) -> list[PauseWindow]:
    """Pauses larger than `threshold_secs` that follow a word ending in `.!?`.

    These approximate places the human voice intentionally finished a thought —
    the strongest candidates for scene cuts.
    """
    boundaries: list[PauseWindow] = []
    for prev, nxt in zip(words, words[1:]):
        gap = nxt.start - prev.end
        if gap <= threshold_secs:
            continue
        stripped_tail = prev.text.rstrip('"\')]}')
        if stripped_tail and stripped_tail[-1] in SENTENCE_END:
            boundaries.append(
                PauseWindow(
                    after_word_index=prev.index,
                    after_word_text=prev.text,
                    gap_secs=round(gap, 4),
                    start_secs=prev.end,
                    end_secs=nxt.start,
                )
            )
    return boundaries


def find_emphatic_words(words: Sequence[Word], top_n: int) -> list[EmphaticWord]:
    """Return the top-N words by spoken duration, longest first."""
    ranked = sorted(words, key=lambda w: w.duration_secs, reverse=True)[:top_n]
    return [
        EmphaticWord(
            word_index=w.index,
            text=w.text,
            start=w.start,
            end=w.end,
            duration_secs=round(w.duration_secs, 4),
        )
        for w in ranked
    ]


def build_narration_map(
    transcript_path: Path,
    *,
    phrases: Sequence[str] = (),
    pause_threshold_secs: float = DEFAULT_PAUSE_THRESHOLD_SECS,
    scene_pause_threshold_secs: float = DEFAULT_SCENE_PAUSE_THRESHOLD_SECS,
    emphatic_top_n: int = DEFAULT_EMPHATIC_TOP_N,
) -> NarrationMap:
    transcript = load_transcript(transcript_path)
    words = word_entries(transcript)
    config: dict[str, Any] = {
        "pause_threshold_secs": pause_threshold_secs,
        "scene_pause_threshold_secs": scene_pause_threshold_secs,
        "emphatic_top_n": emphatic_top_n,
        "anchor_phrase_count": len(phrases),
    }
    return NarrationMap(
        source=str(transcript_path),
        audio_duration_secs=transcript.get("audio_duration_secs"),
        language_code=transcript.get("language_code"),
        word_count=len(words),
        config=config,
        anchors=find_anchors(words, phrases),
        pauses=find_pauses(words, pause_threshold_secs),
        scene_boundaries=find_scene_boundaries(words, scene_pause_threshold_secs),
        emphatic_words=find_emphatic_words(words, emphatic_top_n),
    )
