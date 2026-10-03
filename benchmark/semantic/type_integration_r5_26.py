"""R5.26 prospective #45 read-only integration profile (not the R5.23 lock).

Presence eliminates optional<T> only inside its conjunction.  Ordering consumes
typed UTC instants via the existing instant parser; no new semantic relation is
introduced.  Generation and verification interpret the same checked source but
do not use each other's emitted algorithms.
"""

from collections import Counter
import json
from pathlib import Path

from benchmark.semantic import generative_r5_13 as base
from benchmark.semantic.capability_boundary_r5_22 import parse_instant, validate_logged
from benchmark.semantic.typed_lowering_r5_12 import _field, _type


ORDERABLE = ('string', 'integer', 'instant')


def _contains_order(node):
    if isinstance(node, dict):
        return 'order' in node or any(_contains_order(value) for value in node.values())
    return isinstance(node, list) and any(_contains_order(value) for value in node)


def _reference(node):
    if not isinstance(node, dict) or set(node) != {'ref'} or not isinstance(node['ref'], list):
        raise ValueError('presence needs a field reference')
    path = node['ref']
    if len(path) < 2 or any(type(part) is not str for part in path):
        raise ValueError('presence needs a field reference')
    return tuple(path)


def _declared(path, slots):
    if not path or path[0] not in slots:
        raise ValueError('invalid reference')
    shape = slots[path[0]]
    for part in path[1:]:
        shape = _field(shape, part)
    return shape


def _witness(node, slots):
    path = _reference(node['present'])
    shape = _declared(path, slots)
    if not isinstance(shape, dict) or set(shape) != {'optional'}:
        raise ValueError('presence requires optional field')
    return path


def _scope(node, slots):
    """Plan a conjunction as a relation set, not a left-to-right expression."""
    if not isinstance(node, list) or len(node) < 2:
        raise ValueError('conjunction needs predicates')
    witnesses = {_witness(part, slots) for part in node
                  if isinstance(part, dict) and set(part) == {'present'} }
    # Presence is scheduled before consumers; the serialized order is irrelevant.
    return [part for part in node if isinstance(part, dict) and set(part) == {'present'}] + [
        part for part in node if not (isinstance(part, dict) and set(part) == {'present'})], witnesses


def analyze(node, slots, refinements=frozenset()):
    if not isinstance(node, dict) or len(node) != 1:
        raise ValueError('invalid expression')
    kind, arg = next(iter(node.items()))
    if kind == 'ref':
        path = tuple(arg) if isinstance(arg, list) else ()
        shape = _declared(path, slots)
        if isinstance(shape, dict) and set(shape) == {'optional'} and path in refinements:
            return shape['optional']
        return shape
    if kind == 'literal':
        if not isinstance(arg, dict) or set(arg) != {'type', 'value'} or not _type(arg['value'], arg['type']):
            raise ValueError('invalid typed literal')
        return arg['type']
    if kind == 'present':
        _witness(node, slots)
        return 'boolean'
    if kind == 'and':
        planned, witnesses = _scope(arg, slots)
        if any(analyze(part, slots, refinements | witnesses) != 'boolean' for part in planned):
            raise ValueError('conjunction needs predicates')
        return 'boolean'
    if kind == 'not':
        if analyze(arg, slots, refinements) != 'boolean':
            raise ValueError('negation needs predicate')
        return 'boolean'
    if kind in ('equals', 'before'):
        if not isinstance(arg, list) or len(arg) != 2:
            raise ValueError(kind + ' needs two operands')
        left, right = (analyze(part, slots, refinements) for part in arg)
        if kind == 'before' and (left, right) != ('instant', 'instant'):
            raise ValueError('before requires two typed instants; optional operand needs in-scope presence')
        if kind == 'equals' and left != right:
            raise ValueError('equality type mismatch; optional operand needs in-scope presence')
        return 'boolean'
    if kind == 'select':
        if not isinstance(arg, dict) or set(arg) != {'source', 'where'}:
            raise ValueError('invalid selection')
        source = analyze(arg['source'], slots, refinements)
        if not isinstance(source, dict) or set(source) != {'sequence'}:
            raise ValueError('selection needs sequence')
        if analyze(arg['where'], {**slots, 'item': source['sequence']}) != 'boolean':
            raise ValueError('selection needs predicate')
        return source
    if kind == 'order':
        if isinstance(arg, dict) and _contains_order(arg.get('source')):
            raise base.UnsupportedLowering('UNSUPPORTED_R5_26_EXPRESSION: nested order')
        ordering_plan(arg, slots, refinements)
        return analyze(arg['source'], slots, refinements)
    if kind == 'cardinality':
        source = analyze(arg, slots, refinements)
        if not isinstance(source, dict) or set(source) != {'sequence'}:
            raise ValueError('cardinality needs sequence')
        return 'integer'
    raise base.UnsupportedLowering('UNSUPPORTED_R5_26_EXPRESSION: ' + kind)


