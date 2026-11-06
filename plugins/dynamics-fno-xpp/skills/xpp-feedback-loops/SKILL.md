---
name: xpp-feedback-loops
description: How to check, build, sync, test, reproduce and look at the UI in Dynamics 365 Finance and Operations X++, ranked by speed, with what each loop proves and what was verified on a real 10.0.46 dev VM. Use whenever a process skill (superpowers test-driven-development, systematic-debugging, verification-before-completion; mattpocock tdd, diagnosing-bugs) asks for a build, a test run, a red-capable repro or verification evidence in an F&O repo, or before claiming X++ work is done or fixed.
---

# X++ feedback loops

Process skills (superpowers, mattpocock-skills) say *when* to build, write a failing test or reproduce a bug. This skill says *how* on F&O. Pick the fastest loop that can actually go red on the thing you care about.

**Status (2026-10-29, F&O 10.0.46, d365fo-mcp-server 1.21.0):** the read-only loops were run on a real cloud-hosted dev VM. **Build, sync, SysTest and the UI loop are "verified: pending"**: they were not run, because the model had someone's uncommitted work in it. The commands come from the tools' own sources and `-OutputCommandOnly`. Treat the first real run of each as a check of this skill, and report any difference.

## The loops, fastest first

| Loop | Command | Proves | Needs | Verified |
| --- | --- | --- | --- | --- |
| XML lint | automatic after each edit; `python ${CLAUDE_PLUGIN_ROOT}/scripts/xpp-xml-lint.py <files>` | well-formed XML, CDATA, property styles, control types, patterns, `.rnrproj` registration, prefix, reserved words | Python | yes: 0.2 s; 0 false positives on 5,564 standard files |
| Symbol truth | MCP `search`, `get_object_info`, `extension_info`, `labels`; the `fno-explorer` agent | the table, field, method, label or control exists with that signature | the MCP | yes: 1.6–2.6 s |
| Where-used | MCP `find_references` | what a change reaches, in code and metadata | the MCP with `bridge.xrefDbName` | yes: 2–14 s |
| Code checks | MCP `validate_code` / `analyze_code` on code you pass in | known X++ mistakes, before writing | the MCP | not run |
| BP check | `powershell -File ${CLAUDE_PLUGIN_ROOT}/scripts/xpp-bp-check.ps1 -Package <package> -Targets Table:X,Class:Y` | Microsoft's best-practice rules on those objects | the VM | yes: about 4 s per object, 23 s cold |
| Build | MCP `build_d365fo_project` (`bpCheck: true`), or `Invoke-D365ModuleBuild -Module <Module>` (`xpp-build`) | it compiles: xppc plus labels | the VM, a model with no one else's uncommitted work | pending |
| DB sync | `build_d365fo_project` `dbSync: [tables]`, or `Invoke-D365DbSyncPartial -SyncList …` (`xpp-db-sync`) | tables and fields exist in AxDB | the VM | pending |
| SysTest | `SysTestConsole.17.0.exe /test:<Class> /xml:<file>` (`xpp-run-tests`) | behaviour: validation, posting, defaults, events | the VM, a built model, a SysTest class | pending |
| UI | Playwright MCP against the VM's F&O URL (`xpp-ui-test`) | the form renders, the lookup shows codes, the button does its thing | the VM's web client, a signed-in profile | pending |
| Data check | read-only `sqlcmd -E -d AxDB -Q "SELECT … WHERE DATAAREAID = 'usmf'"` | what was actually written | the VM (SQL is local) | sqlcmd verified on `sys.databases` only |

A clean BP check is not a build: xppbp reads the last *compiled* metadata and does not diagnose compiler errors. A build is not behaviour: it says nothing about defaults, validation or posting. Most X++ bugs are behaviour bugs.

## Mapping process steps to loops

- **TDD red/green:** the red step is a SysTest method (`xpp-write-test`) run by `xpp-run-tests` that fails on the assertion you expect, not on a compile error or missing data. Without a VM run, say "test written, not run" and stop claiming red/green.
- **Debugging / building a repro loop**, in order of preference:
  1. a failing SysTest that reproduces the symptom;
  2. a Playwright script of the user's click path (`xpp-ui-test`);
  3. a read-only SQL query that shows the wrong data;
  4. the user's exact steps, data and company.

  A repro that only runs in someone's head is not a loop.
- **Locate before you fix:** `find_references` and `extension_info` (modes `coc`, `events`) show who else touches the code path. Another model's CoC wrapper or event handler is often the real cause.
- **Verification before completion:** quote the evidence:
  - the lint result;
  - the build summary (errors 0) from `xpp-build`;
  - the SysTest totals from `xpp-run-tests`;
  - the UI check for UI changes.

  When the VM isn't available, or the build is blocked by someone's uncommitted work, the honest status is "XML lint clean, BP check clean on X and Y; not compiled; not run".

## F&O traps that make loops lie

- **The model folder is shared.** A build or sync on the dev VM compiles everything in `PackagesLocalDirectory\<Package>`, including other people's uncommitted edits. Before building, run `git -C <package> --no-optional-locks status --porcelain`. If any change isn't yours, stop and ask.
- **Module name ≠ model name** (`TheAssetGuardian` vs `The Asset Guardian`). The MCP's `run_bp_check` then fails, or reports "clean" without checking. Use `xpp-bp-check.ps1`, and give `build_d365fo_project` the module name. See `${CLAUDE_PLUGIN_ROOT}/reference/d365fo-mcp.md`.
- **Stale compiled metadata:** xppbp and the cross-reference database reflect the last build. Objects edited since then give mixed answers until you build again.
- **Labels:** `labelc` compiles label files into `<package>\Resources`. A label created by hand-editing shows as a literal ID until labels compile. Builds and the MCP's `labels` tool do it.
- **New enums:** the first build after adding an enum and code that uses it can fail with "Qualifier not valid". Build again before calling it a bug.
- **The AOS keeps the old assemblies** until IIS restarts. Tests and UI after a build need `build_d365fo_project` `restartAos: true`, or a restart from Visual Studio. Pending verification.
- **Company and data:** demo companies (`usmf`…) hold different data. Tests create their own data (Acceptance Test Library or their own setup); don't rely on demo records.
- **Schema sync only adds.** Dropping, renaming or retyping a field that holds data needs the user to name it, the same as `ForceSync` in AL.
- **Secrets in command lines:** `Invoke-D365DbSync* -OutputCommandOnly` prints the AxDB SQL password. Never paste that output anywhere.
