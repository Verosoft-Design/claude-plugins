"""Temporary F&O metadata builders and isolated script loading."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
V6 = 'Microsoft.Dynamics.AX.Metadata.V6'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolves its defining module here
    with patch.object(sys, 'dont_write_bytecode', True):
        spec.loader.exec_module(module)
    return module


model = load('fno_model', 'fno_model.py')
linter = load('fno_test_linter', 'xpp-xml-lint.py')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def package(path, name='Contoso Assets', publisher='Contoso'):
    write(path / 'Descriptor' / (name + '.xml'), f'''<AxModelInfo>
<Name>{name}</Name><DisplayName>{name} Display</DisplayName>
<ModelModule>{path.name}</ModelModule><Layer>8</Layer><Publisher>{publisher}</Publisher>
<VersionMajor>1</VersionMajor><VersionMinor>0</VersionMinor><VersionBuild>0</VersionBuild><VersionRevision>0</VersionRevision>
<ModuleReferences xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
<d2p1:string>ApplicationSuite</d2p1:string><d2p1:string>ApplicationPlatform</d2p1:string>
</ModuleReferences></AxModelInfo>''')
    folder = path / name
    folder.mkdir(exist_ok=True)
    return folder


def object_xml(kind='AxTable', name='CTOWidget', body='', attrs=None):
    if attrs is None:
        attrs = f'xmlns:i="{XSI}"'
        if kind in ('AxForm', 'AxFormExtension'):
            attrs += f' xmlns="{V6}"'
        if kind == 'AxEdt':
            attrs += ' xmlns="" i:type="AxEdtInt64"'
    return f'<{kind} {attrs}><Name>{name}</Name>{body}</{kind}>'


def project(pkg, entries=('AxTable\\CTOWidget',)):
    items = ''.join(f'<Content Include="{e}"><SubType>Content</SubType><Name>{e.split(chr(92))[-1]}</Name><Link>Tables\\CTOWidget</Link></Content>' for e in entries)
    return write(pkg / 'Contoso.rnrproj', f'<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><PropertyGroup><Model>Contoso Assets</Model></PropertyGroup><ItemGroup>{items}</ItemGroup></Project>')


class TempTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.env = os.environ.copy()
        for key in ('FNO_XPP_PREFIX', 'FNO_XPP_LINT', 'FNO_PYTHON', 'CLAUDE_PLUGIN_ROOT'):
            self.env.pop(key, None)
        self.env['PYTHONDONTWRITEBYTECODE'] = '1'
        self.env['CLAUDE_PROJECT_DIR'] = str(self.root)
        self.env_patch = patch.dict(os.environ, self.env, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def run_script(self, script, args=(), payload='{}', env=None):
        return subprocess.run([sys.executable, '-B', str(SCRIPTS / script), *map(str, args)], input=payload, text=True, capture_output=True, cwd=self.root, env=self.env | (env or {}), timeout=20)

    def fixture(self):
        self.pkg = self.root / 'ContosoAssets'
        self.folder = package(self.pkg)
        for kind, name in [('AxTable', 'CTOWidget'), ('AxEdt', 'CTOWidgetRecId'), ('AxForm', 'CTOAssets'), ('AxEnum', 'CTOAssetStatus'), ('AxClass', 'CTOService')]:
            write(self.folder / kind / (name + '.xml'), object_xml(kind, name))
        return self.folder
