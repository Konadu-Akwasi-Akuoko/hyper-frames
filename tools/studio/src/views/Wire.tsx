import { useState, useEffect, useCallback } from "react";
import { api } from "../api";
import { ApiError } from "../api";
import type { Idea, IdeaType, IdeaKind } from "../types";
import Dispatch from "../components/Dispatch";
import type { DispatchAnim } from "../components/Dispatch";
import { AllGlyph, MirrorGlyph, CommentGlyph, TrendGlyph } from "../glyphs";

const KIND_NEXT: Record<IdeaKind, IdeaKind> = {
  unset: "long",
  long: "short",
  short: "series",
  series: "unset",
};

function errMsg(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  return e instanceof Error ? e.message : String(e);
}

export default function Wire({
  onPromoted,
  query,
}: {
  onPromoted: () => void;
  query: string;
}) {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [counts, setCounts] = useState<{ total: number; byType: Record<string, number> }>({
    total: 0,
    byType: {},
  });
  const [band, setBand] = useState<IdeaType | null>(null);
  const [sel, setSel] = useState(0);
  const [anim, setAnim] = useState<Record<string, DispatchAnim>>({});
  const [running, setRunning] = useState(false);
  const [toast, setToast] = useState<{ msg: string; err?: boolean } | null>(null);

  const flash = useCallback((msg: string, err = false) => {
    setToast({ msg, err });
    setTimeout(() => setToast(null), 2200);
  }, []);

  const load = useCallback(async () => {
    try {
      const [list, ct] = await Promise.all([
        api.ideas(band ? { type: band } : undefined),
        api.ideaCounts(),
      ]);
      setIdeas(list);
      setCounts(ct);
    } catch (e) {
      flash(errMsg(e), true);
    }
  }, [band, flash]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- canonical fetch-on-(band)change
    load();
  }, [load]);

  const q = query.trim().toLowerCase();
  const visible = q
    ? ideas.filter((i) =>
        `${i.title} ${i.rationale ?? ""}`.toLowerCase().includes(q),
      )
    : ideas;
  const selClamped = visible.length ? Math.min(sel, visible.length - 1) : 0;

  const keep = useCallback(
    async (id: string) => {
      try {
        await api.triage(id, { status: "keep" });
        flash("Kept");
        load();
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [flash, load],
  );

  const reject = useCallback(
    async (id: string) => {
      setAnim((a) => ({ ...a, [id]: "squelched" }));
      try {
        await api.triage(id, { status: "rejected" });
      } catch (e) {
        flash(errMsg(e), true);
      }
      setTimeout(() => load(), 320);
    },
    [flash, load],
  );

  const cycleKind = useCallback(
    async (idea: Idea) => {
      try {
        await api.triage(idea.id, { kind: KIND_NEXT[idea.kind] });
        load();
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [flash, load],
  );

  const setKind = useCallback(
    async (id: string, kind: IdeaKind) => {
      try {
        await api.triage(id, { kind });
        load();
      } catch (e) {
        flash(errMsg(e), true);
      }
    },
    [flash, load],
  );

  const promote = useCallback(
    async (id: string) => {
      setAnim((a) => ({ ...a, [id]: "committing" }));
      try {
        const r = await api.promote(id);
        flash(`Promoted → ${r.slug}`);
      } catch (e) {
        flash(errMsg(e), true);
      }
      setTimeout(() => {
        load();
        onPromoted();
      }, 520);
    },
    [flash, load, onPromoted],
  );

  const runDiscovery = useCallback(async () => {
    setRunning(true);
    flash("Discovery running — serial & bounded, this can take a few minutes…");
    try {
      const r = await api.runDiscovery({ videosPerChannel: 8, commentsPerVideo: 20 });
      flash(`Discovery done — ${r.total} raw signals waiting. Ask the studio-ideas skill to curate.`);
    } catch (e) {
      flash(`Discovery failed: ${errMsg(e)}`, true);
    } finally {
      setRunning(false);
    }
  }, [flash]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = document.activeElement?.tagName;
      if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT") return;
      const cur = visible[selClamped];
      if (e.key === "j") {
        e.preventDefault();
        setSel(Math.min(visible.length - 1, selClamped + 1));
      } else if (e.key === "k") {
        e.preventDefault();
        setSel(Math.max(0, selClamped - 1));
      } else if (e.key === "x" && cur) {
        e.preventDefault();
        reject(cur.id);
      } else if (e.key === "p" && cur) {
        e.preventDefault();
        promote(cur.id);
      } else if (e.key === "Enter" && cur) {
        e.preventDefault();
        keep(cur.id);
      } else if (cur && (e.key === "1" || e.key === "2" || e.key === "3")) {
        e.preventDefault();
        const map = { "1": "long", "2": "short", "3": "series" } as const;
        setKind(cur.id, map[e.key]);
      }
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, [visible, selClamped, reject, promote, keep, setKind]);

  return (
    <section className="view active">
      <div className="wire-wrap">
        <aside className="rail">
          <div>
            <h4>Signal</h4>
            <div className="band">
              <button className={band === null ? "on" : ""} onClick={() => setBand(null)}>
                <span className="glyph">
                  <AllGlyph />
                </span>
                <span className="lbl">All signal</span>
                <span className="ct num">{counts.total}</span>
              </button>
              <button className={band === "mirror" ? "on" : ""} onClick={() => setBand("mirror")}>
                <span className="glyph">
                  <MirrorGlyph />
                </span>
                <span className="lbl">Mirror</span>
                <span className="ct num">{counts.byType.mirror ?? 0}</span>
              </button>
              <button
                className={band === "comment_demand" ? "on" : ""}
                onClick={() => setBand("comment_demand")}
              >
                <span className="glyph">
                  <CommentGlyph />
                </span>
                <span className="lbl">Comment-demand</span>
                <span className="ct num">{counts.byType.comment_demand ?? 0}</span>
              </button>
              <button className={band === "trend" ? "on" : ""} onClick={() => setBand("trend")}>
                <span className="glyph">
                  <TrendGlyph />
                </span>
                <span className="lbl">Trend</span>
                <span className="ct num">{counts.byType.trend ?? 0}</span>
              </button>
            </div>
          </div>

          <div className="legend">
            <div className="cap">Meter = rationale lean. Never a score.</div>
            <div className="ramp" />
            <div className="ends">
              <span>raw</span>
              <span>pursue</span>
            </div>
          </div>

          <div>
            <h4>Discovery</h4>
            <button className="run-btn" disabled={running} onClick={runDiscovery}>
              {running ? "Running…" : "⟲ Run discovery"}
            </button>
            <div className="run-note">
              Serial &amp; bounded. Then ask the <b>studio-ideas</b> skill to curate the raw
              signal into ideas.
            </div>
          </div>

          <div className="keys">
            <div>
              <kbd>j</kbd> <kbd>k</kbd> move · <kbd>↵</kbd> keep · <kbd>x</kbd> reject
            </div>
            <div>
              <kbd>p</kbd> promote → the desk
            </div>
            <div>
              <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> kind: long·short·series
            </div>
          </div>
        </aside>

        <main className="feed">
          <h3>
            Incoming <span className="ct num">{visible.length} on the wire</span>
          </h3>
          {visible.length === 0 ? (
            <div className="empty">
              No ideas on the wire. Run discovery, then ask the <b>studio-ideas</b> skill to
              curate — keepers land here.
            </div>
          ) : (
            visible.map((idea, idx) => (
              <Dispatch
                key={idea.id}
                idea={idea}
                selected={idx === selClamped}
                anim={anim[idea.id]}
                onSelect={() => setSel(idx)}
                onKeep={() => keep(idea.id)}
                onReject={() => reject(idea.id)}
                onPromote={() => promote(idea.id)}
                onCycleKind={() => cycleKind(idea)}
                onAcceptKind={() => setKind(idea.id, idea.kind)}
              />
            ))
          )}
        </main>
      </div>
      {toast ? <div className={"toast" + (toast.err ? " err" : "")}>{toast.msg}</div> : null}
    </section>
  );
}
