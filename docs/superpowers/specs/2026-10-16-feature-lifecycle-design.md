# Feature lifecycle for Verosoft dev work

- **Date:** 2026-10-16
- **Status:** Draft, for Alexis's review
- **Owner:** Alexis Turgeon. **Approver for dev work:** Stéphane Levert (`@stephane.levert` in Linear). Alexis can also approve.
- **Lands in:** a new plugin, `vsd-feature-lifecycle`. The canonical copy lives in this repo (`Verosoft-Design/claude-plugins`). A mirror lives in `Verosoft-Design/cursor-plugin-marketplace`.

Items marked **(my call)** were decided while writing this document, not by Alexis. Everything else comes from Alexis, either in the 2026-10-16 conversation that produced this document or in the PM refactor session.

## Why

On 2026-10-15 and 16, Alexis ran the preventive maintenance (PM) refactor (Linear project "PM Refactor", P-TAG-6) through a full lifecycle with agents:

- a spec;
- grilling rounds recorded in a decision log;
- BC test servers;
- phased builds on one integration branch with one large PR (tag-bc #193);
- a Mobi design reviewed before any screen code, on a shareable site with a Q&A bot;
- test campaigns on real customer data (read-only, under agreement);
- a stakeholder loop in the PM Refactor Teams chat;
- a consultant guide published as a new Hub book (mobi #1297).

It worked, but every step was improvised. Some things went wrong:

- documents ended up in three copies (mobi, tag-bc `docs/pm-refactor/`, Linear documents), and the Linear copies fell behind within a day;
- customer names leaked into the decision log, code comments and release notes;
- each location was chosen on the spot.

PM was the largest kind of change possible: a full refactor of a core process with customer data conversion. Most work is much smaller. Bugs skip almost all of this, and a normal feature needs only a short spec and maybe a small design.

The process has to hold for two kinds of users:

- **People**, in Claude Code and in Cursor. The BC team is in Cursor today and moves to Claude Code soon, so both tools are needed.
- **Agents**, starting the week of 2026-10-19. Alexis will set up a Linear-driven agent process that hands bugs and small features to agents. That wiring is not part of this work, but these skills must already be followable by an agent with nobody watching.

## Goals

1. One entry point that sizes a piece of work (bug, feature, major) and runs the steps that size needs, in order.
2. The same skills work in Claude Code and in Cursor.
3. An agent can follow every step without a person. Where a person must decide, the skill says so and the agent stops.
4. Every artifact has exactly one home and a fixed format. Everything else links to it.
5. The lessons from PM are built into the steps, not left to memory: anonymised customers, one large PR for major work, design before Mobi screens.

## Non-goals

- The Linear trigger and agent runner. That's next week's work. This design only defines the gate semantics, so the Linear side is a thin adapter.
- Replacing existing skills. The lifecycle calls superpowers, mattpocock-skills and business-central-al; it doesn't copy them.
- Changing repo rules. Commit style, PRs to `main` and worktree rules stay in each repo's `AGENTS.md`, and the lifecycle points to them.
- A Mobi design system, or changes to how Hub renders docs.

## Anti-goals (a failure even if it works)

- A bug fix that drags a spec, a design or a grilling round behind it.
- A second copy of any spec or decision document.
- An agent guessing its way past a decision that belongs to a person.
- A plugin that adds a large always-on cost to every session in mobi or tag-bc.
- Customer names in a repo, a PR or release notes.

## The three sizes

| | Bug | Feature | Major change |
| --- | --- | --- | --- |
| **What it is** | Behavior that's wrong against what was already agreed | New or changed behavior inside an existing process | A core process redesigned, a data migration or a customer conversion, a new module |
| **Spec** | None. The Linear issue is the spec. | One spec file with a short numbered decision list inside it | A spec folder like PM's, with `decisions.md` and `decision-log.md` |
| **Decisions** | None | A short brainstorm; questions and answers go into the spec's decision list | Grilling rounds; every question and answer goes into `decision-log.md`, binding rules into `decisions.md` |
| **Design** | None | A quick mockup if it adds or changes a Mobi screen | Mobi mockups on a shareable review site with a Q&A bot |
| **Environment** | What the repo already has | What the repo already has | Dedicated BC test servers when BC is involved |
| **Build** | One PR | One PR (per repo) | One integration branch, phase branches merged into it, one large PR |
| **Prove** | A test that fails before the fix | Tests, plus a code review | Test campaigns, UI tests and walkthroughs, a real-data run, CI on the PR |
| **Docs** | A release-notes entry | A release-notes entry, plus the manual page if users see the change | A release-notes entry and a full guide section with screenshots |
| **Stakeholders** | No | No | The team reviews the design and the decision log |

### When the size goes up (my call)

The size can go up, never down. An agent applies this list mechanically. Hitting any item means it stops, says which item it hit, and waits for approval of the new size (gate G1).

- **Bug becomes a feature** when the fix needs any of these:
  - a new table, field, API page, API entity or enum value;
  - a change to what a screen shows or how it behaves, beyond restoring agreed behavior;
  - new user-facing text, other than fixing existing wording;
  - a new permission, or a change to a permission set;
  - a change in two repos.
- **Feature becomes a major change** when it needs any of these:
  - an upgrade codeunit that changes existing data, or any data migration;
  - a conversion customers have to run;
  - a change to a core process: PM scheduling, work order posting, inventory, purchasing, costing, or meter handling;
  - more than about two weeks of work, or more than one phase.

## Where everything lives

**The rule (Alexis):** a feature's spec and decisions live in the repo where its code lands:

- **BC only:** the BC repo.
- **Mobi only:** mobi.
- **BC and Mobi together:** mobi.

Linear issues, Linear documents and the other repo link to the spec and never copy it.

| Artifact | Bug | Feature | Major |
| --- | --- | --- | --- |
| Spec | The Linear issue | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>/` (folder) |
| Decisions | — | A `## Decisions` section in the spec | `decisions.md` (binding rules, which win over the rest of the spec) and `decision-log.md` (every question) |
| Plan | — | `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` (what superpowers writing-plans produces) | The same, one per phase if needed |
| Release-notes entry | `docs/release-notes/unreleased/<ISSUE-ID>.md` | the same | the same |
| User manual | — | A page in the right `wiki/` book | A section in the right `wiki/` book, with screenshots |

The `docs/superpowers/` paths are where superpowers already writes, and both mobi and tag-bc already use them.

**The major spec folder** follows PM's layout (`docs/superpowers/specs/2026-07-30-preventive-maintenance-redesign/` in mobi):

- `README.md` (scope, status, document index)
- `design.md`
- `data-model.md` (if there's data)
- `migration.md` (if there's a migration or conversion)
- `delivery-plan.md`
- `open-questions.md`
- `decisions.md`
- `decision-log.md`
- `team-faq.md` (answers to stakeholder questions, which also feed the Q&A bot)

The plugin ships one template per file.

**Decision log format,** taken from PM: rounds with a heading and a date, then a table with the columns `#`, `Question`, `Recommendation` and `Answer`. Each entry has a status of Decided, Pending or Info. A decision made during implementation and reported afterwards is marked "controller call". Question IDs are stable (Q1, Q2…), and a series letter is allowed for themed rounds (U, C, E…).

**Manual books.** Each book lives in mobi's `wiki/` folder and is synced into Hub (`bun run docs:sync` in `apps/hub`):

- `wiki/mobi`, the Mobi User Manual;
- `wiki/tag`, The Asset Guardian User Manual, for BC features;
- `wiki/verovia`, Verovia.

So a BC feature with user documentation has a second, docs-only PR in mobi.

## Release notes (Alexis: start now for BC, same process as Mobi)

- **During the work:** each PR adds one small file, `docs/release-notes/unreleased/<ISSUE-ID>.md`, in its repo (my call: one file per PR, so parallel agents never conflict on a shared file). It has this frontmatter:
  - `product`: `tag` | `mobi` | `trax` | `verovia` | `hub` | `iot`
  - `type`: `fix` | `feature` | `change`
  - `issue`: Linear ID
  - `audience`: `users` | `admins` | `consultants`

  The body is one to three plain sentences, written for a customer. It never names a customer.
- **At release:** a release skill gathers the unreleased files for one product and version. It drafts the version's notes and moves the files to `docs/release-notes/<version>/`.
  - Mobi's notes go in Hub's Documentation Management: the published document whose id is `MOBI_RELEASE_NOTES_DOCUMENT_ID`, which Mobi's version pop-up shows.
  - BC gets its own "TAG release notes" document in Hub, with one entry per version.
  - Until Hub has a write API, the skill produces the text and a person pastes it into Hub (my call).

## The steps

Each step lists what it does at each size and which existing skill it uses. "If present" means the entry skill checks whether that skill is installed. If it isn't, the step says what to install and carries on with the plain instructions, without failing.

1. **Intake and size.** Read the Linear issue: title, description, labels (`Bug` / `Feature` / `Improvement`) and comments.
   - Propose a size, using the escalation list.
   - Find the spec's home with the "where everything lives" rule.
   - Check the repo's `AGENTS.md` and `docs/agents/*` (mobi has issue-tracker and triage-labels files).
   - **Bug:** go straight to Build.
2. **Spec and decisions.**
   - **Feature:** a short brainstorm (superpowers `brainstorming` if present), written to the spec file with its decision list. Then gate G2.
   - **Major:** grilling rounds (mattpocock-skills `grilling` if present), each round appended to `decision-log.md` with the binding outcome copied into `decisions.md`. Then gate G2. The Linear project gets a link to the spec folder, never a copy.
   - Then a plan (superpowers `writing-plans` if present).
3. **Environment** (major, BC). Set up BC test servers before any code (business-central-al `bc-server-setup`). Anything that touches a customer environment is gate G4.
4. **Design** (feature or major, only when a Mobi screen is added or changed; never for BC pages, since BC dictates its own UI).
   - Make the mockup in Open Design (the `open-design` MCP server) or Claude Design, whichever is available. If neither is reachable, ask the person to make it or to unblock the tool. Never skip to screen code.
   - The spec records the design link and a numbered list of design decisions.
   - **Major:** also publish a shareable review site in the `verosoft-design` Vercel team, with a Q&A bot that answers from the spec folder, the guide and `team-faq.md`. PM's site, `mobi-pm-design-review`, is the reference.
   - Then gate G3.
5. **Build.**
   - **Bug and feature:** one branch and one PR per repo.
   - **Major:** one integration branch, phase branches merged into it, and one large draft PR that stays open for review, testing and comments until it's ready. There are no side hotfix PRs: every fix goes into the main PR (Alexis, PM).
   - Repo rules come from `AGENTS.md`.
   - In AL repos, the business-central-al skills apply (`al-conventions`, `business-central-al-tdd`, `al-build-and-publish`, `al-upgrade-review` for upgrade code).
6. **Prove.**
   - **Bug:** a test that fails before the fix and passes after (superpowers `test-driven-development` or business-central-al `business-central-al-tdd`). Systematic debugging for anything non-obvious.
   - **Feature:** tests for the new behavior, plus a code review: `bcq-review` in AL repos, `vsd-code-review` in Cursor, `/code-review` in Claude Code.
   - **Major:** the above, plus:
     - test campaigns per area;
     - TestPage tests for every new or changed BC page;
     - a browser walkthrough with screenshots (`al-ui-test` for BC, and a visual check for Mobi);
     - a read-only real-data run where an agreement exists (gate G4);
     - an upgrade test for BC;
     - CI on the PR.
   - **Every size:** before a PR is marked ready, check the diff, the PR description and the release-notes entry for customer names (see "Open for the builder").
   - Finish with superpowers `verification-before-completion` if present.
7. **Stakeholder loop** (major). The team reviews the design site and the decision log.
   - Each question gets an answer in `team-faq.md`, and in the decision log if it decides something.
   - Scope changes become logged decisions, or items in a later phase.
8. **Docs and release notes.**
   - Every PR carries its release-notes entry.
   - **Feature:** if users see the change, update the right manual page in the same change (a docs-only mobi PR for BC features).
   - **Major:** a guide section with real screenshots taken from the final build.
9. **Ship.** A person merges (gate G5); agents never merge. Merging to `main` isn't a release. The release itself (gate G6) runs the release-notes step and follows each product's own release process: AppSource for TAG, the Vercel promotion for Mobi and Hub.

### Gates

A gate is a point where the skill stops and waits for a named person. It works the same way for a person at the keyboard and for an agent.

| Gate | When | Who approves | Bug | Feature | Major |
| --- | --- | --- | --- | --- | --- |
| G1 Size | The size goes up, or work starts as major | Stéphane or Alexis | only on escalation | only on escalation | yes |
| G2 Spec | The spec or its decisions are written | Stéphane or Alexis | — | yes | yes, each grilling round |
| G3 Design | A Mobi mockup is ready | Stéphane or Alexis (the team weighs in for major) | — | yes, if there's a Mobi screen | yes |
| G4 Customer data | Anything that reads a customer environment or uses customer data | Alexis | — | yes, if needed | yes, if needed |
| G5 Merge | The PR is ready | Stéphane or Alexis | yes | yes | yes |
| G6 Release | Shipping to customers | Alexis | yes | yes | yes |

**How a gate waits:**

- **This week, a person is in the session.** The skill asks in the chat and waits.
- **From next week, an agent from Linear.** The skill writes one comment on the issue: the gate, what's ready, links, and the question. It mentions `@stephane.levert`, puts the issue in the waiting state, and ends the run. The next run resumes from the issue comments.

The labels and statuses for that waiting state are decided with the Linear setup next week. Mobi's `docs/agents/triage-labels.md` already defines `needs-info`, `ready-for-agent` and `ready-for-human`.

### Features that touch BC and Mobi

- The spec lives in mobi.
- The work is two sessions in two repos, because the business-central-al skills only load in AL repos.
- Order (my call, from PM): BC and its API first, then Mobi. Mobi detects whether the new API exists, so it works against older BC versions.
- There are two PRs, and each links the spec and the other PR.

## Packaging

- **Plugin:** `vsd-feature-lifecycle`, named like the team's other `vsd-*` plugins (my call). It's listed in both marketplaces.
- **Canonical copy:** `plugins/vsd-feature-lifecycle/` in this repo.
  - The Cursor repo gets a mirror. Both tools read the same `SKILL.md` frontmatter (`name`, `description`, `disable-model-invocation`), so the skill files are copied verbatim.
  - A script in the Cursor repo copies from a tagged commit of this repo, so the mirror never drifts by hand-editing (my call).
  - Cursor-only extras such as `rules/*.mdc` stay in the Cursor repo.
- **Skills** (my call; the builder can merge or split):
  - `feature-lifecycle`: the entry point. It sizes the work, picks the steps, runs the gates and tracks which step the work is on.
    - Only this skill is model-invocable, with a sharp description. The other skills are reached through it, or with `/name`.
    - Target always-on cost: under about 2k tokens for the whole plugin.
  - `lifecycle-spec`: writes the feature spec or the major folder from templates, and keeps the decision log.
  - `lifecycle-design`: the Mobi mockup, the design-decision list and, for major work, the review site with its Q&A bot.
  - `lifecycle-prove`: the test bar per size and per stack (AL and TypeScript), plus the customer-name check.
  - `lifecycle-docs`: the manual page and the release-notes entry.
  - `lifecycle-release`: gathers unreleased entries into a version's notes for Hub.
  - `templates/`: the feature spec, every file of the major folder, the PR description and the release-notes entry.
- **PR description template:**
  - What
  - Why
  - Size
  - Spec link
  - Linear issue
  - Decisions made in this PR, if any
  - Testing (what ran, with counts)
  - Release-notes entry
  - Screenshots for UI changes
- **Dependencies are soft.** The plugin doesn't declare them in `plugin.json`, for two reasons: Alexis runs mattpocock-skills from Matt's own marketplace rather than the official one, and Cursor has no dependency mechanism.
  - The entry skill checks for superpowers, mattpocock-skills and (in AL repos) business-central-al, and names whatever is missing.
  - The README recommends the official sources, as the BC plugin's README already does.
- **Install (my call):**
  - mobi and tag-bc each declare the marketplace and the plugin in a committed `.claude/settings.json` (`extraKnownMarketplaces` plus `enabledPlugins`). The `vsd-feature-lifecycle` entry lives there.
  - That way a Linear-driven agent in a fresh environment gets it with no machine setup, and teammates are offered it when they open the repo.
  - tag-bc also declares `business-central-al` there, for the same reason. Alexis currently has it installed locally in the AL repos; the committed setting adds to that.
  - Cursor installs come from the Cursor marketplace, as today.

## What exists to build on

- PM spec folder: `mobi/docs/superpowers/specs/2026-07-30-preventive-maintenance-redesign/`. It's the model for every major-change template, the decision log and the team FAQ.
- PM PRs:
  - tag-bc #193, the integration-branch PR and its description;
  - mobi #1297, the Hub book;
  - mobi #1295 and #1296.
- PM design review site: `https://mobi-pm-design-review.vercel.app`, with the bot at `/ask.html`.
  - **Its source exists only in the PM session's scratchpad:** `/private/tmp/claude-501/-Users-alexisturgeon-Source-mobi/5a471876-344d-4999-8eb3-ed9335f216ed/scratchpad/pm-design-site/`.
  - That folder is temporary. Before it's gone, the builder copies the generic parts (site shell, bot, the knowledge-build script) into the plugin as the review-site template.
- mobi `docs/agents/issue-tracker.md` and `triage-labels.md`: Linear teams per app, and triage labels.
- mobi `wiki/README.md`: the three books and how they're served.
- `apps/hub/src/lib/mobi-release-notes.ts`: how Mobi's version pop-up reads Hub's release-notes document.
- The PM memory notes about anonymised customers (Customer A, Customer B).

## Left to the builder

- Exact skill wording, how the steps are split across skill files, and the template contents (start from PM's files).
- How the entry skill records which step a piece of work is on (for example a short status block in the spec, or a Linear comment), as long as a fresh session or agent can resume from it.
- The review-site template's structure, and how the bot's knowledge list is built. PM's bot only loaded files named in a fixed list, which made it miss new answers. Build the list from the folder instead.
- The Cursor sync script.
- How the customer-name check gets its list of names without committing that list to any repo (for example a local, untracked file or an environment variable), and what it does when the list is missing.

## Open for the builder (to settle with Alexis if unclear)

- None yet. This section is filled in after the builder check.
