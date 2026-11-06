---
fno-version: [all]
domain: ui
keywords: [form-pattern, pattern-version, detailsmaster, simplelist, form-xml, controls]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# Use form patterns and control types that the platform ships

## Description

A form's `Pattern` and `PatternVersion` must name a pattern the platform knows, and each `AxFormControl` must use a real control type. A survey of 6,544 standard forms on 10.0.46 found 62 patterns. Among them are `SimpleList` 1.1, `SimpleListDetails` 1.3, `DetailsMaster` 1.4, `DetailsTransaction` 1.4, `ListPage` UX7 1.0, `Dialog` 1.2 and `TableOfContents` 1.1. The survey also found 37 control types, for example `AxFormIntegerControl` (not `AxFormIntControl`) and `AxFormReferenceGroupControl`. Names such as `DetailsFormMaster`, `DetailsFormBasic` and a bare `SimpleDetails` don't exist and fail the build.

## Best Practice

Pick the pattern for the form's job (list, list with details, master record, transaction, dialog, setup), scaffold it with the d365fo MCP (`generate_object`, mode `scaffold:form`) or copy a standard form of the same pattern, and let the pattern's required controls guide the layout. Check the result in the web client.

## Anti Pattern

Inventing a pattern name or version, or removing required pattern controls until the build passes, which leaves a form that compiles but renders blank or breaks the pattern's behaviour.
