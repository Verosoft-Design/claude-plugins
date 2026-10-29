---
name: xpp-conventions-classes
description: X++ code rules for classes in F&O metadata XML (Chain of Command wrappers, extension target kinds, event handler classes, prepopulation through table init methods, select statement syntax, reserved words, form control access, verifying field names). Loads automatically when working on AxClass files.
user-invocable: false
paths:
  - "**/AxClass/*.xml"
---

# Classes and X++ code

Full rules and examples: `${CLAUDE_PLUGIN_ROOT}/reference/xpp-classes.md`. Core rules: the `xpp-conventions` skill. `get_knowledge` (kind `knowledge`) has the deeper rulebook: topics `coc-authoring`, `event-handlers`, `select-statement`, `sysoperation`, `number-sequences`, `security`.

- **Source lives in CDATA:** `<Declaration><![CDATA[ … ]]></Declaration>` and one `<Method><Name>…</Name><Source><![CDATA[ … ]]></Source></Method>` per method.
- **Chain of Command:**
  - get the signature first: `get_object_info` with `options: {"method": "<name>", "include": "signature"}`;
  - check existing wrappers with `extension_info` (mode `coc`, `method`);
  - `[ExtensionOf(tableStr|formStr|classStr|formDataSourceStr|formControlStr(...))]`, a `final` class named `…_Extension` (lint XPP014);
  - repeat the parameters **without default values** (XPP016);
  - call `next` once, unconditionally, at the top level.
- **Name the target kind:** `EntAssetObjectTable` is a table and a form. `this` is the buffer in a `tableStr` extension and the FormRun in a `formStr` one.
- **Event handlers** go in their own static class (`[FormDataSourceEventHandler(...)]`, `[FormControlEventHandler(...)]`, `[DataEventHandler(...)]`), never on form methods. A FormRun can't be cast to the form's class; call its methods on the FormRun.
- **Defaulting fields on create dialogs:** extend the table method the form's data source `initValue()` calls (e.g. `EntAssetWorkOrderTable.initFromServiceLevel`), not the form event. Read that `initValue()` with `get_object_info … include: "source"`.
- **Selects:** `order by`/`group by` before `where`, per join segment (lint XPP018). Flat `exists join` chains, not nested joins. `firstOnly`, `firstOnly10`, `firstOnly100`, `firstOnly1000`, but no arbitrary TOP N (use a Query). Compare RecId with RecId, and string ID with string ID: join through the master table when needed. No function calls in `where`; assign them to a variable first.
- **Reserved words** can't be names: `count`, `index`, `select`, `next`, `order`, `group`, `sum`, `str`, `date`… (XPP017); `field`, `table`, `insert`, `update` and `delete` are fine.
- **Verify every field and method name** before writing code: `get_object_info`, or the `fno-explorer` agent. Wrong field names (`ObjectGroup` instead of `ObjectType` on `EntAssetObjectTable`) were the most common TAG build error.
- **Form controls from code:** `formControlStr(Form, Control)` is checked at compile time. Use it for controls defined in the form's XML; for runtime-only controls, use `element.design().controlName('X')` with a null check.
- **Tests:** SysTest classes extend `SysTestCase`; see `xpp-write-test`.
