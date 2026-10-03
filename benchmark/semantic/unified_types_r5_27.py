"""Prospective target-independent type closure for R5.27 operation contracts.

This module does not alter the pinned R5.23 compiler or the R5.26 prototype.
Presence witnesses are local to a positive conjunction (or a direct selection
predicate); a selection never exports its item binding to another expression.
"""

from benchmark.semantic import generative_r5_13 as general
from benchmark.semantic.capability_boundary_r5_22 import capability_type
from benchmark.semantic.typed_lowering_r5_12 import _field, _type, _path, UnsupportedLowering
from benchmark.semantic.capability_boundary_r5_22 import parse_instant
from dataclasses import dataclass
from contextvars import ContextVar


_analysis = ContextVar('checked_semantic_analysis', default=None)


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
    keys, key_facts = [], []
    for key in arg['keys']:
        if type(key) is not str:
            raise ValueError('invalid ordering key')
        declaration = shape = _field(element, key)
        dependency = None
        if isinstance(shape, dict) and set(shape) == {'optional'} and ('item', key) in guards:
            shape = shape['optional']
            where = arg['source']['select']['where']
            producers = where['and'] if 'and' in where else [where]
            producer = [part for part in producers if 'present' in part and part['present']['ref'] == ['item', key]][-1]
            dependency = (id(where), id(producer))
        if shape not in ORDERABLE:
            raise ValueError('non-orderable key; optional key needs selection presence')
        keys.append((key, shape))
        key_facts.append({'field': (id(arg['source']), key), 'declared': declaration,
                          'effective': shape, 'refinement': dependency})
    return {'element': element, 'keys': keys, 'comparison': 'lexicographic',
            'ties': 'unconstrained', 'direction': None, 'source_type': source,
            'refinements': tuple(sorted(guards)), 'source': id(arg['source']),
            'key_facts': key_facts}


def analyze(expr, slots, refinements=frozenset()):
    collector = _analysis.get()
    cache_key = (id(expr), general.canonical(slots), tuple(sorted(refinements)))
    if collector is not None and cache_key in collector['cache']:
        return collector['cache'][cache_key]
    shape = _analyze(expr, slots, refinements)
    if collector is not None:
        kind, arg = next(iter(expr.items()))
        declaration = declared(arg, slots) if kind == 'ref' else shape
        dependencies = tuple(collector['active'][path] for path in sorted(refinements)
                             if kind == 'ref' and tuple(arg) == path)
        fact = {'kind': kind, 'declared': declaration, 'effective': shape,
                'field': tuple(arg) if kind == 'ref' else None,
                'refinement': dependencies,
                'element': shape.get('sequence') if isinstance(shape, dict) else None}
        # Reused source objects may appear in multiple equivalent scopes. A
        # context-dependent reuse cannot be represented by one node binding.
        previous = collector['facts'].get(id(expr))
        if previous is not None and previous != fact:
            raise ValueError('ambiguous reused semantic node binding')
        collector['facts'][id(expr)] = fact
        collector['operands'][id(expr)] = shape
        collector['cache'][cache_key] = shape
    return shape


