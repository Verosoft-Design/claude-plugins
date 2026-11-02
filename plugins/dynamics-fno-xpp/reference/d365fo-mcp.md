# The d365fo MCP: tools and quirks

The plugin's `d365fo` MCP server is the community [d365fo-mcp-server](https://github.com/dynamics365ninja/d365fo-mcp-server) (MIT), the X++ counterpart of the AL MCP. Microsoft ships no X++ MCP server or language server for cloud-hosted dev VMs. The server indexes PackagesLocalDirectory (PLD) into SQLite for symbol search, reads metadata through a C# bridge on Microsoft's metadata API, writes objects through the same API, and wraps `xppc`, `xppbp`, `SyncEngine` and `SysTestConsole`.

It runs **on the F&O dev VM** (it needs PLD and the F&O DLLs). `fno-vm-setup` installs it. The plugin starts it with `scripts/mcp-launch.mjs d365fo`, from `D365FO_MCP_ENTRY` (a git checkout's `dist/index.js`) or a global `npm i -g d365fo-mcp`. It reads its config from `D365FO_CONFIG`.

Everything below was observed on **F&O 10.0.46 with d365fo-mcp-server 1.21.0, on 2026-10-29**, unless it says otherwise.

## Tools (20 in `MCP_SERVER_MODE=full`)

| Group | Tools | Writes? |
| --- | --- | --- |
| Find | `search` (single, batch, `scope: "extensions"`), `get_object_info`, `find_references`, `extension_info` (modes `coc`, `events`, `table-merge`, `points`, `strategy`), `security_info`, `labels` (`search`, `info`), `object_patterns`, `get_workspace_info` | no |
| Knowledge | `get_knowledge` (kinds `knowledge`, `error`, `op-spec`, `bp-moniker`), `validate_code`, `analyze_code`, `validate_object_naming`, `prepare` | no |
| Write | `d365fo_file` (create, modify, delete), `generate_object`, `labels` (`create`, `update`, `rename`) | **model XML, `.rnrproj`, label files** |
| Build and run | `build_d365fo_project` (optional `bpCheck`, `dbSync`, `restartAos`), `run_bp_check`, `run_systest_class`, `verify_d365fo_project`, `update_symbol_index` | **build output, database, AOS** (`run_bp_check`: see below) |

Typical answer times on the VM: 1.6–2.6 s for `search`, `get_object_info`, `extension_info`, `labels` and `get_knowledge` (about 1 s of that is the server starting in a test harness; a session reuses one server). `find_references` through the xref database took 13.9 s on its first call and 2–3 s after.

## Quirks found on 10.0.46

1. **Module name vs model name.** A package (module, e.g. `TheAssetGuardian`) holds a model whose name can differ (`The Asset Guardian`). `run_bp_check` passes one `modelName` as both `xppbp -module:` and `-model:`, and `build_d365fo_project` passes it as `xppc -modelmodule=`.
   - With the display name: xppbp says `ModuleNotFound`, and the tool reports "4 objects checked, 4 with findings" with no findings listed.
   - With the module name: xppbp says "Model 'TheAssetGuardian' in module 'TheAssetGuardian' does not exist", evaluates nothing, and **the tool reports "BP clean"**.

   For such a model, run xppbp directly (`scripts/xpp-bp-check.ps1`, verified), and give `build_d365fo_project` `modelName` = the **module** name (not yet verified). Models whose name equals their module name are not affected.
2. **`run_bp_check` can write build output.** Before xppbp it runs `labelc.exe`, which rewrites `<package>\Resources\<LabelFile>.dll` whenever a label source is newer than its DLL. That's harmless on your own machine, but it's a write into a model someone else may be building. `xppbp.exe` itself only reads: before/after snapshots of the model folder were identical across 4 runs.
3. **`run_systest_class` doesn't find the runner.** It looks for `Bin\SysTestConsole.exe` and `Bin\SysTestRunner.exe`; 10.0.46 ships `Bin\SysTestConsole.17.0.exe`. Call that directly (`xpp-run-tests`).
4. **`find_references` needs the cross-reference database.** On a cloud-hosted VM, set `"bridge": {"xrefDbName": "DYNAMICSXREFDB"}` in the server's config. Without it, answers are a name-based scan of X++ code only, labelled "heuristic". With it, you get exact totals from code plus metadata: 4,503 references to `EntAssetObjectTable`, against 15 from the scan. The xref database is as fresh as the last build: objects edited since then are missing or stale in it.
5. **`extension_info` (mode `coc`) mixes up same-named objects.** `EntAssetObjectTable` is a table and a form. The tool listed a form-button handler class among the table's CoC extensions. Read each hit's `[ExtensionOf(...)]` line.
6. **`get_object_info` with `include: "signature"` gives no file path.** For a citation, use `include: "xml"` (raw XML plus its path), or `search`/`find_references`, which print paths.
7. **Kernel classes aren't indexed.** `Query`, `DictTable`, `FormRun` and other kernel types have no AOT XML, so `get_object_info` says "not found". For their APIs, use `get_knowledge` and Microsoft Learn, and compile to confirm.
8. **Label search warns about referenced packages.** `labels search` marks labels from other packages "resolves only if your model references that package", even when the model does reference it. Check the Descriptor's `ModuleReferences`.
9. **`get_workspace_info` and `doctor` don't agree on where the model name comes from**: one says "D365FO_MODEL_NAME env var", the other `workspace.modelName`. Both gave the same name.

## Which tool for which question

| Question | Tool |
| --- | --- |
| Does table/field/method X exist, and what is its signature? | `get_object_info` (`options.method`, `include: "signature"` or `"source"`) |
| Where is X used (code and metadata)? | `find_references` (needs the xref DB) |
| What do other models add to table X? | `extension_info` mode `table-merge` |
| What already wraps or handles method X? | `extension_info` modes `coc` and `events` |
| Which mechanism should I use to extend X? | `extension_info` mode `strategy`, then `get_knowledge` |
| Is there a label for this text? | `labels` action `search` (pass several phrasings as an array) |
| What does compiler error Y mean? | `get_knowledge` kind `error` |
| Is BP moniker Z real, and how do I suppress it? | `get_knowledge` kind `bp-moniker` |
| Which form pattern, and which controls does it require? | `object_patterns`, `get_knowledge` topic "form patterns" |
| Create or modify an object | `get_knowledge` kind `op-spec` for the contract, then `d365fo_file`; it registers the object in the `.rnrproj` |
| An XML file changed outside the server (hand edit, git) | `update_symbol_index` with its path |

## d365fo.tools (PowerShell) equivalents

d365fo.tools 0.7.36 is on the VM. Its `-OutputCommandOnly` switch prints the underlying command without running it. **The sync cmdlets print the AxDB SQL password** in that output (`SyncEngine -connect=...`), so never paste or log it.

| Step | Cmdlet | Underlying command (TAG example) |
| --- | --- | --- |
| Build | `Invoke-D365ModuleBuild -Module <Module>` | `xppc.exe -metadata=<PLD> -modelmodule=<Module> -output=<PLD>\<Module>\bin -referencefolder=<PLD> -log=… -xmlLog=…`, then `labelc.exe -modelmodule=<Module> -output=<PLD>\<Module>\Resources` |
| Compile only | `Invoke-D365ModuleCompile -Module <Module>` (`-XRefGeneration` to refresh the xref DB) | `xppc.exe` as above |
| Best practice | `Invoke-D365BestPractice -Module <Module> -Model '<Model name>'`. **Never `-RunFixers`**: it rewrites objects | `xppbp.exe -metadata=<PLD> -all -module=<Module> -model=<Model name> -xmlLog=… -log=…` |
| Sync one module | `Invoke-D365DbSyncModule -Module <Module>` | `SyncEngine.exe -syncmode=partiallist -synclist=<the module's tables> -tableextensionlist=<its table extensions> -metadatabinaries=<PLD> -connect=…` |
| Sync named tables | `Invoke-D365DbSyncPartial -SyncList <Table>[,…] [-SyncExtensionsList …]` | `SyncEngine.exe -syncmode=partiallist -synclist=…` |
| Read compiler results | `Get-D365CompilerResult -Path <xppc xml log> -ErrorsOnly -OutputTotals` | n/a |

Microsoft binaries in `<PLD>\Bin` on 10.0.46: `xppc.exe`, `xppbp.exe`, `LabelC.exe`, `SyncEngine.exe`, `SysTestConsole.17.0.exe`, `xppcAgent.17.0.exe`, `xppfagen.exe`.
