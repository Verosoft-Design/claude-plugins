# F&O Form XML Rules

Ported from TAG's Cursor rule `fno-forms.mdc` (January 2026). Notes marked **Checked 2026-10-29** were verified on F&O 10.0.46 (see `xpp-core.md`).

## Form XML Structure (Critical)

### Control Type Names
Use **exact** control type names:
```xml
<!-- WRONG -->
<AxFormControl i:type="AxFormIntControl">

<!-- CORRECT -->
<AxFormControl i:type="AxFormIntegerControl">
```

**Valid control types** (the most used; the lint knows all 37 that standard forms use and flags others, XPP007):
- `AxFormStringControl`, `AxFormIntegerControl`, `AxFormRealControl`, `AxFormCheckBoxControl`
- `AxFormButtonControl`, `AxFormCommandButtonControl`, `AxFormMenuFunctionButtonControl`
- `AxFormGridControl`, `AxFormGroupControl`, `AxFormTabControl`, `AxFormTabPageControl`
- `AxFormActionPaneControl`, `AxFormActionPaneTabControl`, `AxFormButtonGroupControl`

### Valid Form Patterns
**Checked 2026-10-29:** the January list named `DetailsFormMaster` and `DetailsFormTransaction` (version 1.1). No standard form uses those names. The real top-level patterns are `DetailsMaster` and `DetailsTransaction`, version 1.4. These are the pattern/version pairs that standard 10.0.46 forms use (62 patterns in all, in `scripts/xpp_xml_facts.json`; the lint flags others, XPP009):

| Pattern | Versions in standard forms |
| --- | --- |
| `SimpleList` | 1.1 |
| `SimpleListDetails` | 1.3 |
| `DetailsMaster` | 1.3, 1.4 |
| `DetailsTransaction` | 1.4 |
| `ListPage` | UX7 1.0 |
| `Dialog` | 1.2 |
| `DropDialog` | 1.2 |
| `TableOfContents` | 1.1 |
| `Task` | 1.2 |
| `TaskParentChild` | 1.2 |
| `Wizard` | 1.2 |
| `FormPartFactboxCard` | UX7 1.0 |
| `FormPartFactboxGrid` | 1.1 |
| `FormPartSectionList` | 1.2 |
| `TabbedWorkspace` | 1.0 |
| `WorkspaceOperational` | 1.1 |

Sub-patterns used inside forms include `FieldsFieldGroups` 1.1, `ToolbarList` 1.2, `CustomAndQuickFilters` 1.1, `FillText` UX7 1.0, `SectionTiles` 1.1, `SectionTabbedList` 1.1, `SectionRelatedLinks` 1.1 and `FiltersAndToolbarInline` 1.0.

**Invalid patterns (do NOT use):**
- `DetailsFormBasic`, `SimpleDetails` (on its own; `SimpleDetails-FastTabsContainer` 1.4 and other `SimpleDetails-*` variants exist), `DetailsFormMaster`, `DetailsFormTransaction`

**Ask the MCP before choosing one:** `object_patterns`, or `get_knowledge` (kind `knowledge`, topic "form patterns"), lists each pattern's required controls. `generate_object` (mode `scaffold:form`) builds a form that satisfies the pattern.

**If unsure:** Remove `<Pattern>` and `<PatternVersion>` elements entirely.

### Valid CommandButton Commands
```xml
<Command>New</Command>           <!-- Create new record -->
<Command>DeleteRecord</Command>  <!-- Delete current record -->
<Command>Edit</Command>          <!-- Edit mode -->
<Command>View</Command>          <!-- View mode -->
<Command>Find</Command>          <!-- Open find dialog -->
<Command>Filter</Command>        <!-- Open filter dialog -->
<Command>Refresh</Command>       <!-- Refresh data -->
```

**Invalid commands (do NOT use):**
- `SaveAndClose`, `SystemDefinedCloseButton`

**For Save/Close:** Use regular Button with X++ clicked method.

