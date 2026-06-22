import type { DragEvent } from "react";
import type { BoardCard } from "../types";
import DeskMeter from "./DeskMeter";
import { mdDate } from "../format";
import { SCANNED_LADDER, ONAIR_STAGES } from "../constants";

export default function LaneCard({
  card,
  onOpen,
  onDragStart,
  onDragEnd,
}: {
  card: BoardCard;
  onOpen: () => void;
  onDragStart: () => void;
  onDragEnd: () => void;
}) {
  const onair = ONAIR_STAGES.includes(card.stage);

  const handleDragStart = (e: DragEvent<HTMLDivElement>) => {
    e.dataTransfer.setData("text/plain", card.name);
    e.dataTransfer.effectAllowed = "move";
    onDragStart();
  };

  return (
    <div
      className={"card" + (onair ? " live" : "")}
      draggable
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      onClick={onOpen}
    >
      <div className="c-title">
        {card.title}
        {card.hasDrift ? (
          <span className="drift" title={`scan suggests: ${card.suggestedStage}`}>
            ⚠ drift
          </span>
        ) : null}
      </div>
      {card.kind && card.kind !== "unset" ? (
        <span className="c-kind">
          {card.kind}
          {card.kindSource === "ai" ? <span className="ai">·ai</span> : null}
        </span>
      ) : null}
      <div className="c-slug num">
        {card.onDisk ? card.name : card.fromIdea ? "— promoted from the wire" : card.name}
      </div>
      <DeskMeter progress={card.progress} />
      <div className="c-foot">
        {onair ? (
          <span className="onair-tag">
            <span className="dot" /> ON-AIR
          </span>
        ) : (
          <div className="arts">
            {SCANNED_LADDER.map((s) => {
              const st = card.artifacts[s];
              return (
                <i
                  key={s}
                  className={st === "present" ? "on" : st === "partial" ? "partial" : ""}
                  title={`${s}: ${st ?? "missing"}`}
                />
              );
            })}
          </div>
        )}
        <span className="c-date num">{mdDate(card.date)}</span>
      </div>
    </div>
  );
}
