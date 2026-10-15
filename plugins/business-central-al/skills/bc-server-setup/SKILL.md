---
name: bc-server-setup
description: Set up a Business Central server this project can publish to, run tests on and drive through the web client, and record it in .claude/bc-server.json. Choices are a local Docker container via BcContainerHelper (Windows), an online sandbox, or an existing on-prem/dev server.
disable-model-invocation: true
argument-hint: "[container|sandbox|existing]"
---

# Set up a BC server for this project

Without a running Business Central, Claude can compile AL but cannot see what it does. This skill gets a server in place and records how to reach it, so `/al-run-tests`, `/al-ui-test` and `al_publish` can use it.

Never write passwords, client secrets or tokens into any file. Record only the **names of environment variables** that hold them.

## 1. Pick the kind of server

Ask which one fits, unless `$ARGUMENTS` already says:

- **container**: local Docker container built with BcContainerHelper. Best loop (fast publish, full test toolkit, can reset). Needs Windows with Docker running Windows containers. Business Central does not run in Linux containers.
- **sandbox**: a Business Central online sandbox in your tenant (admin center, or `/al-create-online-dev-env` for AL-Go repos). Works from any OS for publishing (AL MCP `al_publish`) and UI testing. `al runtests` runs test codeunits against it from any OS on BC 2026 release wave 2 and later; older versions need BcContainerHelper on Windows.
- **existing**: a server the team already has (on-prem, a shared dev VM, a remote container). Ask for its web client URL and auth type.

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
