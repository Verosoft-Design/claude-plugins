---
name: al-snapshot-debug
description: Capture what actually happened in a failing Business Central session with Microsoft's Snapshot Debugging MCP server (ALTool launchsnapshotmcpproxy). Arms a snapshot, the user reproduces the problem, and the recording (AL errors with call stack and variables at snappoints) comes back for diagnosis. Use for bugs that only reproduce on a real environment, in a specific company or for a specific user, or when a test can't be written yet. BC 2026 release wave 2 (server 29), preview.
argument-hint: "[what fails, e.g. 'posting sales order 1001 errors']"
---

# Snapshot debugging a live BC session

Source: Microsoft Learn, *Snapshot debugging with an AI agent (MCP server)* and *ALTool: Snapshot debugging MCP proxy* (2026). Preview: needs a prerelease of runtime 18 and Business Central server version 29.

## 1. Preconditions (check, don't assume)

- Server version 29+ and the AL Development Tools that include `launchsnapshotmcpproxy` (`altool help` lists it).
- The **Business Central MCP server is enabled** for the environment (admin setting).
- The signed-in user has **D365 Snapshot Debug** and **D365 ATTACH DEBUG** (the agent path needs ATTACH DEBUG even for your own session).
- The code you want snappoints in is **deployed** to that environment, and local symbols match the server's. Otherwise lines won't line up.
- No profiler schedule is active on the same session (they can't run together).

If any is missing, say which and stop.

## 2. Register the MCP server (once per project)

Build the connection from `.claude/bc-server.json`. Credentials never go in args: cloud uses the cached `altool auth login` sign-in (or `BC_ACCESS_TOKEN`), on-prem uses `BC_SERVER_USERNAME`/`BC_SERVER_PASSWORD` from the environment. Show the command and ask before running it:

```sh
# cloud sandbox: sign in once, then register
altool auth login --environmenttype Sandbox --environmentname <env> --tenant <tenant>
claude mcp add --scope local bc-snapshot -- altool launchsnapshotmcpproxy \
  --environmenttype Sandbox --environmentname <env> --tenant <tenant>

# on-prem / container
claude mcp add --scope local bc-snapshot -- altool launchsnapshotmcpproxy \
  --environmenttype OnPrem --server <http://host> --serverinstance <BC> --port <7047> --authentication UserPassword
```

`--port` is the API/OData port (usually 7047), not the dev port (7049). The new server's tools appear after restarting Claude Code (or `/mcp`).

## 3. Arm, reproduce, collect

1. **Arm** with the initialize tool. AL runtime errors are always captured, so a minimal arm needs no snappoints. Add snappoints (`applicationObjectType`, `applicationObjectId` or `applicationObjectName`, `lineNumber`, counted from the start of the object) at lines you need variable values for: read the code first (`al-base-app-source`, `bc-explorer`) to pick them. Set the client type: `WebClient` (default), `WebServiceClient` (API/OData/S2S), `Background` (job queue), `ClientService`. Scope to a user security ID when someone else reproduces it.
2. Tell the user it's armed and exactly what to reproduce. An armed snapshot closes after **30 minutes** without a matching session; a started one must finish within **10 minutes**.
3. Poll with the status tool; when finished, call stop to collect the archive.
4. If the environment restarted, the recording is lost: arm again.

## 4. Use what came back

Read the error, the AL call stack and the variable values at snappoints. Turn them into a hypothesis that names an object, procedure and line, then confirm it with a failing test (`/al-run-tests`) before fixing. For step-through playback, the archive opens in the VS Code AL snapshot debugger.

The archive can contain customer data. Keep it out of git (`.snapshots/` in `.gitignore`), don't paste record contents into chat beyond what's needed, and delete it when done.
