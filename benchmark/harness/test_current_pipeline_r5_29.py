"""One publication archive, five checked operations, one durable program."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.capability_boundary_r5_22 import controlled_descriptor
from benchmark.semantic.refined_generator_r5_28 import canonical, sha
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic.unified_types_r5_27 import checked_plan


EARLY = '2026-01-01T01:00:00Z'
LATE = '2026-01-01T02:00:00Z'
CUTOFF = '2026-01-02T00:00:00Z'
ROW = {'record': {'code': 'string', 'created': 'instant', 'seen': {'optional': 'instant'},
                  'label': 'string'}}
STATE = {'sequence': ROW}


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape):
    return {'literal': {'value': value, 'type': shape}}


def selected(slot='pre', field='seen', exact=True):
    parts = [{'present': ref('item', field)},
             {'before': [ref('item', field), ref('input', 'cutoff')]}]
    if exact:
        parts.append({'equals': [ref('item', 'code'), ref('input', 'target')]})
    return {'select': {'source': ref(slot), 'where': {'and': parts}}}


def application():
    inp = {'record': {'target': 'string', 'cutoff': 'instant', 'label': 'string',
                      'seen': {'optional': 'instant'}, 'preferred': {'optional': 'string'}}}
    identifier = {'external': {'source': 'fresh_unique_id'}}
    timestamp = {'external': {'source': 'utc_clock'}}
    label = {'fallback': {'value': ref('input', 'preferred'), 'default': ref('input', 'label')}}
    record = {'record': {'code': identifier, 'created': timestamp,
                         'seen': ref('input', 'seen'), 'label': label}}
    def branch(tag, when, value, shape, transition):
        return {'tag': tag, 'when': when, 'value': value, 'value_type': shape,
                'transition': transition}
    def operation(name, value, shape, transition, guard=None):
        return {'id': 'archive.' + name, 'version': 'R5.27', 'input': inp,
                'state': STATE, 'branches': [
                    branch('ok', guard or {'equals': [lit(1, 'integer'), lit(1, 'integer')]},
                           value, shape, transition),
                    branch('skip', None, lit('skip', 'string'), 'string', {'preserve': True})]}
    matched = {'equals': [{'cardinality': selected()}, lit(1, 'integer')]}
    create = operation('create', record, ROW, {'relations': [{'exact_frame': {
        'collection': None, 'identity': 'code', 'record': record}}]})
    query = operation('query', selected(), STATE, {'preserve': True})
    ordered = operation('ordered', {'order': {'source': selected(exact=False),
                                              'keys': ['created', 'code']}}, STATE,
                        {'preserve': True})
    replace = operation('replace', {'project': {'row': {'sole': {'select': {
        'source': ref('post'), 'where': {'equals': [ref('item', 'code'), ref('input', 'target')]}}}},
        'fields': ['code', 'label']}}, {'record': {'code': 'string', 'label': 'string'}},
        {'relations': [{'replace_field': {'collection': None, 'key': 'code',
                                         'match': ref('input', 'target'), 'field': 'label',
                                         'value': ref('input', 'label')}}]}, matched)
    remove = operation('remove', {'cardinality': selected()}, 'integer',
        {'relations': [{'remove': {'collection': None, 'identity': 'code',
                                   'match': ref('input', 'target')}}]}, matched)
    return {'id': 'publication.archive', 'state': STATE,
            'operations': {'create': create, 'query': query, 'ordered': ordered,
                           'replace': replace, 'remove': remove}}


def data(target, seen=EARLY, label='old', cutoff=CUTOFF):
    return {'target': target, 'cutoff': cutoff, 'label': label, 'seen': seen}


class CurrentPipelineR529(unittest.TestCase):
    def run_step(self, model, root, name, inp, caps=None):
        event, public, before, after = pipeline.observe(root, name, inp, caps)
        verdict = pipeline.challenge(model, root, event, public, before, after)
        return verdict, json.loads(public['stdout']), before, after

    def test_single_program_continuity_and_read_after_write(self):
        model = application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical([]))
            steps = [('create', data('A', EARLY), controlled_descriptor({'fresh_unique_id': 'A', 'utc_clock': LATE})),
                     ('create', data('B', LATE), controlled_descriptor({'fresh_unique_id': 'B', 'utc_clock': EARLY})),
                     ('query', data('A'), None), ('ordered', data('A'), None),
                     ('replace', data('A', label='new'), None), ('query', data('A'), None),
                     ('remove', data('A'), None), ('query', data('A'), None)]
            previous = None
            results = []
            for name, inp, caps in steps:
                verdict, result, before, after = self.run_step(model, root, name, inp, caps)
                self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True,
                                           'conformant': True}, name)
                if previous is not None:
                    self.assertEqual(previous, before)
                previous = after
                results.append(result)
            self.assertEqual(results[2]['value'][0]['code'], 'A')
            self.assertEqual([r['code'] for r in results[3]['value']], ['B', 'A'])
            self.assertEqual(results[4]['value'], {'code': 'A', 'label': 'new'})
            self.assertEqual(results[5]['value'][0]['label'], 'new')
            self.assertEqual(results[6]['value'], 1)
            self.assertEqual(results[7]['value'], [])
            self.assertEqual([r['code'] for r in json.loads(previous)], ['B'])

    def test_semantic_mutations_and_rejection(self):
        model = application()
        bad = copy.deepcopy(model)
        bad['operations']['query']['branches'][0]['value']['select']['where']['and'][0] = {
            'present': ref('item', 'label')}
        with self.assertRaisesRegex(ValueError, 'presence requires optional field'):
            pipeline.checked(bad)
        rows = [dict(code='A', created=LATE, seen=EARLY, label='old'),
                dict(code='B', created=EARLY, seen=LATE, label='old')]
        changes = [
            ('cutoff', 'query', lambda m: m['operations']['query']['branches'][0]['value']['select']['where']['and'][1]['before'].__setitem__(1, lit(EARLY, 'instant')),
             data('A'), 'value', []),
            ('ordering', 'ordered', lambda m: m['operations']['ordered']['branches'][0]['value']['order']['keys'].__setitem__(slice(None), ['code']),
             data('A'), 'value', rows),
            ('replacement', 'replace', lambda m: m['operations']['replace']['branches'][0]['transition']['relations'][0]['replace_field'].__setitem__('value', lit('fixed', 'string')),
             data('A', label='new'), 'value', {'code': 'A', 'label': 'fixed'}),
            ('removal', 'remove', lambda m: (m['operations']['remove']['branches'][0]['when']['equals'][0]['cardinality']['select']['where']['and'][2]['equals'].__setitem__(1, lit('B', 'string')),
                    m['operations']['remove']['branches'][0]['transition']['relations'][0]['remove'].__setitem__('match', lit('B', 'string'))),
             data('A'), 'value', 1),
        ]
        for name, operation, change, inp, key, expected in changes:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                mutated = copy.deepcopy(model)
                change(mutated)
                root = Path(folder)
                pipeline.generate(mutated, root)
                (root / 'state.json').write_bytes(canonical(rows))
                verdict, result, _, after = self.run_step(mutated, root, operation, inp)
                self.assertTrue(verdict['conformant'])
                self.assertEqual(result[key], expected)
                with tempfile.TemporaryDirectory() as baseline_folder:
                    baseline = Path(baseline_folder)
                    pipeline.generate(model, baseline)
                    (baseline / 'state.json').write_bytes(canonical(rows))
                    baseline_verdict, baseline_result, _, baseline_after = self.run_step(model, baseline, operation, inp)
                    self.assertTrue(baseline_verdict['conformant'])
                    self.assertNotEqual((result, after), (baseline_result, baseline_after))
                if name == 'removal':
                    self.assertEqual([row['code'] for row in json.loads(after)], ['A'])

    def test_persisted_present_optional(self):
        model = application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical([]))
            verdict, _, _, _ = self.run_step(model, root, 'create', data('B', EARLY),
                controlled_descriptor({'fresh_unique_id': 'B', 'utc_clock': LATE}))
            self.assertTrue(verdict['conformant'])
            verdict, result, _, _ = self.run_step(model, root, 'ordered', data('A'))
            self.assertTrue(verdict['conformant'])
            self.assertEqual([row['code'] for row in result['value']], ['B'])

    def test_unsupported_shapes_and_unguarded_optional_reject(self):
        mismatch = application()
        mismatch['operations']['remove']['state'] = {'record': {'rows': STATE}}
        with self.assertRaisesRegex(ValueError, 'operation state or identity mismatch'):
            pipeline.checked(mismatch)
        unsafe = application()
        unsafe['operations']['query']['branches'][0]['value']['select']['where']['and'].pop(0)
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            pipeline.checked(unsafe)
        unknown = application()
        unknown['operations']['remove']['branches'][0]['transition'] = {'relations': [
            {'unrecognized': {}}]}
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LOWERING_CAPABILITY'):
            pipeline.checked(unknown)

    def test_five_faults_on_authoritative_program(self):
        model = application()
        contract = model['operations']['query']
        predicate = emitter.expression(contract['branches'][0]['value']['select']['where'],
            {'post': 'post', 'item': '_element_1'},
            {'input': contract['input'], 'pre': contract['state']},
            plan=checked_plan(contract))

        def faulty(root, old, new):
            artifact = root / 'operation.py'
            source = artifact.read_text(encoding='utf-8')
            self.assertIn(old, source)
            artifact.write_bytes(source.replace(old, new, 1).encode())
            path = root / 'provenance.json'
            manifest = json.loads(path.read_bytes())
            manifest['artifact'] = sha(artifact.read_bytes())
            manifest['generation'] = sha(canonical({k: v for k, v in manifest.items()
                                                    if k != 'generation'}))
            path.write_bytes(canonical(manifest))

        cases = [
            ('A', 'query', ' if ' + predicate + ']',
             " if (('seen' not in _element_1) or " + predicate + ')]',
             [dict(code='A', created=EARLY, label='old')], data('A')),
            ('B', 'ordered', "instant_key(_order_key_1['created'])",
             "-instant_key(_order_key_1['created']).timestamp()",
             [dict(code='A', created=EARLY, seen=EARLY, label='old'),
              dict(code='B', created=LATE, seen=EARLY, label='old')], data('A')),
            ('C', 'replace', "{**item, 'label': input['label']}",
             "{**item, 'seen': input['cutoff']}",
             [dict(code='A', created=EARLY, seen=EARLY, label='old')], data('A', label='new')),
            ('D', 'create', "'created': EXTERNAL['utc_clock']",
             "'created': '2026-01-01T02:00:00Z'", [], data('A')),
        ]
        for label, operation, old, new, rows, inp in cases:
            with self.subTest(fault=label), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                pipeline.generate(model, root)
                faulty(root, old, new)
                (root / 'state.json').write_bytes(canonical(rows))
                caps = controlled_descriptor({'fresh_unique_id': 'A', 'utc_clock': EARLY}) if label == 'D' else None
                event, public, before, after = pipeline.observe(root, operation, inp, caps)
                self.assertEqual(pipeline.challenge(model, root, event, public, before, after),
                                 {'provenance_valid': True, 'grounded': True, 'conformant': False})
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical([]))
            _, _, _, previous = self.run_step(model, root, 'create', data('A'),
                controlled_descriptor({'fresh_unique_id': 'A', 'utc_clock': EARLY}))
            # Fault E is an out-of-band durable write between public invocations.
            changed = json.loads(previous)
            changed[0]['label'] = 'intrusion'
            (root / 'state.json').write_bytes(canonical(changed))
            _, _, actual_pre, _ = self.run_step(model, root, 'query', data('A'))
            self.assertNotEqual(previous, actual_pre)


if __name__ == '__main__':
    unittest.main()
