---
name: feature-lifecycle
description: "Start, size and run Verosoft dev work in Business Central (AL) and Mobi: a bug, a feature or a major change, from a Linear issue or a request. Decides the size, the steps, where the spec lives and when to stop for Stéphane Levert's approval. Use when picking up an issue, starting a fix or feature, or resuming one."
---

# Feature lifecycle

Every piece of Verosoft dev work (Business Central/AL in tag-bc or other AL repos, and the mobi monorepo) goes through the same lifecycle, scaled to its size. This skill sizes the work, runs the steps that size needs, and stops at the gates. The files next to this one hold the detail. Read each one only when you reach it.

## 1. Who's here and what's installed

- **Is the person an approver?** Only Stéphane Levert and Alexis Turgeon approve gates. Check the chat first ("I'm …"), then `git config user.name` or the `gh` login. If it's unclear, ask.
- **Companion plugins.** Steps call these skills when they're installed:
  - superpowers (brainstorming, writing-plans, test-driven-development, systematic-debugging, verification-before-completion);
  - mattpocock-skills (grilling);
  - business-central-al, in AL repos.

  If one is missing, name it with its install line and carry on with the step's plain instructions:
  - `claude plugin install superpowers@claude-plugins-official`
  - `claude plugin install mattpocock-skills@claude-plugins-official`
  - `claude plugin install business-central-al@verosoft-design --scope local`

## 2. Resume first

Look for a status block at the end of the spec, or in the issue's latest lifecycle comment:

```text
<!-- lifecycle-status -->
Size: <Bug|Feature|Major>
Step: <number> <name>
Waiting on: <gate or hand-off, with who> | nothing
```

- **If a status block exists, continue from it.** If its "Waiting on" gate now has an approval from Stéphane or Alexis (in the chat or on the issue), mark it passed and go to the next step. Don't restart intake, and don't ask again.
- **Keep the block current** at every step change. A bug keeps it in a Linear comment.

## 3. Intake and size

1. **Read the issue:** title, description, labels (`Bug`, `Feature`, `Improvement`), comments, and which repo.
2. **Too little to size?** If you can't tell what's wrong, where, or what's expected, don't size it and don't start. Say what's missing and ask, or propose marking the issue `needs-info`.
3. **Propose a size** with `sizes.md`.
   - A label is a hint, not the size: check the escalation list in `sizes.md`.
   - If you hit an item, say which one, and wait for G1.
   - Major work always waits for G1.
4. **Pick the spec's home:**
   - BC only: the BC repo.
   - Mobi only: mobi.
   - BC and Mobi together: mobi.

   Linear and the other repo only link to the spec, never copy it.

   The spec's path in that repo:
   - **Feature:** one file, `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
   - **Major:** a folder, `docs/superpowers/specs/YYYY-MM-DD-<topic>/`.
   - **Bug:** none. The Linear issue is the spec.
5. **Read the repo's rules:** `AGENTS.md` and `docs/agents/*`. Repo rules (commits, PRs to `main`, worktrees) come from there.

## 4. Steps by size

| Step | Bug | Feature | Major | Read |
| --- | --- | --- | --- | --- |
| 2 Spec and decisions | — | yes | yes | `steps/spec.md` |
| 3 Environment | — | — | yes, when BC is involved | `steps/environment.md` |
| 4 Design | — | if a Mobi screen is added or changed | if a Mobi screen is added or changed | `steps/design.md` |
| 5 Build | yes | yes | yes | `steps/build.md` |
| 6 Prove | yes | yes | yes | `steps/prove.md` |
| 7 Stakeholders | — | — | yes | `steps/stakeholders.md` |
| 8 Docs and release notes | yes | yes | yes | `steps/docs.md` |
| 9 Ship | yes | yes | yes | `steps/ship.md` |

- **A bug goes straight from intake to step 5.**
- **BC pages never get a design step,** because BC dictates its own UI.
- **The size can go up at any step, never down.** When it does, stop at G1.

## 5. Gates

Gates G1 to G6 and the two hand-offs ("needs a mockup", "needs a BC test run") are in `gates.md`. Read it the first time you reach a gate. In short:

- Only Stéphane or Alexis can pass a gate.
- Anyone else, or an agent, posts the lifecycle comment on the issue mentioning `@stephane.levert` and stops.
- Agents never merge.
