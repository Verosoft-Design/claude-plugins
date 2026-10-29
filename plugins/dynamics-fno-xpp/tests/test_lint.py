import json
from fixtures import TempTest, linter, object_xml, package, project, write


def source(body, declaration='public class CTOWidget {}', method='run'):
    return f'<SourceCode><Declaration><![CDATA[{declaration}]]></Declaration><Methods><Method><Name>{method}</Name><Source><![CDATA[{body}]]></Source></Method></Methods></SourceCode>'


class LintTests(TempTest):
    def setUp(self):
        super().setUp()
        self.fixture()

    def check(self, code, body='', kind='AxTable', name='CTOWidget', present=True, severity='error', attrs=None, raw=None):
        p = write(self.folder / kind / (name + '.xml'), raw if raw is not None else object_xml(kind, name, body, attrs))
        findings = linter.lint(p)
        matching = [f for f in findings if code in f]
        if present:
            self.assertTrue(matching, findings)
            self.assertTrue(all(f'{code} {severity}:' in f for f in matching), matching)
        else:
            self.assertEqual(matching, [], findings)
        return matching

    def test_xpp001_line_number(self):
        findings = self.check('XPP001', raw='<AxTable>\n<Name>CTOWidget</Name>\n</Wrong>')
        self.assertIn(':3: XPP001', findings[0])

    def test_xpp012_missing_registration(self):
        project(self.pkg, ())
        self.check('XPP012', severity='warning')

    def test_xpp012_registered(self):
        project(self.pkg)
        self.check('XPP012', present=False)

    def test_xpp012_no_project(self):
        self.check('XPP012', present=False)

    def test_xpp015_microsoft_package(self):
        pkg = self.root / 'AosService' / 'PackagesLocalDirectory' / 'ApplicationSuite'
        folder = package(pkg, 'Foundation', 'Microsoft Corporation')
        project(pkg, ())
        write(folder / 'AxTable' / 'CTOWidget.xml', object_xml())
        p = write(folder / 'AxTable' / 'CustTable.xml', object_xml(name='CustTable'))
        findings = linter.lint(p)
        self.assertTrue(any('XPP015 error:' in f for f in findings), findings)
        self.assertFalse(any('XPP012' in f or 'XPP013' in f for f in findings), findings)

    def test_xpp015_own_package(self):
        self.check('XPP015', present=False)


