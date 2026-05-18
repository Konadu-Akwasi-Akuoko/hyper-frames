import type { Cut, TranscriptWordEntry } from "../types";

/**
 * Binary search for the active word at `time`. Returns the index of the
 * largest word whose [start, end) interval contains `time`, or the most-recent
 * word that has ended if `time` falls into a gap. Returns -1 before the first
 * word starts.
 */
export function findWordIndex(
  words: TranscriptWordEntry[],
  time: number,
): number {
  if (words.length === 0) return -1;
  if (time < words[0].start) return -1;

  let lo = 0;
  let hi = words.length - 1;
  let best = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >>> 1;
    const w = words[mid];
    if (w.start <= time) {
      best = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  if (best === -1) return -1;
  const candidate = words[best];
  // Prefer the active word; fall back to the last-ended word.
  if (time <= candidate.end) return best;
  return best;
}

export function isInsideAnyCut(time: number, cuts: Cut[]): boolean {
  for (const c of cuts) {
    if (time >= c.start && time < c.end) return true;
  }
  return false;
}
