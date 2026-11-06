---
fno-version: [all]
domain: data-modeling
keywords: [recid, edt, foreign-key, lookup, autolookup, verosoft, tag]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# TAG foreign keys use a TAG<Table>RecId EDT and the target has an AutoLookup group

## Description

TAG tables reference other records by RecId. A field typed with the generic `RefRecId` shows a bare number on forms with no lookup. TAG's convention, from its January 2026 rules, is one RecId EDT per referenced table: `TAG<Table>RecId`, extending `RefRecId`, with `ReferenceTable` set to the table and `FormHelp` to its list form. Every referenced TAG table also carries an `AutoLookup` field group with its code and description. For standard tables, use the standard EDTs, such as `EntAssetObjectRecID` and `EntAssetWorkerRecId`.

## Best Practice

When adding a reference, create or reuse the RecId EDT, type the field with it, show it on forms with a reference group control bound through `ReferenceField`, and make sure the target table has `AutoLookup`.

## Anti Pattern

`<ExtendedDataType>RefRecId</ExtendedDataType>` on a field users edit, or an `AxFormInt64Control` showing it. The form shows numbers and users can't pick a record.