# Each row becomes its own named unittest, with a fresh temporary model.
CASES = [
    ('001_clean', 'XPP001', {}, False),
    ('002_bad_cdata', 'XPP002', {'raw': '<AxTable><![CDATA>broken</AxTable>'}, True),
    ('002_valid_cdata', 'XPP002', {'body': '<Source><![CDATA[true]]></Source>'}, False),
    ('003_wrong_root', 'XPP003', {'raw': object_xml('AxClass')}, True),
    ('003_correct_root', 'XPP003', {}, False),
    ('004_mismatch', 'XPP004', {'raw': object_xml(name='CTOOther')}, True),
    ('004_case_only', 'XPP004', {'raw': object_xml(name='ctowidget')}, False),
    ('005_edt_namespace', 'XPP005', {'kind': 'AxEdt', 'attrs': 'xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="Microsoft.Dynamics.AX.Metadata.V6" i:type="AxEdtInt64"'}, True),
    ('005_edt_missing_type', 'XPP005', {'kind': 'AxEdt', 'attrs': ''}, True),
    ('005_edt_clean', 'XPP005', {'kind': 'AxEdt'}, False),
    ('005_form_missing_namespace', 'XPP005', {'kind': 'AxForm', 'attrs': ''}, True),
    ('005_form_clean', 'XPP005', {'kind': 'AxForm'}, False),
    ('006_tf_wrong', 'XPP006', {'body': '<IsExtensible>Yes</IsExtensible>'}, True),
    ('006_tf_clean', 'XPP006', {'body': '<IsExtensible>true</IsExtensible>'}, False),
    ('006_yn_wrong', 'XPP006', {'body': '<Mandatory>true</Mandatory>'}, True),
    ('006_yn_clean', 'XPP006', {'body': '<Mandatory>Yes</Mandatory>'}, False),
    ('006_unknown', 'XPP006', {'body': '<Foo>true</Foo>'}, False),
    ('006_source_ignored', 'XPP006', {'kind': 'AxClass', 'body': source('boolean enabled = true; // <Mandatory>true</Mandatory>')}, False),
    ('007_bad_control', 'XPP007', {'kind': 'AxForm', 'body': '<Controls><AxFormControl i:type="AxFormIntControl"><Name>Number</Name></AxFormControl></Controls>'}, True),
    ('007_valid_control', 'XPP007', {'kind': 'AxForm', 'body': '<Controls><AxFormControl i:type="AxFormIntegerControl"><Name>Number</Name></AxFormControl></Controls>'}, False),
    ('008_bad_command', 'XPP008', {'kind': 'AxForm', 'body': '<Command>SaveAndClose</Command>'}, True),
    ('008_bad_close_command', 'XPP008', {'kind': 'AxForm', 'body': '<Command>SystemDefinedCloseButton</Command>'}, True),
    ('008_valid_command', 'XPP008', {'kind': 'AxForm', 'body': '<Command>CloseForm</Command>'}, False),
    ('009_bad_pattern', 'XPP009', {'kind': 'AxForm', 'body': '<Pattern>DetailsFormMaster</Pattern>'}, True),
    ('009_valid_version', 'XPP009', {'kind': 'AxForm', 'body': '<Pattern>SimpleList</Pattern><PatternVersion>1.1</PatternVersion>'}, False),
    ('009_unknown_version', 'XPP009', {'kind': 'AxForm', 'body': '<Pattern>SimpleList</Pattern><PatternVersion>9.9</PatternVersion>', 'severity': 'warning'}, True),
    ('010_enumvalue', 'XPP010', {'kind': 'AxEnum', 'body': '<EnumValues><AxEnumValue><Name>Ready</Name><EnumValue>1</EnumValue></AxEnumValue></EnumValues>'}, True),
    ('010_missing_values', 'XPP010', {'kind': 'AxEnum', 'body': '<EnumValues><AxEnumValue><Name>Ready</Name></AxEnumValue><AxEnumValue><Name>Done</Name></AxEnumValue></EnumValues>'}, True),
    ('010_first_implicit', 'XPP010', {'kind': 'AxEnum', 'body': '<EnumValues><AxEnumValue><Name>Ready</Name></AxEnumValue><AxEnumValue><Name>Done</Name><Value>1</Value></AxEnumValue></EnumValues>'}, False),
    ('011_delete_missing_table', 'XPP011', {'body': '<DeleteActions><AxTableDeleteAction><Name>Related</Name></AxTableDeleteAction></DeleteActions>'}, True),
    ('011_delete_valid', 'XPP011', {'body': '<DeleteActions><AxTableDeleteAction><Name>Related</Name><Table>CTOOther</Table></AxTableDeleteAction></DeleteActions>'}, False),
    ('011_duplicate_primary', 'XPP011', {'body': '<PrimaryIndex>WidgetIdx</PrimaryIndex><Indexes><AxTableIndex><Name>WidgetIdx</Name><AllowDuplicates>Yes</AllowDuplicates></AxTableIndex></Indexes>'}, True),
    ('011_unique_primary', 'XPP011', {'body': '<PrimaryIndex>WidgetIdx</PrimaryIndex><Indexes><AxTableIndex><Name>WidgetIdx</Name><AllowDuplicates>No</AllowDuplicates></AxTableIndex></Indexes>'}, False),
    ('013_unprefixed_object', 'XPP013', {'name': 'Widget', 'severity': 'warning'}, True),
    ('013_prefixed_object', 'XPP013', {}, False),
    ('013_extension_no_dot', 'XPP013', {'kind': 'AxTableExtension', 'name': 'CustTable', 'severity': 'warning'}, True),
    ('013_extension_field', 'XPP013', {'kind': 'AxTableExtension', 'name': 'CustTable.ContosoAssets', 'body': '<Fields><AxTableField><Name>Foo</Name></AxTableField></Fields>', 'severity': 'warning'}, True),
    ('013_prefixed_extension_field', 'XPP013', {'kind': 'AxTableExtension', 'name': 'CustTable.ContosoAssets', 'body': '<Fields><AxTableField><Name>CTOFoo</Name></AxTableField></Fields>'}, False),
    ('014_wrong_class_name', 'XPP014', {'kind': 'AxClass', 'name': 'CTOCustTableExt', 'body': source('', '[ExtensionOf(tableStr(CustTable))] final class CTOCustTableExt {}')}, True),
    ('014_valid_class_name', 'XPP014', {'kind': 'AxClass', 'name': 'CTOCustTable_Extension', 'body': source('', '[ExtensionOf(tableStr(CustTable))] final class CTOCustTable_Extension {}')}, False),
    ('014_commented_attribute', 'XPP014', {'kind': 'AxClass', 'body': source('', '// [ExtensionOf(tableStr(CustTable))]\npublic class CTOWidget {}')}, False),
]
for suffix, code, options, present in CASES:
    def test(self, code=code, options=options, present=present):
        result = self.check(code, present=present, **options)
        if code == 'XPP007' and present:
            self.assertIn('AxFormIntegerControl', result[0])
    setattr(LintTests, 'test_xpp' + suffix, test)

