# business-central-al (Claude Code)

Business Central AL development for Claude Code. It started as a port of the Cursor plugin in [Verosoft-Design/cursor-plugin-marketplace](https://github.com/Verosoft-Design/cursor-plugin-marketplace) (`plugins/business-central-al`), carrying the same Microsoft-sourced content (BCApps, BCQuality, BC-Bench, pinned in `content/PINNED.json`). On top of that it adds the loop the Cursor version was missing: **running the code on a real Business Central**.

## Install

```sh
claude plugin marketplace add Verosoft-Design/claude-plugins
# run inside each AL repo, so the plugin only loads there
claude plugin install business-central-al@verosoft-design --scope local

# recommended: the process skills this plugin is designed to work with, from Anthropic's official marketplace
claude plugin install superpowers@claude-plugins-official
claude plugin install mattpocock-skills@claude-plugins-official
```

Optional: Microsoft's own AL review plugin, the engine behind BCApps PR reviews (needs pwsh and a signed-in GitHub Copilot CLI): `claude plugin marketplace add microsoft/BC-ALAgents && claude plugin install al-review@bc-alagents`.

Prerequisites: `python3` (hooks), `altool` or `al` on PATH for the AL MCP (`/al-setup` walks through it), `gh` for AL-Go skills. For running tests: a BC server (`/bc-server-setup`). For UI replay: Node.js.

First time in a repo: run `/al-init` to write its `CLAUDE.md`, then `/bc-server-setup`. It checks for Windows and Docker, and proposes a local container first when it can run one.

## How it makes Claude better at AL

| Failure mode | What the plugin does |
| --- | --- |
| Invents field names, procedure signatures, event parameters | AL MCP `al_symbolsearch`; `al-base-app-source` gets base-app source at the project's version; the `bc-explorer` agent looks things up and cites `file:line` |
| Ignores the repo's conventions (TAG prefix, ID ranges, file naming) | Session-start context lists apps, ID ranges, affixes; `/al-init` writes them into `CLAUDE.md`; `al-conventions` auto-loads on `.al` files |
| Code that doesn't compile | AL MCP `al_compile` / `al_getdiagnostics` after edits, project loaded automatically |
| Label and style slips | `PostToolUse` lint hook feeds AA0074 / Comment / Locked / StrSubstNo findings straight back after each edit |
| "Compiles, so it works" | `/al-run-tests` runs test codeunits on a BC server; `/al-ui-test` replays page scripting recordings in the web client; `al-feedback-loops` defines what counts as evidence |
| Weak tests | `/al-write-test` uses BC-Bench's ALTest prompt (+10.7 pt on Opus 4.6, Apr 2026; not re-measured since); BCApps test conventions |
| Review misses BC-specific issues | `/bcq-review`: BCQuality super-skill composing 19 domain reviews (388 Microsoft knowledge articles), strict JSON findings; the BCApps review instructions it pulls in measured ~+20 F1 in BC-Bench's code-review benchmark |

Process discipline (brainstorming, plans, TDD, systematic debugging, verification before completion, grilling a spec) comes from **superpowers** and **mattpocock-skills**, installed separately from Anthropic's official marketplace so the community keeps them current. This plugin doesn't copy them. It supplies the BC-specific steps they call for: `al-feedback-loops` maps "run the tests" / "build a repro" / "verify" to real BC commands.

## Components

**MCP** — `.mcp.json`: `al` → `altool launchmcpserver --transport stdio ${CLAUDE_PROJECT_DIR}`.

**Hooks** — `hooks/hooks.json`:
- `SessionStart` → `scripts/session-start.py` (silent outside AL repos).
- `PostToolUse` on Edit/Write → `scripts/al-lint.py` (`BC_AL_LINT=0` to disable; also a CLI: `python3 scripts/al-lint.py <files>`).

**Agent** — `bc-explorer`: base-app/symbol lookups with citations.

**Skills Claude uses on its own**: `al-conventions` (path-scoped), `al-feedback-loops`, `al-run-tests`, `al-ui-test`, `al-base-app-source`, `al-write-test`, `business-central-al-tdd`, `al-build-and-publish`, `al-go-lifecycle`, `al-code-review` + 6 review leaves, `al-entry`, `al-docs`, `al-scaffold-module`, `bcq-write-knowledge`.

**Slash commands** (user-invoked):
- Setup: `/al-setup`, `/al-init`, `/bc-server-setup`
- Inner loop: `/al-symbols`, `/al-symbol-search`, `/al-compile`, `/al-build`, `/al-publish-sandbox`
- AL-Go: `/al-new-pte`, `/al-new-appsource`, `/al-add-test-app`, `/al-add-bcpt-app`, `/al-import-existing-app`, `/al-create-online-dev-env`, `/al-publish-to-environment`, `/al-current`, `/al-next-minor`, `/al-next-major`, `/al-troubleshoot`, `/al-update-system-files`, `/al-increment-version`, `/al-release`, `/al-publish-appsource`, `/al-deploy-docs`, `/al-secrets-setup`, `/al-init-keyvault`, `/al-go-live`
- Quality: `/al-apply-rulesets`, `/al-apply-vscode-defaults`, `/bcq-review`, `/bcq-review-<domain>` for each of the 19 domains (performance, security, privacy, upgrade, style, ui, error-handling, events, interfaces, breaking-changes, web-services, testing, data-modeling, query, reporting, appsource, telemetry, scm, finance) plus `/bcq-review-agents`, `/bcq-update`
- Tests: `/tdd-checklist`, `/scaffold-test-codeunit`, `/scaffold-handler-methods`

Names are namespaced as `/business-central-al:<skill>`; the bare name works when nothing else uses it.

**Reference** — `reference/*.md` are the Cursor rules converted to plain docs (naming, labels, license header, XML docs, testing, AL MCP usage, BCQuality contracts).

## Safety rules (unchanged from the Cursor plugin)

Production deploys and AppSource Go Live need explicit confirmation naming them; `ForceSync`/`Recreate` schema modes need restated confirmation; AL-Go system file updates default to PR mode; credentials are only ever referenced by environment variable name.

## Maintaining

Vendored content is refreshed with `/bcq-update` (or `scripts/vendor-*.sh`) in a checkout of this repo, then committed. The Cursor plugin keeps its own copy. Validate with `claude plugin validate plugins/business-central-al --strict` and `claude plugin validate .` from the repo root.

MIT. See `LICENSE`.
