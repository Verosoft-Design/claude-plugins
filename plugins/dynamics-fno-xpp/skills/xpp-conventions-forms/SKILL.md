---
name: xpp-conventions-forms
description: X++ rules for forms, form extensions and tiles in F&O metadata XML (namespaces, required SourceCode elements, patterns and versions that really exist, control types, commands, ReferenceGroupControl lookups, master-detail, form extension parents, workspaces). Loads automatically when working on AxForm, AxFormExtension or AxTile files.
user-invocable: false
paths:
  - "**/AxForm/*.xml"
  - "**/AxFormExtension/*.xml"
  - "**/AxTile/*.xml"
---

# Forms, form extensions and tiles

Full rules and XML: `${CLAUDE_PLUGIN_ROOT}/reference/xpp-forms.md`; templates in `${CLAUDE_PLUGIN_ROOT}/reference/xpp-templates.md`. Core rules: the `xpp-conventions` skill.

Forms are the most fragile objects to hand-write. Prefer `generate_object` (mode `scaffold:form` or `pattern`) with a pattern from `object_patterns`, or copy a standard form of the same pattern. Hand-edit in small steps and build after each.

- **Root and namespaces:** `<AxForm xmlns:i="…" xmlns="Microsoft.Dynamics.AX.Metadata.V6">` (lint XPP005); inner `Methods`, `DataSources`, `DataControls` and `Members` carry `xmlns=""`. `<SourceCode>` holds all four, even when empty. End with `<Parts />`.
- **Data source methods** go in `<SourceCode><DataSources>`, matching an `<AxFormDataSource>` of the same name in `<DataSources>`. Both must agree.
- **Patterns:** use only pattern/version pairs that standard forms use: `SimpleList` 1.1, `SimpleListDetails` 1.3, `DetailsMaster` 1.4, `DetailsTransaction` 1.4, `ListPage` UX7 1.0, `Dialog` 1.2, `TableOfContents` 1.1, `Workspace…`. Not `DetailsFormMaster`, `DetailsFormBasic` or plain `SimpleDetails` (lint XPP009). When unsure, drop `Pattern`/`PatternVersion`. In a `FieldsFieldGroups` tab, leave `HeightMode`/`WidthMode` out. `FillText` needs `WidthMode` `SizeToAvailable`.
- **Control types** must exist: `AxFormIntegerControl`, not `AxFormIntControl` (lint XPP007). **Commands:** `New`, `DeleteRecord`, `EditRecord`, `Save`, `CloseForm`, `OK`, `Cancel`, `Refresh`, `DetailsView`; never `SaveAndClose` or `SystemDefinedCloseButton` (XPP008).
- **Never show raw RecIds:** an `AxFormReferenceGroupControl` with `<ReferenceField>` (not `DataField`) and an empty `<Controls />`, on a field typed by a specific RecId EDT whose table has an `AutoLookup` group.
- **Master-detail:** the child data source uses `<JoinSource>` with the parent; a lines action pane sets `<DataSource>` to the child.
- **Card forms opened from a list:** `InsertIfEmpty` `No`, and filter in the data source's `init()`, not the form's.
- **Form extensions:** take the exact `<Parent>` control name from `get_object_info` on the base form (`options.searchControl`); place controls with `ElementPosition`. A wrong parent fails the build ("Parent 'X' not found").
- **Event handlers and CoC for forms** live in separate classes (`xpp-conventions-classes`). `EntAssetObjectTable` is both a form and a table, so name the kind (`formStr` vs `tableStr`).
- **Check it in the browser** after the build (`xpp-ui-test`): a form that compiles can still render blank.
