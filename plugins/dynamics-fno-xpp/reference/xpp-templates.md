# F&O XML Templates

Ported from TAG's Cursor rule `fno-templates.mdc` (January 2026). Before hand-writing an object, prefer the MCP: `generate_object` (mode `scaffold`, `scaffold:table`, `scaffold:form`, `pattern`) and `d365fo_file` create, whose contract `get_knowledge` (kind `op-spec`) describes. Templates here are the fallback.

Reference templates for creating new F&O artifacts. Copy and modify as needed.

---

## EDT Template

**CRITICAL:** EDTs must NOT use V6 namespace - use empty `xmlns=""`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns=""
    i:type="AxEdtString">
    <Name>TAGEdtMyString</Name>
    <Label>My String Field</Label>
    <HelpText>Description of the field</HelpText>
    <StringSize>30</StringSize>
</AxEdt>
```

### EDT Type Attribute Values
| EDT Base Type | `i:type` Value |
|---------------|----------------|
| String | `AxEdtString` |
| Integer | `AxEdtInt` |
| Int64 | `AxEdtInt64` |
| Real | `AxEdtReal` |
| Date | `AxEdtDate` |
| DateTime | `AxEdtDateTime` |
| Enum | `AxEdtEnum` |

---

## RecId EDT Template (For Foreign Key Lookups)

**Use this for every TAG table that will be referenced by other tables:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtInt64">
    <Name>TAGMyTableRecId</Name>
    <Extends>RefRecId</Extends>
    <FormHelp>TAGMyTables</FormHelp>
    <HelpText>Reference to my table record</HelpText>
    <Label>My Table</Label>
    <ReferenceTable>TAGMyTable</ReferenceTable>
    <ArrayElements />
    <Relations />
    <TableReferences />
</AxEdt>
```

### Required Properties for Lookup to Work
| Property | Purpose | Notes |
|----------|---------|-------|
| `Extends` | Must be `RefRecId` | Base type for record IDs |
| `ReferenceTable` | Target table name | **CRITICAL** - enables lookup |
| `FormHelp` | Form for F4 lookup | Usually table name + "s" |
| `Label` | Display label | User-friendly name |

### Naming Convention
- EDT Name: `TAG<TableName>RecId` (e.g., `TAGKeySafeRecId`)
- FormHelp: Usually the form name for that table (e.g., `TAGKeySafes`)

---

### Common EDT Errors
```xml
<!-- WRONG - V6 namespace causes deserialization error -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" 
       xmlns="Microsoft.Dynamics.AX.Metadata.V6">

<!-- WRONG - Missing i:type causes lookup failures -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="">

<!-- CORRECT - Empty namespace AND i:type specified -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns=""
    i:type="AxEdtString">
```

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

## Class with Methods Template

**CRITICAL:** CDATA blocks must use `<![CDATA[` (with opening bracket):

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Name>TAGMyService</Name>
    <SourceCode>
        <Declaration><![CDATA[
public class TAGMyService
{
}
]]></Declaration>
        <Methods>
            <Method>
                <Name>myMethod</Name>
                <Source><![CDATA[
    public void myMethod()
    {
        // Method code here
    }

]]></Source>
            </Method>
        </Methods>
    </SourceCode>
</AxClass>
```

### CDATA Syntax (CRITICAL)
```xml
<!-- WRONG - Missing opening bracket causes "not readable" error -->
<Source><![CDATA>
    public void myMethod() { }
]]></Source>

