"""Prospective optional-record elimination prototype; no R5.23 modules edited.

`presence` is a type-directed test of record membership, not a new domain
relation. A conjunction gathers its local refinement facts before checking
its members; the checked executable evaluates the guards before consumers.
"""

import json

from benchmark.semantic.typed_lowering_r5_12 import _type
from benchmark.semantic.capability_boundary_r5_22 import parse_instant
from benchmark.semantic.generative_r5_13 import shape_valid


def _path_type(path, slots, refinements):
    if not isinstance(path, list) or not path or any(type(p) is not str for p in path):
        raise ValueError('invalid reference')
    if path[0] not in slots:
        raise ValueError('unknown reference')
    shape = slots[path[0]]
    for name in path[1:]:
        if not isinstance(shape, dict) or set(shape) != {'record'} or name not in shape['record']:
            raise ValueError('invalid field reference')
        shape = shape['record'][name]
    if tuple(path) in refinements:
        shape = shape['optional']
    return shape


def _presence_path(node, slots):
    if not isinstance(node, dict) or set(node) != {'presence'}:
        return None
    ref = node['presence']
    if not isinstance(ref, dict) or set(ref) != {'ref'} or not isinstance(ref['ref'], list) or len(ref['ref']) < 2:
        raise ValueError('presence requires an optional record field')
    path = ref['ref']
    shape = _path_type(path, slots, frozenset())
    if not isinstance(shape, dict) or set(shape) != {'optional'}:
        raise ValueError('presence requires an optional record field')
    return tuple(path)


def _check(node, slots, refinements=frozenset()):
    if not isinstance(node, dict) or len(node) != 1:
        raise ValueError('invalid expression')
    kind, arg = next(iter(node.items()))
    if kind == 'ref':
        return _path_type(arg, slots, refinements)
    if kind == 'literal':
        if not isinstance(arg, dict) or set(arg) != {'type', 'value'} or not _type(arg['value'], arg['type']):
            raise ValueError('invalid literal')
        return arg['type']
    if kind == 'presence':
        _presence_path(node, slots)
        return 'boolean'
    if kind == 'and':
        if not isinstance(arg, list) or len(arg) < 2:
            raise ValueError('invalid conjunction')
        guards = {_presence_path(x, slots) for x in arg if isinstance(x, dict) and 'presence' in x}
        if any(_check(x, slots, refinements | (guards - {None})) != 'boolean' for x in arg):
            raise ValueError('conjunction requires predicates')
        return 'boolean'
    if kind == 'before':
        if not isinstance(arg, list) or len(arg) != 2 or any(
                _check(x, slots, refinements) != 'instant' for x in arg):
            raise ValueError('before requires two typed instants')
        return 'boolean'
    raise ValueError('unsupported expression')


def validate(contract):
    if not isinstance(contract, dict) or set(contract) != {'state', 'input', 'where'}:
        raise ValueError('invalid contract')
    state = contract['state']
    if not isinstance(state, dict) or set(state) != {'sequence'} or not isinstance(
            state['sequence'], dict) or set(state['sequence']) != {'record'}:
        raise ValueError('expected sequence of records')
    shape_valid(state)
    shape_valid(contract['input'])
    if _check(contract['where'], {'item': state['sequence'], 'input': contract['input']}) != 'boolean':
        raise ValueError('selection needs predicate')
    return contract


def _emit(node):
    kind, arg = next(iter(node.items()))
    if kind == 'ref':
        return arg[0] + ''.join('[' + repr(part) + ']' for part in arg[1:])
    if kind == 'literal':
        return repr(arg['value'])
    if kind == 'presence':
        path = arg['ref']
        parent = _emit({'ref': path[:-1]})
        return '(' + repr(path[-1]) + ' in ' + parent + ')'
    if kind == 'before':
        return '_before(' + ', '.join(_emit(part) for part in arg) + ')'
    if kind == 'and':
        # This order is a checked evaluation plan, not the relation's meaning.
        guards = [part for part in arg if 'presence' in part]
        rest = [part for part in arg if 'presence' not in part]
        return '(' + ' and '.join(_emit(part) for part in guards + rest) + ')'
    raise ValueError('unsupported expression')


def generate(contract):
    validate(contract)
    return '''"""Disposable R5.25 generated publication selection."""
import json
import sys
from pathlib import Path
from benchmark.semantic.typed_lowering_r5_12 import _type
from benchmark.semantic.capability_boundary_r5_22 import parse_instant

STATE = ''' + repr(contract['state']) + '''
INPUT = ''' + repr(contract['input']) + '''

def _before(left, right):
    return parse_instant(left) < parse_instant(right)

def execute(pre, input):
    if not _type(pre, STATE) or not _type(input, INPUT):
        raise ValueError('invalid typed values')
    return [item for item in pre if ''' + _emit(contract['where']) + ''']

if __name__ == '__main__':
    state, payload, trace = map(Path, sys.argv[1:4])
    pre = json.loads(state.read_bytes())
    inp = json.loads(payload.read_bytes())
    result = execute(pre, inp)
    trace.write_text(json.dumps({'pre': pre, 'input': inp, 'result': result,
                                 'post': pre, 'attempted_write': False}), encoding='utf-8')
    print(json.dumps(result))
'''


def conforms(contract, pre, inp, result, post):
    """Independent tuple checker for the deliberately narrow selection contract."""
    validate(contract)
    if not _type(pre, contract['state']) or not _type(inp, contract['input']):
        return False
    def value(node, row):
        kind, arg = next(iter(node.items()))
        if kind == 'ref':
            obj = {'item': row, 'input': inp}[arg[0]]
            for part in arg[1:]:
                obj = obj[part]
            return obj
        if kind == 'literal':
            return arg['value']
        if kind == 'presence':
            path = arg['ref']
            return path[-1] in value({'ref': path[:-1]}, row)
        if kind == 'before':
            return parse_instant(value(arg[0], row)) < parse_instant(value(arg[1], row))
        if kind == 'and':
            return all(value(x, row) for x in arg if 'presence' in x) and all(
                value(x, row) for x in arg if 'presence' not in x)
        raise ValueError('unsupported expression')
    expected = [row for row in pre if value(contract['where'], row)]
    return post == pre and result == expected
