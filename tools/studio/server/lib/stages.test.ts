import { test, expect } from "bun:test";
import { computeSuggested, stageDriftsFrom } from "./stages";

/** Build a full artifact map, defaulting every rung to "missing". */
function arts(present: string[]): Record<string, string> {
  const all = [
    "research",
    "script",
    "voiceover",
    "compose",
    "review",
    "thumbnail",
    "render",
  ];
  return Object.fromEntries(
    all.map((k) => [k, present.includes(k) ? "present" : "missing"]),
  );
}

test("a present downstream artifact does not leapfrog a missing backbone rung", () => {
  // research + script done, voiceover missing, but a phantom compose present
  // (e.g. an empty `hyperframes init` scaffold). Compose is unreachable past the
  // voiceover gap → suggested stays at the furthest completed rung (script),
  // never the leapfrogged compose.
  expect(computeSuggested(arts(["research", "script", "compose"]))).toBe(
    "script",
  );
});

test("missing optional research does not block advancement to script", () => {
  // research (seo/research.json) is routinely skipped; a script with no research
  // is still at script.
  expect(computeSuggested(arts(["script"]))).toBe("script");
});

test("a fully-backboned video with no sfx/music or thumbnails still reads as render", () => {
  // review (sfx/music) and thumbnail are optional side-artifacts; their absence
  // must not halt a finished, rendered video at compose.
  expect(
    computeSuggested(arts(["script", "voiceover", "compose", "render"])),
  ).toBe("render");
});

test("the furthest present backbone rung wins (voiceover done, compose not)", () => {
  expect(computeSuggested(arts(["research", "script", "voiceover"]))).toBe(
    "voiceover",
  );
});

test("an empty folder with no artifacts is still an idea", () => {
  expect(computeSuggested(arts([]))).toBe("idea");
});

test("all artifacts present resolves to the terminal render rung", () => {
  expect(
    computeSuggested(
      arts([
        "research",
        "script",
        "voiceover",
        "compose",
        "review",
        "thumbnail",
        "render",
      ]),
    ),
  ).toBe("render");
});

test("filing a card at the in-progress stage does not drift", () => {
  // The reported case: research + script done, voiceover not yet produced, card
  // filed under voiceover. Prerequisites met, nothing downstream done → calm.
  expect(stageDriftsFrom("voiceover", arts(["research", "script"]))).toBe(false);
});

test("filing past a missing backbone prerequisite drifts", () => {
  // Filed at compose with no voiceover — impossible.
  expect(stageDriftsFrom("compose", arts(["research", "script"]))).toBe(true);
});

test("a card left behind completed downstream work drifts (stale)", () => {
  // Compose is done but the card still says voiceover → advance it.
  expect(
    stageDriftsFrom("voiceover", arts(["script", "voiceover", "compose"])),
  ).toBe(true);
});

test("a script-stage card with only the script done does not drift", () => {
  // SQLite's state: research + script present, voiceover missing, filed script.
  expect(stageDriftsFrom("script", arts(["research", "script"]))).toBe(false);
});

test("absent optional artifacts (sfx/thumbnail) do not drift a rendered card", () => {
  // Backbone complete through render; no review/thumbnail artifacts. Filed render.
  expect(
    stageDriftsFrom("render", arts(["script", "voiceover", "compose", "render"])),
  ).toBe(false);
});

test("post-render milestones are exempt from drift", () => {
  // Filed published with render not yet scanned — human-moved, never drifts.
  expect(stageDriftsFrom("published", arts(["script", "voiceover", "compose"]))).toBe(
    false,
  );
});