def _analyze(expr, slots, refinements=frozenset()):
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError('invalid expression')
    kind, arg = next(iter(expr.items()))
    if kind == 'ref':
        shape = declared(arg, slots)
        return shape['optional'] if isinstance(shape, dict) and set(shape) == {'optional'} and tuple(arg) in refinements else shape
    if kind == 'present':
        witness(expr, slots)
        analyze(arg, slots)
        return 'boolean'
    if kind == 'and':
        planned, guards = conjunction(arg, slots)
        collector = _analysis.get()
        previous = None
        if collector is not None:
            producers = {tuple(p['present']['ref']): (id(expr), id(p)) for p in arg if 'present' in p}
            collector['scopes'][id(expr)] = tuple((path, producer[1]) for path, producer in sorted(producers.items()))
            previous = collector['active']
            collector['active'] = {**previous, **producers}
        try:
            if any(analyze(p, slots, refinements | guards) != 'boolean' for p in planned):
                raise ValueError('conjunction needs predicates')
        finally:
            if collector is not None:
                collector['active'] = previous
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
        order = ordering_plan(arg, slots)
        if _analysis.get() is not None:
            _analysis.get()['orders'][id(expr)] = order
        return order['source_type']
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
        if _analysis.get() is not None:
            _analysis.get()['projections'][id(expr)] = tuple(fields.items())
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
        shape = capability_type(arg['source'])
        if _analysis.get() is not None:
            _analysis.get()['capabilities'][arg['source']] = shape
        return shape
    if kind == 'literal':
        if not isinstance(arg, dict) or set(arg) != {'type', 'value'} or not _type(arg['value'], arg['type']):
            raise ValueError('invalid typed literal')
        return arg['type']
    if kind in ('trim', 'nonblank'):
        if analyze(arg, slots, refinements) != 'string':
            raise ValueError(kind + ' needs string')
        return 'string' if kind == 'trim' else 'boolean'
    if kind in ('map', 'stable_unique'):
        parameter, required = ('transform', 'trim') if kind == 'map' else ('equality', 'case_sensitive_string')
        if not isinstance(arg, dict) or set(arg) != {'sequence', parameter} or arg[parameter] != required:
            raise ValueError('invalid collection operation')
        if analyze(arg['sequence'], slots, refinements) != {'sequence': 'string'}:
            raise ValueError(kind + ' needs string sequence')
        return {'sequence': 'string'}
    if kind == 'for_each':
        if not isinstance(arg, dict) or set(arg) != {'sequence', 'bind', 'property'} or type(arg['bind']) is not str or not arg['bind'].isidentifier() or arg['bind'] in slots:
            raise ValueError('invalid quantifier scope')
        if analyze(arg['sequence'], slots, refinements) != {'sequence': 'string'}:
            raise ValueError('quantifier needs string sequence')
        if analyze(arg['property'], {**slots, arg['bind']: 'string'}) != 'boolean':
            raise ValueError('quantifier needs predicate')
        return 'boolean'
    raise UnsupportedLowering('unsupported relation: ' + str(kind))


def state_slots(contract):
    state = contract['state']
    return state if contract.get('version') == 'R5.33' else {'pre': state, 'post': state}


def uses_evolution(contract, transition):
    if contract.get('version') != 'R5.33' or 'relations' not in transition:
        return False
    states = state_slots(contract)
    return states['pre'] != states['post'] or any(
        isinstance(relation, dict) and isinstance(relation.get('default_missing'), dict)
        and 'source' in relation['default_missing']
        for relation in transition['relations'])


