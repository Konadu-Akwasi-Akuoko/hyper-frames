export type Who = "human" | "ai";
export interface StageDef {
  id: string;
  label: string;
  who: Who;
}

/** The 12 production stages, ids + labels ported verbatim from kanban.html. */
export const STAGES: StageDef[] = [
  { id: "idea", label: "Idea", who: "human" },
  { id: "research", label: "Research", who: "human" },
  { id: "script", label: "Script", who: "ai" },
  { id: "voiceover", label: "Voiceover", who: "ai" },
  { id: "compose", label: "Compose", who: "ai" },
  { id: "review", label: "Review", who: "human" },
  { id: "thumbnail", label: "Thumbnail", who: "ai" },
  { id: "translate", label: "Captions", who: "ai" },
  { id: "render", label: "Render", who: "ai" },
  { id: "published", label: "Published", who: "human" },
  { id: "publish-qa", label: "Publish QA", who: "ai" },
  { id: "shorts", label: "Shorts", who: "ai" },
];

export const STAGE_IDS: string[] = STAGES.map((s) => s.id);

export function stageIndex(id: string): number {
  return STAGE_IDS.indexOf(id);
}

export function isStage(id: string): boolean {
  return STAGE_IDS.includes(id);
}

/** Post-render milestones are human-moved, never scanned; exempt from drift. */
export const MILESTONE_STAGES = ["published", "publish-qa", "shorts"];

/**
 * The scanned artifact ladder, in order. `translate`/`published`/`publish-qa`/
 * `shorts` are stage-derived (not probed on disk), so they are not here — this
 * matches kanban.html's `computeSuggested` reachable set.
 */
export const SCANNED_LADDER = [
  "research",
  "script",
  "voiceover",
  "compose",
  "review",
  "thumbnail",
  "render",
];

/**
 * Side-artifacts that may legitimately be absent on an otherwise-advanced video,
 * so their absence must NOT halt the walk: `research` (seo/research.json is
 * routinely skipped), `review` (sfx/music comps are optional), and `thumbnail`
 * (may be made after render). The backbone every video passes through in order —
 * script → voiceover → compose → render — is the halting set.
 */
export const OPTIONAL_STAGES = ["research", "review", "thumbnail"];

/**
 * The next stage to work on: the furthest rung reachable through a contiguous
 * present backbone. A missing backbone rung halts the walk, so a present
 * *downstream* artifact (e.g. an empty `hyperframes init` scaffold satisfying
 * `compose`) can never leapfrog an earlier gap. Optional side-artifacts are
 * skipped without halting. `idea` when the backbone hasn't started.
 */
export function computeSuggested(
  artifacts: Record<string, string>,
): string {
  let suggested = "idea";
  for (const stage of SCANNED_LADDER) {
    if (artifacts[stage] === "present") {
      suggested = stage;
    } else if (!OPTIONAL_STAGES.includes(stage)) {
      break;
    }
  }
  return suggested;
}

/** The ordered backbone every video passes through; `OPTIONAL_STAGES` branch off. */
export const BACKBONE_STAGES = SCANNED_LADDER.filter(
  (s) => !OPTIONAL_STAGES.includes(s),
);

/**
 * Whether a card filed at `filed` is inconsistent with the artifacts on disk.
 * Drift fires on a genuine contradiction, not on being filed at the
 * work-in-progress stage:
 *  - **ahead/impossible** — a backbone stage *before* `filed` is not present
 *    (you can't be at `compose` with no `voiceover`); or
 *  - **stale** — a backbone stage *after* `filed` is already present (the work
 *    has moved on; advance the card).
 * Filing a card at a stage whose own artifact doesn't exist yet — with all
 * prerequisites met and nothing downstream done — is the normal in-progress
 * state and does NOT drift. Post-render milestones are human-moved and exempt.
 */
export function stageDriftsFrom(
  filed: string,
  artifacts: Record<string, string>,
): boolean {
  if (MILESTONE_STAGES.includes(filed)) return false;
  const fi = stageIndex(filed);
  if (fi < 0) return false;
  for (const b of BACKBONE_STAGES) {
    const bi = stageIndex(b);
    if (bi < fi && artifacts[b] !== "present") return true;
    if (bi > fi && artifacts[b] === "present") return true;
  }
  return false;
}

/** Desk-meter fill fraction: cold idea (0) climbing to red on-air (1). */
export function stageProgress(stage: string): number {
  const idx = stageIndex(stage);
  if (idx < 0) return 0;
  return idx / (STAGES.length - 1);
}
