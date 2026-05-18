type Props = {
  pendingCutStart: number;
  currentTime: number;
  pxPerSec: number;
  scrollLeft: number;
  containerWidth: number;
};

// Sibling overlay rendered alongside the wavesurfer container while a pending
// cut is being marked. The hatched fill itself lives on the wavesurfer region
// (so it inherits zoom/scroll alignment for free); this overlay carries the
// anchor flag (fixed at pendingCutStart) and the floating duration badge.
//
// pointer-events:none on the root + every child — clicks must pass through to
// the waveform for scrub/seek to keep working while a cut is pending.
export default function PendingOverlay({
  pendingCutStart,
  currentTime,
  pxPerSec,
  scrollLeft,
  containerWidth,
}: Props) {
  const anchorPx = pendingCutStart * pxPerSec - scrollLeft;
  const playheadPx = currentTime * pxPerSec - scrollLeft;
  const leftPx = Math.min(anchorPx, playheadPx);
  const widthPx = Math.abs(playheadPx - anchorPx);
  const midPx = leftPx + widthPx / 2;

  const deltaSec = currentTime - pendingCutStart;
  const sign = deltaSec >= 0 ? "+" : "−";
  const badgeLabel = `${sign}${Math.abs(deltaSec).toFixed(2)}s`;

  // Cull when offscreen. Padding so the flag's pin head doesn't pop in/out.
  const FLAG_VISIBLE = anchorPx > -12 && anchorPx < containerWidth + 12;
  const BADGE_VISIBLE =
    midPx > -40 && midPx < containerWidth + 40 && widthPx > 1;

  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 overflow-hidden z-10"
    >
      {FLAG_VISIBLE && (
        <div
          className="pending-overlay__anchor"
          style={{ transform: `translateX(${anchorPx}px)` }}
        >
          <svg
            width="11"
            height="13"
            viewBox="0 0 11 13"
            className="pending-overlay__flag"
            fill="none"
          >
            <path
              d="M1 1h9l-2.5 3L10 7H1z"
              fill="var(--color-cut)"
              stroke="var(--color-cut)"
              strokeWidth="0.8"
              strokeLinejoin="round"
            />
            <line
              x1="1"
              y1="1"
              x2="1"
              y2="13"
              stroke="var(--color-cut)"
              strokeWidth="1.4"
              strokeLinecap="round"
            />
          </svg>
          <span className="pending-overlay__anchor-line" />
        </div>
      )}
      {BADGE_VISIBLE && (
        <div
          className="pending-overlay__badge"
          style={{ transform: `translateX(${midPx}px) translateX(-50%)` }}
        >
          {badgeLabel}
        </div>
      )}
    </div>
  );
}
