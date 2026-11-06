# F&O Common Errors Reference

Ported from TAG's Cursor rule `fno-errors.mdc` (January 2026).

**Checked 2026-10-29, corrections to the tables below:**
- `'count' is invalid variable name`: the reserved words are the compiler's list (`count`, `index`, `select`, `next`, `order`, `group`, `sum`, …). `table`, `field`, `insert`, `update` and `delete` are allowed.
- `Content cannot be converted to Boolean`: only for properties that take lowercase `true`/`false` (`IsExtensible`, `AllowBlank`, `Nullable`, …). Most properties take `Yes`/`No`; see `xpp-core.md`.
- `Pattern 'DetailsFormBasic' not found`: the detail patterns are `DetailsMaster` and `DetailsTransaction` (1.4); see `xpp-forms.md`.
- For an error that isn't here, ask the MCP: `get_knowledge` (kind `error`, with `errorText` and `errorCode`) returns a root cause and a fix.

Quick lookup table for common F&O build and metadata errors.

---

## Form Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid enum value 'AxFormIntControl'` | Wrong control type | Use `AxFormIntegerControl` |
| `Invalid enum value 'SaveAndClose'` | Invalid command | Use Button with X++ clicked method |
| `Invalid enum value 'SystemDefinedCloseButton'` | Invalid command | Use Button with X++ clicked method |
| `Pattern 'DetailsFormBasic' not found` | Invalid pattern | Remove pattern or use `SimpleList` |
| `Pattern 'SimpleDetails' not found` | Invalid pattern | Remove pattern or use `SimpleListDetails` |
| `WidthMode must be 'SizeToAvailable'` | FillText requirement | Add `<WidthMode>SizeToAvailable</WidthMode>` |
| `HeightMode must be 'SizeToContent'` | FieldsFieldGroups pattern | Remove HeightMode/WidthMode attributes entirely |
| `WidthMode must be 'SizeToContent'` | FieldsFieldGroups pattern | Remove HeightMode/WidthMode attributes entirely |
| `NeedsRecord must be 'Yes'` | FormPartSectionList pattern | Set `<NeedsRecord>Yes</NeedsRecord>` on SeeMoreButton |
| `Control not allowed at current location by pattern` | Pattern restriction | Use VS Designer or different parent |
| `Parent 'X' not found on base form` | Wrong parent name | Verify in VS Designer |
| `Metadata for Form is Corrupted` | Field in SourceCode but not in DataSources | Add `<AxFormDataSourceField>` to DataSources |
| `Menu item display 'X' does not exist` | Wrong menu item name | Verify exact name in AxMenuItemDisplay folder |
| `Field 'X' does not exist on data source` | Wrong field name in form | Check actual table field names |
| `The form 'X' that the extension applies to does not exist` | Wrong base form name | Verify form name exists in base package |
| `Variable 'X' is not found in scope` | Using control name directly | Use `this.design().controlName('X')` |
| `Form control 'X' is not found` | Using `formControlStr()` for XML form | Use string literal: `controlName('X')` |
| Card form opens with new blank record | `InsertIfEmpty` is `Yes` | Set `InsertIfEmpty` to `No` |
| Passed record not displayed | Filter set in form `init()` | Move filter to data source `init()` |
| Form renders blank (only title visible) | Missing pattern requirements | Add Pattern, PatternVersion, proper control structure |

---

## X++ and Class Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Form methods cannot be attributed as event handlers` | Handler in form class | Move handler to separate static class |
| `Invalid extension class name. Must end with '_Extension'` | Missing suffix | Rename class to end with `_Extension` |
| `'count' is invalid variable name` | Reserved keyword | Rename to `recordCount`, `idx`, etc. |
| `The name 'FormName' does not denote a class` | Casting FormRun | Call methods directly on `formRun` |
| `'join' expected.` | `order by` after `where` clause | Put `order by` BEFORE `where` in select |
| `'join' expected.` | Invalid TOP N syntax like `select firstonly N` | Use Query framework with `topRows()` |
| `'join' expected.` | Nested join syntax | Use flat `exists join` structure |
| `Table 'X' does not contain field 'Y'` | Wrong field name assumption | Check actual table structure in AOT |
| `Metadata element is not readable` | Malformed CDATA tags in class XML | Check for `<![CDATA>` (missing `[`) - must be `<![CDATA[` |
| `Operator '==' cannot be applied to operands` | Type mismatch in comparison (RecId vs String) | Add intermediate join to convert types |

