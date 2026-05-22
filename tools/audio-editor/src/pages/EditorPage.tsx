import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { apiFetch, ApiError } from "../api";
import type { Session, Cut } from "../types";
import { useCutsEditor } from "../hooks/useCutsEditor";
import Waveform from "../components/Waveform";
import type { WaveformHandle } from "../components/Waveform";
import Transport from "../components/Transport";
import RegionList from "../components/RegionList";
import SaveButton from "../components/SaveButton";
import TranscriptPanel from "../components/TranscriptPanel";
import { formatTime, parseSlugDate, slugTitle } from "../utils/format";

type Props = { slug: string };

type LoadState =
  | { kind: "loading" }
  | { kind: "ok"; session: Session }
  | { kind: "error"; code: string; message: string };

export default function EditorPage({ slug }: Props) {
  const [load, setLoad] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    apiFetch<Session>(`/api/session/${encodeURIComponent(slug)}`)
      .then((data) => {
        if (!cancelled) setLoad({ kind: "ok", session: data });
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        const err = e instanceof ApiError ? e : new ApiError("UNKNOWN", String(e), 0);
        setLoad({ kind: "error", code: err.code, message: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (load.kind === "loading") return <EditorLoading slug={slug} />;
  if (load.kind === "error") return <EditorError slug={slug} code={load.code} message={load.message} />;
  return <EditorView session={load.session} />;
}

function EditorView({ session }: { session: Session }) {
  const editor = useCutsEditor(session.slug, session.cuts);
  const waveformRef = useRef<WaveformHandle | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [zoom, setZoom] = useState(24);
  const [ready, setReady] = useState(false);
  const [pendingCutStart, setPendingCutStart] = useState<number | null>(null);
  const [skipCuts, setSkipCuts] = useState(true);

  // beforeunload guard when dirty
  useEffect(() => {
    const isDirty = editor.saveState.kind === "dirty" || editor.saveState.kind === "saving";
    if (!isDirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      // Some older browsers still require returnValue to be set non-empty
      // for the leave-confirmation prompt to appear.
      (e as { returnValue: string }).returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [editor.saveState.kind]);

  const onAddCut = useCallback(() => {
    const t = waveformRef.current?.getCurrentTime() ?? 0;
    const dur = waveformRef.current?.getDuration() ?? 0;
    if (dur <= 0) return;
    if (pendingCutStart === null) {
      setPendingCutStart(t);
      return;
    }
    const start = Math.min(pendingCutStart, t);
    const end = Math.max(pendingCutStart, t);
    if (end - start >= 0.05) editor.add(start, end);
    setPendingCutStart(null);
  }, [editor, pendingCutStart]);

  const onCancelPending = useCallback(() => setPendingCutStart(null), []);

  const onCutCreate = useCallback(
    (start: number, end: number) => {
      editor.add(start, end);
    },
    [editor],
  );

  // Keyboard shortcuts: space (play/pause), Cmd/Ctrl+S (save), Cmd/Ctrl+Z (undo),
  // Cmd/Ctrl+Shift+Z / Cmd/Ctrl+Y (redo), I (mark start), O (mark end),
  // Esc (cancel pending), \ (toggle preview-cuts).
  const saveKind = editor.saveState.kind;
  const save = editor.save;
  const undo = editor.undo;
  const redo = editor.redo;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      const inField =
        t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
      if (inField) return;

      if (e.code === "Space") {
        e.preventDefault();
        waveformRef.current?.toggle();
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (saveKind === "dirty" || saveKind === "error") {
          void save();
        }
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "z") {
        e.preventDefault();
        if (e.shiftKey) redo();
        else undo();
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "y") {
        e.preventDefault();
        redo();
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      if (e.key === "Escape") {
        setPendingCutStart(null);
        return;
      }
      if (e.key === "i" || e.key === "I") {
        e.preventDefault();
        const time = waveformRef.current?.getCurrentTime() ?? 0;
        setPendingCutStart(time);
        return;
      }
      if (e.key === "o" || e.key === "O") {
        e.preventDefault();
        onAddCut();
        return;
      }
      if (e.key === "\\") {
        e.preventDefault();
        setSkipCuts((v) => !v);
        return;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [save, saveKind, undo, redo, onAddCut]);

  const onZoom = useCallback((z: number) => {
    setZoom(z);
    waveformRef.current?.setZoom(z);
  }, []);

  // Wheel zoom inside Waveform updates px/sec directly; mirror it into our
  // slider state without re-driving setZoom (which would double-apply).
  const onWaveformZoomChange = useCallback((z: number) => setZoom(z), []);

  const onReady = useCallback(({ duration, containerWidth }: { duration: number; containerWidth: number }) => {
    setDuration(duration);
    setReady(true);
    if (duration > 0 && containerWidth > 0) {
      const fitZoom = Math.max(6, Math.min(400, Math.floor(containerWidth / duration)));
      setZoom(fitZoom);
      waveformRef.current?.setZoom(fitZoom);
    }
  }, []);

  const onJump = useCallback((cut: Cut) => {
    waveformRef.current?.seek(cut.start);
  }, []);

  const onCutChange = useCallback(
    (id: string, patch: { start: number; end: number }) => editor.update(id, patch),
    [editor],
  );

  const onTranscriptSeek = useCallback((time: number) => {
    waveformRef.current?.seek(time);
  }, []);

  const title = useMemo(() => slugTitle(session.slug), [session.slug]);
  const date = useMemo(() => parseSlugDate(session.slug), [session.slug]);
  const wordCount = useMemo(
    () => session.transcript.words.filter((w) => w.type === "word").length,
    [session.transcript.words],
  );

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-6 max-w-[1480px] mx-auto w-full flex flex-col gap-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between gap-6 flex-wrap">
        <div className="flex items-start gap-5">
          <a
            href="#/"
            className="mt-1.5 group flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--color-muted)] hover:text-[color:var(--color-accent)] transition-colors"
          >
            <svg width="11" height="11" viewBox="0 0 11 11" fill="none" className="group-hover:-translate-x-0.5 transition-transform">
              <path d="M6.5 1.5l-4 4 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            picker
          </a>
          <div>
            <h1 className="text-[22px] sm:text-[24px] font-semibold leading-tight tracking-[-0.015em] capitalize">
              {title}
            </h1>
            <div className="mt-1.5 flex items-center gap-3 font-mono text-[10.5px] text-[color:var(--color-muted-2)]">
              {date && (
                <>
                  <span className="uppercase tracking-[0.1em]">
                    {date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit" })}
                  </span>
                  <Sep />
                </>
              )}
              <span className="tabular-nums">
                <span className="text-[color:var(--color-muted)]">{wordCount}</span>
                <span className="ml-1">words</span>
              </span>
              <Sep />
              <span className="tabular-nums">
                <span className="text-[color:var(--color-muted)]">{ready ? formatTime(duration) : "—"}</span>
              </span>
            </div>
          </div>
        </div>
        <SaveButton state={editor.saveState} onSave={editor.save} />
      </div>

      <Transport
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        zoom={zoom}
        pendingCutStart={pendingCutStart}
        skipCuts={skipCuts}
        onToggle={() => waveformRef.current?.toggle()}
        onZoomChange={onZoom}
        onAddCut={onAddCut}
        onCancelPending={onCancelPending}
        onSkipCutsChange={setSkipCuts}
        regionCount={editor.cuts.length}
        canAct={ready}
      />

      {/* Main: left column stacks the waveform timeline + transcript directly
          beneath it; right column is the cut-regions sidebar. */}
      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_320px] gap-4 items-start">
        <div className="flex flex-col gap-4 min-w-0">
          <div className="relative p-3 rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)] flex flex-col gap-3 min-w-0">
            <Waveform
              ref={waveformRef}
              audioUrl={session.audioUrl}
              cuts={editor.cuts}
              pendingCutStart={pendingCutStart}
              currentTime={currentTime}
              skipCuts={skipCuts}
              onCutChange={onCutChange}
              onCutCreate={onCutCreate}
              onCutRemove={editor.remove}
              onCutChangeBegin={editor.beginUpdate}
              onCutChangeEnd={editor.commitUpdate}
              onReady={onReady}
              onPlayStateChange={setIsPlaying}
              onTimeUpdate={setCurrentTime}
              onZoomChange={onWaveformZoomChange}
            />
            {!ready && <DecodingOverlay />}
            <KeyHints />
          </div>
          <TranscriptPanel
            transcript={session.transcript}
            currentTime={currentTime}
            cuts={editor.cuts}
            onSeek={onTranscriptSeek}
          />
        </div>
        <RegionList cuts={editor.cuts} onJump={onJump} onRemove={editor.remove} />
      </div>
    </div>
  );
}

function Sep() {
  return <span className="w-px h-3 bg-[color:var(--color-border)]" aria-hidden />;
}

function DecodingOverlay() {
  return (
    <div className="absolute inset-3 flex items-center justify-center rounded-[6px] bg-[color:var(--color-bg)]/85 backdrop-blur-[2px]">
      <div className="flex items-center gap-2 font-mono text-[10.5px] uppercase tracking-[0.14em] text-[color:var(--color-muted)]">
        <span className="w-1.5 h-1.5 rounded-full bg-[color:var(--color-accent)] animate-pulse-soft" aria-hidden />
        decoding waveform…
      </div>
    </div>
  );
}

function KeyHints() {
  return (
    <div className="px-1 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[9.5px] uppercase tracking-[0.12em] text-[color:var(--color-muted-2)]">
      <Hint label="play / pause">
        <Kbd>space</Kbd>
      </Hint>
      <Hint label="save">
        <Kbd>⌘</Kbd>
        <Kbd>S</Kbd>
      </Hint>
      <Hint label="undo">
        <Kbd>⌘</Kbd>
        <Kbd>Z</Kbd>
      </Hint>
      <Hint label="redo">
        <Kbd>⌘</Kbd>
        <Kbd>⇧</Kbd>
        <Kbd>Z</Kbd>
      </Hint>
      <Hint label="mark in / out">
        <Kbd>I</Kbd>
        <Kbd>O</Kbd>
      </Hint>
      <Hint label="cancel">
        <Kbd>esc</Kbd>
      </Hint>
      <Hint label="toggle skip">
        <Kbd>\</Kbd>
      </Hint>
      <Hint label="paint cut">
        <Kbd>shift</Kbd>+drag
      </Hint>
      <Hint label="zoom">
        <Kbd>shift</Kbd>+wheel
      </Hint>
      <Hint label="scrub">drag waveform</Hint>
    </div>
  );
}

function Hint({ children, label }: { children: ReactNode; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="flex items-center gap-0.5">{children}</span>
      <span>{label}</span>
    </span>
  );
}

function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[17px] h-[16px] px-1 rounded border border-[color:var(--color-border-2)] bg-[color:var(--color-panel-2)] text-[color:var(--color-muted)] text-[9px] leading-none">
      {children}
    </kbd>
  );
}

function EditorLoading({ slug }: { slug: string }) {
  return (
    <div className="px-4 sm:px-6 lg:px-8 py-10 max-w-[1480px] mx-auto w-full">
      <div className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-[color:var(--color-muted)]">
        loading session…
      </div>
      <div className="mt-2 font-mono text-[12px] text-[color:var(--color-muted-2)] truncate">
        videos/{slug}
      </div>
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
        <div className="h-[160px] rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)]/40 animate-pulse-soft" />
        <div className="h-[160px] rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)]/40 animate-pulse-soft" style={{ animationDelay: "0.12s" }} />
      </div>
    </div>
  );
}

function EditorError({ slug, code, message }: { slug: string; code: string; message: string }) {
  return (
    <div className="px-4 sm:px-6 lg:px-8 py-10 max-w-3xl mx-auto w-full">
      <a
        href="#/"
        className="inline-flex items-center gap-1.5 font-mono text-[10.5px] uppercase tracking-[0.14em] text-[color:var(--color-muted)] hover:text-[color:var(--color-accent)] transition-colors"
      >
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
          <path d="M6.5 1.5l-4 4 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        back to picker
      </a>
      <div className="mt-6 rounded-[10px] border border-[color:var(--color-cut)]/40 bg-[color:var(--color-cut)]/5 p-6">
        <div className="font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--color-cut)]">
          could not load · {code}
        </div>
        <div className="mt-2 text-[14px]">{message}</div>
        <div className="mt-3 font-mono text-[11px] text-[color:var(--color-muted)] truncate">
          videos/{slug}
        </div>
      </div>
    </div>
  );
}
