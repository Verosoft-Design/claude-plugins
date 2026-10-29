---
fno-version: [all]
domain: extensibility
keywords: [extensionof, tablestr, formstr, target-kind, same-name, coc]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# Name the extension target's kind, because tables and forms can share a name

## Description

Several standard objects exist as both a table and a form with the same name, for example `EntAssetObjectTable` in Asset Management. `[ExtensionOf(tableStr(EntAssetObjectTable))]` and `[ExtensionOf(formStr(EntAssetObjectTable))]` extend different things: in the first, `this` is the table buffer; in the second, it is the form's `FormRun`. On 10.0.46 the d365fo MCP's `extension_info` (mode `coc`) listed a model's form-button handler class among the table's CoC extensions, because it matched the name only.

## Best Practice

When an object name could be a table, a form or a class, confirm the kind before writing the extension (`search` with a `type` filter), use the matching `tableStr`, `formStr` or `classStr`, and when reviewing a list of existing extensions read each hit's `[ExtensionOf(...)]` line rather than trusting the list.

## Anti Pattern

Writing a form event handler against a table method, or concluding that a table already has a CoC wrapper because a tool listed a same-named form's extension class.
