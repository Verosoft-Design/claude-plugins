"""Offline contract tests for the AL Builder check and Studio session hook."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN / 'scripts' / 'al-builder-check.py'
FIXTURES = Path(__file__).parent / 'fixtures'


class BuilderCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        shutil.copytree(FIXTURES / 'valid', self.project, dirs_exist_ok=True)

    def check(self, expected_code=0, json_output=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--project', str(self.project),
             *(['--json'] if json_output else [])],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected_code, result.stderr or result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {'ok', 'idRange', 'tagSurface'})
        self.assertEqual(report['ok'], expected_code == 0)
        return report

    def source(self, fixture, app='app'):
        target = self.project / app / 'src' / 'Case.al'
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURES / 'cases' / fixture, target)
        return f'{app}/src/Case.al'

    def package(self, allowlist=None, tag=True, header=False,
                symbols_fixture='tag-symbols.json', manifest=None, bom=False):
        cache = self.project / '.alpackages'
        cache.mkdir(exist_ok=True)
        target = cache / ('Verosoft_TAG_29.0.0.0.app' if tag else 'Microsoft_Base.app')
        symbols = json.loads((FIXTURES / symbols_fixture).read_text())
        if not tag:
            symbols['App']['Id'] = '11111111-2222-4333-8444-555555555555'
            symbols['App']['Name'] = 'Base Application'
            symbols['Codeunits'][0]['Name'] = 'Sales-Post'
        with zipfile.ZipFile(target, 'w') as package:
            package.writestr('SymbolReference.json', json.dumps(symbols).encode('utf-8-sig' if bom else 'utf-8'))
            if manifest is not None:
                package.writestr('NavxManifest.xml', (FIXTURES / manifest).read_bytes())
            if allowlist is not None:
                package.writestr('Resources/partner-allowlist.json', json.dumps(allowlist))
        if header:
            target.write_bytes(b'NAVX' + bytes(36) + target.read_bytes())
        return target

    def test_valid_ids_for_both_apps_and_page_controls(self):
        report = self.check()
        self.assertEqual(report['idRange'], {'ok': True, 'violations': []})
        self.assertEqual(report['tagSurface'], {'ok': True, 'violations': []})

    def test_object_outside_app_block(self):
        path = self.source('object-outside.al')
        report = self.check(1)
        self.assertEqual(report['idRange']['violations'], [
            {'file': path, 'line': 2, 'kind': 'object', 'id': 50200}])

    def test_tableextension_field_outside_app_block(self):
        path = self.source('field-outside.al')
        report = self.check(1)
        self.assertEqual(report['idRange']['violations'], [
            {'file': path, 'line': 5, 'kind': 'field', 'id': 49999}])

    def test_new_table_fields_use_local_ids(self):
        self.source('new-table-local-fields.al')
        self.assertEqual(self.check()['idRange'], {'ok': True, 'violations': []})

    def test_new_enum_values_use_local_ids(self):
        self.source('new-enum-local-values.al')
        self.assertEqual(self.check()['idRange'], {'ok': True, 'violations': []})

    def test_enumextension_value_below_app_block(self):
        path = self.source('enumvalue-below-block.al')
        self.assertEqual(self.check(1)['idRange']['violations'], [
            {'file': path, 'line': 3, 'kind': 'enumvalue', 'id': 1}])

    def test_enumextension_value_outside_app_block(self):
        path = self.source('enumvalue-outside.al')
        report = self.check(1)
        self.assertEqual(report['idRange']['violations'], [
            {'file': path, 'line': 3, 'kind': 'enumvalue', 'id': 50200}])

    def test_test_objects_use_test_block(self):
        path = self.source('wrong-test-block.al', 'test')
        self.assertEqual(self.check(1)['idRange']['violations'], [
            {'file': path, 'line': 1, 'kind': 'object', 'id': 50000}])

    def test_non_allowlisted_named_codeunit_call(self):
        self.package()
        path = self.source('tag-call.al')
        report = self.check(1)
        self.assertEqual(report['tagSurface']['violations'], [
            {'file': path, 'line': 9, 'call': 'WorkOrderMgt.Release'}])
        self.assertTrue(report['idRange']['ok'])

    def test_manifest_tag_with_namespaced_codeunit_header_and_bom_is_restricted(self):
        self.package(symbols_fixture='tag-namespaced-symbols.json',
                     manifest='tag-manifest.xml', header=True, bom=True)
        path = self.source('tag-call.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 9, 'call': 'WorkOrderMgt.Release'}])

    def test_namespaced_tag_codeunit_can_be_allowlisted(self):
        self.package({'procedures': [{'objectType': 'Codeunit',
            'objectName': 'TAG Work Order Mgt.', 'procedure': 'Release'}]},
            symbols_fixture='tag-namespaced-symbols.json',
            manifest='tag-manifest.xml', header=True, bom=True)
        self.source('tag-call.al')
        self.check()

    def test_namespaced_tag_codeunit_is_resolved_by_numeric_id(self):
        self.package(symbols_fixture='tag-namespaced-symbols.json',
                     manifest='tag-manifest.xml', header=True, bom=True)
        path = self.source('tag-id-call.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 7, 'call': 'WorkOrderMgt.Release'}])

    def test_non_tag_package_with_tag_in_name_is_ignored(self):
        self.package(symbols_fixture='non-tag-symbols.json')
        self.source('tag-call.al')
        self.assertEqual(self.check()['tagSurface'], {'ok': True, 'violations': []})

    def test_allowlist_from_tag_package_allows_call(self):
        self.package({'procedures': [{'objectType': 'Codeunit',
            'objectName': 'TAG Work Order Mgt.', 'procedure': 'Release'}]}, header=True)
        self.source('tag-call.al')
        self.check()

    def test_allowlist_matches_object_and_method_case_insensitively(self):
        self.package({'procedures': [{'objectType': 'codeunit',
            'objectName': 'tag work order mgt.', 'procedure': 'release'}]})
        self.source('tag-call.al')
        self.check()

    def test_allowlisting_another_object_does_not_allow_call(self):
        self.package({'procedures': [{'objectType': 'Codeunit',
            'objectName': 'TAG Other Mgt.', 'procedure': 'Release'}]})
        self.source('tag-call.al')
        self.check(1)

    def test_numeric_codeunit_variable(self):
        self.package()
        path = self.source('tag-id-call.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 7, 'call': 'WorkOrderMgt.Release'}])

    def test_codeunit_run_by_name_and_id(self):
        self.package({'procedures': [{'objectType': 'Codeunit',
            'objectName': 'TAG Work Order Mgt.', 'procedure': 'Release'}]})
        path = self.source('tag-run.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 5, 'call': 'Codeunit.Run(Codeunit::"TAG Work Order Mgt.")'},
            {'file': path, 'line': 6, 'call': 'Codeunit.Run(70015000)'}])

    def test_tag_extensions_subscribers_and_api_pages_are_allowed(self):
        self.package()
        self.source('tag-public-surface.al')
        self.check()

    def test_comments_strings_and_escaped_quotes_are_ignored(self):
        self.package()
        self.source('ignored-text.al')
        self.check()

    def test_global_variables_after_procedures_are_resolved(self):
        self.package()
        path = self.source('tag-late-global.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 5, 'call': 'WorkOrderMgt.Release'}])

    def test_local_variables_do_not_leak_between_procedures_or_objects(self):
        self.package()
        self.source('tag-local-scopes.al')
        self.check()

    def test_each_variable_in_a_multi_name_declaration_is_resolved(self):
        self.package()
        path = self.source('tag-multiple-vars.al')
        self.assertEqual(self.check(1)['tagSurface']['violations'], [
            {'file': path, 'line': 7, 'call': 'FirstMgt.Release'},
            {'file': path, 'line': 8, 'call': 'SecondMgt.Release'}])

    def test_test_app_cannot_bypass_tag_surface(self):
        self.package()
        self.source('tag-test-call.al', 'test')
        self.assertEqual(len(self.check(1)['tagSurface']['violations']), 1)

    def test_corrupt_package_fails_closed(self):
        path = self.package()
        path.write_bytes(b'not an app')
        self.check(1)

    def test_invalid_or_overlapping_blocks_fail_closed(self):
        path = self.project / 'al-builder.json'
        config = json.loads(path.read_text())
        for block in ([1, 50000], [50010, 50000], [50000, 50010], ['50200', 50299]):
            with self.subTest(block=block):
                config['idBlocks']['test'] = block
                path.write_text(json.dumps(config))
                self.check(1)

    def test_no_tag_package_skips_tag_check(self):
        self.source('tag-call.al')
        self.assertEqual(self.check()['tagSurface'], {'ok': True, 'violations': []})

    def test_non_tag_package_is_not_restricted(self):
        self.package(tag=False)
        self.source('microsoft-call.al')
        self.check()

    def test_check_without_json_flag_keeps_machine_readable_contract(self):
        self.check(json_output=False)

    def test_missing_configuration_fails_closed(self):
        (self.project / 'al-builder.json').unlink()
        result = subprocess.run([sys.executable, str(SCRIPT), '--project', str(self.project), '--json'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['ok'])
        self.assertNotIn('Traceback', result.stderr)

    def test_studio_session_uses_broker_without_local_server_advice(self):
        result = subprocess.run([sys.executable, str(PLUGIN / 'scripts' / 'session-start.py')],
            env={**os.environ, 'AL_BUILDER': '1', 'CLAUDE_PROJECT_DIR': str(self.project)},
            input='{}', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ('Cedar Ridge Customizations', 'AL Builder', '50200', '50299', 'CRD',
                     'tests run through bc_run_tests'):
            self.assertIn(text, result.stdout)
        for text in ('bc-server-setup', 'al runtests', 'al-test', 'bc-server.json'):
            self.assertNotIn(text, result.stdout)

    def test_studio_session_before_app_scaffold_still_shows_context(self):
        shutil.rmtree(self.project / 'app')
        shutil.rmtree(self.project / 'test')
        result = subprocess.run([sys.executable, str(PLUGIN / 'scripts' / 'session-start.py')],
            env={**os.environ, 'AL_BUILDER': '1', 'CLAUDE_PROJECT_DIR': str(self.project)},
            input='{}', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Cedar Ridge Customizations', result.stdout)


if __name__ == '__main__':
    unittest.main()
