---
name: fno-vm-setup
description: Prepare a Dynamics 365 F&O cloud-hosted dev VM (LCS, Windows Server) for coding agents. Installs Node, Python, d365fo.tools, the d365fo-mcp-server with its symbol index and cross-reference settings, the Playwright MCP, and SSH access, then records the VM in .claude/fno-vm.json. Every install step needs the owner's yes.
disable-model-invocation: true
argument-hint: "[check|install|record]"
---

# Set up an F&O dev VM for agents

X++ only compiles on a machine with PackagesLocalDirectory (PLD): there is no Linux compiler and no language server. Agents build, sync, test and drive the UI on the dev VM, and read and edit from anywhere.

**Every install, service or config change on the VM needs the owner's explicit yes, step by step.** Never restart the AOS, IIS, SQL or the VM, and never change Windows settings, without being asked. Record only **names** of secrets, never values.

What follows was done on a 10.0.46 cloud-hosted VM (Windows Server 2022, VS 2022 17.14) on 2026-10-29, with the results noted.

## 1. Check what's there

```powershell
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free   # C: is small on LCS VMs (~9 GB free): put tools on a data drive
Test-Path <drive>:\AosService\PackagesLocalDirectory\Bin\xppc.exe
Get-ChildItem <PLD>\Bin -Filter *.exe | Where-Object Name -match 'xpp|Sync|LabelC|SysTest'   # 10.0.46: SysTestConsole.17.0.exe
Get-Command node, python, py, git -ErrorAction SilentlyContinue
```

## 2. Install (on a data drive, e.g. `<drive>:\agent-tools`)

| Tool | How | Notes |
| --- | --- | --- |
| Node 24 LTS | zip to `agent-tools\nodejs`, on machine PATH | set `NPM_CONFIG_PREFIX` and `NPM_CONFIG_CACHE` on the data drive |
| Python 3 | `agent-tools\python313`, on PATH | the hooks find `py -3` or `python`; there is no `python3.exe` |
| d365fo.tools | `Install-Module d365fo.tools -Scope AllUsers` | 0.7.36 has build, sync and BP cmdlets; no SysTest cmdlet |
| d365fo-mcp-server | `npm i -g d365fo-mcp`, then `D365FO_MCP_YES=1 d365fo-mcp setup`, or a git checkout plus `npm ci`, `npm run build` | its C# bridge builds against the VM's F&O DLLs |
| Claude Code | `npm i -g @anthropic-ai/claude-code` | the native installer has an open startup-hang issue on Server 2022; sign in per Windows user |
| Playwright MCP | `npm i -g @playwright/mcp`, browsers with `PLAYWRIGHT_BROWSERS_PATH` on the data drive | see `xpp-ui-test` |
| OpenSSH Server | Windows capability, key-only, PowerShell default shell | not reachable from the internet; use a private network such as Tailscale |

Hold Codex back on the VM: its sandbox fails when started from an OpenSSH session.

## 3. Configure the MCP server

`config\d365fo-mcp.json` (set `D365FO_CONFIG` to it):

```json
{
  "environment": { "type": "traditional", "packagePath": "<PLD>", "customModels": ["<Model name>"] },
  "workspace": { "modelName": "<Model name>", "path": "<PLD>\\<Module>\\<Model name>" },
  "naming": { "prefix": "<PFX>" },
  "index": { "extractMode": "all", "includeLabels": true, "labelLanguages": ["en-US"] },
  "bridge": { "xrefDbName": "DYNAMICSXREFDB" }
}
```

- `bridge.xrefDbName` turns `find_references` from a name scan into exact code-plus-metadata results. Check the database exists first, read-only: `sqlcmd -E -S localhost -Q "SELECT name FROM sys.databases"`. `sqlcmd` lives under `C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn`.
- **Build the index in the background:** a scheduled task running the server's index build. On 10.0.46 (16 cores) it indexed 1,153,870 symbols and 1,055,152 labels in 42 minutes, including metadata extraction. Then run `d365fo-mcp doctor` (or `node dist\cli\index.js doctor` in a checkout), which should say "No blocking problems found".
- Known 1.21.0 quirks: module vs model name in `run_bp_check` and `build_d365fo_project`, `run_systest_class` not finding `SysTestConsole.17.0.exe`, and `run_bp_check` compiling labels. See `${CLAUDE_PLUGIN_ROOT}/reference/d365fo-mcp.md`.

**Register it for Claude Code on the VM** (per Windows user). The plugin's `.mcp.json` starts it through `mcp-launch.mjs`, which needs `D365FO_MCP_ENTRY` (a checkout's `dist\index.js`) or the global npm install, plus `D365FO_CONFIG`, as machine environment variables. Without the plugin, use flags rather than JSON (PowerShell 5.1 strips the quotes): `claude mcp add --scope user d365fo -e D365FO_CONFIG=<config> -e MCP_SERVER_MODE=full -- node <checkout>\dist\index.js`.

## 4. Remote access gotchas (PowerShell 5.1 over SSH)

- Native commands lose double quotes in their arguments. Write JSON arguments to files.
- `powershell -Command -` with the script on stdin **silently skips multi-line blocks** (`foreach { … }` across lines). Send scripts as `-EncodedCommand` (UTF-16LE, base64), or copy a `.ps1` over and use `-File`.
- `az vm run-command` blocks until every child process exits. Never start something that waits (`tailscale up` without `--timeout`).

## 5. Record

Write `.claude/fno-vm.json` in the repo, after showing it to the user:

```json
{
  "kind": "lcs-cloud-hosted",
  "version": "10.0.46",
  "url": "https://<environment URL as LCS shows it>/",
  "packagesRoot": "<drive>:\\AosService\\PackagesLocalDirectory",
  "module": "<Module>",
  "model": "<Model name>",
  "company": "usmf",
  "ssh": "<ssh config host alias>",
  "mcpConfig": "<path to d365fo-mcp.json on the VM>"
}
```

No passwords, keys or tokens. In a public repo, keep this file out of git; the URL and host alias identify the environment.
