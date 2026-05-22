import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions.esm.js";
import type { Region } from "wavesurfer.js/dist/plugins/regions.esm.js";
import TimelinePlugin from "wavesurfer.js/dist/plugins/timeline.esm.js";
import type { Cut } from "../types";
import PendingOverlay from "./PendingOverlay";

type Props = {
  audioUrl: string;
  cuts: Cut[];
  pendingCutStart: number | null;
  currentTime: number;
  skipCuts: boolean;
  onCutChange: (id: string, patch: { start: number; end: number }) => void;
  onCutCreate: (start: number, end: number) => void;
  onCutRemove: (id: string) => void;
  onCutChangeBegin: (id: string) => void;
  onCutChangeEnd: (id: string) => void;
  onReady?: (info: { duration: number; containerWidth: number }) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onTimeUpdate?: (time: number) => void;
  onZoomChange?: (pxPerSec: number) => void;
};

export type WaveformHandle = {
  play: () => void;
  pause: () => void;
  toggle: () => void;
  seek: (time: number) => void;
  setZoom: (pxPerSec: number) => void;
  getCurrentTime: () => number;
  getDuration: () => number;
};

const SVG_NS = "http://www.w3.org/2000/svg";

const REGION_BG = "rgba(255, 84, 112, 0.28)";
const REGION_BG_PENDING = "rgba(255, 84, 112, 0.12)";
const PENDING_REGION_ID = "__pending__";
const MIN_ZOOM = 6;
const MAX_ZOOM = 800;
const SHIFT_DRAG_PAINT_MIN_SECONDS = 0.05;

// Region content (the .region-chrome label + × button built in
// buildRegionContent) is appended into WaveSurfer's shadow root, which
// document-level CSS cannot reach. We inject this stylesheet into the shadow
// tree so the chrome is styled. Selectors use [part~="region"] because the
// band's part is multi-token ("region <id>"). The --color-* / --font-* custom
// properties are inherited through the shadow boundary, so they resolve here.
const REGION_SHADOW_CSS = `
[part="region-content"] {
  position: relative;
  background: transparent !important;
  padding: 0 !important;
  margin: 4px 0 0 6px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  pointer-events: auto;
}
.region-chrome__label {
  position: absolute;
  left: 0;
  bottom: calc(100% + 3px);
  z-index: 6;
  max-width: 240px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--color-cut);
  background: rgba(0, 0, 0, 0.55);
  padding: 1px 4px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  line-height: 1.4;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.12s ease;
}
.region-chrome__x {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.65);
  color: var(--color-cut);
  border: none;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: opacity 0.12s ease, transform 0.12s ease, background-color 0.12s ease, color 0.12s ease;
  pointer-events: auto;
  padding: 0;
}
[part~="region"]:hover .region-chrome__label {
  opacity: 1;
}
[part~="region"]:hover .region-chrome__x,
.region-chrome__x:focus-visible {
  opacity: 1;
  transform: scale(1);
}
.region-chrome__x:hover {
  background: var(--color-cut);
  color: var(--color-bg);
}
`;

function buildRegionContent(
  cutId: string,
  label: string,
  onRemove: (id: string) => void,
): HTMLElement {
  const root = document.createElement("div");
  root.className = "region-chrome";
  // Native tooltip backstop: the hover chip is clipped at the card's right
  // edge, so a title keeps the full reason reachable.
  root.title = label;

  const labelEl = document.createElement("span");
  labelEl.className = "region-chrome__label";
  labelEl.textContent = label;
  root.appendChild(labelEl);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "region-chrome__x";
  btn.setAttribute("aria-label", "Remove cut");
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 10 10");
  svg.setAttribute("width", "10");
  svg.setAttribute("height", "10");
  svg.setAttribute("aria-hidden", "true");
  const path = document.createElementNS(SVG_NS, "path");
  path.setAttribute("d", "M2 2 L8 8 M8 2 L2 8");
  path.setAttribute("stroke", "currentColor");
  path.setAttribute("stroke-width", "1.6");
  path.setAttribute("stroke-linecap", "round");
  svg.appendChild(path);
  btn.appendChild(svg);
  // Block the wavesurfer region from interpreting our click as a resize-drag
  // start or a click-through to the underlying waveform seek.
  btn.addEventListener("mousedown", (e) => e.stopPropagation());
  btn.addEventListener("pointerdown", (e) => e.stopPropagation());
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    e.preventDefault();
    onRemove(cutId);
  });
  root.appendChild(btn);

  return root;
}

