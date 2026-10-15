
# AL MCP Server — Tool Catalog and Usage Rules

Source: Microsoft Learn, *AI agent tools for AL development* and *AL MCP Server* (both updated 2026-10-02). Requires AL Language extension / AL Development Tools **17.0+**; `al_getnextobjectid` and environment symbol search need **18.0+**.

The plugin wires `altool launchmcpserver --transport stdio ${CLAUDE_PROJECT_DIR}` as the `al` MCP server (see the plugin's `.mcp.json`). It needs `altool` on PATH: from the VS Code AL Language extension, or (Microsoft's recommended install for headless use) the `Microsoft.Dynamics.BusinessCentral.Development.Tools` .NET tool, which provides `al` and needs an `altool` shim (`/al-setup`). Logs go to `~/.al-mcp/almcp.log`.

## Tool names in Claude Code

The plugin registers the server as `al`. Claude Code exposes its tools as `mcp__plugin_business-central-al_al__<tool>` (e.g. `mcp__plugin_business-central-al_al__al_build`). Below, tools are named by their short form (`al_build`); call the prefixed tool.

## Tool catalog

| Tool                        | What it does                                                                                          |
| --------------------------- | ----------------------------------------------------------------------------------------------------- |
| `al_build`                  | Compile the AL project and produce a `.app`.                                                          |
| `al_compile`                | Compile WITHOUT producing `.app`. Faster validation. MCP-only.                                        |
| `al_publish`                | Publish the extension to a cloud or on-prem BC environment.                                           |
| `al_downloadsymbols`        | Download dependent symbol packages from an environment or global sources.                             |
| `al_symbolsearch`           | Search symbols in the project + dependencies, or on the connected environment (`source`).             |
| `al_getdiagnostics`         | Retrieve filtered compilation diagnostics.                                                            |
| `al_getnextobjectid`        | Next free object ID(s) for an object type, within `app.json` `idRanges`. 18.0+.                       |
| `al_getpackagedependencies` | List `app.json` dependencies. MCP-only.                                                               |
| `al_addproject`             | Load another AL project into the server after startup. MCP-only.                                      |
| `al_auth_login`             | Interactive MSAL Entra ID sign-in. MCP-only.                                                          |
| `al_auth_logout`            | Clear cached Entra ID tokens. MCP-only.                                                               |

VS Code-only tools (`al_debug`, `al_setbreakpoint`, `al_snapshotdebugging`) are not in the MCP server. For debugging and profiling a live BC from Claude Code, ALTool has separate MCP proxies: see the `al-snapshot-debug` and `al-profile` skills.

## `al_symbolsearch`

Arguments go at the top level **or** under a `parameters` key; both are accepted (older servers required the wrapper, so prefer it). `query` is required (`"*"` matches all; partial names match). `filters` (all optional):

| Filter | Values |
| --- | --- |
| `kinds` | `"Table"`, `"Codeunit"`, `"Page"`, `"Report"`, `"Enum"`, `"Interface"`, ... |
| `objectName` | search members inside one object, e.g. `"Customer"` |
| `memberKinds` | `"Field"`, `"Method"`, `"Key"`, `"Action"`, `"Trigger"` |
| `namespace`, `access` (`"Public"`/`"Internal"`), `obsoleteState` (`"No"`/`"Pending"`/`"Removed"`) | narrowing; obsolete symbols are included unless filtered |
| `match` | `"name"` (default), `"doc"`, `"all"` |
| `scope` | `"project"`, `"dependencies"`, `"all"` (default) |
| `source` | `"workspace"` (default) or `"environment"`: what is actually installed on the connected BC (base app, system app, every installed extension/PTE). 18.0+. Needs `BC_SERVER_URL`/`BC_SERVER_INSTANCE` or the project's `launch.json`, and `al_auth_login` first for cloud. |
| `limit` | max 200; check `truncated` in the result |

Results carry `name`, `fullName`, `kind`, `containerName`, `signature` (methods), `docSummary`, `path`, and for environment hits `appId`/`appName`/`appPublisher`/`appVersion`.

Use it before writing code that references anything you did not just read:

```json
{ "parameters": { "query": "*", "filters": { "objectName": "Customer", "memberKinds": ["Field"] } } }
{ "parameters": { "query": "*", "filters": { "objectName": "Sales-Post", "memberKinds": ["Method"], "access": ["Public"] } } }
{ "parameters": { "query": "Loyalty Program", "filters": { "kinds": ["Table"], "source": "environment" } } }
```

An environment hit that is not yet a dependency: add its `appId`/`appName`/`appPublisher`/`appVersion` to `app.json` `dependencies`, then `al_downloadsymbols`, before referencing it.

## `al_getnextobjectid`