**Checked 2026-10-29:** the commands standard forms actually use, most frequent first: `OK`, `DeleteRecord`, `Cancel`, `New`, `DetailsView`, `DocumentHandling`, `Save`, `EditRecord`, `Refresh`, `CloseForm`. So a Save or Close button can be a CommandButton with `Save` or `CloseForm`, as standard forms do (23 and 13 uses). `Edit`, `View`, `Find` and `Filter` from the list above never appear in standard forms; prefer `EditRecord`.

### FillText Pattern Requirement
When using `FillText` pattern, **MUST** set `WidthMode`:
```xml
<AxFormControl xmlns="" i:type="AxFormTabPageControl">
    <Name>NotesTabPage</Name>
    <Pattern>FillText</Pattern>
    <PatternVersion>UX7 1.0</PatternVersion>
    <WidthMode>SizeToAvailable</WidthMode>  <!-- REQUIRED -->
    ...
</AxFormControl>
```

### ActionPane Hierarchy
```
ActionPane
  -> ActionPaneTab
        -> ButtonGroup
              -> Button / CommandButton / MenuFunctionButton
```

---

## Form Extension Parent Control Validation
Before creating form extensions:
1. Find the exact control name for the `<Parent>` element: `get_object_info` on the base form with `options.searchControl` (or open the base form in VS Designer)
2. Check the parent is a container the pattern allows children in
3. If wrong parent causes failure: delete XML file, remove from `FNO.rnrproj`, rebuild

---

## Form with Child Grids (Master-Detail Pattern)

### Child Data Sources
Link child data sources to parent using `JoinSource`:
```xml
<DataSources>
    <!-- Parent data source -->
    <AxFormDataSource xmlns="">
        <Name>TAGWorkProcedure</Name>
        <Table>TAGWorkProcedure</Table>
        <InsertAtEnd>No</InsertAtEnd>
        <InsertIfEmpty>No</InsertIfEmpty>
    </AxFormDataSource>
    
    <!-- Child data source -->
    <AxFormDataSource xmlns="">
        <Name>TAGWorkProcedureRequirement</Name>
        <Table>TAGWorkProcedureRequirement</Table>
        <InsertAtEnd>No</InsertAtEnd>
        <InsertIfEmpty>No</InsertIfEmpty>
        <JoinSource>TAGWorkProcedure</JoinSource>
        <LinkType>Delayed</LinkType>
    </AxFormDataSource>
</DataSources>
```

---

## ReferenceGroupControl for Lookup Fields (CRITICAL)

### GOLDEN RULE: Never Display Raw RecIds
**Users should NEVER see numeric RecIds in forms.** Always display meaningful codes/names with lookup capability.

### When to Use ReferenceGroupControl
Use `ReferenceGroupControl` instead of `Int64Control` when:
- You have a RecId field pointing to another table
- You want automatic lookup functionality (dropdown with code/description)
- The related table has an `AutoLookup` field group

### Required Setup for ReferenceGroupControl to Work
**All three components are required:**

1. **EDT with ReferenceTable** - The table field must use an EDT that specifies the target table:
```xml
<!-- Create a RecId EDT (in AxEdt folder) -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtInt64">
    <Name>TAGMyTableRecId</Name>
    <Extends>RefRecId</Extends>
    <FormHelp>TAGMyTableForm</FormHelp>      <!-- Form for F4 lookup -->
    <Label>My Table</Label>
    <ReferenceTable>TAGMyTable</ReferenceTable>  <!-- CRITICAL -->
</AxEdt>
```

2. **Table Field with EDT** - The foreign key field must use the specific RecId EDT:
```xml
<AxTableField xmlns="" i:type="AxTableFieldInt64">
    <Name>MyTableRecId</Name>
    <ExtendedDataType>TAGMyTableRecId</ExtendedDataType>  <!-- NOT generic RefRecId -->
    <Mandatory>Yes</Mandatory>
</AxTableField>
```

3. **Form Control with ReferenceField** - Use `ReferenceField` property (NOT `DataField`):
```xml
<AxFormControl xmlns="" i:type="AxFormReferenceGroupControl">
    <Name>MyTableRecId</Name>
    <Type>ReferenceGroup</Type>
    <FormControlExtension i:nil="true" />
    <Controls />                           <!-- REQUIRED empty element -->
    <DataSource>TAGChildTable</DataSource>
    <ReferenceField>MyTableRecId</ReferenceField>  <!-- NOT DataField! -->
</AxFormControl>
```

### Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Using `<DataField>` instead of `<ReferenceField>` | Control not visible | Change to `<ReferenceField>` |
| Using generic `RefRecId` EDT on table field | No lookup, shows number | Create specific EDT with `<ReferenceTable>` |
| Missing `<Controls />` element | Metadata error | Add `<Controls />` element |
| Referenced table missing `AutoLookup` field group | Lookup shows nothing | Add `AutoLookup` group to target table |

### Converting Int64Control to ReferenceGroupControl

**Before (WRONG - shows raw number):**
```xml
<AxFormControl xmlns="" i:type="AxFormInt64Control">
    <Name>WorkerRecId</Name>
    <Type>Int64</Type>
    <FormControlExtension i:nil="true" />
    <DataField>WorkerRecId</DataField>
    <DataSource>TAGMyTable</DataSource>
</AxFormControl>
```

**After (CORRECT - shows worker code with dropdown):**
```xml
<AxFormControl xmlns="" i:type="AxFormReferenceGroupControl">
    <Name>WorkerRecId</Name>
    <Type>ReferenceGroup</Type>
    <FormControlExtension i:nil="true" />
    <Controls />
    <DataSource>TAGMyTable</DataSource>
    <ReferenceField>WorkerRecId</ReferenceField>
</AxFormControl>
```

### Standard RecId EDTs Available in Asset Management
Use these existing EDTs when referencing standard tables:
- `EntAssetWorkerRecId` → EntAssetWorker table
- `EntAssetObjectRecID` → EntAssetObjectTable (assets)
- `EntAssetFunctionalLocationRecID` → EntAssetFunctionalLocation
- `EntAssetWorkOrderLineRecID` → EntAssetWorkOrderLine

### Form Extension with ReferenceGroupControl
```xml
<AxFormExtensionControl xmlns="">
    <Name>FormExtensionControlTAGWorkProcedure</Name>
    <FormControl xmlns="" i:type="AxFormReferenceGroupControl">
        <Name>TAGWorkProcedure</Name>
        <Type>ReferenceGroup</Type>
        <FormControlExtension i:nil="true" />
        <Controls />
        <DataSource>WorkOrderLine</DataSource>
        <ReferenceField>TAGWorkProcedureRecId</ReferenceField>
        <ElementPosition>300000000</ElementPosition>
    </FormControl>
    <Parent>LinesGrid</Parent>
</AxFormExtensionControl>
```

---

## Form Extension Control Positioning

### ElementPosition Property
Use `ElementPosition` to control where extension controls appear:
- Lower numbers = appears earlier/higher in the list
- Higher numbers = appears later/lower in the list

```xml
<ElementPosition>10000000</ElementPosition>   <!-- First position -->
<ElementPosition>300000000</ElementPosition>  <!-- After line number -->
<ElementPosition>1900000000</ElementPosition> <!-- Near the end -->
```

---

## Additional Control Types

### ComboBox for Enums
```xml
<AxFormControl xmlns="" i:type="AxFormComboBoxControl">
    <Name>RequirementTypeControl</Name>
    <Type>ComboBox</Type>
    <FormControlExtension i:nil="true" />
    <DataField>RequirementType</DataField>
    <DataSource>TAGWorkProcedureRequirement</DataSource>
</AxFormControl>
```

### Real/Decimal Control
```xml
<AxFormControl xmlns="" i:type="AxFormRealControl">
    <Name>QuantityControl</Name>
    <Type>Real</Type>
    <FormControlExtension i:nil="true" />
    <DataField>Quantity</DataField>
    <DataSource>TAGWorkProcedureRequirement</DataSource>
</AxFormControl>
```

### CheckBox for NoYes Fields
```xml
<AxFormControl xmlns="" i:type="AxFormCheckBoxControl">
    <Name>RequiredControl</Name>
    <Type>CheckBox</Type>
    <FormControlExtension i:nil="true" />
    <DataField>Required</DataField>
    <DataSource>TAGWorkProcedureQualification</DataSource>
</AxFormControl>
```

---

## Header-Line Form Pattern (Parent-Child Grids)

