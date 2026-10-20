---
type: llm
---

PASS if the reply builds the tab with the impeccable skill (saying it isn't installed in this session is fine), from the approved mockup and the app's `PRODUCT.md`/`DESIGN.md`; gives impeccable's finish review one pass at most, with the session itself applying or declining each fix; and has the session review the full diff itself. Walking the flow in the running app with screenshots is expected too, but don't fail a reply only for leaving it out. This session has no repo: saying so is fine.
FAIL if it doesn't use impeccable for the screen, runs the finish review again after the fixes, or hands the code review to another agent (`/code-review`, reviewer subagents, review rounds).
