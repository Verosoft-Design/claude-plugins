---
name: fno-init
description: Write a CLAUDE.md (and optionally AGENTS.md) for a Dynamics 365 F&O X++ repository that records its real conventions (packages, module vs model name, layer, prefix, references, .rnrproj projects, object folders, labels, tests, build leftovers, dev VM), detected from the code and any .cursor/rules, so every session starts with them.
disable-model-invocation: true
---

# Write the repo's CLAUDE.md for X++ work

The biggest quality lever in a given repo is Claude knowing its rules up front. Detect them from the code; don't invent them, and don't copy generic conventions the repo doesn't follow.

## Detect

1. **Packages and models:** every `Descriptor/*.xml` (AxModelInfo) within 3 levels:
   - `ModelModule` (the package or module name) vs `Name` (the model folder, which may contain spaces);
   - `Layer`, `Publisher`, version;
   - `ModuleReferences`.

   Say plainly when module and model name differ: several tools need one or the other (`reference/d365fo-mcp.md`).
2. **Live checkout?** If the repo folder is inside `PackagesLocalDirectory`, a build compiles whatever is checked out, so record that.
3. **Prefix and naming:** the prefix most object names share (the session-start hook prints it), the extension naming (`<Base>.<Suffix>`), class suffixes (`_Extension`, `Handler`), EDT naming (`TAG<Table>RecId`). Quote 2–3 real names of each.
4. **Projects:** each `.rnrproj`, its `<Model>`, and how many objects it registers. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/xpp-xml-lint.py` over the model and note the XPP012 hits: objects on disk but not in the project.
5. **Object inventory:** counts per `Ax*` folder. Note which kinds the repo hand-edits (tables, EDTs, enums, classes) and which it builds in the designer (forms).
6. **Labels:** label files (`AxLabelFile`), languages, and whether objects use label IDs or literal text (sample `<Label>` values). Literal text means xppbp reports `BPErrorLabelIsText`.
7. **Tests:** classes extending `SysTestCase`, and a test package if any. Say "none" if there are none.
8. **Existing guidance:** `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*.mdc`, `README`/`*.md` notes in the model folder. Carry over what's still true; the plugin's `reference/` files hold the ported TAG rules with corrections.
9. **Git hygiene:** build outputs that are tracked or not ignored (`BuildModelResult.*`, `BuildProjectResult.*`, `CompileLabels.xml`, `*.xref`, `Resources/*.delete`, `bin/`, `XppMetadata/`). Suggest `.gitignore` lines, but don't change it without asking.
10. **Dev VM:** `.claude/fno-vm.json` from `fno-vm-setup` (URL, PLD path, default company). Names only; never secrets.

## Write

Show the draft and ask before writing `CLAUDE.md` at the repo root. Keep it short (under ~100 lines): facts and rules Claude would otherwise get wrong, not X++ tutorials.

```markdown
# <Repo> (Dynamics 365 Finance and Operations, X++)

## Model
- Package/module `<Module>`, model `<Model name>` (layer <n>, publisher <p>). Folder: `<Module>/<Model name>/`.
- References: <list>. Only these packages' objects can be used.
- Prefix `<PFX>` on every object and every field added to a standard table. Extensions: `<Base>.<Module>`.

## Working rules
- Edit only `<Module>/<Model name>/`. Extensions, CoC (`*_Extension`), event handlers; never a Microsoft package.
- Register every new object in `<project>.rnrproj`.
- Look up standard names with the d365fo MCP before using them.
- <repo-specific rules, e.g. labels, enum conventions, form patterns in use>

## Build and test
- Dev VM: <how to reach it; PLD path>. Build: `xpp-build` (module `<Module>`). Sync: `xpp-db-sync`. Tests: `xpp-run-tests` (<test classes or "none yet">).
- Never build or sync while someone else has uncommitted changes in the model.
```

For Codex and other agents, offer an `AGENTS.md` with the same content (or one line pointing to `CLAUDE.md`). Keep `.cursor/rules` for Cursor users.
