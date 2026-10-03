"""Prospective target-independent type closure for R5.27 operation contracts.

This module does not alter the pinned R5.23 compiler or the R5.26 prototype.
Presence witnesses are local to a positive conjunction (or a direct selection
predicate); a selection never exports its item binding to another expression.
"""

from benchmark.semantic import generative_r5_13 as general
from benchmark.semantic.capability_boundary_r5_22 import capability_type
from benchmark.semantic.typed_lowering_r5_12 import _compile, _field
from benchmark.semantic.capability_boundary_r5_22 import parse_instant
from dataclasses import dataclass


ORDERABLE = ('string', 'integer', 'instant')


def declared(path, slots):
    if not isinstance(path, list) or not path or any(type(p) is not str for p in path) or path[0] not in slots:
        raise ValueError('invalid reference')
    shape = slots[path[0]]
    for part in path[1:]:
        shape = _field(shape, part)
    return shape


def witness(expr, slots):
    if not isinstance(expr, dict) or set(expr) != {'present'} or not isinstance(expr['present'], dict) or set(expr['present']) != {'ref'}:
        raise ValueError('presence needs a field reference')
    path = expr['present']['ref']
    if not isinstance(path, list) or len(path) < 2 or not isinstance(declared(path, slots), dict) or declared(path, slots).keys() != {'optional'}:
        raise ValueError('presence requires optional field')
    return tuple(path)


def conjunction(parts, slots):
    if not isinstance(parts, list) or len(parts) < 2:
        raise ValueError('conjunction needs predicates')
    guards = {witness(part, slots) for part in parts if isinstance(part, dict) and set(part) == {'present'}}
    return [part for part in parts if isinstance(part, dict) and set(part) == {'present'}] + [
        part for part in parts if not (isinstance(part, dict) and set(part) == {'present'})], guards


def selection_guards(source, slots, element):
    selection = source.get('select') if isinstance(source, dict) else None
    if selection is None:
        return frozenset()
    where = selection['where']
    scoped = {**slots, 'item': element}
    if isinstance(where, dict) and set(where) == {'and'}:
        return frozenset(conjunction(where['and'], scoped)[1])
    if isinstance(where, dict) and set(where) == {'present'}:
        return frozenset((witness(where, scoped),))
    return frozenset()


def ordering_plan(arg, slots):
    if not isinstance(arg, dict) or set(arg) != {'source', 'keys'} or not isinstance(arg['keys'], list) or not arg['keys']:
        raise ValueError('invalid ordering')
    source = analyze(arg['source'], slots)
    if not isinstance(source, dict) or set(source) != {'sequence'}:
        raise ValueError('ordering needs sequence')
    element = source['sequence']
    guards = selection_guards(arg['source'], slots, element)
    keys = []
    for key in arg['keys']:
        if type(key) is not str:
            raise ValueError('invalid ordering key')
        shape = _field(element, key)
        if isinstance(shape, dict) and set(shape) == {'optional'} and ('item', key) in guards:
            shape = shape['optional']
        if shape not in ORDERABLE:
            raise ValueError('non-orderable key; optional key needs selection presence')
        keys.append((key, shape))
    return {'element': element, 'keys': keys, 'comparison': 'lexicographic',
            'ties': 'unconstrained', 'direction': None}


