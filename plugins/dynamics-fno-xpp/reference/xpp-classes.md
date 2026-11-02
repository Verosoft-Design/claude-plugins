# F&O X++ Patterns

Ported from TAG's Cursor rule `fno-xpp-patterns.mdc` (January 2026). Notes marked **Checked 2026-10-29** were verified on F&O 10.0.46 (see `xpp-core.md`).

## X++ Event Handler Patterns

### Event Handlers Must Be in Separate Classes
Form methods CANNOT have event handler attributes:
```xpp
// WRONG - Will not compile
[Form]
public class MyForm extends FormRun
{
    [FormDataSourceEventHandler(...)]  // ERROR!
    public void onInitValue(...) { }
}

// CORRECT - Put in separate class
public static class MyFormHandler
{
    [FormDataSourceEventHandler(formDataSourceStr(MyForm, MyDataSource), FormDataSourceEventType::InitValue)]
    public static void onInitValue(FormDataSource sender, FormDataSourceEventArgs e)
    {
        // Handler code
    }
}
```

### Form Casting Limitation
You **cannot cast FormRun to a form class name**:
```xpp
// WRONG
TAGAssignments form = formRun as TAGAssignments;  // ERROR!

// CORRECT - Call methods directly on formRun
RefRecId workOrderRecId = formRun.parmWorkOrderRecId();
```

### Button with Context Passing
Use Button + event handler when passing current record as context:
```xpp
[FormControlEventHandler(formControlStr(EntAssetWorkOrderTable, TAGAssignmentsButton), FormControlEventType::Clicked)]
public static void TAGAssignmentsButton_OnClicked(FormControl sender, FormControlEventArgs e)
{
    FormRun formRun = sender.formRun();
    FormDataSource ds = formRun.dataSource(formDataSourceStr(EntAssetWorkOrderTable, WorkOrderTable));
    EntAssetWorkOrderTable record = ds.cursor();
    
    Args args = new Args();
    args.name(formStr(TAGAssignments));
    args.record(record);
    args.caller(formRun);
    
    FormRun newForm = classfactory.formRunClass(args);
    newForm.init();
    newForm.run();
    newForm.wait();
}
```

---

## Chain of Command Rules

Before writing a wrapper:
- Get the exact signature from the MCP: `get_object_info` with `options: {"method": "<name>", "include": "signature"}` (add `includeCocTemplate: true` for a skeleton). `get_knowledge` (kind `knowledge`, topic `coc-authoring`) has the full rule set.
- Check what already wraps it: `extension_info` (mode `coc`, with `method`).
- **Check the target kind.** `[ExtensionOf(tableStr(X))]`, `formStr(X)`, `classStr(X)`, `formDataSourceStr(F, DS)` and `formControlStr(F, C)` are different targets, and `this` is a different thing in each. **Checked 2026-10-29:** `EntAssetObjectTable` is both a table and a form, and `extension_info` (mode `coc`) listed TAG's form-button handler class among the table's CoC extensions. Read the `[ExtensionOf(...)]` line of each hit before relying on the list.
- The class is `final`, its name ends in `_Extension` (XPP014), and `next` is called once, unconditionally, at the top level of the wrapper.

### Default Parameters in Extensions
**Extension methods MUST NOT have default parameter values:**

```xpp
// BASE METHOD (in Microsoft table)
public void initFromServiceLevel(EntAssetServiceLevel _serviceLevel = this.ServiceLevel)
{
    // Base implementation
}

// EXTENSION METHOD - WRONG
[ExtensionOf(tableStr(EntAssetWorkOrderTable))]
final class TAGEntAssetWorkOrderTable_Extension
{
    // ERROR: Cannot have default value
    public void initFromServiceLevel(EntAssetServiceLevel _serviceLevel = this.ServiceLevel)
    {
        next initFromServiceLevel(_serviceLevel);
    }
}

// EXTENSION METHOD - CORRECT
[ExtensionOf(tableStr(EntAssetWorkOrderTable))]
final class TAGEntAssetWorkOrderTable_Extension
{
    // Correct: No default value in extension
    public void initFromServiceLevel(EntAssetServiceLevel _serviceLevel)
    {
        next initFromServiceLevel(_serviceLevel);
    }
}
```

