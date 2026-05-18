import { useCallback, useRef, useState } from "react";
import type { CutsFile, Cut } from "../types";
import { apiFetch, ApiError } from "../api";
import type { SaveState } from "../components/SaveButton";

const HISTORY_DEPTH = 100;

type HistoryEntry =
  | { kind: "add"; cut: Cut }
  | { kind: "remove"; cut: Cut }
  | { kind: "update"; id: string; before: Cut; after: Cut };

function sortCuts(list: Cut[]): Cut[] {
  return [...list].sort((a, b) => a.start - b.start);
}

export function useCutsEditor(slug: string, initial: CutsFile | null) {
  const [cuts, setCuts] = useState<Cut[]>(initial?.cuts ?? []);
  const [saveState, setSaveState] = useState<SaveState>(
    initial ? { kind: "saved", at: new Date() } : { kind: "pristine" },
  );
  const [historyFlags, setHistoryFlags] = useState({ canUndo: false, canRedo: false });

  const idCounter = useRef(0);
  const undoStack = useRef<HistoryEntry[]>([]);
  const redoStack = useRef<HistoryEntry[]>([]);
  // Open snapshots keyed by cut id — captured on first region-update of a drag,
  // committed (or discarded) on region-updated. See Waveform.tsx wiring.
  const openDragSnapshots = useRef<Map<string, Cut>>(new Map());

  const newId = () => {
    idCounter.current += 1;
    return `cut_${Date.now().toString(36)}_${idCounter.current}`;
  };

  const markDirty = () => setSaveState({ kind: "dirty" });

  const syncHistoryFlags = useCallback(() => {
    setHistoryFlags({
      canUndo: undoStack.current.length > 0,
      canRedo: redoStack.current.length > 0,
    });
  }, []);

  const pushHistory = useCallback(
    (entry: HistoryEntry, { clearRedo = true }: { clearRedo?: boolean } = {}) => {
      const stack = undoStack.current;
      stack.push(entry);
      if (stack.length > HISTORY_DEPTH) stack.shift();
      if (clearRedo) redoStack.current.length = 0;
      syncHistoryFlags();
    },
    [syncHistoryFlags],
  );

  const add = useCallback(
    (start: number, end: number, reason?: string): Cut => {
      const cut: Cut = { id: newId(), start, end, reason };
      setCuts((prev) => sortCuts([...prev, cut]));
      pushHistory({ kind: "add", cut });
      markDirty();
      return cut;
    },
    [pushHistory],
  );

  const update = useCallback(
    (id: string, patch: { start?: number; end?: number; reason?: string }) => {
      let before: Cut | null = null;
      let after: Cut | null = null;
      setCuts((prev) => {
        const idx = prev.findIndex((c) => c.id === id);
        if (idx < 0) return prev;
        const current = prev[idx];
        const merged = { ...current, ...patch };
        if (
          merged.start === current.start &&
          merged.end === current.end &&
          merged.reason === current.reason
        ) {
          return prev;
        }
        before = current;
        after = merged;
        const next = prev.slice();
        next[idx] = merged;
        return sortCuts(next);
      });
      if (before && after) {
        // If this `update` is part of an open drag (Waveform calls beginUpdate
        // first), don't push a per-tick entry — the drag-end commitUpdate will
        // push a single coalesced entry covering the whole drag.
        if (!openDragSnapshots.current.has(id)) {
          pushHistory({ kind: "update", id, before, after });
        }
        setSaveState((prev) =>
          prev.kind === "dirty" || prev.kind === "saving" ? prev : { kind: "dirty" },
        );
      }
    },
    [pushHistory],
  );

  const remove = useCallback(
    (id: string) => {
      let removed: Cut | null = null;
      setCuts((prev) => {
        const idx = prev.findIndex((c) => c.id === id);
        if (idx < 0) return prev;
        removed = prev[idx];
        return prev.filter((c) => c.id !== id);
      });
      if (removed) {
        pushHistory({ kind: "remove", cut: removed });
        markDirty();
      }
    },
    [pushHistory],
  );

  // Drag-coalescing for region resize. Called from Waveform on the first
  // region-update of a drag (gated by region.updatingSide != null) and on
  // region-updated, respectively. Each open snapshot collapses an arbitrary
  // number of intermediate `update()` calls into one history entry.
  const beginUpdate = useCallback((id: string) => {
    if (openDragSnapshots.current.has(id)) return;
    setCuts((prev) => {
      const current = prev.find((c) => c.id === id);
      if (current) openDragSnapshots.current.set(id, current);
      return prev;
    });
  }, []);

  const commitUpdate = useCallback(
    (id: string) => {
      const before = openDragSnapshots.current.get(id);
      if (!before) return;
      openDragSnapshots.current.delete(id);
      setCuts((prev) => {
        const after = prev.find((c) => c.id === id);
        if (!after) return prev;
        if (
          after.start === before.start &&
          after.end === before.end &&
          after.reason === before.reason
        ) {
          return prev;
        }
        pushHistory({ kind: "update", id, before, after });
        return prev;
      });
    },
    [pushHistory],
  );

  const undo = useCallback(() => {
    const entry = undoStack.current.pop();
    if (!entry) return;
    redoStack.current.push(entry);
    if (redoStack.current.length > HISTORY_DEPTH) redoStack.current.shift();
    if (entry.kind === "add") {
      setCuts((prev) => prev.filter((c) => c.id !== entry.cut.id));
    } else if (entry.kind === "remove") {
      setCuts((prev) => sortCuts([...prev, entry.cut]));
    } else {
      setCuts((prev) => {
        const idx = prev.findIndex((c) => c.id === entry.id);
        if (idx < 0) return prev;
        const next = prev.slice();
        next[idx] = entry.before;
        return sortCuts(next);
      });
    }
    markDirty();
    syncHistoryFlags();
  }, [syncHistoryFlags]);

  const redo = useCallback(() => {
    const entry = redoStack.current.pop();
    if (!entry) return;
    // Re-push to undo without clearing redo (the user might keep redoing).
    pushHistory(entry, { clearRedo: false });
    if (entry.kind === "add") {
      setCuts((prev) => sortCuts([...prev, entry.cut]));
    } else if (entry.kind === "remove") {
      setCuts((prev) => prev.filter((c) => c.id !== entry.cut.id));
    } else {
      setCuts((prev) => {
        const idx = prev.findIndex((c) => c.id === entry.id);
        if (idx < 0) return prev;
        const next = prev.slice();
        next[idx] = entry.after;
        return sortCuts(next);
      });
    }
    markDirty();
    syncHistoryFlags();
  }, [pushHistory, syncHistoryFlags]);

  const save = useCallback(async () => {
    setSaveState({ kind: "saving" });
    try {
      const body: CutsFile = { version: 1, cuts };
      await apiFetch<{ slug: string; savedAt: string }>(
        `/api/session/${encodeURIComponent(slug)}/cuts`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
      );
      setSaveState({ kind: "saved", at: new Date() });
    } catch (e: unknown) {
      const msg =
        e instanceof ApiError
          ? `${e.code}: ${e.message}`
          : e instanceof Error
            ? e.message
            : String(e);
      setSaveState({ kind: "error", message: msg });
    }
  }, [slug, cuts]);

  return {
    cuts,
    saveState,
    add,
    update,
    remove,
    beginUpdate,
    commitUpdate,
    undo,
    redo,
    canUndo: historyFlags.canUndo,
    canRedo: historyFlags.canRedo,
    save,
  };
}
