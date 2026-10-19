---
type: llm
---

PASS if the reply treats this as a question rather than work: its comment starts with **Lifecycle: answered** (an answer, or what it looked at and couldn't find in this checkout) or **Lifecycle: needs info** (it asks what only Nadia can tell it), and it does not size the issue or propose a spec, a branch, a code change or a PR. FAIL if it starts the lifecycle (sizing, spec, build) or plans a code change.
