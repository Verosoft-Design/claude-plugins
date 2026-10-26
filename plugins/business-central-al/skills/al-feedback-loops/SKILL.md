---
name: al-feedback-loops
description: How to build, test, reproduce, inspect data and check the UI in Business Central AL, ranked by speed. Use whenever a process skill (superpowers test-driven-development, systematic-debugging, verification-before-completion; mattpocock tdd, diagnosing-bugs) asks for a build command, a test run, a red-capable repro or verification evidence in an AL project, or before claiming AL work is done or fixed.
---

# AL feedback loops

## When `AL_BUILDER=1`

Use this branch instead of the server loops below:

- **Symbols:** use `al_downloadsymbols` with `globalSourcesOnly: true` for
  Microsoft and AppSource, then `bc_download_symbols({})` for the customer's other
  apps. Use local `al_symbolsearch` against the downloaded packages.
- **Compile:** use the local AL MCP `al_compile` (or `alc`) for the app and test
  app, writing `.output/app.app` and `.output/test.app`. Run CodeCop, PTECop and
  UICop and resolve new warnings. Use `al_getdiagnostics` for the findings.
- **Publish:** call `bc_publish({ which: 'both' })`; the broker checks the sandbox
  and publishes with `SchemaUpdateMode=synchronize`.
- **TDD red/green:** call `bc_run_tests_start({ codeunitFilter: '<id>' })`, then
  poll `bc_run_tests_status({ testRunId })` every **15 s**. Omit the filter for the
  full suite before delivery. For busy, terminal error and sign-in handling,
  follow `/al-run-tests`' AL Builder branch.
- **Build checks:** run
  `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/al-builder-check.py --project <dir> --json`
  for reserved object/field/enum IDs and TAG's partner procedure allowlist.
- **Evidence:** quote completed test totals and failures with their call stacks.
  Use self-contained fixtures in **AL Builder Tests**. Keep logic in codeunits;
  list page wiring as a sandbox click-through for the requester.

Never use `al runtests`, `al-test`, BcContainerHelper or AL-Go in this branch.
The AL MCP stays local: do not use cloud sign-in, environment queries or publish
there, and do not call BC directly. On `{ needsSignIn: true }`, tell the requester
to sign in again and stop. Never publish to production or use `forcesync`.

## Outside AL Builder

Generic process skills (superpowers, mattpocock-skills) tell you *when* to run a build, a failing test or a repro. This skill tells you *how* in Business Central. Pick the fastest loop that can actually go red on the thing you care about.

## The loops, fastest first

| Loop | Command | Proves | Needs |
| --- | --- | --- | --- |
| Convention check | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/al-lint.py <files>` (also runs automatically after each edit) | label suffixes, Comment, Locked, StrSubstNo | nothing |
| Live diagnostics | AL language server (plugin `.lsp.json`): errors appear after each edit; the LSP tool gives definition, references, call hierarchy | compiles, symbol resolves | `altool` + symbols in `.alpackages` |
| Compile | MCP `al_compile` then `al_getdiagnostics` (`severities: ["error"]`) | it compiles against the real symbols | AL MCP + symbols (`al_downloadsymbols`) |
| Analyzers | `al_compile` with `enableCodeAnalysis: true`, `codeAnalyzers: ["${CodeCop}","${UICop}", "${PerTenantExtensionCop}" or "${AppSourceCop}"]` | CodeCop/UICop/AppSourceCop rules | same |
| Symbol truth | `al_symbolsearch` (`source: "environment"` for what's installed on the tenant), or the `bc-explorer` agent | the field/procedure/event exists with that signature | AL MCP or base-app source |
| Impact | `/al-call-graph`: `al graph query --to "obj:...#Proc" --direction callers` | what a change reaches, incl. events/interfaces | AL tools 2026 wave 2 |
| Tests on a server | `/al-run-tests` (`al runtests`, JSON per method) | behaviour: posting, validation, events, permissions | BC server (`/bc-server-setup`) |
| UI on a server | `/al-ui-test` (page scripting replay, or Playwright MCP exploration) | pages, actions, field visibility, the user's click path | BC server with web client |
| Data check | BC API / OData `GET` with `curl` against the server (`$filter`, `$select`) | what actually got written | BC server, an API page or published web service |
| Live failure | `/al-snapshot-debug`: arm, user reproduces, get error + call stack + variables | what really happened in that environment | BC 29 (preview), Snapshot Debug + Attach Debug permissions |
| Live slowness | `/al-profile`: schedule, reproduce, get CPU profiles + SQL/HTTP timings | where the time goes | BC 29 (preview), profiler permissions |

Compile is not behaviour. A clean compile proves names and types; it says nothing about posting logic, event order, filters or permissions. AL bugs are mostly behaviour bugs.

## Mapping process steps to loops

- **TDD red/green**: the red step is a `[Test]` procedure run by `/al-run-tests` failing on the assertion you expect (not on a compile error or a missing handler). Write tests per `${CLAUDE_PLUGIN_ROOT}/reference/al-testing.md` and `/al-write-test`. Without a server, say "test written, compiles, not run" and stop claiming red/green.
- **Debugging / building a repro loop**: in order of preference (1) a failing `[Test]` that reproduces the user's symptom; (2) a page-scripting recording of the user's click path replayed with `/al-ui-test`; (3) an API `GET` that shows the wrong data; (4) a snapshot captured with `/al-snapshot-debug` while the user reproduces it; (5) telemetry the user captures. A repro that only runs in the user's head is not a loop: ask for access, a recording, or the exact steps and data.
- **Verification before completion**: evidence to quote is `al_getdiagnostics` with 0 errors, plus the `al runtests` summary (`data.passed`/`data.failed`) from `/al-run-tests`, plus the replay result for UI changes. If no server is configured, the honest status is "compiles cleanly; not run on Business Central".

## BC-specific traps that make loops lie

- **Test isolation**: test codeunits need `EventSubscriberInstance = Manual` and a `[TransactionModel]` that matches whether the code commits. `AutoRollback` + a `Commit()` in the code under test fails on the commit, not on your assertion.
- **Unhandled UI**: a `Message`/`Confirm`/page open without a handler fails the test with "Unhandled UI", which looks like red but is not your bug.
- **Performance claims**: "faster" needs a before/after measurement (`/al-profile`, or durations from `al runtests`), not a code reading.
- **Stale app on the server**: publish the new build (with the test app) before running tests. Check the app version in the run output.
- **Wrong company / data**: tests run in the test runner's company; demo data differs by country (`w1` vs `us`/`ca`). Create data with the Library codeunits, don't rely on CRONUS records.
- **Schema changes**: publishing with `ForceSync` or `Recreate` deletes data. Never pick them without the user saying so.
