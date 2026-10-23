---
name: al-run-tests
description: Publish the app and its test app to the configured Business Central server and run AL test codeunits with `al runtests`, returning pass/fail per test method as structured JSON. Use for the red and green steps of TDD, to reproduce a bug with a failing test, and as verification evidence before claiming AL work is done. Falls back to BcContainerHelper for older servers and to AL-Go CI when no server is reachable.
argument-hint: "[test codeunit id] [test method,...]"
---

# Run AL tests on a Business Central server

**On the Verosoft agent server (orca-agents-1), use `al-test` instead of the steps below.** From the repo root (the folder with `app.json`):

```sh
al-test --range 73332625              # your codeunit: red before the fix, green after
al-test --range '73332620..73332629'  # a range, or 73332625|73332630
al-test                               # every test codeunit of the app
```

- It builds the branch with the `TESTS` symbol and the Library Assert dependency added to a temporary copy, publishes it to a free tenant (a1..a3) of the agents' BC server, `bc-agents-0` on AKS, and runs the codeunits there.
- It prints PASS/FAIL per method with each failure's error and AL call stack, then totals. JSON and JUnit results go to `~/.cache/al-test/results/`.
- Exit codes: 0 all passed, 1 a test failed, 2 no tests matched, 3 runner or server error, 4 build or publish failed, 5 no tenant came free.
- `main` has failing tests of its own: compare a full run with its baseline in the server's shared memory before calling a failure yours.

Elsewhere, read `.claude/bc-server.json`. If it does not exist, say tests cannot be run from this session yet, offer `/bc-server-setup`, and (for AL-Go repos) offer the CI fallback below. Never report tests as passing without a run.

## 1. Build and publish both apps

1. `al_build` for the main app and the test app (pass `projectPath` for each when the repo has several).
2. Publish the main app, then the test app, with `al_publish` (call `al_auth_login` first for cloud). Use schema update mode `Synchronize`. If it fails on a destructive schema change, stop and ask; never switch to `ForceSync`/`Recreate` on your own.

## 2. Run with `al runtests` (preferred)

ALTool's `runtests` command (AL Development Tools for **BC 2026 release wave 2** and later; check `al help runtests`) runs test codeunits from the command line on any OS and prints one JSON document to stdout. It reads the connection from the project's `launch.json` (`--project`), from `BC_SERVER_URL` / `BC_SERVER_INSTANCE` / `BC_SERVER_PORT` / `BC_SERVER_USERNAME` / `BC_SERVER_PASSWORD` for on-prem and containers, or from `--environmentname` / `--environmenttype Sandbox` / `--tenant` for cloud (Entra sign-in; sign in once with `altool auth login`).

```sh
# one codeunit, narrowed to the methods you are working on (red/green)
al runtests 50200 --testmethods "PostOrderWithLoyaltyPoints" --project ./Test --company "CRONUS USA, Inc."

# the whole test app in one session (before claiming done)
al runtests --testgroups .claude/testgroups.json --project ./Test
```

`--testgroups` takes a JSON array, one entry per codeunit: `[{"codeunitId": 50200, "testMethods": ["A", "B"]}, {"codeunitId": 50201}]`. Generate it from the test app's `Subtype = Test` codeunits (grep their IDs) and keep it in `.claude/` so the full run is one command.

Use the binary the session-start context reports (`al`, or `altool` when only the VS Code extension is installed). Exit code is `0` only when no test failed.

## 3. Read the results

From the JSON: `data.passed`, `data.failed`, `data.skipped`, `data.total`, and per method `codeunitId`, `methodName`, `status`, `output` (the error text), `durationMs`. Report:

- `N passed, M failed, K skipped`, and which app versions were published.
- For each failure: codeunit, method, and `output`.
- Whether each failure is the expected red (your assertion) or noise. Noise looks like: `Unhandled UI` (missing handler), a commit inside `AutoRollback`, missing permissions, missing setup data, the test app not published. Fix noise before treating a test as red.

## Fallback: BcContainerHelper (servers older than 2026 wave 2)

On a Windows host with BcContainerHelper (prefix with `ssh <host> pwsh -Command` when `host` is `ssh:...`), build the credential from the environment, never from literals:

```powershell
$cred = New-Object PSCredential($env:BC_SERVER_USERNAME, (ConvertTo-SecureString $env:BC_SERVER_PASSWORD -AsPlainText -Force))
Run-TestsInBcContainer -containerName <name> -credential $cred -extensionId <test app id> `
  -testCodeunit <id, optional> -testFunction <method, optional> -detailed `
  -XUnitResultFileName "C:\ProgramData\BcContainerHelper\<name>-results.xml"
```

## Fallback: AL-Go CI (no reachable server)

AL-Go's CI/CD workflow builds a container on the GitHub runner and runs every test app. Ask before pushing, then:

```sh
gh run list --branch <branch> --workflow CICD.yaml --limit 1   # by file name: the display name starts with a space
gh run watch <run-id> --exit-status
gh run view <run-id> --log-failed
```

Test results are in the run's artifacts (`gh run download <run-id>`). Slower (minutes), but real evidence.

## Last resort: the user runs them

The web client's **AL Test Tool** page runs selected test codeunits. If that's the only route, ask the user to run it and paste the result; quote what they report rather than inferring.
