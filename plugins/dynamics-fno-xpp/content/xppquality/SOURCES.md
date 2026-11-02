# Sources to vendor for the X++ review content

Nothing below is vendored yet. This is the list Phase 3 of the plan (`docs/superpowers/plans/2026-10-29-fno-xpp-plugin.md`) asked for: exact files, pinned commits and licences. The plan is to vendor them the way `business-central-al` vendors BCQuality (`content/PINNED.json`, a `scripts/vendor-*.sh`, then hand-written knowledge articles that cite them).

Listed on 2026-10-29 from blobless clones (file names only, no content downloaded).

## 1. MicrosoftDocs/dynamics-365-unified-operations-public

- **Pinned commit:** `c4cce79a3ded830fff97c00e088ef98a15115e0e` (2026-10-29), branch `main`.
- **Licence:** the documentation text is **CC BY 4.0** (`LICENSE`: "Attribution 4.0 International"); the code samples are **MIT** (`LICENSE-CODE`, Copyright (c) Microsoft Corporation).
- **What CC BY 4.0 requires:** credit Microsoft, link the licence, say what was changed, and add no restriction on top. Each vendored or derived article keeps a source line: the file path, the commit and "CC BY 4.0, adapted".
- **Root:** `articles/fin-ops-core/dev-itpro/`.

### dev-ref: the X++ language (48 files, domains: performance, data-modeling, extensibility)

- `dev-ref/api-reference.md`
- `dev-ref/application-explorer-aot-properties.md`
- `dev-ref/query-with-parameters.md`
- `dev-ref/sql-connection-error.md`
- `dev-ref/sysda.md`
- `dev-ref/system-tables.md`
- `dev-ref/xpp-attribute-classes.md`
- `dev-ref/xpp-business-run-time-functions.md`
- `dev-ref/xpp-classes-methods.md`
- `dev-ref/xpp-compile-time-functions.md`
- `dev-ref/xpp-conditional.md`
- `dev-ref/xpp-container-run-time-functions.md`
- `dev-ref/xpp-conversion-run-time-functions.md`
- `dev-ref/xpp-cs-comparison.md`
- `dev-ref/xpp-data-collection.md`
- `dev-ref/xpp-data-composite.md`
- `dev-ref/xpp-data-edt.md`
- `dev-ref/xpp-data-primitive.md`
- `dev-ref/xpp-data/xpp-data-home-page.md`
- `dev-ref/xpp-data/xpp-data-perf.md`
- `dev-ref/xpp-data/xpp-delete.md`
- `dev-ref/xpp-data/xpp-insert.md`
- `dev-ref/xpp-data/xpp-select-expression.md`
- `dev-ref/xpp-data/xpp-select-statement.md`
- `dev-ref/xpp-data/xpp-select.md`
- `dev-ref/xpp-data/xpp-transaction.md`
- `dev-ref/xpp-data/xpp-update.md`
- `dev-ref/xpp-data/xpp-while-select.md`
- `dev-ref/xpp-date-run-time-functions.md`
- `dev-ref/xpp-events.md`
- `dev-ref/xpp-exceptions.md`
- `dev-ref/xpp-inheritance.md`
- `dev-ref/xpp-interfaces.md`
- `dev-ref/xpp-language-reference.md`
- `dev-ref/xpp-library-objects.md`
- `dev-ref/xpp-loops.md`
- `dev-ref/xpp-macros.md`
- `dev-ref/xpp-math-run-time-functions.md`
- `dev-ref/xpp-operator-precedence.md`
- `dev-ref/xpp-operators.md`
- `dev-ref/xpp-reflection-run-time-functions.md`
- `dev-ref/xpp-run-time-functions.md`
- `dev-ref/xpp-session-run-time-functions.md`
- `dev-ref/xpp-statements-loops.md`
- `dev-ref/xpp-static-classes.md`
- `dev-ref/xpp-string-run-time-functions.md`
- `dev-ref/xpp-syntax.md`
- `dev-ref/xpp-variables-data-types.md`

### extensibility: extensions, CoC, events (62 files, domain: extensibility)

