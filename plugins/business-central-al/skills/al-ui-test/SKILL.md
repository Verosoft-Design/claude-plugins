---
name: al-ui-test
description: Check Business Central changes through the real web client. Replay page scripting recordings headlessly with Microsoft's bc-replay (Playwright), write new recordings for a page/action change, or explore the live UI with the Playwright MCP. Use after changing pages, page extensions, actions, field visibility or anything a user clicks through, and to reproduce bugs reported as click paths.
argument-hint: "[recording.yml | page or flow to check]"
---

# UI testing against the BC web client

Read `.claude/bc-server.json` for `webClientUrl`, `auth` and the credential variable names. No server configured means no UI check: say so and offer `/bc-server-setup`.

## Option A: page scripting replay (repeatable, CI-friendly)

Business Central's **Page Scripting** tool (web client, Settings > Page Scripting; BC 2024 release wave 2 and later) records a click path as a YAML file. Microsoft's `@microsoft/bc-replay` npm package replays recordings headlessly with Playwright and reports pass/fail, so recordings become regression tests.

Keep recordings in the repo, e.g. `test/recordings/<flow>.yml`.

Setup once (needs Node.js):

```sh
npm install @microsoft/bc-replay --save-dev
npx playwright install chromium
```

Run:

```sh
npx replay -Tests "test/recordings/*.yml" \
  -StartAddress "<webClientUrl>" \
  -Authentication UserPassword -UserNameKey BC_SERVER_USERNAME -PasswordKey BC_SERVER_PASSWORD \
  -ResultDir test/results
```

`-UserNameKey`/`-PasswordKey` take environment variable **names**. For a cloud sandbox use `-Authentication AAD`; if the test user has MFA, add `-MultiFactorType TOTP` (or `Certificate`) and `-MultiFactorSecretKey <ENV VAR NAME>` holding the TOTP secret (or base64 PFX). `-Headed` shows the browser; `-ResultDir` keeps traces. Options verified against `@microsoft/bc-replay` 0.1.139 (Apr 2026).

**Writing a recording.** Prefer having the user record the flow in the web client and save the YAML to the repo. Claude can then edit it (add a validation step, change a value, parameterise). Writing one from scratch is possible but fragile: copy the structure of an existing recording in the repo, keep page and control names exactly as the web client shows them, and replay it to prove it works before relying on it.

Report the replay summary and, for failures, the step that failed and the screenshot/trace path in the result dir.

## Option B: live exploration with the Playwright MCP

For one-off checks ("does the new action show on the Customer Card?", "reproduce what the user clicked"), drive the web client directly. If the Playwright MCP isn't connected, suggest the user add it:

```sh
claude mcp add playwright -- npx @playwright/mcp@latest
```

Then navigate to `<webClientUrl>?company=<company>&page=<page id>`, sign in with the test user from the environment, and use accessibility snapshots rather than screenshots to read page state. BC's web client is slow to settle: wait for the page's caption and the busy indicator to clear before acting. Turn anything worth keeping into a page scripting recording (Option A) so it can be rerun.

## What counts as evidence

A replay run that passed, or a described sequence of snapshots showing the expected state. "The page extension compiles" is not a UI check.
