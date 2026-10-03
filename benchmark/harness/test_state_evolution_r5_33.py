"""Cross-state source authority, concrete durability and independent challenges."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import refined_evidence_r5_28 as evidence
from benchmark.semantic import refined_runtime_r5_28 as runtime
from benchmark.semantic.evolution_study_r5_33 import (
    application, initial, rows, lit, ref, capture, run_study, ENVELOPE_B, ROWS_A, ROWS_B)


class StateEvolutionR533(unittest.TestCase):
    def test_durable_row_and_root_lifecycles_mutations_and_faults(self):
        report = run_study()
        for lifecycle in report['lifecycles'].values():
            calls = lifecycle['calls']
            for call in calls:
                self.assertEqual(call['verdict'], {'provenance_valid': True, 'grounded': True, 'conformant': True})
            for before, after in zip(calls, calls[1:]):
                self.assertEqual(before['post_digest'], after['pre_digest'])
            self.assertEqual(calls[3]['event']['outcome']['value'], 4)
            self.assertEqual(calls[3]['event']['post']['specimens'][1]['medium'], 'rock')
            self.assertEqual(calls[3]['event']['post']['specimens'][0]['provenance'], 'ridge')
            self.assertEqual(len(calls[-1]['event']['post']['specimens']), 5)
            for call in lifecycle['unavailable_after']:
                self.assertIsNone(call['event'])
                self.assertNotEqual(call['public']['exit'], 0)
                self.assertEqual(call['pre_digest'], call['post_digest'])
        self.assertEqual(report['mutations']['default']['event']['post']['specimens'][0]['medium'], 'crystal')
        self.assertEqual(report['mutations']['metadata']['event']['post']['metadata']['collection'], 'curated-register')
        for call in report['mutations'].values():
            self.assertTrue(call['verdict']['conformant'])
        for name, call in report['faults'].items():
            with self.subTest(fault=name):
                self.assertEqual(call['verdict'], {'provenance_valid': True, 'grounded': True, 'conformant': False})

    def test_independent_slot_and_field_facts_and_no_downstream_typing(self):
        model = application()
        contract = model['operations']['migrate']
        plan = pipeline.checked(model)['migrate']
        self.assertEqual(plan.slots['pre'], ROWS_A)
        self.assertEqual(plan.slots['post'], ENVELOPE_B)
        relation = contract['branches'][0]['transition']['relations'][0]
        binding = plan.bindings[id(relation)]
        self.assertEqual(binding['source'], ('pre',))
        self.assertEqual(binding['target'], ('post', 'specimens'))
        self.assertEqual(binding['source_type'], ROWS_A)
        self.assertEqual(binding['target_type'], ROWS_B)
        with patch.object(types, 'analyze', side_effect=AssertionError('downstream analysis')):
            emitter.generated_unit(contract, plan)
            post = {'revision': 2, 'specimens': [{**r, 'medium': r.get('medium', 'mineral')} for r in rows()],
                    'metadata': {'collection': 'mineral-register'}}
            self.assertTrue(evidence.conforms(contract, {}, rows(), {'kind': 'ok', 'value': 3}, post,
                                              False, True, plan=plan))
        plan.slots['post']['record']['revision'] = 'string'
        with self.assertRaisesRegex(ValueError, 'source changed|facts changed'):
            plan.assert_invariants()

    def test_unavailable_before_and_wrong_versions_reject_before_execution(self):
        for envelope in (False, True):
            model = application(envelope)
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                pipeline.generate(model, root)
                (root / 'state.json').write_bytes(emitter.canonical(initial(envelope)))
                call = capture(model, root, 'current')
                self.assertIsNone(call['event'])
                self.assertEqual(call['pre_bytes'], call['post_bytes'])
                if not envelope:
                    for revision in (2, 99):
                        state = initial(False)
                        state['revision'] = revision
                        (root / 'state.json').write_bytes(emitter.canonical(state))
                        call = capture(model, root, 'migrate')
                        self.assertIsNone(call['event'])
                        self.assertIn('unavailable', call['public']['stderr'])
                        self.assertEqual(call['pre_bytes'], call['post_bytes'])

    def test_type_confusion_and_incomplete_construction_reject(self):
        for fault in ('source_field', 'wrong_source', 'wrong_target', 'missing_mapping', 'preserve', 'source_codec'):
            model = application()
            contract = model['operations']['migrate']
            for branch in contract['branches']:
                relations = branch['transition']['relations']
                if fault == 'source_field':
                    relations[1]['post_equals']['value'] = ref('pre', 'revision')
                elif fault == 'wrong_source':
                    relations[0]['default_missing']['source'] = ['specimens']
                elif fault == 'wrong_target':
                    relations[0]['default_missing']['field'] = 'provenance'
                    relations[0]['default_missing']['value'] = lit(7)
                elif fault == 'missing_mapping':
                    del relations[2]
                elif fault == 'preserve':
                    branch['transition'] = {'preserve': True}
                elif fault == 'source_codec':
                    contract['state']['post'] = copy.deepcopy(contract['state']['pre'])
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                pipeline.checked(model)

    def test_target_only_field_read_from_legacy_type_rejects(self):
        model = application()
        # A genuinely absent V1 field, not its declared optional medium.
        for branch in model['operations']['migrate']['branches']:
            branch['value'] = {'sole': {'select': {'source': ref('pre'),
                'where': {'equals': [ref('item', 'new_target_only'), lit('x')]}}}}
        with self.assertRaisesRegex(ValueError, 'field reference'):
            pipeline.checked(model)

    def test_runtime_post_codec_is_not_pre_codec(self):
        model = application()
        unit = emitter.generated_unit(model['operations']['migrate'], pipeline.checked(model)['migrate'])
        namespace = {}
        exec('\n'.join(unit.declaration), namespace)
        outcome, post, write, _ = runtime._invoke(namespace['execute'], unit.input_shape,
            unit.post_shape, unit.outcome_shapes, rows(), {}, '', unit.capability_shapes)
        self.assertEqual(outcome['value'], 3)
        self.assertTrue(write)
        self.assertTrue(runtime.valid(post, unit.post_shape))
        with self.assertRaisesRegex(ValueError, 'typed transition'):
            runtime._invoke(namespace['execute'], unit.input_shape, unit.state_shape,
                           unit.outcome_shapes, rows(), {}, '', unit.capability_shapes)

    def test_empty_and_multiple_missing_fields_compose(self):
        model = application()
        for branch in model['operations']['migrate']['branches']:
            relation = copy.deepcopy(branch['transition']['relations'][0])
            relation['default_missing']['field'] = 'provenance'
            relation['default_missing']['value'] = lit('unknown')
            branch['transition']['relations'].append(relation)
        model['state']['versions']['V2']['record']['specimens']['sequence']['record']['provenance'] = 'string'
        for branch in model['operations']['current_insert']['branches']:
            literal = branch['transition']['relations'][0]['exact_frame']['record']['literal']
            literal['type'] = copy.deepcopy(model['state']['versions']['V2']['record']['specimens']['sequence'])
            literal['value']['provenance'] = 'unknown'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            for population in ([], rows()):
                (root / 'state.json').write_bytes(emitter.canonical(population))
                call = capture(model, root, 'migrate')
                self.assertTrue(call['verdict']['conformant'])
                self.assertEqual(call['event']['outcome']['value'], len(population))

    def test_new_field_absent_from_source_schema(self):
        model = application()
        del model['state']['versions']['V1']['sequence']['record']['medium']
        for branch in model['operations']['legacy_insert']['branches']:
            branch['transition']['relations'][0]['exact_frame']['record']['literal']['type'] = copy.deepcopy(
                model['state']['versions']['V1']['sequence'])
        population = [{k: v for k, v in row.items() if k != 'medium'} for row in rows()]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(emitter.canonical(population))
            call = capture(model, root, 'migrate')
            self.assertTrue(call['verdict']['conformant'])
            self.assertTrue(all(row['medium'] == 'mineral' for row in call['event']['post']['specimens']))

    def test_conflicting_identity_defaults_reject(self):
        model = application()
        for branch in model['operations']['migrate']['branches']:
            relation = copy.deepcopy(branch['transition']['relations'][0])
            relation['default_missing'].update(identity='designation', field='provenance', value=lit('unknown'))
            branch['transition']['relations'].append(relation)
        with self.assertRaisesRegex(ValueError, 'conflicting cross-state source'):
            pipeline.checked(model)

    def test_capability_matrix(self):
        matrix = json.loads(Path('benchmark/results/phase5c/R5_24-type-matrix.json').read_bytes())
        profile = matrix['r5_33_state_evolution']
        self.assertEqual(profile['candidate_core_constructs'], 30)
        self.assertEqual(set(profile['dimensions']), set(profile['per_dimension']))
        self.assertTrue(all(item['supported'] for item in profile['per_dimension'].values()))
        self.assertEqual(profile['entry_point'], 'benchmark.semantic.current_pipeline')


if __name__ == '__main__':
    unittest.main()
