import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as lucide from 'lucide';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(__dirname, '..', 'icons', 'lucide.json');

// Topics that recur in technical-explainer videos. Add to this list and
// re-run `npm run sync-icons` to expand the cache. Names must match Lucide's
// camelCase exports (Database, FileText, etc., not 'database' / 'file-text').
const TOPICS = [
  'Database', 'Lock', 'Key', 'Code', 'FileText', 'Terminal', 'Cpu',
  'Network', 'Server', 'HardDrive', 'Cloud', 'Globe', 'Shield', 'Layers',
  'GitBranch', 'GitMerge', 'Hash', 'Binary', 'Activity', 'Zap',
  'Dice5', 'KeyRound', 'Fingerprint', 'Eye', 'EyeOff', 'Mouse', 'Keyboard',
  'Image', 'Type', 'Brackets', 'FunctionSquare', 'Workflow',
];

const out = {};
for (const name of TOPICS) {
  const node = lucide[name];
  if (!node) {
    console.warn(`skip: lucide export "${name}" not found`);
    continue;
  }
  // lucide exports each icon as [tag, attrs, children] — render to SVG body
  // (without the outer <svg> tag, so the skill can compose viewBox/styles).
  // Lucide icons are canonically 24x24, so viewBox is fixed.
  const [, , children] = node;
  const body = children.map(([tag, attrs]) => {
    const a = Object.entries(attrs).map(([k, v]) => `${k}="${v}"`).join(' ');
    return `<${tag} ${a} />`;
  }).join('');
  out[name] = { body, viewBox: '0 0 24 24' };
}

writeFileSync(OUT, JSON.stringify(out, null, 2) + '\n');
console.log(`wrote ${Object.keys(out).length} icons to ${OUT}`);
