"""Independent R5.24 semantic type-closure probes, outside historical locks."""

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic.capability_boundary_r5_22 import parse_instant
from benchmark.semantic.generative_evidence_r5_13 import challenge, observe
from benchmark.semantic.generative_r5_13 import canonical, generate, typed
from benchmark.semantic.instant_ordering_r5_24 import evaluate, plan, rank


ROW = {'code': 'string', 'release_at': 'instant', 'edition': 'integer'}
ROWS = [
    {'code': 'c', 'release_at': '2026-01-01T00:00:00.10Z', 'edition': 3},
    {'code': 'b', 'release_at': '2026-01-01T00:00:00Z', 'edition': 2},
    {'code': 'a', 'release_at': '2025-12-31T23:59:59Z', 'edition': 1},
]


class ChronologicalClosure(unittest.TestCase):
    def test_instant_domain_and_semantic_only_key_mutations(self):
        shape = {'record': ROW}
        self.assertEqual(parse_instant('2026-01-01T00:00:00Z'),
                         parse_instant('2026-01-01T00:00:00.000Z'))
        for keys in (['release_at'], ['release_at', 'code'],
                     ['release_at', 'edition']):
            self.assertEqual(plan(shape, keys)[0][1], 'instant')
            self.assertEqual([item['code'] for item in evaluate(ROWS, shape, keys)], ['a', 'b', 'c'])
        tied = [ROWS[1], {'code': 'a', 'release_at': ROWS[1]['release_at'], 'edition': 1}]
        self.assertEqual([r['code'] for r in evaluate(tied, shape, ['release_at', 'code'])], ['a', 'b'])
        self.assertEqual([r['code'] for r in evaluate(tied, shape, ['release_at', 'edition'])], ['a', 'b'])
        tied[0] = {**tied[0], 'edition': 0}
        self.assertEqual([r['code'] for r in evaluate(tied, shape, ['release_at', 'edition'])], ['b', 'a'])
        self.assertEqual([r['code'] for r in evaluate(tied, shape, ['code'])], ['a', 'b'])

    def test_equal_instants_and_wrong_order_semantic_counterexample(self):
        rows = [ROWS[1], {'code': 'a', 'release_at': ROWS[1]['release_at'], 'edition': 1}]
        keys = plan({'record': ROW}, ['release_at'])
        self.assertEqual(rank(rows[0], keys), rank(rows[1], keys))
        self.assertEqual({r['code'] for r in evaluate(rows, {'record': ROW}, ['release_at'])}, {'a', 'b'})
        wrong = list(reversed(evaluate(ROWS, {'record': ROW}, ['release_at'])))
        self.assertNotEqual([rank(row, keys) for row in wrong],
                            sorted(rank(row, keys) for row in wrong))

    def test_optional_and_nullable_instant_keys_reject(self):
        for wrapped in ({'optional': 'instant'}, {'nullable': 'instant'}):
            with self.assertRaisesRegex(ValueError, 'non-orderable key'):
                plan({'record': {'release_at': wrapped}}, ['release_at'])
        with self.assertRaisesRegex(ValueError, 'ordering needs typed sequence'):
            evaluate([{'code': 'x', 'release_at': 'not-an-instant', 'edition': 1}],
                     {'record': ROW}, ['release_at'])

    def test_locked_generator_still_rejects_instant_before_emission(self):
        source = {'id': 'publication.release.order', 'version': '1',
                  'input': {'record': {'request': 'string'}},
                  'state': {'sequence': {'record': ROW}},
                  'branches': [
                      {'tag': 'listed', 'when': {'equals': [
                          {'ref': ['input', 'request']},
                          {'literal': {'type': 'string', 'value': 'list'}}]},
                       'value_type': {'sequence': {'record': ROW}},
                       'value': {'order': {'source': {'ref': ['pre']}, 'keys': ['release_at']}},
                       'transition': {'preserve': True}},
                      {'tag': 'unknown', 'when': None,
                       'value': {'literal': {'type': 'string', 'value': 'unknown'}},
                       'transition': {'preserve': True}}]}
        with self.assertRaisesRegex(ValueError, 'non-orderable key'):
            typed(source)


class BindingBoundary(unittest.TestCase):
    def test_omitted_explicit_and_malformed_at_input_boundary(self):
        source = {'id': 'publication.edition.default', 'version': '1',
                  'input': {'record': {'edition': {'optional': 'string'}}},
                  'state': {'sequence': {'record': {'code': 'string'}}},
                  'branches': [
                      {'tag': 'edition', 'when': {'equals': [
                          {'fallback': {'value': {'ref': ['input', 'edition']},
                                        'default': {'literal': {'type': 'string', 'value': 'standard'}}}},
                          {'literal': {'type': 'string', 'value': 'standard'}}]},
                       'value': {'fallback': {'value': {'ref': ['input', 'edition']},
                                             'default': {'literal': {'type': 'string', 'value': 'standard'}}}},
                       'transition': {'preserve': True}},
                      {'tag': 'alternate', 'when': None,
                       'value': {'literal': {'type': 'string', 'value': 'alternate'}},
                       'transition': {'preserve': True}}]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(source, root)
            for inp in ({}, {'edition': 'standard'}, {'edition': 'extended'}):
                (root / 'state.json').write_bytes(canonical([]))
                event, public, before, after = observe(root, inp)
                verdict = challenge(source, root, event, public, before, after)
                self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
                self.assertEqual(event['input'], inp)
                self.assertEqual(before, after)
            (root / 'state.json').write_bytes(canonical([]))
            (root / 'trace.json').unlink()
            event, public, before, after = observe(root, {'edition': 5})
            self.assertIsNone(event)
            self.assertNotEqual(public['exit'], 0)
            self.assertEqual(before, after)


class Inventory(unittest.TestCase):
    def test_matrix_has_checked_dimensions(self):
        root = Path(__file__).resolve().parents[1] / 'results' / 'phase5c'
        matrix = json.loads((root / 'R5_24-type-matrix.json').read_text(encoding='utf-8'))
        fields = {'accepts', 'produces', 'elements', 'optional', 'refinement',
                  'state', 'outcome', 'generation', 'verifier'}
        self.assertGreaterEqual(len(matrix['relations']), 17)
        for relation in matrix['relations'].values():
            self.assertEqual(set(relation), fields)
        self.assertIn('instant unsupported', matrix['relations']['order']['generation'])


if __name__ == '__main__':
    unittest.main()