def evolution_relations(relations, slots):
    """Check #44 and target equalities with independent, side-qualified shapes.

    Complete target coverage replaces the old implicit unchanged-root frame.
    No renaming, removal, widening or implicit field construction is permitted.
    """
    if not isinstance(relations, list) or not relations:
        raise ValueError('missing evolution relations')
    pre, post = slots['pre'], slots['post']
    targets, groups = {}, {}
    collector = _analysis.get()
    for relation in relations:
        if not isinstance(relation, dict) or len(relation) != 1:
            raise ValueError('invalid evolution relation')
        kind, rule = next(iter(relation.items()))
        if kind == 'post_equals':
            if not isinstance(rule, dict) or set(rule) != {'field', 'value'}:
                raise ValueError('invalid target equality')
            field = rule['field']
            if type(field) is not str:
                raise ValueError('invalid target field identity')
            shape = _field(post, field)
            if field in targets or analyze(rule['value'], {'input': slots['input'], 'pre': pre}) != shape:
                raise ValueError('target equality type or overlap mismatch')
            targets[field] = 'equals'
            binding = {'source': ('pre',), 'target': ('post', field), 'type': shape,
                       'fields': None, 'identity': None, 'field': (field, shape),
                       'operands': {'value': id(rule['value'])}}
        elif kind == 'default_missing':
            if not isinstance(rule, dict) or set(rule) != {'source', 'target', 'identity', 'field', 'value'}:
                raise ValueError('evolution default needs both sides')
            source_path, target_path = rule['source'], rule['target']
            if not isinstance(source_path, list) or len(source_path) > 1:
                raise ValueError('invalid source projection')
            if not isinstance(target_path, list) or len(target_path) > 1:
                raise ValueError('invalid target projection')
            source = declared(['pre', *source_path], slots)
            target = declared(['post', *target_path], slots)
            if not isinstance(source, dict) or set(source) != {'sequence'} or not isinstance(target, dict) or set(target) != {'sequence'}:
                raise ValueError('evolution needs typed collections')
            old, new = source['sequence'], target['sequence']
            if not isinstance(old, dict) or set(old) != {'record'} or not isinstance(new, dict) or set(new) != {'record'}:
                raise ValueError('evolution needs typed rows')
            old_fields, new_fields = old['record'], new['record']
            identity, field = rule['identity'], rule['field']
            if type(identity) is not str or type(field) is not str:
                raise ValueError('invalid cross-state field identity')
            if old_fields.get(identity) != 'string' or new_fields.get(identity) != 'string' or identity == field:
                raise ValueError('cross-state identity mismatch')
            if field not in new_fields:
                raise ValueError('default target field absent')
            target_field = new_fields[field]
            base = target_field['optional'] if isinstance(target_field, dict) and set(target_field) == {'optional'} else target_field
            if analyze(rule['value'], {'input': slots['input'], 'pre': pre}) != base:
                raise ValueError('default target type mismatch')
            if field in old_fields and old_fields[field] not in (target_field, {'optional': base}):
                raise ValueError('default source type mismatch')
            key = tuple(target_path)
            root_field = target_path[0] if target_path else None
            if root_field in targets and targets[root_field] != key:
                raise ValueError('overlapping target construction')
            targets[root_field] = key
            if key not in groups:
                groups[key] = (tuple(source_path), old_fields, new_fields, identity, {})
            previous_source, previous_old, previous_new, previous_identity, defaults = groups[key]
            if (previous_source, previous_old, previous_new, previous_identity) != (tuple(source_path), old_fields, new_fields, identity):
                raise ValueError('conflicting cross-state source')
            if field in defaults:
                raise ValueError('duplicate cross-state default')
            defaults[field] = rule
            binding = {'source': ('pre', *source_path), 'target': ('post', *target_path),
                       'type': target, 'source_type': source, 'target_type': target,
                       'fields': new_fields, 'source_fields': old_fields,
                       'identity': (identity, 'string'), 'field': (field, target_field),
                       'source_field': ('pre', *source_path, field) if field in old_fields else None,
                       'target_field': ('post', *target_path, field),
                       'operands': {'value': id(rule['value'])}}
        else:
            raise UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: cross-state relation ' + kind)
        if collector is not None:
            collector['bindings'][id(relation)] = binding
    expected = set(post['record']) if set(post) == {'record'} else {None}
    if set(targets) != expected:
        raise ValueError('incomplete post-state construction')
    for _, old, new, _, defaults in groups.values():
        if not set(old) <= set(new):
            raise ValueError('keyed default cannot remove source fields')
        for field, shape in new.items():
            if field in defaults:
                continue
            if field not in old or old[field] != shape:
                raise ValueError('unmapped cross-state field')
    return tuple(relations)


