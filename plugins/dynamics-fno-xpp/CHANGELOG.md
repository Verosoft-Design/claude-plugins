# Changelog

## 0.1.0 — 2026-10-29

First release: the `business-central-al` setup mapped to Dynamics 365 Finance and Operations (X++). Plan: `docs/superpowers/plans/2026-10-29-fno-xpp-plugin.md`.

### Decisions (2026-11-02)

- **Labels:** label IDs everywhere, enums included. TAG's January "literal text" rule is retired: raw label IDs in dropdowns come from uncompiled labels or a wrong file ID (TAG's is `TAGLabels`). The reference templates now use label IDs.
- **Tests:** they live in the model under test (TAG), which references `TestEssentials`, plus the ATL packages when a test uses ATL.

### What was checked on a real 10.0.46 dev VM

Platform 7.0.7778, d365fo-mcp-server 1.21.0.

- **Read-only MCP tools:** `search`, `get_object_info`, `find_references`, `extension_info`, `labels` and `get_knowledge` answer in 1.6–2.6 s.
  - With `bridge.xrefDbName: DYNAMICSXREFDB`, `find_references` returns exact code-plus-metadata counts: 4,503 references to `EntAssetObjectTable`, against 15 from the name scan without it.
- **Best practice:** `xppbp.exe` called directly checks a table, form, class or table extension in about 4 s each (23 s cold). Before/after snapshots of the model folder were identical.
- **Hooks on Windows:** both hooks run through the node launcher. The unit tests pass on Linux (Python 3.12) and Windows (Python 3.13).
- **Lint:**
  - on the TAG model's 454 objects: 1 error (a committed `<Name>` that differs from its file name) and 7 warnings (objects not registered in the `.rnrproj`), all real;
  - on 5,564 standard objects: nothing except "this is a Microsoft package".

### Not yet run (skills say "verified: pending")

Build, database sync, SysTest and the Playwright UI loop. The commands come from the tools' sources and from d365fo.tools `-OutputCommandOnly`.

### Contents

- **MCP** (`.mcp.json`):
  - `d365fo` (d365fo-mcp-server) and `playwright` (`@playwright/mcp`);
  - both start through `scripts/mcp-launch.mjs`, because `npx` and npm `.cmd` shims can't be exec'd on Windows.
- **Hooks:** `SessionStart` (model, module vs model name, layer, references, prefix, projects, live-PLD checkout, VM or not) and a `PostToolUse` XML lint with 18 checks (XPP001–XPP018).
  - Both run in exec form through `scripts/run-python.mjs`, which finds `py -3`, `python` or `python3`. F&O VMs have no `python3.exe`.
- **Lint data:** `scripts/xpp_xml_facts.json`, from a survey of 143,603 standard XML files and the compiler's reserved words. The reserved-word list comes from d365fo-mcp-server (MIT License, Copyright (c) 2026 dynamics365ninja), which captured it from xppc 7.0.7996.33.
  - Which properties take `true`/`false` (30) and which take `Yes`/`No` (137).
  - The 37 form control types and 62 form patterns with their versions, and the root namespace per object type.
- **Skills:**
  - conventions: `xpp-conventions` (path-scoped) plus `xpp-conventions-tables`, `-forms`, `-enums` and `-classes`;
  - loops: `xpp-feedback-loops`, `xpp-build`, `xpp-db-sync`, `xpp-run-tests`, `xpp-write-test` (SysTest plus ATL), `xpp-ui-test` (Playwright MCP);
  - setup: `fno-init`, `fno-vm-setup`.
- **Agent:** `fno-explorer`, read-only, with an allowlist of the MCP's read tools.
- **Script:** `scripts/xpp-bp-check.ps1`, which runs xppbp with the module and model names from the Descriptor. A target xppbp didn't evaluate exits 2 ("NOT CHECKED"), never "clean".
- **Reference:** the 8 TAG Cursor rules (January 2026) ported to `reference/`, plus `reference/d365fo-mcp.md`.
- **Tests:** 85 stdlib `unittest` tests for the hooks and the launcher.
- **Review content, draft** (`content/xppquality/`):
  - BCQuality's layout and article format, with `fno-version` in place of `bc-version`;
  - five domains (extensibility, performance, security, data-modeling, ui) with 8 seed articles that pass BCQuality's validator;
  - `SOURCES.md` lists the exact files to vendor next, with pinned commits and licences: 153 Learn pages (CC BY 4.0 text, MIT code) and AppChecker's 21 X++ rules (MIT).

  The security seed comes from a real finding: xppbp reports `BPErrorMenuItemNotCoveredByPrivilege` on a menu item of a custom model that defines no privileges.

### Corrections to the January 2026 Cursor rules (checked 2026-10-29)

- **Booleans:** "Use lowercase true/false, never Yes/No" holds for about 30 properties only. Most take `Yes`/`No`.
- **Reserved words:** `table`, `field`, `insert`, `update` and `delete` are not reserved. `count`, `index`, `select`, `next`, `order`, `group` and `sum` are (the compiler's list).
- **Patterns:** there are no `DetailsFormMaster`/`DetailsFormTransaction` patterns; the real ones are `DetailsMaster`/`DetailsTransaction` 1.4.
- **Commands:** standard forms use the `Save` and `CloseForm` commands.
- **Enums:** labels written as literal text conflict with `BPErrorLabelIsText`. Left as an open question for the repo owner.
- **Unchecked:** `query.topRows()` (a kernel class the index doesn't cover).
- **Templates:** a data-source template that puts `<Methods>` inside `<AxFormDataSource>` contradicts the forms rule; it is flagged in place.

### d365fo-mcp-server 1.21.0 quirks found (in `reference/d365fo-mcp.md`)

- **Module vs model name:** `run_bp_check` and `build_d365fo_project` pass one name as both. For a model whose name differs from its module, BP check reports `ModuleNotFound`, or "clean" without evaluating anything.
- **Label compile:** `run_bp_check` runs `labelc` first, which writes `Resources\*.dll` when label sources are newer.
- **SysTest runner:** `run_systest_class` looks for `SysTestConsole.exe`; 10.0.46 ships `SysTestConsole.17.0.exe`.
- **Same-named objects:** `extension_info` (mode `coc`) mixes up a table and a form with the same name.
