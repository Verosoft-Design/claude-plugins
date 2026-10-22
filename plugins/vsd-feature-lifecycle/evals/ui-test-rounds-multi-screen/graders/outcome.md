---
type: llm
---

PASS if the reply plans UI test rounds with tester subagents, because several screens and flows change. It splits the flows into lanes, for example by role or area (supervisor sign-off, technician checklist, list and filters, permissions or empty and error states). Each lane works on its own test data, and the testers share one running dev server rather than starting one each. The testers use the running app and report findings with screenshots, without reviewing or changing the code. The session itself triages the findings and fixes them. Re-testing is limited, to at most two rounds or only the fixed findings. It also keeps tests and the session's own code review.
FAIL if the reply has the agent walk all the flows alone with no tester subagents, gives the testers the code to review or fix, plans open-ended test-fix rounds between agents, or uses customer or live data.