def typed(contract):
    evolving = isinstance(contract, dict) and contract.get('version') == 'R5.33'
    expected = {'id', 'version', 'input', 'state', 'branches'} | ({'requires'} if evolving else set())
    if not isinstance(contract, dict) or set(contract) != expected or contract['version'] not in ('R5.27', 'R5.33'):
        raise ValueError('R5.27 requires versioned operation contract')
    if type(contract['id']) is not str or not contract['id']:
        raise ValueError('invalid identity')
    inp = contract['input']
    if evolving and (not isinstance(contract['state'], dict) or set(contract['state']) != {'pre', 'post'}):
        raise ValueError('evolution requires independent pre/post types')
    states = state_slots(contract)
    state = states['pre']
    if not isinstance(inp, dict) or set(inp) != {'record'} or not isinstance(state, dict) or set(state) not in ({'sequence'}, {'record'}):
        raise general.UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state/input shape')
    general.shape_valid(inp)
    general.shape_valid(state)
    general.shape_valid(states['post'])
    if evolving and (not isinstance(states['post'], dict) or set(states['post']) not in ({'record'}, {'sequence'})):
        raise ValueError('unsupported post-state root type')
    branches = contract['branches']
    if not isinstance(branches, list) or len(branches) < 2:
        raise ValueError('branches require guards and final otherwise')
    slots = {'input': inp, 'pre': state}
    if evolving and analyze(contract['requires'], slots) != 'boolean':
        raise ValueError('applicability must be boolean')
    if evolving and _analysis.get() is not None and _analysis.get()['capabilities']:
        raise ValueError('applicability cannot acquire external capabilities')
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or set(branch) != {'tag', 'when', 'value', 'value_type', 'transition'}:
            raise ValueError('invalid branch')
        if type(branch['tag']) is not str or not branch['tag'] or (branch['when'] is None) != (index == len(branches) - 1):
            raise ValueError('invalid branch guard or tag')
        if branch['when'] is not None and analyze(branch['when'], slots) != 'boolean':
            raise ValueError('guard must be boolean')
        general.shape_valid(branch['value_type'])
        if analyze(branch['value'], {**slots, 'post': states['post']}) != branch['value_type']:
            raise ValueError('outcome payload type mismatch')
        transition = branch['transition']
        if transition == {'preserve': True}:
            if states['pre'] != states['post']:
                raise ValueError('preserve cannot change state type')
            continue
        if not isinstance(transition, dict) or set(transition) != {'relations'} or not isinstance(transition['relations'], list) or not transition['relations']:
            raise general.UnsupportedLowering('UNSUPPORTED_LOWERING_CAPABILITY: state relation')
        if uses_evolution(contract, transition):
            evolution_relations(transition['relations'], {**slots, 'post': states['post']})
            continue
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
                if _analysis.get() is not None:
                    _analysis.get()['bindings'][id(relation)] = {'source': ('pre', rule['field']), 'target': ('post', rule['field']),
                        'type': _field(state, rule['field']), 'fields': None, 'identity': None,
                        'operands': {'value': id(rule['value'])}, 'field': (rule['field'], _field(state, rule['field']))}
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
            if kind == 'default_missing' and rule['field'] == identity:
                raise ValueError('invalid default identity or optional field')
            if _analysis.get() is not None:
                path = () if rule['collection'] is None else (rule['collection'],)
                _analysis.get()['bindings'][id(relation)] = {'source': ('pre', *path), 'target': ('post', *path),
                    'type': collection, 'fields': fields, 'identity': (identity, fields[identity]),
                    'operands': {name: id(rule[name]) for name in ('match', 'record', 'value') if name in rule},
                    'field': (rule['field'], fields[rule['field']]) if 'field' in rule else None}
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
    facts: dict = None
    bindings: dict = None
    projections: dict = None
    capabilities: dict = None
    slots: dict = None
    outcomes: dict = None
    seal: str = ''
    evolutions: frozenset = frozenset()
    applicability: int = None

    def fact_digest(self):
        return general.sha(general.canonical([self.scopes, self.orders, self.operands,
            self.relations, sorted(self.optional_record_fields), self.facts, self.bindings,
            self.projections, self.capabilities, self.slots, self.outcomes,
            sorted(self.evolutions), self.applicability]))

    def assert_current(self):
        if general.sha(general.canonical(self.contract)) != self.digest:
            raise ValueError('typed plan source changed')
        if self.seal and self.fact_digest() != self.seal:
            raise ValueError('compiler internal consistency failure: checked facts changed')

    def assert_invariants(self):
        """Check recorded closure; this never analyzes the semantic source."""
        self.assert_current()
        if set(self.facts) != set(self.operands):
            raise ValueError('compiler internal consistency failure: expression closure')
        for node, fact in self.facts.items():
            if fact['effective'] != self.operands[node]:
                raise ValueError('compiler internal consistency failure: operand binding')
            for scope, producer in fact['refinement']:
                if not any(p == producer for _, p in self.scopes[scope]):
                    raise ValueError('compiler internal consistency failure: refinement scope')
        for order in self.orders.values():
            if any(shape not in ORDERABLE for _, shape in order['keys']) or order['ties'] != 'unconstrained' or order['comparison'] != 'lexicographic' or order['direction'] is not None:
                raise ValueError('compiler internal consistency failure: ordering emitter contract')
            if order['source'] not in self.operands or order['source_type'] != self.operands[order['source']]:
                raise ValueError('compiler internal consistency failure: ordering source')
            for (key, shape), fact in zip(order['keys'], order['key_facts']):
                if fact['field'] != (order['source'], key) or fact['effective'] != shape:
                    raise ValueError('compiler internal consistency failure: ordering field')
                if fact['refinement'] is not None:
                    scope, producer = fact['refinement']
                    if self.facts[producer]['kind'] != 'present' or (scope != producer and not any(p == producer for _, p in self.scopes[scope])):
                        raise ValueError('compiler internal consistency failure: ordering refinement')
        for binding in self.bindings.values():
            if binding['source'][0] != 'pre' or binding['target'][0] != 'post' or any(node not in self.operands for node in binding['operands'].values()):
                raise ValueError('compiler internal consistency failure: state binding')
        if self.applicability is not None and self.operands.get(self.applicability) != 'boolean':
            raise ValueError('compiler internal consistency failure: applicability')
        if not self.evolutions <= set(self.relations):
            raise ValueError('compiler internal consistency failure: evolution closure')

    def operand_type(self, expr):
        self.assert_current()
        if id(expr) not in self.operands:
            raise ValueError('operand is not in checked plan')
        return self.operands[id(expr)]


