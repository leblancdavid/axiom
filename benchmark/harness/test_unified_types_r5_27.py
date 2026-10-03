"""Prospective R5.27 typed-analysis boundary, independent of task operations."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import generative_r5_13 as base
from benchmark.semantic.generative_evidence_r5_13 import observe, challenge
from benchmark.semantic.capability_boundary_r5_22 import controlled_descriptor


def ref(*parts):
    return {'ref': list(parts)}


def lit(value, shape):
    return {'literal': {'type': shape, 'value': value}}


FIELDS = {'code': 'string', 'seen': {'optional': 'instant'},
          'other': {'optional': 'instant'}, 'label': 'string'}
STATE = {'sequence': {'record': FIELDS}}


def selected(reverse=False):
    parts = [{'present': ref('item', 'seen')},
             {'before': [ref('item', 'seen'), ref('input', 'cutoff')]}]
    return {'select': {'source': ref('pre'), 'where': {'and': parts[::-1] if reverse else parts}}}


def contract(kind='read', reverse=False):
    source = selected(reverse)
    state = STATE
    if kind == 'read':
        value = {'order': {'source': source, 'keys': ['seen', 'code']}}
        transition = {'preserve': True}
        result = STATE
    else:
        match = ref('input', 'target')
        if kind == 'insert':
            state = {'sequence': {'record': {'code': 'string', 'seen': 'instant', 'label': 'string'}}}
            value = {'record': {'code': ref('input', 'target'),
                                'seen': {'external': {'source': 'utc_clock'}},
                                'label': ref('input', 'label')}}
            transition = {'relations': [{'exact_frame': {'collection': None,
                             'identity': 'code', 'record': value}}]}
            result = {'record': {'code': 'string', 'seen': 'instant', 'label': 'string'}}
        else:
            value = {'cardinality': source}
            rule = ({'remove': {'collection': None, 'identity': 'code', 'match': match}}
                    if kind == 'remove' else {'replace_field': {
                        'collection': None, 'key': 'code', 'match': match,
                        'field': 'label', 'value': ref('input', 'label')}})
            transition = {'relations': [rule]}
            result = 'integer'
    guard = {'equals': [ref('input', 'target'), lit('go', 'string')]}
    if kind in ('remove', 'replace'):
        source['select']['where']['and'].append({'equals': [ref('item', 'code'), ref('input', 'target')]})
        guard = {'equals': [{'cardinality': source}, lit(1, 'integer')]}
    return {'id': 'archive.' + kind, 'version': 'R5.27',
            'input': {'record': {'target': 'string', 'cutoff': 'instant', 'label': 'string'}},
            'state': state,
            'branches': [
                {'tag': 'ok', 'when': guard,
                 'value': value, 'value_type': result, 'transition': transition},
                {'tag': 'skip', 'when': None, 'value': lit('skip', 'string'),
                 'value_type': 'string', 'transition': {'preserve': True}}]}


class UnifiedTypesR527(unittest.TestCase):
    def test_ordered_refinement_both_conjunction_orders(self):
        for reverse in (False, True):
            self.assertEqual(types.ordering_plan(contract(reverse=reverse)['branches'][0]['value']['order'],
                             {'input': contract()['input'], 'pre': STATE})['keys'],
                             [('seen', 'instant'), ('code', 'string')])
            types.typed(contract(reverse=reverse))

    def test_transition_operands_are_checked_by_the_same_analyzer(self):
        self.assertIsNotNone(types.typed(contract('insert')))
        for kind in ('remove', 'replace'):
            with self.subTest(kind=kind):
                types.typed(contract(kind))
        bad = contract('replace')
        bad['branches'][0]['transition']['relations'][0]['replace_field']['value'] = lit(3, 'integer')
        with self.assertRaisesRegex(ValueError, 'replacement field or type'):
            types.typed(bad)

    def test_optional_scope_and_instant_rejections(self):
        model = contract()
        where = model['branches'][0]['value']['order']['source']['select']['where']
        wrong = copy.deepcopy(model)
        wrong['branches'][0]['value']['order']['source']['select']['where']['and'][0] = {'present': ref('item', 'other')}
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            types.typed(wrong)
        escaped = copy.deepcopy(model)
        escaped['branches'][0]['value']['order']['source']['select']['where'] = {'and': [
            where, {'before': [ref('item', 'seen'), ref('input', 'cutoff')]}]}
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            types.typed(escaped)
        naked = copy.deepcopy(model)
        naked['branches'][0]['value']['order']['source'] = ref('pre')
        with self.assertRaisesRegex(ValueError, 'optional key needs selection presence'):
            types.typed(naked)
        required = copy.deepcopy(model)
        required['branches'][0]['value']['order']['source']['select']['where']['and'][0] = {'present': ref('item', 'code')}
        with self.assertRaisesRegex(ValueError, 'presence requires optional field'):
            types.typed(required)

    def test_legacy_generation_bridge_external_insertion(self):
        model = contract('insert')
        when = '2026-04-09T12:30:00Z'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            types.generate_legacy_subset(model, root)
            (root / 'state.json').write_bytes(base.canonical([]))
            event, public, before, after = observe(root,
                {'target': 'go', 'cutoff': when, 'label': 'sample'},
                controlled_descriptor({'utc_clock': when}))
            self.assertEqual(json.loads(public['stdout'])['value']['seen'], when)
            self.assertEqual(json.loads(after)[0]['seen'], event['externals']['utc_clock'])
            self.assertEqual(challenge(model, root, event, public, before, after),
                             {'provenance_valid': True, 'grounded': True, 'conformant': True})
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, 'unsupported relation: present|non-orderable key'):
            types.generate_legacy_subset(contract(), Path(folder))


if __name__ == '__main__':
    unittest.main()
