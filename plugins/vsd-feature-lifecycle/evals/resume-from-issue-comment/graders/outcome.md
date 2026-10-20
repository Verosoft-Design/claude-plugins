---
type: llm
---

PASS if the reply treats G1 as passed (the reply is from @stephane.levert), keeps the size as Feature, and continues to step 2: it reads the code to settle what it can, then writes a spec file under docs/superpowers/specs/ in tag-bc with a decision list, ending at G2 Spec approval (or builds straight away if it turns out small with a settled scope); and the status moves to Step 2 Spec. Not being able to write files in this session, and asking for the repo or the issue body to do so, is fine.
FAIL if the reply restarts sizing, asks for G1 again, or skips the spec and goes to build. This session has no repo and no Linear tool: saying so, and that it can't open the files or post the comment here, is fine.
