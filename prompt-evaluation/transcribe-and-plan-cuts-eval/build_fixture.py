#!/usr/bin/env python3
"""Build the transcribe-and-plan-cuts eval fixture from the JS-king recording.

Slices the [LO, HI] window out of the full raw-timeline transcript, rebases
every timestamp to a local [0, HI-LO] clock, and writes:

  - <DUMMY>/transcript.raw.json   the frozen fixture the cut-decider reads
                                  (also what the audio-editor loads)
  - <EVAL>/transcript.clip.json   a snapshot of the same fixture (eval record)
  - <EVAL>/reference-cuts.json    the human's real cuts inside the window,
                                  rebased -- the answer key for grading

The 90s audio clip itself is produced separately with ffmpeg. Re-run this
whenever the window or source files change; it never touches raw.mp3 or the
live video folder.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC_DIR = REPO / "videos" / "javascript-the-king-programming-languages-2026-05-15"
DUMMY = REPO / "videos" / "tapc-eval"
EVAL = Path(__file__).resolve().parent

LO, HI = 150.0, 240.0
OFFSET = LO


def in_window(entry: dict) -> bool:
    s, e = entry.get("start"), entry.get("end")
    return s is not None and e is not None and s >= LO and e <= HI


def rebase(entry: dict) -> dict:
    out = dict(entry)
    out["start"] = round(entry["start"] - OFFSET, 6)
    out["end"] = round(entry["end"] - OFFSET, 6)
    return out


def build_transcript() -> dict:
    src = json.loads((SRC_DIR / "transcript.raw.json").read_text())
    words = [rebase(w) for w in src["words"] if in_window(w)]
    text = "".join(
        w["text"] for w in words if w["type"] in ("word", "spacing")
    ).strip()
    return {
        "audio_duration_secs": round(HI - LO, 6),
        "language_code": src.get("language_code", "en"),
        "language_probability": src.get("language_probability", 1.0),
        "text": text,
        "words": words,
    }


def build_reference() -> dict:
    src = json.loads((SRC_DIR / "cuts.json").read_text())
    cuts = []
    n = 0
    for c in src["cuts"]:
        if c["start"] >= LO and c["end"] <= HI:
            n += 1
            cuts.append(
                {
                    "id": f"ref_{n:04d}",
                    "start": round(c["start"] - OFFSET, 6),
                    "end": round(c["end"] - OFFSET, 6),
                    "reason": c.get("reason", ""),
                }
            )
    return {"version": 1, "cuts": cuts}


def main() -> None:
    transcript = build_transcript()
    (DUMMY / "transcript.raw.json").write_text(json.dumps(transcript, indent=2))
    (EVAL / "transcript.clip.json").write_text(json.dumps(transcript, indent=2))

    reference = build_reference()
    (EVAL / "reference-cuts.json").write_text(json.dumps(reference, indent=2))

    words = sum(1 for w in transcript["words"] if w["type"] == "word")
    print(f"transcript.raw.json  -> {DUMMY}")
    print(f"  {transcript['audio_duration_secs']}s  {words} words  "
          f"{len(transcript['words'])} entries")
    print(f"reference-cuts.json  -> {EVAL}")
    print(f"  {len(reference['cuts'])} reference cuts (answer key)")
    for c in reference["cuts"]:
        print(f"    {c['id']}  {c['start']:.2f}-{c['end']:.2f}  {c['reason']}")


if __name__ == "__main__":
    main()
