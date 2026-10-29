# F&O Asset Management Module Reference

Ported from TAG's Cursor rule `fno-asset-management.mdc` (January 2026).

Field lists here are from January 2026. Before using a field, confirm it with `get_object_info` (or `extension_info` mode `table-merge`, which also shows fields other models add, e.g. TAG's six on `EntAssetObjectTable`).

## Key Tables

### EntAssetObjectTable (Fixed Assets/Equipment)
| Field | Type | Description |
|-------|------|-------------|
| `RecId` | Int64 | Primary key |
| `ObjectId` | String | Asset ID (visible identifier) |
| `Name` | String | Asset name |
| `ObjectType` | RefRecId | FK to EntAssetObjectType |
| `ObjectStatus` | Enum | Active, Inactive, etc. |
| `FunctionalLocation` | RefRecId | FK to functional location |

**Common mistake:** There is NO `ObjectGroup` field. Use `ObjectType` instead.

### EntAssetObjectType (Asset Types/Groups)
| Field | Type | Description |
|-------|------|-------------|
| `RecId` | Int64 | Primary key |
| `ObjectTypeID` | String | Type code (NOT ObjectType!) |
| `Name` | String | Type name |

**Common mistake:** The field is `ObjectTypeID`, NOT `ObjectType`.

### EntAssetWorkOrderTable (Work Orders)
| Field | Type | Description |
|-------|------|-------------|
| `RecId` | Int64 | Primary key |
| `WorkOrderId` | String | Work order number |
| `WorkOrderStatus` | Enum | Status |
| `CreatedDateTime` | UtcDateTime | Creation timestamp |

### EntAssetWorkOrderLine (Work Order Lines)
| Field | Type | Description |
|-------|------|-------------|
| `RecId` | Int64 | Primary key |
| `WorkOrder` | RefRecId | FK to EntAssetWorkOrderTable |
| `ObjectTable` | RefRecId | FK to EntAssetObjectTable (the asset) |
| `LineNum` | Int | Line number |

---

## Common Query Patterns

### Find assets by type
```xpp
EntAssetObjectTable asset;
while select asset
    where asset.ObjectType == _assetTypeId
{
    // process asset
}
```

### Count work orders for an asset
```xpp
EntAssetWorkOrderLine line;
select count(RecId) from line
    where line.ObjectTable == _assetId;
int64 woCount = line.RecId;
```

### Get latest work order for asset
```xpp
EntAssetWorkOrderTable wo;
EntAssetWorkOrderLine line;

select firstonly wo
    order by CreatedDateTime desc
    exists join line
        where line.WorkOrder == wo.RecId
           && line.ObjectTable == _assetId;
```

### Find asset with type information
```xpp
EntAssetObjectTable asset;
EntAssetObjectType assetType;

select asset
    join assetType
        where assetType.RecId == asset.ObjectType
           && asset.RecId == _assetId;

info(strFmt("Asset %1 is type %2", asset.ObjectId, assetType.ObjectType));
```

---

## Extending Asset Management

### Adding Fields to Assets
Use table extension:
```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTableExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Name>EntAssetObjectTable.TheAssetGuardian</Name>
    <Fields>
        <AxTableField xmlns="" i:type="AxTableFieldInt64">
            <Name>TAGHealthIndexProfileId</Name>
            <ExtendedDataType>RefRecId</ExtendedDataType>
            <Label>Health Index Profile</Label>
        </AxTableField>
        <AxTableField xmlns="" i:type="AxTableFieldReal">
            <Name>TAGCurrentHealthScore</Name>
            <ExtendedDataType>TAGHealthScore</ExtendedDataType>
        </AxTableField>
    </Fields>
</AxTableExtension>
```

### Linking Custom Tables to Assets
Use `RefRecId` with relation to `EntAssetObjectTable`:
```xml
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>AssetId</Name>
    <ExtendedDataType>RefRecId</ExtendedDataType>
    <Label>Asset</Label>
    <Mandatory>Yes</Mandatory>
</AxTableField>

<Relations>
    <AxTableRelation>
        <Name>EntAssetObjectTable</Name>
        <Cardinality>ZeroMore</Cardinality>
        <RelatedTable>EntAssetObjectTable</RelatedTable>
        <RelatedTableCardinality>ZeroOne</RelatedTableCardinality>
        <RelationshipType>Association</RelationshipType>
        <Constraints>
            <AxTableRelationConstraint xmlns="" i:type="AxTableRelationConstraintField">
                <Name>AssetId</Name>
                <Field>AssetId</Field>
                <RelatedField>RecId</RelatedField>
            </AxTableRelationConstraint>
        </Constraints>
    </AxTableRelation>
</Relations>
```

---

## Common Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Using `asset.ObjectGroup` | Use `asset.ObjectType` (RecId to EntAssetObjectType) |
| Joining WorkOrder directly to Asset | Join through `EntAssetWorkOrderLine.ObjectTable` |
| Assuming WorkOrderId is RecId | `WorkOrderId` is String display ID; use `RecId` for joins |
| Using `asset.Name` for lookups | Use `asset.ObjectId` (the business key) |
