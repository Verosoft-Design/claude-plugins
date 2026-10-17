---
type: llm
---

PASS if the reply treats design approval as given and moves to step 5, Build (one branch and one PR); says it updates the status block to Step: 5 Build with nothing waiting; and names the proof bar (tests plus a code review) and the release-notes entry.
FAIL if the reply restarts at intake, asks for design approval again, or goes back to design.
