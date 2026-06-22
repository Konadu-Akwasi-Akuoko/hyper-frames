import type { IdeaType } from "./types";

const STROKE = { fill: "none", stroke: "currentColor", strokeWidth: 1.5 } as const;

/** vectorscope target = mirror */
export const MirrorGlyph = (p: { className?: string }) => (
  <svg className={p.className} viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth={1.4}>
    <circle cx="9" cy="9" r="7" />
    <path d="M2 9h14M9 2v14" />
  </svg>
);

/** waveform tick = comment-demand */
export const CommentGlyph = (p: { className?: string }) => (
  <svg className={p.className} viewBox="0 0 18 18" {...STROKE}>
    <path d="M1 9h2l2-5 3 11 3-9 2 5 1-2h2" />
  </svg>
);

/** rising trace = trend */
export const TrendGlyph = (p: { className?: string }) => (
  <svg className={p.className} viewBox="0 0 18 18" {...STROKE}>
    <path d="M2 15l5-6 3 3 6-9" />
    <path d="M16 6V3h-3" />
  </svg>
);

/** concentric target = all signal / manual */
export const AllGlyph = (p: { className?: string }) => (
  <svg className={p.className} viewBox="0 0 18 18" {...STROKE}>
    <circle cx="9" cy="9" r="6.5" />
    <circle cx="9" cy="9" r="2" />
  </svg>
);

export function TypeGlyph(p: { type: IdeaType; className?: string }) {
  switch (p.type) {
    case "mirror":
      return <MirrorGlyph className={p.className} />;
    case "comment_demand":
      return <CommentGlyph className={p.className} />;
    case "trend":
      return <TrendGlyph className={p.className} />;
    default:
      return <AllGlyph className={p.className} />;
  }
}
