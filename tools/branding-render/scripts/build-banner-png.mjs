#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..', '..');
const svgPath = path.join(repoRoot, 'branding', 'banner', 'banner.svg');
const outPath = path.join(repoRoot, 'branding', 'banner', 'banner-2048x1152.png');

console.log(`render: ${svgPath} -> ${outPath} (2048x1152)`);
await renderSvgToPng(svgPath, outPath, { width: 2048, height: 1152 });
console.log(`done: ${outPath}`);
