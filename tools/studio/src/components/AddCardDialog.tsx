import { useState } from "react";
import type { StageDef } from "../types";

const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

export default function AddCardDialog({
  stages,
  onClose,
  onAdd,
}: {
  stages: StageDef[];
  onClose: () => void;
  onAdd: (body: { slug: string; title?: string; date: string; stage: string }) => void;
}) {
  const today = new Date().toISOString().slice(0, 10);
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");
  const [date, setDate] = useState(today);
  const [stage, setStage] = useState("idea");
  const [err, setErr] = useState("");

  const submit = () => {
    if (!SLUG_RE.test(slug)) {
      setErr("Lowercase letters, digits and hyphens only.");
      return;
    }
    onAdd({ slug, title: title || undefined, date, stage });
  };

  return (
    <div className="dialog-scrim" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <h2>Add a card</h2>
        <div>
          <label>Slug</label>
          <input
            value={slug}
            onChange={(e) => {
              setSlug(e.target.value);
              setErr("");
            }}
            placeholder="cloudflare-spof"
            autoFocus
          />
          <div className={"hint" + (err ? " error" : "")}>{err || "Lowercase, hyphens only."}</div>
        </div>
        <div>
          <label>Working title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Cloudflare: who runs the internet"
          />
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <div style={{ flex: 1 }}>
            <label>Date</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div style={{ flex: 1 }}>
            <label>Stage</label>
            <select value={stage} onChange={(e) => setStage(e.target.value)}>
              {stages.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="row">
          <button onClick={onClose}>Cancel</button>
          <button className="primary" onClick={submit}>
            Add card
          </button>
        </div>
      </div>
    </div>
  );
}
