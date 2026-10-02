"""Faults challenge real subprocess calls, not assembled four-slot witnesses."""

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import grounding_r5_7 as ground


OPEN = [{'id': 'v1', 'label': 'glass'}]
SEALED = [{'id': 'v1', 'label': 'glass', 'sealed': True}]


class GroundingPrototype(unittest.TestCase):
    def exercise(self, fault='none', rows=OPEN):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ground.compile_target(root, fault)
            (root / 'state.json').write_bytes(ground.canonical(rows))
            internal, public, pre, post = ground.run_case(root, rows)
            decision = ground.challenge(root, internal, public, pre, post)
            return decision, internal, public, pre, post

    def test_success_and_failure_are_real_grounded_cases(self):
        for initial, classification, final in ((OPEN, 'success', SEALED),
                                               (SEALED, 'error', SEALED)):
            with self.subTest(initial=initial):
                decision, event, public, pre, post = self.exercise(rows=initial)
                self.assertEqual((decision['provenance_valid'],
                                  decision['grounding_challenge_passed'],
                                  decision['contract_conformant']), (True, True, True))
                self.assertEqual(event['classification'], classification)
                self.assertEqual(pre['rows'], initial)
                self.assertEqual(post['rows'], final)
                self.assertEqual(json.loads(public['stdout'])['result'], final)

    def test_a_wrong_result_is_grounded_nonconformance(self):
        decision, event, public, pre, post = self.exercise('wrong_result')
        self.assertEqual((decision['provenance_valid'], decision['grounding_challenge_passed'],
                          decision['contract_conformant']), (True, True, False))
        self.assertEqual(post['rows'], SEALED)

    def test_b_wrong_durable_state_is_grounded_nonconformance(self):
        decision, event, public, pre, post = self.exercise('wrong_state')
        self.assertEqual((decision['grounding_challenge_passed'], decision['contract_conformant']),
                         (True, False))
        self.assertNotEqual(post['rows'], SEALED)
        self.assertEqual(json.loads(public['stdout'])['result'], SEALED)

    def test_c_false_internal_post_is_challenged(self):
        decision, event, public, pre, post = self.exercise('false_post')
        self.assertTrue(decision['provenance_valid'])
        self.assertFalse(decision['grounding_challenge_passed'])
        self.assertIsNone(decision['contract_conformant'])
        self.assertNotEqual(event['facts']['post'], post['rows'])

    def test_d_false_internal_input_is_challenged(self):
        decision, event, public, pre, post = self.exercise('false_input')
        self.assertFalse(decision['grounding_challenge_passed'])
        self.assertNotEqual(event['facts']['input'], public['input'])

    def test_e_wrong_operation_or_stale_provenance(self):
        decision, event, public, pre, post = self.exercise('wrong_identity')
        self.assertFalse(decision['grounding_challenge_passed'])
        self.assertIsNone(decision['contract_conformant'])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = ground.compile_target(root)
            (root / 'state.json').write_bytes(ground.canonical(OPEN))
            event, public, pre, post = ground.run_case(root, OPEN)
            event['provenance'] = 'stale'
            self.assertEqual(ground.challenge(root, event, public, pre, post)['reason'],
                             'grounding_mismatch')

    def test_f_modified_executable_invalidates_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ground.compile_target(root)
            (root / 'state.json').write_bytes(ground.canonical(OPEN))
            event, public, pre, post = ground.run_case(root, OPEN)
            artifact = root / 'operation.py'
            artifact.write_bytes(artifact.read_bytes() + b'\n# drift\n')
            decision = ground.challenge(root, event, public, pre, post)
            self.assertFalse(decision['provenance_valid'])
            self.assertFalse(decision['grounding_challenge_passed'])
            self.assertIsNone(decision['contract_conformant'])

    def test_g_failure_unintended_write_is_visible_and_nonconformant(self):
        decision, event, public, pre, post = self.exercise('failure_write', SEALED)
        self.assertEqual(event['classification'], 'error')
        self.assertNotEqual(pre['sha256'], post['sha256'])
        self.assertEqual((decision['grounding_challenge_passed'], decision['contract_conformant']),
                          (True, False))

    def test_wrong_failure_classification_is_grounded_semantic_nonconformance(self):
        decision, event, public, pre, post = self.exercise('wrong_failure_kind', SEALED)
        self.assertEqual(pre, post)
        self.assertEqual(json.loads(public['stdout'])['classification'], 'success')
        self.assertEqual((decision['provenance_valid'], decision['grounding_challenge_passed'],
                          decision['contract_conformant']), (True, True, False))

    def test_reproducible_generation_and_binding(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            one = ground.compile_target(first)
            two = ground.compile_target(second)
            self.assertEqual(one, two)
            self.assertEqual((Path(first) / 'operation.py').read_bytes(),
                             (Path(second) / 'operation.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
