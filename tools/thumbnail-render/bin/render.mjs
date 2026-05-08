#!/usr/bin/env node
import path from 'node:path';
import { existsSync, statSync } from 'node:fs';
import { renderHtmlToPng, ORIENTATION_DIMS } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <html-path> --out <png-path> [--orientation horizontal|vertical]
  render.mjs <round-dir> --variants --out-dir <video-folder> [--orientation horizontal|vertical]

Single-file mode renders one HTML to one PNG at the orientation's
dimensions (horizontal=1280x720, vertical=1080x1920).

Variants mode renders a.html, b.html, c.html from <round-dir> to:
  - thumbnail-{a,b,c}.png            (horizontal, default)
  - thumbnail-vertical-{a,b,c}.png   (vertical)
in <video-folder>.

In variants mode, the round-dir suffix and the --orientation flag must
agree: a directory ending in '-vertical' requires --orientation vertical,
and any other directory requires --orientation horizontal.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: { orientation: 'horizontal' } };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--variants')        { args.flags.variants    = true; }
    else if (a === '--out')        { args.flags.out         = argv[++i]; }
    else if (a === '--out-dir')    { args.flags.outDir      = argv[++i]; }
    else if (a === '--orientation'){ args.flags.orientation = argv[++i]; }
    else if (a.startsWith('--'))   { console.error(`Unknown flag: ${a}`); usage(); }
    else                           { args.positional.push(a); }
  }
  if (!ORIENTATION_DIMS[args.flags.orientation]) {
    console.error(`Unknown orientation: ${args.flags.orientation} (expected one of: ${Object.keys(ORIENTATION_DIMS).join(', ')})`);
    usage();
  }
  return args;
}

async function renderSingle(htmlPath, outPath, orientation) {
  const absHtml = path.resolve(htmlPath);
  const absOut = path.resolve(outPath);
  console.log(`render (${orientation}): ${absHtml} -> ${absOut}`);
  await renderHtmlToPng(absHtml, absOut, orientation);
  console.log(`done: ${absOut}`);
}

async function renderVariants(roundDir, outDir, orientation) {
  const absRound = path.resolve(roundDir);
  const absOut = path.resolve(outDir);
  if (!existsSync(absRound) || !statSync(absRound).isDirectory()) {
    throw new Error(`round-dir not found or not a directory: ${absRound}`);
  }
  if (!existsSync(absOut) || !statSync(absOut).isDirectory()) {
    throw new Error(`out-dir not found or not a directory: ${absOut}`);
  }
  const dirIsVertical = absRound.endsWith('-vertical');
  if (dirIsVertical !== (orientation === 'vertical')) {
    throw new Error(`round-dir suffix and --orientation disagree: roundDir=${absRound} orientation=${orientation}. Vertical rounds must end in '-vertical' and pass --orientation vertical.`);
  }
  const prefix = orientation === 'vertical' ? 'thumbnail-vertical-' : 'thumbnail-';
  for (const letter of ['a', 'b', 'c']) {
    const html = path.join(absRound, `${letter}.html`);
    if (!existsSync(html)) {
      throw new Error(`missing variant HTML: ${html}`);
    }
    const png = path.join(absOut, `${prefix}${letter}.png`);
    console.log(`render (${orientation}): ${html} -> ${png}`);
    await renderHtmlToPng(html, png, orientation);
  }
  console.log(`done: ${prefix}{a,b,c}.png in ${absOut}`);
}

const args = parseArgs(process.argv.slice(2));

try {
  if (args.flags.variants) {
    if (args.positional.length !== 1 || !args.flags.outDir) usage();
    await renderVariants(args.positional[0], args.flags.outDir, args.flags.orientation);
  } else {
    if (args.positional.length !== 1 || !args.flags.out) usage();
    await renderSingle(args.positional[0], args.flags.out, args.flags.orientation);
  }
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
