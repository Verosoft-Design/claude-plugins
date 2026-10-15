# Verosoft Design — Claude Code plugins

Claude Code plugin marketplace for Microsoft Dynamics 365 Business Central AL development. (Cursor plugins live in [cursor-plugin-marketplace](https://github.com/Verosoft-Design/cursor-plugin-marketplace).)

## Install

```sh
claude plugin marketplace add Verosoft-Design/claude-plugins
claude plugin install business-central-al@verosoft-design

# community process skills the BC plugin is designed to work with (installed from upstream, so they stay current)
claude plugin install superpowers@verosoft-design
claude plugin install mattpocock-skills@verosoft-design
```

Inside a session the same works as `/plugin marketplace add Verosoft-Design/claude-plugins` and `/plugin install ...`. Update with `claude plugin marketplace update verosoft-design`.

## Plugins

| Plugin | Source | What it is |
| --- | --- | --- |
| [`business-central-al`](plugins/business-central-al) | this repo | AL MCP + AL language server, AL-Go lifecycle, BCQuality review (19 domains), BC-Bench ALTest test generation, tests on a real BC (`al runtests`), web-client UI checks, snapshot debugging, profiling, call graph |
| `superpowers` | [obra/superpowers](https://github.com/obra/superpowers) | brainstorming, plans, TDD, systematic debugging, verification before completion |
| `mattpocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills) | grilling, spec and ticket flows, diagnosing bugs, TDD, code review |

Optional, from Microsoft: `claude plugin marketplace add microsoft/BC-ALAgents && claude plugin install al-review@bc-alagents` (Microsoft's BCApps PR reviewer; needs pwsh and a signed-in GitHub Copilot CLI).

## Layout

```text
.claude-plugin/marketplace.json
plugins/
  business-central-al/
    .claude-plugin/plugin.json
    .mcp.json  .lsp.json  hooks/  agents/  skills/  reference/  content/  scripts/
```

## Maintaining

Validate before pushing:

```sh
claude plugin validate . --strict
claude plugin validate plugins/business-central-al --strict
```

Upstream Microsoft content (BCApps, BCQuality, BC-Bench) is pinned in `plugins/business-central-al/content/PINNED.json` and refreshed with the plugin's `scripts/vendor-*.sh` (see `/bcq-update`).

MIT. See `LICENSE`.
