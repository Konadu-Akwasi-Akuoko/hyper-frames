#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..', '..');
const svgPath = path.join(repoRoot, 'branding', 'logo', 'iceberg.svg');
const outDir = path.join(repoRoot, 'branding', 'logo');

const SIZES = [800, 176, 96, 48, 24];

for (const size of SIZES) {
  const out = path.join(outDir, `iceberg-${size}.png`);
  console.log(`render: ${svgPath} -> ${out} (${size}x${size})`);
  await renderSvgToPng(svgPath, out, size);
}
console.log(`done: ${SIZES.length} PNGs in ${outDir}`);
