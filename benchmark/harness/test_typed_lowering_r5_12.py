"""Non-task, non-benchmark typed operation-contract lowering challenges."""

import copy
import unittest

from benchmark.semantic.typed_lowering_r5_12 import UnsupportedLowering, lower


ROW = {'record': {'code': 'string', 'active': 'boolean', 'weight': 'integer'}}
SEQUENCE = {'sequence': ROW}


def ref(*parts):
    return {'ref': list(parts)}


def contract():
    chosen = {'select': {'source': ref('pre'), 'where': {'equals': [ref('item', 'active'),
                                                                   {'literal': {'type': 'boolean', 'value': True}}]}}}
    return {'input': {'record': {}}, 'state': SEQUENCE,
            'outcomes': {'success': {'value': {'record': {'items': SEQUENCE, 'count': 'integer'}},
                                    'constraints': [
                                        {'equals': [ref('post'), ref('pre')]},
                                        {'equals': [ref('outcome', 'items'),
                                                    {'order': {'source': chosen, 'keys': ['weight', 'code']}}]},
                                        {'equals': [ref('outcome', 'count'), {'cardinality': chosen}]}
                                    ]},
                         'rejected': {'value': {'record': {'reason': 'string'}},
                                      'constraints': [{'equals': [ref('post'), ref('pre')]},
                                                      {'equals': [ref('outcome', 'reason'),
                                                                  {'literal': {'type': 'string', 'value': 'closed'}}]}]}}}


class TypedLowering(unittest.TestCase):
    def test_mutated_semantic_source_changes_checked_behavior(self):
        rows = [{'code': 'a', 'active': False, 'weight': 1},
                {'code': 'c', 'active': True, 'weight': 3},
                {'code': 'b', 'active': True, 'weight': 2}]
        original = contract()
        check = lower(original)
        success = {'kind': 'success', 'value': {'items': [rows[2], rows[1]], 'count': 2}}
        self.assertTrue(check({}, rows, success, rows))
        self.assertFalse(check({}, rows, {**success, 'value': {**success['value'], 'count': 3}}, rows))
        self.assertTrue(check({}, rows, {'kind': 'rejected', 'value': {'reason': 'closed'}}, rows))
        self.assertFalse(check({}, rows, {'kind': 'rejected', 'value': {'reason': 'open'}}, rows))
        changed = copy.deepcopy(original)
        selection = changed['outcomes']['success']['constraints'][1]['equals'][1]['order']['source']['select']
        selection['where']['equals'][1]['literal']['value'] = False
        self.assertFalse(lower(changed)({}, rows, success, rows))
        alternative = {'kind': 'success', 'value': {'items': [rows[0]], 'count': 1}}
        self.assertTrue(lower(changed)({}, rows, alternative, rows))
        self.assertFalse(check({}, rows, alternative, rows))

    def test_negative_valid_combination_is_unsupported_not_invalid(self):
        novel = contract()
        # Keyed default_missing on a record sequence is a meaningful #44
        # relation, but this bounded evaluator has no implementation for it.
        novel['outcomes']['success']['constraints'].append(
            {'default_missing': [ref('pre'), ref('post')]})
        with self.assertRaisesRegex(UnsupportedLowering, 'default_missing'):
            lower(novel)

    def test_rejects_mismatched_types_and_unlisted_outcomes(self):
        candidate = contract()
        candidate['outcomes']['success']['constraints'].append(
            {'equals': [ref('outcome', 'count'), ref('outcome', 'items')]})
        with self.assertRaisesRegex(ValueError, 'type mismatch'):
            lower(candidate)
        self.assertFalse(lower(contract())({}, [], {'kind': 'unknown', 'value': {}}, []))


if __name__ == '__main__':
    unittest.main()
