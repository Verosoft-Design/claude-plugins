# Changelog

## 1.1.3 — 2026-10-23

- **The Verosoft agent server builds and tests AL:** on orca-agents-1, `al-run-tests` uses `al-test` (build with `TESTS`, publish to a free tenant of the agents' BC server on AKS, run the codeunits) and `al-compile` uses the server's `al-compile` command, since there's no AL MCP there. `bc-server-setup` sets nothing up on that server and leaves the other BC pods alone.

## 1.1.2 — 2026-10-21

- `bc-server-setup` checks the OS and Docker first. On Windows with Docker running Windows containers, it recommends the local container. On Windows without Docker, or with Docker in Linux-container mode, it says so and offers to switch or install Docker Desktop. On macOS and Linux, it recommends a sandbox, an existing server or a container from the team's BC Docker Manager in Azure, now named under **existing**. The person still picks, and nothing is installed or started without their yes.

## 1.1.1 — 2026-10-15

- Author name corrected to Alexis Turgeon (`plugin.json`, `LICENSE`).
- The `verosoft-design` marketplace no longer re-lists `superpowers` and `mattpocock-skills`. The README recommends installing them from `claude-plugins-official`, and installing this plugin per AL repo with `--scope local`.

## 1.1.0 — 2026-10-15

Refreshed every upstream source to its current state.

### Microsoft ALTool / AL MCP (Learn docs, Oct 2026)
- AL language server (`altool launchlspserver`) wired in `.lsp.json`: diagnostics after each edit, plus go-to-definition / references / call hierarchy through the LSP tool.
- `reference/al-mcp-usage.md` rewritten: `al_getnextobjectid` (free object IDs), `al_addproject`, `al_symbolsearch` `source: "environment"` (search what's installed on the tenant) and the optional `parameters` wrapper, `BC_SERVER_*` connection variables.
- `/al-run-tests` now uses `al runtests` (any OS, JSON per test method, batch `--testgroups`); BcContainerHelper and AL-Go CI remain as fallbacks.
- New skills: `/al-snapshot-debug` (Snapshot Debugging MCP proxy), `/al-profile` (Performance Profiling MCP proxy), `/al-call-graph` (`al graph`). The proxies are BC 29 previews.
- `bc-server-setup` standardises on `BC_SERVER_URL/INSTANCE/PORT/USERNAME/PASSWORD` and `altool auth login`.
- `/al-ui-test`: bc-replay MFA options (`-MultiFactorType`, `-MultiFactorSecretKey`), verified against 0.1.139.

### microsoft/BCQuality 4d59fb73 → 86d809b5
- 19 review domains (was 6) and 388 Microsoft knowledge articles; 28 new review skills; community `agents` review.
- Contracts updated (new finding fields `domain`, `suggested-code`; leaf agent findings; acceptance gate; rollup rules); validator R01–R29; findings renderer handles the new schema.
- Content mirrors the upstream layout (`content/bcquality/skills/`, `schemas/`, `tools/`, `docs/`). TAG API article moved to the `web-services` domain.

### microsoft/BCApps dc1242e3 → 395d98e1
- Rulesets refreshed (AA0139, AL1085, AW0017, AL1430 downgraded to Warning; AL0920 back to Error; AL0925 None). Upstream `ruleset.json` now has a trailing comma.
- The six review prompts were retired upstream (Microsoft's reviewer moved to microsoft/BC-ALAgents and reads BCQuality). Kept frozen at `7040033d`; BC-Bench measures these same prompts at ~+20 F1 on code review.
- `reference/al-naming-and-files.md` aligned with BCApps' extensibility guidelines (record variable names, declaration order, event naming and `IsHandled`).

### microsoft/BC-Bench ef4f4668 → 7c98b750
- ALTest prompt unchanged; claims in the test skills now cite the measured runs and dates. Handlers enqueue, test bodies assert (ALTest pattern) across the testing skills and reference.
- Session context and the `/al-init` CLAUDE.md template add BC-Bench's findings: locate before fixing (half of failed bug fixes edited the wrong place) and an explicit skill nudge (agents rarely invoke skills unprompted).

### AL-Go v9.0 → v10.0
- Workflows dispatched by file name (display names start with a space, so name lookups never matched); `gh` syntax fixed; invalid `useGhTokenWorkflow` input removed from system-file updates; `Create release` inputs and branch naming corrected; v10 authentication (`Authenticate` action, AuthContext lookup order) and secrets guidance.

### Also
- Marketplace README mentions Microsoft's optional `al-review` plugin (microsoft/BC-ALAgents).

## 1.0.0 — 2026-10-15

First Claude Code release, ported from the Cursor plugin v0.6.4 (`plugins/business-central-al`).

### Carried over unchanged
- All vendored Microsoft content in `content/` at the same pinned SHAs (BCApps `dc1242e3`, BCQuality `4d59fb73`, BC-Bench `ef4f4668`): 9 analyzer rulesets, VS Code defaults, 6 review prompts, al-docs, BCQuality contracts + knowledge + AL samples, TAG custom layer, ALTest prompt.
- All 53 skills, with Cursor wording and `<plugin>` paths rewritten for Claude Code (`${CLAUDE_PLUGIN_ROOT}`).
- Vendor scripts, BCQuality validator, findings renderer, altool probe.

### Changed for Claude Code
- Cursor `.mdc` rules → `reference/*.md`, loaded through the path-scoped `al-conventions` skill (auto-loads on `*.al` / `app.json`).
- AL MCP: `.mcp.json` passes `${CLAUDE_PROJECT_DIR}`, so the project loads without `al_addproject` or a per-workspace MCP file. `/al-setup` step 4 removed.
- Hooks: one `SessionStart` hook (silent outside AL repos) replaces the Cursor sessionStart + per-prompt hooks. It reports apps, ID ranges, affixes, AL-Go settings, AL MCP status, BC server status and the AL working rules. The model-recommendation text was dropped.

### New
- `PostToolUse` hook + `scripts/al-lint.py`: after every `.al` edit, label conventions (AA0074 suffixes, placeholder `Comment`, `Locked` on URLs/tokens, `Error(StrSubstNo(...))`, string concatenation) are fed back to Claude. Also usable as a CLI. `BC_AL_LINT=0` disables it.
- `bc-server-setup`: container (BcContainerHelper), online sandbox, or existing server, recorded in `.claude/bc-server.json` (credential env var names only).
- `al-run-tests`: publish app + test app and run test codeunits on the server; AL-Go CI fallback.
- `al-ui-test`: page scripting replay with `@microsoft/bc-replay`, or live exploration with the Playwright MCP.
- `al-base-app-source` + `bc-explorer` agent: base-app source at the project's version for grep, so signatures and events are looked up, not guessed.
- `al-feedback-loops`: the BC answer to "how do I build / test / reproduce / verify" for the superpowers and mattpocock-skills process skills.
- `al-init`: writes the repo's `CLAUDE.md` from its real conventions.
