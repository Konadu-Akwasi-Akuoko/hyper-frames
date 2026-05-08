#!/usr/bin/env node
import path from 'node:path';
import { existsSync, statSync } from 'node:fs';
import { renderHtmlToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <html-path> --out <png-path>
  render.mjs <round-dir> --variants --out-dir <video-folder>

Single-file mode renders one HTML to one PNG at 1280x720.
Variants mode renders a.html, b.html, c.html from <round-dir>
to thumbnail-a.png, thumbnail-b.png, thumbnail-c.png in <video-folder>.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--variants') { args.flags.variants = true; }
    else if (a === '--out')      { args.flags.out      = argv[++i]; }
    else if (a === '--out-dir')  { args.flags.outDir   = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else { args.positional.push(a); }
  }
  return args;
}

async function renderSingle(htmlPath, outPath) {
  const absHtml = path.resolve(htmlPath);
  const absOut = path.resolve(outPath);
  console.log(`render: ${absHtml} -> ${absOut}`);
  await renderHtmlToPng(absHtml, absOut);
  console.log(`done: ${absOut}`);
}

async function renderVariants(roundDir, outDir) {
  const absRound = path.resolve(roundDir);
  const absOut = path.resolve(outDir);
  if (!existsSync(absRound) || !statSync(absRound).isDirectory()) {
    throw new Error(`round-dir not found or not a directory: ${absRound}`);
  }
  if (!existsSync(absOut) || !statSync(absOut).isDirectory()) {
    throw new Error(`out-dir not found or not a directory: ${absOut}`);
  }
  for (const letter of ['a', 'b', 'c']) {
    const html = path.join(absRound, `${letter}.html`);
    if (!existsSync(html)) {
      throw new Error(`missing variant HTML: ${html}`);
    }
    const png = path.join(absOut, `thumbnail-${letter}.png`);
    console.log(`render: ${html} -> ${png}`);
    await renderHtmlToPng(html, png);
  }
  console.log(`done: thumbnail-{a,b,c}.png in ${absOut}`);
}

const args = parseArgs(process.argv.slice(2));

try {
  if (args.flags.variants) {
    if (args.positional.length !== 1 || !args.flags.outDir) usage();
    await renderVariants(args.positional[0], args.flags.outDir);
  } else {
    if (args.positional.length !== 1 || !args.flags.out) usage();
    await renderSingle(args.positional[0], args.flags.out);
  }
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
