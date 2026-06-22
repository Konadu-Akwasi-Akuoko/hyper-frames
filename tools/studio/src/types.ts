// Client-facing types. Must stay aligned with the server's JSON output (the
// house pattern duplicates the envelope + row shapes across the two tsconfig
// projects rather than sharing a module).

export type ArtifactStatus = "present" | "partial" | "missing" | "unknown";
export type IdeaType = "mirror" | "comment_demand" | "trend" | "manual";
export type IdeaKind = "unset" | "long" | "short" | "series";
export type IdeaStatus = "new" | "keep" | "rejected" | "promoted";

export interface Evidence {
  views?: number;
  points?: number;
  comments?: number;
  comment_count?: number;
  duration_s?: number;
  published_at?: string;
  count?: number;
  quotes?: { text: string; likes?: number }[];
  /**
   * Categorical rationale lean (raw → pursue), set by the skill. A 3-state
   * notch, NOT a number/grade — drives the wire meter fill. Optional; absent
   * for manual ideas (defaults from triage status).
   */
  lean?: "hold" | "lean" | "strong";
}

export interface Idea {
  id: string;
  type: IdeaType;
  kind: IdeaKind;
  kind_source: "ai" | "human" | null;
  kind_why: string | null;
  status: IdeaStatus;
  title: string;
  rationale: string | null;
  source: string | null;
  source_url: string | null;
  source_title: string | null;
  evidence: Evidence | null;
  raw_signal_id: string | null;
  first_seen: string;
  notes: string | null;
  promoted_slug: string | null;
}

export interface BoardCard {
  slug: string;
  date: string;
  /** folder key `<slug>-<date>` — the board_overlay PK and API route param. */
  name: string;
  title: string;
  /** promote-time snapshot of the idea's format; "unset" when no overlay kind. */
  kind: IdeaKind;
  kindSource: "ai" | "human" | null;
  stage: string;
  artifacts: Record<string, ArtifactStatus>;
  suggestedStage: string | null;
  hasDrift: boolean;
  /** 0..1 desk-meter fill: cold idea → red on-air. */
  progress: number;
  notes: string | null;
  fromIdea: string | null;
  /** true when a `videos/<slug>-<date>/` folder exists on disk. */
  onDisk: boolean;
}

export interface Channel {
  handle: string;
  url: string;
  note: string | null;
  active: boolean;
}

export interface StageDef {
  id: string;
  label: string;
  who: "human" | "ai";
}

export interface RawCounts {
  total: number;
  bySource: Record<string, number>;
}
