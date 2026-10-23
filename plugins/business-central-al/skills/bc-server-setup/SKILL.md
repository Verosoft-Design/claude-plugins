---
name: bc-server-setup
description: Set up a Business Central server this project can publish to, run tests on and drive through the web client, and record it in .claude/bc-server.json. Choices are a local Docker container via BcContainerHelper (Windows), an online sandbox, or an existing on-prem/dev server, including the team's BC Docker Manager in Azure. It checks for Windows and Docker first and proposes the local container when it can run one.
disable-model-invocation: true
argument-hint: "[container|sandbox|existing]"
---

# Set up a BC server for this project

Without a running Business Central, Claude can compile AL but cannot see what it does. This skill gets a server in place and records how to reach it, so `/al-run-tests`, `/al-ui-test` and `al_publish` can use it.

Never write passwords, client secrets or tokens into any file. Record only the **names of environment variables** that hold them.

**On the Verosoft agent server (orca-agents-1), set nothing up.** Its agents already have a BC server: `al-test` publishes to a free tenant of `bc-agents-0` on AKS and runs the tests there, and `al-compile` builds (see `/al-run-tests`). Don't write `.claude/bc-server.json` there, and don't touch the other BC pods on AKS: they hold people's work and review sites.

## 1. Pick the kind of server

First check what this machine can run. These checks only read, so run them without asking:

- **OS:** in PowerShell, `$env:OS` prints `Windows_NT` on Windows. In Git Bash or another POSIX shell, `uname -s` prints a name starting with `MINGW` or `MSYS` on Windows, `Darwin` on macOS and `Linux` on Linux.
- **Docker:** `docker version --format '{{.Server.Os}}'` prints `windows` when Docker runs Windows containers and `linux` in Linux-container mode. An error means Docker isn't running; "not found" means it isn't installed.

Then recommend from what you found:

- **Windows, Docker on Windows containers:** recommend **container** first. It's the fastest publish and test loop, has the full test toolkit and can be reset. Still offer the others.
- **Windows, no Docker or Linux-container mode:** say so plainly. Offer to switch Docker Desktop to Windows containers (tray menu, "Switch to Windows containers"), or to install Docker Desktop (Windows containers need Windows Pro or Enterprise). Then offer **sandbox** and **existing**.
- **macOS or Linux:** Business Central can't run here, because it needs Windows containers. Recommend **sandbox**, **existing**, or a container from the team's **BC Docker Manager** in Azure (under **existing**).

Ask which one fits, unless `$ARGUMENTS` already says. The checks only order the choices; the person picks. Don't install, switch or start anything without their explicit yes.

- **container**: local Docker container built with BcContainerHelper. Best loop (fast publish, full test toolkit, can reset). Needs Windows with Docker running Windows containers. Business Central does not run in Linux containers.
- **sandbox**: a Business Central online sandbox in your tenant (admin center, or `/al-create-online-dev-env` for AL-Go repos). Works from any OS for publishing (AL MCP `al_publish`) and UI testing. `al runtests` runs test codeunits against it from any OS on BC 2026 release wave 2 and later; older versions need BcContainerHelper on Windows.
- **existing**: a server the team already has (on-prem, a shared dev VM, a remote container). Ask for its web client URL and auth type.
  - **BC Docker Manager (Azure):** the team's web app that creates BC containers on Azure Container Instances. Sign in with a Microsoft account; no Azure CLI needed. Reach a container it created like any remote container: its web client URL and auth type.

If Claude Code runs on Linux/macOS and the user wants the container route, the usual setup is a Windows dev box running the container, with Claude reaching it over SSH (`ssh <host> pwsh -Command ...`) for BcContainerHelper and over HTTP for the web client and APIs.

## 2. Create it

### container (on the Windows host, PowerShell as admin)

Show these commands, then let the user run them, or run them only after explicit confirmation:

```powershell
Install-Module BcContainerHelper -Force
$cred = Get-Credential   # the BC user for the container; not stored anywhere by this skill
$artifact = Get-BcArtifactUrl -type Sandbox -country us -select Latest   # match app.json "platform" and the customer's country
New-BcContainer -accept_eula -containerName bcdev -artifactUrl $artifact `
  -auth NavUserPassword -credential $cred -updateHosts -includeTestToolkit
```

Use `-includeTestToolkit` (or `-includeTestLibrariesOnly` for speed) so the Library codeunits and test runner exist. Pick `-country` and the version from the project's `app.json` `platform` and AL-Go settings, not "Latest", when the customer is on an older version.

### sandbox

Use the BC admin center, or for AL-Go repos `/al-create-online-dev-env`. Then sign in through the AL MCP (`al_auth_login`) when publishing.

## 3. Record it

Write `.claude/bc-server.json` in the repo (ask whether to commit it or add it to `.gitignore`; a personal container usually stays out of git):

```json
{
  "kind": "container",
  "name": "bcdev",
  "webClientUrl": "http://bcdev/BC/",
  "auth": "NavUserPassword",
  "host": "local",
  "company": "CRONUS USA, Inc."
}
```

For a sandbox: `"kind": "sandbox"`, `"tenant"`, `"environment"`, `"webClientUrl": "https://businesscentral.dynamics.com/<tenant>/<environment>"`, `"auth": "AAD"`. For a remote Windows host: `"host": "ssh:<user@host>"`.

Connection secrets live in environment variables, never in this file. Use Microsoft's standard names, which ALTool reads directly (`al runtests`, environment symbol search, the snapshot-debugging and profiling proxies):

| Variable | For |
| --- | --- |
| `BC_SERVER_URL`, `BC_SERVER_INSTANCE`, `BC_SERVER_PORT` | on-prem / container target (e.g. `http://bcdev`, `BC`, `7049`) |
| `BC_SERVER_USERNAME`, `BC_SERVER_PASSWORD` | `UserPassword` auth |
| `BC_ACCESS_TOKEN` | optional, cloud: a pre-acquired Entra token (`az account get-access-token --scope https://api.businesscentral.dynamics.com/.default --query accessToken -o tsv`; ~1 hour) |

For a cloud sandbox the simpler route is signing in once with `altool auth login --environmenttype Sandbox --environmentname <env> --tenant <tenant>`; the token is cached and refreshed. Tell the user to set the variables in the shell they start Claude Code from (or their secret manager), not in this repo.

Also make sure `.vscode/launch.json` has a matching configuration, so the AL MCP and VS Code publish to the same place.

## 4. Verify

- Web client answers: `curl -s -o /dev/null -w '%{http_code}' <webClientUrl>` (200 or a redirect to sign-in).
- Publish works: `al_build` then `al_publish` against the server.
- Test runner works: `/al-run-tests` on one test codeunit. `al runtests` needs the BC 2026 release wave 2 (v29) tooling and server; older servers use the BcContainerHelper fallback.

Report each check's actual result.
