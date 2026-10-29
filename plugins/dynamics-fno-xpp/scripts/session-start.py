#!/usr/bin/env python3
"""
Claude Code SessionStart hook for Dynamics 365 Finance and Operations (X++) repos.

Silent outside F&O repos. Inside one (a package folder with Descriptor/*.xml holding an
AxModelInfo, within 3 levels of the project dir), it prints context to stdout, which
Claude Code adds to the session:
  - each model: name, module, layer, publisher, version, module references
  - the model folder and its object counts per Ax* folder
  - the object prefix (FNO_XPP_PREFIX, or inferred from object names)
  - .rnrproj projects and how many objects they register
  - whether this checkout is the live model inside PackagesLocalDirectory
  - whether this machine is an F&O dev VM (build, sync and tests possible) or not
  - a missing CLAUDE.md
  - the working rules that matter most for X++
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fno_model  # noqa: E402

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)


def describe(pkg: fno_model.Package, root: Path, prefix_override: str) -> list[str]:
    lines: list[str] = []
    rel = os.path.relpath(pkg.path, root)
    for m in pkg.models:
        lines.append(
            f"- {m.display_name} (model `{m.name}`, module `{m.module}`, layer {m.layer}, "
            f"publisher {m.publisher or '?'}, v{m.version}) at {rel}"
        )
        if m.references:
            lines.append(f"  module references: {', '.join(m.references)}")
        if m.folder:
            counts = fno_model.object_names(m.folder)
            top = ", ".join(f"{n} {c}" for n, c in counts.most_common(8))
            lines.append(f"  objects: {sum(counts.values())} in `{os.path.relpath(m.folder, root)}/` ({top})")
            if prefix_override:
                lines.append(f"  object prefix: {prefix_override} (FNO_XPP_PREFIX)")
            else:
                prefix, share = fno_model.infer_prefix(m.folder)
                if prefix:
                    lines.append(f"  object prefix: {prefix} (on {share:.0%} of the model's own object names)")
                else:
                    lines.append("  object prefix: none detected; ask before naming new objects")
        else:
            lines.append(f"  model folder `{m.name}/` not found next to Descriptor/")
    for proj in pkg.projects:
        model = fno_model.project_model(proj)
        lines.append(
            f"  VS project: {os.path.relpath(proj, root)} (model {model or '?'}, "
            f"{len(fno_model.project_entries(proj))} objects registered)"
        )
    return lines


def main() -> None:
    try:
        sys.stdin.read()
    except Exception:
        pass
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    packages = fno_model.find_packages(root)
    if not packages:
        return

    out = [
        "Dynamics 365 Finance and Operations X++ repo (dynamics-fno-xpp plugin).",
        f"Plugin root: {PLUGIN_ROOT}  (skills write it as ${{CLAUDE_PLUGIN_ROOT}})",
        "",
    ]
    if len(packages) > 12:
        out += [
            "This folder holds more than 12 packages: it looks like PackagesLocalDirectory itself.",
            "Open the session in your model's package folder (or the repo that holds it) instead, "
            "so the model, prefix and project are detected.",
        ]
        print("\n".join(out))
        return

    prefix_override = os.environ.get("FNO_XPP_PREFIX", "").strip()
    out.append("Models:")
    for pkg in packages:
        out += describe(pkg, root, prefix_override)

    pld = fno_model.find_pld(root)
    if pld:
        out.append(
            f"Live model: this checkout is inside {pld[0]} (package {pld[1]}). The next build or "
            "database sync on this machine compiles whatever is here, committed or not."
        )

    on_vm, pld_root = fno_model.is_windows_fno_vm()
    if on_vm:
        out.append(
            f"Machine: F&O dev VM ({pld_root}). Build, BP check, database sync and tests can run here; "
            "see the xpp-feedback-loops skill. Never build or sync while someone has uncommitted work "
            "in the model unless they said so."
        )
    else:
        out.append(
            "Machine: not an F&O dev VM. You can read and edit the XML, run the lint and use the MCP's "
            "read-only tools if it is reachable, but compile, sync and tests run only on the dev VM "
            "(fno-vm-setup skill). Say so instead of claiming a build passed."
        )

    if not (root / "CLAUDE.md").is_file() and not (root / ".claude" / "CLAUDE.md").is_file() \
            and not (root / "AGENTS.md").is_file():
        out.append("No CLAUDE.md or AGENTS.md here: suggest /fno-init once, so the model, prefix and layout are written down.")

    out += [
        "",
        "How to work in X++ here:",
        "- Never guess standard names. Tables, fields, methods, EDTs, enums, labels and form controls come from the "
        "d365fo MCP (search, get_object_info, find_references, extension_info, labels) or from PLD XML read by the "
        "fno-explorer agent. Invented field and method names are the most common X++ failure.",
        "- Extend, never overlayer: table/form/enum extensions, Chain of Command (`[ExtensionOf]` classes ending in "
        "`_Extension`), event handlers. Edit only this repo's model; never a Microsoft package.",
        "- Every new object needs its XML file in the right Ax* folder AND an entry in the .rnrproj. The "
        "xpp-xml-lint hook checks XML well-formedness, CDATA, property value styles, form control types, "
        "registration and the prefix after each edit.",
        "- Read the conventions before editing: the xpp-conventions skill loads on Ax* XML; folder-specific rules "
        "load with it for tables, forms, enums and classes.",
        "- Prefer the MCP's write tools (d365fo_file, generate_object, labels create) on the VM: they write through "
        "Microsoft's metadata API and register the object in the project. Hand-edited XML is the fallback.",
        "- Database sync only adds. Dropping, renaming or retyping a field that holds data needs the user to name it.",
        "- A clean BP check is not a build, and a build is not behaviour. Evidence before done: build output, "
        "SysTest results, a UI check (xpp-feedback-loops skill), or say plainly what was not run.",
        f"- Conventions and references: {os.path.join(PLUGIN_ROOT, 'reference', '*.md')}.",
    ]
    print("\n".join(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a context hook must never break the session
        print(f"dynamics-fno-xpp session-start: {exc}", file=sys.stderr)
    sys.exit(0)
