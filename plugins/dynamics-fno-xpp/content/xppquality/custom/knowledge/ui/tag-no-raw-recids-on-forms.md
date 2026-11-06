---
fno-version: [all]
domain: ui
keywords: [reference-group, recid, lookup, form-control, verosoft, tag]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# TAG forms never show raw RecIds

## Description

TAG's January 2026 rules make it a golden rule that users never see a numeric RecId. A RecId field is shown with an `AxFormReferenceGroupControl` whose `ReferenceField` names the field, with an empty `Controls` element. It never uses `DataField` or an `AxFormInt64Control`. This works only when the field is typed with a RecId EDT that sets `ReferenceTable`, and the target table has an `AutoLookup` field group.

## Best Practice

Convert any Int64 control bound to a RecId into a reference group control, and check the three prerequisites: the EDT, `ReferenceTable` and `AutoLookup`. Then open the form in the web client and confirm the field shows a code with a working lookup.

## Anti Pattern

A grid column that shows `5637144576` where users expect an asset ID, or a reference group control bound with `DataField`, which makes it invisible.
