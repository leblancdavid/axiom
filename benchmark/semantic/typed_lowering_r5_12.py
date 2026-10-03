"""Bounded, target-neutral validating lowering of typed #45 tuple relations.

This interpreter checks supplied tuples. It neither constructs target algorithms
nor asserts that a tuple was captured faithfully from a real invocation.
"""

from benchmark.semantic.capability_boundary_r5_22 import (
    CAPABILITY_TYPES, capability_type, is_instant, parse_instant)


class UnsupportedLowering(ValueError):
    """A valid candidate relation is outside this deliberately small lowering."""


def _type(value, shape):
    if shape == 'string':
        return type(value) is str
    if shape == 'integer':
        return type(value) is int
    if shape == 'boolean':
        return type(value) is bool
    if shape == 'instant':
        return is_instant(value)
    if isinstance(shape, dict) and set(shape) == {'nullable'}:
        return value is None or _type(value, shape['nullable'])
    if isinstance(shape, dict) and set(shape) == {'optional'}:
        return _type(value, shape['optional'])
    if isinstance(shape, dict) and set(shape) == {'sequence'}:
        return type(value) is list and all(_type(v, shape['sequence']) for v in value)
    if isinstance(shape, dict) and set(shape) == {'record'}:
        fields = shape['record']
        required = {key for key, child in fields.items() if not (
            isinstance(child, dict) and set(child) == {'optional'})}
        return type(value) is dict and required <= set(value) <= set(fields) and all(
            _type(value[k], t) for k, t in fields.items() if k in value)
    raise ValueError('invalid type declaration')


def _field(shape, name):
    if not isinstance(shape, dict) or set(shape) != {'record'} or name not in shape['record']:
        raise ValueError('invalid typed field reference')
    return shape['record'][name]


