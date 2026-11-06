---
fno-version: [all]
domain: extensibility
keywords: [chain-of-command, coc, extensionof, next, wrapper, default-parameters]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# Chain of Command wrappers repeat the signature without defaults and call next once

## Description

A Chain of Command (CoC) wrapper lives in a `final` class marked `[ExtensionOf(tableStr(X))]` (or `classStr`, `formStr`, `formDataSourceStr`, `formControlStr`, `dataEntityViewStr`, `mapStr`, `viewStr`). The compiler requires the class name to end in `_Extension`. The wrapper repeats the base method's parameters without their default values, and calls `next <method>(...)` exactly once, unconditionally, at the top level of the method. Methods the extension class adds (not wrappers) may declare defaults. In a 10.0.46 sample of 5,564 standard objects, 8 such added methods do, and no wrapper does.

## Best Practice

Read the base signature from the symbol source before writing (the d365fo MCP's `get_object_info` with `include: "signature"`), copy the parameter list without the `= default` parts, and put the added logic before or after a single `next` call. Check existing wrappers on the same method (`extension_info`, mode `coc`) so two models don't fight over the same behaviour.

## Anti Pattern

Copying `_serviceLevel = this.ServiceLevel` into the wrapper's parameter list, calling `next` inside an `if`, a loop or a `try` block, or naming the class `TAGWorkOrderTableExt`. All three fail the build, and a conditional `next` silently skips other models' wrappers.
