"""Prospective R5.28 checked-plan generator fork of the R5.23 general emitter.

Record input and sequence-of-record state; checked expressions, guarded typed
outcomes and bounded preserve/replace/default transitions. Typed ordering emits
only from a canonical ordering plan of required string/integer keys; the key
sequence is semantic. The final branch is unconditional. Unsupported relational
compositions reject explicitly.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from benchmark.semantic.capability_boundary_r5_22 import capability_type
from benchmark.semantic.typed_lowering_r5_12 import _compile, _field, UnsupportedLowering


RUNTIME = Path(__file__).with_name('refined_runtime_r5_28.py')
# A disposable injected-lowering fault marker for an external string identity;
# it faithfully executes but never matches the value the provider persisted.
_STALE_IDENTITY = '__injected_stale_identity__'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def shape_valid(shape):
    if shape in ('string', 'integer', 'boolean', 'instant'):
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
    value_slots = {'input': inp, 'pre': state, 'post': state}
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
        if _compile(branch['value'], value_slots)[0] != payload_type:
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


def _relational(relations, state, slots, plan=None):
    """Check a bounded conjunction of existing frame/default/replace/remove/equality relations.

    A relation has no operation name. Its collection path is storage binding
    metadata; the equality target is a typed post-state field projection. Each
    collection is touched by at most one non-defaulting transform, and multiple
    compatible keyed defaults commute because expressions bind only to input/pre.
    """
    if not isinstance(relations, list) or not relations:
        raise ValueError('missing state relations')

    def resolve(name):
        collection = state if name is None and set(state) == {'sequence'} else (
            state['record'].get(name) if set(state) == {'record'} and type(name) is str else None)
        if (not isinstance(collection, dict) or set(collection) != {'sequence'} or
                not isinstance(collection['sequence'], dict) or
                set(collection['sequence']) != {'record'}):
            raise ValueError('invalid collection projection')
        return collection, collection['sequence']['record']

    single_transform = {'exact_frame', 'replace_field', 'remove'}
    collection_changes = {}
    scalar_changes = set()
    defaults = {}
    planned = []
    def operand(expr):
        return plan.operand_type(expr) if plan is not None else _compile(expr, slots)[0]
    for relation in relations:
        if not isinstance(relation, dict) or len(relation) != 1:
            raise ValueError('invalid state relation')
        kind, rule = next(iter(relation.items()))
        if kind not in single_transform | {'default_missing', 'post_equals'}:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        if not isinstance(rule, dict):
            raise ValueError('invalid state relation parameters')
        if kind == 'post_equals':
            if set(rule) != {'field', 'value'} or set(state) != {'record'}:
                raise ValueError('invalid post equality')
            field = plan.bindings[id(relation)]['field'][0] if plan is not None else rule['field']
            if field in scalar_changes or field in collection_changes or (plan is None and operand(rule['value']) != state['record'].get(field)):
                raise ValueError('invalid post equality field or type')
            scalar_changes.add(field)
            planned.append(relation)
            continue
        expected = {'exact_frame': {'collection', 'identity', 'record'},
                    'default_missing': {'collection', 'identity', 'field', 'value'},
                    'replace_field': {'collection', 'key', 'match', 'field', 'value'},
                    'remove': {'collection', 'identity', 'match'}}[kind]
        if set(rule) != expected:
            raise ValueError('invalid collection relation')
        name = rule['collection']
        if plan is not None:
            binding = plan.bindings[id(relation)]
            collection, fields = binding['type'], binding['fields']
            identity = binding['identity'][0]
        else:
            collection, fields = resolve(name)
            identity = rule.get('identity', rule.get('key'))
        if (plan is None and fields.get(identity) != 'string') or name in scalar_changes:
            raise ValueError('invalid identity')
        if kind in single_transform:
            if plan is None and operand(rule.get('match', rule.get('record'))) != (
                    collection['sequence'] if kind == 'exact_frame' else fields[identity]):
                if kind == 'exact_frame':
                    raise ValueError('framed record type mismatch')
                raise ValueError('key type mismatch')
            if kind == 'replace_field' and plan is None:
                if rule['field'] not in fields or operand(rule['value']) != fields[rule['field']]:
                    raise ValueError('invalid replacement field or type')
            if name in collection_changes:
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations')
            collection_changes[name] = (kind, identity)
            planned.append(relation)
        else:
            field = rule['field']
            owner = collection_changes.get(name)
            if owner is not None and owner != ('default_missing', identity):
                raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations')
            if plan is None and (field == identity or not isinstance(fields.get(field), dict) or
                    set(fields[field]) != {'optional'} or
                    operand(rule['value']) != fields[field]['optional']):
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
    original_relations = {id(next(iter(relation.values()))): relation for relation in relations}
    planned.extend(original_relations[id(defaults[key])] for key in sorted(
        defaults, key=lambda key: ('' if key[0] is None else key[0], key[1])))
    return planned


ORDER_KEY_TYPES = ('string', 'integer')


def ordering_plan(node, slots):
    """Canonical target-independent plan for the existing typed ordering relation.

    The key sequence is semantic and is never sorted or deduplicated. Direction
    is not represented by the existing relation, so the plan carries only
    ascending lexicographic comparison over required string/integer fields.
    Validation mirrors the locked interpreting lowerer exactly; results contain
    no target-language constructs.
    """
    if not isinstance(node, dict) or set(node) != {'source', 'keys'} or (
            not isinstance(node['keys'], list) or not node['keys']):
        raise ValueError('invalid ordering')
    source = _compile(node['source'], slots)[0]
    if not isinstance(source, dict) or set(source) != {'sequence'}:
        raise ValueError('ordering needs a sequence')
    keys = []
    for key in node['keys']:
        if type(key) is not str:
            raise ValueError('invalid ordering key')
        field = _field(source['sequence'], key)
        if field not in ORDER_KEY_TYPES:
            raise ValueError('non-orderable key')
        keys.append((key, field))
    return {'element': source['sequence'], 'keys': keys}


def expression(expr, bindings=None, slots=None, fault=False, plan=None):
    """Emit only checked expression nodes; no code fragments from contract strings."""
    bindings = {} if bindings is None else bindings
    if plan is not None:
        plan.operand_type(expr)
    kind, arg = next(iter(expr.items()))
    if plan is not None and plan.facts[id(expr)]['kind'] != kind:
        raise ValueError('compiler internal consistency failure: emitter node kind')
    def emit(node, env=bindings):
        return expression(node, env, slots, fault, plan)
    def reference(path):
        return bindings.get(path[0], path[0]) + ''.join('[' + repr(part) + ']' for part in path[1:])
    if kind == 'present':
        if plan is None:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: present')
        path = arg['ref']
        return '(' + repr(path[-1]) + ' in ' + reference(path[:-1]) + ')'
    if kind == 'ref':
        return reference(plan.facts[id(expr)]['field'] if plan is not None else arg)
    if kind == 'literal':
        return repr(arg['value'])
    if kind == 'equals':
        return '(' + emit(arg[0]) + ' == ' + emit(arg[1]) + ')'
    if kind == 'and':
        if plan is not None:
            dependencies = plan.scopes.get(id(expr), ())
            guarded = {producer for _, producer in dependencies}
            arg = [e for e in arg if id(e) in guarded] + [e for e in arg if id(e) not in guarded]
        return '(' + ' and '.join(emit(e) for e in arg) + ')'
    if kind == 'not':
        return '(not ' + emit(arg) + ')'
    if kind == 'select':
        name = '_element_' + str(len(bindings))
        return ('[' + name + ' for ' + name + ' in ' + emit(arg['source']) +
                ' if ' + emit(arg['where'], {**bindings, 'item': name}) + ']')
    if kind == 'cardinality':
        return 'len(' + emit(arg) + ')'
    if kind == 'record':
        parts = []
        for key, value in arg.items():
            if plan is not None and id(value) in plan.optional_record_fields:
                path = value['ref']
                parent = reference(path[:-1])
                parts.append('**({' + repr(key) + ': ' + emit(value) + '} if ' +
                             repr(path[-1]) + ' in ' + parent + ' else {})')
            else:
                parts.append(repr(key) + ': ' + emit(value))
        return '{' + ', '.join(parts) + '}'
    if kind == 'trim':
        return '(' + emit(arg) + ').strip()'
    if kind == 'map':
        name = '_element_' + str(len(bindings))
        return ('[' + name + '.strip() for ' + name + ' in ' + emit(arg['sequence']) + ']')
    if kind == 'stable_unique':
        return 'list(dict.fromkeys(' + emit(arg['sequence']) + '))'
    if kind == 'nonblank':
        return 'bool((' + emit(arg) + ').strip())'
    if kind == 'for_each':
        name = '_bound_' + str(len(bindings))
        return ('all(' + emit(arg['property'], {**bindings, arg['bind']: name}) +
                ' for ' + name + ' in ' + emit(arg['sequence']) + ')')
    if kind == 'order':
        # The existing relation orders contract-slot collections only; ordering a
        # quantifier-local binding has no checked interpretation here and rejects.
        if slots is None or (isinstance(arg.get('source'), dict) and 'ref' in arg['source'] and
                             arg['source']['ref'][0] not in slots):
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: order (scoped source)')
        order_plan = plan.orders[id(expr)] if plan is not None else ordering_plan(arg, slots)
        keys = order_plan['keys']
        # Disposable injected lowering faults: drop secondary keys, or reverse a
        # single-key plan. They faithfully execute a wrong typed permutation.
        if fault and len(keys) > 1:
            keys = keys[:1]
        name = '_order_key_' + str(len(bindings))
        projected = ', '.join(('instant_key(' + name + '[' + repr(key) + '])' if shape == 'instant' else
                               name + '[' + repr(key) + ']') for key, shape in keys) + ','
        call = ('sorted(' + emit(arg['source']) +
                 ', key=lambda ' + name + ': (' + projected + '))')
        return 'list(reversed(' + call + '))' if fault and len(order_plan['keys']) == 1 else call
    if kind == 'external':
        shape = plan.operand_type(expr) if plan is not None else capability_type(arg['source'])
        if fault and shape == 'string':
            return repr(_STALE_IDENTITY)
        return 'EXTERNAL[' + repr(arg['source']) + ']'
    if kind == 'fallback':
        if fault:
            # Disposable injected lowering fault: ignore an explicitly present input and
            # always emit the fallback value. Faithfully grounded, contract-violating.
            return expression(arg['default'], bindings, slots, fault, plan)
        path = arg['value']['ref']
        parent = reference(path[:-1])
        return '(' + expression(arg['default'], bindings, slots, fault, plan) + ' if ' + repr(path[-1]) + \
                ' not in ' + parent + ' else ' + expression(arg['value'], bindings, slots, fault, plan) + ')'
    if kind == 'before':
        return 'instant_lt(' + emit(arg[0]) + ', ' + emit(arg[1]) + ')'
    if kind == 'sole':
        return 'sole(' + emit(arg) + ')'
    if kind == 'project':
        fields = [name for name, _ in plan.projections[id(expr)]] if plan is not None else arg['fields']
        return 'project(' + emit(arg['row']) + ', [' + \
               ', '.join(repr(name) for name in fields) + '])'
    raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: ' + kind)


@dataclass(frozen=True)
class GeneratedUnit:
    identity: str
    contract_digest: str
    declaration: tuple
    input_shape: dict
    outcome_shapes: dict
    state_shape: dict
    capability_shapes: dict
    imports: tuple = ('instant_key', 'instant_lt', 'project', 'sole')
    post_shape: dict = None
    applicability: tuple = ()


def evolution_lines(relations, slots, plan):
    """Construct only completely checked target projections from semantic #44."""
    root = plan.slots['post']
    lines = ['        post = {}' if set(root) == {'record'} else '        post = []',
             '        write = True']
    initialized = set()
    for relation in relations:
        kind, rule = next(iter(relation.items()))
        binding = plan.bindings[id(relation)]
        if kind == 'post_equals':
            lines.append('        post[' + repr(binding['target'][1]) + '] = ' + expression(rule['value'], slots=slots, plan=plan))
            continue
        path = binding['target'][1:]
        source = 'pre' + ''.join('[' + repr(p) + ']' for p in binding['source'][1:])
        target = 'post' + ''.join('[' + repr(p) + ']' for p in path)
        identity, field = repr(binding['identity'][0]), repr(binding['field'][0])
        if path not in initialized:
            lines.extend(['        if len({row[' + identity + '] for row in ' + source + '}) != len(' + source + '):',
                          '            raise ValueError("duplicate identity")',
                          '        ' + target + ' = ' + source])
            initialized.add(path)
        lines.append('        ' + target + ' = [{**item, ' + field + ': ' + expression(rule['value'], slots=slots, plan=plan) +
                     '} if ' + field + ' not in item else item for item in ' + target + ']')
    return lines


