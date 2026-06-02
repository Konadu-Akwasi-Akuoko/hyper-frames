"""Deterministic duplicate-take detection from a Scribe v2 transcript.

A re-take is a phrase spoken, then spoken again near-verbatim a moment later
because the first attempt was off. On the transcript that shows up as two runs
of words whose *normalized* text is identical, close together in time. This
module finds those runs with plain string matching — no model, no audio, zero
run-to-run variance — and decides which copy to keep by comparing how tightly
each take was delivered (a flubbed take carries extra hesitation between words).

The companion `audio-cut-decider` agent does the editorial judgment that needs
language understanding (fillers, false starts, varying/escalating rhetoric).
Detecting identical repeats is pure mechanics, so it lives here instead — the
agent was unreliable at it (it would silently classify the same repeat as
"rhetorical, keep both" on some runs and "re-take, cut" on others).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_NORM = re.compile(r"[^a-z0-9]+")

# Default keep the later take; only keep the earlier take when it is tighter by
# more than this margin. Re-takes overwhelmingly favour the later take (it is the
# completed attempt; the earlier one was abandoned), so a near-tie in delivery
# slack must not flip the decision.
DEFAULT_SLACK_MARGIN = 0.15

# A matched repeat is treated as a genuine re-take only if at least ONE of these
# holds. Otherwise it is a coincidental phrase overlap (e.g. "the browser. And
# ..." vs "... the browser and ...") OR deliberate rhetorical repetition
# (anadiplosis: "...the most generated. The most generated becomes..."; anaphora:
# "X is a browser. Y is a browser.") — both must be left alone, since cutting
# would delete real content. The three signals, in order of reliability:
#   1. TRUNCATION — take A ends in a word fragment ("con...", "sourced--",
#      "re-"), the classic speech-repair interruption marker. A truncated first
#      attempt is a near-certain re-take; rhetorical repeats are never truncated.
#   2. LONG match — a coincidence/rhetorical reuse rarely spans this many
#      identical words in a row.
#   3. RESTART pause — a real redo restarts after a beat; rhetorical cadence
#      pauses are shorter (~0.5s), so the threshold sits above them.
# Tuned so every human-confirmed re-take in a full-length transcript passes and
# every coincidental/rhetorical match fails.
PAUSE_RESTART = 0.7  # seconds of silence before the 2nd take marking a real redo
LONG_MATCH = 5  # identical words in a row a coincidence is unlikely to hit


def _is_truncated(text: str) -> bool:
    """True if a word is a truncated fragment — Scribe marks these with a
    trailing hyphen or ellipsis ("con...", "sourced--", "re-")."""
    s = text.rstrip()
    return s.endswith("-") or s.endswith("...") or s.endswith("…")


def normalize(text: str) -> str:
    """Lowercase and drop everything but alphanumerics (so case and punctuation
    don't defeat a match): ``"JavaScript."`` and ``"javascript"`` both become
    ``"javascript"``."""
    return _NORM.sub("", text.lower())


@dataclass
class Token:
    idx: int
    text: str
    norm: str
    start: float
    end: float


def word_tokens(transcript: dict) -> list[Token]:
    """Flatten a Scribe v2 transcript to normalized word tokens, dropping
    ``spacing`` / ``audio_event`` rows and any word that normalizes to empty."""
    out: list[Token] = []
    for w in transcript["words"]:
        if w["type"] != "word":
            continue
        norm = normalize(w["text"])
        if not norm:
            continue
        out.append(
            Token(len(out), w["text"], norm, float(w["start"]), float(w["end"]))
        )
    return out


@dataclass
class Duplicate:
    a_lo: int  # first token index of the earlier take (inclusive)
    a_hi: int  # last token index of the earlier take (inclusive)
    b_lo: int  # first token index of the later take (inclusive)
    b_hi: int  # last token index of the later take (inclusive)
    length: int
    phrase: str
    a_slack: float
    b_slack: float

    def keep_last(self, margin: float = DEFAULT_SLACK_MARGIN) -> bool:
        """True => cut the earlier take (A), keep the later (B).

        Default to keeping the later take — the retake is the completed attempt,
        the earlier one was usually abandoned. Only flip to keeping the earlier
        take when it is *clearly* tighter (looser ``b_slack`` by more than
        ``margin``), i.e. the rare case where the retake introduced the stumble.
        """
        return self.a_slack >= self.b_slack - margin


def _slack(tokens: list[Token], lo: int, hi: int) -> float:
    """Total inter-word gap inside ``[lo, hi]``. Higher = looser, more hesitant
    delivery — the tell of the flubbed take."""
    return sum(max(0.0, tokens[i + 1].start - tokens[i].end) for i in range(lo, hi))


def find_duplicates(
    tokens: list[Token],
    window: float = 30.0,
    min_words: int = 3,
    pause_restart: float = PAUSE_RESTART,
    long_match: int = LONG_MATCH,
) -> list[Duplicate]:
    """Find non-overlapping identical word-runs (length >= ``min_words``) whose
    two occurrences start within ``window`` seconds of each other AND look like a
    genuine re-take rather than a coincidental phrase overlap (see the re-take
    test below / the ``PAUSE_RESTART`` etc. constants).

    Greedy left to right: at each position take the longest qualifying repeat,
    then jump past both takes. Complexity is bounded by the time ``window`` (the
    inner scan stops once a candidate start drifts past it), so this stays well
    clear of quadratic on real transcripts.
    """
    n = len(tokens)
    dups: list[Duplicate] = []
    i = 0
    while i < n:
        best: tuple[int, int] | None = None  # (run_length, k)
        k = i + 1
        while k < n:
            if tokens[k].start - tokens[i].start > window:
                break
            if tokens[k].norm == tokens[i].norm:
                t = 0
                while (
                    i + t < k
                    and k + t < n
                    and tokens[i + t].norm == tokens[k + t].norm
                ):
                    t += 1
                # require min length and that the two runs do not overlap
                if t >= min_words and (i + t) <= k:
                    # Re-take test (vs. coincidental or rhetorical repeat): take A
                    # is truncated (a word fragment — the speech-repair marker),
                    # OR a long verbatim match, OR a real restart pause precedes
                    # the 2nd take. See the constants above.
                    trunc_a = any(_is_truncated(tokens[j].text) for j in range(i, k))
                    pause_before = tokens[k].start - tokens[k - 1].end
                    is_retake = (
                        trunc_a or t >= long_match or pause_before >= pause_restart
                    )
                    if is_retake and (best is None or t > best[0]):
                        best = (t, k)
            k += 1
        if best is not None:
            t, k = best
            a_lo, a_hi, b_lo, b_hi = i, i + t - 1, k, k + t - 1
            phrase = " ".join(tok.text for tok in tokens[a_lo : a_hi + 1])
            dups.append(
                Duplicate(
                    a_lo,
                    a_hi,
                    b_lo,
                    b_hi,
                    t,
                    phrase,
                    _slack(tokens, a_lo, a_hi),
                    _slack(tokens, b_lo, b_hi),
                )
            )
            i = b_hi + 1  # skip past both takes
        else:
            i += 1
    return dups


def to_cut(
    dup: Duplicate, tokens: list[Token], margin: float = DEFAULT_SLACK_MARGIN
) -> dict:
    """Render a duplicate as a bracketed cut span (word edges only — boundary
    refinement onto silence is cut-snap's job downstream). The cut absorbs the
    inter-take pause so the splice lands on the kept take's onset."""
    if dup.keep_last(margin):
        start = tokens[dup.a_lo].start  # cut earlier take + the pause up to B
        end = tokens[dup.b_lo].start
        kept = "last"
    else:
        start = tokens[dup.a_hi].end  # cut the pause after A + the later take
        end = tokens[dup.b_hi].end
        kept = "first"
    delta_ms = abs(dup.a_slack - dup.b_slack) * 1000
    reason = (
        f'flag: duplicate_or_rhetorical: "{dup.phrase}" '
        f"— kept {kept} take (tighter by {delta_ms:.0f}ms)"
    )
    return {"start": round(start, 3), "end": round(end, 3), "reason": reason}
