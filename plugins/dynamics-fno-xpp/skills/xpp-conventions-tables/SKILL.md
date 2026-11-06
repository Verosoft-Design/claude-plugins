---
name: xpp-conventions-tables
description: X++ rules for tables, table extensions and EDTs in F&O metadata XML (relations, delete actions, RecId EDTs for lookups, AutoLookup, indexes, best-practice findings). Loads automatically when working on AxTable, AxTableExtension, AxEdt or AxEdtExtension files.
user-invocable: false
paths:
  - "**/AxTable/*.xml"
  - "**/AxTableExtension/*.xml"
  - "**/AxEdt/*.xml"
  - "**/AxEdtExtension/*.xml"
---

# Tables, table extensions and EDTs

Full rules and XML: `${CLAUDE_PLUGIN_ROOT}/reference/xpp-tables.md`; templates in `${CLAUDE_PLUGIN_ROOT}/reference/xpp-templates.md`. Core rules: the `xpp-conventions` skill.

- **Look up the standard table first:** `get_object_info` (`objectType: "table"`) for fields, indexes and relations. `extension_info` (mode `table-merge`) shows what other models already add to it, e.g. TAG's six fields on `EntAssetObjectTable`.
- **Delete actions, once:** a `DeleteAction` on the parent with both `<Name>` and `<Table>` (lint XPP011), and no `OnDelete` on the child's relation. Never both.
- **Foreign keys use a specific RecId EDT** (`TAG<Table>RecId`, `Extends` `RefRecId`, `ReferenceTable`, `FormHelp`), not bare `RefRecId`; otherwise the form shows a number with no lookup. The referenced table needs an `AutoLookup` field group (code plus description). Standard ones exist: `EntAssetObjectRecID`, `EntAssetWorkerRecId`, `EntAssetFunctionalLocationRecID`, `EntAssetWorkOrderLineRecID` (confirm with `search`).
- **Optional modules:** an EDT or table is usable only when its package is in the Descriptor's `ModuleReferences`. Fall back to `RefRecId` only for modules that aren't referenced.
- **Indexes:** `PrimaryIndex` must be unique (lint XPP011); an alternate key makes an index unique, and `ReplacementKey` should point at it.
- **EDTs:** root `<AxEdt xmlns="" i:type="AxEdtString|AxEdtInt64|AxEdtEnum|...">` (lint XPP005).
- **Table extensions:** named `<BaseTable>.<Model>`; every added field starts with the prefix (XPP013); add to `FieldGroups` rather than reordering the base.
- **Best practice** (xppbp on a TAG table, 2026-10-29): every field typed by an EDT (`BPErrorTableFieldNotDefinedUsingType`), label IDs for `Label`/`HelpText` (`BPErrorLabelIsText`), `TitleField1`, `DeveloperDocumentation`, and `ReplacementKey` when an alternate key exists.
- **Schema changes need a database sync** (`xpp-db-sync`). Sync only adds: dropping, renaming or retyping a field with data needs the user to name it.
