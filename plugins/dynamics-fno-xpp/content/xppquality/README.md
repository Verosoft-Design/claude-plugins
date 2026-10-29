# X++ review content (draft)

The F&O counterpart of the BCQuality content in `business-central-al`: knowledge articles grouped by review domain, which a future `xpp-review` super-skill and its domain leaves will read. **Status: draft structure and 8 seed articles. No review skill yet, nothing vendored from Microsoft yet.**

## Layout (BCQuality's, unchanged)

```text
content/xppquality/
  microsoft/knowledge/<domain>/   vendored or adapted from Microsoft sources (empty; see SOURCES.md)
  community/knowledge/<domain>/   platform facts verified on a real F&O, not specific to one model
  custom/knowledge/<domain>/      house rules of one product (the tag-* articles are TAG's)
  SOURCES.md                      exact upstream files, pinned commits, licences
```

## Article format

BCQuality's article format, with one change: `fno-version` instead of `bc-version`.

```yaml
---
fno-version: [all]          # or a range of F&O versions, e.g. ["10.0.46.."]
domain: extensibility       # one of the domains below
keywords: [chain-of-command, coc, extensionof]   # lowercase kebab-case
technologies: [xpp]
countries: [w1]
application-area: [all]
---
```

The body is a `# Title`, then `## Description`, `## Best Practice` and `## Anti Pattern`. It has no fenced code and stays under 100 lines.

To check an article, copy the tree and rename `fno-version` to `bc-version`, then run `business-central-al`'s `scripts/validate-bcquality-frontmatter.py --root <copy>` (rules R01–R29). The 8 seed articles pass with 0 errors and 0 warnings.

## Domains (first five)

| Domain | Covers | Seed articles |
| --- | --- | --- |
| extensibility | CoC, event handlers, delegates, extensions instead of overlayering, extension naming | `xpp-coc-wrapper-shape`, `xpp-extension-target-kind` |
| performance | select shape, set-based operations, caching, firstOnly, joins | `xpp-select-shape` |
| security | privileges, duties and roles for new menu items and entities; role and duty extensions | `xpp-menu-items-need-privileges` |
| data-modeling | tables, EDTs, relations, delete actions, indexes, replacement keys | `xpp-table-bp-basics`, `tag-recid-edt-for-foreign-keys` |
| ui | form patterns, control types, lookups, labels | `xpp-form-patterns-that-exist`, `tag-no-raw-recids-on-forms` |

Every seed article states a fact checked on F&O 10.0.46 on 2026-10-29 (xppbp output, a survey of standard XML, or the MCP's catalogue), or a TAG rule from its Cursor rules.

## Next steps

1. **Vendor the sources in `SOURCES.md`:** pin them in a `PINNED.json` and add a vendor script.
2. **Write articles from them:** about 5–10 per domain to start. Take AppChecker's 21 rules and the Customization Analysis Report's `BPCheck*` rules first.
3. **Add the `xpp-review` super-skill and five `xpp-review-<domain>` leaves.** Reuse BCQuality's contracts and findings JSON schema (`business-central-al/content/bcquality/schemas/`, `reference/bcquality-*-contract.md`) so reviews keep the same shape. Fold in xppbp output (`scripts/xpp-bp-check.ps1`) and the MCP's `get_knowledge` rulebook as evidence sources.
4. **An eval suite** on the model of `vsd-feature-lifecycle/evals`.
