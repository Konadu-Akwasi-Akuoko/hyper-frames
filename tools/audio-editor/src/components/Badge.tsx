type Props = {
  on: boolean;
  label: string;
};

export default function Badge({ on, label }: Props) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-1.5 h-[18px] rounded font-mono text-[9.5px] uppercase tracking-[0.08em] border ${
        on
          ? "bg-[color:var(--color-keep)]/10 text-[color:var(--color-keep)] border-[color:var(--color-keep)]/30"
          : "bg-[color:var(--color-panel-2)] text-[color:var(--color-muted-2)] border-[color:var(--color-border)]"
      }`}
    >
      <span
        className={`w-1 h-1 rounded-full ${on ? "bg-[color:var(--color-keep)]" : "bg-[color:var(--color-muted-2)]"}`}
        aria-hidden
      />
      {label}
    </span>
  );
}