- `extensibility/Changes-80.md`
- `extensibility/add-datasource.md`
- `extensibility/add-enum-value.md`
- `extensibility/add-field-extension.md`
- `extensibility/add-index.md`
- `extensibility/add-method-table.md`
- `extensibility/add-relation.md`
- `extensibility/app-sealing-faq.md`
- `extensibility/breaking-changes.md`
- `extensibility/change-caption-form.md`
- `extensibility/changes-july-2017.md`
- `extensibility/class-extensions.md`
- `extensibility/compatibility-checker-tool.md`
- `extensibility/customization-overlayering-extensions.md`
- `extensibility/customize-model-elements-extensions.md`
- `extensibility/decimal-point-precision.md`
- `extensibility/extend-number-sequence-scope.md`
- `extensibility/extend-runbase-class.md`
- `extensibility/extensibility-attributes.md`
- `extensibility/extensibility-changes-10-1.md`
- `extensibility/extensibility-changes-10-2.md`
- `extensibility/extensibility-changes-10-3.md`
- `extensibility/extensibility-changes-10.md`
- `extensibility/extensibility-changes-73.md`
- `extensibility/extensibility-changes-801.md`
- `extensibility/extensibility-changes-802.md`
- `extensibility/extensibility-changes-803.md`
- `extensibility/extensibility-changes-804.md`
- `extensibility/extensibility-changes-81.md`
- `extensibility/extensibility-changes-811.md`
- `extensibility/extensibility-changes-812.md`
- `extensibility/extensibility-changes-813.md`
- `extensibility/extensibility-home-page.md`
- `extensibility/extensibility-new.md`
- `extensibility/extensibility-requests.md`
- `extensibility/extensibility-roadmap.md`
- `extensibility/extensible-classes.md`
- `extensibility/extensible-code-delegates.md`
- `extensibility/extensible-edts.md`
- `extensibility/extensible-enums.md`
- `extensibility/extensible-forms.md`
- `extensibility/extensible-methods.md`
- `extensibility/extensible-tables.md`
- `extensibility/intrusive-customizations.md`
- `extensibility/inventory-dimensions.md`
- `extensibility/map-extensions.md`
- `extensibility/maps-as-interfaces.md`
- `extensibility/maps-with-versioning.md`
- `extensibility/method-wrapping-coc.md`
- `extensibility/migrate-overlayer-extension.md`
- `extensibility/modify-control-properties.md`
- `extensibility/modify-edt.md`
- `extensibility/modify-existing-field.md`
- `extensibility/modify-properties.md`
- `extensibility/naming-guidelines-extensions.md`
- `extensibility/pricing-app73.md`
- `extensibility/refactoring-over-layering.md`
- `extensibility/register-subclass-factory-methods.md`
- `extensibility/respond-event-handler-result.md`
- `extensibility/startup-customizations.md`
- `extensibility/subscribe-table-events.md`
- `extensibility/writing-extensible-code.md`

### perf-test: SysTest, ATL, trace parser (24 files outside `rsat/`, domains: testing, performance)

RSAT (`perf-test/rsat/`, 19 files) is left out: it is unsupported after May 2027.

- `perf-test/acceptance-test-library.md`
- `perf-test/atl-best-practices.md`
- `perf-test/atl-faq.md`
- `perf-test/batch-para-multi-thread.md`
- `perf-test/code-generation-wizard.md`
- `perf-test/concepts-commands.md`
- `perf-test/concepts-creators.md`
- `perf-test/concepts-entities.md`
- `perf-test/concepts-navigation.md`
- `perf-test/concepts-queries.md`
- `perf-test/concepts-specifications.md`
- `perf-test/continuous-build-test-automation.md`
- `perf-test/performance-timer.md`
- `perf-test/perfsdk-multi-user-testing.md`
- `perf-test/public-application-tests.md`
- `perf-test/single-user-test-perf-sdk.md`
- `perf-test/systest-filtering.md`
- `perf-test/systest-row.md`
- `perf-test/test-data-methods.md`
- `perf-test/testing-support.md`
- `perf-test/testing-validation.md`
- `perf-test/trace-parser.md`
- `perf-test/trace-trace-tutorial.md`
- `perf-test/troubleshoot-perf-sdk-user-testing.md`

### Best practice and review (domain: all)

- `dev-tools/customization-analysis-report.md`: the `BPCheck*` rules of the Customization Analysis Report (the plan counts 27; not recounted)
- `dev-tools/design-best-practices.md`
- `dev-tools/author-best-practice-rules.md`

### Security (domain: security)

- `sysadmin/role-based-security.md`
- `sysadmin/security-architecture.md`
- `sysadmin/extensible-data-security-policies.md`
- `data-entities/security-data-entities.md`

### Form patterns (domain: ui; 39 pattern and subpattern pages)

