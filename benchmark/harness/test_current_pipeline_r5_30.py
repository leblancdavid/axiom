"""Structured assembly and independent durable witnesses for the current entry."""

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.harness.test_current_pipeline_r5_29 import (
    application, data, EARLY, LATE)
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.capability_boundary_r5_22 import controlled_descriptor
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


class CurrentPipelineR530(unittest.TestCase):
    def test_current_entry_normalization_order_and_same_shape_defaults(self):
        row = {'record': {'code': 'string', 'rank': 'integer',
                          'label': {'optional': 'string'}, 'flag': {'optional': 'boolean'}}}
        state = {'record': {'rows': {'sequence': row}, 'version': 'integer'}}
        inp = {'record': {'tags': {'sequence': 'string'}}}
        yes = {'equals': [{'literal': {'type': 'integer', 'value': 1}},
                          {'literal': {'type': 'integer', 'value': 1}}]}
        def operation(name, value, shape, transition):
            return {'id': 'inventory.' + name, 'version': 'R5.27', 'input': inp,
                    'state': state, 'branches': [
                        {'tag': 'ok', 'when': yes, 'value': value, 'value_type': shape,
                         'transition': transition},
                        {'tag': 'skip', 'when': None, 'value': {'literal': {'type': 'string', 'value': 'skip'}},
                         'value_type': 'string', 'transition': {'preserve': True}}]}
        norm = {'stable_unique': {'sequence': {'map': {'sequence': {'ref': ['input', 'tags']},
                                                     'transform': 'trim'}}, 'equality': 'case_sensitive_string'}}
        order = {'order': {'source': {'ref': ['pre', 'rows']}, 'keys': ['rank', 'code']}}
        migration = {'relations': [
            {'default_missing': {'collection': 'rows', 'identity': 'code', 'field': 'label',
                                 'value': {'literal': {'type': 'string', 'value': 'untitled'}}}},
            {'default_missing': {'collection': 'rows', 'identity': 'code', 'field': 'flag',
                                 'value': {'literal': {'type': 'boolean', 'value': False}}}},
            {'post_equals': {'field': 'version', 'value': {'literal': {'type': 'integer', 'value': 2}}}}]}
        model = {'id': 'inventory', 'state': state, 'operations': {
            'normalize': operation('normalize', norm, {'sequence': 'string'}, {'preserve': True}),
            'ordered': operation('ordered', order, {'sequence': row}, {'preserve': True}),
            'migrate': operation('migrate', {'cardinality': {'ref': ['post', 'rows']}},
                                 'integer', migration)}}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical({'rows': [
                {'code': 'B', 'rank': 2}, {'code': 'A', 'rank': 1}], 'version': 1}))
            for name, expected in [('normalize', ['a', 'b']),
                                   ('ordered', ['A', 'B']), ('migrate', 2)]:
                event, public, before, after = pipeline.observe(root, name,
                    {'tags': [' a ', 'b', 'a']})
                verdict = pipeline.challenge(model, root, event, public, before, after)
                self.assertEqual(verdict['conformant'], True, name)
                value = json.loads(public['stdout'])['value']
                self.assertEqual([row['code'] for row in value] if name == 'ordered' else value,
                                 expected)
            self.assertEqual(json.loads(after)['version'], 2)
            self.assertTrue(all(row['label'] == 'untitled' and row['flag'] is False
                                for row in json.loads(after)['rows']))

    def test_deterministic_structured_assembly_and_provenance(self):
        model = application()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            one, two = Path(first), Path(second)
            self.assertEqual(pipeline.generate(model, one), pipeline.generate(model, two))
            self.assertEqual((one / 'operation.py').read_bytes(), (two / 'operation.py').read_bytes())
            manifest = json.loads((one / 'provenance.json').read_bytes())
            self.assertEqual(manifest['units'], {name: sha(canonical(contract))
                for name, contract in model['operations'].items()})
            (one / 'state.json').write_bytes(canonical([]))
            event, public, before, after = pipeline.observe(one, 'create', data('A'),
                controlled_descriptor({'fresh_unique_id': 'A', 'utc_clock': EARLY}))
            self.assertEqual(event['operation'], 'create')
            self.assertEqual(pipeline.challenge(model, one, event, public, before, after)['conformant'], True)

    def test_omitted_optional_persists_absence_and_refinement(self):
        model = application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical([]))
            omitted = data('A')
            del omitted['seen']
            supplied = data('B', EARLY)
            supplied['preferred'] = 'explicit-label'
            for name, inp in [('A', omitted), ('B', supplied)]:
                event, public, before, after = pipeline.observe(root, 'create', inp,
                    controlled_descriptor({'fresh_unique_id': name, 'utc_clock': LATE}))
                self.assertEqual(pipeline.challenge(model, root, event, public, before, after)['conformant'], True)
            rows = json.loads((root / 'state.json').read_bytes())
            self.assertNotIn('seen', rows[0])
            self.assertEqual(rows[1]['seen'], EARLY)
            self.assertEqual(rows[0]['label'], 'old')
            self.assertEqual(rows[1]['label'], 'explicit-label')
            # Selection witnesses refine only the PRESENT row, without making
            # the absent field appear during construction or readback.
            event, public, before, after = pipeline.observe(root, 'query', data('B'))
            self.assertEqual(pipeline.challenge(model, root, event, public, before, after)['conformant'], True)
            self.assertEqual([row['code'] for row in json.loads(public['stdout'])['value']], ['B'])
            self.assertEqual(before, after)

    def test_operation_caused_unintended_write_is_grounded_not_conformant(self):
        model = application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            rows = [{'code': 'A', 'created': EARLY, 'seen': EARLY, 'label': 'old'},
                    {'code': 'B', 'created': LATE, 'seen': EARLY, 'label': 'old'}]
            (root / 'state.json').write_bytes(canonical(rows))
            original = (root / 'operation.py').read_text(encoding='utf-8')
            # Disposable target fault, injected inside the query operation:
            # return the same public value but overwrite an unrelated row.
            start = original.index('def execute_1(')
            end = original.index('def execute_2(')
            body = original[start:end]
            self.assertIn('        post = pre\n        write = False', body)
            body = body.replace('        post = pre\n        write = False',
                '        post = [{**row, "label": "intrusion"} if row["code"] == "B" else row for row in pre]\n        write = True', 1)
            artifact = root / 'operation.py'
            artifact.write_bytes((original[:start] + body + original[end:]).encode())
            manifest_path = root / 'provenance.json'
            manifest = json.loads(manifest_path.read_bytes())
            manifest['artifact'] = sha(artifact.read_bytes())
            manifest['generation'] = sha(canonical({k: v for k, v in manifest.items() if k != 'generation'}))
            manifest_path.write_bytes(canonical(manifest))
            event, public, before, after = pipeline.observe(root, 'query', data('A'))
            self.assertEqual(json.loads(public['stdout'])['value'], rows[:1])
            self.assertEqual(json.loads(before), rows)
            self.assertEqual(json.loads(after)[1]['label'], 'intrusion')
            self.assertEqual(pipeline.challenge(model, root, event, public, before, after),
                             {'provenance_valid': True, 'grounded': True, 'conformant': False})
            next_event, next_public, next_before, next_after = pipeline.observe(root, 'query', data('A'))
            self.assertEqual(after, next_before)
            self.assertNotEqual(before, next_before)


if __name__ == '__main__':
    unittest.main()
