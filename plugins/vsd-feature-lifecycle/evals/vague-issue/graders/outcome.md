---
type: llm
---

PASS if the reply does not size the issue or start work, and instead says what is missing (what is wrong, where, and the expected behavior) and asks for it, or proposes marking the issue needs-info.
FAIL if the reply starts investigating or changing code, or picks a size without saying it needs confirmation.
