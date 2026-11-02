---
name: xpp-build
description: Build (compile) a Dynamics 365 F&O X++ model on the dev VM with xppc and labelc, through the d365fo MCP's build_d365fo_project or d365fo.tools Invoke-D365ModuleBuild, and read the result. Checks first that nobody else's uncommitted work is in the model. Use after editing X++ or metadata, before tests, and as verification evidence.
argument-hint: "[module name] [full]"
---

# Build an X++ model

**Status: verified: pending.** The commands were captured from the MCP's source and from `Invoke-D365ModuleBuild -OutputCommandOnly` on F&O 10.0.46 (2026-10-29), but not yet run. Report the first real run's timings and output, and fix this skill if they differ.

A build compiles the **whole model** (xppc reads every object in the package), then compiles its labels. It writes `<PLD>\<Module>\bin`, `XppMetadata`, `Resources` and the `BuildModelResult.*` files. On a dev VM where PackagesLocalDirectory *is* the checkout, that means the live environment.

## 0. Gate: whose changes are in the model?

```powershell
git -C <PLD>\<Module> --no-optional-locks status --porcelain
```

`--no-optional-locks` keeps git from rewriting `.git\index`. If anything is listed that this task didn't change, **stop and ask** the person who owns the VM. Their half-finished work would be compiled into the running environment. One build at a time per machine.

## 1. Build

**MCP (preferred on the VM):**

```json
build_d365fo_project { "modelName": "<Module>", "bpCheck": true }
```

- Pass the **module** name (the package folder, e.g. `TheAssetGuardian`), not the display name. The tool passes `modelName` to `xppc -modelmodule=`, and on TAG the configured name is `The Asset Guardian`.
- `fullBuild: true` fixes "not been successfully compiled since it was last changed" (stale symbols).
- The call blocks until done (default timeout 30 min); call it once, don't poll.
- Add `dbSync: ["Table1", "Table2"]` when tables changed (see `xpp-db-sync`), and `restartAos: true` before UI checks or tests that need the new code.

**d365fo.tools (PowerShell, run as admin on the VM):**

```powershell
Invoke-D365ModuleBuild -Module <Module>
# underlying, from -OutputCommandOnly on 10.0.46:
#   <PLD>\bin\xppc.exe -metadata=<PLD> -modelmodule=<Module> -output=<PLD>\<Module>\bin -referencefolder=<PLD> -log=<log> -xmlLog=<xml> -verbose
#   <PLD>\bin\labelc.exe -metadata=<PLD> -modelmodule=<Module> -output=<PLD>\<Module>\Resources -outlog=<log> -errlog=<err>
Get-D365CompilerResult -Path <the xppc .xml log> -ErrorsOnly -OutputTotals
```

The logs land under `C:\temp\d365fo.tools\Logs\ModuleCompile\<Module>\`. `Invoke-D365ModuleCompile -XRefGeneration` also refreshes the cross-reference database that `find_references` reads.

## 2. Read the result

- **Errors** block everything: fix each one, using `get_knowledge` (kind `error`) for the meaning. A cascade often starts at the first error; fix from the top.
- **"Qualifier 'X' not valid"** right after adding an enum: build once more (the enum compiles first).
- **Warnings and BP findings:** fix the ones on objects you touched; don't sweep the whole model.
- **Evidence to quote:** the error and warning totals, the build time, and the module name.

## 3. Then

- Tables changed: `xpp-db-sync`.
- Behaviour: `xpp-run-tests`. UI: `xpp-ui-test`.
- Build leftovers (`BuildModelResult.*`, `BuildProjectResult.*`, `CompileLabels.xml`, `*.xref`, `Resources\*.delete`) are not source: don't commit them.
