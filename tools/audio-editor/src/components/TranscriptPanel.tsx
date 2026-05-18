import { useEffect, useMemo, useRef } from "react";
import type { Cut, Transcript, TranscriptWordEntry } from "../types";
import { findWordIndex, isInsideAnyCut } from "../utils/wordIndex";
import { formatTimeShort } from "../utils/format";
import { speakerColor } from "../utils/speaker";

type Props = {
  transcript: Transcript;
  currentTime: number;
  cuts: Cut[];
  onSeek: (time: number) => void;
};

const AUTOSCROLL_MIN_INTERVAL_MS = 150;
// Paragraph rule: break every N sentences (predictable rhythm), on speaker
// change, or after any silence beyond the safety pause (so a 90s monologue
// can't collapse two topics into one wall of text).
const SENTENCES_PER_PARAGRAPH = 3;
const SAFETY_PAUSE_MS = 1500;
// Trailing sentence-ender: . ! or ? optionally followed by one closing
// quote/bracket. ElevenLabs Scribe attaches punctuation to the word itself
// (e.g. "instantly.", `here."`), so a regex on `w.text` is all we need.
const SENTENCE_END_RE = /[.!?]["')\]'’”]?$/;
// Scribe v2 confident words sit near logprob -0.05 to -0.2; -0.8 catches the
// genuinely uncertain tail (mumbled words, hard names) without dimming half
// the script.
const LOWCONF_LOGPROB_THRESHOLD = -0.8;

type Paragraph = {
  speakerId: string;
  startTime: number;
  startWordIdx: number;
  endWordIdx: number;
};

export default function TranscriptPanel({
  transcript,
  currentTime,
  cuts,
  onSeek,
}: Props) {
  const words = useMemo(
    () =>
      transcript.words.filter(
        (w): w is TranscriptWordEntry => w.type === "word",
      ),
    [transcript.words],
  );

  // Pre-compute which words sit inside a cut so we don't iterate `cuts`
  // for every render of every word. Same pass also flags low-confidence words
  // so the per-word render stays O(1).
  const { cutMask, confMask } = useMemo(() => {
    const cm = cuts.length === 0 ? null : new Uint8Array(words.length);
    const conf = new Uint8Array(words.length);
    for (let i = 0; i < words.length; i++) {
      const w = words[i];
      if (cm && isInsideAnyCut((w.start + w.end) / 2, cuts)) cm[i] = 1;
      if (typeof w.logprob === "number" && w.logprob < LOWCONF_LOGPROB_THRESHOLD) {
        conf[i] = 1;
      }
    }
    return { cutMask: cm, confMask: conf };
  }, [words, cuts]);

  // Group consecutive words into paragraphs. Break when ANY of:
  //   (a) speaker_id changes
  //   (b) we've accumulated SENTENCES_PER_PARAGRAPH sentence-ending words
  //   (c) the inter-word gap exceeds SAFETY_PAUSE_MS (catches awkward
  //       silences that the sentence counter alone would merge across).
  // wordToParagraph lets the sticky "now playing" header look up the active
  // paragraph in O(1).
  const { paragraphs, wordToParagraph } = useMemo(() => {
    const paras: Paragraph[] = [];
    const map = new Uint16Array(words.length);
    let cur: Paragraph | null = null;
    let sentencesInCur = 0;
    for (let i = 0; i < words.length; i++) {
      const w = words[i];
      const speakerId = w.speaker_id || "unknown";
      const prev = i > 0 ? words[i - 1] : null;
      const gapMs = prev ? (w.start - prev.end) * 1000 : 0;
      const speakerBreak = prev && speakerId !== (prev.speaker_id || "unknown");
      const sentenceBreak = sentencesInCur >= SENTENCES_PER_PARAGRAPH;
      const pauseBreak = prev && gapMs > SAFETY_PAUSE_MS;
      if (!cur || speakerBreak || sentenceBreak || pauseBreak) {
        if (cur) paras.push(cur);
        cur = {
          speakerId,
          startTime: w.start,
          startWordIdx: i,
          endWordIdx: i,
        };
        sentencesInCur = 0;
      } else {
        cur.endWordIdx = i;
      }
      if (SENTENCE_END_RE.test(w.text)) sentencesInCur++;
      map[i] = paras.length; // index of the paragraph this word will land in
    }
    if (cur) paras.push(cur);
    return { paragraphs: paras, wordToParagraph: map };
  }, [words]);

  const activeIdx = useMemo(
    () => findWordIndex(words, currentTime),
    [words, currentTime],
  );

  const activeParagraph = useMemo(() => {
    if (activeIdx < 0) return null;
    const pi = wordToParagraph[activeIdx];
    return paragraphs[pi] ?? null;
  }, [activeIdx, wordToParagraph, paragraphs]);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const activeRef = useRef<HTMLSpanElement | null>(null);
  const lastScrollTsRef = useRef<number>(0);

  useEffect(() => {
    if (activeIdx < 0 || !activeRef.current || !containerRef.current) return;
    const now = performance.now();
    if (now - lastScrollTsRef.current < AUTOSCROLL_MIN_INTERVAL_MS) return;
    lastScrollTsRef.current = now;

    const container = containerRef.current;
    const el = activeRef.current;
    const cRect = container.getBoundingClientRect();
    const eRect = el.getBoundingClientRect();

    // Work in container-relative coords. el.offsetTop is relative to the
    // nearest positioned ancestor — which may not be `container` — so
    // deriving the target from bounding rects is the only safe way.
    const elTopInContainer = eRect.top - cRect.top + container.scrollTop;
    const elBottomInContainer = elTopInContainer + el.clientHeight;
    const margin = 60;
    const viewTop = container.scrollTop;
    const viewBottom = viewTop + container.clientHeight;
    const inView =
      elTopInContainer >= viewTop + margin &&
      elBottomInContainer <= viewBottom - margin;
    if (inView) return;

    const target = Math.max(
      0,
      elTopInContainer - container.clientHeight / 2 + el.clientHeight / 2,
    );
    container.scrollTo({ top: target, behavior: "smooth" });
  }, [activeIdx]);

  if (words.length === 0) {
    return (
      <div className="rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)] p-4 font-mono text-[11px] text-[color:var(--color-muted)]">
        no transcript words available
      </div>
    );
  }

  return (
    <div className="rounded-[10px] border border-[color:var(--color-border)] bg-[color:var(--color-panel)] flex flex-col min-h-0">
      <div className="flex items-center justify-between px-4 pt-3 pb-2 border-b border-[color:var(--color-border)]/60">
        <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--color-muted)]">
          transcript
        </span>
        <span className="font-mono text-[10px] tabular-nums text-[color:var(--color-muted-2)]">
          {activeIdx >= 0 ? `${activeIdx + 1} / ${words.length}` : `— / ${words.length}`}
        </span>
      </div>
      <div
        ref={containerRef}
        className="px-4 max-h-[50vh] overflow-y-auto text-[14px] text-[color:var(--color-text)]"
      >
        <NowPlayingHeader paragraph={activeParagraph} words={words} activeIdx={activeIdx} />
        <div className="pt-1 pb-3">
          {paragraphs.map((para) => (
            <ParagraphBlock
              key={para.startWordIdx}
              para={para}
              words={words}
              activeIdx={activeIdx}
              cutMask={cutMask}
              confMask={confMask}
              activeRef={activeRef}
              onSeek={onSeek}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function ParagraphBlock({
  para,
  words,
  activeIdx,
  cutMask,
  confMask,
  activeRef,
  onSeek,
}: {
  para: Paragraph;
  words: TranscriptWordEntry[];
  activeIdx: number;
  cutMask: Uint8Array | null;
  confMask: Uint8Array;
  activeRef: React.RefObject<HTMLSpanElement | null>;
  onSeek: (time: number) => void;
}) {
  const palette = speakerColor(para.speakerId);
  const spans: React.ReactNode[] = [];
  for (let i = para.startWordIdx; i <= para.endWordIdx; i++) {
    const w = words[i];
    const isActive = i === activeIdx;
    const inCut = cutMask?.[i] === 1;
    const isLowConf = confMask[i] === 1;
    const classes = ["transcript-word"];
    if (isActive) classes.push("transcript-word--active");
    if (inCut) classes.push("transcript-word--cut");
    if (isLowConf) classes.push("transcript-word--lowconf");
    spans.push(
      <span
        key={`${i}-${w.start}`}
        ref={isActive ? activeRef : undefined}
        onClick={() => onSeek(w.start)}
        className={classes.join(" ")}
        title={`${w.start.toFixed(2)}s`}
      >
        {w.text}
        <span> </span>
      </span>,
    );
  }
  return (
    <div className="transcript-paragraph">
      <div className="transcript-paragraph__gutter">
        {formatTimeShort(para.startTime)}
      </div>
      <div className="transcript-paragraph__body leading-[1.85]">
        <SpeakerChip speakerId={para.speakerId} palette={palette} />
        {spans}
      </div>
    </div>
  );
}

function SpeakerChip({
  speakerId,
  palette,
  compact = false,
}: {
  speakerId: string;
  palette: ReturnType<typeof speakerColor>;
  compact?: boolean;
}) {
  const style = {
    ["--speaker-bg" as string]: palette.bg,
    ["--speaker-fg" as string]: palette.fg,
  } as React.CSSProperties;
  return (
    <span className="speaker-chip" style={style} title={`Speaker: ${speakerId}`}>
      <span className="speaker-chip__avatar">{palette.initial}</span>
      {!compact && <span>{speakerId.replace(/_/g, " ")}</span>}
    </span>
  );
}

function NowPlayingHeader({
  paragraph,
  words,
  activeIdx,
}: {
  paragraph: Paragraph | null;
  words: TranscriptWordEntry[];
  activeIdx: number;
}) {
  if (!paragraph || activeIdx < 0) {
    return (
      <div className="sticky top-0 z-10 -mx-4 px-4 py-2 backdrop-blur-sm bg-[color:var(--color-panel)]/90 border-b border-[color:var(--color-border)]/60">
        <div className="font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--color-muted-2)]">
          press play
        </div>
      </div>
    );
  }
  const palette = speakerColor(paragraph.speakerId);
  // Preview the next ~7 words from the active position so the sticky strip
  // tracks the read-head, not the paragraph start.
  const previewWords: string[] = [];
  for (
    let i = activeIdx;
    i <= paragraph.endWordIdx && previewWords.length < 8;
    i++
  ) {
    previewWords.push(words[i].text);
  }
  return (
    <div className="sticky top-0 z-10 -mx-4 px-4 py-2 backdrop-blur-sm bg-[color:var(--color-panel)]/90 border-b border-[color:var(--color-border)]/60">
      <div className="flex items-center gap-2 min-w-0">
        <SpeakerChip speakerId={paragraph.speakerId} palette={palette} compact />
        <span className="font-mono text-[10px] tabular-nums text-[color:var(--color-muted-2)]">
          {formatTimeShort(paragraph.startTime)}
        </span>
        <span className="text-[12px] text-[color:var(--color-muted)] truncate">
          {previewWords.join(" ")}
        </span>
      </div>
    </div>
  );
}
