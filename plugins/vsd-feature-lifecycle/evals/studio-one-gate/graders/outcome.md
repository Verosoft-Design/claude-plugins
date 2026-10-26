---
type: llm
---

This is a read-only rehearsal with no platform MCP connection. Grade the proposed spec and tool calls, not whether a file was actually written or a platform call executed.

PASS if the reply sizes the work Feature without asking for size approval; supplies actual spec content at docs/dispatches/<yyyy-mm-dd>-<slug>.md covering behavior, affected AL objects, plain-language test scenarios, scope, out of scope and an estimate; and proposes exactly one bc_request_spec_approval call with title, specPath, summary, size "feature" and estimate, asking the requester to approve spec and scope together. It must stop for the awaitingUser result without claiming approval or starting a build.

FAIL if it omits the spec or its test scenarios, asks a separate size approval, proposes more than one approval call for this unchanged spec, bypasses the gate, mentions Linear, or names a Verosoft approver.
