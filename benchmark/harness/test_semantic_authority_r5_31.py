"""Authority closure, poisoned alternate typers and independent behavior checks."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.harness.test_current_pipeline_r5_29 import application, data, EARLY, LATE, lit, ref
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import refined_evidence_r5_28 as evidence
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic.typed_lowering_r5_12 import _compile
from benchmark.semantic import refined_runtime_r5_28 as runtime
from benchmark.semantic.capability_boundary_r5_22 import controlled_descriptor


class SemanticAuthorityR531(unittest.TestCase):
    def test_complete_expression_refinement_outcome_state_and_projection_facts(self):
        model = application()
        plans = pipeline.checked(model)
        for plan in plans.values():
            plan.assert_invariants()
            self.assertEqual(set(plan.facts), set(plan.operands))
            self.assertEqual(plan.slots['pre'], plan.slots['post'])
        query = model['operations']['query']['branches'][0]['value']
        before = query['select']['where']['and'][1]['before'][0]
        fact = plans['query'].facts[id(before)]
        self.assertEqual(fact['declared'], {'optional': 'instant'})
        self.assertEqual(fact['effective'], 'instant')
        self.assertEqual(fact['field'], ('item', 'seen'))
        scope, producer = fact['refinement'][0]
        where = query['select']['where']
        self.assertEqual((scope, producer), (id(where), id(where['and'][0])))
        create = plans['create']
        self.assertEqual(create.capabilities, {'fresh_unique_id': 'string', 'utc_clock': 'instant'})
        binding = next(iter(create.bindings.values()))
        self.assertEqual((binding['source'], binding['target']), (('pre',), ('post',)))
        self.assertEqual(binding['identity'], ('code', 'string'))
        self.assertEqual(create.outcomes['ok'], model['state']['sequence'])
        project = model['operations']['replace']['branches'][0]['value']
        self.assertEqual(plans['replace'].projections[id(project)], (('code', 'string'), ('label', 'string')))
        ordered = model['operations']['ordered']['branches'][0]['value']
        ordered['order']['keys'] = ['seen']
        order = next(iter(types.checked_plan(model['operations']['ordered']).orders.values()))
        key = order['key_facts'][0]
        self.assertEqual((key['declared'], key['effective']), ({'optional': 'instant'}, 'instant'))
        self.assertEqual(key['field'], (id(ordered['order']['source']), 'seen'))
        where = ordered['order']['source']['select']['where']
        self.assertEqual(key['refinement'], (id(where), id(where['and'][0])))

    def test_legacy_disagreement_has_one_current_outcome(self):
        model = application()
        contract = model['operations']['ordered']
        expression = contract['branches'][0]['value']
        with self.assertRaisesRegex(ValueError, 'unsupported relation: present|non-orderable key'):
            _compile(expression, {'input': contract['input'], 'pre': contract['state']})
        rows = [dict(code='A', created=LATE, seen=EARLY, label='old'),
                dict(code='B', created=EARLY, seen=EARLY, label='old')]
        # If any current component selects the legacy type interpretation, fail.
        with (patch('benchmark.semantic.typed_lowering_r5_12._compile', side_effect=AssertionError('legacy authority')),
             patch.object(emitter, '_compile', side_effect=AssertionError('legacy emitter authority')),
             patch.object(evidence, '_compile', side_effect=AssertionError('legacy verifier authority'))):
            self.run_current(model, 'ordered', rows, data('A'), ['B', 'A'], codes=True)

    def run_current(self, model, operation, rows, inp, expected, codes=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(emitter.canonical(rows))
            event, public, before, after = pipeline.observe(root, operation, inp)
            self.assertEqual(pipeline.challenge(model, root, event, public, before, after),
                {'provenance_valid': True, 'grounded': True, 'conformant': True})
            value = json.loads(public['stdout'])['value']
            self.assertEqual([row['code'] for row in value] if codes else value, expected)

    def test_downstream_does_not_reanalyze_after_plan_is_established(self):
        model = application()
        rows = [dict(code='A', created=EARLY, seen=EARLY, label='old')]
        for name, contract in model['operations'].items():
            plan = types.checked_plan(contract)
            with (self.subTest(operation=name), patch.object(types, 'analyze', side_effect=AssertionError('downstream retyping')),
                 patch.object(emitter, 'typed', side_effect=AssertionError('alternate checker')),
                 patch.object(emitter, 'ordering_plan', side_effect=AssertionError('alternate order'))):
                emitter.generated_unit(contract, plan)
                if name != 'create':
                    with tempfile.TemporaryDirectory() as folder:
                        root = Path(folder)
                        emitter.generate(contract, root, plan=plan)
                        (root / 'state.json').write_bytes(emitter.canonical(rows))
                        event, public, before, after = evidence.observe(root, data('A'))
                        outcome = json.loads(public['stdout'])
                        self.assertTrue(evidence.conforms(contract, data('A'), json.loads(before), outcome,
                            json.loads(after), before == after, event['attempted_write'], event['externals'], plan))

    def test_mutated_checked_facts_fail_internal_consistency(self):
        for component in ('orders', 'operands', 'outcomes', 'bindings', 'projections', 'scopes', 'slots'):
            model = application()
            name = {'orders': 'ordered', 'projections': 'replace', 'scopes': 'query', 'bindings': 'create'}.get(component, 'query')
            contract = model['operations'][name]
            plan = types.checked_plan(contract)
            facts = getattr(plan, component)
            facts[next(iter(facts))] = 'contradictory emitter assumption'
            with self.subTest(component=component), self.assertRaisesRegex(ValueError, 'internal consistency failure'):
                emitter.generated_unit(contract, plan)
            with self.assertRaisesRegex(ValueError, 'internal consistency failure'):
                types.interpret(contract['branches'][0]['value'], {}, {}, plan)

    def test_alien_expression_and_stale_source_fail_closed(self):
        contract = application()['operations']['ordered']
        plan = types.checked_plan(contract)
        with self.assertRaisesRegex(ValueError, 'not in checked plan'):
            emitter.expression(copy.deepcopy(contract['branches'][0]['value']), plan=plan)
        contract['branches'][0]['value']['order']['keys'] = ['code']
        with self.assertRaisesRegex(ValueError, 'source changed'):
            emitter.generated_unit(contract, plan)

    def test_runtime_capability_validation_consumes_authoritative_shapes(self):
        plan = pipeline.checked(application())['create']
        with patch.dict(runtime.CAPABILITY_TYPES, {'utc_clock': 'integer'}):
            caps = runtime.Capabilities(controlled_descriptor({'utc_clock': EARLY}), plan.capabilities)
            self.assertEqual(caps['utc_clock'], EARLY)
            wrong = runtime.Capabilities(json.dumps({'mode': 'controlled', 'values': {'utc_clock': 42}}), plan.capabilities)
            with self.assertRaisesRegex(ValueError, 'violates capability type'):
                wrong['utc_clock']

    def test_semantic_order_and_projection_mutations_change_plan_and_behavior(self):
        rows = [dict(code='A', created=LATE, seen=EARLY, label='old'),
                dict(code='B', created=EARLY, seen=EARLY, label='old')]
        baseline = application()
        mutated = copy.deepcopy(baseline)
        mutated['operations']['ordered']['branches'][0]['value']['order']['keys'] = ['code']
        for model, expected in ((baseline, ['B', 'A']), (mutated, ['A', 'B'])):
            plan = pipeline.checked(model)['ordered']
            self.assertEqual(next(iter(plan.orders.values()))['keys'][0][0], 'created' if model is baseline else 'code')
            self.run_current(model, 'ordered', rows, data('A'), expected, codes=True)
        changed = copy.deepcopy(baseline)
        branch = changed['operations']['replace']['branches'][0]
        branch['value']['project']['fields'] = ['code']
        branch['value_type'] = {'record': {'code': 'string'}}
        self.assertEqual(pipeline.checked(changed)['replace'].outcomes['ok'], {'record': {'code': 'string'}})
        self.run_current(changed, 'replace', rows, data('A', label='new'), {'code': 'A'})
        self.run_current(baseline, 'replace', rows, data('A', label='new'), {'code': 'A', 'label': 'new'})

    def test_normalization_and_fallback_mutations_use_current_authority(self):
        model = application()
        state = model['state']
        def contract(value, shape):
            return {'id': 'independent.values', 'version': 'R5.27',
                'input': {'record': {'tags': {'sequence': 'string'}, 'preferred': {'optional': 'string'}}},
                'state': state, 'branches': [
                    {'tag': 'ok', 'when': {'equals': [lit(1, 'integer'), lit(1, 'integer')]},
                     'value': value, 'value_type': shape, 'transition': {'preserve': True}},
                    {'tag': 'skip', 'when': None, 'value': lit('skip', 'string'),
                     'value_type': 'string', 'transition': {'preserve': True}}]}
        norm = {'stable_unique': {'sequence': {'map': {'sequence': ref('input', 'tags'), 'transform': 'trim'}},
                                   'equality': 'case_sensitive_string'}}
        for value, expected in ((norm, ['a', 'b']), (norm['stable_unique']['sequence'], ['a', 'b', 'a'])):
            app = {'id': 'independent.normalization', 'state': state,
                   'operations': {'run': contract(value, {'sequence': 'string'})}}
            self.run_current(app, 'run', [], {'tags': [' a ', 'b', 'a']}, expected)
        for default in ('first', 'second'):
            value = {'fallback': {'value': ref('input', 'preferred'), 'default': lit(default, 'string')}}
            app = {'id': 'independent.fallback', 'state': state, 'operations': {'run': contract(value, 'string')}}
            self.run_current(app, 'run', [], {'tags': []}, default)
            self.run_current(app, 'run', [], {'tags': [], 'preferred': 'explicit'}, 'explicit')


if __name__ == '__main__':
    unittest.main()
