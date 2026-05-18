export function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00.000";
  const totalMs = Math.floor(seconds * 1000);
  const m = Math.floor(totalMs / 60000);
  const s = Math.floor((totalMs % 60000) / 1000);
  const ms = totalMs % 1000;
  return `${m}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

export function formatTimeShort(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const total = Math.floor(seconds);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

const SLUG_DATE_RE = /-(\d{4})-(\d{2})-(\d{2})$/;

export function parseSlugDate(slug: string): Date | null {
  const m = slug.match(SLUG_DATE_RE);
  if (!m) return null;
  const date = new Date(`${m[1]}-${m[2]}-${m[3]}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function slugTitle(slug: string): string {
  const m = slug.match(SLUG_DATE_RE);
  const base = m ? slug.slice(0, m.index) : slug;
  return base.replace(/-/g, " ");
}

export function relativeSeconds(from: Date, now: Date = new Date()): string {
  const diff = Math.max(0, Math.floor((now.getTime() - from.getTime()) / 1000));
  if (diff < 5) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}
