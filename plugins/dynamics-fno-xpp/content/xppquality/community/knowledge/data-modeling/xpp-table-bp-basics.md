---
fno-version: [all]
domain: data-modeling
keywords: [table, edt, title-field, replacement-key, developer-documentation, labels]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# New tables: EDT-typed fields, title fields, a replacement key and label IDs

## Description

xppbp checks a table's design. On a custom table on 10.0.46 it reported eleven warnings that a new table should avoid from the start. Fields declared with a bare type instead of an EDT (`BPErrorTableFieldNotDefinedUsingType`). No `TitleField1` (`BPErrorTableTitleField1NotDeclared`). No `DeveloperDocumentation` (`BPErrorDeveloperDocumentationNotDefined`). An alternate key without a `ReplacementKey` (`BPTableWithRecIdIndexMissingReplacementKey`). Literal text in `Label` and `HelpText` (`BPErrorLabelIsText`, `BPErrorHelpIsText`).

## Best Practice

Give every field an EDT, either a standard one or one of the model's own. Set `TitleField1` and `TitleField2` to the business key and description, and `ReplacementKey` to the unique alternate-key index, so lookups and references show codes instead of RecIds. Write `DeveloperDocumentation`. Use label IDs for every user-visible text. Run a BP check on the new table before the first commit.

## Anti Pattern

A table whose fields are plain strings and integers with literal labels and no title fields. It compiles, but every form that shows it displays numbers instead of codes, and translation is impossible.