def generated_unit(contract, plan, symbol='execute', fault=False):
    """Lower one checked operation into a structured declaration, not a file."""
    if plan.contract is not contract:
        raise ValueError('typed plan belongs to another contract')
    plan.assert_invariants()
    slots = {name: plan.slots[name] for name in ('input', 'pre')}
    value_slots = plan.slots
    lines = [f'def {symbol}(input, pre):']
    for index, branch in enumerate(contract['branches']):
        condition = 'if ' + expression(branch['when'], slots=slots, plan=plan) + ':' if index == 0 else (
            'elif ' + expression(branch['when'], slots=slots, plan=plan) + ':' if branch['when'] is not None else 'else:')
        lines.append('    ' + condition)
        transition = branch['transition']
        if transition == {'preserve': True}:
            lines.extend(['        post = pre', '        write = False'])
        elif 'relations' in transition:
            if id(branch) in plan.evolutions:
                lines.extend(evolution_lines(plan.relations[id(branch)], slots, plan))
                lines.append('        return {"kind": ' + repr(branch['tag']) + ', "value": ' +
                             expression(branch['value'], {'post': 'post'}, value_slots, fault, plan) + '}, post, write')
                continue
            lines.extend(['        post = pre', '        write = True'])
            for relation in plan.relations[id(branch)]:
                kind, rule = next(iter(relation.items()))
                binding = plan.bindings[id(relation)]
                if kind == 'post_equals':
                    lines.append('        post = {**post, ' + repr(binding['field'][0]) + ': ' + expression(rule['value'], slots=slots, plan=plan) + '}')
                    continue
                name = binding['target'][1] if len(binding['target']) > 1 else None
                source = 'post' if name is None else 'post[' + repr(name) + ']'
                identity = repr(binding['identity'][0])
                lines.extend(['        if len({row[' + identity + '] for row in ' + source + '}) != len(' + source + '):',
                              '            raise ValueError("duplicate identity")'])
                if kind == 'exact_frame':
                    lines.extend(['        _new = ' + expression(rule['record'], slots=slots, plan=plan),
                                  '        if _new[' + identity + '] in {row[' + identity + '] for row in ' + source + '}:',
                                  '            raise ValueError("identity not fresh")',
                                  '        _rows = [*' + source + ', _new]'])
                elif kind == 'remove':
                    match = expression(rule['match'], slots=slots, plan=plan)
                    lines.append('        _rows = ' + source + '[1:]' if fault else
                                 '        _rows = [item for item in ' + source +
                                 ' if item[' + identity + '] != ' + match + ']')
                elif kind == 'replace_field':
                    field = repr(binding['field'][0])
                    match, value = expression(rule['match'], slots=slots, plan=plan), expression(rule['value'], slots=slots, plan=plan)
                    value = 'item[' + field + ']' if fault else value
                    lines.append('        _rows = [{**item, ' + field + ': ' + value +
                                 '} if item[' + identity + '] == ' + match + ' else item for item in ' + source + ']')
                else:
                    field = repr(binding['field'][0])
                    lines.append('        _rows = [{**item, ' + field + ': ' + expression(rule['value'], slots=slots, plan=plan) +
                                 '} if ' + field + ' not in item else item for item in ' + source + ']')
                lines.append('        post = _rows' if name is None else
                             '        post = {**post, ' + repr(name) + ': _rows}')
        else:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: current transition')
        lines.append('        return {"kind": ' + repr(branch['tag']) + ', "value": ' +
                     expression(branch['value'], {'post': 'post'}, value_slots, fault, plan) + '}, post, write')
    applicability = ()
    if plan.applicability is not None:
        applicability = (f'def {symbol}_applicable(input, pre):',
                         '    return ' + expression(contract['requires'], slots=slots, plan=plan))
    return GeneratedUnit(contract['id'], plan.digest, tuple(lines), plan.slots['input'],
                         plan.outcomes, plan.slots['pre'], plan.capabilities,
                         post_shape=plan.slots['post'], applicability=applicability)


