# F&O Table XML Rules

Ported from TAG's Cursor rule `fno-tables.mdc` (January 2026). Notes marked **Checked 2026-10-29** were verified on F&O 10.0.46 (see `xpp-core.md`).

## Parent-Child Table Relationships

### Delete Actions - ONLY Define Once

The lint checks part of this: a DeleteAction without `<Table>` (XPP011).
**CRITICAL:** You cannot have both a `DeleteAction` on the parent table AND an `OnDelete` on the child's relation. Choose ONE approach.

```xml
<!-- WRONG - Causes error: "The delete action is specified in both the DeleteAction node, and the OnDelete property of the relation" -->

<!-- Parent table has DeleteAction -->
<DeleteActions>
    <AxTableDeleteAction>
        <Name>TAGChildTable</Name>
        <DeleteAction>Cascade</DeleteAction>
        <Relation>TAGChildTable</Relation>
    </AxTableDeleteAction>
</DeleteActions>

<!-- Child table relation also has OnDelete -->
<Relations>
    <AxTableRelation>
        <Name>TAGParentTable</Name>
        <OnDelete>Cascade</OnDelete>  <!-- ERROR! Remove this -->
        ...
    </AxTableRelation>
</Relations>
```

**CORRECT:** Use DeleteActions on the parent table ONLY:
```xml
<!-- Parent table (TAGWorkProcedure) -->
<DeleteActions>
    <AxTableDeleteAction>
        <Name>TAGWorkProcedureRequirement</Name>
        <DeleteAction>Cascade</DeleteAction>
        <Relation>TAGWorkProcedureRequirement</Relation>
    </AxTableDeleteAction>
</DeleteActions>

<!-- Child table relation - NO OnDelete -->
<Relations>
    <AxTableRelation>
        <Name>TAGWorkProcedure</Name>
        <Cardinality>ZeroMore</Cardinality>
        <RelatedTable>TAGWorkProcedure</RelatedTable>
        <RelatedTableCardinality>ZeroOne</RelatedTableCardinality>
        <RelationshipType>Association</RelationshipType>
        <Constraints>
            <AxTableRelationConstraint i:type="AxTableRelationConstraintField">
                <Name>WorkProcedureRecId</Name>
                <Field>WorkProcedureRecId</Field>
                <RelatedField>RecId</RelatedField>
            </AxTableRelationConstraint>
        </Constraints>
    </AxTableRelation>
</Relations>
```

### DeleteAction XML Structure
**CRITICAL:** DeleteActions require BOTH `<Name>` AND `<Table>` tags:

```xml
<!-- WRONG - Missing <Table> tag causes "Property cannot be empty" error -->
<DeleteActions>
    <AxTableDeleteAction>
        <Name>TAGChildTable</Name>
        <DeleteAction>Cascade</DeleteAction>
        <Relation>TAGChildTable</Relation>
    </AxTableDeleteAction>
</DeleteActions>

<!-- CORRECT - Include <Table> tag -->
<DeleteActions>
    <AxTableDeleteAction>
        <Name>TAGHealthDataSource</Name>
        <Table>TAGHealthDataSource</Table>
        <DeleteAction>Cascade</DeleteAction>
    </AxTableDeleteAction>
</DeleteActions>
```

**Note:** The `<Name>` and `<Table>` values are typically the same (the child table name). The `<Relation>` tag is optional if the relationship name matches the table name.

### Child Table Standard Fields
When creating child tables, include:
- `ParentRecId` (Int64) - FK to parent with **specific RecId EDT**
- `LineNum` (Int) - for ordering (optional)

**CRITICAL:** Always use specific RecId EDTs (not generic `RefRecId`) for foreign key fields that users will interact with on forms. This enables automatic lookup functionality.