### Child Data Source Configuration
For header-line forms, use `<JoinSource>` on the child data source (NOT DataSourceLinks):
```xml
<DataSources>
    <!-- Parent/Header data source -->
    <AxFormDataSource xmlns="">
        <Name>TAGWorkOrderTemplate</Name>
        <Table>TAGWorkOrderTemplate</Table>
        <InsertIfEmpty>No</InsertIfEmpty>
    </AxFormDataSource>
    
    <!-- Child/Line data source - Use JoinSource! -->
    <AxFormDataSource xmlns="">
        <Name>TAGWorkOrderTemplateLine</Name>
        <Table>TAGWorkOrderTemplateLine</Table>
        <JoinSource>TAGWorkOrderTemplate</JoinSource>
        <InsertAtEnd>No</InsertAtEnd>
        <InsertIfEmpty>No</InsertIfEmpty>
    </AxFormDataSource>
</DataSources>
```

### Line ActionPane with DataSource
The ActionPane containing line buttons MUST have `<DataSource>` set to the child data source:
```xml
<AxFormControl xmlns="" i:type="AxFormActionPaneControl">
    <Name>LinesActionPane</Name>
    <Type>ActionPane</Type>
    <DataSource>TAGWorkOrderTemplateLine</DataSource>
    <Style>Strip</Style>
    <Controls>
        <!-- Buttons here inherit the data source context -->
    </Controls>
</AxFormControl>
```

**Key points:**
- `<DataSource>` is on the ActionPane control, not on individual buttons
- `<Style>Strip</Style>` makes a compact action pane for the lines section
- Do NOT set `<DataSource>` on the CommandButton controls themselves

---

## Form Field Navigation (JumpRef Pattern)

### How Blue Hyperlinks Work in F&O
Fields appear as blue clickable links in grids when:
1. **Table Relation exists** - Field has a relation to another table (automatic)
2. **EDT FormHelp** - EDT has `<FormHelp>` property pointing to a form
3. **jumpRef method** - Custom navigation logic on data source field

### Form XML Dual-Structure Rule
Form XML has TWO places for data source definitions:
1. `<SourceCode><DataSources>` - Contains X++ method overrides (CDATA blocks)
2. `<DataSources>` - Contains metadata declarations (fields, properties)

Both must be synchronized when adding field-level method overrides.

### Card Form Record Positioning (Critical)
When a card form opens from a list form, it must filter to show the passed record:

**CRITICAL Settings:**
1. **`InsertIfEmpty` must be `No`** - Prevents auto-creating new records
2. **Filter in data source `init()`, not form `init()`** - Query must be set before data is fetched

### Simple Forms Without Patterns
Forms without patterns are simpler and more reliable:
```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V6">
    <Name>TAGWorkCodes</Name>
    <SourceCode>
        <Methods xmlns="">
            <Method>
                <Name>classDeclaration</Name>
                <Source><![CDATA[
[Form]
public class TAGWorkCodes extends FormRun
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
            <Name>TAGWorkCode</Name>
            <Table>TAGWorkCode</Table>
            <Fields />
            <ReferencedDataSources />
            <AllowCreate>Yes</AllowCreate>
            <AllowDelete>Yes</AllowDelete>
            <InsertAtEnd>Yes</InsertAtEnd>
            <InsertIfEmpty>No</InsertIfEmpty>
        </AxFormDataSource>
    </DataSources>
    <Design>
        <Caption xmlns="">Work Codes</Caption>
        <Controls xmlns="">
            <AxFormControl xmlns="" i:type="AxFormGridControl">
                <Name>MainGrid</Name>
                <Type>Grid</Type>
                <FormControlExtension i:nil="true" />
                <DataSource>TAGWorkCode</DataSource>
            </AxFormControl>
        </Controls>
    </Design>
    <Parts />
</AxForm>
```
**Recommendation:** Start with simple forms without patterns, add patterns only when needed.

---

## Form XML Namespace Rules (CRITICAL)

### Root Element Namespace
**Forms MUST use the V6 namespace on the root element:**
```xml
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V6">
```

