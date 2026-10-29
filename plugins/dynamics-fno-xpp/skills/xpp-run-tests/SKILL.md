---
name: xpp-run-tests
description: Run X++ SysTest classes on the Dynamics 365 F&O dev VM with SysTestConsole and report pass/fail per test method. Use for the red and green steps of TDD, to reproduce a bug with a failing test, and as verification evidence before claiming X++ work is done. Needs a built model.
argument-hint: "[test class,...]"
---

# Run SysTest classes

**Status: verified: pending.** On F&O 10.0.46 the runner is `<PLD>\Bin\SysTestConsole.17.0.exe`. Its `/?` help was read on 2026-10-29; no test has been run. Report the first run's command, duration, admin needs and result format, and fix this skill.

Never report tests as passing without a run. No VM, a model that can't be built (someone else's uncommitted work), or no SysTest class means the status is "not run".

## 0. Before running

1. **Build first** (`xpp-build`), with `restartAos: true` if the test touches code the AOS has loaded. A test runs the compiled code, not the XML.
2. **A real test class:** it extends `SysTestCase` (see `xpp-write-test`). TAG had no SysTest class on 2026-10-29; `TAGEnumTest` is a plain job with a `main` method, not a test.

## 1. Run

The MCP's `run_systest_class` (1.21.0) looks only for `SysTestConsole.exe` and `SysTestRunner.exe`, so on 10.0.46 it reports "Neither … found". Call the console directly:

```powershell
$pld = 'J:\AosService\PackagesLocalDirectory'   # the VM's PLD
$out = "$env:TEMP\systest-TAGWidgetTest.xml"
& "$pld\Bin\SysTestConsole.17.0.exe" /test:TAGWidgetTest /xml:$out /unattended
```

- `/test:` takes one or more classes, comma-separated. There is no per-method filter; put a method you iterate on in its own small class while you work.
- `/unattended` skips the interactive prompt. The MCP's authors found it works although `/?` documents it only with `/devfabric`; confirm on the first run.
- Other switches from `/?`: `/granularity:UnitTest|ScenarioTest`, `/htmlsummary:<file>`, `/traceFile:<file>`, `/cit` (all check-in tests). The default mode runs tests against the local AOS database.

## 2. Report

Parse the `/xml:` file: per method, pass/fail and the failure message. Quote the totals plus each failure's method and message.

- **Red** must fail on your assertion: not on a missing class (not built), missing data, or a dialog (unhandled UI).
- **Green:** the same methods pass, and the class's other methods still pass.
- **Before done:** run every test class the model has, not just the new one, and compare with the result before your change.
