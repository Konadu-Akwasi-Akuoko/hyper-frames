import type { Idea } from "../types";
import WireMeter from "./WireMeter";
import { TypeGlyph } from "../glyphs";
import { TYPE_LABEL } from "../constants";
import { leanOf, evidenceLines } from "../format";

export type DispatchAnim = "squelched" | "committing" | undefined;

export default function Dispatch({
  idea,
  selected,
  anim,
  onSelect,
  onKeep,
  onReject,
  onPromote,
  onCycleKind,
  onAcceptKind,
}: {
  idea: Idea;
  selected: boolean;
  anim: DispatchAnim;
  onSelect: () => void;
  onKeep: () => void;
  onReject: () => void;
  onPromote: () => void;
  onCycleKind: () => void;
  onAcceptKind: () => void;
}) {
  const ev = evidenceLines(idea);
  const quote = idea.evidence?.quotes?.[0]?.text;
  const cls = ["dispatch"];
  if (selected) cls.push("sel");
  if (anim) cls.push(anim);

  return (
    <article className={cls.join(" ")} tabIndex={0} onMouseDown={onSelect}>
      <WireMeter lean={leanOf(idea)} />
      <div className="d-main">
        <div className="d-title">
          <span className="tg">
            <TypeGlyph type={idea.type} />
          </span>
          {idea.title}
        </div>
        <div className="d-rat">
          {idea.rationale}
          {quote ? (
            <>
              {" "}
              <span className="q">&ldquo;{quote}&rdquo;</span>
            </>
          ) : null}
        </div>
        <div className="d-tags">
          <span className="chip">{TYPE_LABEL[idea.type]}</span>
          {/* On an AI suggestion a click ACCEPTS it (locks the same value as human,
              clearing the ·ai mark); to change an AI pick use 1/2/3 or the action
              button. A human/unset chip cycles as before. */}
          <span
            className={"chip kind" + (idea.kind !== "unset" ? " set" : "")}
            onClick={idea.kind_source === "ai" ? onAcceptKind : onCycleKind}
            title={idea.kind_source === "ai" ? (idea.kind_why ?? undefined) : undefined}
            role="button"
            tabIndex={-1}
          >
            {idea.kind !== "unset" ? idea.kind : "set kind"}
            {idea.kind_source === "ai" ? <span className="ai">·ai</span> : null}
          </span>
        </div>
        <div className="d-actions">
          <button className="act keep" onClick={onKeep}>
            {idea.status === "keep" ? "Kept ✓" : "Keep"}
          </button>
          <button className="act reject" onClick={onReject}>
            Reject
          </button>
          <button className="act" onClick={onCycleKind}>
            long · short · series
          </button>
          <button className="act promote" onClick={onPromote}>
            ↑ Promote
          </button>
        </div>
      </div>
      <div className="d-evid">
        <div className="big num">{ev.big}</div>
        {ev.sub ? <div className="sub num">{ev.sub}</div> : null}
        <div className="src">{ev.src}</div>
      </div>
    </article>
  );
}