### Inner Elements Use Empty Namespace
**Inner elements like Methods, Controls use empty namespace:**
```xml
<SourceCode>
    <Methods xmlns="">  <!-- Empty namespace -->
        <Method>...</Method>
    </Methods>
    <DataSources xmlns="" />  <!-- Required even if empty -->
    <DataControls xmlns="" />  <!-- Required even if empty -->
    <Members xmlns="" />       <!-- Required even if empty -->
</SourceCode>
```

### SourceCode Required Sub-elements
**The `<SourceCode>` block MUST contain these elements (even if empty):**
```xml
<SourceCode>
    <Methods xmlns="">...</Methods>
    <DataSources xmlns="" />     <!-- REQUIRED -->
    <DataControls xmlns="" />    <!-- REQUIRED -->
    <Members xmlns="" />         <!-- REQUIRED -->
</SourceCode>
```

### DataSource Required Properties
**Each `<AxFormDataSource>` should include:**
```xml
<AxFormDataSource xmlns="">
    <Name>TableName</Name>
    <Table>TableName</Table>
    <Fields />
    <ReferencedDataSources />   <!-- Add this -->
    <AllowCreate>Yes</AllowCreate>
    <AllowDelete>Yes</AllowDelete>
    <InsertAtEnd>Yes</InsertAtEnd>
    <InsertIfEmpty>No</InsertIfEmpty>  <!-- Usually No for list forms -->
</AxFormDataSource>
```

### Symptoms of Missing Elements
| Symptom | Cause | Fix |
|---------|-------|-----|
| `Metadata element is not readable` | Missing namespace or required elements | Add V6 namespace and all required sub-elements |
| Form compiles but blank | Missing `<Parts />` element | Add `<Parts />` before closing `</AxForm>` |
| Corrupted metadata error | Wrong namespace on root | Use `xmlns="Microsoft.Dynamics.AX.Metadata.V6"` |

---

## Workspace Pattern (TabbedWorkspace)

### Workspace Form Structure
```xml
<Design>
    <Caption xmlns="">Asset Health Workspace</Caption>
    <Pattern xmlns="">TabbedWorkspace</Pattern>
    <PatternVersion xmlns="">1.0</PatternVersion>
    <Style xmlns="">Workspace</Style>
    <ViewEditMode xmlns="">View</ViewEditMode>
    <ShowDeleteButton xmlns="">No</ShowDeleteButton>
    <ShowNewButton xmlns="">No</ShowNewButton>
</Design>
```

### Workspace Sections
```
TabbedWorkspace
  -> Tab (FormTabControl1)
       -> TabPage (WorkSpace)
            -> Tab (PanoramaBody) [Style=FastTabs, ExtendedStyle=tab_simpleFastTab]
                 -> TabPage (TabSummary) [Pattern=SectionTiles]
                 -> TabPage (TabTabbedList) [Pattern=SectionTabbedList]
                 -> TabPage (TabRelatedLinks) [Pattern=SectionRelatedLinks]
```

### KPI Tiles in Workspace
Use `TileButtonControl` extension:
```xml
<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
    <Name>CriticalTile</Name>
    <Type>MenuFunctionButton</Type>
    <FormControlExtension>
        <Name>TileButtonControl</Name>
        <ExtensionComponents />
        <ExtensionProperties>
            <AxFormControlExtensionProperty>
                <Name>tile</Name>
                <Type>String</Type>
                <Value>TAGAssetHealthCriticalTile</Value>
            </AxFormControlExtensionProperty>
            <AxFormControlExtensionProperty>
                <Name>tileDisplay</Name>
                <Type>Enum</Type>
                <TypeName>TileDisplay</TypeName>
                <Value>Auto</Value>
            </AxFormControlExtensionProperty>
        </ExtensionProperties>
    </FormControlExtension>
    <Text>Critical Assets</Text>
</AxFormControl>
```

