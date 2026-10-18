# Changelog

## 0.2.0 — 2026-10-18

- **UI testing in the mobi monorepo apps** (Mobi, Hub, Trax, Verovia), in the Prove step:
  - The agent signs in to the running app with the development login (`bun run dev:login`, from mobi PR #1312) as a test member, on the Dev environment and the TA - TS company.
  - A bug with UI steps is reproduced before the fix and again after it.
  - A feature's UX flow is walked end to end.
  - Screenshots go to `docs/pr-assets/<PR number>/` and into the PR description.
- **New hand-off, "needs UI test access":** used when the development login isn't configured on the machine.
- **README:** a new "Agents, CI and cloud sessions" section. A repo's committed settings don't reach fresh agents, so it covers the bootstrap, seed and managed-settings routes.

## 0.1.0 — 2026-10-17

- First release: the `feature-lifecycle` entry skill (sizes, steps, gates, spec homes, status block), the `lifecycle-release` skill, templates for feature and major specs, the PR description and release-notes entries, and a review-site template with a Q&A bot.
