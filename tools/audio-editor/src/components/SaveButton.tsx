import { useEffect, useState } from "react";
import { relativeSeconds } from "../utils/format";

export type SaveState =
  | { kind: "pristine" }
  | { kind: "saved"; at: Date }
  | { kind: "saving" }
  | { kind: "dirty" }
  | { kind: "error"; message: string };

type Props = {
  state: SaveState;
  onSave: () => void;
};

export default function SaveButton({ state, onSave }: Props) {
  const canSave = state.kind === "dirty" || state.kind === "error";
  return (
    <div className="flex items-center gap-3">
      <SaveStatePill state={state} />
      <button
        type="button"
        onClick={onSave}
        disabled={!canSave}
        className={`h-9 px-4 rounded-md text-[12px] font-medium tracking-wide transition-all ${
          canSave
            ? "bg-[color:var(--color-accent)] text-[color:var(--color-bg)] hover:brightness-110 shadow-[0_4px_14px_-4px_rgba(110,168,255,0.55)] active:scale-[0.98]"
            : "bg-[color:var(--color-panel-2)] text-[color:var(--color-muted-2)] border border-[color:var(--color-border)] cursor-not-allowed"
        }`}
      >
        Save cuts
      </button>
    </div>
  );
}

function SaveStatePill({ state }: { state: SaveState }) {
  const [, force] = useState(0);
  useEffect(() => {
    if (state.kind !== "saved") return;
    const t = window.setInterval(() => force((n) => n + 1), 1000);
    return () => window.clearInterval(t);
  }, [state.kind]);

  let dot = "bg-[color:var(--color-muted-2)]";
  let label = "";
  let tone = "text-[color:var(--color-muted)]";

  switch (state.kind) {
    case "pristine":
      label = "no changes";
      break;
    case "saved":
      dot = "bg-[color:var(--color-keep)]";
      tone = "text-[color:var(--color-keep)]";
      label = `saved · ${relativeSeconds(state.at)}`;
      break;
    case "saving":
      dot = "bg-[color:var(--color-accent)] animate-pulse-soft";
      tone = "text-[color:var(--color-accent)]";
      label = "saving…";
      break;
    case "dirty":
      dot = "bg-[color:var(--color-filler)] animate-pulse-soft";
      tone = "text-[color:var(--color-filler)]";
      label = "unsaved changes";
      break;
    case "error":
      dot = "bg-[color:var(--color-cut)]";
      tone = "text-[color:var(--color-cut)]";
      label = `error · ${state.message}`;
      break;
  }

  return (
    <div className={`hidden md:flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.12em] ${tone}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} aria-hidden />
      <span className="truncate max-w-[220px]">{label}</span>
    </div>
  );
}