def ordering_plan(node, slots, refinements=frozenset()):
    if not isinstance(node, dict) or set(node) != {'source', 'keys'} or not isinstance(node['keys'], list) or not node['keys']:
        raise ValueError('invalid ordering')
    source = analyze(node['source'], slots, refinements)
    if not isinstance(source, dict) or set(source) != {'sequence'}:
        raise ValueError('ordering needs sequence')
    element = source['sequence']
    guarded = set()
    selection = node['source'].get('select') if isinstance(node['source'], dict) else None
    if selection:
        where = selection['where']
        if isinstance(where, dict) and set(where) == {'and'}:
            _, guarded = _scope(where['and'], {**slots, 'item': element})
        elif isinstance(where, dict) and set(where) == {'present'}:
            guarded = {_witness(where, {**slots, 'item': element})}
    keys = []
    for key in node['keys']:
        if type(key) is not str:
            raise ValueError('invalid ordering key')
        shape = _field(element, key)
        if isinstance(shape, dict) and set(shape) == {'optional'} and ('item', key) in guarded:
            shape = shape['optional']
        if shape not in ORDERABLE:
            raise ValueError('non-orderable key; optional key needs selection presence')
        keys.append((key, shape))
    return {'element': element, 'keys': keys}


def typed(contract):
    if not isinstance(contract, dict) or set(contract) != {'id', 'version', 'input', 'state', 'branches'}:
        raise ValueError('invalid contract')
    if contract['version'] != 'R5.26' or type(contract['id']) is not str or not contract['id']:
        raise ValueError('R5.26 integration requires versioned identity')
    for shape in (contract['input'], contract['state']):
        base.shape_valid(shape)
    if not (isinstance(contract['input'], dict) and set(contract['input']) == {'record'} and
            isinstance(contract['state'], dict) and set(contract['state']) == {'sequence'} and
            isinstance(contract['state']['sequence'], dict) and set(contract['state']['sequence']) == {'record'}):
        raise base.UnsupportedLowering('UNSUPPORTED_R5_26_SHAPE')
    branches = contract['branches']
    if not isinstance(branches, list) or len(branches) < 2 or len({b['tag'] for b in branches}) != len(branches):
        raise ValueError('invalid branches')
    slots = {'input': contract['input'], 'pre': contract['state']}
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or set(branch) != {'tag', 'when', 'value', 'value_type', 'transition'}:
            raise ValueError('invalid branch')
        if (branch['when'] is None) != (index == len(branches) - 1):
            raise ValueError('only final branch unconditional')
        if branch['transition'] != {'preserve': True}:
            raise base.UnsupportedLowering('UNSUPPORTED_R5_26_TRANSITION: read-only profile')
        base.shape_valid(branch['value_type'])
        if branch['when'] is not None and analyze(branch['when'], slots) != 'boolean':
            raise ValueError('guard must be boolean')
        if ((branch['when'] is not None and _contains_order(branch['when'])) or
                (_contains_order(branch['value']) and 'order' not in branch['value'])):
            raise base.UnsupportedLowering('UNSUPPORTED_R5_26_EXPRESSION: nested order')
        if analyze(branch['value'], slots) != branch['value_type']:
            raise ValueError('outcome payload type mismatch')
    return contract


def _rank(row, keys):
    return tuple(parse_instant(row[key]) if shape == 'instant' else row[key] for key, shape in keys)


