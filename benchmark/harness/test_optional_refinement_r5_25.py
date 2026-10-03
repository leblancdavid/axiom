"""Independent non-task optional/refinement witnesses (prospective R5.25)."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from benchmark.semantic.optional_refinement_r5_25 import validate, generate, conforms


ROW = {'record': {'id': 'string', 'due': {'optional': 'instant'},
                  'other': {'optional': 'instant'}}}
CUTOFF = '2026-05-10T00:00:00Z'
ROWS = [{'id': 'absent'},
        {'id': 'early', 'due': '2026-05-09T23:59:59Z'},
        {'id': 'late', 'due': '2026-05-11T00:00:00Z'},
        {'id': 'equal', 'due': CUTOFF}]


def ref(*parts):
    return {'ref': list(parts)}


def source(order=False, field='due'):
    guard = {'presence': ref('item', field)}
    compare = {'before': [ref('item', field), ref('input', 'cutoff')]}
    return {'state': {'sequence': ROW}, 'input': {'record': {'cutoff': 'instant'}},
            'where': {'and': [compare, guard] if order else [guard, compare]}}


class OptionalRefinementR525(unittest.TestCase):
    def test_two_orders_and_absent_earlier_later_equal(self):
        for reverse in (False, True):
            contract = source(reverse)
            script = generate(contract)
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                program, state, payload, trace = (root / name for name in
                                                  ('program.py', 'state.json', 'input.json', 'trace.json'))
                program.write_text(script, encoding='utf-8')
                state.write_text(json.dumps(ROWS), encoding='utf-8')
                payload.write_text(json.dumps({'cutoff': CUTOFF}), encoding='utf-8')
                before = state.read_bytes()
                process = subprocess.run([sys.executable, str(program), str(state), str(payload), str(trace)],
                                         capture_output=True, text=True, check=True,
                                         env={**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[2])})
                actual = json.loads(process.stdout)
                observed = json.loads(trace.read_text(encoding='utf-8'))
                self.assertEqual([row['id'] for row in actual], ['early'])
                self.assertEqual(state.read_bytes(), before)
                self.assertEqual(observed['pre'], ROWS)
                self.assertEqual(observed['result'], actual)
                self.assertEqual(observed['post'], ROWS)
                self.assertFalse(observed['attempted_write'])
                self.assertTrue(conforms(contract, ROWS, {'cutoff': CUTOFF}, actual, ROWS))
                # Disposable emitted-code fault: the absent row satisfies the predicate.
                damaged = script.replace("if (('due' in item) and", "if (('due' not in item) or ('due' in item) and")
                self.assertNotEqual(damaged, script)
                program.write_text(damaged, encoding='utf-8')
                faulty_run = subprocess.run([sys.executable, str(program), str(state), str(payload), str(trace)],
                                            capture_output=True, text=True, check=True,
                                            env={**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[2])})
                faulty = json.loads(faulty_run.stdout)
                faulty_event = json.loads(trace.read_text(encoding='utf-8'))
                self.assertIn('absent', [row['id'] for row in faulty])
                self.assertEqual(faulty_event['result'], faulty)
                self.assertEqual(faulty_event['pre'], ROWS)
                self.assertFalse(faulty_event['attempted_write'])
                self.assertEqual(state.read_bytes(), before)  # grounded, read-only
                self.assertFalse(conforms(contract, ROWS, {'cutoff': CUTOFF}, faulty, ROWS))

    def test_semantic_mutations_without_lowerer_edits(self):
        rows = [dict(row, other='2026-05-01T00:00:00Z') for row in ROWS]
        for contract, expected in ((source(), ['early']),
                                   (source(field='other'), ['absent', 'early', 'late', 'equal'])):
            # The second mutation changes only the checked semantic field.
            namespace = {'__name__': 'prototype'}
            exec(generate(contract), namespace)
            population = rows if contract['where']['and'][0]['presence']['ref'][-1] == 'other' else ROWS
            self.assertEqual([r['id'] for r in namespace['execute'](population, {'cutoff': CUTOFF})], expected)
        contract = source()
        contract['where']['and'][1]['before'][1] = {'literal': {'type': 'instant',
                                                              'value': '2026-05-12T00:00:00Z'}}
        namespace = {'__name__': 'prototype'}
        exec(generate(contract), namespace)
        self.assertEqual([r['id'] for r in namespace['execute'](ROWS, {'cutoff': CUTOFF})],
                         ['early', 'late', 'equal'])

    def test_unsafe_combinations_rejected(self):
        variants = []
        bare = source()
        bare['where'] = bare['where']['and'][1]
        variants.append(bare)
        nonoptional = source()
        nonoptional['where']['and'][0] = {'presence': ref('item', 'id')}
        variants.append(nonoptional)
        wrong_field = source()
        wrong_field['where']['and'][0] = {'presence': ref('item', 'other')}
        variants.append(wrong_field)
        escaped = source()
        escaped['where'] = {'and': [source()['where'], bare['where']]}
        variants.append(escaped)
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                generate(variant)

    def test_generic_optional_shapes_and_null(self):
        from benchmark.semantic.typed_lowering_r5_12 import _type
        for inner, present in [('string', ''), ('integer', 0),
                               ({'record': {'key': 'string'}}, {'key': 'x'}),
                               ('instant', CUTOFF)]:
            shape = {'record': {'field': {'optional': inner}}}
            self.assertTrue(_type({}, shape))
            self.assertTrue(_type({'field': present}, shape))
            self.assertFalse(_type({'field': None}, shape))
            self.assertEqual(validate({'state': {'sequence': shape},
                                       'input': {'record': {}},
                                       'where': {'presence': ref('item', 'field')}})['state'],
                             {'sequence': shape})
        nullable = {'record': {'field': {'optional': {'nullable': 'instant'}}}}
        self.assertTrue(_type({}, nullable))
        self.assertTrue(_type({'field': None}, nullable))
        # Presence eliminates only optional; it must not silently eliminate nullable.
        model = source()
        model['state'] = {'sequence': {'record': {'due': {'optional': {'nullable': 'instant'}}}}}
        with self.assertRaises(ValueError):
            validate(model)


if __name__ == '__main__':
    unittest.main()
