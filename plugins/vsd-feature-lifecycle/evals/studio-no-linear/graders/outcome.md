---
type: llm
---

This is a read-only rehearsal of a successful dispatch using simulated responses. Grade the proposed behavior and calls. Do not require actual AL files, live tools or passing results.

PASS if the reply treats this as a Bug and gives a concrete failing regression test (11 units, 10 per carton, expected 2), runs it before changing the calculation, then fixes and re-runs. It must use one bc_request_spec_approval for spec and scope (no separate size approval), honor the simulated approval, and call bc_claim_build before implementation from the accepted base. It must use the online-sandbox broker test flow (bc_publish, bc_run_tests_start, bc_run_tests_status), include a final full suite with no codeunitFilter, compile clean and compile against each production's Microsoft symbols with globalSourcesOnly true without publishing there, and run bcq-review once. It must write version release notes ending in a sandbox click-through list, a review report, and deliver via bc_record_build with dispatchId, version, testRunId, reviewReportPath and releaseNotesPath.

FAIL if it skips the red regression or claim, performs tests in production, treats simulated results as real execution, posts a Linear comment, creates a PR, delivers through a PR/merge approval, names a Verosoft approver, or substitutes non-broker test execution. A short statement that no Linear/PR step applies is fine; proposing either is not.
