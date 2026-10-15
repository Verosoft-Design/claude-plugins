---
name: al-base-app-source
description: Get Microsoft's Business Central base application source (Base Application, System Application, country layers) onto disk at the project's version so field names, procedures, event publishers and posting logic can be read and grepped instead of guessed. Use before subscribing to a base-app event, extending a base table or page, or reasoning about how posting or validation works.
argument-hint: "[country-major, e.g. ca-27]"
---

# Base application source for grep

Claude writes much better AL when it reads the real base-app code than when it recalls it. Symbols (`al_symbolsearch`) give signatures; source gives behaviour (what `OnBeforePostSalesDoc` actually passes, which `Validate` triggers fire, where `Commit` happens).

## Where the source comes from

`StefanMaron/MSDyn365BC.Code.History` on GitHub mirrors Microsoft's published BC source every month, one branch per localization and major version: `w1-27`, `us-27`, `ca-27`, `de-26`, and so on. It's a community mirror of Microsoft's code, so treat it as reference and check against symbols when it matters.

## 1. Pick the branch

- Major version: from `app.json` `platform` / `application` (e.g. `27.0.0.0` → `27`), or the AL-Go `artifact` setting.
- Country: AL-Go `country` setting, or ask. Use `w1` when the customer has no localization-specific behaviour, otherwise their country (Canadian customers: `ca`).
- `$ARGUMENTS` overrides both.

## 2. Fetch once per version (shallow, single branch)

```sh
DEST="$HOME/.cache/bc-base-app/<branch>"
[ -d "$DEST/.git" ] || git clone --depth 1 --single-branch --branch <branch> \
  https://github.com/StefanMaron/MSDyn365BC.Code.History.git "$DEST"
```

The repo is big (several GB across branches), but one shallow branch is far smaller. Tell the user before the first download. To refresh a month later: `git -C "$DEST" pull --depth 1`.

## 3. Use it

Grep, don't read whole folders:

```sh
# event publisher signature
grep -rn "procedure OnBeforePostSalesDoc" "$DEST" --include=*.al
# where a field is validated
grep -rln "field(\"Shipment Date\"" "$DEST/BaseApp" --include=*.Table.al
```

For anything larger than a couple of greps, hand it to the `bc-explorer` agent so the source dumps stay out of the main context.

Cite what you found as `path:line` from the cache when you explain a design choice ("subscribing to `OnAfterInitFromSalesHeader` in `SalesLine.Table.al:...` because ...").

## Alternative: symbols already in the project

`.alpackages/*.app` files hold the symbols the compiler uses. They give signatures but usually not code. `al_symbolsearch` over them is the fastest way to confirm a name exists at the exact version the project compiles against. When source and symbols disagree, symbols win: they are what the compiler sees.
