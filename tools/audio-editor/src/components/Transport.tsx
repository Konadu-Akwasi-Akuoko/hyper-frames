import { formatTime } from "../utils/format";

type Props = {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  zoom: number;
  pendingCutStart: number | null;
  skipCuts: boolean;
  onToggle: () => void;
  onZoomChange: (zoom: number) => void;
  onAddCut: () => void;
  onCancelPending: () => void;
  onSkipCutsChange: (next: boolean) => void;
  regionCount: number;
  canAct: boolean;
};

export default function Transport({
  isPlaying,
  currentTime,
  duration,
  zoom,
  pendingCutStart,
  skipCuts,
  onToggle,
  onZoomChange,
  onAddCut,
  onCancelPending,
  onSkipCutsChange,
  regionCount,
  canAct,
}: Props) {
  const isPending = pendingCutStart !== null;
  return (
    <div className="flex items-center gap-3 flex-wrap p-3 rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)]">
      <button
        type="button"
        onClick={onToggle}
        disabled={!canAct}
        className="w-10 h-10 flex items-center justify-center rounded-full bg-[color:var(--color-accent)] text-[color:var(--color-bg)] hover:brightness-110 active:scale-95 transition-all disabled:opacity-30 disabled:hover:brightness-100 shadow-[0_4px_14px_-4px_rgba(110,168,255,0.55)]"
        aria-label={isPlaying ? "Pause" : "Play"}
      >
        {isPlaying ? (
          <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
            <rect x="0" y="0" width="4" height="14" rx="1" />
            <rect x="8" y="0" width="4" height="14" rx="1" />
          </svg>
        ) : (
          <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
            <path d="M1 0v14l11-7z" />
          </svg>
        )}
      </button>

      <div className="flex items-baseline gap-1.5 font-mono tabular-nums">
        <span className="text-[15px] text-[color:var(--color-text)]">{formatTime(currentTime)}</span>
        <span className="text-[color:var(--color-muted-2)]">/</span>
        <span className="text-[12px] text-[color:var(--color-muted)]">{formatTime(duration)}</span>
      </div>

      <span className="w-px h-7 bg-[color:var(--color-border)] mx-1" aria-hidden />

      <button
        type="button"
        onClick={() => onSkipCutsChange(!skipCuts)}
        disabled={!canAct}
        title="Skip past cut regions during playback (\\)"
        aria-pressed={skipCuts}
        className={[
          "flex items-center gap-2 h-9 px-3 rounded-md border text-[11px] font-medium transition-colors",
          skipCuts
            ? "border-[color:var(--color-accent)]/50 bg-[color:var(--color-accent)]/10 text-[color:var(--color-accent)] hover:bg-[color:var(--color-accent)]/20"
            : "border-[color:var(--color-border)] bg-[color:var(--color-panel-2)] text-[color:var(--color-muted)] hover:text-[color:var(--color-text)]",
          "disabled:opacity-40",
        ].join(" ")}
      >
        <span
          className={[
            "inline-block w-2 h-2 rounded-full",
            skipCuts ? "bg-[color:var(--color-accent)]" : "bg-[color:var(--color-muted-2)]",
          ].join(" ")}
          aria-hidden
        />
        <span className="font-mono uppercase tracking-[0.08em]">preview cuts</span>
        <span className="font-mono text-[9px] text-[color:var(--color-muted-2)]">
          {skipCuts ? "on" : "off"}
        </span>
      </button>

      <span className="w-px h-7 bg-[color:var(--color-border)] mx-1" aria-hidden />

      <div className="flex items-center gap-2.5 px-3 h-9 bg-[color:var(--color-panel-2)] border border-[color:var(--color-border)] rounded-md">
        <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-[color:var(--color-muted)]">zoom</span>
        <input
          type="range"
          min={6}
          max={400}
          step={1}
          value={zoom}
          onChange={(e) => onZoomChange(parseFloat(e.target.value))}
          disabled={!canAct}
          className="slider w-36"
          aria-label="Waveform zoom"
        />
        <span className="font-mono text-[10px] tabular-nums text-[color:var(--color-accent)] min-w-[46px] text-right">
          {Math.round(zoom)}px/s
        </span>
      </div>

      <div className="flex-1" />

      <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.08em] text-[color:var(--color-muted)]">
        <span className="tabular-nums text-[color:var(--color-text)] text-[12px]">
          {String(regionCount).padStart(2, "0")}
        </span>
        <span>region{regionCount === 1 ? "" : "s"}</span>
      </div>

      {isPending && (
        <button
          type="button"
          onClick={onCancelPending}
          className="flex items-center gap-1.5 h-9 px-2.5 rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-panel-2)] text-[color:var(--color-muted)] text-[11px] hover:text-[color:var(--color-text)] hover:border-[color:var(--color-border-2)] transition-colors"
          title="Cancel pending cut (Esc)"
        >
          <span className="font-mono text-[10px] uppercase tracking-[0.08em]">esc</span>
          <span>cancel</span>
        </button>
      )}

      <button
        type="button"
        onClick={onAddCut}
        disabled={!canAct}
        title={isPending ? "Mark cut end at playhead (O)" : "Mark cut start at playhead (I)"}
        className={[
          "flex items-center gap-2 h-9 px-3 rounded-md border text-[12px] font-medium transition-colors disabled:opacity-40",
          isPending
            ? "border-[color:var(--color-cut)] bg-[color:var(--color-cut)]/20 text-[color:var(--color-cut)] hover:bg-[color:var(--color-cut)]/30 animate-pulse-soft"
            : "border-[color:var(--color-cut)]/40 bg-[color:var(--color-cut)]/5 text-[color:var(--color-cut)] hover:bg-[color:var(--color-cut)]/15 hover:border-[color:var(--color-cut)]/70",
        ].join(" ")}
      >
        {isPending ? (
          <>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M1 6h10M8 3l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Mark cut end
          </>
        ) : (
          <>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 1v10M1 6h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            Mark cut start
          </>
        )}
      </button>
    </div>
  );
}
