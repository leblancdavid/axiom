"""R5.21 third frozen B02 retry probes; observation only, no repair.

This is not a B02 candidate or a frozen acceptance run. Each probe feeds one
faithful B02-shaped obligation (or, for frontier probes, the obligation's
representing relation node) through the general lowerer. Slice executions use
disposable temporary directories; no historical artifact, compiler component,
frozen requirement, profile or oracle changes.

Frontier markers (`external`, `fallback`, `sole`, `before`, `remove`) named
relations that were generative-unsupported at the R5.21 lock. R5.22 closed the
known general-lowering set on independent non-task domains, so the four
`external`/`fallback`/`before`/`sole` rejection expectations are retired here by
the established lifecycle precedent (R5.19, R5.20 updated superseded retry
expectations). They now assert *type-level* interpretation only — never B02
generation, grounding or acceptance. The two top-level-shape boundaries
(`remove` and envelope `replace_field` as single transitions) remain outside the
relation-set grammar and still reject, matching the R5.22 result.
"""

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.harness.test_b02_retry_r5_17 import b02_migration_contract, literal, ref
from benchmark.harness.test_b02_retry_r5_19 import b02_ordered_list_contract
from benchmark.semantic.generative_evidence_r5_13 import challenge, observe
from benchmark.semantic.generative_r5_13 import (
    canonical, generate, render, typed, UnsupportedLowering)


LEGACY_ROW = {'id': 'string', 'title': 'string', 'description': 'string',
              'status': 'string', 'created_at': 'string',
              'priority': {'optional': 'string'},
              'due_date': {'optional': {'nullable': 'string'}},
              'tags': {'optional': {'sequence': 'string'}}}

CURRENT_ROW = {'id': 'string', 'title': 'string', 'description': 'string',
               'status': 'string', 'priority': 'string', 'created_at': 'string',
               'due_date': {'nullable': 'string'}, 'tags': {'sequence': 'string'}}

# B02-shaped population: t2/t3 tie on created_at so the declared id key decides;
# storage order differs from the semantic (created_at, id) order.
TASKS = [
    {'id': 't3', 'title': 'Third', 'description': 'x', 'status': 'pending',
     'priority': 'HIGH', 'created_at': '2026-06-03T00:00:00Z', 'due_date': None,
     'tags': ['work', 'Work']},
    {'id': 't1', 'title': 'First', 'description': 'x', 'status': 'completed',
     'priority': 'NORMAL', 'created_at': '2026-06-01T00:00:00Z',
     'due_date': '2020-01-01T00:00:00Z', 'tags': []},
    {'id': 't2', 'title': 'Second', 'description': 'x', 'status': 'pending',
     'priority': 'HIGH', 'created_at': '2026-06-03T00:00:00Z',
     'due_date': '2999-01-01T00:00:00Z', 'tags': ['home']},
]


def ordered_list():
    return b02_ordered_list_contract()


