---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---
Lifecycle mode: studio

Bug in the fictional Cedar Ridge BC online extension: an existing pure calculation codeunit's CalculateCartonCount(Quantity, UnitsPerCarton) truncates the division. For 11 units and 10 per carton it returns 1; the agreed result is 2. Zero quantity stays 0 and exact multiples are unchanged. Restore that agreed behavior without adding fields or changing posting.

Use the feature lifecycle. This is a read-only rehearsal of a whole successful dispatch: describe the concrete regression test and the sequence from the spec through delivery, including exact proposed platform calls as JSON with tool names. No platform MCP tools, AL source, compiler or BC sandbox are connected to this eval; do not fabricate execution or passing results.

For the rehearsal only, the spec approval returns { "approved": true, "dispatchId": "demo-dispatch" }, and the build claim returns { "claimed": true, "baseVersion": "1.0.0.0" }. Project context says the existing app/test IDs and blocks are in al-builder.json and there are two production targets, CA and US, with different BC versions. A filtered red test run would finish with the expected assertion failure; after the fix the full unfiltered suite would return status "done", failed 0, testRunId "demo-green-run" for the final candidate tree. Review findings are resolved. Show what you would do using these simulated responses, without executing anything.
