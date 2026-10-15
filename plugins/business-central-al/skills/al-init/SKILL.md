---
name: al-init
description: Write a CLAUDE.md for a Business Central AL repository that records its real conventions (apps, ID ranges, affix, file naming, folder layout, namespaces, test setup, build and test commands, BC server), detected from the code, so every session starts with them.
disable-model-invocation: true
---

# Write the repo's CLAUDE.md for AL work

The biggest quality lever for AL in a given repo is Claude knowing that repo's rules up front. Detect them from the code; don't invent them, and don't copy generic BCApps defaults that the repo doesn't follow.

## Detect

1. **Apps**: every `app.json` (skip `.alpackages`): name, id, publisher, version, `platform`/`application`, `runtime`, `target`, `idRanges`, dependencies, `features`. Mark which are test apps (dependency on `Library Assert`/`Tests-TestLibraries`, or `Subtype = Test` codeunits inside).
2. **Affix**: `AppSourceCop.json` `mandatoryAffixes`; otherwise the prefix/suffix most object names share (sample object declarations with grep).
3. **File naming and folders**: list ~20 `.al` paths. Write down the pattern you actually see (e.g. `BC/CodeUnit/Codeunit 50100 - TAG Name.al` vs `src/Sales/SalesHelper.Codeunit.al`).
4. **Code style**: namespaces or not; variable/parameter naming (e.g. `p` prefix on parameters); license header text; XML docs used or not. Quote one short real example of each.
5. **Used ID map**: per object type, the highest ID in use and any gaps, so new IDs are picked correctly.
6. **Analyzers**: `.vscode/settings.json` `al.codeAnalyzers`, ruleset files.
7. **AL-Go**: `.AL-Go/settings.json` / `.github/AL-Go-Settings.json`: type, country, artifact, apps/testFolders.
8. **BC server**: `.claude/bc-server.json` and `.vscode/launch.json` configurations (names only, no secrets).

If the repo has an existing `CLAUDE.md` or `AGENTS.md`, or `.cursor/rules/*.mdc`, read them and carry over what's still true. Cursor rules from the old plugin setup often hold the house conventions.

## Write

Show the draft and ask before writing `CLAUDE.md` at the repo root. Keep it short (under ~100 lines): facts and rules Claude would otherwise get wrong, not AL tutorials. Sections:

```markdown
# <Repo> (Business Central AL)

## Apps
<table: app, folder, ID range, target, depends on>

## Conventions (follow these over BCApps defaults)
- Affix: ... ; object names ≤ 30 chars including it
- File naming: <pattern> e.g. `<real example>`
- Folders: ...
- Variables/parameters: ...
- Namespaces: ...
- License header: ...

## Next free IDs
<per object type>

## Build, test, run
- Compile: AL MCP `al_compile` (project: <path>)
- Tests: /al-run-tests (test app: <name>, server: <bc-server.json name or "none yet">)
- UI checks: /al-ui-test (recordings in <path>)
- CI: AL-Go CI/CD on push

## How to work here
- New object: `al_getnextobjectid` for the ID. Unsure a field/event/procedure exists: `al_symbolsearch` or the bc-explorer agent; never guess.
- Writing a test: the al-write-test skill. Fixing a bug: failing test first, trace the call path (`/al-call-graph`) before editing.
- Before saying done: compile clean, `/al-run-tests` green, `/al-ui-test` for page changes. Review: `/bcq-review`.

## Gotchas
<anything surprising you found: customer-specific behaviour, deprecated objects still in use, etc.>
```

Keep the "How to work here" section even though the plugin's session-start context says similar things: Microsoft's BC-Bench found agents rarely invoke skills unprompted, and a short nudge in the repo's own CLAUDE.md is what makes them fire.

After writing, mention that the user can commit it so the whole team (and Cursor via `AGENTS.md`, if they mirror it) get the same context.
