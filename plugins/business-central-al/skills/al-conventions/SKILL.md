---
name: al-conventions
description: Business Central AL coding conventions (naming, files, labels, Locked, XML docs, license header, tests) with the full reference docs. Loads automatically when working on .al files and app.json.
user-invocable: false
paths: "**/*.al, **/app.json"
---

# AL conventions

**The repository's own conventions win.** Read its `CLAUDE.md` first, then sample 2–3 neighbouring `.al` files in the same folder before creating or renaming anything: file-name pattern, prefix/affix, namespace, folder, variable and parameter naming. The defaults below are Microsoft's BCApps conventions and apply only where the repo has none.

## Must-haves

- **Objects**: get IDs from `al_getnextobjectid` (`objectType`, `count`) right before creating objects; it stays inside `app.json` `idRanges` but only sees this project, so in a shared sandbox also check `al_symbolsearch` with `source: "environment"`. Without the AL MCP, grep the repo for the ID before using it. Names ≤ 30 characters including the affix. Extend base objects with `tableextension`/`pageextension`/event subscribers; never copy base-app code.
- **Files**: one object per file; BCApps pattern `<ObjectName>.<ObjectType>.al` unless the repo uses another (e.g. `Codeunit 50100 - TAG Name.al`).
- **Code**: PascalCase identifiers, lowercase keywords, 4-space indent, reference objects by name not ID, `namespace` + `using` at the top when the repo uses namespaces.
- **Labels** (checked automatically after each edit): suffix `Err`/`Msg`/`Qst`/`Lbl`/`Tok`/`Txt`; `Comment = '%1 = ...'` for every placeholder; `Locked = true` for URLs, tokens, telemetry text; `Error(MyErr, Value)`, never `Error(StrSubstNo(...))` or string concatenation.
- **Data**: `DataClassification` on every table field (not `ToBeClassified` in shipped code). `SetLoadFields` before `Get`/`Find` on wide tables; `IsEmpty()` instead of `Count() > 0`; filter before `FindSet`; no `Commit()` inside loops.
- **Public surface**: XML doc comments on `Access = Public` codeunit procedures, integration events and interface methods. Raise `OnBefore…`/`OnAfter…` integration events where partners need to extend.
- **Tests**: separate test app; `Subtype = Test`, `EventSubscriberInstance = Manual`, `Library Assert` (codeunit 130002), `[TransactionModel]` matching the code's `Commit` behaviour, `// [SCENARIO] / [GIVEN] / [WHEN] / [THEN]`, a handler for every UI call.

## Full references (read the one you need)

| Topic | File |
| --- | --- |
| Naming, files, namespaces | `${CLAUDE_PLUGIN_ROOT}/reference/al-naming-and-files.md` |
| Labels, suffixes, Locked | `${CLAUDE_PLUGIN_ROOT}/reference/al-labels-and-locked.md` |
| XML docs on public procedures | `${CLAUDE_PLUGIN_ROOT}/reference/al-xmldoc-public-procedures.md` |
| License header | `${CLAUDE_PLUGIN_ROOT}/reference/al-license-header.md` |
| Testing conventions | `${CLAUDE_PLUGIN_ROOT}/reference/al-testing.md` |
| General workflow | `${CLAUDE_PLUGIN_ROOT}/reference/al-workflow.md` |
| AL MCP tools and quirks | `${CLAUDE_PLUGIN_ROOT}/reference/al-mcp-usage.md` |
| Verosoft/TAG house rules (prefix, ID ranges, filenames, folders, `p` parameter prefix, API triplet) | `${CLAUDE_PLUGIN_ROOT}/content/bcquality/custom/knowledge/` |
| Microsoft's review knowledge, 19 domains (performance, security, privacy, upgrade, style, ui, error-handling, events, interfaces, breaking-changes, web-services, testing, data-modeling, query, reporting, appsource, telemetry, scm, finance) | `${CLAUDE_PLUGIN_ROOT}/content/bcquality/microsoft/knowledge/` |