const Waveform = forwardRef<WaveformHandle, Props>(function Waveform(
  {
    audioUrl,
    cuts,
    pendingCutStart,
    currentTime,
    skipCuts,
    onCutChange,
    onCutCreate,
    onCutRemove,
    onCutChangeBegin,
    onCutChangeEnd,
    onReady,
    onPlayStateChange,
    onTimeUpdate,
    onZoomChange,
  },
  ref,
) {
  const outerRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WaveSurfer | null>(null);
  const regionsRef = useRef<RegionsPlugin | null>(null);
  const regionMapRef = useRef<Map<string, Region>>(new Map());
  const pendingRegionRef = useRef<Region | null>(null);
  const zoomRef = useRef<number>(24);
  const dragSelectionDisposerRef = useRef<(() => void) | null>(null);
  // IDs of regions we created via addRegion(); the plugin fires
  // `region-created` synchronously inside addRegion(), so we tag the id
  // BEFORE the call to keep that event from being mistaken for a user paint.
  const ownIdsRef = useRef<Set<string>>(new Set());
  const shiftArmedRef = useRef(false);
  // Per-id flag: have we already begun a drag snapshot for this id? Cleared on
  // region-updated. `region.updatingSide` is set while a drag is in flight, so
  // we use it to distinguish user drags from programmatic setOptions.
  const openDragIdsRef = useRef<Set<string>>(new Set());

  // State that drives the sibling PendingOverlay. Updated from wavesurfer
  // scroll/zoom subscriptions + a ResizeObserver on the container.
  const [scrollLeft, setScrollLeft] = useState(0);
  const [pxPerSec, setPxPerSec] = useState(24);
  const [containerWidth, setContainerWidth] = useState(0);
  // Gates the cuts→regions sync. The regions plugin clamps a region's
  // start/end against the duration known at construction time; before "ready"
  // that duration is 0, so every region collapses to start===end===0 (a marker
  // pinned at left:0%) and never recovers. Only add regions once ready.
  const [isReady, setIsReady] = useState(false);

  const cbRef = useRef({
    onCutChange,
    onCutCreate,
    onCutRemove,
    onCutChangeBegin,
    onCutChangeEnd,
    onReady,
    onPlayStateChange,
    onTimeUpdate,
    onZoomChange,
    cuts,
    skipCuts,
  });
  useEffect(() => {
    cbRef.current = {
      onCutChange,
      onCutCreate,
      onCutRemove,
      onCutChangeBegin,
      onCutChangeEnd,
      onReady,
      onPlayStateChange,
      onTimeUpdate,
      onZoomChange,
      cuts,
      skipCuts,
    };
  });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    // Snapshot the ref's current Set so the cleanup closure works on the same
    // object that was in scope at effect-setup time (silences react-hooks/
    // exhaustive-deps and is the documented pattern for ref cleanup).
    const openDragIds = openDragIdsRef.current;

    const regions = RegionsPlugin.create();
    const timeline = TimelinePlugin.create({
      height: 18,
      insertPosition: "beforebegin",
      style: {
        fontSize: "10px",
        color: "rgba(139, 148, 163, 0.85)",
        fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace",
      },
    });

    const ws = WaveSurfer.create({
      container,
      url: audioUrl,
      height: 128,
      barWidth: 2,
      barGap: 1,
      barRadius: 1,
      waveColor: "rgba(139, 148, 163, 0.5)",
      progressColor: "rgba(110, 168, 255, 0.9)",
      cursorColor: "#6ea8ff",
      cursorWidth: 1,
      minPxPerSec: 12,
      normalize: true,
      dragToSeek: true,
      autoCenter: true,
      plugins: [regions, timeline],
    });

    wsRef.current = ws;
    regionsRef.current = regions;
    regionMapRef.current = new Map();
    pendingRegionRef.current = null;

    // Region chrome lives in WaveSurfer's shadow root, out of reach of document
    // CSS — inject its stylesheet into the shadow tree. ws.destroy() disposes
    // the shadow tree, so no explicit teardown is needed.
    const shadowRoot = ws.getWrapper().getRootNode();
    if (shadowRoot instanceof ShadowRoot) {
      const styleEl = document.createElement("style");
      styleEl.textContent = REGION_SHADOW_CSS;
      shadowRoot.appendChild(styleEl);
    }

    const subs: Array<() => void> = [];
    subs.push(
      ws.on("ready", (duration) => {
        setIsReady(true);
        cbRef.current.onReady?.({
          duration,
          containerWidth: container.clientWidth,
        });
      }),
    );
    subs.push(ws.on("play", () => cbRef.current.onPlayStateChange?.(true)));
    subs.push(ws.on("pause", () => cbRef.current.onPlayStateChange?.(false)));
    subs.push(ws.on("finish", () => cbRef.current.onPlayStateChange?.(false)));
    subs.push(
      ws.on("timeupdate", (t) => {
        cbRef.current.onTimeUpdate?.(t);
        if (!cbRef.current.skipCuts || !ws.isPlaying()) return;
        const dur = ws.getDuration();
        if (dur <= 0) return;
        // 5ms guard so we don't oscillate at the boundary
        const hit = cbRef.current.cuts.find(
          (c) => t >= c.start && t < c.end - 0.005,
        );
        if (hit) {
          const next = Math.min(hit.end + 0.001, dur - 0.001);
          if (next > t) ws.setTime(next);
        }
      }),
    );

    // Single source of truth for scroll/zoom — wavesurfer dispatches both for
    // user gestures (wheel, drag-scroll, slider) AND for autoCenter / programmatic
    // changes, so one subscription each covers every case.
    subs.push(
      ws.on("scroll", (_visibleStart, _visibleEnd, sLeft) => {
        setScrollLeft(sLeft);
      }),
    );
    subs.push(
      ws.on("zoom", (next) => {
        zoomRef.current = next;
        setPxPerSec(next);
        cbRef.current.onZoomChange?.(next);
      }),
    );

    // region-update: fires every mousemove during a user drag-resize. Use it
    // to open the drag snapshot once per drag (gated on updatingSide so
    // programmatic setOptions never trips this).
    subs.push(
      regions.on("region-update", (region) => {
        if (region.id === PENDING_REGION_ID) return;
        if (!region.updatingSide) return;
        if (openDragIdsRef.current.has(region.id)) return;
        openDragIdsRef.current.add(region.id);
        cbRef.current.onCutChangeBegin(region.id);
      }),
    );

    subs.push(
      regions.on("region-updated", (region) => {
        if (region.id === PENDING_REGION_ID) return;
        cbRef.current.onCutChange(region.id, {
          start: region.start,
          end: region.end,
        });
        if (openDragIdsRef.current.has(region.id)) {
          openDragIdsRef.current.delete(region.id);
          cbRef.current.onCutChangeEnd(region.id);
        }
      }),
    );

    // Shift+drag-to-paint: the regions plugin's drag-selection helper paints
    // a region as the user drags. We promote it to state via onCutCreate, then
    // remove the plugin's temporary region so our cuts→regions sync owns it.
    subs.push(
      regions.on("region-created", (region) => {
        // Programmatic regions are pre-tagged in ownIdsRef before addRegion()
        // is called. Consume the tag and skip — otherwise we'd treat our own
        // committed cut as a fresh user paint and feed it back into the
        // cuts-sync loop, which would spawn another addRegion, ad infinitum.
        if (ownIdsRef.current.has(region.id)) {
          ownIdsRef.current.delete(region.id);
          return;
        }
        if (region.id === PENDING_REGION_ID) return;
        // The only path that legitimately spawns an unknown region is the
        // plugin's drag-selection, which is only enabled while Shift is held.
        // If anything else fires region-created (future code, a stray call),
        // throw it away rather than risk another feedback loop.
        if (!shiftArmedRef.current) {
          region.remove();
          return;
        }
        const start = region.start;
        const end = region.end;
        region.remove();
        if (end - start >= SHIFT_DRAG_PAINT_MIN_SECONDS) {
          cbRef.current.onCutCreate(start, end);
        }
      }),
    );

    // Shift to arm drag-selection. We toggle it on/off so a plain click+drag
    // still does dragToSeek (scrub).
    const armDragSelection = () => {
      if (dragSelectionDisposerRef.current) return;
      dragSelectionDisposerRef.current = regions.enableDragSelection({
        color: REGION_BG_PENDING,
      });
      shiftArmedRef.current = true;
      container.classList.add("ws-paint-armed");
    };
    const disarmDragSelection = () => {
      dragSelectionDisposerRef.current?.();
      dragSelectionDisposerRef.current = null;
      shiftArmedRef.current = false;
      container.classList.remove("ws-paint-armed");
    };
    const onShiftDown = (e: KeyboardEvent) => {
      if (e.key === "Shift") armDragSelection();
    };
    const onShiftUp = (e: KeyboardEvent) => {
      if (e.key === "Shift") disarmDragSelection();
    };
    const onBlur = () => disarmDragSelection();
    window.addEventListener("keydown", onShiftDown);
    window.addEventListener("keyup", onShiftUp);
    window.addEventListener("blur", onBlur);

    // Shift+wheel zoom, cursor-anchored. Plain wheel keeps native scroll.
    const onWheel = (e: WheelEvent) => {
      if (!e.shiftKey) return;
      e.preventDefault();
      const dur = ws.getDuration();
      if (dur <= 0) return;

      const rect = container.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const scroll = ws.getScroll();
      const oldPxPerSec = zoomRef.current;
      const timeUnderMouse = (scroll + mouseX) / oldPxPerSec;

      const factor = Math.exp(-e.deltaY / 200);
      const next = Math.max(
        MIN_ZOOM,
        Math.min(MAX_ZOOM, oldPxPerSec * factor),
      );
      if (Math.abs(next - oldPxPerSec) < 0.01) return;
      // ws.zoom() fires the `zoom` event which our subscription mirrors into
      // zoomRef + pxPerSec state + onZoomChange callback.
      ws.zoom(next);

      // Re-anchor the time that was under the cursor.
      const newScroll = timeUnderMouse * next - mouseX;
      const maxScroll = Math.max(0, dur * next - container.clientWidth);
      ws.setScroll(Math.max(0, Math.min(maxScroll, newScroll)));
    };
    container.addEventListener("wheel", onWheel, { passive: false });

    // Track container width so the PendingOverlay can clip badge/flag to the
    // visible waveform extent across browser resizes.
    setContainerWidth(container.clientWidth);
    const resizeObs = new ResizeObserver(() => {
      setContainerWidth(container.clientWidth);
    });
    resizeObs.observe(container);

    return () => {
      window.removeEventListener("keydown", onShiftDown);
      window.removeEventListener("keyup", onShiftUp);
      window.removeEventListener("blur", onBlur);
      container.removeEventListener("wheel", onWheel);
      resizeObs.disconnect();
      disarmDragSelection();
      subs.forEach((off) => off());
      ws.destroy();
      wsRef.current = null;
      regionsRef.current = null;
      regionMapRef.current = new Map();
      pendingRegionRef.current = null;
      openDragIds.clear();
      setIsReady(false);
    };
  }, [audioUrl]);

  // Sync cuts → regions plugin (committed cuts only; pending lives separately).
  // Gated on isReady so regions are never constructed against a 0 duration
  // (which would clamp every start/end to 0 — see isReady declaration).
  useEffect(() => {
    const regions = regionsRef.current;
    const ws = wsRef.current;
    if (!regions || !ws || ws.getDuration() <= 0) return;
    const map = regionMapRef.current;
    const cutIds = new Set(cuts.map((c) => c.id));

    for (const [id, region] of map.entries()) {
      if (!cutIds.has(id)) {
        region.remove();
        map.delete(id);
      }
    }

    for (const cut of cuts) {
      const existing = map.get(cut.id);
      if (!existing) {
        // Tag before addRegion(); see ownIdsRef comment at component top.
        ownIdsRef.current.add(cut.id);
        const r = regions.addRegion({
          id: cut.id,
          start: cut.start,
          end: cut.end,
          color: REGION_BG,
          drag: true,
          resize: true,
          content: buildRegionContent(
            cut.id,
            cut.reason ?? "cut",
            (id) => cbRef.current.onCutRemove(id),
          ),
        });
        map.set(cut.id, r);
      } else if (
        Math.abs(existing.start - cut.start) > 0.001 ||
        Math.abs(existing.end - cut.end) > 0.001
      ) {
        existing.setOptions({
          start: cut.start,
          end: cut.end,
          color: REGION_BG,
        });
      }
    }
  }, [cuts, isReady]);

  // Sync the pending overlay (two-click in-progress region).
  useEffect(() => {
    const regions = regionsRef.current;
    const ws = wsRef.current;
    if (!regions || !ws) return;
    const dur = ws.getDuration();
    if (dur <= 0) return;

    if (pendingCutStart === null) {
      pendingRegionRef.current?.remove();
      pendingRegionRef.current = null;
      return;
    }

    const a = Math.max(0, Math.min(dur, pendingCutStart));
    const b = Math.max(0, Math.min(dur, currentTime));
    const start = Math.min(a, b);
    const end = Math.max(a, b);
    // Need a non-zero width or the region is invisible.
    const safeEnd = end - start < 0.01 ? Math.min(dur, start + 0.01) : end;
    const direction: "forward" | "backward" = b >= a ? "forward" : "backward";

    const applyClass = (el: HTMLElement | null) => {
      if (!el) return;
      el.classList.add("region--pending");
      el.dataset.direction = direction;
    };

    if (!pendingRegionRef.current) {
      ownIdsRef.current.add(PENDING_REGION_ID);
      pendingRegionRef.current = regions.addRegion({
        id: PENDING_REGION_ID,
        start,
        end: safeEnd,
        color: REGION_BG_PENDING,
        drag: false,
        resize: false,
      });
      applyClass(pendingRegionRef.current.element);
    } else {
      pendingRegionRef.current.setOptions({
        start,
        end: safeEnd,
        color: REGION_BG_PENDING,
      });
      applyClass(pendingRegionRef.current.element);
    }
  }, [pendingCutStart, currentTime]);

  useImperativeHandle(
    ref,
    () => ({
      play: () => wsRef.current?.play(),
      pause: () => wsRef.current?.pause(),
      toggle: () => wsRef.current?.playPause(),
      seek: (time: number) => {
        const ws = wsRef.current;
        if (!ws) return;
        const dur = ws.getDuration();
        if (dur > 0) ws.seekTo(Math.max(0, Math.min(1, time / dur)));
      },
      setZoom: (pxPerSec: number) => {
        // ws.zoom() emits the `zoom` event which our subscription mirrors
        // into zoomRef / pxPerSec state — keep that the single source.
        wsRef.current?.zoom(pxPerSec);
      },
      getCurrentTime: () => wsRef.current?.getCurrentTime() ?? 0,
      getDuration: () => wsRef.current?.getDuration() ?? 0,
    }),
    [],
  );

  return (
    <div
      ref={outerRef}
      className="relative w-full bg-[color:var(--color-bg)] rounded-[6px] border border-[color:var(--color-border)] overflow-hidden"
    >
      <div ref={containerRef} className="w-full" />
      {pendingCutStart !== null && (
        <PendingOverlay
          pendingCutStart={pendingCutStart}
          currentTime={currentTime}
          pxPerSec={pxPerSec}
          scrollLeft={scrollLeft}
          containerWidth={containerWidth}
        />
      )}
    </div>
  );
});

export default Waveform;
