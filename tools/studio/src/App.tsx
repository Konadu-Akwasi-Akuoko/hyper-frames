import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "./api";
import type { StageDef, BoardCard } from "./types";
import Wire from "./views/Wire";
import Desk from "./views/Desk";

type View = "wire" | "desk";

export default function App() {
  const [view, setView] = useState<View>("wire");
  const [stages, setStages] = useState<StageDef[]>([]);
  const [board, setBoard] = useState<BoardCard[]>([]);
  const [query, setQuery] = useState("");
  const searchRef = useRef<HTMLInputElement>(null);

  const refreshBoard = useCallback(async () => {
    try {
      setBoard(await api.board());
    } catch {
      /* surfaced inside views; masthead count just stays */
    }
  }, []);

  useEffect(() => {
    api.stages().then(setStages).catch(() => {});
    // eslint-disable-next-line react-hooks/set-state-in-effect -- canonical fetch-on-mount
    refreshBoard();
  }, [refreshBoard]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, []);

  const onAir = board.filter((c) => c.stage === "published").length;

  return (
    <>
      <header className="masthead">
        <div className="wordmark">
          <span className="bars">
            <i />
            <i />
            <i />
          </span>{" "}
          studio
        </div>
        <div className="viewtoggle">
          <button className={view === "wire" ? "active" : ""} onClick={() => setView("wire")}>
            The Wire
          </button>
          <button className={view === "desk" ? "active" : ""} onClick={() => setView("desk")}>
            The Desk
          </button>
        </div>
        <div className="spacer" />
        <div className="meta">
          <input
            ref={searchRef}
            className="search"
            placeholder="⌘K  search the signal"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {onAir > 0 ? (
            <span className="onair">
              <span className="dot" /> {onAir} ON-AIR
            </span>
          ) : null}
        </div>
      </header>

      {view === "wire" ? (
        <Wire onPromoted={refreshBoard} query={query} />
      ) : (
        <Desk stages={stages} board={board} onChange={refreshBoard} query={query} />
      )}
    </>
  );
}
