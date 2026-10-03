"""Independent public/durable witnesses and layer-specific fault detection."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import binding_study_r5_32 as study
from benchmark.semantic import public_binding_r5_32 as public
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import input_binding_r5_32 as binder
from benchmark.semantic.refined_generator_r5_28 import canonical


class InputBindingR532(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = study.study()

    def test_all_public_cases_ground_at_the_correct_layer(self):
        for name, case in self.evidence['cases'].items():
            with self.subTest(case=name):
                verdict = case['verdict']
                self.assertTrue(verdict['provenance_valid'])
                self.assertTrue(verdict['binding_grounded'])
                self.assertTrue(verdict['binding_conformant'])
                self.assertEqual(verdict['semantic_grounded'], case['semantic_invoked'])
                self.assertEqual(verdict['semantic_conformant'], True if case['semantic_invoked'] else None)

    def test_omission_fallback_equivalence_and_optional_durable_membership(self):
        omitted = self.evidence['cases']['omitted']
        explicit = self.evidence['cases']['fallback_equivalent']
        self.assertEqual(omitted['semantic_input'], {})
        self.assertEqual(explicit['semantic_input'], {'preferred': 'quiet'})
        self.assertEqual(omitted['public']['outcome'], {'kind': 'omitted', 'value': 'quiet'})
        self.assertEqual(explicit['public']['outcome'], {'kind': 'supplied', 'value': 'quiet'})
        self.assertEqual(omitted['after']['label'], explicit['after']['label'])
        self.assertEqual(omitted['after']['last'], {})
        self.assertEqual(explicit['after']['last'], {'note': 'quiet'})
        self.assertFalse(omitted['binding']['slots']['preferred']['supplied'])
        self.assertTrue(explicit['binding']['slots']['preferred']['supplied'])
        self.assertEqual(self.evidence['cases']['optional_explicit']['after']['last'],
                         {'note': 'bright', 'seen': study.EARLY})

    def test_binding_failures_have_no_semantic_event_or_state_transition(self):
        names = ('malformed_instant', 'invalid_domain', 'malformed_integer', 'missing_required',
                 'malformed_string', 'malformed_payload', 'unknown_argument', 'unknown_operation')
        for name in names:
            with self.subTest(case=name):
                case = self.evidence['cases'][name]
                self.assertFalse(case['semantic_invoked'])
                self.assertIsNone(case['semantic_input'])
                self.assertEqual(case['public']['status'], 'binding_failure')
                self.assertEqual(case['exit'], 2)
                self.assertEqual(case['before'], case['after'])
                self.assertTrue(case['bytes_equal'])
        self.assertNotIn('not-a-date', json.dumps(self.evidence['cases']['malformed_instant']['binding']))

    def test_well_formed_semantic_failure_is_not_parse_failure(self):
        for name in ('valid_domain_forbidden', 'state_forbidden', 'semantic_integer_failure', 'semantic_instant_failure'):
            case = self.evidence['cases'][name]
            with self.subTest(case=name):
                self.assertTrue(case['semantic_invoked'])
                self.assertEqual(case['binding']['failures'], [])
                self.assertEqual(case['public']['outcome']['kind'], 'rule_rejected')
                self.assertTrue(case['bytes_equal'])
        self.assertEqual(self.evidence['cases']['valid_integer']['semantic_input'], {'amount': 7})

    def test_multi_operation_byte_continuity(self):
        cases = list(self.evidence['cases'].values())
        for previous, following in zip(cases, cases[1:]):
            self.assertEqual(previous['after'], following['before'])
            self.assertEqual(previous['after_digest'], following['before_digest'])
        self.assertEqual(cases[-1]['after']['quota'], 7)
        self.assertEqual(cases[-1]['after']['mode'], 'acquire')

    def test_all_four_faults_ground_but_fail_binding_conformance(self):
        for fault, case in self.evidence['faults'].items():
            with self.subTest(fault=fault):
                self.assertTrue(case['verdict']['provenance_valid'])
                self.assertTrue(case['verdict']['binding_grounded'])
                self.assertFalse(case['verdict']['binding_conformant'])
                self.assertIsNone(case['verdict']['semantic_conformant'])
        self.assertTrue(self.evidence['faults']['A']['semantic_invoked'])
        self.assertFalse(self.evidence['faults']['C']['bytes_equal'])
        self.assertEqual(self.evidence['faults']['C']['after']['at'], study.EARLY)
        self.assertFalse(self.evidence['faults']['D']['semantic_invoked'])

    def test_semantic_only_mutations_propagate_without_binder_changes(self):
        mutations = self.evidence['semantic_mutations']
        for case in mutations.values():
            self.assertTrue(case['verdict']['binding_conformant'])
            self.assertTrue(case['verdict']['semantic_conformant'])
        self.assertEqual(mutations['default']['after']['label'], 'bright')
        self.assertEqual(mutations['type']['semantic_input'], {'amount': '7x'})
        self.assertEqual(mutations['type']['public']['outcome']['kind'], 'rule_rejected')
        self.assertEqual(mutations['constraint']['after']['mode'], 'calibrate')

    def test_metadata_consumes_sealed_plan_without_retyping(self):
        plans = pipeline.checked(study.application())
        with (patch.object(types, 'analyze', side_effect=AssertionError('second analyzer')),
              patch.object(binder, 'bind', side_effect=AssertionError('oracle trusts binder')),
              patch.object(binder, 'decode', side_effect=AssertionError('oracle trusts decoder'))):
            metadata = public.metadata(plans, study.policy())
            expected = public.expected_binding('quota', '{"units":"8"}', metadata)
            self.assertEqual(expected['input'], {'amount': 8})
        self.assertEqual(metadata['operations']['schedule']['when']['type'], 'instant')
        self.assertEqual(metadata['operations']['quota']['units']['slot'], 'amount')
        plans['schedule'].slots['input']['record']['when'] = 'integer'
        with self.assertRaisesRegex(ValueError, 'source changed|internal consistency'):
            public.metadata(plans, study.policy())

    def test_invalid_metadata_and_unknown_shapes_fail_closed(self):
        for policy in ({'operations': {'absent': {}}},
                       {'operations': {'quota': {'absent': {}}}},
                       {'operations': {'quota': {'amount': {'domain': ['not-an-int']}}}},
                       {'operations': {'configure': {'seen': {'argument': 'preferred'}}}},
                       {'error_codes': {}}):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                public.metadata(pipeline.checked(study.application()), policy)

    def test_public_mapping_is_independent_of_semantic_outcomes(self):
        model = study.application()
        policy = study.policy()
        policy['error_codes']['malformed_scalar'] = 'decode.invalid'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public.generate(model, root, policy)
            (root / 'state.json').write_bytes(canonical(study.initial()))
            binding, semantic, observed, before, after = public.observe(root, 'schedule', {'when': 'bad'})
            self.assertEqual(json.loads(observed['stdout'])['errors'][0]['code'], 'decode.invalid')
            self.assertIsNone(semantic)
            self.assertTrue(public.challenge(model, root, binding, semantic, observed, before, after, policy)['binding_conformant'])
        self.assertNotIn('decode.invalid', json.dumps(model))

    def test_forged_binding_evidence_and_scalar_edges(self):
        model = study.application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public.generate(model, root, study.policy())
            (root / 'state.json').write_bytes(canonical(study.initial()))
            for raw in (True, None, 7.0, ' 7', '', '1_0', '٧'):
                binding, semantic, observed, before, after = public.observe(root, 'quota', {'units': raw})
                self.assertIsNone(semantic)
                self.assertTrue(public.challenge(model, root, binding, semantic, observed, before, after, study.policy())['binding_conformant'])
            binding, semantic, observed, before, after = public.observe(root, 'configure', {})
            forged = copy.deepcopy(binding)
            forged['semantic_invoked'] = False
            self.assertFalse(public.challenge(model, root, forged, semantic, observed, before, after, study.policy())['binding_grounded'])

    def test_capability_matrix_accounting(self):
        path = Path(__file__).resolve().parents[1] / 'results/phase5c/R5_24-type-matrix.json'
        matrix = json.loads(path.read_bytes())['r5_32_input_binding']
        self.assertEqual(matrix['candidate_core_constructs'], 30)
        self.assertFalse(matrix['frozen_transport_binding']['supported'])
        self.assertEqual(set(matrix['dimensions']), {'raw_input_binding', 'suppliedness', 'parse_decode',
            'binding_failure', 'typed_invocation', 'semantic_invalidity_distinction', 'public_adapter', 'binding_grounding'})
        for dimension in matrix['dimensions']:
            self.assertTrue(matrix['per_dimension'][dimension]['supported'])