def analyze(expr, slots, refinements=frozenset()):
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError('invalid expression')
    kind, arg = next(iter(expr.items()))
    if kind == 'ref':
        shape = declared(arg, slots)
        return shape['optional'] if isinstance(shape, dict) and set(shape) == {'optional'} and tuple(arg) in refinements else shape
    if kind == 'present':
        witness(expr, slots)
        return 'boolean'
    if kind == 'and':
        planned, guards = conjunction(arg, slots)
        if any(analyze(p, slots, refinements | guards) != 'boolean' for p in planned):
            raise ValueError('conjunction needs predicates')
        return 'boolean'
    if kind == 'not':
        if analyze(arg, slots, refinements) != 'boolean':
            raise ValueError('negation needs predicate')
        return 'boolean'
    if kind in ('equals', 'before'):
        if not isinstance(arg, list) or len(arg) != 2:
            raise ValueError('invalid operands')
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
        ordering_plan(arg, slots)
        return analyze(arg['source'], slots)
    if kind == 'record':
        if not isinstance(arg, dict) or any(type(name) is not str for name in arg):
            raise ValueError('invalid record')
        return {'record': {name: analyze(value, slots, refinements) for name, value in arg.items()}}
    if kind == 'cardinality':
        source = analyze(arg, slots, refinements)
        if not isinstance(source, dict) or set(source) != {'sequence'}:
            raise ValueError('cardinality needs sequence')
        return 'integer'
    if kind == 'sole':
        source = analyze(arg, slots, refinements)
        if not isinstance(source, dict) or set(source) != {'sequence'}:
            raise ValueError('sole needs sequence')
        return source['sequence']
    if kind == 'project':
        if not isinstance(arg, dict) or set(arg) != {'row', 'fields'} or not isinstance(arg['fields'], list) or not arg['fields'] or any(type(name) is not str for name in arg['fields']) or len(set(arg['fields'])) != len(arg['fields']):
            raise ValueError('invalid projection')
        row = analyze(arg['row'], slots, refinements)
        fields = {name: _field(row, name) for name in arg['fields']}
        if any(isinstance(shape, dict) and set(shape) == {'optional'} for shape in fields.values()):
            raise ValueError('projection cannot require an optionally-present field')
        return {'record': fields}
    if kind == 'fallback':
        if not isinstance(arg, dict) or set(arg) != {'value', 'default'}:
            raise ValueError('invalid fallback')
        value = arg['value']
        if not isinstance(value, dict) or set(value) != {'ref'} or len(value['ref']) < 2:
            raise ValueError('fallback requires optional reference')
        source = analyze(value, slots, refinements)
        if not isinstance(source, dict) or set(source) != {'optional'} or analyze(arg['default'], slots, refinements) != source['optional']:
            raise ValueError('incompatible fallback')
        return source['optional']
    if kind == 'external':
        if not isinstance(arg, dict) or set(arg) != {'source'}:
            raise ValueError('invalid external')
        return capability_type(arg['source'])
    # Existing string/collection operations and typed literals retain their
    # already checked behavior; none carries a refinement into a new scope.
    return _compile(expr, slots)[0]


