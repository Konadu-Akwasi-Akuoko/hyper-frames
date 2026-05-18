import type { Video } from "../types";
import { parseSlugDate, slugTitle } from "../utils/format";
import Badge from "./Badge";

type Props = {
  video: Video;
  ready: boolean;
};

export default function VideoCard({ video, ready }: Props) {
  const date = parseSlugDate(video.slug);
  const title = slugTitle(video.slug);
  const missing: string[] = [];
  if (!video.hasAudio) missing.push("audio");
  if (!video.hasTranscript) missing.push("transcript");

  const inner = (
    <>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="text-[15px] font-medium text-[color:var(--color-text)] leading-snug tracking-[-0.005em] capitalize line-clamp-2">
            {title}
          </div>
          {date && (
            <div className="mt-1.5 font-mono text-[10px] text-[color:var(--color-muted-2)] uppercase tracking-[0.12em]">
              {date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit" })}
            </div>
          )}
        </div>
        {ready && (
          <span
            className="shrink-0 mt-0.5 text-[color:var(--color-muted-2)] group-hover:text-[color:var(--color-accent)] group-hover:translate-x-0.5 transition-all"
            aria-hidden
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M5 3l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
        )}
      </div>

      <div className="font-mono text-[10.5px] text-[color:var(--color-muted)] truncate">
        videos/<span className="text-[color:var(--color-text)]">{video.slug}</span>
      </div>

      <div className="flex items-center justify-between gap-2 pt-1 mt-auto">
        <div className="flex flex-wrap gap-1.5">
          <Badge on={video.hasAudio} label="audio" />
          <Badge on={video.hasTranscript} label="transcript" />
          <Badge on={video.hasCuts} label="cuts" />
        </div>
        {!ready && (
          <span className="font-mono text-[9.5px] uppercase tracking-[0.08em] text-[color:var(--color-cut)]/85 whitespace-nowrap">
            needs {missing.join(" + ")}
          </span>
        )}
      </div>
    </>
  );

  const baseClass =
    "group relative flex flex-col gap-3 p-4 rounded-[10px] border bg-[color:var(--color-panel)] min-h-[140px] transition-all duration-150";

  if (ready) {
    return (
      <a
        href={`#/edit/${encodeURIComponent(video.slug)}`}
        className={`${baseClass} border-[color:var(--color-border)] hover:border-[color:var(--color-accent)]/60 hover:bg-[color:var(--color-panel-2)] hover:-translate-y-px hover:shadow-[0_8px_24px_-8px_rgba(110,168,255,0.25)] cursor-pointer`}
      >
        {inner}
      </a>
    );
  }
  return (
    <div className={`${baseClass} border-[color:var(--color-border)]/60 opacity-70`}>
      {inner}
    </div>
  );
}
