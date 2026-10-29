# F&O Enum XML Rules

Ported from TAG's Cursor rule `fno-enums.mdc` (January 2026). Notes marked **Checked 2026-10-29** were verified on F&O 10.0.46 (see `xpp-core.md`).

## Enum XML Structure (CRITICAL FOR DROPDOWN DISPLAY)

### Required Properties for Working Enums
**TAG convention: every new enum sets these two properties:**

```xml
<UseEnumValue>No</UseEnumValue>
<IsExtensible>true</IsExtensible>
```

**Checked 2026-10-29:** 1,548 of 5,270 standard enums are extensible (`IsExtensible` true, `UseEnumValue` No). The other 3,722 have neither property and display fine, so missing properties alone don't explain blank dropdowns. Keep the convention: extensible enums let other models add values. Note the compiler rule: an extensible enum can't use `UseEnumValue` Yes, and code must never rely on its integer values.

### Enum Value Tag Name
**CRITICAL:** Use `<Value>` tag, NOT `<EnumValue>` tag:

```xml
<!-- WRONG - Causes compile errors -->
<AxEnumValue>
    <Name>Open</Name>
    <EnumValue>0</EnumValue>  <!-- Wrong tag! -->
</AxEnumValue>

<!-- CORRECT -->
<AxEnumValue>
    <Name>Open</Name>
    <Value>1</Value>  <!-- Correct tag -->
    <Label>Open</Label>
</AxEnumValue>
```

### First Enum Value (Index 0)
**Omit `<Value>` tag from first enum value** - it defaults to 0:

```xml
<!-- CORRECT - First value defaults to 0 -->
<AxEnumValue>
    <Name>First</Name>
    <Label>First Value</Label>
    <!-- No <Value> tag needed -->
</AxEnumValue>
<AxEnumValue>
    <Name>Second</Name>
    <Label>Second Value</Label>
    <Value>1</Value>  <!-- Explicit value for non-zero -->
</AxEnumValue>
```

### Label References (disputed, decide per repo)
**The TAG rule from January 2026 says to use hardcoded labels, not label file references:**

```xml
<!-- WRONG - Label references don't render in enum dropdowns -->
<Label>@TAGLabels:MyEnumValue</Label>

<!-- CORRECT - Hardcoded text works -->
<Label>My Enum Value</Label>
```

**Note:** Microsoft's base enums use label references, but for custom enums created via XML editing, hardcoded labels were more reliable at the time.

**Checked 2026-10-29, conflicts with best practice:** xppbp reports every hardcoded label as `BPErrorLabelIsText`; the TAG table and class it was run on had 5 and 6 of them. A label ID shows as literal text when the label file hasn't been compiled (`labelc`). Hand-edited XML never triggered that compile, while the MCP's write tools and `build_d365fo_project` do. Hypothesis, not yet verified: label IDs work once labels are compiled. Until the repo owner decides, follow what the repo's existing enums do, and open the form after the build (`xpp-ui-test`) to check the dropdown.

### Build Order for New Enums
1. Create enum XML files first
2. Build project to register enums
3. Then add X++ code referencing enum values
4. "Qualifier not valid" errors = enum not compiled yet

### "Qualifier Not Valid" Error Explained
**Error:** `The qualifier 'TAGMyEnum' is not valid for field 'EnumValue'`

**Cause:** The enum hasn't been compiled yet, so the compiler doesn't recognize `TAGMyEnum::EnumValue` syntax.

**Solutions:**
1. **Build twice** - First build compiles enums, second build compiles X++ code
2. **Check enum XML structure** - Ensure `UseEnumValue` and `IsExtensible` are correct
3. **Verify project file** - Enum must be in `FNO.rnrproj`

**Note:** When creating multiple new enums + classes together, expect this error on first build. Rebuild to resolve.

---

## Enum XML Template (Visual Studio Standard)

**This is the EXACT structure Visual Studio Designer creates:**

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
            <!-- First value defaults to 0 -->
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

---

## Common Enum Errors

| Error/Symptom | Cause | Solution |
|-------|-------|----------|
| **Dropdown shows blank values** | Missing `UseEnumValue` or `IsExtensible` properties | Add `<UseEnumValue>No</UseEnumValue>` and `<IsExtensible>true</IsExtensible>` |
| **Dropdown shows literal label references** | Using `@LabelFile:Label` format | Use hardcoded label text instead |
| **Compile error: tag `EnumValue`** | Using wrong XML tag | Change `<EnumValue>` to `<Value>` |
| `Content cannot be converted to Boolean` | Using `Yes`/`No` | Use lowercase `true`/`false` |
| `UseEnumValue must be 'No' when IsExtensible is 'True'` | Invalid property combination | Always use `UseEnumValue="No"` with `IsExtensible="true"` |
| `Qualifier 'EnumName' not valid` | Enum not compiled | Build enums first, then add references |
| `Duplicate value '0' detected` | Multiple values without explicit `<Value>` | Only first value should omit `<Value>` tag |

---

## Invalid Property Combinations

**These combinations cause blank dropdowns:**

```xml
<!-- WRONG - Causes blank dropdowns -->
<IsExtensible>false</IsExtensible>
<UseEnumValue>true</UseEnumValue>

<!-- CORRECT - Works properly -->
<UseEnumValue>No</UseEnumValue>
<IsExtensible>true</IsExtensible>
```
