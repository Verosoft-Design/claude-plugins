---
type: llm
---

PASS if the reply says the session runs `bcq-review` once (its checks may run as subagents), judges each finding itself (fixes it, or says in the PR why not), and doesn't run the review again after the fixes. Saying the session also reads the diff itself, or that the independent reviews come on the PR, is fine. This session has no repo: saying so is fine.
FAIL if it runs `bcq-review` again to check the fixes, plans review → fix → re-review rounds, or hands the findings to another agent to judge or fix.
