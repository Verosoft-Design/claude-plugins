# Changelog

## 0.3.11 — 2026-10-19

- **An approver's own request counts:** when the person asking for the work can approve a gate and their request already decides it (the size they set, "implement it", "no design needed"), that gate is passed. The run doesn't stop to ask them again; it says which gates their request passed.
- **A small feature with a settled scope goes straight to the build:** one app, a few files, nothing on the escalation list, no open question, and a scope settled by the request, an approver or your own undisputed answer on the issue. No G2 stop: the decisions go in the PR description and G5 reviews it. A tweak to an existing screen needs no mockup.
- **Evals:** new cases, `approver-request-skips-gates` and `small-feature-settled-scope-builds`.

## 0.3.10 — 2026-10-19

- **A one-line status in Linear comments:** `**Status:** Feature · Step 9 Ship · Waiting on …`. Linear printed the `<!-- lifecycle-status -->` marker as text. Specs keep the block, and older comments' blocks are still read.
- **Reply where you were called:** when the agent server says a comment called you, every comment goes in that comment's thread.

## 0.3.9 — 2026-10-19

- **Screenshots on the Linear issue too:** upload them with the Linear MCP (`prepare_attachment_upload`, PUT, `create_attachment_from_upload`) and show them in the lifecycle comment, besides committing them for the PR. mobi is private, so GitHub's mobile app can't show images stored in the repo.

## 0.3.8 — 2026-10-19

- **The team lead approves:** Frederick Cleroux on Verovia (VERO), Stéphane Levert on every other team, with Alexis able to approve any gate (G4 and G6 stay his alone). Stéphane no longer approves Verovia work.
- **Ask once:** the G2 comment asks for every later approval you can foresee (a migration on the shared AI database, customer data, no mockup needed), and an answer then covers the later step. With Alexis's yes, apply such a migration yourself, in one transaction.
- **Short lifecycle comments:** one line each for Ready and Needed, links instead of explanations; don't quote the skill.
- **Ship** names the Verovia Review code and security reviews instead of the retired review bots.
- **Evals:** a new case, `verovia-merge-goes-to-frederick`.

## 0.3.7 — 2026-10-19

- **No design tool, no stall:** when neither Open Design nor Claude Design is reachable (a headless agent), make a quick mockup yourself: static HTML pages in the app's style, screenshotted and attached to the issue, then wait for G3 as usual. Ask a person for a mockup only when you can't render one.
- **The design waiver:** Stéphane or Alexis can say no mockup is needed, which approves G3. Build like the existing screens and put screenshots in the PR.
- **Evals:** `design-handoff` now expects your own mockup, and a new case, `design-waiver`.

## 0.3.6 — 2026-10-19

- **GitHub feedback never passes a gate:** it reaches the run with a `github:` author. Approvals come only from Linear.

## 0.3.5 — 2026-10-19

- **Feedback on your PR comes back to you on the agent server:** review comments from people and the review bots, and a failed CI run (one automatic fix). Address each point, push, reply on GitHub to each comment, and post the G5 Merge comment again.

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
