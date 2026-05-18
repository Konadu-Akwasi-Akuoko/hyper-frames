import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { apiFetch, ApiError } from "../api";
import type { Video } from "../types";
import VideoCard from "../components/VideoCard";
import SearchInput from "../components/SearchInput";

type State =
  | { kind: "loading" }
  | { kind: "ok"; videos: Video[] }
  | { kind: "error"; code: string; message: string };

export default function PickerPage() {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [query, setQuery] = useState("");

  useEffect(() => {
    let cancelled = false;
    apiFetch<{ videos: Video[] }>("/api/videos")
      .then((data) => {
        if (!cancelled) setState({ kind: "ok", videos: data.videos });
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        const err = e instanceof ApiError ? e : new ApiError("UNKNOWN", String(e), 0);
        setState({ kind: "error", code: err.code, message: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const { ready, missing, totalReady, totalAll } = useMemo(() => {
    if (state.kind !== "ok") {
      return { ready: [] as Video[], missing: [] as Video[], totalReady: 0, totalAll: 0 };
    }
    const q = query.trim().toLowerCase();
    const filtered = q ? state.videos.filter((v) => v.slug.toLowerCase().includes(q)) : state.videos;
    return {
      ready: filtered.filter((v) => v.hasAudio && v.hasTranscript),
      missing: filtered.filter((v) => !(v.hasAudio && v.hasTranscript)),
      totalReady: state.videos.filter((v) => v.hasAudio && v.hasTranscript).length,
      totalAll: state.videos.length,
    };
  }, [state, query]);

  return (
    <div className="max-w-[1480px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 lg:py-14 animate-fade-in">
      <Hero state={state} totalReady={totalReady} totalAll={totalAll} />

      {state.kind === "ok" && state.videos.length > 0 && (
        <div className="mb-8 max-w-md">
          <SearchInput value={query} onChange={setQuery} />
        </div>
      )}

      {state.kind === "loading" && <LoadingGrid />}
      {state.kind === "error" && <ErrorBlock code={state.code} message={state.message} />}

      {state.kind === "ok" && (
        <div className="space-y-12">
          {state.videos.length === 0 ? (
            <NoVideos />
          ) : (
            <>
              <Section
                label="ready to edit"
                count={ready.length}
                emptyMessage={
                  query
                    ? `No ready videos match "${query}".`
                    : "No videos have both audio and transcript yet."
                }
              >
                {ready.map((v) => (
                  <VideoCard key={v.slug} video={v} ready />
                ))}
              </Section>

              {missing.length > 0 && (
                <Section label="missing assets" count={missing.length} emptyMessage="">
                  {missing.map((v) => (
                    <VideoCard key={v.slug} video={v} ready={false} />
                  ))}
                </Section>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Hero({
  state,
  totalReady,
  totalAll,
}: {
  state: State;
  totalReady: number;
  totalAll: number;
}) {
  return (
    <div className="mb-10 flex items-start justify-between gap-8 flex-wrap">
      <div className="max-w-xl">
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--color-muted-2)] mb-3">
          01 · select source
        </div>
        <h1 className="text-[34px] sm:text-[40px] leading-[1.05] font-semibold tracking-[-0.025em]">
          Fine-tune the cuts
          <br />
          <span className="text-[color:var(--color-muted)]">your agent proposed.</span>
        </h1>
        <p className="mt-5 text-[13.5px] text-[color:var(--color-muted)] leading-relaxed max-w-md">
          Pick a video folder to open in the waveform editor. The picker shows
          which folders are ready and what's still missing.
        </p>
      </div>

      {state.kind === "ok" && totalAll > 0 && (
        <div className="flex items-center gap-3 px-4 py-2.5 rounded-[10px] bg-[color:var(--color-panel)] border border-[color:var(--color-border)]">
          <div className="flex flex-col items-end">
            <span className="font-mono text-[9.5px] uppercase tracking-[0.14em] text-[color:var(--color-muted-2)]">
              ready
            </span>
            <span className="font-mono text-[20px] text-[color:var(--color-text)] tabular-nums leading-none mt-1">
              {totalReady}
              <span className="text-[color:var(--color-muted-2)]">/{totalAll}</span>
            </span>
          </div>
          <span className="w-px h-9 bg-[color:var(--color-border)]" aria-hidden />
          <span
            className="w-2 h-2 rounded-full bg-[color:var(--color-keep)] shadow-[0_0_8px_rgba(74,222,128,0.6)] animate-pulse-soft"
            aria-hidden
          />
        </div>
      )}
    </div>
  );
}

function Section({
  label,
  count,
  emptyMessage,
  children,
}: {
  label: string;
  count: number;
  emptyMessage: string;
  children: ReactNode;
}) {
  return (
    <section>
      <div className="flex items-baseline gap-3 mb-4">
        <h2 className="font-mono text-[11px] uppercase tracking-[0.14em] text-[color:var(--color-muted)]">
          {label}
        </h2>
        <span className="font-mono text-[10px] text-[color:var(--color-muted-2)] tabular-nums">
          {String(count).padStart(2, "0")}
        </span>
        <span
          className="flex-1 h-px bg-gradient-to-r from-[color:var(--color-border)] to-transparent"
          aria-hidden
        />
      </div>
      {count === 0 ? (
        emptyMessage && <p className="text-[12.5px] text-[color:var(--color-muted-2)] italic">{emptyMessage}</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">{children}</div>
      )}
    </section>
  );
}

function LoadingGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div
          key={i}
          className="h-[148px] rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)]/40 animate-pulse-soft"
          style={{ animationDelay: `${i * 0.12}s` }}
        />
      ))}
    </div>
  );
}

function ErrorBlock({ code, message }: { code: string; message: string }) {
  return (
    <div className="rounded-[10px] border border-[color:var(--color-cut)]/40 bg-[color:var(--color-cut)]/5 p-5">
      <div className="font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--color-cut)]">
        error · {code}
      </div>
      <div className="mt-2 text-[13px] text-[color:var(--color-text)]">{message}</div>
    </div>
  );
}

function NoVideos() {
  return (
    <div className="rounded-[10px] border border-dashed border-[color:var(--color-border)] p-10 text-center">
      <p className="text-[13px] text-[color:var(--color-muted)]">
        No <span className="font-mono">videos/&lt;slug&gt;/</span> folders found at the repo root.
      </p>
    </div>
  );
}
