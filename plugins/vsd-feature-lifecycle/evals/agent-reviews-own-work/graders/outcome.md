---
type: llm
---

PASS if the reply says the session itself (the main agent) reviews the branch's full diff, including what both subagents wrote, against the spec and the repo's rules, in one pass: it fixes what it finds without reviewing the fixes again. Mentioning that the independent reviews come later on the PR (the Verovia Review reviews, the person who merges) is fine. So is one pass of impeccable's finish review of the card, with the session applying or declining its fixes itself.
FAIL if it hands the review to another agent: running `/code-review`, dispatching a reviewer subagent, having one subagent review the other's work, or planning review → fix → re-review rounds between agents.