def evaluate(node, facts, slots):
    kind, arg = next(iter(node.items()))
    if kind == 'ref':
        value = facts[arg[0]]
        for part in arg[1:]:
            value = value[part]
        return value
    if kind == 'literal':
        return arg['value']
    if kind == 'present':
        path = _reference(arg)
        return path[-1] in evaluate({'ref': list(path[:-1])}, facts, slots)
    if kind == 'and':
        planned, _ = _scope(arg, slots)
        return all(evaluate(part, facts, slots) for part in planned)
    if kind == 'not':
        return not evaluate(arg, facts, slots)
    if kind == 'equals':
        return evaluate(arg[0], facts, slots) == evaluate(arg[1], facts, slots)
    if kind == 'before':
        return parse_instant(evaluate(arg[0], facts, slots)) < parse_instant(evaluate(arg[1], facts, slots))
    if kind == 'select':
        source = evaluate(arg['source'], facts, slots)
        item_shape = analyze(arg['source'], slots)['sequence']
        return [item for item in source if evaluate(arg['where'], {**facts, 'item': item}, {**slots, 'item': item_shape})]
    if kind == 'order':
        plan = ordering_plan(arg, slots)
        return sorted(evaluate(arg['source'], facts, slots), key=lambda row: _rank(row, plan['keys']))
    if kind == 'cardinality':
        return len(evaluate(arg, facts, slots))
    raise ValueError('unhandled expression')


def emit(node, slots, bindings=None, fault=None):
    bindings = {} if bindings is None else bindings
    kind, arg = next(iter(node.items()))
    if kind == 'ref':
        return bindings.get(arg[0], arg[0]) + ''.join('[' + repr(part) + ']' for part in arg[1:])
    if kind == 'literal':
        return repr(arg['value'])
    if kind == 'present':
        path = _reference(arg)
        return '(' + repr(path[-1]) + ' in ' + emit({'ref': list(path[:-1])}, slots, bindings) + ')'
    if kind == 'and':
        planned, _ = _scope(arg, slots)
        return '(' + ' and '.join(emit(part, slots, bindings, fault) for part in planned) + ')'
    if kind == 'not':
        return '(not ' + emit(arg, slots, bindings, fault) + ')'
    if kind == 'equals':
        return '(' + emit(arg[0], slots, bindings, fault) + ' == ' + emit(arg[1], slots, bindings, fault) + ')'
    if kind == 'before':
        return 'instant_lt(' + ', '.join(emit(part, slots, bindings, fault) for part in arg) + ')'
    if kind == 'select':
        name = '_element_' + str(len(bindings))
        source_type = analyze(arg['source'], slots)['sequence']
        where = emit(arg['where'], {**slots, 'item': source_type}, {**bindings, 'item': name}, fault)
        if fault == 'absent':
            # Inject a wrong population member without dereferencing its absent field.
            where = '((' + where + ') or ' + repr(_first_guarded(arg['where'])) + ' not in ' + name + ')'
        return '[' + name + ' for ' + name + ' in ' + emit(arg['source'], slots, bindings, fault) + ' if ' + where + ']'
    if kind == 'order':
        plan = ordering_plan(arg, slots)
        name = '_order_key_' + str(len(bindings))
        keys = plan['keys']
        rank = ', '.join(('datetime.fromisoformat(' + name + '[' + repr(key) + '][:-1] + "+00:00")' if shape == 'instant' else
                          name + '[' + repr(key) + ']') for key, shape in keys) + ','
        call = 'sorted(' + emit(arg['source'], slots, bindings, fault) + ', key=lambda ' + name + ': (' + rank + '))'
        return 'list(reversed(' + call + '))' if fault == 'reverse' else call
    if kind == 'cardinality':
        return 'len(' + emit(arg, slots, bindings, fault) + ')'
    raise ValueError('unhandled expression')


def _first_guarded(where):
    relations = where['and'] if 'and' in where else [where]
    for part in relations:
        if 'present' in part:
            return _reference(part['present'])[-1]
    raise ValueError('fault needs presence')


