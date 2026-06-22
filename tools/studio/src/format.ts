import type { Idea } from "./types";

export function fmtCount(n?: number | null): string {
  if (n == null) return "";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}k`;
  return String(n);
}

export function fmtDuration(s?: number | null): string {
  if (s == null) return "";
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${String(sec).padStart(2, "0")}`;
}

/** ISO date or yt `YYYYMMDD` → `MM·DD`. */
export function mdDate(iso?: string | null): string {
  if (!iso) return "";
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) return `${m[2]}·${m[3]}`;
  const y = iso.match(/^(\d{4})(\d{2})(\d{2})$/);
  if (y) return `${y[2]}·${y[3]}`;
  return "";
}

export type Lean = "hold" | "lean" | "strong";

/** Wire-meter fill: the skill's categorical lean, else derived from triage. */
export function leanOf(idea: Idea): Lean {
  const l = idea.evidence?.lean;
  if (l === "hold" || l === "lean" || l === "strong") return l;
  if (idea.status === "keep") return "strong";
  return "lean";
}

export interface EvidenceLines {
  big: string;
  sub: string;
  src: string;
}

/** The right-hand evidence column, shaped per source type. */
export function evidenceLines(idea: Idea): EvidenceLines {
  const ev = idea.evidence ?? {};
  const date = mdDate(ev.published_at ?? idea.first_seen);
  const src = (idea.source ?? "").trim();
  if (idea.type === "comment_demand") {
    return {
      big: ev.count != null ? `×${ev.count} asks` : "asks",
      sub:
        ev.views != null
          ? `${fmtCount(ev.views)} vid`
          : ev.comments != null
            ? `${ev.comments} replies`
            : "",
      src: `comment · ${date}`,
    };
  }
  if (idea.type === "mirror") {
    return {
      big: ev.views != null ? `▶ ${fmtCount(ev.views)}` : "▶ mirror",
      sub: ev.duration_s != null ? fmtDuration(ev.duration_s) : "",
      src: `${src || "youtube"} · ${date}`,
    };
  }
  if (idea.type === "trend") {
    return {
      big: ev.points != null ? `${fmtCount(ev.points)} ▲` : "trend",
      sub: ev.comments != null ? `${ev.comments} ◷` : "",
      src: `${(src || "trend").toUpperCase()} · ${date}`,
    };
  }
  return { big: "", sub: "", src: date };
}
