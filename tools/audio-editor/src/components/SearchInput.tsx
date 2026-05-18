type Props = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

export default function SearchInput({ value, onChange, placeholder = "Filter by slug…" }: Props) {
  return (
    <label className="relative flex items-center group">
      <span
        className="absolute left-3 text-[color:var(--color-muted-2)] group-focus-within:text-[color:var(--color-accent)] transition-colors pointer-events-none"
        aria-hidden
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M9.5 9.5L12 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        spellCheck={false}
        className="w-full h-10 pl-9 pr-9 bg-[color:var(--color-panel)] border border-[color:var(--color-border)] rounded-md text-sm font-mono placeholder:text-[color:var(--color-muted-2)] focus:outline-none focus:border-[color:var(--color-accent)]/60 focus:bg-[color:var(--color-panel-2)] transition-colors"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange("")}
          className="absolute right-2 w-6 h-6 flex items-center justify-center rounded text-[color:var(--color-muted-2)] hover:text-[color:var(--color-text)] hover:bg-[color:var(--color-panel-2)]"
          aria-label="Clear search"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M1 1l8 8M9 1l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      )}
    </label>
  );
}