def checked_plan(contract):
    collector = {name: {} for name in ('cache', 'active', 'scopes', 'orders', 'operands',
                                      'facts', 'bindings', 'projections', 'capabilities')}
    token = _analysis.set(collector)
    try:
        typed(contract)
    finally:
        _analysis.reset(token)
    scopes, orders, operands = (collector[name] for name in ('scopes', 'orders', 'operands'))
    # Optional construction is a checked reference fact, not emitter inference.
    optional_record_fields = frozenset(node for node, fact in collector['facts'].items()
        if fact['field'] is not None and isinstance(fact['declared'], dict)
        and set(fact['declared']) == {'optional'})
    slots = {'input': contract['input'], **state_slots(contract)}
    # Relation overlap/framing is checked once, after operand typing. The
    # emitter consumes the resulting conjunction rather than planning again.
    from benchmark.semantic.refined_generator_r5_28 import _relational
    relations = {}
    evolutions = set()
    for branch in contract['branches']:
        transition = branch['transition']
        if 'relations' in transition:
            if uses_evolution(contract, transition):
                evolutions.add(id(branch))
                relations[id(branch)] = tuple(transition['relations'])
                continue
            provisional = CheckedPlan(contract, general.sha(general.canonical(contract)),
                                      scopes, orders, operands, bindings=collector['bindings'])
            relations[id(branch)] = tuple(_relational(transition['relations'], slots['pre'],
                slots, provisional))
    plan = CheckedPlan(contract, general.sha(general.canonical(contract)), scopes, orders,
        operands, relations, optional_record_fields, collector['facts'], collector['bindings'],
        collector['projections'], collector['capabilities'], slots,
        {b['tag']: operands[id(b['value'])] for b in contract['branches']})
    object.__setattr__(plan, 'evolutions', frozenset(evolutions))
    object.__setattr__(plan, 'applicability', id(contract['requires']) if contract['version'] == 'R5.33' else None)
    object.__setattr__(plan, 'seal', plan.fact_digest())
    plan.assert_invariants()
    return plan


def interpret(expr, facts, slots, plan):
    """Interpret semantic source against observations; never read emitted code."""
    plan.operand_type(expr)
    kind, arg = next(iter(expr.items()))
    def ev(node, values=facts, shapes=slots):
        return interpret(node, values, shapes, plan)
    if kind == 'present':
        path = arg['ref']
        return path[-1] in _path(facts, path[:-1])
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
        element = plan.operand_type(arg['source'])['sequence']
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
                if path[-1] not in _path(facts, path[:-1]):
                    continue
            result[key] = ev(value)
        return result
    if kind == 'project':
        row = ev(arg['row'])
        return {key: row[key] for key, _ in plan.projections[id(expr)]}
    if kind == 'ref':
        return _path(facts, arg)
    if kind == 'literal':
        return arg['value']
    if kind == 'external':
        return facts['external'][arg['source']]
    if kind == 'fallback':
        path = arg['value']['ref']
        return ev(arg['default']) if path[-1] not in _path(facts, path[:-1]) else ev(arg['value'])
    if kind == 'trim':
        return ev(arg).strip()
    if kind == 'nonblank':
        return bool(ev(arg).strip())
    if kind == 'map':
        return [value.strip() for value in ev(arg['sequence'])]
    if kind == 'stable_unique':
        return list(dict.fromkeys(ev(arg['sequence'])))
    if kind == 'for_each':
        return all(ev(arg['property'], {**facts, arg['bind']: value}) for value in ev(arg['sequence']))
    raise UnsupportedLowering('unsupported relation: ' + str(kind))


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
