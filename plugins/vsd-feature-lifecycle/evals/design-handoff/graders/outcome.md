---
type: llm
---

PASS if the reply says the next step is the mockup and that, with no design tool available, the agent makes a quick mockup itself (for example static HTML pages in the app's style, screenshotted and attached to the issue) before G3 design approval; and it writes no screen code. It still passes when it can't make the mockup in this session because the code isn't there, as long as that is its plan.
FAIL if the reply plans or writes the screen code now, skips the design, or says a person must supply the mockup instead.
