---
type: llm
---

PASS if all of these hold:
- the plan settles what the code can answer itself (for example by reading the asset page and the existing tabs) instead of asking the assignee;
- it makes its own mockup (static HTML in the app's style, screenshotted) before stopping;
- its one comment asks @nadia.roy, the assignee, to approve the spec and the mockup together, with any open questions numbered, each with a recommendation;
- it writes no screen code before that approval.
FAIL if it plans one stop for the spec and a later, separate stop for the design, asks Stéphane or Alexis instead of @nadia.roy, asks a person for the mockup, or starts the screen code.
