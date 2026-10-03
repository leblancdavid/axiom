"""Prospective bounded #45 generator; contract data drives disposable target code.

Record input and sequence-of-record state; checked expressions, guarded typed
outcomes and bounded preserve/replace/default transitions. The final branch is
unconditional. Unsupported relational compositions reject explicitly.
"""

import hashlib
import json
from pathlib import Path

from benchmark.semantic.typed_lowering_r5_12 import _compile, UnsupportedLowering


RUNTIME = Path(__file__).with_name('generative_runtime_r5_13.py')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def shape_valid(shape):
    if shape in ('string', 'integer', 'boolean'):
        return
    if isinstance(shape, dict) and set(shape) in ({'sequence'}, {'optional'}, {'nullable'}):
        shape_valid(next(iter(shape.values())))
        return
    if isinstance(shape, dict) and set(shape) == {'record'} and isinstance(shape['record'], dict):
        for name, child in shape['record'].items():
            if type(name) is not str:
                raise ValueError('invalid field name')
            shape_valid(child)
        return
    raise ValueError('invalid type declaration')


def typed(contract):
    if not isinstance(contract, dict) or set(contract) != {'id', 'version', 'input', 'state', 'branches'}:
        raise ValueError('invalid contract')
    if not all(type(contract[k]) is str and contract[k] for k in ('id', 'version')):
        raise ValueError('invalid identity')
    inp, state = contract['input'], contract['state']
    if not (isinstance(inp, dict) and set(inp) == {'record'} and
            isinstance(state, dict) and (set(state) == {'sequence'} and
            isinstance(state['sequence'], dict) and set(state['sequence']) == {'record'} or
            set(state) == {'record'})):
        raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state/input shape')
    for shape in (inp, state):
        shape_valid(shape)
    branches = contract['branches']
    if not isinstance(branches, list) or len(branches) < 2:
        raise ValueError('branches require guards and final otherwise')
    slots = {'input': inp, 'pre': state}
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or set(branch) not in (
                {'tag', 'when', 'value', 'transition'},
                {'tag', 'when', 'value', 'value_type', 'transition'}):
            raise ValueError('invalid branch')
        if type(branch['tag']) is not str or not branch['tag']:
            raise ValueError('invalid tag')
        if (branch['when'] is None) != (index == len(branches) - 1):
            raise ValueError('only final branch is unconditional')
        if branch['when'] is not None and _compile(branch['when'], slots)[0] != 'boolean':
            raise ValueError('guard must be boolean')
        payload_type = branch.get('value_type', 'string')
        shape_valid(payload_type)
        if _compile(branch['value'], slots)[0] != payload_type:
            raise ValueError('outcome payload type mismatch')
        transition = branch['transition']
        if transition == {'preserve': True}:
            continue
        if isinstance(transition, dict) and set(transition) == {'relations'}:
            _relational(transition['relations'], state, slots)
            continue
        if set(state) != {'sequence'}:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        if isinstance(transition, dict) and set(transition) == {'default_missing'}:
            rule = transition['default_missing']
            if not isinstance(rule, dict) or set(rule) != {'identity', 'field', 'value'}:
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation (default_missing shape)')
            fields = state['sequence']['record']
            if (rule['identity'] == rule['field'] or fields.get(rule['identity']) != 'string' or
                    not isinstance(fields.get(rule['field']), dict) or
                    set(fields[rule['field']]) != {'optional'} or
                    fields[rule['field']]['optional'] not in ('string', 'boolean')):
                raise ValueError('invalid default identity or optional field')
            if (not isinstance(rule['value'], dict) or set(rule['value']) != {'literal'} or
                    _compile(rule['value'], slots)[0] != fields[rule['field']]['optional']):
                raise ValueError('incompatible default')
            continue
        if not isinstance(transition, dict) or set(transition) != {'replace_field'}:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        update = transition['replace_field']
        if not isinstance(update, dict) or set(update) != {'key', 'match', 'field', 'value'}:
            raise ValueError('invalid replacement')
        fields = state['sequence']['record']
        if update['key'] not in fields or update['field'] not in fields:
            raise ValueError('invalid state field')
        if _compile(update['match'], slots)[0] != fields[update['key']]:
            raise ValueError('key type mismatch')
        if _compile(update['value'], slots)[0] != fields[update['field']]:
            raise ValueError('assignment type mismatch')
    if len({b['tag'] for b in branches}) != len(branches):
        raise ValueError('duplicate outcome tag')
    return contract


