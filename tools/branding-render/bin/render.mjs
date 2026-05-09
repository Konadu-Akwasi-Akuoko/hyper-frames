#!/usr/bin/env node
import path from 'node:path';
import { renderSvgToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <svg-path> --out <png-path> --size <pixels>
  render.mjs <svg-path> --out <png-path> --width <px> --height <px>

Renders an SVG file to a PNG at the requested size with transparent
background. --size is shorthand for a square output. Used by the build
scripts under scripts/ to produce branding artifacts.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out')          { args.flags.out    = argv[++i]; }
    else if (a === '--size')    { args.flags.size   = argv[++i]; }
    else if (a === '--width')   { args.flags.width  = argv[++i]; }
    else if (a === '--height')  { args.flags.height = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else                        { args.positional.push(a); }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.positional.length !== 1 || !args.flags.out) usage();

let dims;
if (args.flags.size) {
  dims = Number.parseInt(args.flags.size, 10);
} else if (args.flags.width && args.flags.height) {
  dims = {
    width: Number.parseInt(args.flags.width, 10),
    height: Number.parseInt(args.flags.height, 10),
  };
} else {
  usage();
}

const svgPath = path.resolve(args.positional[0]);
const outPath = path.resolve(args.flags.out);

try {
  const dimsLabel = typeof dims === 'number' ? `${dims}x${dims}` : `${dims.width}x${dims.height}`;
  console.log(`render: ${svgPath} -> ${outPath} (${dimsLabel})`);
  await renderSvgToPng(svgPath, outPath, dims);
  console.log(`done: ${outPath}`);
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