def typed(contract):
    if not isinstance(contract, dict) or set(contract) != {'id', 'version', 'input', 'state', 'branches'} or contract['version'] != 'R5.27':
        raise ValueError('R5.27 requires versioned operation contract')
    if type(contract['id']) is not str or not contract['id']:
        raise ValueError('invalid identity')
    inp, state = contract['input'], contract['state']
    if not isinstance(inp, dict) or set(inp) != {'record'} or not isinstance(state, dict) or set(state) not in ({'sequence'}, {'record'}):
        raise general.UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state/input shape')
    general.shape_valid(inp)
    general.shape_valid(state)
    branches = contract['branches']
    if not isinstance(branches, list) or len(branches) < 2:
        raise ValueError('branches require guards and final otherwise')
    slots = {'input': inp, 'pre': state}
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or set(branch) != {'tag', 'when', 'value', 'value_type', 'transition'}:
            raise ValueError('invalid branch')
        if type(branch['tag']) is not str or not branch['tag'] or (branch['when'] is None) != (index == len(branches) - 1):
            raise ValueError('invalid branch guard or tag')
        if branch['when'] is not None and analyze(branch['when'], slots) != 'boolean':
            raise ValueError('guard must be boolean')
        general.shape_valid(branch['value_type'])
        if analyze(branch['value'], {**slots, 'post': state}) != branch['value_type']:
            raise ValueError('outcome payload type mismatch')
        transition = branch['transition']
        if transition == {'preserve': True}:
            continue
        if not isinstance(transition, dict) or set(transition) != {'relations'} or not isinstance(transition['relations'], list) or not transition['relations']:
            raise general.UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        # Relation operands bind to input/pre, never to post or to a leaked item.
        # This is operand typing, not a replacement for the relation-set planner:
        # overlap, framing and uniqueness still require planning before lowering.
        for relation in transition['relations']:
            if not isinstance(relation, dict) or len(relation) != 1:
                raise ValueError('invalid state relation')
            kind, rule = next(iter(relation.items()))
            if kind not in ('remove', 'replace_field', 'exact_frame', 'default_missing', 'post_equals'):
                raise general.UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
            if not isinstance(rule, dict):
                raise ValueError('invalid state relation')
            expected = {'remove': {'collection', 'identity', 'match'},
                        'replace_field': {'collection', 'key', 'match', 'field', 'value'},
                        'exact_frame': {'collection', 'identity', 'record'},
                        'default_missing': {'collection', 'identity', 'field', 'value'},
                        'post_equals': {'field', 'value'}}[kind]
            if set(rule) != expected:
                raise ValueError('invalid state relation parameters')
            if kind == 'post_equals':
                if set(state) != {'record'} or analyze(rule['value'], slots) != _field(state, rule['field']):
                    raise ValueError('post equality type mismatch')
                continue
            collection = state if rule['collection'] is None else _field(state, rule['collection'])
            if not isinstance(collection, dict) or set(collection) != {'sequence'} or not isinstance(collection['sequence'], dict) or set(collection['sequence']) != {'record'}:
                raise ValueError('invalid collection projection')
            fields = collection['sequence']['record']
            identity = rule.get('identity', rule.get('key'))
            if fields.get(identity) != 'string':
                raise ValueError('invalid identity')
            if kind == 'exact_frame':
                if analyze(rule['record'], slots) != collection['sequence']:
                    raise ValueError('framed record type mismatch')
            elif kind in ('remove', 'replace_field'):
                if analyze(rule['match'], slots) != 'string':
                    raise ValueError('key type mismatch')
                if kind == 'replace_field' and analyze(rule['value'], slots) != fields.get(rule['field']):
                    raise ValueError('invalid replacement field or type')
            elif not isinstance(fields.get(rule['field']), dict) or set(fields[rule['field']]) != {'optional'} or analyze(rule['value'], slots) != fields[rule['field']]['optional']:
                raise ValueError('invalid default field or type')
    if len({b['tag'] for b in branches}) != len(branches):
        raise ValueError('duplicate outcome tag')
    return contract


@dataclass(frozen=True)
class CheckedPlan:
    """Checked source identity and scoped relation dependencies, not an AST copy.

    Node IDs refer to the actual source objects. A consumer cannot silently
    substitute a different expression or export a selection's item witness.
    """
    contract: dict
    digest: str
    scopes: dict
    orders: dict
    operands: dict
    relations: dict = None
    optional_record_fields: frozenset = frozenset()

    def assert_current(self):
        if general.sha(general.canonical(self.contract)) != self.digest:
            raise ValueError('typed plan source changed')

    def operand_type(self, expr):
        self.assert_current()
        if id(expr) not in self.operands:
            raise ValueError('operand is not in checked plan')
        return self.operands[id(expr)]


