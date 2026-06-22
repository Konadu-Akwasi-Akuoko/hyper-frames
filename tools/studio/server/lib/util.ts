import { randomUUID } from "node:crypto";

export function nowISO(): string {
  return new Date().toISOString();
}
export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}
export function uuid(): string {
  return randomUUID();
}

/** kebab-case a title for a folder slug (ported from kanban.html). */
export function kebabSlug(input: string): string {
  return String(input ?? "")
    .toLowerCase()
    .replace(/[^a-z0-9\s\-_]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export interface IdeaRow {
  id: string;
  type: string;
  kind: string;
  status: string;
  title: string;
  rationale: string | null;
  source: string | null;
  source_url: string | null;
  source_title: string | null;
  evidence_json: string | null;
  raw_signal_id: string | null;
  first_seen: string;
  notes: string | null;
  promoted_slug: string | null;
  kind_source: string | null;
  kind_why: string | null;
}

export function mapIdeaRow(r: IdeaRow) {
  let evidence: unknown = null;
  if (r.evidence_json) {
    try {
      evidence = JSON.parse(r.evidence_json);
    } catch {
      evidence = null;
    }
  }
  return {
    id: r.id,
    type: r.type,
    kind: r.kind,
    status: r.status,
    title: r.title,
    rationale: r.rationale,
    source: r.source,
    source_url: r.source_url,
    source_title: r.source_title,
    evidence,
    raw_signal_id: r.raw_signal_id,
    first_seen: r.first_seen,
    notes: r.notes,
    promoted_slug: r.promoted_slug,
    kind_source: r.kind_source,
    kind_why: r.kind_why,
  };
}