---

## Form Field Prepopulation Pattern

**Learning:** For dialog/create forms, extend table initialization methods rather than using form events.

### Prepopulating Fields on Dialog Forms
**For dialog forms (like Create forms), extend table methods instead of using form data source events.**

#### Problem: Form Event Handlers Don't Work Reliably
```xpp
// THIS APPROACH DOESN'T WORK for dialog forms:
[FormDataSourceEventHandler(formDataSourceStr(EntAssetWorkOrderTableCreate, WorkOrderTable), FormDataSourceEventType::InitValue)]
public static void WorkOrderTable_onInitValue(FormDataSource _sender, FormDataSourceEventArgs _e)
{
    // Values set here may not display in the dialog
    EntAssetWorkOrderTable workOrder = _sender.cursor();
    workOrder.TAGDueByDate = today() + 7;
    _sender.refresh(); // Still doesn't show
}
```

#### Solution: Extend Table Initialization Methods
**Look at the base form's data source `initValue()` method to see what table method it calls:**

```xpp
// Example from EntAssetWorkOrderTableCreate.xml:
public void initValue()
{
    super();
    // ... form logic ...
    workOrderTable.initFromServiceLevel();  // <- This is what to extend!
}

[ExtensionOf(tableStr(EntAssetWorkOrderTable))]
final class TAGEntAssetWorkOrderTable_Extension
{
    public void initFromServiceLevel(EntAssetServiceLevel _serviceLevel)
    {
        TAGControls controls;
        TransDate referenceDate;
        
        // Call base implementation first
        next initFromServiceLevel(_serviceLevel);
        
        // Only for new records
        if (this.RecId)
        {
            return;
        }
        
        controls = TAGControls::find();
        if (!controls.RecId)
        {
            return;
        }
        
        // Use same date calculation as Microsoft
        referenceDate = DateTimeUtil::getSystemDate(DateTimeUtil::getUserPreferredTimeZone());
        
        // Prepopulate custom fields
        if (controls.TAGDueByLeadTime != 0)
        {
            this.TAGDueByDate = referenceDate + controls.TAGDueByLeadTime;
        }
    }
}
```

---

## Investigation Pattern for Field Prepopulation
**When you need to prepopulate fields on a form, follow this investigation pattern:**

1. **Find the base form's data source methods**: `get_object_info` on the form (`include: "source"` for one method), or the XML in `<PLD>\[Package]\[Model]\AxForm\`
2. **Look at the data source's `initValue()` method**
3. **Identify what table method is called** (e.g., `initFromServiceLevel()`, `initValue()`, etc.)
4. **Extend THAT table method** using Chain of Command

**Example investigation:**
```powershell
# Step 1: Find how base form initializes
Get-Content "J:\...\AxForm\EntAssetWorkOrderTableCreate.xml" | Select-String -Context 0,20 "initValue"

# Step 2: Look for table method calls
# You'll see: workOrderTable.initFromServiceLevel()

# Step 3: Find that table method implementation
Get-Content "J:\...\AxTable\EntAssetWorkOrderTable.xml" | Select-String -Context 0,50 "initFromServiceLevel"

# Step 4: Extend that method in your package
```

**Key principle:** Match Microsoft's patterns by extending the same methods they use for initialization.

---

## X++ Select Statement Syntax Rules

### Clause Order in Select Statements
**Checked 2026-10-29:** the MCP's select-statement knowledge confirms it ("`select t where c order by f` is a compile error, 'join' expected"), and the lint flags it (XPP018). Each joined buffer starts a new segment with its own `order by` and `where`.

**CRITICAL:** In X++ select statements, clauses MUST be in this order:
1. `select` / `select firstonly`
2. `order by` (if needed)
3. `where` (if needed)

