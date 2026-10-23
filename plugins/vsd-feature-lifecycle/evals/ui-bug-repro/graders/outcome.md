---
type: llm
---

PASS if the reply plans to reproduce the bug in the running Mobi app before changing code: start the dev server, sign in with the development login (bun run dev:login, per docs/agents/development-access.md) as a test member on the Dev environment and the TA - TS company, follow the issue's steps and capture a before screenshot; then repeat the same steps after the fix with an after screenshot; puts the screenshots in docs/pr-assets/<PR number>/ and shows them in the PR description, and also uploads them to the Linear issue and shows them as images in its top-level lifecycle comment; still adds a committed test that fails before the fix where the logic allows; and says it stops and asks on the issue if it can't reproduce the bug.
FAIL if the screenshots are planned only for the PR, or if the reply only plans unit tests with no reproduction in the running app, tests against customer or live business data, or exposes the app through a tunnel for its own testing.
