# Verosoft Design — Claude Code plugins

Claude Code plugin marketplace for Verosoft Design: Business Central AL development, Dynamics 365 Finance and Operations X++ development, and the Verosoft feature lifecycle. (Cursor plugins live in [cursor-plugin-marketplace](https://github.com/Verosoft-Design/cursor-plugin-marketplace).)

## Install

```sh
claude plugin marketplace add Verosoft-Design/claude-plugins

# run inside each AL repo, so the plugin only loads there
claude plugin install business-central-al@verosoft-design --scope local

# run inside each Dynamics 365 F&O (X++) repo
claude plugin install dynamics-fno-xpp@verosoft-design --scope local

# the feature lifecycle (bug / feature / major, gates, spec homes): in mobi and AL repos
claude plugin install vsd-feature-lifecycle@verosoft-design --scope local
```

Installing at user scope (the default) loads the plugin's skills, MCP server and hooks in every repo, AL or not. `--scope local` records it in the repo's gitignored `.claude/settings.local.json`.

Inside a session the same works as `/plugin marketplace add Verosoft-Design/claude-plugins` and `/plugin install ...`. Update with `claude plugin marketplace update verosoft-design`.

### Recommended companions

The plugins are designed to work with these community skills. Install them the way their authors recommend:

```sh
claude plugin install superpowers@claude-plugins-official        # obra/superpowers: brainstorming, plans, TDD, systematic debugging, verification
claude plugin install mattpocock-skills@claude-plugins-official  # mattpocock/skills: grilling, spec and ticket flows, diagnosing bugs, TDD, code review

# pbakaus/impeccable: UI design for the mobi apps' screens (mockups, building, the finish review)
claude plugin marketplace add pbakaus/impeccable
claude plugin install impeccable@impeccable
```

For Codex, install impeccable with its own installer instead: `npx impeccable install -y --providers=codex`. Use one route per tool, so the skill isn't loaded twice.

## Plugins

| Plugin | Source | What it is |
| --- | --- | --- |
| [`business-central-al`](plugins/business-central-al) | this repo | AL MCP + AL language server, AL-Go lifecycle, BCQuality review (19 domains), BC-Bench ALTest test generation, tests on a real BC (`al runtests`), web-client UI checks, snapshot debugging, profiling, call graph |
| [`dynamics-fno-xpp`](plugins/dynamics-fno-xpp) | this repo | 0.1.0. The community d365fo-mcp-server (symbols, where-used with the xref database, labels, BP check, build, sync, SysTest), X++ metadata conventions with an 18-check post-edit XML lint, feedback loops, SysTest + ATL test writing, Playwright UI checks on a dev VM. Build, sync, test and UI loops are still "verified: pending" |
| [`vsd-feature-lifecycle`](plugins/vsd-feature-lifecycle) | this repo | Sizes dev work (bug, feature, major), runs its steps, keeps one home for specs and decisions, release-notes entries, and gates for the issue assignee's approval |

Optional, from Microsoft: `claude plugin marketplace add microsoft/BC-ALAgents && claude plugin install al-review@bc-alagents` (Microsoft's BCApps PR reviewer; needs pwsh and a signed-in GitHub Copilot CLI).

## Layout

```text
.claude-plugin/marketplace.json
plugins/
  business-central-al/
    .claude-plugin/plugin.json
    .mcp.json  .lsp.json  hooks/  agents/  skills/  reference/  content/  scripts/
  dynamics-fno-xpp/
    .claude-plugin/plugin.json
    .mcp.json  hooks/  agents/  skills/  reference/  scripts/  tests/
```

## Maintaining

Validate before pushing:

```sh
claude plugin validate . --strict
claude plugin validate plugins/business-central-al --strict
claude plugin validate plugins/dynamics-fno-xpp --strict
python3 -m unittest discover -s plugins/dynamics-fno-xpp/tests
```

Upstream Microsoft content (BCApps, BCQuality, BC-Bench) is pinned in `plugins/business-central-al/content/PINNED.json` and refreshed with the plugin's `scripts/vendor-*.sh` (see `/bcq-update`).

MIT. See `LICENSE`.
