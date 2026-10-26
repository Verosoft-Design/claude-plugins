#!/usr/bin/env python3
"""Offline AL Builder ID-block and TAG partner-surface checks (stdlib only).

This is a source check, not an AL compiler. Quoted identifiers remain tokens;
comments and string literals cannot contribute declarations or calls. Package
resources are read in place, including .app archives with a NAVX prefix.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import NamedTuple


class Token(NamedTuple):
    text: str
    kind: str
    line: int

    @property
    def key(self):
        return self.text.casefold()


LEXEME = re.compile(
    r'//[^\n]*|/\*.*?\*/|\'(?:\'\'|[^\'])*\'|"(?:""|[^"])*"|'
    r'[A-Za-z_][A-Za-z_0-9]*|[0-9]+|::|[^\s]', re.DOTALL,
)
OBJECT_TYPES = {
    'table', 'tableextension', 'page', 'pageextension', 'codeunit', 'report',
    'reportextension', 'query', 'xmlport', 'enum', 'enumextension',
    'permissionset', 'permissionsetextension',
}


def tokenize(source):
    tokens = []
    line = 1
    position = 0
    for match in LEXEME.finditer(source):
        line += source[position:match.start()].count('\n')
        value = match.group()
        if not value.startswith(('//', '/*', "'")):
            if value.startswith('"'):
                tokens.append(Token(value[1:-1].replace('""', '"'), 'name', line))
            elif value.isdigit():
                tokens.append(Token(value, 'number', line))
            else:
                tokens.append(Token(value, 'word' if value[0].isalpha() or value[0] == '_' else 'punct', line))
        line += value.count('\n')
        position = match.end()
    return tokens


def objects(tokens):
    """Yield each numbered object and its body, without mixing object scopes."""
    i = 0
    while i + 2 < len(tokens):
        if tokens[i].kind == 'word' and tokens[i].key in OBJECT_TYPES and tokens[i + 1].kind == 'number':
            start = i
            while i < len(tokens) and tokens[i].text != '{':
                i += 1
            depth = 1
            end = i + 1
            while end < len(tokens) and depth:
                if tokens[end].text == '{':
                    depth += 1
                elif tokens[end].text == '}':
                    depth -= 1
                end += 1
            yield tokens[start], tokens[start + 1], tokens[i + 1:end - 1]
            i = end
        else:
            i += 1


def id_violations(tokens, block, file):
    violations = []

    def check(token, kind):
        value = int(token.text)
        if not block[0] <= value <= block[1]:
            violations.append({'file': file, 'line': token.line, 'kind': kind, 'id': value})

    for obj, number, body in objects(tokens):
        check(number, 'object')
        member = {'tableextension': 'field', 'enumextension': 'value'}.get(obj.key)
        if member:
            for i in range(len(body) - 3):
                if (body[i].kind == 'word' and body[i].key == member and body[i + 1].text == '('
                        and body[i + 2].kind == 'number' and body[i + 3].text == ';'):
                    check(body[i + 2], 'field' if member == 'field' else 'enumvalue')
    return violations


def load_tag_surface(project):
    """Index TAG codeunits by name and ID; absent allowlists grant no calls."""
    codeunits = {}
    allowlist = set()
    for path in sorted((project / '.alpackages').glob('*.app')):
        with zipfile.ZipFile(path) as package:
            symbols = json.loads(package.read('SymbolReference.json'))
            app = symbols.get('App', symbols)
            name = app.get('Name', '').casefold()
            units = symbols.get('Codeunits', [])
            if not (re.search(r'\btag\b', name) or 'the asset guardian' in name
                    or (not name and any(unit.get('Name', '').casefold().startswith('tag ') for unit in units))):
                continue
            for unit in units:
                canonical = unit['Name'].casefold()
                codeunits[canonical] = canonical
                codeunits[str(unit['Id'])] = canonical
            resource = 'Resources/partner-allowlist.json'
            if resource in package.namelist():
                for item in json.loads(package.read(resource)).get('procedures', []):
                    if item.get('objectType', '').casefold() == 'codeunit':
                        allowlist.add((item['objectName'].casefold(), item['procedure'].casefold()))
    return codeunits, allowlist


def declarations(tokens, codeunits):
    """Include non-TAG declarations so local names can shadow TAG globals."""
    result = {}
    for i in range(len(tokens) - 3):
        if tokens[i].kind in ('word', 'name') and tokens[i + 1].text == ':':
            target = codeunits.get(tokens[i + 3].key) if tokens[i + 2].key == 'codeunit' else None
            result[tokens[i].key] = target
            j = i - 1
            while j >= 1 and tokens[j].text == ',' and tokens[j - 1].kind in ('word', 'name'):
                result[tokens[j - 1].key] = target
                j -= 2
    return result


def routine_ranges(body):
    """Separate routine locals from globals, including globals declared last.

    AL begin/end and case/end nest; repeat/until does not add an end. Quoted
    identifiers and literal text cannot change the nesting.
    """
    i = 0
    while i + 2 < len(body):
        if not (body[i].kind == 'word' and body[i].key in ('procedure', 'trigger')
                and body[i + 1].kind in ('word', 'name') and body[i + 2].text == '('):
            i += 1
            continue
        start = i
        while i < len(body) and not (body[i].kind == 'word' and body[i].key == 'begin'):
            i += 1
        depth = 1
        i += 1
        while i < len(body) and depth:
            if body[i].kind == 'word':
                if body[i].key in ('begin', 'case'):
                    depth += 1
                elif body[i].key == 'end':
                    depth -= 1
            i += 1
        if depth:
            raise ValueError('incomplete_routine')
        yield start, i


def tag_violations(tokens, codeunits, allowlist, file):
    violations = []
    if not codeunits:
        return violations
    for _, _, body in objects(tokens):
        ranges = list(routine_ranges(body))
        global_tokens = []
        previous = 0
        for start, end in ranges:
            global_tokens.extend(body[previous:start])
            previous = end
        global_tokens.extend(body[previous:])
        globals_ = declarations(global_tokens, codeunits)
        for start, end in ranges:
            routine = body[start:end]
            variables = {**globals_, **declarations(routine, codeunits)}
            for i in range(len(routine) - 3):
                receiver, dot, method, paren = routine[i:i + 4]
                if dot.text != '.' or paren.text != '(':
                    continue
                target = variables.get(receiver.key)
                if target and (target, method.key) not in allowlist:
                    violations.append({'file': file, 'line': receiver.line,
                                       'call': f'{receiver.text}.{method.text}'})
                elif receiver.key == 'codeunit' and method.key == 'run':
                    args = routine[i + 4:]
                    if not args:
                        continue
                    if len(args) >= 3 and args[0].key == 'codeunit' and args[1].text == '::':
                        ref = args[2]
                        argument = f'Codeunit::"{ref.text}"' if ref.kind != 'number' else f'Codeunit::{ref.text}'
                    else:
                        ref = args[0]
                        argument = ref.text
                    if ref.key in codeunits:
                        violations.append({'file': file, 'line': receiver.line,
                                           'call': f'Codeunit.Run({argument})'})
    return violations


def check_project(project):
    config = json.loads((project / 'al-builder.json').read_text(encoding='utf-8-sig'))
    blocks = config['idBlocks']
    if not isinstance(config['affix'], str) or not config['affix'].strip():
        raise ValueError('invalid_affix')
    for kind in ('app', 'test'):
        block = blocks[kind]
        if (not isinstance(block, list) or len(block) != 2
                or any(type(value) is not int for value in block)
                or not 50000 <= block[0] <= block[1] <= 99999):
            raise ValueError('invalid_id_block')
    if max(blocks['app'][0], blocks['test'][0]) <= min(blocks['app'][1], blocks['test'][1]):
        raise ValueError('overlapping_id_blocks')
    codeunits, allowlist = load_tag_surface(project)
    ids, calls = [], []
    for kind in ('app', 'test'):
        for path in sorted((project / kind).rglob('*.al')):
            file = path.relative_to(project).as_posix()
            tokens = tokenize(path.read_text(encoding='utf-8-sig'))
            ids.extend(id_violations(tokens, blocks[kind], file))
            calls.extend(tag_violations(tokens, codeunits, allowlist, file))
    return {'ok': not ids and not calls,
            'idRange': {'ok': not ids, 'violations': ids},
            'tagSurface': {'ok': not calls, 'violations': calls}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--json', action='store_true', help='compact JSON (default: indented JSON)')
    args = parser.parse_args()
    try:
        report = check_project(args.project)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        # Keep the C7 shape, fail closed, and never echo file contents or values.
        print('al_builder_check_input_error', file=sys.stderr)
        report = {'ok': False, 'idRange': {'ok': False, 'violations': []},
                  'tagSurface': {'ok': False, 'violations': []}}
    print(json.dumps(report, indent=None if args.json else 2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