### Embedded Form Parts in Workspace
Use `FormPartControl` extension:
```xml
<AxFormControl xmlns="" i:type="AxFormContainerControl">
    <Name>CriticalPart</Name>
    <AutoDeclaration>Yes</AutoDeclaration>
    <HeightMode>SizeToAvailable</HeightMode>
    <Type>Container</Type>
    <WidthMode>SizeToAvailable</WidthMode>
    <FormControlExtension>
        <Name>FormPartControl</Name>
        <ExtensionComponents>
            <AxFormControlExtensionComponent xmlns="" i:type="AxFormControlExtensionComponentComposite">
                <Name>dataLinks</Name>
                <ExtensionComponents />
            </AxFormControlExtensionComponent>
        </ExtensionComponents>
        <ExtensionProperties>
            <AxFormControlExtensionProperty>
                <Name>targetName</Name>
                <Type>String</Type>
                <Value>TAGAssetHealthCritical</Value> <!-- Menu item name -->
            </AxFormControlExtensionProperty>
            <AxFormControlExtensionProperty>
                <Name>parmRunMode</Name>
                <Type>Enum</Type>
                <TypeName>FormPartControlRunMode</TypeName>
                <Value>Local</Value>
            </AxFormControlExtensionProperty>
        </ExtensionProperties>
    </FormControlExtension>
</AxFormControl>
```

---

## FormPartSectionList Pattern (Embedded Forms)

### Part Form Structure
```xml
<Design>
    <Pattern xmlns="">FormPartSectionList</Pattern>
    <PatternVersion xmlns="">1.2</PatternVersion>
    <Style xmlns="">FormPart</Style>
</Design>
```

### Required Elements
1. **HeaderGroup** with `FiltersAndToolbarInline` pattern
2. **ContentGrid** - Main data grid
3. **GridDefaultButton** (hidden) - Double-click action
4. **SeeMoreButton** - Link to full list form

### SeeMoreButton Requirements
```xml
<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
    <Name>SeeMoreButton</Name>
    <Type>MenuFunctionButton</Type>
    <FormControlExtension i:nil="true" />
    <ButtonDisplay>TextOnly</ButtonDisplay>
    <CopyCallerQuery>Yes</CopyCallerQuery>
    <DataSource>TAGAssetHealthSnapshot</DataSource>
    <MenuItemName>TAGAssetHealthSnapshots</MenuItemName>
    <NeedsRecord>Yes</NeedsRecord>  <!-- REQUIRED by pattern -->
    <Style>Link</Style>
    <Text>See more</Text>
</AxFormControl>
```

---

## FieldsFieldGroups Pattern Requirements

### CRITICAL: Do NOT Set HeightMode/WidthMode
Controls in `FieldsFieldGroups` pattern tabs must use defaults (SizeToContent):
```xml
<!-- WRONG - causes pattern error -->
<AxFormControl xmlns="" i:type="AxFormRealControl">
    <Name>TAGAssetHealthSnapshot_RiskScore</Name>
    <HeightMode>Auto</HeightMode>  <!-- ERROR! -->
    <WidthMode>Auto</WidthMode>    <!-- ERROR! -->
    <DataField>RiskScore</DataField>
</AxFormControl>

<!-- CORRECT - omit HeightMode/WidthMode -->
<AxFormControl xmlns="" i:type="AxFormRealControl">
    <Name>TAGAssetHealthSnapshot_RiskScore</Name>
    <Type>Real</Type>
    <VerticalSpacing>-1</VerticalSpacing>
    <FormControlExtension i:nil="true" />
    <DataField>RiskScore</DataField>
    <DataSource>TAGAssetHealthSnapshot</DataSource>
</AxFormControl>
```

---

## Tile Definitions (AxTile)

### Basic Tile Structure
```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTile xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V1">
    <Name>TAGAssetHealthCriticalTile</Name>
    <Label>Critical Assets</Label>
    <MenuItemName>TAGAssetHealthCritical</MenuItemName>
    <NormalImage>Error</NormalImage>
    <Query>TAGAssetHealthCritical</Query>
    <Size>Wide</Size>
    <TileDisplay>TextAndImage</TileDisplay>
    <Type>Count</Type>
</AxTile>
```

### Tile Properties
| Property | Purpose |
|----------|---------|
| `MenuItemName` | Form to open when clicked |
| `Query` | Query for counting records |
| `NormalImage` | Icon (Manage, Warning, Error, Recent) |
| `Size` | Wide, Normal |
| `Type` | Count (shows record count) |

