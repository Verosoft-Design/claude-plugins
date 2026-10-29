import io
from pathlib import Path
from unittest.mock import patch
from fixtures import TempTest, load, model, object_xml, package, project, write


class ModelTests(TempTest):
    def test_package_depths(self):
        for depth in (0, 1, 3, 4):
            with self.subTest(depth=depth):
                root = self.root / str(depth)
                pkg = root.joinpath(*(['nested'] * depth))
                package(pkg)
                self.assertEqual([p.path for p in model.find_packages(root)], [pkg] if depth <= 3 else [])

    def test_stops_at_package(self):
        folder = self.fixture()
        package(folder / 'NestedPackage')
        self.assertEqual([p.path for p in model.find_packages(self.root)], [self.pkg])

    def test_ignores_non_model_descriptor(self):
        write(self.root / 'Descriptor' / 'Other.xml', '<Other/>')
        self.assertEqual(model.find_packages(self.root), [])

    def test_thirteen_packages(self):
        for i in range(13):
            package(self.root / f'Contoso{i}')
        self.assertEqual(len(model.find_packages(self.root)), 13)

    def test_unreadable_directory(self):
        with patch.object(Path, 'iterdir', side_effect=PermissionError('unreadable')):
            self.assertEqual(model.find_packages(self.root), [])
        with patch.object(Path, 'is_dir', side_effect=PermissionError('unreadable')):
            self.assertFalse(model.is_dir(self.root))

    def test_descriptor(self):
        self.fixture()
        m = model.read_descriptor(self.pkg / 'Descriptor' / 'Contoso Assets.xml')
        self.assertEqual((m.name, m.module, m.layer, m.version), ('Contoso Assets', 'ContosoAssets', '8 (ISV)', '1.0.0.0'))
        self.assertEqual(m.references, ['ApplicationPlatform', 'ApplicationSuite'])

    def test_prefix_longest_and_ignored_folders(self):
        folder = self.fixture()
        for kind in ('AxTableExtension', 'AxLabelFile'):
            for i in range(20):
                write(folder / kind / f'Other{i}.xml', '<Other/>')
        self.assertEqual(model.infer_prefix(folder), ('CTO', 1.0))
        write(folder / 'AxTable' / 'Other.xml', '<AxTable/>')
        self.assertEqual(model.infer_prefix(folder), ('CTO', 5 / 6))

    def test_prefix_below_threshold_and_empty(self):
        self.assertEqual(model.infer_prefix(self.root), ('', 0.0))
        for name in ('CTOWidget', 'ABThing', 'XYOther'):
            write(self.root / 'AxTable' / (name + '.xml'), '<AxTable/>')
        self.assertEqual(model.infer_prefix(self.root), ('', 0.0))

    def test_project(self):
        self.fixture()
        p = project(self.pkg)
        self.assertEqual(model.project_entries(p), {'axtable/ctowidget'})
        self.assertEqual(model.project_model(p), 'Contoso Assets')

    def test_pld_case_insensitive(self):
        pld = self.root / 'packagesLOCALdirectory'
        self.assertEqual(model.find_pld(pld / 'ContosoAssets' / 'Contoso Assets'), (pld, 'ContosoAssets'))
        self.assertIsNone(model.find_pld(self.root))

    def test_locate_object(self):
        p = self.root / 'Contoso Assets' / 'AxTable' / 'X.xml'
        self.assertEqual(model.locate_object(p), (p.parent.parent, 'AxTable', 'X'))
        for folder in ('AxLabelFile', 'Other'):
            self.assertIsNone(model.locate_object(self.root / folder / 'X.xml'))


class SessionTests(TempTest):
    def test_empty_folder_silent(self):
        r = self.run_script('session-start.py')
        self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_model_context_and_init(self):
        self.fixture()
        project(self.pkg)
        r = self.run_script('session-start.py')
        self.assertEqual(r.returncode, 0)
        for text in ('Contoso Assets Display', 'ContosoAssets', '8 (ISV)', 'object prefix: CTO', 'Contoso.rnrproj', '1 objects registered', '/fno-init'):
            self.assertIn(text, r.stdout)
        write(self.root / 'CLAUDE.md', '# Conventions')
        self.assertNotIn('/fno-init', self.run_script('session-start.py').stdout)

    def test_prefix_override(self):
        self.fixture()
        r = self.run_script('session-start.py', env={'FNO_XPP_PREFIX': 'ZZZ'})
        self.assertIn('object prefix: ZZZ (FNO_XPP_PREFIX)', r.stdout)
        self.assertNotIn('object prefix: CTO', r.stdout)

    def test_packages_local_directory(self):
        for i in range(13):
            package(self.root / f'Contoso{i}')
        r = self.run_script('session-start.py')
        self.assertEqual(r.returncode, 0)
        self.assertIn('more than 12 packages', r.stdout)
        self.assertIn('PackagesLocalDirectory itself', r.stdout)

    def test_file_as_project_dir(self):
        p = write(self.root / 'file', 'content')
        r = self.run_script('session-start.py', env={'CLAUDE_PROJECT_DIR': str(p)})
        self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_raised_discovery_is_caught_at_entrypoint(self):
        # Execute the actual __main__ guard while forcing discovery to fail.
        import runpy
        with patch.object(model, 'find_packages', side_effect=OSError('unreadable')), patch('sys.stdin', io.StringIO('{}')), patch('sys.stderr', io.StringIO()), self.assertRaises(SystemExit) as caught:
            runpy.run_path(str(__import__('fixtures').SCRIPTS / 'session-start.py'), run_name='__main__')
        self.assertEqual(caught.exception.code, 0)
