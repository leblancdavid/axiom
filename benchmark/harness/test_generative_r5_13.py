"""Prospective non-task generation, source mutations and challenged execution."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic.generative_r5_13 import generate, typed, UnsupportedLowering
from benchmark.semantic.generative_evidence_r5_13 import observe, challenge
from benchmark.semantic.generative_r5_13 import canonical


ROOT = Path(__file__).resolve().parents[1] / 'semantic'
ROWS = [{'code': 'c1', 'seal': 'locked', 'zone': 'south'},
        {'code': 'c2', 'seal': 'open', 'zone': 'north'}]


def load(letter):
    return json.loads((ROOT / ('r5_13-contract-' + letter + '.json')).read_bytes())


def ref(*parts):
    return {'ref': list(parts)}


class GenerativeLowering(unittest.TestCase):
    def case(self, contract, rows, inp=None, fault=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = generate(contract, root, fault=fault)
            (root / 'state.json').write_bytes(canonical(rows))
            event, public, before, after = observe(root, inp or {'code': 'c1'})
            verdict = challenge(contract, root, event, public, before, after)
            return manifest, event, json.loads(public['stdout']), json.loads(after), verdict, before, after

    def test_semantic_value_and_structural_mutations(self):
        a, b, c = (load(k) for k in 'abc')
        for contract, outcome, final_seal in ((a, 'released', 'open'),
                                              (b, 'unavailable', 'locked'),
                                              (c, 'unavailable', 'locked')):
            with self.subTest(contract=contract['version']):
                manifest, event, public, post, verdict, before, after = self.case(contract, ROWS)
                self.assertEqual(public['kind'], outcome)
                self.assertEqual(post[0]['seal'], final_seal)
                self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                                  verdict['conformant']), (True, True, True))
                if outcome == 'unavailable':
                    self.assertEqual(before, after)
                    self.assertFalse(event['attempted_write'])
        self.assertEqual(self.case(b, ROWS, {'code': 'c2'})[2]['kind'], 'released')
        self.assertEqual(self.case(c, ROWS, {'code': 'c2'})[2]['kind'], 'released')
        with tempfile.TemporaryDirectory() as x, tempfile.TemporaryDirectory() as y:
            ma, mb = generate(a, x), generate(b, y)
            self.assertNotEqual(ma['contract'], mb['contract'])
            self.assertNotEqual(ma['artifact'], mb['artifact'])
            mc = generate(c, y)
            self.assertNotEqual(mb['artifact'], mc['artifact'])

    def test_novel_composition_without_lowerer_edit(self):
        d = copy.deepcopy(load('a'))
        d['version'] = 'D'
        # Different Boolean structure, different state field and typed result expression.
        d['branches'][0]['when'] = {'not': {'equals': [ref('input', 'code'),
                                                      {'literal': {'type': 'string', 'value': 'blocked'}}]}}
        d['branches'][0]['transition']['replace_field']['field'] = 'zone'
        d['branches'][0]['transition']['replace_field']['value']['literal']['value'] = 'east'
        d['branches'][0]['value'] = {'literal': {'type': 'string', 'value': 'moved'}}
        result = self.case(d, ROWS)
        self.assertEqual(result[2], {'kind': 'released', 'value': 'moved'})
        self.assertEqual(result[3][0], {'code': 'c1', 'seal': 'locked', 'zone': 'east'})
        self.assertTrue(result[4]['conformant'])
        self.assertEqual(self.case(d, ROWS, {'code': 'blocked'})[2]['kind'], 'unavailable')

    def test_valid_unsupported_and_invalid_typed_combinations(self):
        unsupported = copy.deepcopy(load('a'))
        unsupported['branches'][0]['when'] = {'default_missing': [ref('pre'), ref('pre')]}
        with self.assertRaisesRegex(UnsupportedLowering, 'default_missing'):
            generate(unsupported, Path('.'))
        unsupported = copy.deepcopy(load('a'))
        unsupported['branches'][0]['transition'] = {'default_missing': [ref('pre'), ref('pre')]}
        with self.assertRaisesRegex(UnsupportedLowering, 'state relation'):
            typed(unsupported)
        invalid = copy.deepcopy(load('a'))
        invalid['branches'][0]['when'] = {'equals': [ref('input', 'code'), ref('pre')]}
        with self.assertRaisesRegex(ValueError, 'type mismatch'):
            typed(invalid)
        invalid = copy.deepcopy(load('a'))
        invalid['branches'][0]['transition']['replace_field']['value'] = {
            'literal': {'type': 'integer', 'value': 4}}
        with self.assertRaisesRegex(ValueError, 'assignment type mismatch'):
            typed(invalid)
        invalid = copy.deepcopy(load('a'))
        invalid['branches'][0]['value'] = {'literal': {'type': 'integer', 'value': 4}}
        with self.assertRaisesRegex(ValueError, 'payload type mismatch'):
            typed(invalid)

    def test_grounding_fault_drift_and_determinism(self):
        a = load('a')
        fault = self.case(a, ROWS, fault=True)
        self.assertEqual((fault[4]['provenance_valid'], fault[4]['grounded'],
                          fault[4]['conformant']), (True, True, False))
        with tempfile.TemporaryDirectory() as x, tempfile.TemporaryDirectory() as y:
            one, two = generate(a, x), generate(a, y)
            self.assertEqual(one, two)
            self.assertEqual((Path(x) / 'operation.py').read_bytes(),
                             (Path(y) / 'operation.py').read_bytes())
            root = Path(x)
            (root / 'state.json').write_bytes(canonical(ROWS))
            event, public, before, after = observe(root, {'code': 'c1'})
            event['post'] = ROWS
            self.assertFalse(challenge(a, root, event, public, before, after)['grounded'])
            event, public, before, after = observe(root, {'code': 'c1'})
            (root / 'operation.py').write_bytes((root / 'operation.py').read_bytes() + b'# manual drift\n')
            self.assertFalse(challenge(a, root, event, public, before, after)['provenance_valid'])
            self.assertEqual(generate(a, root), one)
            self.assertEqual((root / 'operation.py').read_bytes(), (Path(y) / 'operation.py').read_bytes())

    def test_runtime_rejects_mistyped_input_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(load('a'), root)
            (root / 'state.json').write_bytes(canonical(ROWS))
            event, public, before, after = observe(root, {'code': 7})
            self.assertNotEqual(public['exit'], 0)
            self.assertIsNone(event)
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
