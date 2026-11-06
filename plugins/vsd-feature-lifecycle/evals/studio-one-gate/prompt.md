---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---
Lifecycle mode: studio

Add Delivery Instructions to customers, copied to new sales orders and shown on the sales order. This is a Business Central online extension project for the fictional Cedar Ridge demo company. The project already has a sandbox, reserved app and test ID blocks, and no existing delivery-instructions field. Existing customers and orders need no backfill. BC's standard order creation has an event for copying the field, so no posting or other core process needs redesigning.

Use the feature lifecycle. This is a read-only rehearsal: show the spec text you would save, its path, the exact platform tool call you would make next, and where you would stop. No platform MCP tools are connected in this eval, so represent proposed calls as JSON with the tool name; do not claim they ran. Assume the approval tool would return { "awaitingUser": true, "dispatchId": "demo-dispatch" }. Do not implement the extension.
