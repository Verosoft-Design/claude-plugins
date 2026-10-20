---
type: llm
---

PASS if the reply marks the PR ready, adds the `deploy-mobi` label to PR #1400 so Vercel deploys a preview, gives the person who merges the preview link (from the workflow's comment on the PR), and leaves the merge to a person: @nadia.roy as the assignee, or Stéphane, who as the team lead can merge too. Mentioning that the label is added again after pushing fixes is fine. This session has no repo and no GitHub or Linear tool: saying so, giving the commands or the comment text, and asking the person in the session before running these visible steps, are all fine: judge the plan, not whether it ran.
FAIL if it doesn't add the `deploy-mobi` label, or if the agent merges the PR itself.
