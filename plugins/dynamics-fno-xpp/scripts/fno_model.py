"""
Shared helpers for the dynamics-fno-xpp hooks: find F&O model packages in a repo,
read their descriptors, infer the object prefix, and read .rnrproj registrations.

Standard library only. Works on Windows and Unix paths.

Layout of a package (the same in PackagesLocalDirectory and in a repo that holds one):

    <Package>/                     e.g. TheAssetGuardian  (the "module")
      Descriptor/<Model>.xml       AxModelInfo: Name, DisplayName, ModelModule, Layer, ...
      <Model name>/                e.g. "The Asset Guardian" (may contain spaces)
        AxClass/  AxTable/  AxForm/ ...   one XML file per object
      *.rnrproj                    optional Visual Studio project(s)
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

LAYERS = ["SYS", "SYP", "GLS", "GLP", "FPK", "FPP", "SLN", "SLP", "ISV", "ISP", "VAR", "VAP", "CUS", "CUP", "USR", "USP"]

# Folders never worth descending into while looking for packages.
SKIP_DIRS = {
    ".git", ".vs", ".idea", ".vscode", "node_modules", "bin", "obj", "XppMetadata", "Resources",
    "AdditionalFiles", "modeloutput", "Descriptor",
}

# Object folders whose names are "<Base>.<Suffix>" (extensions) rather than prefixed names.
EXTENSION_FOLDERS_SUFFIX = "Extension"


@dataclass
class Model:
    name: str                      # <Name> in the descriptor (the folder name under the package)
    display_name: str
    module: str                    # <ModelModule> (the package folder name)
    layer: str
    publisher: str
    version: str
    references: list[str]
    descriptor: Path
    folder: Path | None            # <package>/<name>, if it exists


@dataclass
class Package:
    path: Path
    models: list[Model] = field(default_factory=list)
    projects: list[Path] = field(default_factory=list)


def _text(root: ET.Element, tag: str) -> str:
    el = root.find(tag)
    return (el.text or "").strip() if el is not None and el.text else ""


def read_descriptor(path: Path) -> Model | None:
    """Parse one Descriptor/*.xml. Returns None if it is not an AxModelInfo."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None
    if root.tag.split("}")[-1] != "AxModelInfo":
        return None
    name = _text(root, "Name")
    module = _text(root, "ModelModule") or path.parent.parent.name
    module_refs = root.find("ModuleReferences")
    refs = sorted((c.text or "").strip() for c in (module_refs if module_refs is not None else []) if (c.text or "").strip())
    try:
        layer_num = int(_text(root, "Layer") or -1)
    except ValueError:
        layer_num = -1
    layer = f"{layer_num} ({LAYERS[layer_num]})" if 0 <= layer_num < len(LAYERS) else _text(root, "Layer") or "?"
    version = ".".join(_text(root, t) or "0" for t in ("VersionMajor", "VersionMinor", "VersionBuild", "VersionRevision"))
    folder = path.parent.parent / name if name else None
    return Model(
        name=name,
        display_name=_text(root, "DisplayName") or name,
        module=module,
        layer=layer,
        publisher=_text(root, "Publisher"),
        version=version,
        references=refs,
        descriptor=path,
        folder=folder if folder and is_dir(folder) else None,
    )


def is_dir(path: Path) -> bool:
    """Path.is_dir() that treats unreadable paths as absent instead of raising."""
    try:
        return path.is_dir()
    except OSError:
        return False


def find_packages(root: Path, max_depth: int = 3, limit: int = 12) -> list[Package]:
    """Packages (folders with a Descriptor/ of AxModelInfo files) at most max_depth below root.

    Stops descending at a package, so it never walks a model's thousands of object files.
    Returns at most `limit` + 1 packages; more than `limit` means root is PackagesLocalDirectory itself.
    """
    found: list[Package] = []
    stack = [(root, 0)]
    while stack and len(found) <= limit:
        d, depth = stack.pop()
        desc = d / "Descriptor"
        if is_dir(desc):
            try:
                descriptors = sorted(desc.glob("*.xml"))
            except OSError:
                descriptors = []
            models = [m for m in (read_descriptor(p) for p in descriptors) if m]
            if models:
                found.append(Package(path=d, models=models, projects=sorted(d.glob("*.rnrproj"))))
                continue
        if depth >= max_depth:
            continue
        try:
            entries = sorted(d.iterdir(), reverse=True)
        except OSError:
            continue
        for e in entries:
            if e.name not in SKIP_DIRS and is_dir(e) and not e.name.startswith(".") and not e.name.startswith("Ax"):
                stack.append((e, depth + 1))
    return sorted(found, key=lambda p: str(p.path))


def object_names(model_folder: Path) -> Counter:
    """Count of objects per Ax* folder."""
    counts: Counter = Counter()
    try:
        for d in model_folder.iterdir():
            if d.is_dir() and d.name.startswith("Ax"):
                counts[d.name] = sum(1 for f in d.glob("*.xml"))
    except OSError:
        pass
    return counts


def infer_prefix(model_folder: Path, min_share: float = 0.6, per_folder: int = 300) -> tuple[str, float]:
    """The longest all-uppercase prefix shared by at least min_share of the model's own
    (non-extension) object names, e.g. ("TAG", 0.97). ("", 0.0) when there is none.
    Reads at most `per_folder` names per Ax* folder, so a huge model stays fast."""
    names: list[str] = []
    try:
        for d in model_folder.iterdir():
            if d.name.startswith("Ax") and not d.name.endswith(EXTENSION_FOLDERS_SUFFIX) and d.name != "AxLabelFile" and is_dir(d):
                for i, f in enumerate(d.glob("*.xml")):
                    if i >= per_folder:
                        break
                    names.append(f.stem)
    except OSError:
        return "", 0.0
    if not names:
        return "", 0.0
    best = ("", 0.0)
    for length in range(2, 9):
        counts = Counter(n[:length] for n in names if len(n) > length and n[:length].isupper() and n[:length].isalpha())
        if not counts:
            break
        prefix, hits = counts.most_common(1)[0]
        share = hits / len(names)
        if share < min_share:
            break
        best = (prefix, share)
    return best


_CONTENT_RE = re.compile(r'<Content\s+Include="([^"]+)"', re.IGNORECASE)


def project_entries(project: Path) -> set[str]:
    """Registered objects of a .rnrproj, normalised to 'axtype/name' in lower case."""
    try:
        text = project.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return set()
    return {m.replace("\\", "/").strip("/").lower() for m in _CONTENT_RE.findall(text)}


def project_model(project: Path) -> str:
    try:
        m = re.search(r"<Model>([^<]+)</Model>", project.read_text(encoding="utf-8-sig", errors="replace"))
    except OSError:
        return ""
    return m.group(1).strip() if m else ""


def find_pld(path: Path) -> tuple[Path, str] | None:
    """If path is inside a PackagesLocalDirectory, return (pld, package name)."""
    parts = path.parts
    for i, part in enumerate(parts):
        if part.lower() == "packageslocaldirectory" and i + 1 < len(parts):
            return Path(*parts[: i + 1]), parts[i + 1]
    return None


def locate_object(path: Path) -> tuple[Path, str, str] | None:
    """For <...>/<Model folder>/<AxType>/<Name>.xml return (model folder, AxType, Name)."""
    if path.suffix.lower() != ".xml":
        return None
    ax_type = path.parent.name
    if not ax_type.startswith("Ax") or ax_type == "AxLabelFile":
        return None
    return path.parent.parent, ax_type, path.stem


def package_of_model_folder(model_folder: Path) -> Path | None:
    """The package that owns a model folder: its parent, when that has a Descriptor/."""
    pkg = model_folder.parent
    return pkg if is_dir(pkg / "Descriptor") else None


def is_windows_fno_vm() -> tuple[bool, str]:
    """True on a Windows machine with an F&O PackagesLocalDirectory (xppc.exe present)."""
    if os.name != "nt":
        return False, ""
    for drive in "CDEFGHIJKLMNOPQ":
        xppc = Path(f"{drive}:/AosService/PackagesLocalDirectory/Bin/xppc.exe")
        if xppc.is_file():
            return True, str(xppc.parent.parent)
    return False, ""
