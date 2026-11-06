#!/usr/bin/env python3
"""
X++ metadata XML linter (dynamics-fno-xpp).

Hook mode (no arguments): reads a Claude Code PostToolUse payload on stdin. When the edited
file is AOT XML (<model>/Ax*/<Name>.xml), a Descriptor/*.xml or a .rnrproj, it lints the file
and returns findings to the agent as additional context, so they get fixed in the same turn.
It never blocks, and says nothing when the file is clean or not F&O metadata.

CLI mode: xpp-xml-lint.py <file> [...] prints findings and exits 1 if there are any.

The checks come from the error tables of the TAG Cursor rules (January 2026) and from a survey
of 143,603 standard XML files on F&O 10.0.46 (scripts/xpp_xml_facts.json). They catch what
breaks a build or the metadata reader before you ever reach Visual Studio:

  XPP001 error    XML is not well-formed
  XPP002 error    `<![CDATA` not followed by `[` ("Metadata element is not readable")
  XPP003 error    root element does not match the Ax* folder
  XPP004 error    <Name> differs from the file name
  XPP005 error    namespace the deserializer rejects (AxEdt: V6 namespace or no i:type;
                  AxForm/AxFormExtension: not the V6 namespace)
  XPP006 error    true/false on a Yes/No property or the reverse ("cannot be converted to Boolean")
  XPP007 error    form control i:type that no standard form uses (AxFormIntControl)
  XPP008 error    CommandButton command that doesn't exist (SaveAndClose, SystemDefinedCloseButton)
  XPP009 warning  form Pattern/PatternVersion that no standard 10.0.46 form uses
  XPP010 error    enum value written as <EnumValue>, or several values without <Value> (duplicate 0)
  XPP011 error    DeleteAction without <Table>; PrimaryIndex on an index that allows duplicates
  XPP012 warning  object not registered in the package's .rnrproj
  XPP013 warning  object or added field without the model prefix; extension not named <Base>.<Suffix>
  XPP014 error    [ExtensionOf] class whose name does not end in _Extension
  XPP015 error    file in a Microsoft package (never edit outside your own model)
  XPP016 warning  Chain of Command wrapper (calls `next`) with a default parameter value
  XPP017 error    X++ reserved word used as a variable or parameter name (count, index, next, order, ...)
  XPP018 warning  select statement with `order by` after `where`

FNO_XPP_LINT=0 disables the hook. FNO_XPP_PREFIX overrides the inferred object prefix.
"""

from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fno_model  # noqa: E402

FACTS = json.loads((Path(__file__).resolve().parent / "xpp_xml_facts.json").read_text(encoding="utf-8"))
TF_PROPS = set(FACTS["lowercaseBooleanProperties"])
YN_PROPS = set(FACTS["yesNoProperties"])
CONTROL_TYPES = set(FACTS["formControlTypes"])
PATTERNS = {k: set(v) for k, v in FACTS["formPatterns"].items()}
BAD_COMMANDS = set(FACTS["knownInvalid"]["commands"])
BAD_PATTERNS = set(FACTS["knownInvalid"]["formPatterns"])

XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
V6 = "Microsoft.Dynamics.AX.Metadata.V6"
# Reserved words that can't be identifiers, from the compiler (see xpp_xml_facts.json), minus the
# ones that legitimately follow a field name in a select (`order by Name desc;`) or are literals.
NOT_IDENTIFIER_CHECKED = {
    "asc", "desc", "reverse", "like", "is", "as", "join", "from", "where", "outer", "exists", "notexists",
    "by", "in", "mod", "div", "firstfast", "forupdate", "nofetch", "crosscompany", "validtimestate",
    "repeatableread", "pessimisticlock", "optimisticlock", "forceliterals", "forceplaceholders",
    "forcenestedloop", "forceselectorder", "generateonly", "having", "true", "false", "null", "new",
    "extends", "implements", "unchecked", "using", "namespace",
}
XPP_KEYWORDS = sorted(
    w for w in FACTS.get("xppReservedWords", ["count", "index", "select", "next", "order", "group", "sum"])
    if w not in NOT_IDENTIFIER_CHECKED and not w.startswith("firstonly")
)

