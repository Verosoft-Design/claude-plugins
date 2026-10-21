# vsd-feature-lifecycle

The Verosoft feature lifecycle for Business Central (AL) and Mobi work. Its one entry skill, `feature-lifecycle`, takes a Linear issue or a request through four stages:

1. **It sizes the work** as a bug, a feature or a major change.
2. **It runs the steps that size needs:**
   - spec and decisions;
   - environment;
   - Mobi design;
   - build;
   - prove;
   - stakeholders;
   - docs and release notes;
   - ship.
3. **It keeps one home for every spec:**
   - BC-only work goes in the BC repo.
   - Mobi-only work, or work touching both, goes in mobi.
4. **It stops at named gates** for approval, mostly the issue's assignee, and as rarely as it can: it settles what the code answers itself, and asks the rest in one round.

It works the same way for a person in Claude Code or Cursor and for an agent driven from Linear.

| Size | Spec | Design | Build | Prove | Docs |
| --- | --- | --- | --- | --- | --- |
| Bug | The Linear issue | — | One PR | A test that fails before the fix | Release-notes entry |
| Feature | One spec file with a decision list | Mockup if a Mobi screen changes | One PR per repo | Tests plus the agent's own code review | Entry, plus the manual page if users see it |
| Major | A spec folder with `decisions.md` and `decision-log.md` | Mockups on a review site with a Q&A bot | Integration branch, one large PR | Test campaigns, UI walkthroughs, real-data run, CI | Entry, plus a guide section with screenshots |

**Gates:**
- **G1 Size:** the assignee, only when the work is or becomes major
- **G2 Spec:** the assignee
- **G3 Design:** the assignee, with the spec when the mockup is ready
- **G4 Customer data:** Stéphane (Alexis on Verovia)
- **G5 Merge:** the assignee, never an agent
- **G6 Release:** Stéphane (Alexis on Verovia)

The issue's assignee owns the work's decisions, also on their own work. When nobody is assigned, the team lead approves: Frederick Cleroux (`@frederick.cleroux`) for Verovia, Stéphane Levert (`@stephane.levert`) for every other team. The team lead or Alexis (`@alexisturgeon`) can approve any gate, but G4 and G6 go to Stéphane on every team but Verovia, and to Alexis on Verovia; Alexis can approve them anywhere. Anyone else's session posts a comment on the Linear issue and waits. On the agent server, people assign (delegate) an issue to the Linear agent or @-mention it to start work, and reply in its thread to continue; an approval there counts by the reply's author.

`lifecycle-release` (`/vsd-feature-lifecycle:lifecycle-release <tag|mobi> <version>`) gathers the unreleased release-notes entries into a version's notes for Hub.

## Install

mobi and tag-bc declare the marketplace and the plugin in their committed `.claude/settings.json`. Claude Code offers both once you open and trust one of those repos in an interactive session. For another repo, run this inside it:

```sh
claude plugin marketplace add Verosoft-Design/claude-plugins
claude plugin install vsd-feature-lifecycle@verosoft-design --scope local
```

It adds about 200 tokens to a session. The steps, templates and scripts load only when they're used.

### Agents, CI and cloud sessions

A repo's committed settings don't reach a fresh agent. Claude Code applies a repository's marketplace only after the folder is trusted interactively: a `-p` run applies it only in an already-trusted folder, and a cloud session never does. Install the plugin in the environment instead, with one of these:

- **A bootstrap step** in the environment's setup, before the agent runs. It needs no login, because the marketplace is public:

  ```sh
  claude plugin marketplace add Verosoft-Design/claude-plugins
  claude plugin install vsd-feature-lifecycle@verosoft-design --scope user
  # in AL repos also: claude plugin install business-central-al@verosoft-design --scope user
  ```

  In a fresh config this installs and enables the plugin (`claude plugin list` shows `vsd-feature-lifecycle@verosoft-design 0.1.0 ✔ enabled`).
- **A seed directory** baked into a container image: install with `CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/claude-seed`, then run with `CLAUDE_CODE_PLUGIN_SEED_DIR=/opt/claude-seed`.
- **Server-managed settings** from the claude.ai admin console (Owner role): `extraKnownMarketplaces` plus `enabledPlugins` for the whole organization. This is the only route that reaches Anthropic-hosted cloud sessions.

To check that a headless run loaded it, run `claude -p ... --output-format stream-json --verbose`: the `init` event lists the loaded plugins.

### Companions (recommended, not required)

Each step calls these skills when they're installed, and carries on with plain instructions when they aren't:

```sh
claude plugin install superpowers@claude-plugins-official        # brainstorming, writing-plans, TDD, debugging, verification
claude plugin install mattpocock-skills@claude-plugins-official  # grilling, for major changes
claude plugin install business-central-al@verosoft-design --scope local   # in AL repos
```

### Codex

```sh
bash scripts/install-codex.sh   # copies the skills from the installed plugin into ~/.codex/skills
```

### Cursor

The Cursor marketplace (`Verosoft-Design/cursor-plugin-marketplace`) carries a mirror. It's synced from a tagged release of this plugin and never edited by hand.

## Customer names

Customer names never go into a repo, a PR or release notes. `skills/feature-lifecycle/scripts/check_customer_names.py` checks a branch against a list kept only on your machine: `VSD_CUSTOMER_NAMES`, or `~/.config/verosoft/customer-names.txt`, one name per line. Ask Alexis for the list.

## Develop

```sh
python3 -m unittest discover -s plugins/vsd-feature-lifecycle/tests
node --test plugins/vsd-feature-lifecycle/tests/review-site/*.test.mjs
claude plugin eval plugins/vsd-feature-lifecycle --trust-plugin --scaffold --judge-model sonnet --no-publish
```

`--scaffold` gives each case the git identity its person really has. `--judge-model sonnet` matters: the default small judge fails correct long answers about a third of the time.

Bump `version` in `.claude-plugin/plugin.json` for every release, because installs are pinned to it.
