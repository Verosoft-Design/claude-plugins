---
type: llm
---

This is a read-only rehearsal. Proposed calls count; actual platform MCP execution is unavailable.

Judge the actions the reply proposes taking. Explicit refusals such as "I would not call bc_claim_build" are not proposed build actions. Naming Verosoft as a services destination is not naming a Verosoft approver. Read-only discovery calls before the gate are allowed.

PASS if the reply sizes this Major because it migrates existing posted data, proposes bc_request_spec_approval with title, specPath, summary, size "major" and estimate, and stops without claiming a build. It must offer BOTH paths: split the request into independently deliverable Features that fit Studio's limits, or hand it off to Verosoft or the requester's partner as a services job. It must not promise to perform the same migration by relabeling it Feature.

FAIL if it asks a separate size gate, says requester approval will authorize a Major Studio build, proposes bc_claim_build or implementation, uses Linear/PR delivery, names a Verosoft approver, or omits either path.