def _compile(expr, slots):
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError('invalid expression')
    kind, arg = next(iter(expr.items()))
    if kind == 'ref':
        if (not isinstance(arg, list) or not arg or
                any(type(part) is not str for part in arg) or arg[0] not in slots):
            raise ValueError('invalid reference')
        shape = slots[arg[0]]
        for part in arg[1:]:
            shape = _field(shape, part)
        return shape, lambda facts: _path(facts, arg)
    if kind == 'literal':
        if not isinstance(arg, dict) or set(arg) != {'type', 'value'} or not _type(arg['value'], arg['type']):
            raise ValueError('invalid typed literal')
        return arg['type'], lambda facts: arg['value']
    if kind == 'record':
        if not isinstance(arg, dict):
            raise ValueError('invalid record expression')
        fields = {key: _compile(value, slots) for key, value in arg.items()}
        if any(type(key) is not str for key in fields):
            raise ValueError('invalid record field')
        return {'record': {key: shape for key, (shape, _) in fields.items()}}, (
            lambda facts: {key: fn(facts) for key, (_, fn) in fields.items()})
    if kind == 'trim':
        shape, fn = _compile(arg, slots)
        if shape != 'string':
            raise ValueError('trim needs string')
        return 'string', lambda facts: fn(facts).strip()
    if kind == 'map':
        if not isinstance(arg, dict) or set(arg) != {'sequence', 'transform'} or arg['transform'] != 'trim':
            raise ValueError('invalid collection operation')
        shape, fn = _compile(arg['sequence'], slots)
        if shape != {'sequence': 'string'}:
            raise ValueError('map needs string sequence')
        return shape, lambda facts: [s.strip() for s in fn(facts)]
    if kind == 'stable_unique':
        if not isinstance(arg, dict) or set(arg) != {'sequence', 'equality'} or arg['equality'] != 'case_sensitive_string':
            raise ValueError('invalid comparison')
        shape, fn = _compile(arg['sequence'], slots)
        if shape != {'sequence': 'string'}:
            raise ValueError('stable_unique needs string sequence')
        return shape, lambda facts: list(dict.fromkeys(fn(facts)))
    if kind == 'nonblank':
        shape, fn = _compile(arg, slots)
        if shape != 'string':
            raise ValueError('nonblank needs string')
        return 'boolean', lambda facts: bool(fn(facts).strip())
    if kind == 'for_each':
        if not isinstance(arg, dict) or set(arg) != {'sequence', 'bind', 'property'} or (
                type(arg['bind']) is not str or not arg['bind'].isidentifier() or
                arg['bind'] in slots):
            raise ValueError('invalid quantifier scope')
        shape, source = _compile(arg['sequence'], slots)
        if shape != {'sequence': 'string'}:
            raise ValueError('quantifier needs string sequence')
        result, predicate = _compile(arg['property'], {**slots, arg['bind']: 'string'})
        if result != 'boolean':
            raise ValueError('quantifier needs predicate')
        return 'boolean', lambda facts: all(predicate({**facts, arg['bind']: item})
                                            for item in source(facts))
    if kind == 'select':
        if not isinstance(arg, dict) or set(arg) != {'source', 'where'}:
            raise ValueError('invalid selection')
        source_type, source = _compile(arg['source'], slots)
        if not isinstance(source_type, dict) or set(source_type) != {'sequence'}:
            raise ValueError('selection needs a sequence')
        predicate_type, predicate = _compile(arg['where'], {**slots, 'item': source_type['sequence']})
        if predicate_type != 'boolean':
            raise ValueError('selection needs a predicate')
        return source_type, lambda facts: [item for item in source(facts)
                                          if predicate({**facts, 'item': item})]
    if kind == 'order':
        if not isinstance(arg, dict) or set(arg) != {'source', 'keys'} or not isinstance(arg['keys'], list) or not arg['keys']:
            raise ValueError('invalid ordering')
        source_type, source = _compile(arg['source'], slots)
        if not isinstance(source_type, dict) or set(source_type) != {'sequence'}:
            raise ValueError('ordering needs a sequence')
        for key in arg['keys']:
            if type(key) is not str:
                raise ValueError('invalid ordering key')
            if _field(source_type['sequence'], key) not in ('string', 'integer'):
                raise ValueError('non-orderable key')
        return source_type, lambda facts: sorted(source(facts), key=lambda row: tuple(row[k] for k in arg['keys']))
    if kind == 'cardinality':
        shape, source = _compile(arg, slots)
        if not isinstance(shape, dict) or set(shape) != {'sequence'}:
            raise ValueError('cardinality needs a sequence')
        return 'integer', lambda facts: len(source(facts))
    if kind == 'external':
        if not isinstance(arg, dict) or set(arg) != {'source'}:
            raise ValueError('invalid external reference')
        return capability_type(arg['source']), (
            lambda facts: facts['external'][arg['source']])
    if kind == 'fallback':
        if not isinstance(arg, dict) or set(arg) != {'value', 'default'}:
            raise ValueError('invalid fallback')
        shape, fn = _compile(arg['value'], slots)
        if not isinstance(shape, dict) or set(shape) != {'optional'}:
            raise ValueError('fallback source must be an optionally-present reference')
        if not isinstance(arg['value'], dict) or set(arg['value']) != {'ref'} or len(arg['value']['ref']) < 2:
            raise ValueError('fallback source must be a field reference')
        path = arg['value']['ref']
        base = shape['optional']
        default_shape, default_fn = _compile(arg['default'], slots)
        if default_shape != base:
            raise ValueError('incompatible fallback default')
        parent_shape, parent_fn = _compile({'ref': path[:-1]}, slots)
        terminal = path[-1]
        return base, lambda facts: (default_fn(facts) if terminal not in parent_fn(facts)
                                    else fn(facts))
    if kind == 'before':
        if not isinstance(arg, list) or len(arg) != 2:
            raise ValueError('before needs two operands')
        left, right = (_compile(part, slots) for part in arg)
        if left[0] != 'instant' or right[0] != 'instant':
            raise ValueError('before requires two typed instants')
        return 'boolean', lambda facts: parse_instant(left[1](facts)) < parse_instant(right[1](facts))
    if kind == 'sole':
        shape, fn = _compile(arg, slots)
        if not isinstance(shape, dict) or set(shape) != {'sequence'}:
            raise ValueError('sole needs a sequence')
        return shape['sequence'], lambda facts: _sole(fn(facts))
    if kind == 'project':
        if not isinstance(arg, dict) or set(arg) != {'row', 'fields'} or (
                not isinstance(arg['fields'], list) or not arg['fields'] or
                len(set(arg['fields'])) != len(arg['fields'])):
            raise ValueError('invalid projection')
        shape, fn = _compile(arg['row'], slots)
        if not isinstance(shape, dict) or set(shape) != {'record'}:
            raise ValueError('projection needs a record source')
        record = shape['record']
        projected = {}
        for name in arg['fields']:
            if name not in record:
                raise ValueError('projected field is not in the source record')
            if isinstance(record[name], dict) and set(record[name]) == {'optional'}:
                raise ValueError('projection cannot require an optionally-present field')
            projected[name] = record[name]
        return {'record': projected}, lambda facts: {name: fn(facts)[name] for name in arg['fields']}
    if kind in ('equals', 'and'):
        if not isinstance(arg, list) or len(arg) < 2 or (kind == 'equals' and len(arg) != 2):
            raise ValueError('invalid operands')
        compiled = [_compile(part, slots) for part in arg]
        if kind == 'equals' and compiled[0][0] != compiled[1][0]:
            raise ValueError('equality type mismatch')
        if kind == 'and' and any(shape != 'boolean' for shape, _ in compiled):
            raise ValueError('conjunction needs predicates')
        return 'boolean', (lambda facts: compiled[0][1](facts) == compiled[1][1](facts)) if kind == 'equals' else (
            lambda facts: all(fn(facts) for _, fn in compiled))
    if kind == 'not':
        shape, fn = _compile(arg, slots)
        if shape != 'boolean':
            raise ValueError('negation needs a predicate')
        return 'boolean', lambda facts: not fn(facts)
    raise UnsupportedLowering('unsupported relation: ' + str(kind))


