#!/usr/bin/env node
// Starts one of this plugin's MCP servers over stdio, the same way on Windows and Unix.
//
// A plugin .mcp.json can't use npx or npm .cmd shims on Windows (they need a shell), and
// the d365fo-mcp-server is often a git checkout rather than an npm install. This launcher
// finds the server's JavaScript entry point and runs it with this same node.
//
//   node mcp-launch.mjs d365fo       d365fo-mcp-server (MIT, github.com/dynamics365ninja/d365fo-mcp-server)
//   node mcp-launch.mjs playwright   @playwright/mcp
//
// Settings (environment variables, all optional):
//   D365FO_MCP_ENTRY    path to the server's dist/index.js (a git checkout). Default: global npm d365fo-mcp.
//   D365FO_CONFIG       its config file (passed through). MCP_SERVER_MODE defaults to "full".
//   FNO_PLAYWRIGHT_ARGS extra @playwright/mcp arguments, e.g. "--ignore-https-errors --browser msedge".
//                       --ignore-https-errors is never added on its own: set it only for a dev VM
//                       whose certificate you know has expired.

import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const which = process.argv[2];

function globalNodeModules() {
  const roots = [];
  const prefix = process.env.NPM_CONFIG_PREFIX || process.env.npm_config_prefix;
  if (prefix) roots.push(process.platform === 'win32' ? join(prefix, 'node_modules') : join(prefix, 'lib', 'node_modules'));
  const npm = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32', windowsHide: true, timeout: 15000 });
  if (npm.status === 0 && npm.stdout.trim()) roots.push(npm.stdout.trim());
  return [...new Set(roots)];
}

function firstExisting(paths) {
  return paths.find((p) => p && existsSync(p));
}

function fail(message) {
  process.stderr.write(`dynamics-fno-xpp (${which}): ${message}\n`);
  process.exit(1);
}

let entry;
let args = [];
const env = { ...process.env };

if (which === 'd365fo') {
  entry = firstExisting([
    process.env.D365FO_MCP_ENTRY,
    ...globalNodeModules().map((r) => join(r, 'd365fo-mcp', 'dist', 'index.js')),
  ]);
  if (!entry) {
    fail('d365fo-mcp-server not found. Install it on the F&O dev VM (`npm i -g d365fo-mcp`, then ' +
      '`d365fo-mcp setup`), or set D365FO_MCP_ENTRY to dist/index.js of a git checkout. ' +
      'See the fno-vm-setup skill. Off the VM this server is not needed.');
  }
  env.MCP_SERVER_MODE = env.MCP_SERVER_MODE || 'full';
} else if (which === 'playwright') {
  entry = firstExisting(globalNodeModules().map((r) => join(r, '@playwright', 'mcp', 'cli.js')));
  if (!entry) fail('@playwright/mcp not found. Install it with `npm i -g @playwright/mcp` (see the fno-vm-setup skill).');
  args = (process.env.FNO_PLAYWRIGHT_ARGS || '').split(/\s+/).filter(Boolean);
} else {
  fail('usage: node mcp-launch.mjs d365fo|playwright');
}

const child = spawn(process.execPath, [entry, ...args], { stdio: 'inherit', env, windowsHide: true });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
child.on('exit', (code, signal) => process.exit(code ?? (signal ? 1 : 0)));