---

## Enum Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Content cannot be converted to Boolean` | Using `Yes`/`No` | Use lowercase `true`/`false` |
| `UseEnumValue must be 'No' when IsExtensible is 'True'` | Invalid combination | Set `IsExtensible` to `false` |
| `Qualifier 'EnumName' not valid` | Enum not compiled | Build enums first, then add references |
| `Duplicate value '0' detected` | Enum missing explicit values | Add `<Value>0</Value>`, `<Value>1</Value>` to each AxEnumValue |

---

## Table Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Delete action specified in both DeleteAction node and OnDelete property` | Duplicate delete specification | Remove `<OnDelete>` from child relation |
| `The data method 'X' was not found on the data source` | Display method from extension not bound | Use `ReferenceGroupControl` instead |
| `The underlying type 'HcmSkillRecId' does not exist` | HR module not available | Use `RefRecId` instead |
| `The underlying type 'UnitOfMeasureSymbol' does not exist` | EDT not resolved | Use `String` field with `StringSize` |
| `Table 'InventTable' does not contain field 'Name'` | Wrong field access | Use `InventTable::find().itemName()` |
| `Property cannot be empty` on DeleteActions | Missing `<Table>` tag in DeleteAction | Add `<Table>ChildTableName</Table>` to DeleteAction |
| `Table 'EntAssetObjectTable' does not contain field 'ObjectGroup'` | Wrong field name | Use `ObjectType` (RecId to EntAssetObjectType) |
| `Non-unique index 'X' not allowed` for PrimaryIndex | Index has `AllowDuplicates=Yes` | Remove `<PrimaryIndex>` or make index unique |
| `Extended data type 'X' does not exist` | EDT not found or wrong name | Check EDT name, verify in AxEdt folder |
| `Data type mismatch` on field | Field type doesn't match EDT type | Match `AxTableFieldInt`/`AxTableFieldReal` to EDT base type |

---

## EDT Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot be deserialized as 'AxEdt'` | Wrong namespace in EDT XML | Use `xmlns=""` NOT `xmlns="Microsoft.Dynamics.AX.Metadata.V6"` |
| `Expecting element 'AxEdt' from namespace ''` | V6 namespace in EDT | Change to empty namespace: `xmlns=""` |
| EDT not found in lookup | Missing `i:type` attribute | Add `i:type="AxEdtString"` or appropriate type to `<AxEdt>` element |

---

## General XML Errors

| Error | Cause | Solution |
|-------|-------|----------|
| XML parsing error | Malformed XML | Check for unclosed tags, special characters |
| Boolean property error | Using `Yes`/`No` | Use lowercase `true`/`false` |
| Missing reference | Object not in project | Add to `FNO.rnrproj` |
| `Metadata element is not readable` | Malformed XML structure | Check CDATA tags, namespace, required elements |
| `<![CDATA>` causing XML parse error | Missing opening bracket | Must be `<![CDATA[` (with opening bracket) |

---

## CDATA Block Errors (Critical)

**CRITICAL:** CDATA blocks in X++ source must have correct syntax:
```xml
<!-- WRONG - Missing opening bracket causes "not readable" error -->
<Source><![CDATA>
    public void myMethod() { }
]]></Source>

<!-- CORRECT - Note the opening bracket -->
<Source><![CDATA[
    public void myMethod() { }
]]></Source>
```

**Symptoms:** `Metadata element 'X' is not readable` error on classes.
