import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEMPLATE = join(
  dirname(fileURLToPath(import.meta.url)),
  '..', '..', 'skills', 'feature-lifecycle', 'templates', 'review-site',
);

// A spec folder with the template copied into spec/review-site/, as the design step does.
function setup(files) {
  const root = mkdtempSync(join(tmpdir(), 'review-site-'));
  const spec = join(root, 'spec');
  const site = join(spec, 'review-site');
  cpSync(TEMPLATE, site, { recursive: true });
  for (const [path, content] of Object.entries(files)) {
    mkdirSync(dirname(join(spec, path)), { recursive: true });
    writeFileSync(join(spec, path), content);
  }
  const home = join(root, 'home');
  mkdirSync(home);
  return { site, home };
}

function build({ site, home }, names) {
  const env = { PATH: process.env.PATH, HOME: home };
  if (names !== undefined) env.VSD_CUSTOMER_NAMES = names;
  return spawnSync(process.execPath, ['scripts/build-knowledge.mjs'], { cwd: site, env, encoding: 'utf8' });
}

function generatedDocs(site) {
  const text = readFileSync(join(site, 'api', '_knowledge.generated.ts'), 'utf8');
  return JSON.parse(text.slice(text.indexOf('= ') + 2, text.lastIndexOf(';')));
}

const generatedPath = (site) => join(site, 'api', '_knowledge.generated.ts');

test('collects_every_markdown_file_recursively', () => {
  const ctx = setup({ 'README.md': '# Readme', 'decisions.md': '# Decisions', 'notes/deep.md': '# Deep' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 0, result.stderr);
  const paths = generatedDocs(ctx.site).map((d) => d.path).sort();
  assert.deepEqual(paths, ['README.md', 'decisions.md', 'notes/deep.md']);
});

test('skips_the_review_site_folder', () => {
  const ctx = setup({ 'README.md': '# Readme', 'review-site/notes.md': '# Not knowledge' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 0, result.stderr);
  const paths = generatedDocs(ctx.site).map((d) => d.path);
  assert.ok(!paths.some((p) => p.startsWith('review-site/')), paths.join(','));
});

test('turns_screen_review_notes_into_docs', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  writeFileSync(
    join(ctx.site, 'forecast.html'),
    '<html><body><details class="review"><summary>What to review</summary><ul><li>Check the <b>due</b> column.</li></ul></details></body></html>',
  );
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 0, result.stderr);
  const screen = generatedDocs(ctx.site).find((d) => d.path === 'screens/forecast.md');
  assert.ok(screen, 'screens/forecast.md missing');
  assert.match(screen.content, /1\. Check the \*\*due\*\* column\./);
});

test('strips_security_rows_and_internal_sections', () => {
  const ctx = setup({
    'decision-log.md': [
      '| # | Question | Recommendation | Answer |',
      '| --- | --- | --- | --- |',
      '| Q1 | Captions only? | Yes | **Yes** |',
      '| SEC1 | Route gap? | Fix later | Open |',
      '',
      '<!-- internal -->',
      'Internal only: the unfixed gap.',
      '<!-- /internal -->',
      'After the internal part.',
    ].join('\n'),
  });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 0, result.stderr);
  const log = generatedDocs(ctx.site).find((d) => d.path === 'decision-log.md').content;
  assert.match(log, /\| Q1 \|/);
  assert.doesNotMatch(log, /SEC1/);
  assert.doesNotMatch(log, /unfixed gap/);
  assert.match(log, /After the internal part\./);
});

test('fails_on_a_customer_name', () => {
  const ctx = setup({ 'decisions.md': '# Decisions\nAgreed with Zeta Industries.' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? decisions\.md:2/);
  assert.equal(existsSync(generatedPath(ctx.site)), false);
});

test('fails_closed_without_a_names_list', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  const result = build(ctx, undefined);
  assert.equal(result.status, 2);
  assert.equal(existsSync(generatedPath(ctx.site)), false);
});

test('fails_on_a_secret', () => {
  const ctx = setup({ 'README.md': '# Readme\napi_key = abc123' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.equal(existsSync(generatedPath(ctx.site)), false);
});

test('fails_clearly_on_a_missing_folder', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  const configPath = join(ctx.site, 'site.config.json');
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  config.guideDirs = ['../no-such-guide'];
  writeFileSync(configPath, JSON.stringify(config));
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /folder not found: .*no-such-guide/);
  assert.doesNotMatch(result.stderr, /at .*build-knowledge\.mjs:\d+/);
});