def checked_plan(contract):
    typed(contract)
    scopes, orders, operands = {}, {}, {}
    optional_record_fields = set()
    slots = {'input': contract['input'], 'pre': contract['state']}

    def visit(expr, environment):
        if not isinstance(expr, dict) or len(expr) != 1:
            return
        kind, arg = next(iter(expr.items()))
        if kind == 'and':
            _, guards = conjunction(arg, environment)
            # Dependencies are on semantic node identity, not the field label.
            producers = {tuple(part['present']['ref']): id(part) for part in arg if 'present' in part}
            scopes[id(expr)] = tuple((path, producers[path]) for path in sorted(guards))
            for part in arg:
                visit(part, environment)
        elif kind == 'select':
            visit(arg['source'], environment)
            element = analyze(arg['source'], environment)['sequence']
            visit(arg['where'], {**environment, 'item': element})
        elif kind == 'order':
            orders[id(expr)] = ordering_plan(arg, environment)
            visit(arg['source'], environment)
        elif kind in ('equals', 'before'):
            for part in arg:
                visit(part, environment)
        elif kind == 'record':
            for part in arg.values():
                if isinstance(part, dict) and set(part) == {'ref'}:
                    shape = declared(part['ref'], environment)
                    if isinstance(shape, dict) and set(shape) == {'optional'}:
                        optional_record_fields.add(id(part))
                visit(part, environment)
        elif kind in ('not', 'cardinality', 'sole'):
            visit(arg, environment)
        elif kind == 'project':
            visit(arg['row'], environment)
        elif kind == 'fallback':
            visit(arg['value'], environment)
            visit(arg['default'], environment)

    for branch in contract['branches']:
        if branch['when'] is not None:
            visit(branch['when'], slots)
        visit(branch['value'], {**slots, 'post': contract['state']})
        for relation in branch['transition'].get('relations', []):
            kind, rule = next(iter(relation.items()))
            for name in ('match', 'record', 'value'):
                if name in rule:
                    operands[id(rule[name])] = analyze(rule[name], slots)
                    visit(rule[name], slots)
    # Relation overlap/framing is checked once, after operand typing. The
    # emitter consumes the resulting conjunction rather than planning again.
    from benchmark.semantic.refined_generator_r5_28 import _relational
    relations = {}
    for branch in contract['branches']:
        transition = branch['transition']
        if 'relations' in transition:
            provisional = CheckedPlan(contract, general.sha(general.canonical(contract)),
                                      scopes, orders, operands)
            relations[id(branch)] = tuple(_relational(transition['relations'], contract['state'],
                slots, provisional))
    return CheckedPlan(contract, general.sha(general.canonical(contract)), scopes, orders,
                       operands, relations, frozenset(optional_record_fields))


def interpret(expr, facts, slots, plan):
    """Interpret semantic source against observations; never read emitted code."""
    plan.assert_current()
    kind, arg = next(iter(expr.items()))
    def ev(node, values=facts, shapes=slots):
        return interpret(node, values, shapes, plan)
    if kind == 'present':
        path = arg['ref']
        return path[-1] in ev({'ref': path[:-1]})
    if kind == 'and':
        guarded = {producer for _, producer in plan.scopes[id(expr)]}
        parts = [p for p in arg if id(p) in guarded] + [p for p in arg if id(p) not in guarded]
        return all(ev(part) for part in parts)
    if kind == 'not':
        return not ev(arg)
    if kind == 'equals':
        return ev(arg[0]) == ev(arg[1])
    if kind == 'before':
        return parse_instant(ev(arg[0])) < parse_instant(ev(arg[1]))
    if kind == 'select':
        source = ev(arg['source'])
        element = analyze(arg['source'], slots)['sequence']
        return [row for row in source if ev(arg['where'], {**facts, 'item': row}, {**slots, 'item': element})]
    if kind == 'order':
        keys = plan.orders[id(expr)]['keys']
        return sorted(ev(arg['source']), key=lambda row: tuple(
            parse_instant(row[key]) if shape == 'instant' else row[key] for key, shape in keys))
    if kind == 'cardinality':
        return len(ev(arg))
    if kind == 'sole':
        return _sole(ev(arg))
    if kind == 'record':
        result = {}
        for key, value in arg.items():
            if id(value) in plan.optional_record_fields:
                path = value['ref']
                if path[-1] not in ev({'ref': path[:-1]}):
                    continue
            result[key] = ev(value)
        return result
    if kind == 'project':
        row = ev(arg['row'])
        return {key: row[key] for key in arg['fields']}
    return _compile(expr, slots)[1](facts)


def _sole(rows):
    if len(rows) != 1:
        raise ValueError('sole needs exactly one selected element')
    return rows[0]


def generate_legacy_subset(contract, directory):
    """Exercise existing general lowering after R5.27 typing where it still applies.

    Explicitly fail closed for newly typed expressions that the pinned R5.23
    emitter cannot lower. This is a compatibility bridge, not R5.27 generation
    of optional refinement or chronological ordering.
    """
    typed(contract)
    general.typed(contract)
    return general.generate(contract, directory)


def generate(contract, directory, fault=False):
    """R5.28 general generator entry with an authoritative checked source plan."""
    plan = checked_plan(contract)
    from benchmark.semantic import refined_generator_r5_28
    return refined_generator_r5_28.generate(contract, directory, fault=fault, plan=plan)
