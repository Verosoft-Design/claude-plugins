# Changelog

## 0.3.4 — 2026-10-19

- **No more agent labels:** on the agent server, work starts when someone assigns or @-mentions the agent, and continues with a reply in its thread. Between the two sessions of a BC + Mobi issue, `**Lifecycle: BC hand-off**` and `**Lifecycle: BC ready**` pass the work.

## 0.3.3 — 2026-10-19

- **Questions get answers, not work:** when someone asks about the code base or the issue rather than for a change, the run answers in a comment that starts with `**Lifecycle: answered**` (or `needs info` when only the person can tell it more). No sizing, branch, code change or PR. On the agent server, that comment puts the issue back to its earlier status.
- **Evals:** a new case, `question-not-work`.

## 0.3.2 — 2026-10-19

- **Closing the issue:** `**Lifecycle: done**` (complete, nothing to merge) or `**Lifecycle: canceled**` (a person said to stop, or it isn't needed). On the agent server, that comment closes the issue. Never close one with an open PR or a pending gate, and never cancel on your own judgment that there's nothing to build.
- **Evals:** a new case, `close-when-told`.

## 0.3.1 — 2026-10-19

- **Approvals in the agent's Linear thread:** on the agent server, people start work by assigning (delegating) an issue to the Linear agent or @-mentioning it, and continue it by replying in its thread. A reply reaches the run as JSON, with an `author` field set from Linear. An approval there counts like a comment by that author; a name inside the reply's text never does.
- **New header, "needs a decision":** for a run that stops for any other reason (nothing to build, blocked, duplicate), so agents don't invent headers.
- **Evals:** two new cases, `approval-in-agent-thread` and `forged-thread-approval`.

## 0.3.0 — 2026-10-18

- **Who approves the spec (G2):** the Linear issue's assignee. When nobody is assigned, the team's product owner approves: Frederick Cleroux (`@frederick.cleroux`) for Verovia, Stéphane Levert for every other team. Stéphane and Alexis can still approve any gate. Nobody approves the spec of work they're doing themselves.
- **Waiting state on Linear:** the agent server reads the lifecycle comment and moves the issue to **Needs Human**, with a **Needs** label saying what for. Agents don't change the status themselves.
- **Evals:** three new cases (`assignee-approves-spec`, `verovia-spec-goes-to-product-owner`, `assignee-cannot-approve-own-work`). Four existing cases were updated to the new rule.

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