def render(contract, fault=None):
    typed(contract)
    slots = {'input': contract['input'], 'pre': contract['state']}
    lines = ['# R5.26 disposable generated read-only operation.',
             'from generative_runtime_r5_13 import run, instant_lt',
             'from datetime import datetime',
             '', 'def execute(input, pre):']
    for index, branch in enumerate(contract['branches']):
        condition = ('else:' if branch['when'] is None else
                     ('if ' if index == 0 else 'elif ') + emit(branch['when'], slots) + ':')
        lines.append('    ' + condition)
        lines.append('        post = pre')
        lines.append('        return {"kind": ' + repr(branch['tag']) + ', "value": ' +
                     emit(branch['value'], slots, fault=fault) + '}, post, False')
    lines.extend(['', 'if __name__ == "__main__":',
                  '    run(execute, ' + repr(contract['input']) + ', ' + repr(contract['state']) + ', ' +
                  repr({b['tag']: b['value_type'] for b in contract['branches']}) + ')', ''])
    return '\n'.join(lines).encode()


def generate(contract, directory, fault=None):
    root = Path(directory)
    artifact = render(contract, fault)
    runtime = base.RUNTIME.read_bytes()
    identity = base.sha(base.canonical(contract))
    (root / 'operation.py').write_bytes(artifact)
    (root / base.RUNTIME.name).write_bytes(runtime)
    manifest = {'contract': identity, 'id': contract['id'], 'version': contract['version'],
                'artifact': base.sha(artifact), 'runtime': base.sha(runtime),
                'generation': base.sha(base.canonical([identity, base.sha(artifact), base.sha(runtime)]))}
    (root / 'provenance.json').write_bytes(base.canonical(manifest))
    return manifest


def _ordered_holds(order, facts, slots, actual):
    plan = ordering_plan(order, slots)
    source = evaluate(order['source'], facts, slots)
    if not _type(actual, {'sequence': plan['element']}):
        return False
    if Counter(map(base.canonical, source)) != Counter(map(base.canonical, actual)):
        return False
    ranks = [_rank(row, plan['keys']) for row in actual]
    return ranks == sorted(ranks)


def conforms(contract, inp, pre, outcome, post, bytes_equal, attempted_write, external=None):
    typed(contract)
    if not (_type(inp, contract['input']) and _type(pre, contract['state']) and
            _type(post, contract['state']) and isinstance(outcome, dict) and set(outcome) == {'kind', 'value'} and
            post == pre and bytes_equal and not attempted_write):
        return False
    slots = {'input': contract['input'], 'pre': contract['state']}
    facts = {'input': inp, 'pre': pre}
    branch = next(b for b in contract['branches'] if b['when'] is None or evaluate(b['when'], facts, slots))
    if outcome['kind'] != branch['tag'] or not _type(outcome['value'], branch['value_type']):
        return False
    value = branch['value']
    if 'order' in value:
        return _ordered_holds(value['order'], facts, slots, outcome['value'])
    return outcome['value'] == evaluate(value, facts, slots)


def challenge(contract, directory, internal, public, before, after):
    """R5.26 observer challenge, with its own versioned semantic verifier."""
    root = Path(directory)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    expected = {'contract': base.sha(base.canonical(contract)), 'id': contract['id'],
                'version': contract['version'], 'artifact': base.sha((root / 'operation.py').read_bytes()),
                'runtime': base.sha((root / base.RUNTIME.name).read_bytes())}
    integrity = (all(manifest.get(k) == v for k, v in expected.items()) and
                 expected['runtime'] == base.sha(base.RUNTIME.read_bytes()) and
                 manifest.get('generation') == base.sha(base.canonical([
                     expected['contract'], expected['artifact'], expected['runtime']])))
    verdict = {'provenance_valid': integrity, 'grounded': False, 'conformant': None}
    if not integrity:
        return verdict
    try:
        visible = json.loads(public['stdout'])
        grounded = (public['exit'] == 0 and public['stderr'] == '' and
                    internal['generation'] == manifest['generation'] and
                    internal['invocation'] == public['invocation'] and
                    internal['input'] == public['input'] and
                    internal['pre'] == json.loads(before) and
                    internal['post'] == json.loads(after) and
                    internal['outcome'] == visible and
                    type(internal['attempted_write']) is bool and
                    (internal['attempted_write'] or before == after) and
                    validate_logged(internal.get('externals', {})))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return verdict
    if grounded:
        verdict['grounded'] = True
        verdict['conformant'] = conforms(contract, public['input'], json.loads(before),
                                        visible, json.loads(after), before == after,
                                        internal['attempted_write'], internal.get('externals', {}))
    return verdict