for suffix, body, present in [
    ('default_wrapper', 'public void initFromX(Foo _foo = this.Foo) { next initFromX(_foo); }', True),
    ('wrapper_without_default', 'public void initFromX(Foo _foo) { next initFromX(_foo); }', False),
    ('new_method_default', 'public void initFromX(Foo _foo = this.Foo) { this.Foo = _foo; }', False),
]:
    def test(self, body=body, present=present):
        self.check('XPP016', kind='AxClass', name='CTOCustTable_Extension', body=source(body, '[ExtensionOf(tableStr(CustTable))] final class CTOCustTable_Extension {}', 'initFromX'), present=present, severity='warning')
    setattr(LintTests, 'test_xpp016_' + suffix, test)

for suffix, code, body, present in [
    ('count', 'XPP017', 'int count;', True),
    ('index', 'XPP017', 'CustTable index = CustTable::find();', True),
    ('field_allowed', 'XPP017', 'TAGField field;', False),
    ('desc_allowed', 'XPP017', 'select x order by Name desc;', False),
    ('comment_ignored', 'XPP017', '// int count;\nint recordCount;', False),
    ('wrong_order', 'XPP018', 'select x where x.A == 1 order by B;', True),
    ('valid_order', 'XPP018', 'select x order by B where x.A == 1;', False),
    ('join_segments', 'XPP018', 'select a order by F where a.A == 1 join b where b.A == a.A;', False),
]:
    def test(self, code=code, body=body, present=present):
        self.check(code, kind='AxClass', body=source(body), present=present, severity='warning' if code == 'XPP018' else 'error')
    setattr(LintTests, 'test_' + code.lower() + '_' + suffix, test)


class HookCliTests(TempTest):
    def setUp(self):
        super().setUp()
        self.fixture()
        self.clean = self.folder / 'AxTable' / 'CTOWidget.xml'
        self.bad = write(self.folder / 'AxTable' / 'CTOBroken.xml', object_xml(name='Wrong'))

    def hook(self, path, **kwargs):
        return self.run_script('xpp-xml-lint.py', payload=json.dumps({'tool_input': {'file_path': str(path)}}), **kwargs)

    def test_hook_findings_json(self):
        r = self.hook(self.bad)
        self.assertEqual(r.returncode, 0)
        output = json.loads(r.stdout)['hookSpecificOutput']
        self.assertEqual(output['hookEventName'], 'PostToolUse')
        self.assertIn('XPP004 error:', output['additionalContext'])
        self.assertIn(str(self.bad), output['additionalContext'])

    def test_hook_clean_silent(self):
        r = self.hook(self.clean)
        self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_hook_non_aot_silent(self):
        for name in ('README.md', 'other.xml', 'Axios/config.xml'):
            with self.subTest(name=name):
                r = self.hook(write(self.root / name, 'not XML'))
                self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_hook_disabled(self):
        r = self.hook(self.bad, env={'FNO_XPP_LINT': '0'})
        self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_hook_invalid_json(self):
        r = self.run_script('xpp-xml-lint.py', payload='{invalid')
        self.assertEqual((r.returncode, r.stdout), (0, ''))

    def test_cli_findings(self):
        r = self.run_script('xpp-xml-lint.py', [self.bad])
        self.assertEqual(r.returncode, 1)
        self.assertIn('XPP004 error:', r.stdout)

    def test_cli_clean(self):
        r = self.run_script('xpp-xml-lint.py', [self.clean])
        self.assertEqual((r.returncode, r.stdout), (0, ''))
