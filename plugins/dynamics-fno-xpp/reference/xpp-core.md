# X++ core rules

Ported from TAG's Cursor rule `fno-core.mdc` (January 2026, written while building The Asset Guardian model by editing XML directly). The corrections marked **Checked 2026-10-29** come from F&O 10.0.46: a survey of 143,603 standard XML files, the compiler's reserved-word list, and xppbp runs. See the plugin's CHANGELOG.

**Goal:** make changes by editing F&O metadata XML in the model folder (PackagesLocalDirectory or a repo that holds the package), then build, sync and test on the dev VM.

---

## Golden principles

1. **The metadata XML is the source of truth**, under `<Package>/<Model name>/` (for example `TheAssetGuardian/The Asset Guardian/`).
2. The agent edits XML, preferably through the d365fo MCP's write tools (`d365fo_file`, `generate_object`, `labels`), which go through Microsoft's metadata API and register the object in the project. The dev VM is used for:
   - build/compile (`xpp-build`);
   - database sync (`xpp-db-sync`);
   - running tests (`xpp-run-tests`) and the UI (`xpp-ui-test`);
   - Visual Studio's designer, when a form layout is too complex for XML.
3. **Never edit objects outside your model or package.** Only create *extensions* in your package.
4. Keep changes **minimal and additive**: no overlayering, no edits to base objects.
5. Prefer **stable patterns**: table extensions, form extensions, Chain of Command (CoC), event handlers and data contracts.
6. Standard examples to copy: `PackagesLocalDirectory\EnterpriseAssetManagementAppSuite\EnterpriseAssetManagementAppSuite` has thousands of XML files. Find them with the MCP's `search` and `object_patterns`, or the `fno-explorer` agent.

---

## Repository layout and boundaries

