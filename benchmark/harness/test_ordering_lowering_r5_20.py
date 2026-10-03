"""Prospective generative lowering of the existing typed ordering relation.

Independent non-task domains only: media assets and device inventory. No B02
task, command, field name or fixture value participates; the lowerer receives
ordering data solely from typed contracts.
"""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import generative_r5_13
from benchmark.semantic.generative_evidence_r5_13 import (
    challenge, conforms, observe, _ordered_relation_holds)
from benchmark.semantic.generative_r5_13 import (
    canonical, generate, ordering_plan, render, sha, typed, UnsupportedLowering)


MEDIA_ROW = {'asset_id': 'string', 'title': 'string', 'year': 'integer', 'shelf': 'integer'}
DEVICE_ROW = {'serial': 'string', 'model': 'string', 'site': 'string',
              'installed': 'integer', 'warranty': 'integer'}


def ref(*parts):
    return {'ref': list(parts)}


def literal(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def ordered(source, keys):
    return {'order': {'source': source, 'keys': list(keys)}}


def media(keys=('title',), state=None, value=None, value_type=None):
    """Read-only ordered listing over a typed media-asset population."""
    state = MEDIA_ROW if state is None else state
    return {'id': 'media.catalogue.list', 'version': '1',
            'input': {'record': {'request': 'string'}},
            'state': {'sequence': {'record': state}},
            'branches': [
                {'tag': 'listed', 'when': {'equals': [ref('input', 'request'), literal('list')]},
                 'value_type': value_type or {'sequence': {'record': state}},
                 'value': value or ordered(ref('pre'), keys),
                 'transition': {'preserve': True}},
                {'tag': 'unavailable', 'when': None, 'value': literal('unavailable'),
                 'transition': {'preserve': True}}]}


def devices(keys=('site', 'serial'), source=None, value_type=None):
    state = DEVICE_ROW
    return {'id': 'device.inventory.list', 'version': '1',
            'input': {'record': {'request': 'string', 'model': {'optional': 'string'}}},
            'state': {'sequence': {'record': state}},
            'branches': [
                {'tag': 'listed', 'when': {'equals': [ref('input', 'request'), literal('list')]},
                 'value_type': value_type or {'sequence': {'record': state}},
                 'value': ordered(source if source is not None else ref('pre'), keys),
                 'transition': {'preserve': True}},
                {'tag': 'unavailable', 'when': None, 'value': literal('unavailable'),
                 'transition': {'preserve': True}}]}


ASSETS = [{'asset_id': 'a1', 'title': 'Zephyr', 'year': 2001, 'shelf': 3},
          {'asset_id': 'a2', 'title': 'Apple', 'year': 1999, 'shelf': 1},
          {'asset_id': 'a3', 'title': 'Mango', 'year': 2001, 'shelf': 2}]

RIGS = [{'serial': 'S9', 'model': 'Widget', 'site': 'north', 'installed': 100, 'warranty': 2},
        {'serial': 'S2', 'model': 'Widget', 'site': 'north', 'installed': 90, 'warranty': 1},
        {'serial': 'S1', 'model': 'Widget', 'site': 'north', 'installed': 100, 'warranty': 3},
        {'serial': 'S5', 'model': 'Gadget', 'site': 'south', 'installed': 50, 'warranty': 4}]


def rank(rows, keys):
    return [tuple(row[key] for key in keys) for row in rows]


class OrderingLowering(unittest.TestCase):
    def case(self, contract, pre, inp, fault=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root, fault=fault)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe(root, inp)
            verdict = challenge(contract, root, event, public, before, after)
            return json.loads(public['stdout']), before, after, verdict

    # Part 5: single-key ordering drives real executable behavior.
    def test_single_key_orders_already_sorted_reversed_arbitrary_empty_and_one(self):
        for rows in (ASSETS, list(reversed(ASSETS)), [ASSETS[1], ASSETS[0], ASSETS[2]]):
            outcome, _, _, verdict = self.case(media(), rows, {'request': 'list'})
            self.assertEqual(outcome['value'], sorted(rows, key=lambda row: row['title']))
            self.assertEqual([row['title'] for row in outcome['value']], ['Apple', 'Mango', 'Zephyr'])
            self.assertEqual((verdict['provenance_valid'], verdict['grounded'], verdict['conformant']),
                             (True, True, True))
        for rows in ([], [ASSETS[2]]):
            outcome, _, _, verdict = self.case(media(), rows, {'request': 'list'})
            self.assertEqual(outcome['value'], rows)
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_integer_key_duplicate_values_ties_stay_unconstrained(self):
        # 'year' ties: 2001 occurs twice. The semantics constrain only that the
        # result is a multiset permutation with nondecreasing key sequence.
        for rows in (ASSETS, list(reversed(ASSETS))):
            outcome, _, _, verdict = self.case(media(keys=('year',)), rows, {'request': 'list'})
            self.assertEqual(rank(outcome['value'], ['year']), sorted(rank(outcome['value'], ['year'])))
            self.assertEqual(sorted(map(canonical, outcome['value'])), sorted(map(canonical, rows)))
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_inapplicable_request_selects_other_branch(self):
        outcome, before, after, verdict = self.case(media(), ASSETS, {'request': 'audit'})
        self.assertEqual(outcome, {'kind': 'unavailable', 'value': 'unavailable'})
        self.assertEqual(before, after)
        self.assertTrue(verdict['conformant'])

    # Part 6: lexicographic multi-key ordering; ties exercise the secondary key.
    def test_lexicographic_two_key_and_three_key_orders_secondary_decides_ties(self):
        # All three Widgets tie on 'site'; the secondary 'serial' decides.
        outcome, _, _, verdict = self.case(devices(), RIGS, {'request': 'list'})
        self.assertEqual([row['serial'] for row in outcome['value']], ['S1', 'S2', 'S9', 'S5'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

        three = devices(keys=('site', 'installed', 'serial'))
        rows = copy.deepcopy(RIGS)
        rows[0]['installed'] = 90  # S9 ties S2 through (north, 90); serial decides
        outcome, _, _, verdict = self.case(three, rows, {'request': 'list'})
        self.assertEqual([row['serial'] for row in outcome['value']], ['S2', 'S9', 'S1', 'S5'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_n_key_plan_is_general_not_specialized_to_two(self):
        keys = ('site', 'installed', 'warranty', 'serial')
        contract = devices(keys=keys)
        plan = ordering_plan({'source': ref('pre'), 'keys': list(keys)},
                             {'input': contract['input'], 'pre': contract['state']})
        self.assertEqual([key for key, _ in plan['keys']], list(keys))
        self.assertEqual([shape for _, shape in plan['keys']], ['string', 'integer', 'integer', 'string'])
        generated = render(contract)
        for field in keys:
            self.assertIn(repr(field).encode(), generated)
        rows = copy.deepcopy(RIGS)
        rows[0]['warranty'] = rows[1]['warranty']  # tie through key 3; serial breaks it
        outcome, _, _, verdict = self.case(contract, rows, {'request': 'list'})
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertEqual(rank(outcome['value'], list(keys)), sorted(rank(outcome['value'], list(keys))))

    # Part 7: direction is NOT represented by the existing relation.
    def test_direction_is_not_represented_and_cannot_be_silently_invented(self):
        contract = media()
        contract['branches'][0]['value']['order']['direction'] = 'descending'
        with self.assertRaisesRegex(ValueError, 'invalid ordering'):
            typed(contract)
        plan = ordering_plan({'source': ref('pre'), 'keys': ['title']},
                             {'input': contract['input'], 'pre': contract['state']})
        self.assertNotIn('direction', plan)
        self.assertNotIn('reverse', render(media()).decode())

    # Part 8: implementation determinism versus semantic requirement.
    def test_tie_permutations_are_semantically_equivalent(self):
        tied = [{'asset_id': 't1', 'title': 'Same', 'year': 5, 'shelf': 1},
                {'asset_id': 't2', 'title': 'Same', 'year': 5, 'shelf': 2}]
        contract = media()
        slots = {'input': contract['input'], 'pre': contract['state']}
        facts = {'input': {'request': 'list'}, 'pre': tied}
        order = contract['branches'][0]['value']['order']
        for permutation in (tied, list(reversed(tied))):
            self.assertTrue(_ordered_relation_holds(order, facts, slots, permutation))
            outcome, _, _, verdict = self.case(contract, permutation, {'request': 'list'})
            self.assertTrue(verdict['conformant'])
            # Backend determinism (a stable Python sort) is observed, not required.
            self.assertEqual(outcome['value'], sorted(permutation, key=lambda row: row['title']))
        self.assertFalse(_ordered_relation_holds(
            order, facts, slots,
            [{'asset_id': 't3', 'title': 'Other', 'year': 5, 'shelf': 3}, tied[1]]))

    # Part 9: typed lowering diagnostics before any generated execution.
    def test_ordering_contract_type_safety_rejects_before_generation(self):
        for keys, message in ((['missing_title'], 'invalid typed field reference'),
                              ([7], 'invalid ordering key'),
                              ([], 'invalid ordering')):
            contract = media()
            contract['branches'][0]['value']['order']['keys'] = keys
            with self.assertRaisesRegex(ValueError, message):
                typed(contract)
        scalar = media()
        scalar['branches'][0]['value']['order']['source'] = ref('input', 'request')
        with self.assertRaisesRegex(ValueError, 'ordering needs a sequence'):
            typed(scalar)
        strings = media()
        strings['input']['record']['names'] = {'sequence': 'string'}
        strings['branches'][0]['value'] = ordered(ref('input', 'names'), ['name'])
        strings['branches'][0]['value_type'] = {'sequence': {'record': {'name': 'string'}}}
        with self.assertRaisesRegex(ValueError, 'invalid typed field reference'):
            typed(strings)
        nested = media(state={**MEDIA_ROW, 'tags': {'sequence': 'string'}})
        nested['branches'][0]['value']['order']['keys'] = ['tags']
        with self.assertRaisesRegex(ValueError, 'non-orderable key'):
            typed(nested)
        mismatched = media(value_type={'sequence': {'record': {'asset_id': 'string'}}})
        with self.assertRaisesRegex(ValueError, 'payload type mismatch'):
            typed(mismatched)

    def test_redundant_duplicate_key_generates_consistently(self):
        # The validating interpreter tolerates repeated keys as redundant
        # projections; emission stays identical in behavior, never redefined.
        duplicated = media(keys=('year', 'year'))
        outcome, _, _, verdict = self.case(duplicated, ASSETS, {'request': 'list'})
        plain = media(keys=('year',))
        expected, _, _, expected_verdict = self.case(plain, ASSETS, {'request': 'list'})
        self.assertEqual(outcome['value'], expected['value'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_scoped_source_rejects_explicitly_never_falls_back(self):
        node = {'order': {'source': ref('item', 'rows'), 'keys': ['title']}}
        with self.assertRaisesRegex(UnsupportedLowering, 'order \\(scoped source\\)'):
            generative_r5_13.expression(node)
        with self.assertRaisesRegex(UnsupportedLowering, 'order \\(scoped source\\)'):
            generative_r5_13.expression({'order': {'source': ref('pre'), 'keys': ['title']}},
                                         {'pre': 'rows'})

    # Part 10: semantic-only mutations change generated behavior.
    def test_semantic_only_key_mutation_changes_executable_order(self):
        by_title = self.case(media(), ASSETS, {'request': 'list'})[0]['value']
        by_year = self.case(media(keys=('year',)), ASSETS, {'request': 'list'})[0]['value']
        self.assertEqual([row['asset_id'] for row in by_title], ['a2', 'a3', 'a1'])
        self.assertEqual(rank(by_year, ['year']), sorted(rank(by_year, ['year'])))
        self.assertEqual(sorted(map(canonical, by_year)), sorted(map(canonical, ASSETS)))
        inp = {'request': 'list', 'model': 'Widget'}
        narrowed = devices(keys=('site',))
        outcome, _, _, verdict = self.case(narrowed, RIGS, inp)
        self.assertEqual(rank(outcome['value'], ['site']), sorted(rank(outcome['value'], ['site'])))
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        widened = devices(keys=('site', 'serial', 'installed'))
        outcome, _, _, verdict = self.case(widened, RIGS, inp)
        self.assertEqual([row['serial'] for row in outcome['value']], ['S1', 'S2', 'S9', 'S5'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    # Part 11: semantic sequence of keys versus irrelevant serialization order.
    def test_serialization_order_independence_and_key_sequence_meaning(self):
        left = media(keys=('year', 'title'))
        right = copy.deepcopy(left)
        value = right['branches'][0]['value']['order']
        right['branches'][0]['value'] = {'order': {'keys': value['keys'], 'source': value['source']}}
        self.assertEqual(canonical(left), canonical(right))
        self.assertEqual(sha(canonical(left)), sha(canonical(right)))
        self.assertEqual(render(left), render(right))
        reversed_keys = media(keys=('title', 'year'))
        self.assertNotEqual(sha(canonical(left)), sha(canonical(reversed_keys)))
        crossed = ASSETS + [{'asset_id': 'a4', 'title': 'Cedar', 'year': 1998, 'shelf': 4}]
        by_year_first = self.case(left, crossed, {'request': 'list'})[0]['value']
        by_title_first = self.case(reversed_keys, crossed, {'request': 'list'})[0]['value']
        self.assertEqual([row['asset_id'] for row in by_year_first], ['a4', 'a2', 'a3', 'a1'])
        self.assertEqual([row['asset_id'] for row in by_title_first], ['a2', 'a4', 'a3', 'a1'])
        self.assertNotEqual(by_year_first, by_title_first)
        # A three-key rotation keeps meaning in the list, not the envelope.
        self.assertNotEqual(render(media(keys=('year', 'title', 'shelf'))),
                            render(media(keys=('shelf', 'title', 'year'))))

    # Part 12: composition with exact selection.
    def test_selection_then_ordering_composes_without_domain_code(self):
        selection = {'select': {'source': ref('pre'),
                                'where': {'equals': [ref('item', 'model'), literal('Widget')]}}}
        contract = devices(keys=('site', 'serial'), source=selection)
        outcome, _, _, verdict = self.case(contract, RIGS, {'request': 'list', 'model': 'Widget'})
        self.assertEqual([row['serial'] for row in outcome['value']], ['S1', 'S2', 'S9'])
        self.assertFalse(any(row['model'] != 'Widget' for row in outcome['value']))
        self.assertEqual(rank(outcome['value'], ['site', 'serial']),
                         sorted(rank(outcome['value'], ['site', 'serial'])))
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'], verdict['conformant']),
                         (True, True, True))

    # Part 13: ordered typed records cross the outcome boundary unflattened.
    def test_ordered_records_cross_public_boundary_as_typed_records(self):
        outcome, _, _, verdict = self.case(media(), ASSETS, {'request': 'list'})
        self.assertEqual(set(outcome), {'kind', 'value'})
        for row in outcome['value']:
            self.assertIsInstance(row, dict)
            self.assertEqual(set(row), set(MEDIA_ROW))
            self.assertEqual([type(row[name]) for name in ('asset_id', 'title', 'year', 'shelf')],
                             [str, str, int, int])
        self.assertTrue(verdict['grounded'])

    # Part 14: ordering a returned view must not rewrite durable storage.
    def test_durable_read_only_ordering_preserves_storage_bytes_and_order(self):
        unsorted = [ASSETS[2], ASSETS[0], ASSETS[1]]
        outcome, before, after, verdict = self.case(media(), unsorted, {'request': 'list'})
        self.assertEqual(before, after)
        self.assertEqual(json.loads(after), unsorted)
        self.assertEqual([row['title'] for row in outcome['value']], ['Apple', 'Mango', 'Zephyr'])
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'], verdict['conformant']),
                         (True, True, True))

    # Parts 15/16: grounding and conformance with a disposable lowering fault.
    def test_grounded_fault_returns_wrong_order_and_fails_conformance(self):
        outcome, before, after, verdict = self.case(media(), ASSETS, {'request': 'list'}, fault=True)
        self.assertEqual(outcome['value'], list(reversed(
            sorted(ASSETS, key=lambda row: row['title']))))
        self.assertEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded']), (True, True))
        self.assertFalse(verdict['conformant'])
        multi = devices(keys=('site', 'serial'))
        outcome, _, _, verdict = self.case(multi, RIGS, {'request': 'list'}, fault=True)
        self.assertEqual(rank(outcome['value'], ['site']), sorted(rank(outcome['value'], ['site'])))
        self.assertNotEqual(rank(outcome['value'], ['site', 'serial']),
                            sorted(rank(outcome['value'], ['site', 'serial'])))
        self.assertTrue(verdict['grounded'])
        self.assertFalse(verdict['conformant'])

    # Part 17: a novel supported combination with no lowerer modification.
    def test_novel_selection_three_key_ordering_guarded_composition(self):
        contract = devices(keys=('site', 'installed', 'serial'))
        contract['version'] = 'novel'
        contract['branches'][0]['when'] = {'and': [
            {'equals': [ref('input', 'request'), literal('list')]},
            {'equals': [{'cardinality': {'select': {
                'source': ref('pre'),
                'where': {'equals': [ref('item', 'site'), literal('north')]}}}},
                literal(3, 'integer')]}]}
        contract['branches'][0]['value'] = ordered(
            {'select': {'source': ref('pre'),
                        'where': {'not': {'equals': [ref('item', 'model'), literal('Gadget')]}}}},
            ('site', 'installed', 'serial'))
        outcome, _, _, verdict = self.case(contract, RIGS, {'request': 'list', 'model': 'Widget'})
        self.assertEqual([row['serial'] for row in outcome['value']], ['S2', 'S1', 'S9'])
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'], verdict['conformant']),
                         (True, True, True))

    # Part 19: contamination audit over the general ordering machinery.
    def test_lowerer_contains_no_task_b02_or_benchmark_vocabulary(self):
        lowered = Path(generative_r5_13.__file__).read_text(encoding='utf-8')
        for token in ("'created_at'", "'task'", "'b02'", 'B02', "'priority'", "'due_date'",
                      "'critical'", "'NORMAL'", "'HIGH'", "'tags'", "'status'", "'title'",
                      "'asset_id'", "'serial'", "'site'", "'installed'", "'warranty'",
                      "'shelf'", "'year'", 'insert_task', 'tasks.json', 'schema_version'):
            self.assertNotIn(token, lowered)
        evidence = Path(__import__('benchmark.semantic.generative_evidence_r5_13',
                                   fromlist=['x']).__file__).read_text(encoding='utf-8')
        for token in ("'created_at'", "'b02'", 'B02', "'priority'", "'due_date'",
                      "'NORMAL'", "'HIGH'", "'tags'", 'tasks.json'):
            self.assertNotIn(token, evidence)


if __name__ == '__main__':
    unittest.main()
