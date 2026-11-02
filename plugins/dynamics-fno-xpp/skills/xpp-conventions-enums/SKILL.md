---
name: xpp-conventions-enums
description: X++ rules for enums and enum extensions in F&O metadata XML (Value vs EnumValue, the implicit 0, extensible enums, labels and the blank-dropdown question, build order). Loads automatically when working on AxEnum or AxEnumExtension files.
user-invocable: false
paths:
  - "**/AxEnum/*.xml"
  - "**/AxEnumExtension/*.xml"
---

# Enums

Full rules and XML: `${CLAUDE_PLUGIN_ROOT}/reference/xpp-enums.md`. Core rules: the `xpp-conventions` skill.

- **Values:** each `<AxEnumValue>` has `<Name>`, `<Label>` and `<Value>`. Only the first may omit `<Value>` (it is 0); a second value without one is "Duplicate value 0". The tag is `<Value>`, never `<EnumValue>` (lint XPP010).
- **TAG convention:** new enums set `<UseEnumValue>No</UseEnumValue>` and `<IsExtensible>true</IsExtensible>`, lowercase `true` (lint XPP006). An extensible enum can't use `UseEnumValue` Yes, and code must never depend on its integer values. 1,548 of 5,270 standard enums are extensible; the rest have neither property.
- **Extending a standard enum:** an `AxEnumExtension` named `<BaseEnum>.<Model>`, and only when the base is extensible (check with `get_object_info`).
- **Labels:** label IDs (`@TAGLabels:MyValue`), never literal text; xppbp reports literals as `BPErrorLabelIsText` (decided 2026-11-02, replacing TAG's January rule). A label ID that shows as raw text or blank in a dropdown means the label doesn't resolve: either the label file wasn't compiled (create labels with the MCP's `labels` tool, or build the model, which runs `labelc`), or the reference names the wrong file ID. TAG's label file ID is `TAGLabels`, not `TAG`. After the build, open the form and check the dropdown (`xpp-ui-test`).
- **Build order:** the first build after adding an enum and code that uses it can fail with "Qualifier 'X' not valid". Build again; the enum compiles first.
