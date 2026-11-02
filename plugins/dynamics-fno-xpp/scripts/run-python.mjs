#!/usr/bin/env node
// Runs one of this plugin's Python scripts with whatever Python the machine has.
//
// Hooks use exec form ("command": "node"), because on Windows exec form needs a real
// .exe and there is no python3.exe on an F&O dev VM (only py.exe and python.exe).
// Node is already required by both MCP servers this plugin starts.
//
// Usage: node run-python.mjs <script.py> [args...]
// A relative script path resolves next to this file. stdin, stdout and stderr pass through.
// If no Python is found, it says so on stderr and exits 0, so a hook never breaks a session.

import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const [script, ...rest] = process.argv.slice(2);
if (!script) {
  process.stderr.write('usage: node run-python.mjs <script.py> [args...]\n');
  process.exit(2);
}
const target = isAbsolute(script) ? script : join(here, script);

// FNO_PYTHON overrides the search, e.g. FNO_PYTHON=C:\Python313\python.exe
const candidates = [];
if (process.env.FNO_PYTHON) candidates.push([process.env.FNO_PYTHON]);
if (process.platform === 'win32') candidates.push(['py', '-3'], ['python'], ['python3']);
else candidates.push(['python3'], ['python']);

// A hook payload arrives on stdin. Read it once, then hand it to the interpreter that runs.
let input = Buffer.alloc(0);
if (!process.stdin.isTTY) {
  try {
    input = readFileSync(0);
  } catch {
    // no stdin (closed or not readable): run with empty input
  }
}

for (const [exe, ...pre] of candidates) {
  // Windows has python.exe/python3.exe "App Execution Alias" stubs that only open the
  // Microsoft Store. They fail this probe, so they are skipped.
  const probe = spawnSync(exe, [...pre, '-c', 'import sys; print(sys.version_info[0])'], {
    encoding: 'utf8',
    windowsHide: true,
    timeout: 10000,
  });
  if (probe.error || probe.status !== 0 || probe.stdout.trim() !== '3') continue;
  const run = spawnSync(exe, [...pre, '-X', 'utf8', target, ...rest], {
    input,
    stdio: ['pipe', 'inherit', 'inherit'],
    windowsHide: true,
  });
  process.exit(run.status ?? 0);
}

process.stderr.write(
  'dynamics-fno-xpp: no Python 3 found (tried ' +
    candidates.map((c) => c.join(' ')).join(', ') +
    '). Install Python 3 or set FNO_PYTHON to its python executable.\n',
);
process.exit(0);
