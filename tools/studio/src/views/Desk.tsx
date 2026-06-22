import { useState, useEffect, useCallback } from "react";
import { api, ApiError } from "../api";
import type { BoardCard, StageDef } from "../types";
import LaneCard from "../components/LaneCard";
import DetailPanel from "../components/DetailPanel";
import AddCardDialog from "../components/AddCardDialog";

function errMsg(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  return e instanceof Error ? e.message : String(e);
}

export default function Desk({
  stages,
  board,
  onChange,
  query,
}: {
  stages: StageDef[];
  board: BoardCard[];
  onChange: () => void;
  query: string;
}) {
  const [openName, setOpenName] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [dragName, setDragName] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; err?: boolean } | null>(null);

  const flash = useCallback((msg: string, err = false) => {
    setToast({ msg, err });
    setTimeout(() => setToast(null), 2000);
  }, []);

  const q = query.trim().toLowerCase();
  const filtered = q
    ? board.filter((c) => `${c.title} ${c.name}`.toLowerCase().includes(q))
    : board;
  const openCard = board.find((c) => c.name === openName) ?? null;

  const move = useCallback(
    async (name: string, stage: string) => {
      try {
        await api.setCard(name, { stage });
        onChange();
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [onChange, flash],
  );

  const sync = useCallback(async () => {
    try {
      await api.syncBoard();
      onChange();
      flash("Rescanned videos/");
    } catch (e) {
      flash(errMsg(e), true);
    }
  }, [onChange, flash]);

  const save = useCallback(
    async (name: string, body: { stage: string; notes: string }) => {
      try {
        await api.setCard(name, body);
        onChange();
        setOpenName(null);
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [onChange, flash],
  );

  const del = useCallback(
    async (name: string) => {
      try {
        await api.deleteCard(name);
        onChange();
        setOpenName(null);
        flash("Card removed (videos/ folder left untouched)");
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [onChange, flash],
  );

  const add = useCallback(
    async (body: { slug: string; title?: string; date: string; stage: string }) => {
      try {
        await api.addCard(body);
        onChange();
        setAdding(false);
        flash("Card added");
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [onChange, flash],
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = document.activeElement?.tagName;
      if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT") return;
      if (adding) return;
      if (e.key === "n") {
        e.preventDefault();
        setAdding(true);
      } else if (e.key === "s") {
        e.preventDefault();
        sync();
      } else if (e.key === "Escape") {
        setOpenName(null);
      } else if (e.key === "Delete" && openName) {
        e.preventDefault();
        del(openName);
      }
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, [adding, openName, sync, del]);

  return (
    <section className="view active">
      <div className="deskhead">
        <div className="legend">
          <div className="cap">
            Card meter = artifact progress, scanned from <code>videos/</code>
          </div>
          <div className="ramp" />
          <div className="ends">
            <span>idea</span>
            <span>on-air</span>
          </div>
        </div>
        <div className="spacer" />
        <div className="desk-actions">
          <button onClick={() => setAdding(true)}>+ Add card</button>
          <button onClick={sync}>⟳ Sync</button>
        </div>
      </div>

      <div className="deskwrap">
        <div className="lanes">
          {stages.map((st) => {
            const cards = filtered.filter((c) => c.stage === st.id);
            return (
              <div
                key={st.id}
                className={"lane" + (st.id === "published" ? " published" : "")}
              >
                <div className="lane-head">
                  <span>
                    <span className="name">{st.label}</span>
                    <span className="who">{st.who}</span>
                  </span>
                  <span className="ct num">{cards.length}</span>
                </div>
                <div
                  className={"trough" + (dragOver === st.id ? " dragover" : "")}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragOver(st.id);
                  }}
                  onDragLeave={() => setDragOver((d) => (d === st.id ? null : d))}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragOver(null);
                    if (dragName) move(dragName, st.id);
                    setDragName(null);
                  }}
                >
                  {cards.map((c) => (
                    <LaneCard
                      key={c.name}
                      card={c}
                      onOpen={() => setOpenName(c.name)}
                      onDragStart={() => setDragName(c.name)}
                      onDragEnd={() => setDragName(null)}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {openCard ? (
        <DetailPanel
          card={openCard}
          stages={stages}
          onClose={() => setOpenName(null)}
          onSave={(b) => save(openCard.name, b)}
          onDelete={() => del(openCard.name)}
        />
      ) : null}

      {adding ? (
        <AddCardDialog stages={stages} onClose={() => setAdding(false)} onAdd={add} />
      ) : null}

      {toast ? <div className={"toast" + (toast.err ? " err" : "")}>{toast.msg}</div> : null}
    </section>
  );
}