<!-- CORRECT - Note the [ after CDATA -->
<Source><![CDATA[
    public void myMethod() { }
]]></Source>
```

**Symptom:** `Metadata element 'ClassName' is not readable` error = check CDATA blocks for missing `[`

---

## Enum Template

**CRITICAL:** Enums require `UseEnumValue` and `IsExtensible` for dropdowns to work:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEnum xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Name>TAGMyEnum</Name>
    <Label>My Enum Label</Label>
    <UseEnumValue>No</UseEnumValue>
    <EnumValues>
        <AxEnumValue>
            <Name>Value1</Name>
            <Label>First Value</Label>
            <!-- First value: omit <Value> tag, defaults to 0 -->
        </AxEnumValue>
        <AxEnumValue>
            <Name>Value2</Name>
            <Label>Second Value</Label>
            <Value>1</Value>
        </AxEnumValue>
        <AxEnumValue>
            <Name>Value3</Name>
            <Label>Third Value</Label>
            <Value>2</Value>
        </AxEnumValue>
    </EnumValues>
    <IsExtensible>true</IsExtensible>
</AxEnum>
```

**Common mistakes that cause "Qualifier not valid" errors:**
- Missing `<UseEnumValue>No</UseEnumValue>`
- Using `<IsExtensible>false</IsExtensible>` instead of `true`
- Explicit `<Value>0</Value>` on first enum value

---

## SimpleList Form Template

**CRITICAL:** Forms require `xmlns="Microsoft.Dynamics.AX.Metadata.V6"` on root element:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V6">
    <Name>TAGMyForm</Name>
    <SourceCode>
        <Methods xmlns="">
            <Method>
                <Name>classDeclaration</Name>
                <Source><![CDATA[
[Form]
public class TAGMyForm extends FormRun
{
}
]]></Source>
            </Method>
        </Methods>
        <DataSources xmlns="" />
        <DataControls xmlns="" />
        <Members xmlns="" />
    </SourceCode>
    <DataSources>
        <AxFormDataSource xmlns="">
            <Name>TAGMyTable</Name>
            <Table>TAGMyTable</Table>
            <Fields />
            <ReferencedDataSources />
            <AllowCreate>Yes</AllowCreate>
            <AllowDelete>Yes</AllowDelete>
            <InsertAtEnd>Yes</InsertAtEnd>
            <InsertIfEmpty>No</InsertIfEmpty>
        </AxFormDataSource>
    </DataSources>
    <Design>
        <Caption xmlns="">My Form</Caption>
        <Pattern xmlns="">SimpleList</Pattern>
        <PatternVersion xmlns="">1.1</PatternVersion>
        <Style xmlns="">SimpleList</Style>
        <TitleDataSource xmlns="">TAGMyTable</TitleDataSource>
        <Controls xmlns="">
            <AxFormControl i:type="AxFormActionPaneControl">
                <Name>MainActionPane</Name>
                <Type>ActionPane</Type>
                <FormControlExtension i:nil="true" />
                <Controls>
                    <AxFormControl i:type="AxFormActionPaneTabControl">
                        <Name>MainActionPaneTab</Name>
                        <Type>ActionPaneTab</Type>
                        <FormControlExtension i:nil="true" />
                        <Controls>
                            <AxFormControl i:type="AxFormButtonGroupControl">
                                <Name>MainButtonGroup</Name>
                                <Type>ButtonGroup</Type>
                                <FormControlExtension i:nil="true" />
                                <Controls>
                                    <AxFormControl i:type="AxFormCommandButtonControl">
                                        <Name>NewButton</Name>
                                        <Type>CommandButton</Type>
                                        <FormControlExtension i:nil="true" />
                                        <Command>New</Command>
                                    </AxFormControl>
                                    <AxFormControl i:type="AxFormCommandButtonControl">
                                        <Name>DeleteButton</Name>
                                        <Type>CommandButton</Type>
                                        <FormControlExtension i:nil="true" />
                                        <Command>DeleteRecord</Command>
                                    </AxFormControl>
                                </Controls>
                            </AxFormControl>
                        </Controls>
                    </AxFormControl>
                </Controls>
            </AxFormControl>
            <AxFormControl i:type="AxFormGroupControl">
                <Name>FilterGroup</Name>
                <Type>Group</Type>
                <FormControlExtension i:nil="true" />
                <Controls />
            </AxFormControl>
            <AxFormControl i:type="AxFormGridControl">
                <Name>MainGrid</Name>
                <Type>Grid</Type>
                <FormControlExtension i:nil="true" />
                <DataSource>TAGMyTable</DataSource>
                <Controls>
                    <!-- Add field controls here -->
                </Controls>
            </AxFormControl>
        </Controls>
    </Design>
    <Parts />
</AxForm>
```

---

## ReferenceGroupControl Template (For RecId Lookups)

**Use this instead of Int64Control for RecId fields to show user-friendly dropdowns:**

```xml
<AxFormControl xmlns="" i:type="AxFormReferenceGroupControl">
    <Name>MyTableRecId</Name>
    <Type>ReferenceGroup</Type>
    <FormControlExtension i:nil="true" />
    <Controls />
    <DataSource>TAGChildTable</DataSource>
    <ReferenceField>MyTableRecId</ReferenceField>
</AxFormControl>
```

### Critical Properties
| Property | Value | Notes |
|----------|-------|-------|
| `i:type` | `AxFormReferenceGroupControl` | NOT Int64Control |
| `Type` | `ReferenceGroup` | Required |
| `Controls` | Empty `<Controls />` | **REQUIRED** even if empty |
| `ReferenceField` | Field name | **NOT** `DataField` |

### Prerequisites for Lookup to Work
1. Table field uses specific RecId EDT (not generic `RefRecId`)
2. EDT has `<ReferenceTable>` property set
3. Target table has `AutoLookup` field group

---

## Basic Grid Form Template (No Pattern - Most Reliable)

**Use this when patterns cause issues:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V6">
    <Name>TAGMyBasicForm</Name>
    <SourceCode>
        <Methods xmlns="">
            <Method>
                <Name>classDeclaration</Name>
                <Source><![CDATA[
[Form]
public class TAGMyBasicForm extends FormRun
{
}
]]></Source>
            </Method>
        </Methods>
        <DataSources xmlns="" />
        <DataControls xmlns="" />
        <Members xmlns="" />
    </SourceCode>
    <DataSources>
        <AxFormDataSource xmlns="">
            <Name>TAGMyTable</Name>
            <Table>TAGMyTable</Table>
            <Fields />
            <ReferencedDataSources />
            <AllowCreate>Yes</AllowCreate>
            <AllowDelete>Yes</AllowDelete>
            <InsertAtEnd>Yes</InsertAtEnd>
            <InsertIfEmpty>No</InsertIfEmpty>
        </AxFormDataSource>
    </DataSources>
    <Design>
        <Caption xmlns="">My Basic Form</Caption>
        <Controls xmlns="">
            <AxFormControl xmlns=""
                i:type="AxFormGridControl">
                <Name>MainGrid</Name>
                <Type>Grid</Type>
                <FormControlExtension
                    i:nil="true" />
                <Controls>
                    <AxFormControl xmlns=""
                        i:type="AxFormStringControl">
                        <Name>Field1</Name>
                        <Type>String</Type>
                        <FormControlExtension
                            i:nil="true" />
                        <DataField>Field1</DataField>
                        <DataSource>TAGMyTable</DataSource>
                    </AxFormControl>
                </Controls>
                <DataSource>TAGMyTable</DataSource>
            </AxFormControl>
        </Controls>
    </Design>
    <Parts />
</AxForm>
```

**Why use this:** When forms have "Metadata element is not readable" errors, start with this minimal structure and add complexity incrementally.

---

## Data Source with Query Range Template

**Checked 2026-10-29, inconsistent with `xpp-forms.md`:** this template puts `<Methods>` inside `<AxFormDataSource>`, but the forms rule (dual structure) and standard forms put data source method overrides under `<SourceCode><DataSources xmlns=""><DataSource><Name>…</Name><Methods>`. Use that structure; this one is kept only as it was written.

```xml
<AxFormDataSource xmlns="">
    <Name>TAGMyTable</Name>
    <Table>TAGMyTable</Table>
    <InsertAtEnd>No</InsertAtEnd>
    <InsertIfEmpty>No</InsertIfEmpty>
    <Methods>
        <Method>
            <Name>init</Name>
            <Source><![CDATA[
    public void init()
    {
        super();
        QueryBuildDataSource qbds = this.queryBuildDataSource();
        qbds.addRange(fieldNum(TAGMyTable, SomeField)).value(queryValue(0));
    }
]]></Source>
        </Method>
    </Methods>
    <Fields />
</AxFormDataSource>
```
