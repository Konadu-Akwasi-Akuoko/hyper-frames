import { test, expect } from "bun:test";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { scanVideos } from "./scan";

test("scan infers the suggested stage from real artifacts on disk", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "studio-scan-"));
  try {
    // alpha: only script.md → suggested = script
    const a = path.join(root, "alpha-2026-01-01");
    await mkdir(a, { recursive: true });
    await writeFile(path.join(a, "script.md"), "# Alpha\n");

    // beta: script + full voiceover trio → suggested = voiceover, partial→present
    const b = path.join(root, "beta-2026-02-02");
    await mkdir(path.join(b, "audio"), { recursive: true });
    await writeFile(path.join(b, "script.md"), "x");
    await writeFile(path.join(b, "audio", "voiceover.mp3"), "x");
    await writeFile(path.join(b, "transcript.json"), "{}");
    await writeFile(path.join(b, "narration-map.json"), "{}");

    // gamma: mp3+transcript but no narration-map → voiceover partial, suggested = script
    const g = path.join(root, "gamma-2026-03-03");
    await mkdir(path.join(g, "audio"), { recursive: true });
    await writeFile(path.join(g, "script.md"), "x");
    await writeFile(path.join(g, "audio", "voiceover.mp3"), "x");
    await writeFile(path.join(g, "transcript.json"), "{}");

    // not-a-video: no date suffix → ignored
    await mkdir(path.join(root, "scratch"), { recursive: true });

    const res = await scanVideos(root);
    const by = Object.fromEntries(res.map((v) => [v.slug, v]));

    expect(res.length).toBe(3);
    expect(by.alpha.suggestedStage).toBe("script");
    expect(by.alpha.artifacts.script).toBe("present");
    expect(by.alpha.artifacts.voiceover).toBe("missing");
    expect(by.beta.suggestedStage).toBe("voiceover");
    expect(by.beta.artifacts.voiceover).toBe("present");
    expect(by.gamma.artifacts.voiceover).toBe("partial");
    expect(by.gamma.suggestedStage).toBe("script");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("an empty `hyperframes init` scaffold does not count as a finished compose", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "studio-scaffold-"));
  try {
    // research + script + full voiceover trio, plus a bare init scaffold whose
    // only clip markers live inside the placeholder comment.
    const d = path.join(root, "scaffold-2026-04-04");
    await mkdir(path.join(d, "audio"), { recursive: true });
    await mkdir(path.join(d, "seo"), { recursive: true });
    await writeFile(path.join(d, "seo", "research.json"), "{}");
    await writeFile(path.join(d, "script.md"), "x");
    await writeFile(
      path.join(d, "index.html"),
      `<!doctype html><html><body>
        <div id="root" data-composition-id="main" data-start="0" data-duration="10">
          <!-- Add your clips here. Example:
            <div id="title" class="clip" data-start="0" data-duration="5">Hello</div>
          -->
        </div>
      </body></html>`,
    );

    const res = await scanVideos(root);
    const v = res[0];
    expect(v.artifacts.compose).toBe("partial");
    // the absurd "compose" suggestion is gone — suggested is the furthest
    // completed rung (script), never the leapfrogged scaffold.
    expect(v.suggestedStage).toBe("script");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("an index.html with a real mounted clip counts as compose present", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "studio-real-compose-"));
  try {
    const d = path.join(root, "real-2026-05-05");
    await mkdir(path.join(d, "audio"), { recursive: true });
    await writeFile(path.join(d, "script.md"), "x");
    await writeFile(path.join(d, "audio", "voiceover.mp3"), "x");
    await writeFile(path.join(d, "transcript.json"), "{}");
    await writeFile(path.join(d, "narration-map.json"), "{}");
    await writeFile(
      path.join(d, "index.html"),
      `<!doctype html><html><body>
        <div id="root" data-composition-id="main" data-start="0" data-duration="30">
          <div id="s1" class="clip" data-start="0" data-duration="5" data-track-index="1">Real scene</div>
        </div>
      </body></html>`,
    );

    const res = await scanVideos(root);
    expect(res[0].artifacts.compose).toBe("present");
    expect(res[0].suggestedStage).toBe("compose");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("scan returns [] for a missing root", async () => {
  const res = await scanVideos("/nonexistent/studio/videos/xyz");
  expect(res).toEqual([]);
});
