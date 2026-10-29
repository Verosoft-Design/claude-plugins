---
name: xpp-conventions
description: Dynamics 365 Finance and Operations X++ metadata conventions (model boundaries, naming and prefix, extensions, .rnrproj registration, XML editing rules, property value styles, reserved words) and the lint codes, with the full reference docs. Loads automatically when working on AOT XML (Ax* folders), Descriptor files and .rnrproj projects.
user-invocable: false
paths:
  - "**/Ax*/*.xml"
  - "**/Descriptor/*.xml"
  - "**/*.rnrproj"
---

# X++ conventions

**The repository's own conventions win.** Read its `CLAUDE.md` or `AGENTS.md` first (`/fno-init` writes one). Then sample 2–3 neighbouring objects in the same `Ax*` folder before creating or renaming anything: prefix, naming, labels, property style. The rules below come from TAG's Cursor rules (January 2026), corrected against F&O 10.0.46 on 2026-10-29. They apply where the repo has nothing more specific.

Folder-specific rules load on their own: `xpp-conventions-tables` (AxTable, AxTableExtension, AxEdt), `xpp-conventions-forms` (AxForm, AxFormExtension, AxTile), `xpp-conventions-enums` (AxEnum) and `xpp-conventions-classes` (AxClass).

## Must-haves

- **Your model only.** Edit files under `<Package>/<Model name>/` of this repo's model. Never touch a Microsoft package (lint XPP015) or another model; extend instead: table/form/enum extensions, Chain of Command (`[ExtensionOf]`, class name ends in `_Extension`), event handlers. No overlayering.
- **Look up, don't guess.** Every standard table, field, method, EDT, enum value, label and form control you reference must come from the d365fo MCP (`search`, `get_object_info`, `find_references`, `extension_info`, `labels`) or the `fno-explorer` agent, with the path it was found at. Kernel classes (`Query`, `DictTable`, `FormRun`) aren't indexed; compile to confirm those.
- **Prefer the MCP's writers** on the VM: `d365fo_file` (create, modify), `generate_object`, and `labels` (create). They write through Microsoft's metadata API, register the object in the `.rnrproj` and refresh the index. Ask `get_knowledge` (kind `op-spec`) for each operation's contract. Hand-edit XML when the MCP isn't reachable, then call `update_symbol_index` with the paths.
- **Names:** every new object and every field added to a standard table starts with the model prefix (the session context shows it; TAG uses `TAG`) (XPP013). Extensions are named `<Base>.<Model or suffix>`, e.g. `EntAssetObjectTable.TheAssetGuardian`. `<Name>` equals the file name (XPP004).
- **Register** every new object in the package's `.rnrproj`: `<Content Include="AxTable\TAGFoo">` with `SubType`, `Name` and `Link`, like its neighbours (XPP012).
- **XML:** well-formed (XPP001); keep node order; minimal diffs, no reformatting; X++ inside `<![CDATA[ ... ]]>` (XPP002); the root element and namespace standard XML uses for that folder (XPP003, XPP005).
- **Property values:** most properties take `Yes`/`No` (`AllowEdit`, `Mandatory`, `InsertIfEmpty`…); about 30 take lowercase `true`/`false` (`IsExtensible`, `AllowBlank`, `Nullable`…). Copy a standard object, and trust the lint (XPP006).
- **Labels:** user-visible text should be a label ID (`@TAGLabels:MyLabel`). xppbp reports literal text as `BPErrorLabelIsText`. Create labels with `labels` (action `create`, `createIfMissing: true`). TAG's January rule used literal text for enum values; see `xpp-conventions-enums` before changing an existing enum.
- **X++:** don't use reserved words as names (`count`, `index`, `select`, `next`, `order`, `group`, `sum`…; `table`, `field`, `insert`, `update`, `delete` are allowed) (XPP017). In selects, `order by` comes before `where` (XPP018). Respect `DataAreaId`, and never hardcode URLs, tenants or secrets.
- **Done means built:** after editing, build, sync if the schema changed, and test on the VM (`xpp-feedback-loops`). The lint and a BP check are not a compile.

## Stop and ask

- You can't confirm a base object's exact name or kind (`EntAssetObjectTable` is both a table and a form).
- The target is in another model, or a Microsoft package.
- A build or sync would compile someone else's uncommitted changes (the session context says when the checkout is the live model in PackagesLocalDirectory).
- A schema change would drop, rename or retype a field that holds data.
- A complex form layout. Use `generate_object` with a pattern, or Visual Studio's designer.

## Lint codes (xpp-xml-lint hook)

Runs after every Edit/Write on AOT XML, a Descriptor or a `.rnrproj`. CLI: `python scripts/xpp-xml-lint.py <files>`. `FNO_XPP_LINT=0` disables it; `FNO_XPP_PREFIX` sets the prefix.

| Code | Severity | Means |
| --- | --- | --- |
| XPP001 | error | XML not well-formed |
| XPP002 | error | `<![CDATA` without `[` ("Metadata element is not readable") |
| XPP003 | error | root element doesn't match the Ax* folder |
| XPP004 | error | `<Name>` differs from the file name |
| XPP005 | error | AxEdt not `xmlns=""` with `i:type`; AxForm not the V6 namespace |
| XPP006 | error | `true`/`false` on a Yes/No property, or the reverse |
| XPP007 | error | form control type that doesn't exist (`AxFormIntControl` → `AxFormIntegerControl`) |
| XPP008 | error | command `SaveAndClose` / `SystemDefinedCloseButton` |
| XPP009 | error/warning | form pattern or version that no standard form uses |
| XPP010 | error | `<EnumValue>` instead of `<Value>`; several enum values without `<Value>` |
| XPP011 | error | DeleteAction without `<Table>`; PrimaryIndex allows duplicates |
| XPP012 | warning | object not in the `.rnrproj` |
| XPP013 | warning | missing prefix; extension not `<Base>.<Suffix>` |
| XPP014 | error | `[ExtensionOf]` class not ending in `_Extension` |
| XPP015 | error | file in a Microsoft package |
| XPP016 | warning | CoC wrapper with a default parameter value |
| XPP017 | error | reserved word as a variable or parameter name |
| XPP018 | warning | `order by` after `where` in a select |

Its data (`scripts/xpp_xml_facts.json`) comes from 143,603 standard XML files on 10.0.46 and the compiler's reserved-word list. On 5,564 standard objects it reports nothing but XPP015.

## Full references (read the one you need)

| Topic | File |
| --- | --- |
| Core rules: principles, layout, naming, what to create, XML rules, hard stops | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-core.md` |
| Tables, relations, delete actions, RecId EDTs, indexes | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-tables.md` |
| Forms: structure, patterns, controls, extensions, workspaces, tiles | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-forms.md` |
| Enums | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-enums.md` |
| X++ patterns: event handlers, CoC, prepopulation, selects, form control access | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-classes.md` |
| XML templates | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-templates.md` |
| Build errors and fixes | `${CLAUDE_PLUGIN_ROOT}/reference/xpp-errors.md` |
| Asset Management tables and joins | `${CLAUDE_PLUGIN_ROOT}/reference/asset-management.md` |
| The d365fo MCP: tools, quirks, d365fo.tools equivalents | `${CLAUDE_PLUGIN_ROOT}/reference/d365fo-mcp.md` |