def _path(facts, parts):
    value = facts[parts[0]]
    for part in parts[1:]:
        value = value[part]
    return value


def _sole(items):
    if not isinstance(items, list) or len(items) != 1:
        raise ValueError('sole needs exactly one selected element')
    return items[0]


def lower(contract):
    """Compile a checked contract into a reusable case-scoped tuple validator."""
    if not isinstance(contract, dict) or set(contract) != {'input', 'state', 'outcomes'}:
        raise ValueError('invalid operation contract')
    # Validate type declarations even for empty collections and unused fields.
    def valid_shape(shape):
        if shape in ('string', 'integer', 'boolean', 'instant'):
            return
        if isinstance(shape, dict) and set(shape) in ({'sequence'}, {'nullable'}):
            valid_shape(next(iter(shape.values())))
        elif (isinstance(shape, dict) and set(shape) == {'record'} and
              isinstance(shape['record'], dict) and
              all(type(key) is str for key in shape['record'])):
            for child in shape['record'].values():
                valid_shape(child)
        else:
            raise ValueError('invalid type declaration')
    valid_shape(contract['input'])
    valid_shape(contract['state'])
    outcomes = contract['outcomes']
    if not isinstance(outcomes, dict) or not outcomes:
        raise ValueError('missing outcomes')
    compiled = {}
    for tag, branch in outcomes.items():
        if not isinstance(tag, str) or not isinstance(branch, dict) or set(branch) != {'value', 'constraints'}:
            raise ValueError('invalid outcome alternative')
        valid_shape(branch['value'])
        checks = branch['constraints']
        if not isinstance(checks, list) or not checks:
            raise ValueError('missing constraints')
        slots = {'input': contract['input'], 'pre': contract['state'],
                 'post': contract['state'], 'outcome': branch['value']}
        typed = [_compile(check, slots) for check in checks]
        if any(shape != 'boolean' for shape, _ in typed):
            raise ValueError('constraint must be boolean')
        compiled[tag] = (branch['value'], [fn for _, fn in typed])

    def check(input_value, pre, outcome, post):
        if (not isinstance(outcome, dict) or set(outcome) != {'kind', 'value'} or
                type(outcome['kind']) is not str or outcome['kind'] not in compiled):
            return False
        shape, checks = compiled[outcome['kind']]
        if not all((_type(input_value, contract['input']), _type(pre, contract['state']),
                    _type(outcome['value'], shape), _type(post, contract['state']))):
            return False
        facts = {'input': input_value, 'pre': pre, 'outcome': outcome['value'], 'post': post}
        return all(fn(facts) for fn in checks)

    return check
