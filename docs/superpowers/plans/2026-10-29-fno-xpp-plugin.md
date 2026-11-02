# F&O X++ plugin: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

- **Goal:** let Claude Code (and later Codex) build whole features in Dynamics 365 Finance & Operations (X++) the way `business-central-al` lets them build AL. That means checking real symbols instead of guessing, compiling, syncing the database, running tests and checking the UI on a real F&O, plus a structured review.
- **Architecture:**
  - **Where agents run:** on a Windows F&O dev machine. X++ only compiles there (`xppc` against `PackagesLocalDirectory`, "PLD"). Unlike AL, there is no Linux compiler and no language server.
  - **The MCP:** the community [d365fo-mcp-server](https://github.com/dynamics365ninja/d365fo-mcp-server) (MIT, npm `d365fo-mcp`, 1.21.0). It indexes PLD for symbol search. It creates and changes objects through Microsoft's metadata API (a C# bridge), registered in the `.rnrproj`. It also builds, runs best-practice checks, syncs the database and runs SysTest. Microsoft ships no X++ MCP server or language server.
  - **The plugin, `dynamics-fno-xpp`:** adds what the MCP lacks: conventions, feedback loops, test writing, UI checks (Playwright), a structured review and hooks.
  - **The Linear-to-agent pipeline comes last.** It needs a decision first (Phase 4).
- **Facts as of 2026-10-29** (machine identifiers are kept out of this public repo):
  - **Machine:** an LCS cloud-hosted dev VM running **F&O 10.0.46** (platform 7.0.7778), Windows Server 2022, VS 2022 17.14, .NET 4.8 and .NET SDK 9.
  - **Tools present:** `xppc`, `xppbp`, `SyncEngine` and `SysTestConsole.17.0.exe`.
  - **Tools missing:** Node, Python, Claude Code, Codex, d365fo.tools, OpenSSH.
  - **Disk:** the system drive has ~9 GB free; the data drives have hundreds of GB.
  - **Model:** The Asset Guardian (`TheAssetGuardian`, ISV layer, ~680 objects, 1 test class). Its source repo (`FNO-Schema`) is cloned straight into `PLD\TheAssetGuardian`, along with 8 Cursor rule files (`.cursor/rules/fno-*.mdc`) from January 2026.

## Global constraints

- **This repo is public.** No hostnames, subscription or tenant IDs, customer names or secrets in any committed file.
- **One copy of the model per machine, so one agent at a time.** PLD holds exactly one copy of each model at a fixed path, so git worktrees can't be used for the model folder. Phase 4 has to solve this before agents run in parallel.
- Agents change only `TheAssetGuardian`: extensions, Chain of Command (CoC) and event handlers. They never touch Microsoft packages and never overlayer.
- Database sync only adds. Dropping or retyping fields that hold data needs the user to name it, the same as the `ForceSync`/`Recreate` rule in `business-central-al`.
- Hooks must run on Windows: no `python3` on PATH there. Call Python through a launcher that works on both OSes.
- Ship and commit rules are the same as the other plugins: bump the version, commit with explicit paths, add the `Co-Authored-By` trailer.

## Phase 0: prepare the VM

The user does:
- [ ] Commit or stash the uncommitted changes in `PLD\TheAssetGuardian` (several forms and tables, plus the deleted `FNO_MAX.rnrproj`).
- [ ] Renew the SSL certificate in LCS: environment > Maintain > Rotate secrets > SSL. It expired on 2026-07-06. Until then, browsers need `thisisunsafe` and Playwright needs `ignoreHTTPSErrors`.
- [ ] Sign in to Tailscale on the VM (interactive), so the developer's machine and the agent server can reach it without opening port 22 to the internet.

The agent does (through `az vm run-command` or RDP):
- [ ] Install Node 24 LTS and Python 3. Put the npm prefix and cache and `PLAYWRIGHT_BROWSERS_PATH` on a data drive.
- [ ] Install Claude Code, native on Windows. There's an open startup-hang issue on Server 2022 ([#100969](https://github.com/anthropics/claude-code/issues/100969)); if it hits, fall back to WSL (nested virtualization is enabled). Hold Codex back: its sandbox fails when Codex starts from an OpenSSH session ([openai/codex#37722](https://github.com/openai/codex/issues/37722)).
- [ ] Install d365fo.tools from the PowerShell Gallery.
- [ ] Install d365fo-mcp-server (`npm i -g d365fo-mcp`, then `d365fo-mcp setup` with `D365FO_MCP_YES=1`). Build the PLD index in the background; the author says it takes hours.
- [ ] Install OpenSSH Server, listening on the Tailscale address only.
- [ ] Add a nightly auto-shutdown to the VM.

## Phase 1: prove the loop by hand (gates everything after it)

For each step, record the command, how long it took, whether it needs admin rights or stopped services, and what the output looks like. The skills will quote that output as evidence.

- [ ] **Build:** `build_d365fo_project` on TheAssetGuardian, compared with `Invoke-D365ModuleBuild -Module TheAssetGuardian`.
- [ ] **Best practices:** `run_bp_check` on a few TAG objects.
- [ ] **Database sync:** a module or partial sync of TAG tables.
- [ ] **Tests:** `run_systest_class` on `TAGEnumTest` (`SysTestConsole.17.0.exe`).
- [ ] **Symbol truth:** look up an Asset Management table and method, a CoC target and a label. Every answer must cite a file path.
- [ ] **Object write:** create a throwaway EDT through the MCP, check that it's registered in the `.rnrproj`, build, then revert it.
- [ ] **UI:** Playwright MCP signs in once (manual MFA, session saved), opens a TAG form and reads its grid.
- [ ] **Decision:** the MCP is tested on 10.0.47/10.0.48, not 10.0.46. If it fails here, fall back to d365fo.tools plus [TrudAX/d365fo-xpp-skills](https://github.com/TrudAX/d365fo-xpp-skills) (MIT) for build and where-used, and to `rg` over PLD for symbols.

## Phase 2: the `dynamics-fno-xpp` plugin (core)

What carries over from `business-central-al`: about 20 of its ~90 skills have an F&O equivalent. About 30 are AL-Go or AppSource lifecycle skills; F&O has its own lifecycle (Azure DevOps builds, deployable packages, LCS or Power Platform admin center deploys), which is a later, separate skill set. About 20 are BCQuality review domains whose content has to be written (Phase 3).

| `business-central-al` | `dynamics-fno-xpp` | Source |
| --- | --- | --- |
| AL MCP (compile, symbols, diagnostics) | d365fo-mcp-server | community, MIT |
| AL language server (`.lsp.json`) | none exists; the MCP's symbol tools replace it | n/a |
| `al-base-app-source` | not needed: PLD holds all standard source as XML | n/a |
| `bc-explorer` agent | `fno-explorer` agent: standard-app lookups citing PLD `file:line` | new |
| `al-conventions` (path-scoped) | `xpp-conventions`, scoped per `Ax*` folder | port of the 8 Cursor rules |
| `al-feedback-loops` | `xpp-feedback-loops` | new |
| `al-compile`, `al-build` | `xpp-build` | MCP, d365fo.tools |
| publish + schema sync | `xpp-db-sync` | MCP, d365fo.tools |
| `al-run-tests` | `xpp-run-tests` | MCP (`SysTestConsole`) |
| `al-write-test`, `business-central-al-tdd`, scaffolds | `xpp-write-test`, `fno-tdd` (SysTest and the Acceptance Test Library) | Learn docs |
| `al-ui-test` (page scripting) | `xpp-ui-test` (Playwright MCP) | new. Task Recorder stopped working on cloud-hosted environments in January 2026, and RSAT is unsupported after May 2027 |
| `al-init`, `al-setup`, `bc-server-setup` | `fno-init` (writes CLAUDE.md), `fno-vm-setup` | new |
| `al-code-review`, `bcq-review-*` | `xpp-review` super-skill plus 5 domains | Phase 3 |
| `SessionStart` hook | detects `Descriptor/*.xml` plus `Ax*/`, then lists model, layer, references, prefix, MCP and VM status | new |
| `al-lint` post-edit hook | `xpp-xml-lint`: well-formed XML, CDATA, lowercase booleans, `.rnrproj` registration, TAG prefix, nothing outside the model | the Cursor rules' error tables |
| `al-snapshot-debug`, `al-profile` | later: Trace Parser (TrudAX skill), the MCP's read-only `axdb_sql` | community |
| AL-Go and AppSource skills | later: Azure DevOps build pipeline, deployable package, deploy | Microsoft samples |

Tasks:
- [ ] Scaffold `plugins/dynamics-fno-xpp/` (`plugin.json`, README, CHANGELOG, LICENSE) and add it to `.claude-plugin/marketplace.json`.
- [ ] `.mcp.json`: d365fo-mcp (stdio on the VM) and Playwright MCP.
- [ ] Hooks: session-start and `xpp-xml-lint`, written in Python with a Windows-safe launcher. Unit tests for both.
- [ ] Skills from the table above. Each one references the Phase 1 commands and evidence formats.
- [ ] A `claude plugin eval` suite modelled on `vsd-feature-lifecycle/evals`.
- [ ] `vsd-feature-lifecycle`: recognise F&O repos (`Descriptor/*.xml`), add the install line and a "needs an F&O test run" hand-off.
- [ ] Run `fno-init` in FNO-Schema to write its CLAUDE.md/AGENTS.md. Keep `.cursor/rules` for Cursor users.

## Phase 3: review content (the BCQuality equivalent)

Microsoft publishes no BCQuality, BCApps prompts or benchmark for X++. Seed the knowledge base from:
- **The TAG Cursor rules:** proven on this model.
- **[microsoft/Dynamics365FO-AppChecker](https://github.com/microsoft/Dynamics365FO-AppChecker):** 21 X++ rules (MIT). The repo is stale (last push 2025-06), but the rules still apply.
- **The 27 `BPCheck*` rules** listed on the [Customization Analysis Report](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/customization-analysis-report) page.
- **A selected slice of the Learn docs** in [MicrosoftDocs/dynamics-365-unified-operations-public](https://github.com/MicrosoftDocs/dynamics-365-unified-operations-public) (text CC BY 4.0, so attribute it): `dev-ref/xpp-*`, `extensibility/`, `perf-test/`. That's about 150 of the 1,449 dev-itpro files.
- **[Success by Design: extend F&O apps](https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/extend-your-solution-guidance-product-fo):** the go-live checklist.

Use BCQuality's article frontmatter and JSON findings schema, so the review super-skill keeps the same shape. Start with 5 domains:
- **extensibility:** CoC, events, no overlayering;
- **performance:** set-based operations, caching, select patterns;
- **security:** privileges, duties and roles for new menu items;
- **data-modeling:** tables, indexes, relations, delete actions, EDTs;
- **UI:** form patterns, labels.

## Phase 4: the agent pipeline (decision needed)

Because one machine holds one copy of the model, the Linear-to-agent runs on the agent server can't simply get a worktree each. Options:
1. **Lease the VM, like `al-test` does.** Lock it, check the agent's branch out into PLD, then build, sync, test and report. Runs take minutes and go one at a time, and nobody can work on the VM by hand meanwhile.
2. **A second dev VM just for agents.** It costs another always-on 16-core VM, and new LCS projects are frozen (2026-02-16), so check that the existing project can still deploy one.
3. **UDE** (see below). Each agent machine compiles locally and deploys to its own Power Platform-hosted environment.

## Parallel track: evaluate UDE

- **Microsoft's only supported route for agents:**
  - the `pac` CLI: `pac package compile/deploy/db-sync`, in preview, Windows only;
  - Microsoft's [`erp-xpp` skill](https://github.com/microsoft/Dataverse-skills/tree/main/.github/plugins/dataverse/skills/erp-xpp);
  - the [Dynamics 365 ERP MCP server](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp) for checking behaviour after deployment. It needs 10.0.47 (or 10.0.46 PQU-2), is not supported on cloud-hosted environments, and charges 0.1 Copilot credits per call outside Copilot Studio.
- **Needs:**
  - a Windows 10/11 machine (Windows Server isn't listed);
  - VS 2022 with Power Platform Tools;
  - 16 GB of free disk;
  - Power Platform capacity for an F&O dev environment.
- **LCS:**
  - new projects have been frozen since 2026-02-16;
  - moving existing projects to the Power Platform admin center went into preview in September 2026;
  - no end date for cloud-hosted environments has been announced.
- **Visual Studio:** from platform update 74 (10.0.49), Visual Studio 2026 is required. This VM has VS 2022, which matters at the next upgrade.

## Still unverified

- d365fo-mcp-server on 10.0.46 (Phase 1 settles it).
- `SysTestConsole` switches: Microsoft doesn't document them; the MCP wraps them.
- Admin rights, service stops and timings for sync and tests.
- Claude Code's startup on this Windows Server 2022 VM.
