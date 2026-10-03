"""Independent CLI observations, checked-profile negative cases and six faults."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import checked_transport_r5_34 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import transport_study_r5_34 as study
from benchmark.semantic import transport_runtime_r5_34 as adapter
from benchmark.semantic.refined_generator_r5_28 import canonical


class CheckedTransportR534(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = study.study()

    def assert_layers(self, call, semantic=True):
        verdict = call['verdict']
        self.assertTrue(verdict['profile_integrity'])
        self.assertTrue(verdict['transport_grounded'])
        for layer in ('TRANSPORT_BINDING_CONFORMANT', 'TRANSPORT_OUTPUT_CONFORMANT'):
            self.assertIs(verdict[layer], True, (layer, call))
        if call['event']['binding'] is not None:
            self.assertIs(verdict['INPUT_BINDING_CONFORMANT'], True)
        self.assertIs(verdict['SEMANTIC_EXECUTION_CONFORMANT'], True if semantic else None)

    def test_same_shape_public_lifecycle_and_continuity(self):
        calls = self.report['A']['calls']
        previous = None
        for name, call in calls.items():
            self.assert_layers(call, call['semantic'] is not None)
            if previous is not None:
                self.assertEqual(previous, call['pre_bytes'], name)
            previous = call['post_bytes']
        final = json.loads(previous)
        self.assertEqual([(r['code'], r['label']) for r in final], [('M-1', 'new')])

    def test_binding_suppliedness_and_failure_taxonomy(self):
        calls = self.report['A']['calls']
        omitted = calls['omitted']['event']['binding']['slots']
        explicit = calls['explicit']['event']['binding']['slots']
        self.assertFalse(omitted['preferred']['supplied'])
        self.assertFalse(omitted['seen']['supplied'])
        self.assertTrue(explicit['preferred']['supplied'])
        self.assertTrue(explicit['seen']['supplied'])
        for name in ('malformed_instant', 'invalid_domain', 'malformed_scalar', 'missing_required', 'unknown_argument'):
            call = calls[name]
            self.assertEqual(call['event']['public']['status'], 'BINDING_FAILURE')
            self.assertEqual(call['public']['exit'], 2)
            self.assertIsNone(call['semantic'])
            self.assertEqual(call['pre_bytes'], call['post_bytes'])
        rejected = calls['semantic_rejection']
        self.assertEqual(rejected['event']['binding']['failures'], [])
        self.assertEqual(rejected['event']['public']['status'], 'SEMANTIC_FAILURE')
        self.assertEqual(rejected['public']['exit'], 1)
        self.assert_layers(rejected)

    def test_cross_shape_lifecycles_and_semantic_availability(self):
        for name, result in self.report['B'].items():
            previous = None
            for call in result['calls']:
                self.assert_layers(call)
                if previous is not None:
                    self.assertEqual(previous, call['pre_bytes'])
                previous = call['post_bytes']
            self.assertEqual(json.loads(previous)['revision'], 2)
            self.assertEqual(len(json.loads(previous)['specimens']), 5)
            for call in result['unavailable_before'] + result['unavailable_after']:
                self.assert_layers(call, False)
                self.assertEqual(call['public']['exit'], 3, name)
                self.assertEqual(call['event']['public']['status'], 'INVOCATION_FAILURE')
                self.assertTrue(call['event']['semantic_invoked'])
                self.assertEqual(call['pre_bytes'], call['post_bytes'])

    def test_six_disposable_faults_fail_correct_layers(self):
        faults = self.report['faults']
        self.assertIs(faults['A']['verdict']['TRANSPORT_BINDING_CONFORMANT'], False)
        self.assertIs(faults['B']['verdict']['TRANSPORT_BINDING_CONFORMANT'], False)
        self.assertIs(faults['B']['verdict']['INPUT_BINDING_CONFORMANT'], False)
        self.assertIs(faults['C']['verdict']['profile_integrity'], False)
        self.assertEqual(faults['C']['event']['public']['status'], 'BINDING_FAILURE')
        for name in ('D', 'E'):
            self.assertIs(faults[name]['verdict']['SEMANTIC_EXECUTION_CONFORMANT'], True)
            self.assertIs(faults[name]['verdict']['TRANSPORT_OUTPUT_CONFORMANT'], False)
        self.assertNotEqual(faults['F']['pre_bytes'], faults['F']['post_bytes'])
        self.assertIs(faults['F']['verdict']['TRANSPORT_BINDING_CONFORMANT'], False)
        self.assertIs(faults['F']['verdict']['SEMANTIC_EXECUTION_CONFORMANT'], False)

    def test_metadata_semantic_mutation_unchanged_adapter(self):
        for call in self.report['mutations'].values():
            self.assert_layers(call, call['semantic'] is not None)
        self.assertEqual(len({c['adapter_digest'] for c in self.report['mutations'].values()}), 1)
        self.assertEqual(self.report['mutations']['rename']['event']['requested'], 'enrol')
        self.assertEqual(self.report['mutations']['default']['semantic']['outcome']['value']['label'], 'curated')
        self.assertEqual(self.report['mutations']['projection']['semantic']['outcome']['value'], 'M-1')
        self.assertEqual(self.report['mutations']['domain']['event']['public']['status'], 'BINDING_FAILURE')

    def test_invalid_profiles_rejected_against_checked_facts(self):
        plans = pipeline.checked(study.application())
        spec = study.specification(study.application())
        changes = {
            'operation': lambda s: s[0].__setitem__('semantic', 'absent'),
            'public_duplicate': lambda s: s.append(copy.deepcopy(s[0])),
            'slot': lambda s: s[0]['arguments'][0].__setitem__('slot', 'absent'),
            'missing_required': lambda s: s[0]['arguments'].pop(0),
            'decoder': lambda s: s[0]['arguments'][0].__setitem__('decoder', 'instant'),
            'duplicate_binding': lambda s: s[0]['arguments'].append(copy.deepcopy(s[0]['arguments'][0])),
            'encoding': lambda s: s[0]['outcomes']['ok'].__setitem__('encoding', 'domain-specific'),
            'outcome_type': lambda s: s[0]['outcomes']['ok'].__setitem__('type', 'integer'),
            'outcome_identity': lambda s: s[0]['outcomes'].__setitem__('absent', s[0]['outcomes'].pop('ok')),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                altered = copy.deepcopy(spec)
                change(altered)
                with self.assertRaises(ValueError):
                    transport.validate(plans, altered)

    def test_stale_profile_blocked_before_execution(self):
        model = study.application()
        spec = study.specification(model)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec)
            (root / 'state.json').write_bytes(canonical([]))
            changed = study.application(default='changed')
            pipeline.generate(changed, root)
            event, semantic, public, before, after = transport.observe(root, ['list'])
            self.assertIsNone(event)
            self.assertIsNone(semantic)
            self.assertEqual(public['exit'], 4)
            self.assertIn('stale or corrupt', public['stderr'])
            self.assertEqual(before, after)

    def test_encoder_rejects_wrong_shape_and_supports_nested_shapes(self):
        for shape, value in [('integer', 4), ('string', 'text'),
            ({'record': {'reason': 'string'}}, {'reason': 'error'}),
            ({'sequence': {'record': {'code': 'string'}}}, [{'code': 'A'}])]:
            route = {'outcomes': {'ok': {'type': shape, 'status': 'SUCCESS'}}}
            visible, code = adapter.encode({'kind': 'ok', 'value': value}, route)
            self.assertEqual(visible['outcome']['value'], value)
            self.assertEqual(code, 0)
            with self.assertRaises(ValueError):
                adapter.encode({'kind': 'ok', 'value': None}, route)

    def test_boolean_raw_json_and_profile_authority(self):
        model = study.application()
        model['operations']['list']['input']['record']['enabled'] = {'optional': 'boolean'}
        plans = pipeline.checked(model)
        spec = transport.specification(plans)
        # Validation should consume the sealed plan even if alternate typing is poisoned.
        from unittest.mock import patch
        with patch('benchmark.semantic.unified_types_r5_27.analyze', side_effect=AssertionError('retyped')):
            transport.validate(plans, spec)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec)
            (root / 'state.json').write_bytes(canonical([]))
            for argv, supplied in [(['list'], False), (['list', '--enabled', 'false'], True)]:
                call = study.capture(model, root, spec, argv)
                self.assert_layers(call)
                self.assertEqual(call['event']['binding']['slots']['enabled']['supplied'], supplied)

    def test_capability_matrix(self):
        matrix = json.loads(Path('benchmark/results/phase5c/R5_24-type-matrix.json').read_bytes())
        profile = matrix['r5_34_checked_transport']
        self.assertEqual(profile['candidate_core_constructs'], 30)
        self.assertEqual(set(profile['dimensions']), set(profile['per_dimension']))
        self.assertTrue(all(item['supported'] for item in profile['per_dimension'].values()))
        self.assertEqual(profile['entry_point'], 'benchmark.semantic.current_pipeline')

    def test_aliases_can_exchange_slot_names(self):
        model = study.application()
        plans = pipeline.checked(model)
        spec = study.specification(model)
        for arg in spec[0]['arguments']:
            if arg['slot'] == 'quantity':
                arg['public'] = 'code'
            elif arg['slot'] == 'code':
                arg['public'] = 'quantity'
        transport.validate(plans, spec)


if __name__ == '__main__':
    unittest.main()
