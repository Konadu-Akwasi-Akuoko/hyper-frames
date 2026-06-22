import { useState } from "react";
import type { BoardCard, StageDef } from "../types";
import { SCANNED_LADDER } from "../constants";

export default function DetailPanel({
  card,
  stages,
  onClose,
  onSave,
  onDelete,
}: {
  card: BoardCard;
  stages: StageDef[];
  onClose: () => void;
  onSave: (body: { stage: string; notes: string }) => void;
  onDelete: () => void;
}) {
  const [stage, setStage] = useState(card.stage);
  const [notes, setNotes] = useState(card.notes ?? "");

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="panel">
        <div>
          <h2>{card.title}</h2>
          <div className="slug">{card.onDisk ? `videos/${card.name}/` : card.name}</div>
        </div>

        {card.hasDrift ? (
          <div className="drift-flag">
            Scan suggests <b>{card.suggestedStage}</b>, but this card is filed under{" "}
            <b>{card.stage}</b>.
          </div>
        ) : null}

        <div>
          <label>Stage</label>
          <select value={stage} onChange={(e) => setStage(e.target.value)}>
            {stages.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Artifacts on disk</label>
          <div className="checklist">
            {SCANNED_LADDER.map((s) => {
              const st = card.artifacts[s] ?? "missing";
              return (
                <div
                  key={s}
                  className={
                    "row " + (st === "present" ? "present" : st === "partial" ? "partial" : "")
                  }
                >
                  <span className="dot" /> {s}
                  <span style={{ marginLeft: "auto" }} className="num">
                    {st}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <label>Notes</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        <div className="panel-foot">
          <button className="btn danger" onClick={onDelete}>
            Remove card
          </button>
          <button className="btn" onClick={() => onSave({ stage, notes })}>
            Save
          </button>
        </div>
      </aside>
    </>
  );
}
