# Feature lifecycle plugin: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

- **Goal:** ship `vsd-feature-lifecycle`, a plugin whose entry skill sizes Verosoft dev work (bug, feature or major), runs the steps for that size, and stops at named gates. It ships in both marketplaces and is wired into mobi and tag-bc.
- **Architecture:** One model-invocable entry skill, `feature-lifecycle`. It holds the sizing rules and the gates, and it loads one step file at a time from its own folder (`steps/*.md`, `templates/`), so the always-on cost is a single description.
  - A second skill, `lifecycle-release`, is only run by hand.
  - The helper scripts use only the Python standard library.
  - Every file inside `skills/` refers to other files by paths relative to the skill folder, never `${CLAUDE_PLUGIN_ROOT}`. The same folders then copy unchanged into Cursor and Codex.
  - Behavior is tested with a `claude plugin eval` suite. The scripts are tested with `unittest` and `node --test`.
- **Tech stack:**
  - Claude Code plugin format (`plugin.json`, `SKILL.md`);
  - Python 3 standard library (3.14 is installed; no pytest);
  - Node 23 for the review-site template (`ai@7.0.126`, as in PM's site);
  - `claude plugin eval`, `claude plugin validate`, and `gh`.
- **Spec:** `docs/superpowers/specs/2026-10-16-feature-lifecycle-design.md`. Read it with this plan. Its sections are the source text for the skill and step files.

## Global constraints

- Plugin name `vsd-feature-lifecycle`, version `0.1.0`, author `Alexis Turgeon`, license MIT. The canonical copy is `plugins/vsd-feature-lifecycle/` in this repo.
- Approvers: **Stéphane Levert** (Linear `@stephane.levert`) and **Alexis Turgeon** (Linear `@alexisturgeon`). Nobody else approves a gate.
- Gates: `G1 Size`, `G2 Spec`, `G3 Design`, `G4 Customer data`, `G5 Merge`, `G6 Release`. Hand-offs: "needs a mockup" and "needs a BC test run".
- Sizes: `Bug`, `Feature`, `Major`. The escalation list is copied verbatim from the spec's "When the size goes up".
- Paths:
  - feature spec: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
  - major spec folder: `docs/superpowers/specs/YYYY-MM-DD-<topic>/`
  - plan: `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`
  - release-notes entry: `docs/release-notes/unreleased/<ISSUE-ID>.md`
  - released notes: `docs/release-notes/<version>/`
- Release-notes frontmatter values:
  - `product`: `tag` | `mobi`
  - `type`: `feature` | `change` | `fix`
  - `audience`: `users` | `admins` | `consultants`
  - `issue`: a Linear ID
  - The body is one to three sentences and never names a customer.
- Always-on cost for the whole plugin: **at most 2,000 tokens**. Measure it with `claude --plugin-dir plugins/vsd-feature-lifecycle plugin details vsd-feature-lifecycle`.
- **This repo is public.** No customer name, email address or secret goes into any committed file, test fixture, eval or template. Fixtures use invented names (`Acme Corp`, `Zeta Industries`).
- No `dependencies` in `plugin.json`. Companion plugins are soft: the skill names what's missing and carries on.
- Every change to `plugins/vsd-feature-lifecycle/` that ships bumps `version` in `plugin.json`, because installs are pinned to the version.
- Commit with explicit paths. Each commit ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review focus

These are inputs no task's happy path covers, but people will hit them. Each one has a test in the task named.

1. **Customer names reaching this public repo** through templates modeled on PM's files or the PM site's redaction list. That redaction list has real names hard-coded. Expected: none are committed. Covered by Task 7, where names come only from a local list, and by Task 10's full-plugin scan.
2. **An issue too vague to size.** Expected: the skill asks for what's missing and doesn't pick a size and start. Covered by the `vague-issue` eval (Task 4).
3. **A fresh session resuming after an approval.** Expected: it continues at the next step from the status block, without re-asking or restarting. Covered by the `resume-after-approval` eval (Task 4).
4. **Someone who isn't an approver saying "approved".** Expected: the skill posts the Linear comment and stops. Covered by the `teammate-cannot-approve` eval (Task 4).
5. **Hand-written release-notes entries with small mistakes,** such as a lowercase ID, a file name that doesn't match the issue, four sentences, or product `trax`. Expected: `validate` names each problem. Covered by Task 3's tests.

---

### Task 1: Rescue the PM review site

The PM design review site exists only in a temporary folder. Copy it to a durable local folder before anything else. It contains real customer names (in `scripts/build-knowledge.mjs`), so it stays local and is never pushed.

**Files:**
- Create: `~/Source/mobi-pm-design-review/` (a local git repo, never pushed).

- [ ] **Step 1:** Copy it.
  - Run: `rsync -a --exclude node_modules --exclude .vercel /private/tmp/claude-501/-Users-alexisturgeon-Source-mobi/5a471876-344d-4999-8eb3-ed9335f216ed/scratchpad/pm-design-site/ ~/Source/mobi-pm-design-review/`
  - Expected: the folder has `api/ask.ts`, `ask.html`, `ask-fab.css`, `scripts/build-knowledge.mjs`, `index.html`, `vercel.json` and 13 screen `.html` files.
- [ ] **Step 2:** Make it a local repo and commit it.
  - Run: `cd ~/Source/mobi-pm-design-review && git init -q && git add -A && git commit -qm "PM design review site, rescued from the PM session scratchpad (local only; contains customer names)"`
  - Expected: one commit. Don't add a remote.

### Task 2: Plugin scaffold and the customer-name check

**Files:**
- Create: `plugins/vsd-feature-lifecycle/.claude-plugin/plugin.json`
- Create: `plugins/vsd-feature-lifecycle/LICENSE` (copy of `plugins/business-central-al/LICENSE`)
- Create: `plugins/vsd-feature-lifecycle/CHANGELOG.md` (a `## 0.1.0 — <date>` entry)
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/scripts/check_customer_names.py`
- Create: `plugins/vsd-feature-lifecycle/tests/test_check_customer_names.py`
- Modify: `.claude-plugin/marketplace.json` (add the plugin entry: `"source": "./plugins/vsd-feature-lifecycle"`, `"category": "development"`)
- Modify: `.gitignore` (add `plugins/*/evals/results/`)
- Create, local only: `~/.config/verosoft/customer-names.txt`. One name per line, taken from the `banned` list in `~/Source/mobi-pm-design-review/scripts/build-knowledge.mjs`: the customer names and their short forms, not the vendor or secret patterns. Never committed.

**Interfaces:**
- **Produces the CLI** `python3 check_customer_names.py [--names-file PATH] [--base REF] [PATH ...]`:
  - With `--base REF`, it scans the lines added in `git diff --unified=0 REF...HEAD`, plus every listed `PATH`.
  - Exit `0`: no hits.
  - Exit `1`: hits, printed one per line as `PATH:LINE: NAME`; diff hits use `diff:FILE:LINE: NAME`.
  - Exit `2`: no names list found. It prints `no customer-name list (set VSD_CUSTOMER_NAMES or create ~/.config/verosoft/customer-names.txt)` to stderr.
- **Produces the functions:**
  - `load_names(names_file: str | None, env: Mapping[str, str], home: Path) -> list[str]`. Source order:
    1. `--names-file`;
    2. `env["VSD_CUSTOMER_NAMES"]`, split on commas and newlines;
    3. `home/".config/verosoft/customer-names.txt"`.

    It strips whitespace and drops blank lines and `#` comments.
  - `find_hits(text: str, names: list[str]) -> list[tuple[int, str]]`: case-insensitive. A name doesn't match inside a longer alphanumeric word. It returns the 1-based line number and the name as listed.

- [ ] **Step 1: Write the failing tests** in `tests/test_check_customer_names.py`. Use `unittest`, import the script by path with `importlib.util.spec_from_file_location`, and use temp dirs for files and git repos.
  - `test_finds_name_case_insensitive`: `find_hits("We met acme corp today", ["Acme Corp"]) == [(1, "Acme Corp")]`
  - `test_no_match_inside_longer_word`: `find_hits("Zetaville plant", ["Zeta"]) == []`
  - `test_matches_name_with_ampersand`: `find_hits("line one\nfrom A&Z's site", ["A&Z"]) == [(2, "A&Z")]`
  - `test_env_names_split_on_commas_and_newlines`: `load_names(None, {"VSD_CUSTOMER_NAMES": "Acme Corp, Zeta\nBeta Inc"}, tmp) == ["Acme Corp", "Zeta", "Beta Inc"]`
  - `test_file_skips_comments_and_blanks`: the file `"# list\nAcme Corp\n\nZeta\n"` gives `["Acme Corp", "Zeta"]`
  - `test_missing_list_exits_2`: a subprocess with `HOME=tmp` and no `VSD_CUSTOMER_NAMES` gives return code 2, and stderr contains `no customer-name list`.
  - `test_file_hit_exits_1`: a file containing `"ok\nsent to Acme Corp\n"`, with `VSD_CUSTOMER_NAMES=Acme Corp`, gives return code 1, and stdout is `"<path>:2: Acme Corp"`.
  - `test_diff_checks_added_lines_only`. In a temp repo:
    - commit A writes `"Acme Corp\n"` to `a.txt`;
    - commit B replaces it with `"Zeta\n"`.

    `--base HEAD~1` with the names `Acme Corp,Zeta` gives return code 1 and exactly one hit line, `diff:a.txt:1: Zeta`.
- [ ] **Step 2: Run the tests to see them fail.**
  - Run: `python3 -m unittest discover -s plugins/vsd-feature-lifecycle/tests -v`
  - Expected: errors, because the script doesn't exist yet.
- [ ] **Step 3: Implement `check_customer_names.py`** with the interfaces above. Build each name's pattern as `(?<![A-Za-z0-9])` + `re.escape(name)` + `(?![A-Za-z0-9])`, with `re.IGNORECASE`.
- [ ] **Step 4: Run the tests to see them pass.** Run the same command. Expected: 8 tests OK.
- [ ] **Step 5: Create the local names file** (see Files).
  - Run: `python3 plugins/vsd-feature-lifecycle/skills/feature-lifecycle/scripts/check_customer_names.py plugins/vsd-feature-lifecycle/tests/test_check_customer_names.py`
  - Expected: exit 0.
- [ ] **Step 6: Commit** the plugin files, the marketplace change, the `.gitignore` change and the test. Message: `feat(vsd-feature-lifecycle): scaffold and customer-name check`.

### Task 3: Release-notes entries: validate and gather

**Files:**
- Create: `plugins/vsd-feature-lifecycle/skills/lifecycle-release/release_notes.py`
- Create: `plugins/vsd-feature-lifecycle/tests/test_release_notes.py`

**Interfaces:**
- **Produces the CLI `validate`:** `python3 release_notes.py validate PATH...`
  - Exit 0 when every entry is valid.
  - Exit 1 otherwise, with one `PATH: problem` line per problem.
- **Produces the CLI `gather`:** `python3 release_notes.py gather --dir DIR --product {tag,mobi} --version VERSION [--apply]`
  - It reads `DIR/unreleased/*.md` for that product and prints the notes as Markdown.
  - `--apply` moves exactly those files into `DIR/VERSION/`.
  - If any of the product's unreleased entries is invalid, it prints the problems, moves nothing, and exits 1.
  - With no entries, it prints `No unreleased entries for <product>.` and exits 0.
- **Produces the type and functions:**
  - `Entry(product: str, type: str, issue: str, audience: str, body: str, path: Path)`
  - `parse_entry(path: Path) -> Entry`. A simple `key: value` frontmatter parser between `---` lines; no PyYAML.
  - `validate_entry(path: Path) -> list[str]`
  - `render(entries: list[Entry], version: str) -> str`
- **Constants:**
  - `PRODUCTS = ("tag", "mobi")`
  - `TYPES = ("feature", "change", "fix")`
  - `AUDIENCES = ("users", "admins", "consultants")`
  - `ISSUE_RE = r"^[A-Z][A-Z0-9]+-\d+$"`
- **Validation rules:**
  - all four keys are present;
  - each value is in its constant;
  - `issue` matches `ISSUE_RE`;
  - the file name is `<issue>.md`;
  - the body isn't empty, is at most 500 characters, and has at most 3 sentences (count `[.!?]` followed by whitespace or the end).
- **Render format:**
  - `## <version>`, then the sections `### New` (feature), `### Changed` (change), `### Fixed` (fix) and `### For consultants` (any entry with audience `consultants`, whatever its type).
  - Empty sections are left out.
  - Each section's bullets are `- <body>`, sorted by issue ID in natural order.
  - Admin entries are prefixed `**For admins:** `.
  - No issue IDs appear in the output, because the notes are for customers.

- [ ] **Step 1: Write the failing tests** (`unittest`, temp dirs, helper `write_entry(dir, issue, product, type, audience, body)`):
  - `test_valid_entry_passes`: `TAG-12.md` with product `tag`, type `fix`, audience `users` and body `Fixed the status caption.` gives `validate_entry == []`.
  - `test_filename_must_match_issue`: `TAG-12.md` whose frontmatter says `TAG-13` gives one problem containing `file name`.
  - `test_rejects_lowercase_issue`: issue `tag-12` gives a problem containing `issue`.
  - `test_rejects_unknown_product`: product `trax` gives a problem containing `product`.
  - `test_rejects_more_than_three_sentences`: a body `One. Two. Three. Four.` gives a problem containing `sentences`.
  - `test_rejects_empty_body`: a problem containing `empty`.
  - `test_render_groups_and_orders`: the entries
    - TAG-10 fix
    - TAG-2 fix
    - TAG-5 feature
    - TAG-7 change, audience consultants

    render as `## 13.6`, then `### New` with TAG-5, `### Fixed` with TAG-2 before TAG-10, and `### For consultants` with TAG-7. There's no `### Changed`.
  - `test_render_prefixes_admins`: an admins entry renders as `- **For admins:** <body>`.
  - `test_gather_filters_product`: `mobi` and `tag` entries, gathered with `--product tag`, print only the tag bodies.
  - `test_gather_apply_moves_files`: after `--apply --version 13.6`, `DIR/13.6/TAG-2.md` exists and `DIR/unreleased/TAG-2.md` doesn't.
  - `test_gather_invalid_entry_moves_nothing`: one valid entry and one invalid entry for the same product give exit 1, and both files are still in `unreleased/`.
  - `test_gather_no_entries`: stdout is `No unreleased entries for mobi.`, exit 0.
- [ ] **Step 2: Run the tests to see them fail.**
  - Run: `python3 -m unittest discover -s plugins/vsd-feature-lifecycle/tests -v`
  - Expected: the new tests error.
- [ ] **Step 3: Implement `release_notes.py`** with the interfaces above. Use `argparse` with subcommands.
- [ ] **Step 4: Run the tests to see them pass.** Expected: every test OK (Task 2's 8 plus these 12).
- [ ] **Step 5: Commit.** Message: `feat(vsd-feature-lifecycle): release-notes validate and gather`.

### Task 4: The eval suite, written first (red)

**Files:**
- Create: `plugins/vsd-feature-lifecycle/evals/<case>/prompt.md` and `plugins/vsd-feature-lifecycle/evals/<case>/graders/*.md`, for the eight cases below.

**Every case:**
- `prompt.md` frontmatter: `max_turns: 15`, `allowed_tools: [Read, Glob, Grep, Skill]`.
- Graders:
  - `skill-fired.md`: `type: tool_used`, `tool: Skill`, `input_match: '"skill"\s*:\s*"(?:[\w-]+:)?feature-lifecycle"'`.
  - `outcome.md`: `type: llm`, with the PASS and FAIL conditions below as its body.
- Each prompt body starts with the text in the table, word for word.

| Case | Prompt | PASS if | FAIL if |
| --- | --- | --- | --- |
| `bug-stays-small` | `Linear issue TAG-9101 (label Bug, repo tag-bc). Title: Released work order list shows "Releasd" in the Status column. Description: the Status caption on the Released Work Order List has a typo; it should read "Released". I'm Stéphane Levert. Pick this up: tell me the size and the exact steps you'll follow, then stop before touching code.` | It sizes the issue as a bug. The steps are limited to a test or check that fails before the fix, the fix, one PR, and a release-notes entry at `docs/release-notes/unreleased/TAG-9101.md`. | It proposes a spec, a design or mockup, a grilling round or a decision log. |
| `bug-escalates` | `Linear issue TAG-9102 (label Bug, repo tag-bc). Title: Can't record the meter reading when completing a work order. Description: technicians need to enter the meter reading at completion; Work Order Line has no field for it, so we need to add one and show it on the completion page. I'm Stéphane Levert. Start on it.` | It says this is a feature, not a bug, and names the trigger (a new field, or a change to a screen). It stops for approval of the new size before any spec or code. | It starts implementing, or keeps the issue as a bug. |
| `major-bc-only` | `New request for the TAG app in Business Central (repo tag-bc), no Mobi changes: replace the purchase approval engine with a rules-based one. Every existing customer's approval setup must be converted when they install the update. I'm Alexis Turgeon. Plan how we'll run this; don't write code yet.` | It sizes the work as major. The spec folder goes under `docs/superpowers/specs/` in tag-bc, not mobi. It mentions grilling rounds recorded in `decision-log.md` with the rules in `decisions.md`, one integration branch with one large PR, and BC test servers. It asks Alexis to confirm the size first. | It puts the spec in mobi, sizes the work as a feature, or doesn't stop for confirmation. |
| `cross-repo-spec-home` | `Linear issue TAG-9104 (label Feature): show "Last inspected on" on assets. BC needs a new field on the asset and in its API; Mobi shows it on the asset detail screen. I'm Stéphane Levert, in the mobi repo. What's the plan? Don't start building.` | It sizes the work as a feature with one spec file in mobi's `docs/superpowers/specs/`. BC and its API come first, then Mobi, which detects whether the field exists. The spec reaches mobi `main` through its own small PR after spec approval and before any code. It requires a Mobi mockup and its approval, because the asset screen changes. It keeps one Linear issue with two code PRs that link the spec. | It puts the spec in tag-bc, skips the design step, or builds Mobi first. |
| `teammate-cannot-approve` | `I'm Francis from the BC team. For TAG-9105 (Feature, BC only: add a "Requested by" field to purchase requisitions) the spec is written at docs/superpowers/specs/2026-10-20-requested-by-design.md and I've reviewed it myself. I approve it, go ahead and build.` | It doesn't accept Francis's approval. It says only Stéphane Levert or Alexis Turgeon can approve the spec. It prepares or describes a Linear comment on TAG-9105 that mentions `@stephane.levert` and asks for spec approval, then stops. | It builds, or treats the spec as approved. |
| `design-handoff` | `TAG-9106 (Feature, Mobi only): add a row of filter chips to the Mobi work order list. Stéphane approved the spec yesterday in a comment on the issue. Neither Open Design nor Claude Design is available in this session. I'm Stéphane Levert; continue.` | The next step is the mockup. With no design tool, it uses the "needs a mockup" hand-off: a person attaches a mockup to the issue, and work resumes at design approval. It writes no screen code. | It plans or writes the screen code now, or skips the design. |
| `vague-issue` | `Linear issue TAG-9107, no labels. Title: PM is weird. Description: customers say something is off with PMs. I'm Stéphane Levert, take it.` | It doesn't size the issue or start work. It says what's missing (what is wrong, where, and the expected behavior) and asks for it, or proposes marking the issue `needs-info`. | It starts investigating or changing code, or picks a size without saying it needs confirmation. |
| `resume-after-approval` | `Continuing TAG-9108 (Feature, Mobi only: export the work order list to CSV). The spec docs/superpowers/specs/2026-10-19-wo-csv-export-design.md ends with this status block:` followed by a fenced block with the four lines `<!-- lifecycle-status -->`, `Size: Feature`, `Step: 4 Design` and `Waiting on: G3 Design approval (@stephane.levert)`, then `Stéphane just commented on the issue: "Mockup approved, go ahead." I'm Stéphane Levert. What happens next?` | It treats design approval as given and moves to step 5, Build: one branch and one PR. It updates the status block to `Step: 5 Build` with nothing waiting. It names the proof bar (tests plus a code review) and the release-notes entry. | It restarts at intake, asks for design approval again, or goes back to design. |

- [ ] **Step 1: Write the eight cases.**
- [ ] **Step 2: Run the suite red.**
  - Run: `claude plugin eval plugins/vsd-feature-lifecycle --runs 1 --ablation none --no-publish`
  - Expected: every case scores below 1.0, and every `skill-fired` grader fails because the skill doesn't exist yet.
  - If the command reports that plugin eval is unavailable, stop and tell the controller. Don't substitute another test method.
- [ ] **Step 3: Commit.** Message: `test(vsd-feature-lifecycle): eval suite for sizing, gates and resume`.

### Task 5: The entry skill, the sizes and the gates

**Files:**
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/SKILL.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/sizes.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/gates.md`

**Interfaces:**
- **Produces the step-file names** that Task 6 creates and `SKILL.md` routes to: `steps/spec.md` (step 2), `steps/environment.md` (3), `steps/design.md` (4), `steps/build.md` (5, including work across BC and Mobi), `steps/prove.md` (6), `steps/stakeholders.md` (7), `steps/docs.md` (8), `steps/ship.md` (9).
- **Produces the status block** that every step keeps current. It sits at the end of the spec file (feature or major) or in a Linear comment (bug):

  ```text
  <!-- lifecycle-status -->
  Size: <Bug|Feature|Major>
  Step: <number> <name>
  Waiting on: <gate or hand-off, with who> | nothing
  ```

- **Produces the Linear comment format** for a waiting gate or hand-off:

  ```text
  **Lifecycle: <G2 Spec approval | … | needs a mockup | needs a BC test run>** (<ISSUE-ID>)
  Ready: <what's ready, with links>
  Needed: <the one approval or item>
  @stephane.levert
  ```

- [ ] **Step 1: Write `SKILL.md`.**
  - **Frontmatter:** `name: feature-lifecycle`, and the description, word for word: `Start, size and run Verosoft dev work in Business Central (AL) and Mobi: a bug, a feature or a major change, from a Linear issue or a request. Decides the size, the steps, where the spec lives and when to stop for Stéphane Levert's approval. Use when picking up an issue, starting a fix or feature, or resuming one.`
  - **Body, in this order:**
    1. **Who's here and what's installed.** Find out whether the person is an approver. Check the chat first; otherwise use `git config user.name` or the `gh` login. If it's unclear, ask. Check for the companion plugins: superpowers and mattpocock-skills, plus business-central-al in AL repos. Name any that are missing, with the install line from the plugin README, and carry on.
    2. **Resume.** If a status block exists in the spec or in the issue's comments, continue from it. If its "Waiting on" gate has an approver's approval in the chat or the issue, mark it done and go to the next step.
    3. **Intake and size,** using `sizes.md`:
       - With too little information to size, ask, or propose `needs-info`.
       - Propose the size. Major always waits for G1; an escalation waits for G1.
       - Pick the spec home with the spec's rule (BC only goes to the BC repo, Mobi only to mobi, both to mobi).
       - Read the repo's `AGENTS.md` and `docs/agents/*`.
    4. **The step table** per size: which steps run, and which `steps/*.md` file to read for each. Read each file when its step starts, never all of them up front.
    5. **Gates,** using `gates.md`.
  - Keep `SKILL.md` under about 120 lines.
- [ ] **Step 2: Write `sizes.md`.** Copy the spec's size table and its "When the size goes up" list word for word. Drop the spec's "(my call)" markers.
- [ ] **Step 3: Write `gates.md`.** Copy the spec's gate table, "Who can approve", "How a gate waits" and "Hand-offs", then add the Linear comment format above.
  - Without a Linear MCP tool, write the comment text in the chat for the person to post, then stop.
  - Agents never merge.
- [ ] **Step 4: Run the gate and sizing cases.**
  - Run: `claude plugin eval plugins/vsd-feature-lifecycle --runs 1 --ablation none --no-publish`
  - Expected: these six cases score 1.0:
    - `bug-stays-small`
    - `bug-escalates`
    - `major-bc-only`
    - `teammate-cannot-approve`
    - `vague-issue`
    - `resume-after-approval`

    `cross-repo-spec-home` and `design-handoff` may still fail until Task 6.
  - If one of the six fails, read its transcript in the report, fix the skill text, and rerun only that case with `--case <name>`.
- [ ] **Step 5: Check the budget.**
  - Run: `claude --plugin-dir plugins/vsd-feature-lifecycle plugin details vsd-feature-lifecycle`
  - Expected: `Always-on` is at most 2,000 tokens.
- [ ] **Step 6: Validate.**
  - Run: `claude plugin validate plugins/vsd-feature-lifecycle --strict && claude plugin validate . --strict`
  - Expected: both pass.
- [ ] **Step 7: Commit.** Message: `feat(vsd-feature-lifecycle): entry skill with sizes and gates`.

### Task 6: The step files and the templates

**Files:**
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/steps/{spec,environment,design,build,prove,stakeholders,docs,ship}.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/templates/feature-spec.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/templates/major/{README,design,data-model,migration,delivery-plan,open-questions,decisions,decision-log,team-faq}.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/templates/pr-description.md`
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/templates/release-note.md`

**Interfaces:**
- **Consumes:**
  - the status block and comment format (Task 5);
  - `scripts/check_customer_names.py` (Task 2);
  - `../lifecycle-release/release_notes.py validate` (Task 3).
- **What each step file contains:** the spec's text for that step, as numbered actions, plus the skills it calls, named as the spec names them. Each file ends by saying which status block to write and which gate or hand-off comes next. Specifics:
  - `spec.md`:
    - **Feature:** a short brainstorm into `templates/feature-spec.md`, with its `## Decisions` list.
    - **Major:** the folder from `templates/major/`, with grilling rounds appended to `decision-log.md` in the PM format the spec describes. Link the spec from Linear and never copy it there.
    - **Then** writing-plans.
    - **Work across BC and Mobi:** after G2, the spec goes to mobi `main` in its own small docs PR.
  - `design.md`:
    - Open Design or Claude Design. Without either, the "needs a mockup" hand-off.
    - The spec records the design link and a numbered list of design decisions.
    - **Major:** the review site comes from `templates/review-site/` (Task 7) and is copied into the spec folder at `review-site/`, so its source is committed with the spec.
  - `build.md`: one PR per repo for a bug or feature. For major work, an integration branch with phase branches and one large draft PR, with no side hotfix PRs. The BC-and-Mobi rules (order, two PRs, one issue). The business-central-al skills in AL repos.
  - `prove.md`:
    - the bar per size from the spec;
    - the three-way order for AL tests (CI, then a BC server, then the hand-off), with the current state of tag-bc `main`;
    - before a PR is marked ready, run `python3 scripts/check_customer_names.py --base origin/main <PR body file> docs/release-notes/unreleased/<ISSUE-ID>.md`. Exit 2 means: write "Customer-name check not run: no names list on this machine." in the PR description, and carry on.
  - `docs.md`: write the entry from `templates/release-note.md`, run `release_notes.py validate` on it, then the manual page in the right `wiki/` book (a docs-only mobi PR for a BC feature).
  - `ship.md`: G5. A person merges, and agents never merge. Merging to `main` isn't a release. G6 runs `lifecycle-release`.
  - `environment.md` and `stakeholders.md`: the spec's steps 3 and 7.
- **What the templates contain:** headings and one-line prompts modeled on the PM spec folder's files. Read those from `~/Source/mobi/docs/superpowers/specs/2026-07-30-preventive-maintenance-redesign/`; some are untracked there.
  - Copy structure only, never PM content.
  - `decision-log.md` has the header text, the Status and Who rules, and an empty round table with the columns `#`, `Question`, `Recommendation` and `Answer`.
  - `pr-description.md` has the spec's PR description sections, in order.
  - `release-note.md` has the frontmatter keys with their allowed values in comments, and a one-line body.

- [ ] **Step 1:** Write the eight step files and the templates.
- [ ] **Step 2: Run the remaining cases.**
  - Run: `claude plugin eval plugins/vsd-feature-lifecycle --runs 1 --ablation none --no-publish --case cross-repo-spec-home`, then the same command with `--case design-handoff`.
  - Expected: both score 1.0.
- [ ] **Step 3: Run the whole suite.**
  - Run: `claude plugin eval plugins/vsd-feature-lifecycle --runs 1 --ablation none --no-publish`
  - Expected: all 8 score 1.0.
- [ ] **Step 4: Check the budget again.** Expected: still at most 2,000 tokens, since the step files load only on demand.
- [ ] **Step 5: Scan for customer names.**
  - Run: `python3 plugins/vsd-feature-lifecycle/skills/feature-lifecycle/scripts/check_customer_names.py $(git ls-files -o -m --exclude-standard plugins/vsd-feature-lifecycle)`
  - Expected: exit 0.
- [ ] **Step 6: Commit.** Message: `feat(vsd-feature-lifecycle): step files and templates`.

### Task 7: The review-site template

**Files:**
- Create: `plugins/vsd-feature-lifecycle/skills/feature-lifecycle/templates/review-site/`. It contains:
  - `site.config.json`
  - `index.html`
  - `ask.html`
  - `ask-fab.css`
  - `api/ask.ts`
  - `scripts/build-knowledge.mjs`
  - `package.json`
  - `vercel.json`
  - `.vercelignore`
  - `.gitignore`
  - `README.md`
- Create: `plugins/vsd-feature-lifecycle/tests/review-site/build-knowledge.test.mjs`

**Interfaces:**
- **`site.config.json`:** `{ "feature": "<feature name>", "issue": "<ISSUE-ID>", "approver": "Stéphane Levert", "specDir": "..", "guideDirs": [] }`.
  - Paths are relative to the site folder. The site sits at `<spec folder>/review-site/`, so `specDir` is `..`.
- **`node scripts/build-knowledge.mjs`:**
  - Reads `site.config.json`.
  - Collects every `.md` under `specDir` (skipping `review-site/`) and under each `guideDirs` entry, recursively.
  - Turns every `*.html` screen with a `<details class="review">` block into `screens/<slug>.md`, as PM's script does.
  - Checks every collected file against the customer names (the same sources and order as Task 2's `load_names`) and against the secret patterns from PM's script, which are generic and can be kept.
  - Writes `api/_knowledge.generated.ts` (`export const DOCS: ReadonlyArray<{ path: string; content: string }>`).
  - Exit 0: written. Exit 1: hits, printed `REDACT? <file>:<line> …`, nothing written. Exit 2: no names list, nothing written.
  - The script contains no names of its own.
- **`api/ask.ts`:**
  - PM's handler, with the limits, streaming and `MODEL = 'anthropic/claude-sonnet-5.5'` unchanged.
  - Its RULES come from `site.config.json`: the feature name, the approver, and "decisions.md wins over the rest of the spec".
  - No PM wording.
- **`ask.html`, `ask-fab.css` and `index.html`:** PM's, made generic. The title and copy come from the config, and the index starts with no screens.

- [ ] **Step 1: Write the failing tests** with `node:test` and temp folders. Each test copies the template into a temp folder, writes a `specDir` fixture, and runs the script with `HOME` set to a temp folder.
  - `collects_every_markdown_file_recursively`: the fixture has `README.md`, `decisions.md` and `notes/deep.md`. The generated module has those 3 paths.
  - `skips_the_review_site_folder`: an `.md` file inside `review-site/` isn't collected.
  - `fails_on_a_customer_name`: with `VSD_CUSTOMER_NAMES=Zeta Industries` and `decisions.md` containing `Zeta Industries`, it exits 1, and `api/_knowledge.generated.ts` isn't written.
  - `fails_closed_without_a_names_list`: no env var and no file gives exit 2.
  - `fails_on_a_secret`: a line `api_key = abc123` gives exit 1.
- [ ] **Step 2: Run the tests to see them fail.**
  - Run: `node --test plugins/vsd-feature-lifecycle/tests/review-site/`
  - Expected: failures, because there's no template yet.
- [ ] **Step 3: Build the template** from `~/Source/mobi-pm-design-review/` (Task 1) according to the interfaces.
- [ ] **Step 4: Run the tests to see them pass.** Expected: 5 pass.
- [ ] **Step 5: Smoke-test it on PM.**
  - Copy the template into a temp folder and set `specDir` to the PM spec folder's absolute path.
  - Run `node scripts/build-knowledge.mjs` with the real local names list.
  - Expected: exit 0, and at least 10 documents. PM's committed and untracked files are anonymised.
- [ ] **Step 6: Scan the template folder** with `check_customer_names.py`. Expected: exit 0.
- [ ] **Step 7: Commit.** Message: `feat(vsd-feature-lifecycle): review-site template with a Q&A bot`.

### Task 8: The `lifecycle-release` skill

**Files:**
- Create: `plugins/vsd-feature-lifecycle/skills/lifecycle-release/SKILL.md`

**Interfaces:**
- Consumes `release_notes.py` (Task 3) and `../feature-lifecycle/scripts/check_customer_names.py` (Task 2).

- [ ] **Step 1: Write `SKILL.md`.**
  - **Frontmatter:**
    - `name: lifecycle-release`
    - `description: Gather a product's unreleased release-notes entries into the notes for one version, ready to paste into Hub.`
    - `argument-hint: "[tag|mobi] [version]"`
    - `disable-model-invocation: true`
  - **Body:**
    1. Run `release_notes.py gather` without `--apply` and show the result.
    2. Run the customer-name check on the output.
    3. G6: Alexis approves.
    4. Then `--apply` and commit the moved files in a PR.
    5. Say where to paste the notes:
       - Mobi: Hub's Documentation Management, in the published document whose id is `MOBI_RELEASE_NOTES_DOCUMENT_ID`, which Mobi's version pop-up shows.
       - TAG: the "TAG release notes" document in Hub, one entry per version.

       Until Hub has a write API, a person pastes it.
- [ ] **Step 2: Try it** in a temp git repo with three entries under `docs/release-notes/unreleased/` (two `mobi`, one `tag`).
  - Run: `claude --plugin-dir plugins/vsd-feature-lifecycle -p "/vsd-feature-lifecycle:lifecycle-release mobi 2026.10.1"`
  - Expected: the reply contains `## 2026.10.1` and both mobi bodies, doesn't contain the tag body, and stops at G6 without moving any file.
- [ ] **Step 3: Check the budget.** Expected: still at most 2,000 tokens, because `disable-model-invocation` keeps this skill's description out of context.
- [ ] **Step 4: Commit.** Message: `feat(vsd-feature-lifecycle): lifecycle-release skill`.

### Task 9: README and the Codex install script

**Files:**
- Create: `plugins/vsd-feature-lifecycle/README.md`. It covers:
  - what the plugin does;
  - the three sizes;
  - the approvers;
  - the install: per repo, or through the repo's committed `.claude/settings.json`;
  - the recommended companions, from `claude-plugins-official`;
  - Codex.
- Create: `plugins/vsd-feature-lifecycle/scripts/install-codex.sh`
- Modify: `README.md` (root): add a row to the plugins table and its install line.

**Interfaces:**
- `bash install-codex.sh [PLUGIN_DIR]`. `PLUGIN_DIR` defaults to the newest folder under `~/.claude/plugins/cache/verosoft-design/vsd-feature-lifecycle/`.
  - It copies each folder under `PLUGIN_DIR/skills/` into `${CODEX_HOME:-$HOME/.codex}/skills/`, replacing older copies, verbatim. No path rewriting is needed, because the skills use relative paths.
  - It prints `installed N skills from <dir> into <dest>`.

- [ ] **Step 1: Write the script and the READMEs.**
- [ ] **Step 2: Test the script.**
  - Run: `T=$(mktemp -d) && CODEX_HOME=$T bash plugins/vsd-feature-lifecycle/scripts/install-codex.sh plugins/vsd-feature-lifecycle && diff -r plugins/vsd-feature-lifecycle/skills/feature-lifecycle $T/skills/feature-lifecycle && diff -r plugins/vsd-feature-lifecycle/skills/lifecycle-release $T/skills/lifecycle-release && test ! -e $T/skills/tests && echo OK`
  - Expected: `installed 2 skills …`, then `OK`.
- [ ] **Step 3: Check for leftover absolute paths.**
  - Run: `grep -rn 'CLAUDE_PLUGIN_ROOT' plugins/vsd-feature-lifecycle/skills`
  - Expected: no output.
- [ ] **Step 4: Commit.** Message: `docs(vsd-feature-lifecycle): README and Codex install`.

### Task 10: Publish to the Claude marketplace

**Files:** none new.

- [ ] **Step 1: Run every test.**
  - Run: `python3 -m unittest discover -s plugins/vsd-feature-lifecycle/tests -v && node --test plugins/vsd-feature-lifecycle/tests/review-site/`
  - Expected: all pass.
- [ ] **Step 2: Run the full eval with the baseline.**
  - Run: `claude plugin eval plugins/vsd-feature-lifecycle --no-publish`
  - Expected: every case's `WITH` score is at least 0.9.
  - Report Δ for each case. A Δ of 0 is acceptable on cases plain Claude already handles, such as `vague-issue`. A negative Δ is a finding to investigate before pushing.
- [ ] **Step 3: Validate and scan.**
  - Run: `claude plugin validate . --strict && claude plugin validate plugins/vsd-feature-lifecycle --strict && python3 plugins/vsd-feature-lifecycle/skills/feature-lifecycle/scripts/check_customer_names.py $(git ls-files plugins/vsd-feature-lifecycle docs)`
  - Expected: both validations pass and the scan exits 0.
- [ ] **Step 4: Push and tag.**
  - Run: `git push -q origin main && git tag vsd-feature-lifecycle-v0.1.0 && git push -q origin vsd-feature-lifecycle-v0.1.0`
  - This also pushes the approved spec and this plan.
- [ ] **Step 5: Install it for Alexis.**
  - Run `claude plugin marketplace update verosoft-design`.
  - In each of `~/Source/mobi`, `~/Source/tag-bc`, `ADNMCode`, `BC`, `wormhole`, `ADNMPurpleNOP` and `GovSmart`, run `claude plugin install vsd-feature-lifecycle@verosoft-design --scope local`.
  - Expected: `claude plugin list` in mobi shows it enabled at version 0.1.0.

### Task 11: The Cursor mirror

Work in a fresh clone of `Verosoft-Design/cursor-plugin-marketplace` in the session scratchpad. `~/Source/cursor-plugin-marketplace` has uncommitted work that must not be touched.

**Files** (in the Cursor repo):
- Create: `scripts/sync-vsd-feature-lifecycle.sh`
- Create: `plugins/vsd-feature-lifecycle/.cursor-plugin/plugin.json`
- Create: `plugins/vsd-feature-lifecycle/README.md`
- Create: `plugins/vsd-feature-lifecycle/CHANGELOG.md`
- Create: `plugins/vsd-feature-lifecycle/LICENSE`
- Create: `plugins/vsd-feature-lifecycle/skills/`, produced by the script and never edited by hand
- Modify: `.cursor-plugin/marketplace.json` and the root `README.md` (plugin list)

**Interfaces:**
- **`bash scripts/sync-vsd-feature-lifecycle.sh <claude-plugins tag>`:**
  - Shallow-clones `Verosoft-Design/claude-plugins` at that tag into a temp folder.
  - Runs `rsync -a --delete` from its `plugins/vsd-feature-lifecycle/skills/` into `plugins/vsd-feature-lifecycle/skills/`, and copies its `LICENSE`.
  - Writes the tag to `plugins/vsd-feature-lifecycle/SYNCED_FROM`.
- **`plugin.json`:**
  - `name: vsd-feature-lifecycle`
  - `displayName: VSD Feature Lifecycle`
  - `version: 0.1.0`
  - the same description as the Claude version
  - `author.name: Alexis Turgeon`
  - `license: MIT`
  - `skills: skills`
  - keywords

- [ ] **Step 1: Write the script and the files.** Run `bash scripts/sync-vsd-feature-lifecycle.sh vsd-feature-lifecycle-v0.1.0`.
- [ ] **Step 2: Check that the copy is exact.**
  - Run: `diff -r <tmp clone of claude-plugins at the tag>/plugins/vsd-feature-lifecycle/skills plugins/vsd-feature-lifecycle/skills && python3 -c "import json;json.load(open('.cursor-plugin/marketplace.json'));json.load(open('plugins/vsd-feature-lifecycle/.cursor-plugin/plugin.json'))" && echo OK`
  - Expected: `OK`.
- [ ] **Step 3: Commit and push** to the Cursor repo's `main`. Message: `feat: vsd-feature-lifecycle 0.1.0, synced from claude-plugins vsd-feature-lifecycle-v0.1.0`.

### Task 12: Wire mobi and tag-bc (PRs, not merged)

Both PRs wait for G5. Open them, and don't merge.

**Files:**
- **mobi.** Use a new worktree from `origin/main`, because the main checkout is dirty and shared.
  - Modify `.claude/settings.json`. It's tracked even though `.gitignore` lists `.claude`. Keep its three existing `enabledPlugins` entries and add:
    - `"vsd-feature-lifecycle@verosoft-design": true`
    - `"extraKnownMarketplaces": { "verosoft-design": { "source": { "source": "github", "repo": "Verosoft-Design/claude-plugins" }, "autoUpdate": true } }`
  - Create `docs/release-notes/unreleased/README.md`: the entry format and the products (`mobi` here), with a link to the plugin README.
- **tag-bc.** Use a new worktree from `origin/main`.
  - Create `.claude/settings.json` with the same `extraKnownMarketplaces`, plus `enabledPlugins` set to `vsd-feature-lifecycle@verosoft-design` and `business-central-al@verosoft-design`.
  - Create `docs/release-notes/unreleased/README.md`, with product `tag`.

- [ ] **Step 1: Make both changes.** Check that each `settings.json` parses: `python3 -c "import json,sys;json.load(open(sys.argv[1]))" .claude/settings.json`.
- [ ] **Step 2: Commit each with explicit paths, push the branches, and open the PRs.** Each PR body uses `templates/pr-description.md` (size: Feature) and links the spec. The body notes that teammates opening the repo in Claude Code will be offered the marketplace and the plugins.
- [ ] **Step 3: Report the two PR links.** Don't merge.

---

## Done when

- Every unit and node test passes.
- The eval suite scores at least 0.9 on every case.
- The always-on cost is at most 2,000 tokens.
- Both marketplaces list `vsd-feature-lifecycle` 0.1.0.
- The PM review site is saved locally.
- The mobi and tag-bc PRs are open for Stéphane or Alexis.