CDATA_RE = re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL)
BAD_CDATA_RE = re.compile(r"<!\[CDATA(?!\[)")
PROP_RE = re.compile(r"<([A-Za-z][A-Za-z0-9]*)(?:\s+xmlns=\"[^\"]*\")?>(true|false|True|False|Yes|No)</\1>")
CONTROL_RE = re.compile(r'i:type="(AxForm[A-Za-z0-9]*Control)"')
COMMAND_RE = re.compile(r"<Command(?:\s+xmlns=\"[^\"]*\")?>([^<]+)</Command>")
PATTERN_RE = re.compile(
    r"<Pattern(?:\s+xmlns=\"[^\"]*\")?>([^<]+)</Pattern>"
    r"(?:\s*<PatternVersion(?:\s+xmlns=\"[^\"]*\")?>([^<]+)</PatternVersion>)?"
)
KEYWORD_VAR_RE = re.compile(
    r"\b(?:int|int64|real|str|boolean|date|utcdatetime|container|anytype|var|guid|[A-Z][A-Za-z0-9_]*)\s+"
    r"((?i:" + "|".join(XPP_KEYWORDS) + r"))\s*[;=,)]"
)
SELECT_RE = re.compile(r"\bselect\b(.*?)(?:;|\{)", re.DOTALL | re.IGNORECASE)
JOIN_SPLIT_RE = re.compile(r"\b(?:outer\s+|exists\s+|notexists\s+)?join\b", re.IGNORECASE)


def local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def namespace(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def child(el: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in el if local(c.tag) == name), None)


def descendants(el: ET.Element, name: str) -> list[ET.Element]:
    return [e for e in el.iter() if local(e.tag) == name]


def blank_cdata(raw: str) -> str:
    """Replace CDATA contents with spaces (newlines kept), so regexes see only metadata."""
    return CDATA_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), raw)


