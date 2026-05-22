import type { Cut } from "../types";
import { formatTime } from "../utils/format";

type Props = {
  cuts: Cut[];
  onJump: (cut: Cut) => void;
  onRemove: (id: string) => void;
};

export default function RegionList({ cuts, onJump, onRemove }: Props) {
  const totalCut = cuts.reduce((sum, c) => sum + (c.end - c.start), 0);

  return (
    <div className="flex flex-col h-full min-h-[260px] lg:min-h-0 lg:max-h-[60vh] bg-[color:var(--color-panel)] border border-[color:var(--color-border)] rounded-[10px] overflow-hidden">
      <div className="px-4 py-3 border-b border-[color:var(--color-border)] flex items-center justify-between gap-3">
        <div className="flex items-baseline gap-2">
          <h3 className="font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--color-muted)]">
            cut regions
          </h3>
          <span className="font-mono text-[10px] text-[color:var(--color-muted-2)] tabular-nums">
            {String(cuts.length).padStart(2, "0")}
          </span>
        </div>
        <span className="font-mono text-[11px] text-[color:var(--color-cut)] tabular-nums">
          {totalCut > 0 ? `-${formatTime(totalCut)}` : "—"}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {cuts.length === 0 ? (
          <EmptyState />
        ) : (
          <ul className="divide-y divide-[color:var(--color-border)]">
            {cuts.map((cut, i) => (
              <RegionRow key={cut.id} cut={cut} idx={i} onJump={onJump} onRemove={onRemove} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="p-6 text-center">
      <div className="mx-auto w-10 h-10 rounded-full border border-dashed border-[color:var(--color-border-2)] flex items-center justify-center mb-3">
        <span className="font-mono text-[16px] text-[color:var(--color-muted-2)]">∅</span>
      </div>
      <p className="text-[12px] text-[color:var(--color-muted)] leading-relaxed">
        No cuts yet. Use <span className="font-mono text-[color:var(--color-cut)]">+ Add cut</span> to mark a region for removal.
      </p>
    </div>
  );
}

function RegionRow({
  cut,
  idx,
  onJump,
  onRemove,
}: {
  cut: Cut;
  idx: number;
  onJump: (cut: Cut) => void;
  onRemove: (id: string) => void;
}) {
  const duration = cut.end - cut.start;
  return (
    <li className="group relative">
      <div
        className="absolute left-0 top-0 bottom-0 w-[2px] bg-[color:var(--color-cut)]/40 group-hover:bg-[color:var(--color-cut)] transition-colors"
        aria-hidden
      />
      <button
        type="button"
        onClick={() => onJump(cut)}
        className="w-full text-left px-4 py-3 pr-10 hover:bg-[color:var(--color-panel-2)] transition-colors"
      >
        <div className="flex items-baseline justify-between gap-3">
          <div className="font-mono text-[10px] uppercase tracking-[0.08em] text-[color:var(--color-muted-2)]">
            #{String(idx + 1).padStart(2, "0")}
          </div>
          <div className="font-mono text-[11px] tabular-nums text-[color:var(--color-cut)]">
            -{formatTime(duration)}
          </div>
        </div>
        <div className="mt-1 font-mono text-[12px] tabular-nums text-[color:var(--color-text)]">
          {formatTime(cut.start)}{" "}
          <span className="text-[color:var(--color-muted-2)]">→</span>{" "}
          {formatTime(cut.end)}
        </div>
        {cut.reason && (
          <div className="mt-1 text-[11px] text-[color:var(--color-muted)] truncate">
            {cut.reason}
          </div>
        )}
      </button>
      <button
        type="button"
        onClick={() => onRemove(cut.id)}
        className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded flex items-center justify-center text-[color:var(--color-muted-2)] hover:text-[color:var(--color-cut)] hover:bg-[color:var(--color-cut)]/10 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-opacity"
        aria-label={`Remove cut ${idx + 1}`}
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>
    </li>
  );
}