def _relational(relations, state, slots):
    """Check a bounded conjunction of existing exact frame/default/equality relations.

    A relation has no operation name. Its collection path is storage binding
    metadata; the equality target is a typed post-state field projection.
    """
    if not isinstance(relations, list) or not relations:
        raise ValueError('missing state relations')
    collection_changes = {}
    scalar_changes = set()
    defaults = {}
    planned = []
    for relation in relations:
        if not isinstance(relation, dict) or len(relation) != 1:
            raise ValueError('invalid state relation')
        kind, rule = next(iter(relation.items()))
        if kind not in ('exact_frame', 'default_missing', 'post_equals'):
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        if not isinstance(rule, dict):
            raise ValueError('invalid state relation parameters')
        if kind == 'post_equals':
            if set(rule) != {'field', 'value'} or set(state) != {'record'}:
                raise ValueError('invalid post equality')
            field = rule['field']
            if field in scalar_changes or field in collection_changes or _compile(rule['value'], slots)[0] != state['record'].get(field):
                raise ValueError('invalid post equality field or type')
            scalar_changes.add(field)
            planned.append(relation)
            continue
        expected = {'collection', 'identity', 'record'} if kind == 'exact_frame' else {'collection', 'identity', 'field', 'value'}
        if set(rule) != expected:
            raise ValueError('invalid collection relation')
        name = rule['collection']
        collection = state if name is None and set(state) == {'sequence'} else (
            state['record'].get(name) if set(state) == {'record'} and type(name) is str else None)
        if not isinstance(collection, dict) or set(collection) != {'sequence'} or not isinstance(collection['sequence'], dict) or set(collection['sequence']) != {'record'}:
            raise ValueError('invalid collection projection')
        fields = collection['sequence']['record']
        identity = rule['identity']
        if fields.get(identity) != 'string' or name in scalar_changes:
            raise ValueError('invalid identity')
        # A frame or a default maps each collection once; no implicit order of
        # multiple noncommuting transforms is inferred from a relation list.
        if kind == 'exact_frame':
            if _compile(rule['record'], slots)[0] != collection['sequence']:
                raise ValueError('framed record type mismatch')
            if name in collection_changes:
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations')
            collection_changes[name] = (kind, identity)
            planned.append(relation)
        else:
            field = rule['field']
            owner = collection_changes.get(name)
            if owner is not None and owner != ('default_missing', identity):
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations')
            if (field == identity or not isinstance(fields.get(field), dict) or
                    set(fields[field]) != {'optional'} or
                    _compile(rule['value'], slots)[0] != fields[field]['optional']):
                raise ValueError('invalid default field or type')
            collection_changes[name] = ('default_missing', identity)
            key = (name, field)
            previous = defaults.get(key)
            if previous is not None:
                if canonical(previous['value']) == canonical(rule['value']):
                    continue  # identical relation is idempotent
                if 'literal' in previous['value'] and 'literal' in rule['value']:
                    raise ValueError('CONFLICTING_RELATIONS: incompatible defaults for one field')
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: unresolved default equivalence')
            defaults[key] = rule
    # Collection plans are sorted by typed projection and field, not serialization
    # order. Expressions are bound only to input/pre, so disjoint defaults commute.
    planned.extend({'default_missing': defaults[key]} for key in sorted(
        defaults, key=lambda key: ('' if key[0] is None else key[0], key[1])))
    return planned


def expression(expr, bindings=None):
    """Emit only checked expression nodes; no code fragments from contract strings."""
    bindings = {} if bindings is None else bindings
    kind, arg = next(iter(expr.items()))
    if kind == 'ref':
        return bindings.get(arg[0], arg[0]) + ''.join('[' + repr(part) + ']' for part in arg[1:])
    if kind == 'literal':
        return repr(arg['value'])
    if kind == 'equals':
        return '(' + expression(arg[0], bindings) + ' == ' + expression(arg[1], bindings) + ')'
    if kind == 'and':
        return '(' + ' and '.join(expression(e, bindings) for e in arg) + ')'
    if kind == 'not':
        return '(not ' + expression(arg, bindings) + ')'
    if kind == 'select':
        name = '_element_' + str(len(bindings))
        return ('[' + name + ' for ' + name + ' in ' + expression(arg['source'], bindings) +
                ' if ' + expression(arg['where'], {**bindings, 'item': name}) + ']')
    if kind == 'cardinality':
        return 'len(' + expression(arg, bindings) + ')'
    if kind == 'record':
        return '{' + ', '.join(repr(k) + ': ' + expression(v, bindings) for k, v in arg.items()) + '}'
    if kind == 'trim':
        return '(' + expression(arg, bindings) + ').strip()'
    if kind == 'map':
        name = '_element_' + str(len(bindings))
        return '[' + name + '.strip() for ' + name + ' in ' + expression(arg['sequence'], bindings) + ']'
    if kind == 'stable_unique':
        return 'list(dict.fromkeys(' + expression(arg['sequence'], bindings) + '))'
    if kind == 'nonblank':
        return 'bool((' + expression(arg, bindings) + ').strip())'
    if kind == 'for_each':
        name = '_bound_' + str(len(bindings))
        return ('all(' + expression(arg['property'], {**bindings, arg['bind']: name}) +
                ' for ' + name + ' in ' + expression(arg['sequence'], bindings) + ')')
    raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: ' + kind)


