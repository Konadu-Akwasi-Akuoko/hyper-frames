# data/cold-search/ — historical calibration probes

One-off, hand-collected `yt-dlp ytsearch5:` probes from 2026-05-08, used
to calibrate the v2 demand axis (see `../../CALIBRATION-2026-05-08.md`).

This directory is **not** part of the daily pipeline. The active
cold-search output lives at `data/archive/YYYY-MM-DD/ytsearch.json` and
is produced by `cold_search.py`. Nothing here is read by any script;
keep it as a frozen audit trail of how the rubric thresholds were chosen.

Contents (`2026-05-08/`):
- `*.txt` — per-topic raw `yt-dlp` output captured during calibration
- `full-run.log` — combined run log

Safe to delete if disk pressure ever matters; the calibration write-up in
`CALIBRATION-2026-05-08.md` is the real artifact.
