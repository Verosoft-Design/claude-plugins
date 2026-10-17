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

test('strips_security_rows_without_a_leading_pipe', () => {
  const ctx = setup({ 'decision-log.md': 'Q1 | Captions only? | Yes |\nSEC3 | Route gap? | Open |\n' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 0, result.stderr);
  const log = generatedDocs(ctx.site).find((d) => d.path === 'decision-log.md').content;
  assert.doesNotMatch(log, /SEC3/);
});

test('fails_closed_on_a_security_id_left_in_the_text', () => {
  const ctx = setup({ 'decisions.md': '# Decisions\nAs SEC2 notes, the route stays open.' });
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? decisions\.md:2 .*security/);
  assert.equal(existsSync(generatedPath(ctx.site)), false);
});

test('checks_screen_notes_for_security_ids', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  writeFileSync(
    join(ctx.site, 'meters.html'),
    '<html><head><title>Meters</title></head><body><details class="review"><summary>Review</summary><ul><li>See SEC4 first.</li></ul></details></body></html>',
  );
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? screens\/meters\.md/);
});

test('fails_on_a_customer_name_in_a_screen_page_body', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  writeFileSync(
    join(ctx.site, 'assets.html'),
    '<html><head><title>Assets</title></head><body><table><tr><td>Zeta Industries</td></tr></table>' +
      '<details class="review"><summary>Review</summary><ul><li>Check the table.</li></ul></details></body></html>',
  );
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? assets\.html:1/);
  assert.equal(existsSync(generatedPath(ctx.site)), false);
});

test('fails_on_a_secret_in_a_deployed_css_file', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  writeFileSync(join(ctx.site, 'extra.css'), '/* token = abc123 */\n');
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? extra\.css:1/);
});

test('fails_on_a_customer_name_in_the_config', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  const configPath = join(ctx.site, 'site.config.json');
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  config.examples = [{ lang: 'en', text: 'What does Zeta Industries get?' }];
  writeFileSync(configPath, JSON.stringify(config));
  const result = build(ctx, 'Zeta Industries');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /REDACT\? site\.config\.json/);
  assert.equal(existsSync(join(ctx.site, 'ask.html')), false);
});

test('generated_files_are_gitignored', () => {
  const ctx = setup({ 'README.md': '# Readme' });
  spawnSync('git', ['init', '-q'], { cwd: ctx.site });
  for (const path of ['api/_knowledge.generated.ts', 'api/_site.generated.ts', 'ask.html', 'index.html']) {
    const r = spawnSync('git', ['check-ignore', '-q', path], { cwd: ctx.site });
    assert.equal(r.status, 0, `${path} is not ignored`);
  }
  const kept = spawnSync('git', ['check-ignore', '-q', 'ask.template.html'], { cwd: ctx.site });
  assert.equal(kept.status, 1, 'ask.template.html must stay tracked');
});
