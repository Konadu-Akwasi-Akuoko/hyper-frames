# iteration-1 grading — baseline (current audio-cut-decider)

Grade by ear in the editor: `http://localhost:5173/#/edit/tapc-eval`
(clip plays 0:00–1:30; cut times below are in clip-local seconds).

Verdict key: **OK** = keep as-is · **BND** = right cut, boundary off · **FP** =
false positive (shouldn't be cut) · plus list any **MISSED** cuts at the bottom.

## Proposed cuts vs. answer key

| id | agent cut | your real cut | targets | verdict | notes |
|----|-----------|---------------|---------|---------|-------|
| cut_0001 | 15.00–19.22 | 14.85–19.01 | false start "...choke under con..." | BND | both edges sit on speech; want 14.743 / 18.854 — INSIDE silence valleys, sub-token. Start: pull into [14.38,15.00] gap. End: pull into the 1.7s silence before the restart to keep its lead-in. |
| cut_0002 | 27.05–29.72 | 26.95–29.48 | false start "server collapsed too..." | | |
| cut_0003 | 39.68–42.62 | 37.76–41.11 | dup take "And he chose JavaScript" | | |
| cut_0004 | 65.18–67.08 | 64.41–66.31 | false start "and it was re..." | | |
| cut_0005 | 69.58–73.80 | 69.01–73.56 | dup take "had to b-bolt it on" | | |

## Anaphora traps (should NOT be cut — confirm agent left them alone)

- "Every request opened a new thread. Every thread ate memory." — agent cut? **no** ✓
- "Ruby had EventMachine. Python had Twisted." — agent cut? **no** ✓

## Missed cuts (anything you'd add that the agent didn't propose)

-

## Overall verdict

-

## What to change in audio-cut-decider.md for iteration-2

-