def blank_xpp_comments(src: str) -> str:
    """Blank // and /* */ comments in X++ source; keep strings and line numbers."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            j = i + 1
            while j < n and src[j] != c and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
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


def line_at(raw: str, pos: int) -> int:
    return raw.count("\n", 0, pos) + 1


def line_of(raw: str, needle: str, default: int = 1) -> int:
    pos = raw.find(needle)
    return line_at(raw, pos) if pos >= 0 else default


class Linter:
    def __init__(self, path: Path, project_dir: Path | None):
        self.path = path
        self.project_dir = project_dir
        self.findings: list[str] = []

    def add(self, line: int, code: str, severity: str, msg: str) -> None:
        self.findings.append(f"{self.path}:{line}: {code} {severity}: {msg}")

    def run(self) -> list[str]:
        try:
            raw = self.path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return []
        for m in BAD_CDATA_RE.finditer(raw):
            self.add(line_at(raw, m.start()), "XPP002", "error", "`<![CDATA` must be followed by `[`: write `<![CDATA[ ... ]]>`")
        try:
            root = ET.fromstring(raw.encode("utf-8"))
        except ET.ParseError as exc:
            line = getattr(exc, "position", (1, 0))[0]
            self.add(line, "XPP001", "error", f"XML is not well-formed: {exc}")
            return self.findings

        located = fno_model.locate_object(self.path)
        if self.path.suffix.lower() == ".rnrproj" or self.path.parent.name in ("Descriptor", "AxLabelFile") or not located:
            return self.findings
        model_folder, ax_type, name = located
        meta = blank_cdata(raw)

        microsoft = self.check_outside_model(model_folder)
        self.check_root(root, raw, ax_type, name)
        self.check_property_styles(meta)
        if ax_type in ("AxForm", "AxFormExtension"):
            self.check_form(meta)
        if ax_type == "AxEnum":
            self.check_enum(root, raw)
        if ax_type == "AxTable":
            self.check_table(root, raw)
        if ax_type == "AxClass":
            self.check_class(root, raw, name)
        self.check_xpp_sources(root, raw)
        if not microsoft:
            self.check_registration(model_folder, ax_type, name)
            self.check_prefix(root, raw, model_folder, ax_type, name)
        return self.findings

    # -- structure ---------------------------------------------------------------------------

    def check_root(self, root: ET.Element, raw: str, ax_type: str, name: str) -> None:
        root_name = local(root.tag)
        if root_name != ax_type:
            self.add(1, "XPP003", "error", f"root element <{root_name}> in folder {ax_type}: the file must be an <{ax_type}>")
            return
        name_el = child(root, "Name")
        # AOT names are case-insensitive: standard objects differ from their file name in case only.
        if name_el is None or (name_el.text or "").strip().lower() != name.lower():
            found = (name_el.text or "").strip() if name_el is not None else "(missing)"
            self.add(line_of(raw, "<Name>"), "XPP004", "error", f"<Name> is '{found}' but the file is {name}.xml; they must match")
        ns = namespace(root.tag)
        if ax_type == "AxEdt":
            if ns:
                self.add(1, "XPP005", "error", f"AxEdt must use xmlns=\"\" (not {ns}): 'Cannot be deserialized as AxEdt'")
            if XSI_TYPE not in root.attrib:
                self.add(1, "XPP005", "error", "AxEdt needs i:type on the root (AxEdtString, AxEdtInt64, AxEdtEnum, ...)")
        if ax_type in ("AxForm", "AxFormExtension") and ns != V6:
            self.add(1, "XPP005", "error", f"{ax_type} root needs xmlns=\"{V6}\" (inner elements use xmlns=\"\")")

    def check_property_styles(self, meta: str) -> None:
        for m in PROP_RE.finditer(meta):
            prop, value = m.group(1), m.group(2)
            if prop in TF_PROPS and value not in ("true", "false"):
                self.add(line_at(meta, m.start()), "XPP006", "error",
                         f"<{prop}> takes lowercase true/false, not {value} ('Content cannot be converted to Boolean')")
            elif prop in YN_PROPS and value not in ("Yes", "No"):
                self.add(line_at(meta, m.start()), "XPP006", "error", f"<{prop}> takes Yes/No, not {value}")

    def check_form(self, meta: str) -> None:
        for m in CONTROL_RE.finditer(meta):
            ctl = m.group(1)
            if ctl not in CONTROL_TYPES:
                hint = " (use AxFormIntegerControl)" if ctl == "AxFormIntControl" else ""
                self.add(line_at(meta, m.start()), "XPP007", "error", f"form control type {ctl} doesn't exist{hint}")
        for m in COMMAND_RE.finditer(meta):
            if m.group(1).strip() in BAD_COMMANDS:
                self.add(line_at(meta, m.start()), "XPP008", "error",
                         f"command {m.group(1)} doesn't exist; standard forms use CloseForm or Save, "
                         "or a Button with a clicked() method")
        for m in PATTERN_RE.finditer(meta):
            pattern, version = m.group(1).strip(), (m.group(2) or "").strip()
            line = line_at(meta, m.start())
            if pattern in BAD_PATTERNS or pattern not in PATTERNS:
                close = sorted(p for p in PATTERNS if p.lower().startswith(pattern.lower()[:6]))[:4]
                self.add(line, "XPP009", "error" if pattern in BAD_PATTERNS else "warning",
                         f"form pattern '{pattern}' is not used by any standard form"
                         + (f"; did you mean {', '.join(close)}?" if close else "")
                         + " Check it with the MCP's object_patterns, or drop Pattern/PatternVersion.")
            elif version and version not in PATTERNS[pattern]:
                self.add(line, "XPP009", "warning",
                         f"pattern {pattern} version '{version}' not seen in standard forms (they use "
                         f"{', '.join(sorted(PATTERNS[pattern]))})")

    def check_enum(self, root: ET.Element, raw: str) -> None:
        values = descendants(root, "AxEnumValue")
        if any(child(v, "EnumValue") is not None for v in values):
            self.add(line_of(raw, "<EnumValue>"), "XPP010", "error", "enum values use <Value>, not <EnumValue>")
        without = [v for v in values if child(v, "Value") is None]
        if len(without) > 1:
            names = ", ".join((child(v, "Name").text or "?") if child(v, "Name") is not None else "?" for v in without[:4])
            self.add(line_of(raw, "<EnumValues"), "XPP010", "error",
                     f"{len(without)} enum values have no <Value> ({names}); only the first may omit it "
                     "(it defaults to 0), otherwise 'Duplicate value 0'")

    def check_table(self, root: ET.Element, raw: str) -> None:
        for da in descendants(root, "AxTableDeleteAction"):
            if child(da, "Table") is None:
                nm = child(da, "Name")
                self.add(line_of(raw, "<AxTableDeleteAction"), "XPP011", "error",
                         f"DeleteAction '{(nm.text if nm is not None else '?')}' has no <Table>: 'Property cannot be empty'")
        primary = child(root, "PrimaryIndex")
        if primary is not None and (primary.text or "").strip():
            for idx in descendants(root, "AxTableIndex"):
                nm = child(idx, "Name")
                dup = child(idx, "AllowDuplicates")
                if nm is not None and (nm.text or "").strip() == primary.text.strip() and dup is not None and (dup.text or "").strip() == "Yes":
                    self.add(line_of(raw, "<PrimaryIndex>"), "XPP011", "error",
                             f"PrimaryIndex '{primary.text.strip()}' allows duplicates; make it unique (AlternateKey) "
                             "or use it as ClusteredIndex only")

    def check_class(self, root: ET.Element, raw: str, name: str) -> None:
        decl = descendants(root, "Declaration")
        text = blank_xpp_comments(decl[0].text or "") if decl else ""
        if re.search(r"\[\s*ExtensionOf\s*\(", text) and not name.endswith("_Extension"):
            self.add(line_of(raw, "ExtensionOf"), "XPP014", "error",
                     f"class {name} has [ExtensionOf] but its name doesn't end in _Extension "
                     "('Invalid extension class name')")
        if re.search(r"\[\s*ExtensionOf\s*\(", text):
            for method in descendants(root, "Method"):
                src = child(method, "Source")
                nm = child(method, "Name")
                body = blank_xpp_comments(src.text or "") if src is not None else ""
                mname = (nm.text or "").strip() if nm is not None else ""
                # Only wrappers (methods that call `next <name>(`) must drop defaults; a new method
                # added by the extension class may declare them.
                is_wrapper = bool(mname) and re.search(r"\bnext\s+" + re.escape(mname) + r"\s*\(", body)
                signature = body.split("{", 1)[0]
                if is_wrapper and re.search(r"\([^)]*=", signature):
                    self.add(line_of(raw, f"<Name>{mname}</Name>"), "XPP016", "warning",
                             f"wrapper {mname}() has a default parameter value; Chain of Command wrappers "
                             "repeat the parameters without defaults")

    def check_xpp_sources(self, root: ET.Element, raw: str) -> None:
        for el in root.iter():
            if local(el.tag) not in ("Source", "Declaration") or not el.text:
                continue
            src = blank_xpp_comments(el.text)
            start = raw.find(el.text[:60]) if el.text.strip() else -1
            base = line_at(raw, start) if start >= 0 else 1
            for m in KEYWORD_VAR_RE.finditer(src):
                self.add(base + src.count("\n", 0, m.start()), "XPP017", "error",
                         f"'{m.group(1)}' is an X++ reserved word and can't name a variable or parameter; "
                         "rename it (e.g. recordCount, idx, nextValue)")
            for m in SELECT_RE.finditer(src):
                for segment in JOIN_SPLIT_RE.split(m.group(1)):
                    w = re.search(r"\bwhere\b", segment, re.IGNORECASE)
                    o = re.search(r"\b(?:order|group)\s+by\b", segment, re.IGNORECASE)
                    if w and o and o.start() > w.start():
                        self.add(base + src.count("\n", 0, m.start()), "XPP018", "warning",
                                 "`order by`/`group by` must come before `where` in an X++ select ('join' expected)")
                        break

    # -- model boundaries --------------------------------------------------------------------

    def check_outside_model(self, model_folder: Path) -> bool:
        """XPP015. True when the file is in a Microsoft package."""
        pld = fno_model.find_pld(self.path.resolve())
        if not pld:
            return False
        pkg = pld[0] / pld[1]
        publishers = []
        try:
            for d in (pkg / "Descriptor").glob("*.xml"):
                m = fno_model.read_descriptor(d)
                if m:
                    publishers.append(m.publisher)
        except OSError:
            pass
        if any("microsoft" in p.lower() for p in publishers):
            self.add(1, "XPP015", "error",
                     f"{pld[1]} is a Microsoft package. Never edit it: extend it from your own model "
                     "(table/form extension, Chain of Command, event handler). Revert this edit.")
            return True
        return False

    def check_registration(self, model_folder: Path, ax_type: str, name: str) -> None:
        pkg = fno_model.package_of_model_folder(model_folder)
        if not pkg:
            return
        try:
            projects = sorted(pkg.glob("*.rnrproj"))
        except OSError:
            return
        if not projects:
            return
        key = f"{ax_type}/{name}".lower()
        if any(key in fno_model.project_entries(p) for p in projects):
            return
        names = ", ".join(p.name for p in projects)
        self.add(1, "XPP012", "warning",
                 f"{ax_type}\\{name} is not in {names}: add <Content Include=\"{ax_type}\\{name}\"> with "
                 "<SubType>Content</SubType>, <Name> and <Link> like its neighbours (the MCP's d365fo_file "
                 "create registers it for you)")

    def check_prefix(self, root: ET.Element, raw: str, model_folder: Path, ax_type: str, name: str) -> None:
        prefix = os.environ.get("FNO_XPP_PREFIX", "").strip() or fno_model.infer_prefix(model_folder)[0]
        is_extension = ax_type.endswith("Extension")
        if is_extension:
            if "." not in name:
                self.add(1, "XPP013", "warning", f"extension {name} should be named <BaseObject>.<ModelOrSuffix>, "
                         "e.g. EntAssetObjectTable.TheAssetGuardian")
            if prefix and ax_type == "AxTableExtension":
                for fld in descendants(root, "AxTableField"):
                    nm = child(fld, "Name")
                    fname = (nm.text or "").strip() if nm is not None else ""
                    if fname and not fname.startswith(prefix):
                        self.add(line_of(raw, f"<Name>{fname}</Name>"), "XPP013", "warning",
                                 f"field {fname} added to a standard table should start with {prefix}")
            return
        if prefix and not name.startswith(prefix):
            self.add(1, "XPP013", "warning", f"{name} doesn't start with the model prefix {prefix}")


def lint(path: Path, project_dir: Path | None = None) -> list[str]:
    return Linter(path, project_dir).run()


def is_target(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() == ".rnrproj":
        return True
    return p.suffix.lower() == ".xml" and (fno_model.is_ax_folder(p.parent.name) or p.parent.name == "Descriptor")


def hook() -> None:
    if os.environ.get("FNO_XPP_LINT") == "0":
        return
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not file_path or not is_target(file_path):
        return
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd")
    findings = lint(Path(file_path), Path(project_dir) if project_dir else None)
    if not findings:
        return
    context = (
        "X++ metadata check on the file you just edited (dynamics-fno-xpp xpp-xml-lint; codes are explained "
        "at the top of scripts/xpp-xml-lint.py and in the xpp-conventions skill). Errors break the build or "
        "the metadata reader; fix them now. Warnings: fix unless the repo deliberately does otherwise.\n"
        + "\n".join(findings[:30])
        + (f"\n... and {len(findings) - 30} more" if len(findings) > 30 else "")
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))


def main() -> int:
    if len(sys.argv) == 1:
        try:
            hook()
        except Exception as exc:  # a lint hook must never break the session
            print(f"dynamics-fno-xpp xpp-xml-lint: {exc}", file=sys.stderr)
        return 0
    findings = [f for arg in sys.argv[1:] for f in lint(Path(arg))]
    if findings:
        print("\n".join(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