```xpp
// WRONG - 'join' expected error
select snapshot
    where snapshot.HealthTrend == TAGHealthTrend::Declining
    order by CurrentHealthScore asc;  // ERROR! order by after where

// CORRECT - order by BEFORE where
select snapshot
    order by CurrentHealthScore asc
    where snapshot.HealthTrend == TAGHealthTrend::Declining;
```

### No "TOP N" in Select Statements
X++ does NOT support `SELECT TOP N` syntax. **Checked 2026-10-29:** the fixed sizes `firstOnly`, `firstOnly10`, `firstOnly100` and `firstOnly1000` exist; they go between `select` and the buffer. For any other N, use the Query framework. `query.topRows()` below is from the January rule and was not checked (`Query` is a kernel class, which the MCP's index doesn't cover); compile it before relying on it:

```xpp
// WRONG - Invalid syntax
select firstonly 20 snapshot  // ERROR! No TOP N support
    order by CurrentHealthScore asc;

// CORRECT - Use Query framework with topRows()
public static QueryRun getWorstHealthAssets(int _topCount = 20)
{
    Query query = new Query();
    QueryBuildDataSource qbds;
    
    qbds = query.addDataSource(tableNum(TAGAssetHealthSnapshot));
    qbds.addSortField(fieldNum(TAGAssetHealthSnapshot, CurrentHealthScore), SortOrder::Ascending);
    
    if (_topCount > 0)
    {
        query.topRows(_topCount);
    }
    
    return new QueryRun(query);
}

// Caller iterates:
QueryRun qr = TAGAssetHealthSnapshot::getWorstHealthAssets(10);
while (qr.next())
{
    TAGAssetHealthSnapshot snapshot = qr.get(tableNum(TAGAssetHealthSnapshot));
    // process...
}
```

### Join Syntax in Select Statements
When joining tables, use proper X++ join syntax:

```xpp
// WRONG - Nested/invalid join
select count(RecId) from workOrderLine
    exists join workOrder
        join asset  // ERROR! Can't nest joins like this
    where workOrder.RecId == workOrderLine.WorkOrder
    && asset.RecId == workOrderLine.ObjectTable;

// CORRECT - Flat join structure
select count(RecId) from workOrderLine
    exists join workOrder
        where workOrder.RecId == workOrderLine.WorkOrder
    exists join asset
        where asset.RecId == workOrderLine.ObjectTable
              && asset.RecId == _assetId;
```

### Type Mismatch in Join Comparisons (CRITICAL)
**Cannot compare RecId (int64) directly to String ID fields:**

```xpp
// WRONG - Type mismatch: RecId vs String
// Error: "Operator '==' cannot be applied to operands of type 'int64' and 'str'"
select fracasCase
    exists join faultSymptom
        where faultSymptom.RecId == fracasCase.ObjectFaultSymptomRecId
           && faultSymptom.Object == _objectId;  // Object is RecId, _objectId is string!

// CORRECT - Add intermediate join to match types
select fracasCase
    exists join faultSymptom
        where faultSymptom.RecId == fracasCase.ObjectFaultSymptomRecId
        exists join assetTable
            where assetTable.RecId == faultSymptom.Object    // RecId to RecId
               && assetTable.ObjectID == _objectId;          // String to String
```

**Key insight:** When filtering by a business key (like ObjectID), but the FK is a RecId, add a join to the master table to compare matching types.

### Getting Max/Latest Record
```xpp
// Get latest work order date for an asset
public static TransDate getLastWorkOrderDate(RefRecId _assetId)
{
    EntAssetWorkOrderLine workOrderLine;
    EntAssetWorkOrderTable workOrder;
    
    select firstonly workOrder
        order by CreatedDateTime desc
        exists join workOrderLine
            where workOrderLine.WorkOrder == workOrder.RecId
               && workOrderLine.ObjectTable == _assetId;
    
    if (workOrder.RecId)
    {
        return DateTimeUtil::date(workOrder.CreatedDateTime);
    }
    return dateNull();
}
```

---

## Asset Management Module Reference

### EntAssetObjectTable (Asset Master)
Key fields to know:
- `ObjectType` - RecId reference to `EntAssetObjectType` (asset type/group)
- NOT `ObjectGroup` - this field doesn't exist!