def render(contract, fault=False):
    typed(contract)
    lines = ['# Disposable generated program; regenerate from semantic contract.',
             'from generative_runtime_r5_13 import run', '',
             'def execute(input, pre):']
    for index, branch in enumerate(contract['branches']):
        condition = 'if ' + expression(branch['when']) + ':' if index == 0 else (
            'elif ' + expression(branch['when']) + ':' if branch['when'] is not None else 'else:')
        lines.append('    ' + condition)
        transition = branch['transition']
        if transition == {'preserve': True}:
            lines.extend(['        post = pre', '        write = False'])
        elif 'relations' in transition:
            lines.extend(['        post = pre', '        write = True'])
            for relation in _relational(transition['relations'], contract['state'],
                                        {'input': contract['input'], 'pre': contract['state']}):
                kind, rule = next(iter(relation.items()))
                if kind == 'post_equals':
                    lines.append('        post = {**post, ' + repr(rule['field']) + ': ' + expression(rule['value']) + '}')
                    continue
                name = rule['collection']
                source = 'post' if name is None else 'post[' + repr(name) + ']'
                key = repr(rule['identity'])
                lines.extend(['        if len({row[' + key + '] for row in ' + source + '}) != len(' + source + '):',
                              '            raise ValueError("duplicate identity")'])
                if kind == 'exact_frame':
                    lines.extend(['        _new = ' + expression(rule['record']),
                                  '        if _new[' + key + '] in {row[' + key + '] for row in ' + source + '}:',
                                  '            raise ValueError("identity not fresh")',
                                  '        _rows = [*' + source + ', _new]'])
                else:
                    field = repr(rule['field'])
                    lines.append('        _rows = [{**item, ' + field + ': ' + expression(rule['value']) +
                                 '} if ' + field + ' not in item else item for item in ' + source + ']')
                lines.append('        post = _rows' if name is None else
                             '        post = {**post, ' + repr(name) + ': _rows}')
        elif 'default_missing' in transition:
            rule = transition['default_missing']
            identity, field = repr(rule['identity']), repr(rule['field'])
            lines.extend(['        if len({row[' + identity + '] for row in pre}) != len(pre):',
                          '            raise ValueError("duplicate identity")',
                          '        post = [{**item, ' + field + ': ' + expression(rule['value']) +
                          '} if ' + field + ' not in item else item for item in pre]',
                          '        write = True'])
        else:
            update = transition['replace_field']
            key, field = repr(update['key']), repr(update['field'])
            match, value = expression(update['match']), expression(update['value'])
            # Disposable injected compiler fault: wrong replacement value, never alter semantics.
            if fault:
                value = 'item[' + field + ']'
            lines.extend(['        post = [{**item, ' + field + ': ' + value + '} if item[' + key +
                          '] == ' + match + ' else item for item in pre]',
                          '        write = True'])
        lines.append('        return {"kind": ' + repr(branch['tag']) + ', "value": ' +
                     expression(branch['value']) + '}, post, write')
    lines.extend(['', 'if __name__ == "__main__":',
                   '    run(execute, ' + repr(contract['input']) + ', ' +
                   repr(contract['state']) + ', ' +
                   repr({b['tag']: b.get('value_type', 'string') for b in contract['branches']}) + ')', ''])
    return '\n'.join(lines).encode()


def generate(contract, directory, fault=False):
    """Fault variant is a disposable lowering experiment, excluded from normal generation."""
    directory = Path(directory)
    artifact = render(contract, fault)
    runtime = RUNTIME.read_bytes()
    identity = sha(canonical(contract))
    (directory / 'operation.py').write_bytes(artifact)
    (directory / RUNTIME.name).write_bytes(runtime)
    manifest = {'contract': identity, 'id': contract['id'], 'version': contract['version'],
                'artifact': sha(artifact), 'runtime': sha(runtime),
                'generation': sha(canonical([identity, sha(artifact), sha(runtime)]))}
    (directory / 'provenance.json').write_bytes(canonical(manifest))
    return manifest