Call it right before creating any new object, instead of picking an ID by hand. Arguments at the top level: `objectType` (required: `Table`, `Page`, `Codeunit`, `Report`, `Query`, `XmlPort`, `Enum`, `EnumExtension`, `PageExtension`, `TableExtension`, `ReportExtension`, `PermissionSet`, `PermissionSetExtension`), `count` (1–50), optional `rangeStart`+`rangeEnd`, `projectPath` (required with several projects loaded).

```json
{ "objectType": "Table", "count": 3 }
```

It does not reserve IDs: save the new object before calling again, or ask for a larger `count`. It only scans the project's own source, not other extensions published to the same sandbox, so in a shared dev sandbox also check with `al_symbolsearch` (`source: "environment"`). `outOfRange: true` means the ranges in `app.json` are full: tell the user, don't pick an ID outside them.

## Other tools

Every other tool takes its arguments at the top level (example `al_build`):

```json
{
  "scope": "current",
  "onlyErrors": true,
  "enableCodeAnalysis": true,
  "codeAnalyzers": ["${CodeCop}", "${AppSourceCop}"]
}
```

## Code analyzer placeholders

Pass these literal placeholder strings (with the dollar-brace) when enabling analyzers via `al_build.codeAnalyzers` or `al_compile.codeAnalyzers`:

- `${CodeCop}`
- `${AppSourceCop}`
- `${PerTenantExtensionCop}`
- `${UICop}`

## Diagnostic codes and area filters

`al_getdiagnostics` returns diagnostics with stable `code` strings (e.g. `AL0118`, `AS0023`, `AA0074`). The `areas` filter accepts `"AL"`, `"AppSourceCop"`, `"CodeCop"`, `"PerTenantExtensionCop"`, `"UICop"`. The `severities` filter accepts `"error"`, `"warning"`, `"info"`, `"hint"`. Limit defaults to 200, max 500.

## Authentication

`al_auth_login` is MCP-only and uses browser-based MSAL for Entra ID. Tokens are cached. Required before `al_publish` or `al_downloadsymbols` against a cloud environment. NOT required when:

- `al_downloadsymbols` is called with `globalSourcesOnly: true` (pulls from MS NuGet feeds and AppSource — ideal for CI and offline).
- `al_publish` targets an on-prem server with Windows authentication.

Pass `noCache: true` on any tool to force a fresh sign-in. Call `al_auth_logout` to clear cached tokens.

## Canonical workflows (use these compositions)

### Validate-only (PR gate, fast)

```text
al_downloadsymbols  (globalSourcesOnly: true)
al_compile          (onlyErrors: true)
al_getdiagnostics   (severities: ["error"])
```

### Full build and deploy to sandbox

```text
al_auth_login       (tenant, environmentType: "Sandbox", environmentName)
al_downloadsymbols
al_build            (scope: "current")
al_publish          (environmentName, environmentType, tenant)
```

### AppSourceCop quality gate

```text
al_compile          (enableCodeAnalysis: true, codeAnalyzers: ["${AppSourceCop}"])
al_getdiagnostics   (areas: ["AppSourceCop"])
```

## `al_publish` schema-update modes

`schemaUpdateMode` accepts `"Synchronize"` (default), `"ForceSync"`, or `"Recreate"`. **Never default to `"Recreate"`** in compound commands — it drops data. Reserve it for explicit user-initiated resets.

## Project-path arguments

When the workspace contains multiple AL projects, pass `projectPath` (absolute path to the `app.json` folder) on `al_build`, `al_compile`, `al_publish`, `al_downloadsymbols`, `al_getdiagnostics`, and `al_getpackagedependencies`. Without it, the tools target "the first project in the workspace" which can be wrong.

## Connections, environment variables, headless use

Connected tools (`al_publish`, `al_downloadsymbols`, environment symbol search) read the target from the project's `launch.json`, or from `BC_SERVER_URL`, `BC_SERVER_INSTANCE`, `BC_SERVER_PORT`, `BC_SERVER_USERNAME`, `BC_SERVER_PASSWORD` (on-prem/container, `UserPassword` auth). The same variables drive `al runtests` and the debugging/profiling proxies, so `/bc-server-setup` standardises on them. Never put their values in files.

## Initial project load

The plugin's `.mcp.json` launches `altool launchmcpserver --transport stdio ${CLAUDE_PROJECT_DIR}`, so the project Claude Code was started in is loaded automatically. If a project-scoped tool returns an empty/no-project result (multi-app repo, `app.json` not at the root, or Claude Code started from a parent folder), call `al_addproject` with the absolute path to the folder containing the relevant `app.json` before anything else.

## Related plugin skills

- `/al-symbols` — wraps `al_downloadsymbols`
- `/al-symbol-search` — wraps `al_symbolsearch`
- `/al-compile` — wraps `al_compile` + `al_getdiagnostics`
- `/al-build` — wraps `al_build`
- `/al-publish-sandbox` — wraps `al_auth_login` + `al_publish`
- `/al-setup` — diagnose and install the `altool`/`al` prerequisite.

The `al-build-and-publish` skill composes the build/deploy skills into the canonical workflows above.
