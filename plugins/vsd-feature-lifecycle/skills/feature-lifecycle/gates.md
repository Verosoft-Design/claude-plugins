# Gates and hand-offs

A gate is a point where the work stops and waits for a named person. It works the same way for a person at the keyboard and for an agent.

| Gate | When | Who approves | Bug | Feature | Major |
| --- | --- | --- | --- | --- | --- |
| G1 Size | The size goes up, or work starts as major | Stéphane or Alexis | only on escalation | only on escalation | yes |
| G2 Spec | The spec or its decisions are written | Stéphane or Alexis | — | yes | yes, each grilling round |
| G3 Design | A Mobi mockup is ready | Stéphane or Alexis (the team weighs in for major) | — | yes, if there's a Mobi screen | yes |
| G4 Customer data | Anything that reads a customer environment or uses customer data | Alexis | — | yes, if needed | yes, if needed |
| G5 Merge | The PR is ready | Stéphane or Alexis | yes | yes | yes |
| G6 Release | Shipping to customers | Alexis | yes | yes | yes |

## Who can approve

Only **Stéphane Levert** (Linear `@stephane.levert`), who is in charge of all dev work, or **Alexis Turgeon** (Linear `@alexisturgeon`). A teammate running the session can't approve a gate for their own work, however sure they are.

## How a gate waits

- **Stéphane or Alexis is in the session.** Ask in the chat and wait for a clear yes.
- **Anyone else is in the session, or an agent is running from Linear.**
  1. Write one comment on the issue, in the format below.
  2. Put the issue in the waiting state.
  3. End the run.

  The next run resumes from the approval comment. Never start the gated work in the meantime.
- **No Linear tool in this session:** write the comment text in the chat for the person to post, then stop.

The comment:

```text
**Lifecycle: <G2 Spec approval | … | needs a mockup | needs a BC test run>** (<ISSUE-ID>)
Ready: <what's ready, with links>
Needed: <the one approval or item>
@stephane.levert
```

Labels and statuses for the waiting state come with the Linear agent setup. Until then, use the triage labels in the repo's `docs/agents/triage-labels.md` if it exists (`needs-info`, `ready-for-human`), and otherwise just the comment.

## Hand-offs

Hand-offs wait the same way, but they aren't approvals. The work needs something only a person can supply:

- **Needs a mockup:** no design tool is reachable (Open Design or Claude Design).
- **Needs a BC test run:** there's no CI that runs AL tests and no reachable BC server.

The run resumes once the missing piece is on the issue.

## Never

- Agents never merge a PR. G5 is always a person.
- Never treat an approval from anyone other than Stéphane or Alexis as a gate passed.
- Never skip a gate because the work looks small. Size it again instead.
