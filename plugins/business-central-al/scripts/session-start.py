#!/usr/bin/env python3
"""
Claude Code SessionStart hook.

Silent outside Business Central projects. Inside one (an app.json with an
idRanges/publisher shape within 3 levels of the project dir, or AL-Go
settings), prints context to stdout, which Claude Code adds to the session:
  - plugin root path (skills reference ${CLAUDE_PLUGIN_ROOT}/...)
  - each AL app: name, publisher, version, runtime, platform, ID ranges
  - AppSourceCop mandatory affixes, AL-Go type/country
  - AL MCP status, BC server config status, missing CLAUDE.md
  - the working rules that matter most for AL
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".alpackages", ".alcache", ".snapshots", "bin", "obj", ".output"}
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)


def read_json(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def find_apps(root: Path, max_depth: int = 3) -> list[Path]:
    apps = []
    stack = [(root, 0)]
    while stack and len(apps) < 20:
        d, depth = stack.pop()
        try:
            entries = list(d.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.name == "app.json" and e.is_file():
                data = read_json(e)
                if "publisher" in data and ("idRanges" in data or "idRange" in data or "runtime" in data):
                    apps.append(e)
            elif e.is_dir() and depth < max_depth and e.name not in SKIP_DIRS and not e.name.startswith("."):
                stack.append((e, depth + 1))
    return sorted(apps)


def describe_app(app_json: Path, root: Path) -> list[str]:
    a = read_json(app_json)
    ranges = a.get("idRanges") or ([a["idRange"]] if "idRange" in a else [])
    range_txt = ", ".join(f"{r.get('from')}-{r.get('to')}" for r in ranges if isinstance(r, dict)) or "none declared"
    deps = [d.get("name") for d in a.get("dependencies", []) if isinstance(d, dict)]
    lines = [
        f"- {a.get('name', '(unnamed)')} by {a.get('publisher', '?')} v{a.get('version', '?')} "
        f"(runtime {a.get('runtime', '?')}, platform {a.get('platform', '?')}, target {a.get('target', 'Cloud')}) "
        f"at {app_json.parent.relative_to(root) if app_json.parent != root else '.'}",
        f"  object ID ranges: {range_txt}",
    ]
    if deps:
        lines.append(f"  dependencies: {', '.join(deps[:8])}{' ...' if len(deps) > 8 else ''}")
    cop = read_json(app_json.parent / "AppSourceCop.json")
    if cop.get("mandatoryAffixes"):
        lines.append(f"  mandatory affixes (AppSourceCop): {', '.join(cop['mandatoryAffixes'])}")
    return lines


def altool_status() -> str:
    try:
        out = subprocess.run(
            [sys.executable, str(PLUGIN_ROOT / "scripts" / "check-altool.py")],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except Exception:
        out = "missing"
    if out.startswith("altool:"):
        return "ready (altool on PATH). Use al_compile / al_getdiagnostics / al_symbolsearch freely."
    if out.startswith("al:"):
        return "the NuGet `al` binary is on PATH but the MCP server runs `altool`. Run /al-setup to add a shim."
    return "NOT AVAILABLE (neither altool nor al on PATH), so you cannot compile. Tell the user, and suggest /al-setup."


def main() -> None:
    try:
        sys.stdin.read()
    except Exception:
        pass
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    if os.environ.get("AL_BUILDER") == "1":
        project = read_json(root / "al-builder.json")
        blocks = project.get("idBlocks", {})
        print("\n".join([
            "AL Builder Studio project (business-central-al plugin).",
            f"Plugin root: {PLUGIN_ROOT}",
            f"Project: {project.get('name', '(not configured)')}; affix: {project.get('affix', '?')}",
            f"Reserved app block: {blocks.get('app', '?')}; test block: {blocks.get('test', '?')}",
            "BC online sandbox only; tests run through bc_run_tests_start and bc_run_tests_status, in AL Builder Tests.",
            "Compile locally to .output/app.app and .output/test.app; publish through bc_publish (synchronize).",
            "Use al-write-test and business-central-al-tdd's Online sandbox rules; page wiring needs a requester click-through.",
            "Use al-feedback-loops for symbols and broker tests. On needsSignIn, ask the requester to sign in again and stop.",
            "Keep IDs in al-builder.json's blocks; check TAG procedure calls with scripts/al-builder-check.py.",
        ]))
        return
    apps = find_apps(root)
    algo_path = next((p for p in (root / ".AL-Go" / "settings.json", root / ".github" / "AL-Go-Settings.json") if p.is_file()), None)
    if not apps and not algo_path:
        return

    out = [
        "Business Central AL project (business-central-al plugin).",
        f"Plugin root: {PLUGIN_ROOT}  (skills write it as ${{CLAUDE_PLUGIN_ROOT}})",
        "",
        "AL apps:" if apps else "No app.json found yet.",
    ]
    for app in apps[:6]:
        out += describe_app(app, root)
    if len(apps) > 6:
        out.append(f"- ... and {len(apps) - 6} more")
    if algo_path:
        algo = read_json(algo_path)
        out.append(f"AL-Go repo: type={algo.get('type', '?')}, country={algo.get('country', '?')} ({algo_path.relative_to(root)})")

    out += ["", f"AL MCP: {altool_status()}"]

    server_cfg = root / ".claude" / "bc-server.json"
    if server_cfg.is_file():
        cfg = read_json(server_cfg)
        out.append(f"BC server: {cfg.get('kind', '?')} '{cfg.get('name', '?')}' configured in .claude/bc-server.json. "
                   "Use /al-run-tests and /al-ui-test to verify behaviour on it.")
    else:
        out.append("BC server: none configured, so tests cannot be run from this session. /bc-server-setup sets one up.")

    if not (root / "CLAUDE.md").is_file() and not (root / ".claude" / "CLAUDE.md").is_file():
        out.append("No CLAUDE.md in this repo: suggest /al-init once, so prefixes, ID ranges and folder layout are written down.")

    out += [
        "",
        "How to work in AL here:",
        "- Never guess base-app names. Field names, procedure signatures, event publishers and enum values must come from "
        "al_symbolsearch, the .alpackages symbols, or base-app source (bc-explorer agent, al-base-app-source skill). "
        "Invented field names and event signatures are the most common AL failure.",
        "- Follow the repo's existing conventions (prefix/affix, file naming, folder layout, ID range) over generic BCApps ones. "
        "Get new object IDs from al_getnextobjectid, never by guessing.",
        "- Locate before you fix: in Microsoft's BC-Bench, about half of failed AL bug fixes edited the wrong file or region. "
        "Trace the call path (al_symbolsearch, LSP, /al-call-graph, bc-explorer) and write a failing test before editing.",
        "- Writing an AL test: use the al-write-test skill (BC-Bench's ALTest prompt, the only measured test-generation lever). "
        "Reviewing AL: /bcq-review (the BCApps review instructions it uses add ~20 F1 points in BC-Bench's code-review benchmark).",
        "- Extend, don't modify: tableextension/pageextension, event subscribers, interfaces. No base-app copy-paste.",
        "- After editing .al files, compile (al_compile, then al_getdiagnostics severities=error) and fix errors before moving on. "
        "A PostToolUse hook also flags label convention issues.",
        "- Process skills come from superpowers / mattpocock-skills when installed (brainstorming, writing-plans, "
        "test-driven-development, systematic-debugging, verification-before-completion, diagnosing-bugs, grill-with-docs). "
        "When one of them needs a build, a test run, a repro or a UI check, the al-feedback-loops skill says how to do it in BC.",
        "- Real-environment loops: /al-run-tests (al runtests), /al-ui-test, /al-snapshot-debug (live failures), "
        "/al-profile (slowness), /al-call-graph (who calls what).",
        "- Never claim AL works from a clean compile alone. Run the tests on a BC server, or say plainly what was not verified.",
        f"- Conventions: the al-conventions skill and {PLUGIN_ROOT}/reference/*.md.",
    ]
    print("\n".join(out))


if __name__ == "__main__":
    main()
