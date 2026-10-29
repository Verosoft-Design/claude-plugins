# dynamics-fno-xpp (Claude Code)

Dynamics 365 Finance and Operations (X++) development for Claude Code: the `business-central-al` setup, mapped to F&O. Claude looks up real symbols instead of guessing, follows the model's conventions, checks the metadata XML after every edit, and builds, syncs, tests and checks the UI on a real F&O dev VM.

**Status: 0.1.0, first cut.** The read-only loops (symbols, where-used, labels, knowledge, BP check, XML lint) were run on a 10.0.46 cloud-hosted dev VM. Build, database sync, SysTest and the UI loop are written from the tools' sources and marked **verified: pending** in their skills until their first real run.

## Install

```sh
claude plugin marketplace add Verosoft-Design/claude-plugins
# run inside each F&O repo, so the plugin only loads there
claude plugin install dynamics-fno-xpp@verosoft-design --scope local

# recommended: the process skills this plugin is designed to work with
claude plugin install superpowers@claude-plugins-official
claude plugin install mattpocock-skills@claude-plugins-official
```

**Prerequisites:**
- Node.js, which runs the hook launcher and both MCP servers;
- Python 3 for the hooks (`python3`, `python` or `py -3`; set `FNO_PYTHON` to override).

**On the F&O dev VM:** the community [d365fo-mcp-server](https://github.com/dynamics365ninja/d365fo-mcp-server) (MIT), d365fo.tools and `@playwright/mcp`. `/fno-vm-setup` walks through it.

**Off the VM** (a Mac, or the agent server), you can read and edit XML and run the lint. Builds and tests need the VM.

First time in a repo: `/fno-init` writes its `CLAUDE.md`.

## How it makes Claude better at X++

| Failure mode | What the plugin does |
| --- | --- |
| Invents table, field and method names, or CoC signatures | d365fo MCP `search`, `get_object_info`, `find_references` (with the xref database), `extension_info`, `labels`; the `fno-explorer` agent cites PLD paths |
| Breaks the metadata reader with hand-written XML | `PostToolUse` lint, 18 checks: well-formed XML, CDATA, Yes/No vs true/false per property, real form control types and patterns, `.rnrproj` registration, prefix, extension naming, reserved words, select clause order |
| Edits a Microsoft package, or overlayers | The lint flags any file in a Microsoft package (XPP015); conventions say extend: CoC, event handlers, table and form extensions |
| Ignores the model's conventions (prefix, naming, labels) | Session start prints the model, module vs model name, layer, references, prefix and project; `xpp-conventions` plus 4 folder-scoped rule sets auto-load on AOT XML |
| "Compiles, so it works" | `xpp-feedback-loops` ranks the loops and says what each proves; `xpp-run-tests` runs SysTest; `xpp-ui-test` drives the web client |
| Weak or no tests | `xpp-write-test`: SysTestCase red-first, Acceptance Test Library for standard data, with the MCP's rulebook from the shipped tests |
| Builds someone else's half-done work into the environment | Build and sync skills check `git status` of the model first and stop if anything isn't theirs |

Process discipline (brainstorming, plans, TDD, debugging, verification) comes from **superpowers** and **mattpocock-skills**. This plugin supplies the F&O steps they call for.

## Components

**MCP** (`.mcp.json`; both start through `scripts/mcp-launch.mjs`, so they work on Windows without `npx`):
- `d365fo`: d365fo-mcp-server. Found via `D365FO_MCP_ENTRY` (a checkout's `dist/index.js`) or a global `npm i -g d365fo-mcp`; config in `D365FO_CONFIG`.
- `playwright`: `@playwright/mcp`, from a global install. Extra flags in `FNO_PLAYWRIGHT_ARGS`.

**Hooks** (`hooks/hooks.json`; exec form `node scripts/run-python.mjs <script>`, which finds Python on Windows and Unix):
- `SessionStart` → `scripts/session-start.py`, silent outside F&O repos.
- `PostToolUse` on Edit/Write → `scripts/xpp-xml-lint.py` (`FNO_XPP_LINT=0` disables it). It is also a CLI: `python scripts/xpp-xml-lint.py <files>`.

**Agent:** `fno-explorer`, read-only standard-code lookups with citations.

**Skills Claude uses on its own:**
- conventions: `xpp-conventions`, path-scoped, plus `xpp-conventions-tables`, `-forms`, `-enums` and `-classes`;
- `xpp-feedback-loops`, `xpp-build`, `xpp-db-sync`, `xpp-run-tests`, `xpp-write-test`, `xpp-ui-test`.

**Slash commands:** `/fno-init`, `/fno-vm-setup`.

**Scripts:** `xpp-bp-check.ps1` runs Microsoft's xppbp directly, read-only. Use it instead of the MCP's `run_bp_check` when the model's name differs from its module.

**Reference:** `reference/*.md`:
- the 8 TAG Cursor rules (January 2026) ported to plain docs, with corrections marked "Checked 2026-10-29";
- `d365fo-mcp.md`: the MCP's tools and the quirks found on 10.0.46.

## How it maps to business-central-al

| business-central-al | dynamics-fno-xpp |
| --- | --- |
| AL MCP (`altool`) | d365fo-mcp-server (community, MIT) |
| AL language server | none exists for X++; the MCP's symbol tools stand in |
| `al-base-app-source` | not needed: PLD holds all standard source as XML |
| `bc-explorer` | `fno-explorer` |
| `al-conventions` + `al-lint` hook | `xpp-conventions` (+4) + `xpp-xml-lint` hook |
| `al-feedback-loops`, `al-run-tests`, `al-write-test`, `al-ui-test` | `xpp-feedback-loops`, `xpp-run-tests`, `xpp-write-test`, `xpp-ui-test` |
| `al-compile`/`al-build`, publish + schema sync | `xpp-build`, `xpp-db-sync` |
| `al-init`, `bc-server-setup` | `fno-init`, `fno-vm-setup` |
| BCQuality review (`/bcq-review`) | planned: `xpp-review` with five domains (see `docs/superpowers/plans/2026-10-29-fno-xpp-plugin.md`) |

## Safety rules

- Build and sync only when the model has no one else's uncommitted work.
- Database sync is additive; destructive schema changes need the user to name the field.
- Never edit a Microsoft package.
- Never print or store credentials. The d365fo.tools sync cmdlets print the SQL password with `-OutputCommandOnly`.

## Maintaining

Run the tests: `python3 -m unittest discover -s plugins/dynamics-fno-xpp/tests` (85 tests; they pass on Linux and on Windows with Python 3.13). Validate with `claude plugin validate plugins/dynamics-fno-xpp --strict` and `claude plugin validate .` from the repo root. `scripts/xpp_xml_facts.json` is data from a 10.0.46 survey; refresh it when the platform moves.

MIT. See `LICENSE`.
