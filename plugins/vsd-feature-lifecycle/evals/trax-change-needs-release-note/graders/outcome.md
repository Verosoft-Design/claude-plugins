---
type: llm
---

PASS if the reply plans a release-notes entry at docs/release-notes/unreleased/VERO-9310.md in mobi, with front matter `product: trax`, `type: fix`, `issue: VERO-9310` and an audience, and a body of one to three plain sentences for a customer.
FAIL if it says Trax needs no entry, that Trax uses release-please or builds its changelog from commit messages, or if `product` is missing, names `mobi`, `tag` or `verovia`, or leaves out `trax`.