```xml
<!-- WRONG - Generic RefRecId prevents lookups from working -->
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>WorkProcedureRecId</Name>
    <ExtendedDataType>RefRecId</ExtendedDataType>
    <Mandatory>Yes</Mandatory>
</AxTableField>

<!-- CORRECT - Specific EDT enables automatic lookup -->
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>WorkProcedureRecId</Name>
    <ExtendedDataType>TAGWorkProcedureRecId</ExtendedDataType>
    <Mandatory>Yes</Mandatory>
</AxTableField>

<AxTableField xmlns="" i:type="AxTableFieldInt">
    <Name>LineNum</Name>
    <ExtendedDataType>LineNum</ExtendedDataType>
</AxTableField>
```

---

## External Module Dependencies

### Avoid Direct Dependencies on Optional Modules

Check the model's `ModuleReferences` (Descriptor) first: an EDT or table is only usable when its package is referenced. TAG references ApplicationFoundation, ApplicationPlatform, ApplicationSuite, CaseManagement, Directory, EnterpriseAssetManagementAppSuite, HRPlatform, Ledger, PersonnelCore and PersonnelManagement. A generic `RefRecId` loses the automatic lookup (see the RecId EDT pattern below), so use it only for modules that aren't referenced.
When referencing EDTs/tables from modules that may not be installed (HR, Retail, etc.), use generic types:

```xml
<!-- WRONG - Direct dependency on HR module -->
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>HcmSkillRecId</Name>
    <ExtendedDataType>HcmSkillRecId</ExtendedDataType>  <!-- May not exist! -->
</AxTableField>

<!-- CORRECT - Generic field, link via code if HR exists -->
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>SkillRecId</Name>
    <ExtendedDataType>RefRecId</ExtendedDataType>
    <HelpText>@TAGLabels:ReferenceToHcmSkillRecordHelp</HelpText>
</AxTableField>
```

### Safe EDT References
These EDTs are always available:
- `RefRecId` - for any RecId reference
- `Description`, `Name` - for text fields
- `LineNum` - for sequence numbers
- `NoYesId` - for boolean fields

### Unit of Measure Workaround
If `UnitOfMeasureSymbol` EDT is not available:
```xml
<!-- Use String with appropriate size -->
<AxTableField xmlns="" i:type="AxTableFieldString">
    <Name>UnitId</Name>
    <Label>@TAGLabels:Unit</Label>
    <StringSize>10</StringSize>
</AxTableField>
```

---

## Index Constraints

### PrimaryIndex Must Be Unique
**A non-unique index CANNOT be used as PrimaryIndex:**

```xml
<!-- WRONG - Non-unique index as PrimaryIndex -->
<Indexes>
    <AxTableIndex>
        <Name>MyIdx</Name>
        <AllowDuplicates>Yes</AllowDuplicates>  <!-- Non-unique -->
        <Fields>
            <AxTableIndexField>
                <DataField>SomeField</DataField>
            </AxTableIndexField>
        </Fields>
    </AxTableIndex>
</Indexes>
<PrimaryIndex>MyIdx</PrimaryIndex>  <!-- ERROR! -->

<!-- CORRECT - Either make index unique or remove PrimaryIndex -->
<Indexes>
    <AxTableIndex>
        <Name>MyIdx</Name>
        <AllowDuplicates>Yes</AllowDuplicates>
        <Fields>...</Fields>
    </AxTableIndex>
</Indexes>
<ClusteredIndex>MyIdx</ClusteredIndex>  <!-- ClusteredIndex CAN be non-unique -->
<!-- No PrimaryIndex specified -->
```

### AlternateKey Index Pattern
```xml
<AxTableIndex>
    <Name>CodeIdx</Name>
    <AlternateKey>Yes</AlternateKey>  <!-- Makes it unique -->
    <Fields>
        <AxTableIndexField>
            <DataField>Code</DataField>
        </AxTableIndexField>
    </Fields>
</AxTableIndex>
```

---

## RecId EDT Pattern for Lookups (CRITICAL)

### Why Specific RecId EDTs Are Required
When a form field references another table via RecId, the user should see meaningful codes/names instead of numbers. This requires a specific EDT that tells the system which table to look up.

