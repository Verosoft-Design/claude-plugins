#!/usr/bin/env python3
"""
Lightweight AL convention linter.

Two modes:
  - Hook mode (no args): reads a Claude Code PostToolUse payload on stdin.
    When the edited file is a .al file, lints it and returns findings to the
    agent as additional context so it can fix them in the same turn.
    Never blocks; emits nothing when the file is clean or not AL.
  - CLI mode: al-lint.py <file.al> [...] prints findings, exits 1 if any.

Checks only what the compiler does NOT catch without CodeCop enabled, and
only the label rules from reference/al-labels-and-locked.md, which are
mechanical enough to check with a regex scanner:

  AA0074   Label name must end in Err/Msg/Qst/Lbl/Tok/Txt
  LBL001   Label with %1/#1 placeholders needs Comment = '...'
  LBL002   Label containing a URL needs Locked = true
  LBL003   Tok label needs Locked = true
  LBL004   Error/Message/Confirm(StrSubstNo(...)) - pass params directly
  LBL005   Error/Message('literal' + ...) - use a Label

Set BC_AL_LINT=0 to disable the hook.
"""

import json
import os
import re
import sys
from pathlib import Path

SUFFIXES = ("Err", "Msg", "Qst", "Lbl", "Tok", "Txt")

LABEL_RE = re.compile(
    r"""(?P<name>[A-Za-z_][A-Za-z0-9_]*|"[^"]+")\s*:\s*Label\s+
        '(?P<text>(?:[^']|'')*)'
        (?P<props>[^;]*);""",
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)
STRSUBSTNO_RE = re.compile(r"\b(Error|Message|Confirm)\s*\(\s*StrSubstNo\s*\(", re.IGNORECASE)
CONCAT_RE = re.compile(r"\b(Error|Message)\s*\(\s*'(?:[^']|'')*'\s*\+", re.IGNORECASE)


def blank_comments(src: str) -> str:
    """Replace // and /* */ comments with spaces, leaving strings and line numbers intact."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "'":
            j = i + 1
            while j < n:
                if src[j] == "'":
                    if j + 1 < n and src[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            out.append(src[i : j + 1])
            i = j + 1
        elif src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def line_of(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def lint(path: Path) -> list[str]:
    try:
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return []
    src = blank_comments(raw)
    findings = []

    def add(pos: int, code: str, msg: str) -> None:
        findings.append(f"{path}:{line_of(src, pos)}: {code} {msg}")

    for m in LABEL_RE.finditer(src):
        name = m.group("name").strip('"')
        text, props = m.group("text"), m.group("props")
        locked = re.search(r"\bLocked\s*=\s*true\b", props, re.IGNORECASE)
        if not name.endswith(SUFFIXES):
            add(m.start(), "AA0074", f"label '{name}' must end in one of {'/'.join(SUFFIXES)}")
        if re.search(r"[%#]\d", text) and not re.search(r"\bComment\s*=", props, re.IGNORECASE):
            add(m.start(), "LBL001", f"label '{name}' has placeholders but no Comment = '%1 = ...'")
        if "://" in text and not locked:
            add(m.start(), "LBL002", f"label '{name}' contains a URL; add Locked = true")
        if name.endswith("Tok") and not locked:
            add(m.start(), "LBL003", f"token label '{name}' needs Locked = true")

    for m in STRSUBSTNO_RE.finditer(src):
        add(m.start(), "LBL004", f"{m.group(1)}(StrSubstNo(...)): pass the label and params to {m.group(1)} directly")
    for m in CONCAT_RE.finditer(src):
        add(m.start(), "LBL005", f"{m.group(1)}('literal' + ...): use a Label with placeholders")

    return findings


def hook() -> None:
    if os.environ.get("BC_AL_LINT") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not file_path.lower().endswith(".al"):
        return
    findings = lint(Path(file_path))
    if not findings:
        return
    context = (
        "AL convention check on the file you just edited "
        "(business-central-al plugin; see reference/al-labels-and-locked.md). "
        "Fix these unless the repository deliberately does otherwise:\n"
        + "\n".join(findings[:30])
        + (f"\n... and {len(findings) - 30} more" if len(findings) > 30 else "")
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }))


def main() -> int:
    if len(sys.argv) == 1:
        hook()
        return 0
    findings = [f for arg in sys.argv[1:] for f in lint(Path(arg))]
    print("\n".join(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