```xpp
// WRONG - Field doesn't exist
select asset where asset.ObjectGroup == _groupId;  // ERROR!

// CORRECT - Use ObjectType
select asset where asset.ObjectType == _assetTypeId;

// To find profile by asset type:
TAGHealthIndexProfile profile;
EntAssetObjectTable asset = EntAssetObjectTable::find(_assetId);

select firstonly profile
    where profile.EntAssetObjectTypeId == asset.ObjectType
       && profile.IsActive == true;
```

### Dynamic Field Access with DictTable/DictField
For configurable field lookups (e.g., health index data sources):

```xpp
public real getFieldValue(Common _record, str _fieldName)
{
    DictTable dictTable = new DictTable(_record.TableId);
    DictField dictField;
    FieldId fieldId;
    
    fieldId = dictTable.fieldName2Id(_fieldName);
    if (fieldId)
    {
        dictField = new DictField(_record.TableId, fieldId);
        if (dictField)
        {
            return _record.(fieldId);  // Dynamic field access
        }
    }
    return 0;
}
```

---

## Form Control Access in X++

### Runtime vs Compile-Time Control Lookup (CRITICAL)

**Note (2026-10-29):** `formControlStr(Form, Control)` is checked at compile time against the form's compiled metadata, which is a safety net, not a defect. The error below means the compiler didn't see that control in that form: it was misnamed, created at runtime, or the form hadn't been built yet. Prefer `formControlStr` for controls defined in the form's XML, and fall back to the string literal with a null check for controls built at runtime.

**WRONG - formControlStr is compile-time validation:**
```xpp
// This FAILS at compile time for XML-created forms:
FormRealControl healthScoreCtrl = this.design().controlName(formControlStr(TAGAssetHealthDetail, HealthScoreDisplay));
// Error: "Form control 'HealthScoreDisplay' is not found in 'TAGAssetHealthDetail'"
```

**CORRECT - Use string literal for runtime lookup:**
```xpp
// This works - control is found at runtime:
FormRealControl healthScoreCtrl = this.design().controlName('HealthScoreDisplay');
if (healthScoreCtrl)
{
    healthScoreCtrl.realValue(currentSnapshot.CurrentHealthScore);
}
```

### Pattern for Updating Form Controls
```xpp
public void updateKPIs()
{
    FormRealControl totalAssetsCtrl;
    FormRealControl avgHealthCtrl;
    
    // Always use string literals and null-check
    totalAssetsCtrl = this.design().controlName('TotalAssetsValue');
    if (totalAssetsCtrl)
    {
        totalAssetsCtrl.realValue(totalAssets);
    }
    
    avgHealthCtrl = this.design().controlName('AvgHealthValue');
    if (avgHealthCtrl)
    {
        avgHealthCtrl.realValue(avgHealthScore);
    }
}
```

### Form Control Type Reference
| Control Type | X++ Class |
|--------------|-----------|
| String | `FormStringControl` |
| Real | `FormRealControl` |
| Integer | `FormIntControl` |
| DateTime | `FormDateTimeControl` |
| ComboBox | `FormComboBoxControl` |
| CheckBox | `FormCheckBoxControl` |
| Grid | `FormGridControl` |
| Tab | `FormTabControl` |

---

## Data Source Methods in Form XML

### Dual Structure Rule
Form XML has TWO places for data source methods:
1. `<SourceCode><DataSources>` - X++ method overrides (CDATA blocks)
2. `<DataSources>` - Metadata declarations

**Both must be synchronized:**
```xml
<SourceCode>
    <DataSources xmlns="">
        <DataSource>
            <Name>TAGAssetHealthSnapshot</Name>
            <Methods>
                <Method>
                    <Name>init</Name>
                    <Source><![CDATA[
        public void init()
        {
            super();
            if (assetId)
            {
                this.query().dataSourceTable(tableNum(TAGAssetHealthSnapshot))
                    .addRange(fieldNum(TAGAssetHealthSnapshot, AssetId))
                    .value(queryValue(assetId));
            }
        }
]]></Source>
                </Method>
            </Methods>
        </DataSource>
    </DataSources>
</SourceCode>
<DataSources>
    <AxFormDataSource xmlns="">
        <Name>TAGAssetHealthSnapshot</Name>  <!-- Must match! -->
        <Table>TAGAssetHealthSnapshot</Table>
        <!-- ... -->
    </AxFormDataSource>
</DataSources>
```

