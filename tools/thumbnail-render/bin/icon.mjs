#!/usr/bin/env node
import { getIconifyIcon } from '../src/iconify.mjs';

const name = process.argv[2];
if (!name) {
  console.error('Usage: icon.mjs <set>:<icon-name>\nExample: icon.mjs ph:cursor-click\nPrints JSON: {"body": "...", "viewBox": "..."}');
  process.exit(2);
}

try {
  const icon = await getIconifyIcon(name);
  process.stdout.write(JSON.stringify(icon));
  process.stdout.write('\n');
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
