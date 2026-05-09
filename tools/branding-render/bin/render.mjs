#!/usr/bin/env node
import path from 'node:path';
import { renderSvgToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <svg-path> --out <png-path> --size <pixels>

Renders an SVG file to a square PNG of the requested size with transparent
background. Used by scripts/build-logo-pngs.mjs to produce the avatar PNGs
at every size YouTube uses.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out')         { args.flags.out  = argv[++i]; }
    else if (a === '--size')   { args.flags.size = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else                       { args.positional.push(a); }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.positional.length !== 1 || !args.flags.out || !args.flags.size) usage();

const size = Number.parseInt(args.flags.size, 10);
const svgPath = path.resolve(args.positional[0]);
const outPath = path.resolve(args.flags.out);

try {
  console.log(`render: ${svgPath} -> ${outPath} (${size}x${size})`);
  await renderSvgToPng(svgPath, outPath, size);
  console.log(`done: ${outPath}`);
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
