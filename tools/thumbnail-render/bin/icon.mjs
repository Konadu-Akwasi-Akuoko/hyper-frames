#!/usr/bin/env node
import { getIconifyBody } from '../src/iconify.mjs';

const name = process.argv[2];
if (!name) {
  console.error('Usage: icon.mjs <set>:<icon-name>\nExample: icon.mjs ph:cursor-click');
  process.exit(2);
}

try {
  const body = await getIconifyBody(name);
  process.stdout.write(body);
  process.stdout.write('\n');
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