### Calling Form Methods from Button Handlers
```xml
<DataControls xmlns="">
    <Control>
        <Name>RecalculateButton</Name>
        <Type>CommandButton</Type>
        <Methods>
            <Method>
                <Name>clicked</Name>
                <Source><![CDATA[
        public void clicked()
        {
            super();
            element.recalculateHealth();  // Call form method
        }
]]></Source>
            </Method>
        </Methods>
    </Control>
</DataControls>
```

---

## Table Field Denormalization Pattern

### Store Business Keys for Display
When linking to other tables, store both RecId (for relations) and business key (for display):

```xpp
// Table fields:
// AssetId (RefRecId) - FK to EntAssetObjectTable.RecId
// ObjectId (EntAssetObjectID) - Business key for display

public static TAGAssetHealthSnapshot updateOrCreate(RefRecId _assetId, RefRecId _profileId, real _healthScore)
{
    TAGAssetHealthSnapshot snapshot;
    EntAssetObjectTable assetTable;
    
    // Get ObjectID from asset table
    select firstonly ObjectID from assetTable
        where assetTable.RecId == _assetId;
    
    ttsbegin;
    snapshot = TAGAssetHealthSnapshot::findByAsset(_assetId, true);
    
    if (snapshot.RecId)
    {
        snapshot.ObjectId = assetTable.ObjectID;  // Denormalize business key
        snapshot.CurrentHealthScore = _healthScore;
        snapshot.update();
    }
    else
    {
        snapshot.AssetId = _assetId;
        snapshot.ObjectId = assetTable.ObjectID;  // Denormalize business key
        snapshot.CurrentHealthScore = _healthScore;
        snapshot.insert();
    }
    ttscommit;
    
    return snapshot;
}
```

**Benefits:**
- Forms can display ObjectId directly without joins
- Filters/searches work on business key
- Reduces join complexity in queries

---

## Field Name Verification Pattern (CRITICAL)

### Always Verify Field Names Before Coding
**BEFORE writing X++ code that references table fields, VERIFY the actual field names exist.** First choice: the MCP, `get_object_info` (`objectType: "table"`, with `options.fieldFilter` for wide tables), or the `fno-explorer` agent. For a standard table, `extension_info` (mode `table-merge`) shows the fields every model adds. Reading the XML works too:

```powershell
# Check what fields exist in a table
Get-Content "J:\...\AxTable\TAGFMEAHeader.xml" | Select-String -Pattern "<Name>.*</Name>" | Select-Object -First 30

# Or search for specific field pattern
grep -A 1 "AxTableField" "J:\...\AxTable\TAGFMEAFailureMode.xml"
```

### Common Field Name Mismatches

| Assumed Name | Actual Name | Table |
|--------------|-------------|-------|
| `FMEAId` | `FMEACode` | TAGFMEAHeader |
| `FMEAHeaderRecId` | `HeaderRecId` | TAGFMEAFailureMode |
| `FailureModeDescription` | `FunctionFailure` | TAGFMEAFailureMode |
| `AssetRecId` | May not exist | Check table definition |

### Pattern: Read Table XML First
**Before writing service class methods that query tables:**
1. Open the table XML file
2. Search for `<Fields>` section
3. Note exact field names (case-sensitive!)
4. Use those exact names in X++ code

```xpp
// WRONG - Assumed field names
analysis.Description = strFmt("RCM from FMEA: %1", fmeaHeader.FMEAId);  // FMEAId doesn't exist!

// CORRECT - Verified field names
analysis.Description = strFmt("RCM from FMEA: %1", fmeaHeader.FMEACode);  // Actual field name
```