### Creating a RecId EDT
For every TAG table that will be referenced by other tables, create a matching RecId EDT:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtInt64">
    <Name>TAGMyTableRecId</Name>
    <Extends>RefRecId</Extends>
    <FormHelp>TAGMyTables</FormHelp>        <!-- Lookup form name -->
    <HelpText>@TAGLabels:ReferenceToMyTableHelp</HelpText>
    <Label>@TAGLabels:MyTable</Label>
    <ReferenceTable>TAGMyTable</ReferenceTable>  <!-- Target table -->
    <ArrayElements />
    <Relations />
    <TableReferences />
</AxEdt>
```

### Key Properties
| Property | Purpose | Example |
|----------|---------|---------|
| `Extends` | Must extend `RefRecId` | `RefRecId` |
| `ReferenceTable` | Table this RecId points to | `TAGKeySafe` |
| `FormHelp` | Form to open for F4 lookup | `TAGKeySafes` |
| `Label` | User-friendly field label | `Key Safe` |

### Using the EDT on Foreign Key Fields
```xml
<!-- In the child/referencing table -->
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>KeySafeRecId</Name>
    <ExtendedDataType>TAGKeySafeRecId</ExtendedDataType>  <!-- Specific EDT -->
    <Mandatory>Yes</Mandatory>
</AxTableField>
```

### Standard Asset Management RecId EDTs
Use these existing EDTs when referencing standard tables:
| EDT Name | Target Table | Use For |
|----------|--------------|---------|
| `EntAssetWorkerRecId` | EntAssetWorker | Maintenance workers |
| `EntAssetObjectRecID` | EntAssetObjectTable | Assets |
| `EntAssetFunctionalLocationRecID` | EntAssetFunctionalLocation | Functional locations |
| `EntAssetWorkOrderLineRecID` | EntAssetWorkOrderLine | Work order lines/jobs |

---

## AutoLookup Field Group
The referenced table MUST have an `AutoLookup` field group for ReferenceGroupControl to work:
```xml
<AxTableFieldGroup>
    <Name>AutoLookup</Name>
    <Fields>
        <AxTableFieldGroupField>
            <DataField>ProcedureCode</DataField>
        </AxTableFieldGroupField>
        <AxTableFieldGroupField>
            <DataField>Description</DataField>
        </AxTableFieldGroupField>
    </Fields>
</AxTableFieldGroup>
```

**Ensure every TAG table has an AutoLookup group** containing the code/ID and description fields.

---

## Table Extension Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTableExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Name>EntAssetWorkOrderTable.TheAssetGuardian</Name>
    <FieldGroups />
    <Fields>
        <AxTableField xmlns="" i:type="AxTableFieldString">
            <Name>TAGAssignedWorkers</Name>
            <ExtendedDataType>TAGEdtAssignedWorkers</ExtendedDataType>
        </AxTableField>
    </Fields>
    <Indexes />
    <Mappings />
    <PropertyModifications />
    <Relations />
</AxTableExtension>
```

---

## Best-practice findings on TAG tables (Checked 2026-10-29)

xppbp on `TAGAssetCriticalityClass` reported 11 warnings. Avoid them in new tables:

| Moniker | Fix |
| --- | --- |
| `BPErrorTableFieldNotDefinedUsingType` | Give every field an EDT (`<ExtendedDataType>`), not a bare type. |
| `BPErrorLabelIsText`, `BPErrorHelpIsText` | Use label IDs for `Label` and `HelpText` (`labels` tool, action `create`). |
| `BPErrorTableTitleField1NotDeclared` | Set `TitleField1` (and usually `TitleField2`). |
| `BPErrorDeveloperDocumentationNotDefined` | Set `DeveloperDocumentation` on the table. |
| `BPTableWithRecIdIndexMissingReplacementKey` | With an alternate key, set `ReplacementKey` to it. |

## Common Table Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Delete action specified in both DeleteAction node and OnDelete property` | Duplicate delete specification | Remove `<OnDelete>` from child relation |
| `The underlying type 'HcmSkillRecId' does not exist` | HR module not available | Use `RefRecId` instead |
| `The underlying type 'UnitOfMeasureSymbol' does not exist` | EDT not resolved | Use `String` field with `StringSize` |
| `Table 'InventTable' does not contain field 'Name'` | Wrong field access | Use `InventTable::find().itemName()` |
