---
name: xpp-ui-test
description: Check Dynamics 365 Finance and Operations changes in the real web client with the Playwright MCP. Open a form by menu item, read its grid and fields, check lookups show codes instead of RecIds, click actions and read the infolog. Use after changing forms, form extensions, menu items, lookups or anything a user clicks through, and to reproduce bugs reported as click paths.
argument-hint: "[menu item or form] [what to check]"
---

# UI checks in the F&O web client

**Status: verified: pending.** `@playwright/mcp` 0.0.83 and Chromium were installed on the 10.0.46 dev VM on 2026-10-29, but no form has been opened through it yet. Report what the first run needed (sign-in, flags, timings) and fix this skill.

Task Recorder stopped working on cloud-hosted environments in January 2026, and RSAT is unsupported after May 2027. Playwright is the route for both checks and repeatable click paths.

## Setup (once per machine)

- The plugin starts the Playwright MCP from a global `npm i -g @playwright/mcp` (`scripts/mcp-launch.mjs playwright`). Extra flags go in `FNO_PLAYWRIGHT_ARGS`:
  - `--user-data-dir <folder on a data drive>`: keeps the signed-in profile, so MFA happens once;
  - `--ignore-https-errors`: **only** while the environment's SSL certificate is expired. LCS renews it under environment > Maintain > Rotate secrets > SSL. Remove the flag after that.
- **URL:** use the environment URL exactly as LCS shows it. The sign-in reply URL is registered for that host only; another name for the same VM fails after the password with AADSTS50011.
- **First sign-in is a person's job:** Entra ID with MFA. Run the browser headed where someone can see it (an RDP session on the VM, or their own machine pointed at the URL), let them sign in, and keep the profile. Never type or store their password.
- `.claude/fno-vm.json` (written by `fno-vm-setup`) records the URL and default company. No secrets go there.

## A check

1. **Build first,** with the AOS restarted (`xpp-build`, `restartAos: true`). The browser runs whatever the AOS has loaded.
2. **Open the form through its menu item** (company in `cmp`):
   `https://<environment URL>/?cmp=usmf&mi=<DisplayMenuItemName>`
   F&O sends `mi=` to the form the menu item opens.
3. **Wait for the page** to settle (the shell loads, then the form). Take a `browser_snapshot` and read the accessibility tree rather than screenshots: grids, field labels and values, and buttons with their names.
4. **Check what the change promised.** For example:
   - the new field appears in the grid or field group with its label (not a label ID such as `@TAGLabels:Foo`, which means labels weren't compiled);
   - a RecId field shows a code with a lookup, not a number;
   - a button opens the right form for the selected record;
   - an enum dropdown lists named values, not blanks.
5. **Read the message bar and infolog** after each action; errors appear there, not as exceptions.
6. **Leave the data as you found it,** or use a test company. Don't post or delete in shared demo data unless the user asked.

## Evidence

The URL opened (menu item and company), what you checked, and what you saw: the field values from the snapshot, the error text if any. A screenshot is useful for a person, but the snapshot text is the evidence. For a repeatable check, write the steps as a short script (menu item, actions, expected values) in the repo, e.g. `Tests/ui/<flow>.md`, so the next run follows the same path.
