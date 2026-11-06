---
type: llm
---

The run was told not to post anything, so judge the comments it drafts. Placeholders for upload URLs and links are fine.

PASS if all of these hold:
- It drafts the G5 Merge comment (PR #1690, the test result, the screenshots, @alexisturgeon) and, as a separate top-level comment, a `## QA test card`.
- The card has Where (Verovia Studio), numbered Steps a person would follow in the live app (make a publish fail, then try to publish again without reloading), an Expected result that tells a pass from a fail (the Publish button is enabled again), and Needs (a test account that can publish, a throwaway interface).
- The card is written for someone using the app, not for a developer: no file paths, test names or code.
- It says the issue gets the `QA: agent` label.

FAIL if there is no QA test card, if the card is folded into the G5 comment instead of being its own top-level comment, or if its steps only describe running tests or reading code.