- All work happens in the model folder: `<Package>\<Model name>\`.
- Primary folders: `AxClass\`, `AxTable\`, `AxTableExtension\`, `AxForm\`, `AxFormExtension\`, `AxViewExtension\`, `AxEdt\`, `AxEnum\`, `AxMenuItemDisplay\`, `AxSecurityRole\`, `AxSecurityDuty\`, `AxSecurityPrivilege\`, `AxLabelFile\`. `Descriptor\` sits one level up, in the package.
- Register every new object in the package's `.rnrproj` (TAG: `FNO.rnrproj`). The lint flags a missing entry (XPP012).
- **Don't generate** build outputs or temp files unless explicitly required. `BuildModelResult.*`, `BuildProjectResult.*`, `CompileLabels.xml`, `*.xref` and `Resources\*.delete` are build leftovers. Don't commit them.

---

## Naming and conventions (strict)

- Prefix everything with the model prefix (TAG: `TAG`). The session-start hook prints the prefix it detected; `FNO_XPP_PREFIX` overrides it.
- **Extensions:**
  - table extension: `BaseTable.<Model or suffix>`, e.g. `EntAssetWorkOrderTable.TheAssetGuardian`;
  - form extension: `BaseForm.<Model or suffix>`;
  - **extension classes must end in `_Extension`**, e.g. `TAGWorkOrderFormHandler_Extension`. The compiler refuses anything else: "Invalid extension class name" (XPP014).
- **Naming patterns:**
  - Class: `TAG<Area><Purpose>` (e.g., `TAGAssetService`)
  - EDT: `TAGEdt<Meaning>` (e.g., `TAGEdtAssignedWorkers`), and `TAG<Table>RecId` for record-reference EDTs
  - Enum: `TAG<Meaning>` (e.g., `TAGDependencyType`)
  - Table: `TAG<Purpose>` (e.g., `TAGAssignment`)
  - Form: `TAG<Purpose>`, usually the plural (e.g., `TAGAssignments`)
  - Field added to a standard table: `TAG<FieldName>` (e.g., `TAGExternalId`)

---

## What to create, and how

**Safe to create or modify by hand-editing XML:**
1. **AxClass**: X++ inside XML CDATA
2. **AxEdt**
3. **AxEnum**
4. **AxTable**: new custom tables with fields, indexes, relations and methods
5. **AxTableExtension**: add fields and field groups
6. **AxMenuItemDisplay**: simple menu items

**Prefer the MCP's generators, or Visual Studio's designer:**
- **AxForm**: fragile in raw XML. Use `generate_object` with a form pattern (`object_patterns` lists them), or start from a standard form of the same pattern.
- **AxFormExtension**: only add simple controls by hand; find the parent control's exact name first (`get_object_info` on the form with `options.searchControl`).
- **AxReport / SSRS** artifacts.
- Complex security artifacts (use `security_info` to see what exists).

If you edit forms in XML: start minimal, build after each step, and validate.

---

## How to create new artifacts

**Every new artifact needs:**
- an XML file in the correct folder, with `<Name>` equal to the file name (XPP004);
- consistent naming (see above);
- **an entry in the `.rnrproj`**, under the correct `<Content Include="AxType\Name">` item (XPP012).

**Never modify:**
- any XML under a Microsoft package (XPP015);
- any base table, form or class XML that isn't in your package.

---

## X++ authoring rules

1. Use **CoC** where applicable: `[ExtensionOf(...)]` and `next` calls.
2. Avoid static global state.
3. **Don't name variables or parameters with X++ reserved words.** **Checked 2026-10-29** against the compiler's own list: `count`, `index`, `select`, `next`, `order`, `group`, `sum`, `avg`, `str`, `date`, `real` and others are reserved; `table`, `field`, `insert`, `update` and `delete` are **not** (the old rule listed them too). Use `recordCount`, `idx`, `nextValue`. The lint flags reserved words (XPP017).
4. For integration: data contracts (DTOs), service classes and explicit security checks.
5. Multi-company safe: respect `DataAreaId`, and use `changecompany()` when needed.
6. Never hardcode URLs, tenants or secrets.

---

## XML editing rules

1. Keep the XML valid: well-formed, correct encoding (XPP001).
2. Preserve the existing node order.
3. **Minimise diffs:** add only the nodes you need; don't reformat the file.
4. Put X++ source in CDATA blocks, written `<![CDATA[ ... ]]>` (XPP002).
5. **Property values: use what the property takes.** **Checked 2026-10-29:** the old rule said "lowercase true/false, never Yes/No". That holds for a few properties only. Across 143,603 standard files, 30 properties only ever take lowercase `true`/`false` (`IsExtensible`, `AllowBlank`, `Nullable`, `UserDefined`, `IsEncrypted`, …). 137 only ever take `Yes`/`No` (`AllowEdit`, `Mandatory`, `InsertIfEmpty`, `AutoDeclaration`, `AlternateKey`, `AllowDuplicates`, `NeedsRecord`, …). Copy the style of a standard object, or let the lint tell you (XPP006).
6. Standard XML omits properties that are at their default: `<AllowEdit>Yes</AllowEdit>` is never written, only `No`. Writing the default is harmless but noisy.

---

## Build and validate workflow

After editing:
1. **Build** the model (`xpp-build`). A build compiles whatever is in the model folder, other people's uncommitted work included.
2. If table fields or indexes changed: **synchronise the database** (`xpp-db-sync`).
3. Run a smoke test: a SysTest class (`xpp-run-tests`), or open the form (`xpp-ui-test`).
4. Commit only after the build succeeds with no metadata errors.

---

## Hard stops

Stop and ask if:
- you can't confirm the exact base table or form name (look it up with the MCP first);
- the target artifact is in a different model;
- the change involves a complex form layout;
- the base object is a view with unknown projection rules;
- a build or sync would compile someone else's uncommitted changes in the model.

---

## Artifact folders

| Artifact | Folder |
|----------|--------|
| Table extension | `AxTableExtension\` |
| Class | `AxClass\` |
| EDT | `AxEdt\` |
| Enum | `AxEnum\` |
| Form extension | `AxFormExtension\` |
| Table | `AxTable\` |
| Form | `AxForm\` |
| Menu item | `AxMenuItemDisplay\` |
| Label file | `AxLabelFile\` |

---

## Related references

- `xpp-classes.md`: event handlers, Chain of Command, prepopulation, select syntax
- `xpp-enums.md`: enum XML structure
- `xpp-forms.md`: form XML structure, patterns and controls
- `xpp-tables.md`: table relations, delete actions, RecId EDTs
- `xpp-templates.md`: XML templates (EDT, table, class, enum, form)
- `xpp-errors.md`: build errors and their fixes
- `asset-management.md`: Asset Management tables and joins
- `d365fo-mcp.md`: the MCP tools, and what was found when testing them on 10.0.46