---

## Queries for Workspace Tiles

### Query with Range Filter
```xml
<?xml version="1.0" encoding="utf-8"?>
<AxQuery xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxQuerySimple">
    <Name>TAGAssetHealthCritical</Name>
    <SourceCode>
        <Methods>
            <Method>
                <Name>classDeclaration</Name>
                <Source><![CDATA[
[Query]
public class TAGAssetHealthCritical extends QueryRun
{
}
]]></Source>
            </Method>
        </Methods>
    </SourceCode>
    <Title>Critical Assets</Title>
    <DataSources>
        <AxQuerySimpleRootDataSource>
            <Name>TAGAssetHealthSnapshot</Name>
            <Table>TAGAssetHealthSnapshot</Table>
            <DataSources />
            <DerivedDataSources />
            <Fields>
                <AxQuerySimpleDataSourceField>
                    <Name>ObjectId</Name>
                    <Field>ObjectId</Field>
                </AxQuerySimpleDataSourceField>
            </Fields>
            <Ranges>
                <AxQuerySimpleDataSourceRange>
                    <Name>RiskCategory</Name>
                    <Field>RiskCategory</Field>
                    <Value>Critical</Value>
                </AxQuerySimpleDataSourceRange>
            </Ranges>
        </AxQuerySimpleRootDataSource>
    </DataSources>
</AxQuery>
```

### Multiple Values in Range
```xml
<Value>Moderate,High</Value>  <!-- OR condition -->
```

---

## Checklist: Converting RecId to Lookup

When converting a raw RecId field to a user-friendly lookup:

- [ ] **1. Create/Find RecId EDT** - Check if EDT exists for target table, if not create one:
  - `<Extends>RefRecId</Extends>`
  - `<ReferenceTable>TAGTargetTable</ReferenceTable>`
  - `<FormHelp>TAGTargetForms</FormHelp>`

- [ ] **2. Update Table Field** - Change `ExtendedDataType` from `RefRecId` to specific EDT

- [ ] **3. Update Form Control** - Change from `Int64Control` to `ReferenceGroupControl`:
  - Change `i:type` to `AxFormReferenceGroupControl`
  - Change `<Type>` to `ReferenceGroup`
  - Add `<Controls />`
  - Change `<DataField>` to `<ReferenceField>`

- [ ] **4. Verify Target Table** - Has `AutoLookup` field group with code and description

- [ ] **5. Build & Sync** - Rebuild in VS and synchronize database

---

## Common Form Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid enum value 'AxFormIntControl'` | Wrong control type | Use `AxFormIntegerControl` |
| `Invalid enum value 'SaveAndClose'` | Invalid command | Use Button with X++ clicked method |
| `Pattern 'DetailsFormBasic' not found` | Invalid pattern | Remove pattern or use `SimpleList` |
| `WidthMode must be 'SizeToAvailable'` | FillText requirement | Add `<WidthMode>SizeToAvailable</WidthMode>` |
| `Control not allowed at current location by pattern` | Pattern restriction | Use VS Designer or different parent |
| `Parent 'X' not found on base form` | Wrong parent name | Verify in VS Designer |
| `Metadata for Form is Corrupted` | Field in SourceCode but not DataSources | Add `<AxFormDataSourceField>` to DataSources |
| Card form opens with new blank record | `InsertIfEmpty` is `Yes` | Set `InsertIfEmpty` to `No` |
| `HeightMode must be 'SizeToContent'` | FieldsFieldGroups pattern | Remove HeightMode/WidthMode attributes |
| `NeedsRecord must be 'Yes'` | FormPartSectionList pattern | Set `<NeedsRecord>Yes</NeedsRecord>` |
| `Menu item 'X' does not exist` | Wrong menu item name | Verify exact name in AxMenuItemDisplay folder |
| ReferenceGroupControl not visible | Using `DataField` instead of `ReferenceField` | Change to `<ReferenceField>` |
| Lookup shows number instead of code | Field uses generic `RefRecId` EDT | Create/use specific RecId EDT with `<ReferenceTable>` |
| Lookup dropdown empty | Target table missing `AutoLookup` group | Add `AutoLookup` field group to target table |
