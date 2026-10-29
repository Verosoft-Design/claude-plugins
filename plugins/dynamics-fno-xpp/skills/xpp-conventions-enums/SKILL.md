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
- **Labels, open question:** TAG's January rule says to write literal text, because label IDs showed blank or literal in dropdowns. xppbp reports every literal as `BPErrorLabelIsText`. The likely cause was label files that were never compiled: hand-edited XML didn't run `labelc`, while the MCP's `labels` tool and builds do. This hasn't been verified on TAG. Until the repo owner decides, follow what the repo's existing enums do, and open the form after the build to check the dropdown (`xpp-ui-test`).
- **Build order:** the first build after adding an enum and code that uses it can fail with "Qualifier 'X' not valid". Build again; the enum compiles first.