def render(contract, fault=False, cli=False, plan=None):
    if contract.get('version') == 'R5.33':
        raise ValueError('R5.33 requires current_pipeline application assembly')
    if plan is not None:
        unit = generated_unit(contract, plan, fault=fault)
        entry = 'run_cli' if cli else 'run'
        return '\n'.join(['# Disposable generated program; regenerate from semantic contract.',
                          'from refined_runtime_r5_28 import instant_key, instant_lt, project, run, run_cli, sole',
                          '', *unit.declaration, '', 'if __name__ == "__main__":',
                          '    ' + entry + '(execute, ' + repr(unit.input_shape) + ', ' +
                           repr(unit.state_shape) + ', ' + repr(unit.outcome_shapes) +
                           ', capability_shapes=' + repr(unit.capability_shapes) + ')', '']).encode()
    if plan is None:
        typed(contract)
    else:
        if plan.contract is not contract:
            raise ValueError('typed plan belongs to another contract')
        plan.assert_current()
    slots = {'input': contract['input'], 'pre': contract['state']}
    value_slots = {'input': contract['input'], 'pre': contract['state'], 'post': contract['state']}
    lines = ['# Disposable generated program; regenerate from semantic contract.',
              'from refined_runtime_r5_28 import instant_key, instant_lt, project, run, run_cli, sole', '',
             'def execute(input, pre):']
    for index, branch in enumerate(contract['branches']):
        condition = 'if ' + expression(branch['when'], slots=slots, plan=plan) + ':' if index == 0 else (
            'elif ' + expression(branch['when'], slots=slots, plan=plan) + ':' if branch['when'] is not None else 'else:')
        lines.append('    ' + condition)
        transition = branch['transition']
        if transition == {'preserve': True}:
            lines.extend(['        post = pre', '        write = False'])
        elif 'relations' in transition:
            lines.extend(['        post = pre', '        write = True'])
            for relation in _relational(transition['relations'], contract['state'],
                                        {'input': contract['input'], 'pre': contract['state']}, plan):
                kind, rule = next(iter(relation.items()))
                if kind == 'post_equals':
                    lines.append('        post = {**post, ' + repr(rule['field']) + ': ' + expression(rule['value'], slots=slots, plan=plan) + '}')
                    continue
                name = rule['collection']
                source = 'post' if name is None else 'post[' + repr(name) + ']'
                identity = repr(rule['identity'] if 'identity' in rule else rule['key'])
                lines.extend(['        if len({row[' + identity + '] for row in ' + source + '}) != len(' + source + '):',
                              '            raise ValueError("duplicate identity")'])
                if kind == 'exact_frame':
                    lines.extend(['        _new = ' + expression(rule['record'], slots=slots, plan=plan),
                                  '        if _new[' + identity + '] in {row[' + identity + '] for row in ' + source + '}:',
                                  '            raise ValueError("identity not fresh")',
                                  '        _rows = [*' + source + ', _new]'])
                elif kind == 'remove':
                    match = expression(rule['match'], slots=slots, plan=plan)
                    # Disposable injected lowering fault: drop the first element by
                    # position instead of honoring the keyed target. Faithfully grounded.
                    if fault:
                        lines.append('        _rows = ' + source + '[1:]')
                    else:
                        lines.append('        _rows = [item for item in ' + source +
                                     ' if item[' + identity + '] != ' + match + ']')
                elif kind == 'replace_field':
                    field = repr(rule['field'])
                    match, value = expression(rule['match'], slots=slots, plan=plan), expression(rule['value'], slots=slots, plan=plan)
                    # Disposable injected lowering fault: retain the old field value,
                    # faithfully grounded but never matching the assigned value.
                    value = 'item[' + field + ']' if fault else value
                    lines.append('        _rows = [{**item, ' + field + ': ' + value +
                                 '} if item[' + identity + '] == ' + match + ' else item for item in ' + source + ']')
                else:
                    field = repr(rule['field'])
                    lines.append('        _rows = [{**item, ' + field + ': ' + expression(rule['value'], slots=slots, plan=plan) +
                                  '} if ' + field + ' not in item else item for item in ' + source + ']')
                lines.append('        post = _rows' if name is None else
                             '        post = {**post, ' + repr(name) + ': _rows}')
        elif 'default_missing' in transition:
            rule = transition['default_missing']
            identity, field = repr(rule['identity']), repr(rule['field'])
            lines.extend(['        if len({row[' + identity + '] for row in pre}) != len(pre):',
                          '            raise ValueError("duplicate identity")',
                          '        post = [{**item, ' + field + ': ' + expression(rule['value'], slots=slots) +
                          '} if ' + field + ' not in item else item for item in pre]',
                          '        write = True'])
        else:
            update = transition['replace_field']
            key, field = repr(update['key']), repr(update['field'])
            match, value = expression(update['match'], slots=slots), expression(update['value'], slots=slots)
            # Disposable injected compiler fault: wrong replacement value, never alter semantics.
            if fault:
                value = 'item[' + field + ']'
            lines.extend(['        post = [{**item, ' + field + ': ' + value + '} if item[' + key +
                          '] == ' + match + ' else item for item in pre]',
                          '        write = True'])
        lines.append('        return {"kind": ' + repr(branch['tag']) + ', "value": ' +
                      expression(branch['value'], {'post': 'post'}, value_slots, fault, plan) + '}, post, write')
    entry = 'run_cli' if cli else 'run'
    lines.extend(['', 'if __name__ == "__main__":',
                   '    ' + entry + '(execute, ' + repr(contract['input']) + ', ' +
                   repr(contract['state']) + ', ' +
                   repr({b['tag']: b.get('value_type', 'string') for b in contract['branches']}) + ')', ''])
    return '\n'.join(lines).encode()


def generate(contract, directory, fault=False, cli=False, plan=None):
    """Fault variant is a disposable lowering experiment, excluded from normal generation."""
    directory = Path(directory)
    artifact = render(contract, fault, cli, plan)
    runtime = RUNTIME.read_bytes()
    identity = sha(canonical(contract))
    (directory / 'operation.py').write_bytes(artifact)
    (directory / RUNTIME.name).write_bytes(runtime)
    manifest = {'contract': identity, 'id': contract['id'], 'version': contract['version'],
                'artifact': sha(artifact), 'runtime': sha(runtime),
                'generation': sha(canonical([identity, sha(artifact), sha(runtime)]))}
    (directory / 'provenance.json').write_bytes(canonical(manifest))
    return manifest
