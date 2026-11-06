---
name: xpp-db-sync
description: Synchronise the AxDB schema after X++ table, view or data entity changes on a Dynamics 365 F&O dev VM, as a partial sync of the changed tables (MCP build_d365fo_project dbSync, or d365fo.tools Invoke-D365DbSyncPartial / Invoke-D365DbSyncModule). Additive only; destructive changes need the user to name them.
argument-hint: "[table,...]"
---

# Database sync

**Status: verified: pending.** The commands come from the MCP's schema and `-OutputCommandOnly` on F&O 10.0.46 (2026-10-29); nothing was run. Report the first run's timings, and whether it needed admin rights or stopped services.

Sync makes AxDB match the compiled metadata. Run it after a **successful build** that changed tables, table extensions, views or data entities.

## Rules

- **Additive only.** Adding tables, fields and indexes is safe. Dropping a field, renaming one, shrinking a string or changing a type can destroy data: stop and ask, and name the field and the table, as for `ForceSync`/`Recreate` in AL. Never pick a destructive option on your own.
- **The same gate as `xpp-build`:** nobody else's uncommitted work in the model. One sync at a time per machine.
- **Partial over full.** A full sync of the database takes far longer and touches every module.
- **Never print the connection string.** `Invoke-D365DbSync*` builds `SyncEngine -connect="…;Password=…"` from the VM's config, and `-OutputCommandOnly` prints it, password included. Don't paste that output into chat, logs, issues or commits.

## Commands

**MCP, with the build** (preferred):

```json
build_d365fo_project { "modelName": "<Module>", "dbSync": ["TAGNewTable", "TAGChangedTable"] }
```

`dbSync: true` syncs the syncable objects of the project; an array syncs exactly those tables and views, which is much faster.

**d365fo.tools** (PowerShell on the VM):

```powershell
# exactly these tables (and table extensions), e.g. after adding fields
Invoke-D365DbSyncPartial -SyncList TAGNewTable,TAGChangedTable -SyncExtensionsList EntAssetObjectTable.TheAssetGuardian
# every table and table extension of one module
Invoke-D365DbSyncModule -Module <Module>
# underlying: <PLD>\bin\SyncEngine.exe -syncmode=partiallist -synclist=<tables> -tableextensionlist=<extensions> -metadatabinaries=<PLD> -connect=<from the VM config>
```

## Evidence

The sync's summary line and its duration. Then check one changed table read-only:

```powershell
& "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE" -E -S localhost -d AxDB -W -Q "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TAGNEWTABLE'"
```

(`sqlcmd` is not on PATH in an SSH session; the path above is where 10.0.46 has it. F&O table names in SQL are upper case.)
