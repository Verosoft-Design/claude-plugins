---
type: llm
---

PASS if the reply plans a release-notes entry at docs/release-notes/unreleased/VERO-9311.md in mobi whose `product` names both `trax` and `verovia` (for example `product: trax, verovia`), with `type: feature`, `issue: VERO-9311` and an audience. A `title` that makes it a highlight is fine.
FAIL if it says the change needs no entry, that `packages/ai`, Trax or Verovia use release-please or build their changelog from commit messages, or if `product` leaves out `trax` or `verovia`, or names `mobi` or `tag`.
