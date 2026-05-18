type Props = {
  inEditor: boolean;
};

export default function AppHeader({ inEditor }: Props) {
  return (
    <header className="sticky top-0 z-30 backdrop-blur-md bg-[color:var(--color-bg)]/80 border-b border-[color:var(--color-border)]">
      <div className="max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-6">
        <a
          href="#/"
          className="group flex items-center gap-2.5 font-mono text-[13px] tracking-wide outline-none rounded"
        >
          <Mark />
          <span className="text-[color:var(--color-text)]">
            audio<span className="text-[color:var(--color-muted-2)]">/</span>editor
          </span>
        </a>

        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--color-muted-2)]">
          <span className="hidden sm:inline">
            {inEditor ? "session · review" : "pipeline · pick source"}
          </span>
          <span className="hidden sm:inline-block w-1 h-1 rounded-full bg-[color:var(--color-border-2)]" aria-hidden />
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[color:var(--color-keep)] shadow-[0_0_6px_rgba(74,222,128,0.7)] animate-pulse-soft" aria-hidden />
            <span>:3001</span>
          </span>
        </div>
      </div>
    </header>
  );
}

function Mark() {
  return (
    <svg width="24" height="14" viewBox="0 0 24 14" fill="none" aria-hidden className="shrink-0">
      <rect x="0" y="5" width="2" height="4" rx="1" fill="var(--color-muted-2)" />
      <rect x="3" y="3" width="2" height="8" rx="1" fill="var(--color-muted)" />
      <rect x="6" y="1" width="2" height="12" rx="1" fill="var(--color-accent)" />
      <rect x="9" y="4" width="2" height="6" rx="1" fill="var(--color-muted)" />
      <rect x="12" y="2" width="2" height="10" rx="1" fill="var(--color-accent)" />
      <rect x="15" y="5" width="2" height="4" rx="1" fill="var(--color-muted-2)" />
      <rect x="18" y="3" width="2" height="8" rx="1" fill="var(--color-muted)" />
      <rect x="21" y="6" width="2" height="2" rx="1" fill="var(--color-muted-2)" />
    </svg>
  );
}