- `user-interface/advanced-selection-form-pattern.md`
- `user-interface/custom-filter-group-subpattern.md`
- `user-interface/details-master-form-pattern.md`
- `user-interface/details-transaction-form-pattern.md`
- `user-interface/dialog-form-pattern.md`
- `user-interface/drop-dialog-form-pattern.md`
- `user-interface/factbox-form-patterns.md`
- `user-interface/fields-field-groups-subpattern.md`
- `user-interface/fill-text-subpattern.md`
- `user-interface/filters-toolbar-subpattern.md`
- `user-interface/form-pattern-add-ins.md`
- `user-interface/form-styles-patterns.md`
- `user-interface/horizontal-fields-buttons-group-subpattern.md`
- `user-interface/image-preview-subpattern.md`
- `user-interface/list-page-form-pattern.md`
- `user-interface/list-panel-subpattern.md`
- `user-interface/lookup-form-pattern.md`
- `user-interface/nested-simple-list-details-subpattern.md`
- `user-interface/section-chart-form-pattern.md`
- `user-interface/section-list-form-pattern.md`
- `user-interface/section-powerbi-subpattern.md`
- `user-interface/section-related-links-subpattern.md`
- `user-interface/section-stacked-chart-subpattern.md`
- `user-interface/section-tabbed-list-subpattern.md`
- `user-interface/section-tiles-subpattern.md`
- `user-interface/select-form-pattern.md`
- `user-interface/simple-details-form-pattern.md`
- `user-interface/simple-list-details-form-pattern.md`
- `user-interface/simple-list-form-pattern.md`
- `user-interface/table-of-contents-form-pattern.md`
- `user-interface/tabular-fields-subpattern.md`
- `user-interface/task-double-form-pattern.md`
- `user-interface/task-single-form-pattern.md`
- `user-interface/testing-forms-custom-patterns.md`
- `user-interface/toolbar-fields-subpattern.md`
- `user-interface/toolbar-list-subpattern.md`
- `user-interface/wizard-form-pattern.md`
- `user-interface/workspace-filter-group-subpattern.md`
- `user-interface/workspace-form-pattern.md`

## 2. microsoft/Dynamics365FO-AppChecker

- **Pinned commit:** `07124ead370a3da60a1065852d6737d3aee78fe1` (2025-06-23, the latest commit on `main`).
- **Licence:** **MIT** (Copyright (c) Microsoft Corporation).
- **Files:** `rules/X++/*.xq`, 21 XQuery rules over the X++ AST, plus `rules/X++/ExcludedRules.lst`: BalancedTtsStatement, BooleanExpressionWithLiteral, Breakpoint, ComplexityIndentationCombined, ConstantConditions, ConstrainedStringTypes, DeleteFromNotUsed, DirectSQL, ExtensionsWithoutPrefix, InsertInLoop, MissingClassDocumentation, MissingMethodDocumentation, NestedSearch, RecursiveMethods, SelectForUpdateAbsent, SelectUsingFirstOnly, SystemReflection, TableIndex, TableTPFIntegrity, callsnext, skipResultsNeverUsed.
- **Use:** each rule becomes a knowledge article (description, best practice, anti pattern) in the matching domain, citing the `.xq` file. The queries themselves need AppChecker's BaseX tooling to run, so they are documentation for the reviewer, not something the plugin executes.
- `Sample rules/X++/` holds 235 more sample queries. Don't vendor them; mine them for ideas.

## 3. Success by Design: extend Finance and Operations apps

- **Page:** <https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/extend-your-solution-guidance-product-fo> (the go-live checklist for extensions).
- **Source repo:** not located yet (it isn't in `dynamics-365-unified-operations-public`). Find it before vendoring; Learn guidance text is normally CC BY 4.0, but check the repo's `LICENSE`.

## 4. Already available at run time, not to vendor

- **d365fo-mcp-server** (MIT, Copyright (c) 2026 dynamics365ninja): its `get_knowledge` rulebook (`coc-authoring`, `select-statement`, `unit-testing`, `test-data-atl`, `bp-rules`, `security`, form patterns) and its BP-moniker catalogue. The review skill should call it rather than copy it.
- **The TAG Cursor rules** (January 2026): already ported to `reference/`.

## 5. Candidates, not checked

- TrudAX/d365fo-xpp-skills (listed as MIT in the plan): build and where-used skills from the community. Check its licence and content before taking anything.