def ordered_read(command, row, where):
    return {'id': 'b02.' + command, 'version': 'r5.21',
            'input': {'record': {'request': 'string'}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': row}}}},
            'branches': [
                {'tag': 'listed', 'when': {'equals': [ref('pre', 'schema_version'),
                                                      literal(4, 'integer')]},
                 'value_type': {'sequence': {'record': row}},
                 'value': {'order': {'source': where, 'keys': ['created_at', 'id']}},
                 'transition': {'preserve': True}},
                {'tag': 'migration_required', 'when': None,
                 'value': literal('migration_required', 'string'),
                 'transition': {'preserve': True}}]}


def blank_tag_guard():
    tags = ref('input', 'tags')
    return {'id': 'b02.create.invalid_tag', 'version': 'r5.21',
            'input': {'record': {'request': 'string', 'title': 'string',
                                 'description': 'string', 'tags': {'sequence': 'string'}}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': LEGACY_ROW}}}},
            'branches': [
                {'tag': 'invalid_tag', 'when': {'not': {'for_each': {
                    'sequence': tags, 'bind': 'tag',
                    'property': {'nonblank': {'trim': ref('tag')}}}}},
                 'value': literal('invalid_tag', 'string'),
                 'transition': {'preserve': True}},
                {'tag': 'create_success_not_lowered', 'when': None,
                 'value': literal('slice boundary: create success is probed separately',
                                  'string'),
                 'transition': {'preserve': True}}]}


def tags_projection():
    # Isolates the R5.15 normalization composition on the frozen B02 tag values;
    # the complete create outcome and insertion remain probed elsewhere.
    tags = ref('input', 'tags')
    return {'id': 'b02.create.tags_projection', 'version': 'r5.21',
            'input': {'record': {'tags': {'sequence': 'string'}}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': LEGACY_ROW}}}},
            'branches': [
                {'tag': 'normalized', 'when': {'for_each': {
                    'sequence': tags, 'bind': 'tag',
                    'property': {'nonblank': {'trim': ref('tag')}}}},
                 'value_type': {'record': {'tags': {'sequence': 'string'}}},
                 'value': {'record': {'tags': {'stable_unique': {
                     'sequence': {'map': {'sequence': tags, 'transform': 'trim'}},
                     'equality': 'case_sensitive_string'}}}},
                 'transition': {'preserve': True}},
                {'tag': 'invalid_tag', 'when': None,
                 'value': literal('invalid_tag', 'string'),
                 'transition': {'preserve': True}}]}


def complete_transition(envelope=False):
    pending = {'select': {'source': ref('pre', 'records') if envelope else ref('pre'),
                          'where': {'and': [
        {'equals': [ref('item', 'id'), ref('input', 'id')]},
        {'equals': [ref('item', 'status'), literal('pending', 'string')]}]}}}
    guard = {'equals': [{'cardinality': pending}, literal(1, 'integer')]}
    state = ({'record': {'schema_version': 'integer',
                         'records': {'sequence': {'record': CURRENT_ROW}}}}
             if envelope else {'sequence': {'record': CURRENT_ROW}})
    if envelope:
        guard = {'and': [{'equals': [ref('pre', 'schema_version'),
                                     literal(4, 'integer')]}, guard]}
    return {'id': 'b02.complete.transition', 'version': 'r5.21',
            'input': {'record': {'request': 'string', 'id': 'string'}},
            'state': state,
            'branches': [
                {'tag': 'completed', 'when': guard,
                 'value': literal('completed', 'string'),
                 'transition': {'replace_field': {
                     'key': 'id', 'match': ref('input', 'id'), 'field': 'status',
                     'value': literal('completed', 'string')}}},
                {'tag': 'not_completed', 'when': None,
                 'value': literal('slice boundary: task_not_found and '
                                  'invalid_transition share this one branch here',
                                  'string'),
                 'transition': {'preserve': True}}]}


def single_relation(node, shape='string'):
    # Frontier probe: does the locked generative grammar interpret one existing
    # candidate/inherited relation node at all? A rejection is the finding.
    return {'id': 'b02.frontier', 'version': 'r5.21',
            'input': {'record': {'request': 'string', 'priority': {'optional': 'string'},
                                 'a': 'string', 'b': 'string'}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': LEGACY_ROW}}}},
            'branches': [
                {'tag': 'probed', 'when': {'equals': [ref('input', 'request'),
                                                      literal('probe', 'string')]},
                 'value_type': shape, 'value': node,
                 'transition': {'preserve': True}},
                {'tag': 'otherwise', 'when': None,
                 'value': literal('otherwise', 'string'),
                 'transition': {'preserve': True}}]}


class ThirdB02Retry(unittest.TestCase):
    def case(self, contract, pre, inp):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe(root, inp)
            verdict = challenge(contract, root, event, public, before, after)
            return (json.loads(public['stdout']) if public['exit'] == 0 else None,
                    json.loads(after), verdict, before, after)

    # Part 3: the decisive R5.19 gate, recorded before any further lowering.
    def test_r5_19_order_blocker_is_resolved_by_the_locked_lowerer(self):
        slice_contract = ordered_list()
        self.assertIs(typed(slice_contract), slice_contract)
        generated = render(slice_contract)
        self.assertIn(b"sorted(pre['records']", generated)
        self.assertIn(b"'created_at'", generated)
        self.assertIn(b"'id'", generated)

    # Part 4 / Part 12: the ordered list obligation now lowers end-to-end.
    def test_ordered_list_slice_executes_grounds_and_conforms_on_b02_shape(self):
        pre = {'schema_version': 4, 'records': [TASKS[0], TASKS[2], TASKS[1]]}
        outcome, post, verdict, before, after = self.case(
            ordered_list(), pre, {'request': 'list'})
        self.assertEqual([row['id'] for row in outcome['value']], ['t1', 't2', 't3'])
        self.assertEqual(post, pre)
        self.assertEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        legacy = {'schema_version': 1, 'records': [TASKS[0]]}
        outcome, post, verdict, before, after = self.case(
            ordered_list(), legacy, {'request': 'list'})
        self.assertEqual(outcome, {'kind': 'migration_required', 'value': 'migration_required'})
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_blank_tag_guard_slice_executes_and_preserves_storage(self):
        pre = {'schema_version': 4, 'records': []}
        for tags in (['  '], ['work', '  '], ['']):
            outcome, post, verdict, before, after = self.case(
                blank_tag_guard(), pre,
                {'request': 'create', 'title': 'T', 'description': 'x', 'tags': tags})
            self.assertEqual(outcome, {'kind': 'invalid_tag', 'value': 'invalid_tag'})
            self.assertEqual(post, pre)
            self.assertEqual(before, after)
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_normalized_tags_projection_reaches_b02_shaped_execution(self):
        outcome, _, verdict, before, after = self.case(
            tags_projection(), {'schema_version': 4, 'records': []},
            {'tags': ['  work  ', 'Work', 'work', 'home']})
        self.assertEqual(outcome, {'kind': 'normalized',
                                   'value': {'tags': ['work', 'Work', 'home']}})
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertEqual(before, after)

    def test_exact_high_selection_composed_with_ordering_executes_and_conforms(self):
        rows = TASKS + [{'id': 't4', 'title': 'Critical', 'description': 'x',
                         'status': 'pending', 'priority': 'CRITICAL',
                         'created_at': '2026-06-03T00:00:00Z', 'due_date': None,
                         'tags': ['now', 'NEW']}]
        selection = {'select': {'source': ref('pre', 'records'), 'where':
            {'equals': [ref('item', 'priority'), literal('HIGH', 'string')]}}}
        contract = ordered_read('list-high', CURRENT_ROW, selection)
        outcome, post, verdict, before, after = self.case(
            contract, {'schema_version': 4, 'records': [rows[3], rows[0], rows[2], rows[1]]},
            {'request': 'list-high'})
        self.assertEqual([row['id'] for row in outcome['value']], ['t2', 't3'])
        self.assertEqual(post, {'schema_version': 4,
                                'records': [rows[3], rows[0], rows[2], rows[1]]})
        self.assertEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        outcome, _, verdict, before, after = self.case(
            contract, {'schema_version': 3, 'records': [rows[0]]}, {'request': 'list-high'})
        self.assertEqual(outcome['kind'], 'migration_required')
        self.assertEqual(before, after)
        self.assertTrue(verdict['conformant'])

    def test_lifecycle_transition_slice_executes_with_preserved_record(self):
        pre = [TASKS[2], TASKS[1], TASKS[0]]
        outcome, post, verdict, before, after = self.case(
            complete_transition(), pre, {'request': 'complete', 'id': 't3'})
        self.assertEqual(outcome, {'kind': 'completed', 'value': 'completed'})
        updated = {**TASKS[0], 'status': 'completed'}
        self.assertEqual(post, [TASKS[2], TASKS[1], updated])
        self.assertNotEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        outcome, post, verdict, before, after = self.case(
            complete_transition(), pre, {'request': 'complete', 'id': 't1'})
        self.assertEqual(outcome['kind'], 'not_completed')
        self.assertEqual(post, pre)
        self.assertEqual(before, after)
        self.assertTrue(verdict['conformant'])

    def test_migration_slice_executes_defaults_version_and_count(self):
        legacy_rows = [
            {'id': 'm1', 'title': 'Old', 'description': 'x', 'status': 'pending',
             'created_at': '2026-05-01T00:00:00Z'},
            {'id': 'm2', 'title': 'Part', 'description': 'x', 'status': 'pending',
             'created_at': '2026-05-02T00:00:00Z', 'priority': 'HIGH',
             'due_date': '2030-01-01T00:00:00Z'}]
        contract = b02_migration_contract()
        outcome, post, verdict, before, after = self.case(
            contract, {'schema_version': 1, 'records': legacy_rows},
            {'request': 'migrate'})
        self.assertEqual(outcome, {'kind': 'migrated', 'value': {'migrated': 2}})
        self.assertEqual(post, {'schema_version': 4, 'records': [
            {**legacy_rows[0], 'priority': 'NORMAL', 'due_date': None, 'tags': []},
            {**legacy_rows[1], 'tags': []}]})
        self.assertNotEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        current = {'schema_version': 4, 'records': [post['records'][0]]}
        outcome, post2, verdict, before, after = self.case(contract, current,
                                                           {'request': 'migrate'})
        self.assertEqual(outcome, {'kind': 'current', 'value': {'migrated': 0}})
        self.assertEqual(post2, current)
        self.assertEqual(before, after)
        self.assertTrue(verdict['conformant'])

    # Part 5: frontier probes. Each node below is a relation represented in the
    # candidate inventory or inherited as an obligation, fed to the locked
    # generative grammar unchanged.
    def test_external_value_relation_is_now_interpretable_by_the_lowerer(self):
        # R5.22 closed this frontier on independent domains; type-level only.
        node = {'external': {'source': 'fresh_unique_id'}}
        self.assertIsNotNone(typed(single_relation({'record': {'id': node}},
                                                   {'record': {'id': 'string'}})))
        clock = {'external': {'source': 'utc_clock'}}
        with self.assertRaisesRegex(ValueError, 'outcome payload type mismatch'):
            typed(single_relation(clock, 'string'))

    def test_input_fallback_relation_is_now_interpretable_by_the_lowerer(self):
        node = {'fallback': {'value': ref('input', 'priority'),
                             'default': literal('NORMAL', 'string')}}
        self.assertIsNotNone(typed(single_relation(node, 'string')))

    def test_strict_time_comparison_is_now_a_typed_instant_relation(self):
        # `before` lowerings require typed instants, so plain-string operands
        # reject by type rather than as an uninterpreted frontier relation.
        node = {'before': [ref('input', 'a'), ref('input', 'b')]}
        with self.assertRaisesRegex(ValueError, 'before requires two typed instants'):
            typed(single_relation(node, 'boolean'))
        guarded = single_relation(literal('x', 'string'), 'string')
        guarded['branches'][0]['when'] = {'and': [
            {'equals': [ref('input', 'request'), literal('probe', 'string')]}, node]}
        with self.assertRaisesRegex(ValueError, 'before requires two typed instants'):
            typed(guarded)

    def test_matched_record_projection_is_now_interpretable_by_the_lowerer(self):
        node = {'sole': {'select': {'source': ref('pre', 'records'), 'where':
            {'equals': [ref('item', 'id'), ref('input', 'request')]}}}}
        self.assertIsNotNone(typed(single_relation(node, {'record': LEGACY_ROW})))

    def test_removal_transition_is_not_supported_by_the_lowerer(self):
        contract = {'id': 'b02.delete', 'version': 'r5.21',
                    'input': {'record': {'request': 'string', 'id': 'string'}},
                    'state': {'sequence': {'record': CURRENT_ROW}},
                    'branches': [
                        {'tag': 'deleted', 'when': {'equals': [
                            ref('input', 'request'), literal('delete', 'string')]},
                         'value': ref('input', 'id'),
                         'transition': {'remove': {'identity': 'id',
                                                   'match': ref('input', 'id')}}},
                        {'tag': 'missing', 'when': None,
                         'value': literal('task_not_found', 'string'),
                         'transition': {'preserve': True}}]}
        with self.assertRaisesRegex(UnsupportedLowering, 'state relation'):
            typed(contract)

    def test_keyed_replacement_over_a_versioned_envelope_state_is_not_supported(self):
        with self.assertRaisesRegex(UnsupportedLowering, 'state relation'):
            typed(complete_transition(envelope=True))

    # Part 5 (superseded): the R5.21 external/fallback frontier blockers are resolved
    # by R5.22's general lowering. The *complete* B02 create is still not asserted
    # serializable here (R5.22 never runs B02); for this frozen fixture the declared
    # created_at is a plain string while the clock capability types as an instant, so
    # any residual rejection is ordinary type consistency, never the blanket
    # `unsupported relation` frontier error.
    def test_integrated_b02_create_no_longer_blocks_on_external_or_fallback(self):
        task_expression = {'record': {
            'id': {'external': {'source': 'fresh_unique_id'}},
            'title': ref('input', 'title'),
            'description': ref('input', 'description'),
            'status': literal('pending', 'string'),
            'priority': {'fallback': {'value': ref('input', 'priority'),
                                      'default': literal('NORMAL', 'string')}},
            'created_at': {'external': {'source': 'utc_clock'}},
            'due_date': {'fallback': {
                'value': ref('input', 'due_date'),
                'default': literal(None, {'nullable': 'string'})}},
            'tags': {'stable_unique': {
                'sequence': {'map': {'sequence': ref('input', 'tags'),
                                     'transform': 'trim'}},
                'equality': 'case_sensitive_string'}}}}
        create_success = {'id': 'b02.create.full', 'version': 'r5.21',
                          'input': {'record': {'request': 'string', 'title': 'string',
                                               'description': 'string',
                                               'priority': {'optional': 'string'},
                                               'due_date': {'optional': {'nullable': 'string'}},
                                               'tags': {'sequence': 'string'}}},
                          'state': {'record': {'schema_version': 'integer',
                                               'records': {'sequence': {'record': LEGACY_ROW}}}},
                          'branches': [
                              {'tag': 'created', 'when': {'and': [
                                  {'equals': [ref('input', 'request'),
                                              literal('create', 'string')]},
                                  {'for_each': {'sequence': ref('input', 'tags'),
                                                'bind': 'tag',
                                                'property': {'nonblank': {'trim': ref('tag')}}}}]},
                               'value_type': {'record': CURRENT_ROW},
                               'value': task_expression,
                               'transition': {'relations': [{'exact_frame': {
                                   'collection': 'records', 'identity': 'id',
                                   'record': task_expression}}]}},
                              {'tag': 'otherwise', 'when': None,
                               'value': literal('remaining commands share this AST',
                                                'string'),
                               'transition': {'preserve': True}}]}
        try:
            typed(create_success)
            raised = None
        except Exception as exc:
            raised = exc
        if raised is not None:
            self.assertNotIsInstance(raised, UnsupportedLowering)
            self.assertNotIn('unsupported relation:', str(raised))


if __name__ == '__main__':
    unittest.main()
