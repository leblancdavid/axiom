"""R5.23 comprehensive frozen B02 integration retry: whole-program evidence, no repair.

This is not a B02 candidate and not a frozen acceptance run. It assembles the
complete B02 semantic source (every frozen obligation, from `requirements/B02.md`
inherited through `B01.md` and `baseline.md`) and feeds it through the locked
general lowering pipeline. The recorded generation-gate diagnostics are the
finding. Executed probes are disposable B02-shaped slices grounding the
individual compositions that *do* serialize; they are not candidate behavior.
No semantic construct, relation definition, lowerer, planner, runtime, boundary,
binding, provenance or verifier was modified; the post-lock addition is this
evidence file alone.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from benchmark.semantic.capability_boundary_r5_22 import (
    controlled_descriptor, real_descriptor, validate_logged)
from benchmark.semantic.generative_evidence_r5_13 import challenge, observe
from benchmark.semantic.generative_r5_13 import (
    canonical, generate, render, typed, UnsupportedLowering)


# Part 20 / lock integrity: sha256 of the locked working copies at the R5.23 lock.
LOCK_DIGESTS = {
    'benchmark/semantic/typed_lowering_r5_12.py':
        '3e79b67f0ce6a2e44aea3cbf1c2b340609a732ab29446b297bc6599e312077c7',
    'benchmark/semantic/generative_r5_13.py':
        '6e8fd5e2135033c40b5bf9bfc7da68c94eeb59df55ef4011558c1ec46560cafc',
    'benchmark/semantic/generative_runtime_r5_13.py':
        'f71cc378f97d1409c67a35525934b4ed8a7e173411f6b60e6339030906cf1887',
    'benchmark/semantic/generative_evidence_r5_13.py':
        'd025eefdb25bd7d0546cd44a692f3e1ee32ce79db162693a2575c2760cfa4ce9',
    'benchmark/semantic/capability_boundary_r5_22.py':
        '30243e60823ef0087748969308e70203c0bca163a0e99b311c5a12744f83e0ef',
    'air/task_manager.json':
        '971b8ec4079d45101ff8fd7877b6ccd86e7c931124621cf4b5394e93e9dd2f14',
    'benchmark/requirements/B02.md':
        '8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b',
    'benchmark/requirements/B01.md':
        'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d',
    'benchmark/baseline.md':
        'd69de8d4da44c74aff1ac9c6361995ad8dc881f454271cfaedff61d3e98651e5',
    'benchmark/harness/regression.py':
        '8fa1ff4e8b627cc3c334a099151b97647219abac41949a3a3d32c5e9da2fc596',
    'benchmark/harness/profiles/B02.json':
        '46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f',
    'benchmark/harness/capabilities/B02.json':
        '71aa0309e092ec72d8f6b23bfee6d4f7f8420f8a5d5ae380eb01d5777323d456',
}

CLOCK = '2026-07-01T00:00:00Z'


def ref(*parts):
    return {'ref': list(parts)}


def literal(value, shape):
    return {'literal': {'type': shape, 'value': value}}


def external(source):
    return {'external': {'source': source}}


def fallback(value, default):
    return {'fallback': {'value': value, 'default': default}}


def or_(predicates):
    return {'not': {'and': [{'not': predicate} for predicate in predicates]}}


def sel(source, where):
    return {'select': {'source': source, 'where': where}}


def card(source):
    return {'cardinality': source}


def order(source, keys):
    return {'order': {'source': source, 'keys': keys}}


def branch(tag, when, value, transition, value_type=None):
    result = {'tag': tag, 'when': when, 'value': value, 'transition': transition}
    if value_type is not None:
        result['value_type'] = value_type
    return result


def doc(branches, state, contract_input=None):
    return {'id': 'b02.application', 'version': 'r5.23',
            'input': contract_input or B02_INPUT, 'state': state, 'branches': branches}


# Faithful B02 row types. A creation-writing row must store the external clock,
# which the capability boundary types as `instant`; a read ordered by
# (created_at, id) needs an orderable key. The legacy-permissive row additionally
# keeps migration-optional fields for the migrate obligation.
LEGACY_ROW = {'id': 'string', 'title': 'string', 'description': 'string', 'status': 'string',
              'created_at': 'instant', 'priority': {'optional': 'string'},
              'due_date': {'optional': {'nullable': 'instant'}},
              'tags': {'optional': {'sequence': 'string'}}}
CURRENT_ROW = {'id': 'string', 'title': 'string', 'description': 'string', 'status': 'string',
               'priority': 'string', 'created_at': 'instant',
               'due_date': {'nullable': 'instant'}, 'tags': {'sequence': 'string'}}
STATE_LEGACY = {'record': {'schema_version': 'integer',
                           'records': {'sequence': {'record': LEGACY_ROW}}}}
STATE_CURRENT = {'record': {'schema_version': 'integer',
                            'records': {'sequence': {'record': CURRENT_ROW}}}}
B02_INPUT = {'record': {'request': 'string', 'title': {'optional': 'string'},
                        'description': {'optional': 'string'},
                        'priority': {'optional': 'string'},
                        'due_date': {'optional': {'nullable': 'instant'}},
                        'tags': {'optional': {'sequence': 'string'}},
                        'id': {'optional': 'string'}}}

REQ = ref('input', 'request')
SV = ref('pre', 'schema_version')


def is_req(name):
    return {'equals': [REQ, literal(name, 'string')]}


def at_version(number):
    return {'equals': [SV, literal(number, 'integer')]}


CREATED_TASK = {'record': {
    'id': external('fresh_unique_id'),
    'title': fallback(ref('input', 'title'), literal('', 'string')),
    'description': fallback(ref('input', 'description'), literal('', 'string')),
    'status': literal('pending', 'string'),
    'priority': fallback(ref('input', 'priority'), literal('NORMAL', 'string')),
    'created_at': external('utc_clock'),
    'due_date': fallback(ref('input', 'due_date'), literal(None, {'nullable': 'instant'})),
    'tags': {'stable_unique': {'sequence': {'map': {
        'sequence': fallback(ref('input', 'tags'), literal([], {'sequence': 'string'})),
        'transform': 'trim'}}, 'equality': 'case_sensitive_string'}}}}


def fb_id():
    return fallback(ref('input', 'id'), literal('', 'string'))


PENDING_ONE = card(sel(ref('pre', 'records'), {'and': [
    {'equals': [ref('item', 'id'), fb_id()]},
    {'equals': [ref('item', 'status'), literal('pending', 'string')]}]}))
DONE_ONE = card(sel(ref('pre', 'records'), {'and': [
    {'equals': [ref('item', 'id'), fb_id()]},
    {'equals': [ref('item', 'status'), literal('completed', 'string')]}]}))
BY_ID = card(sel(ref('pre', 'records'), {'equals': [ref('item', 'id'), fb_id()]}))
MATCHED_ROW = sel(ref('post', 'records'), {'equals': [ref('item', 'id'), fb_id()]})
PRE_MATCHED_ROW = sel(ref('pre', 'records'), {'equals': [ref('item', 'id'), fb_id()]})

OVERDUE_SOURCE = sel(ref('pre', 'records'), {'and': [
    {'equals': [ref('item', 'status'), literal('pending', 'string')]},
    {'not': {'equals': [ref('item', 'due_date'), literal(None, {'nullable': 'instant'})]}},
    {'before': [ref('item', 'due_date'), external('utc_clock')]}]})

INVALID_PRIORITY = {'and': [
    {'not': {'equals': [fallback(ref('input', 'priority'), literal('NORMAL', 'string')),
                        literal(value, 'string')]}}
    for value in ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')]}

MIGRATE_RELATIONS = [
    {'default_missing': {'collection': 'records', 'identity': 'id', 'field': 'priority',
                         'value': literal('NORMAL', 'string')}},
    {'default_missing': {'collection': 'records', 'identity': 'id', 'field': 'due_date',
                         'value': literal(None, {'nullable': 'instant'})}},
    {'default_missing': {'collection': 'records', 'identity': 'id', 'field': 'tags',
                         'value': literal([], {'sequence': 'string'})}},
    {'post_equals': {'field': 'schema_version', 'value': literal(4, 'integer')}}]

CREATE_GUARDS = [
    branch('invalid_title', {'and': [is_req('create'), {'not': {'nonblank': {'trim': fallback(
        ref('input', 'title'), literal('', 'string'))}}}]},
        literal('invalid_title', 'string'), {'preserve': True}),
    branch('invalid_tag', {'and': [is_req('create'), {'not': {'for_each': {
        'sequence': fallback(ref('input', 'tags'), literal([], {'sequence': 'string'})),
        'bind': 'tag', 'property': {'nonblank': {'trim': ref('tag')}}}}}]},
        literal('invalid_tag', 'string'), {'preserve': True}),
    branch('invalid_priority', {'and': [is_req('create'), INVALID_PRIORITY]},
         literal('invalid_priority', 'string'), {'preserve': True})]

COMPLETE_BRANCHES = [
    branch('migration_required', {'and': [{'not': at_version(4)}, or_([
        is_req('list'), is_req('list-high'), is_req('list-overdue')])]},
        literal('migration_required', 'string'), {'preserve': True}),
    branch('listed', {'and': [is_req('list'), at_version(4)]},
         order(ref('pre', 'records'), ['created_at', 'id']), {'preserve': True},
         {'sequence': {'record': LEGACY_ROW}}),
    branch('listed_high', {'and': [is_req('list-high'), at_version(4)]},
         order(sel(ref('pre', 'records'), {'equals': [
             ref('item', 'priority'), literal('HIGH', 'string')]}), ['created_at', 'id']),
         {'preserve': True}, {'sequence': {'record': LEGACY_ROW}}),
    branch('listed_overdue', {'and': [is_req('list-overdue'), at_version(4)]},
         order(OVERDUE_SOURCE, ['created_at', 'id']), {'preserve': True},
         {'sequence': {'record': LEGACY_ROW}}),
    *CREATE_GUARDS,
    branch('created', is_req('create'), CREATED_TASK,
         {'relations': [{'exact_frame': {'collection': 'records', 'identity': 'id',
                                         'record': CREATED_TASK}}]},
         {'record': LEGACY_ROW}),
    branch('completed', {'and': [is_req('complete'), at_version(4),
                                 {'equals': [PENDING_ONE, literal(1, 'integer')]}]},
         {'sole': MATCHED_ROW},
         {'relations': [{'replace_field': {'collection': 'records', 'key': 'id',
                                           'match': fb_id(), 'field': 'status',
                                           'value': literal('completed', 'string')}}]},
         {'record': LEGACY_ROW}),
    branch('invalid_transition', {'and': [is_req('complete'),
                                          {'equals': [DONE_ONE, literal(1, 'integer')]}]},
         literal('invalid_transition', 'string'), {'preserve': True}),
    branch('task_not_found', {'and': [or_([is_req('complete'), is_req('delete')]),
                                      {'equals': [BY_ID, literal(0, 'integer')]}]},
         literal('task_not_found', 'string'), {'preserve': True}),
    branch('deleted', {'and': [is_req('delete'), {'equals': [BY_ID, literal(1, 'integer')]}]},
         {'sole': PRE_MATCHED_ROW},
         {'relations': [{'remove': {'collection': 'records', 'identity': 'id',
                                    'match': fb_id()}}]},
         {'record': LEGACY_ROW}),
    branch('migrated', {'and': [is_req('migrate'), {'not': at_version(4)}]},
         {'record': {'migrated': {'cardinality': ref('pre', 'records')}}},
         {'relations': MIGRATE_RELATIONS}, {'record': {'migrated': 'integer'}}),
    branch('current', is_req('migrate'),
         {'record': {'migrated': literal(0, 'integer')}}, {'preserve': True},
         {'record': {'migrated': 'integer'}}),
    branch('invalid_request', None, literal('invalid_request', 'string'),
         {'preserve': True})]

# The maximal *composable* integrated document: every branch that the locked
# grammar accepts under one current-row state. list-overdue, versioned migrate
# and (created_at,id) ordering are excluded by the recorded rejections below;
# this document is diagnostic of composition coverage, never a B02 candidate.
MAXIMAL_BRANCHES = [
    branch('migration_required', {'and': [{'not': at_version(4)}, is_req('list')]},
         literal('migration_required', 'string'), {'preserve': True}),
    *CREATE_GUARDS,
    branch('created', is_req('create'), CREATED_TASK,
         {'relations': [{'exact_frame': {'collection': 'records', 'identity': 'id',
                                         'record': CREATED_TASK}}]},
         {'record': CURRENT_ROW}),
    branch('listed', {'and': [is_req('list'), at_version(4)]}, ref('pre', 'records'),
         {'preserve': True}, {'sequence': {'record': CURRENT_ROW}}),
    branch('listed_high', {'and': [is_req('list-high'), at_version(4)]},
         sel(ref('pre', 'records'), {'equals': [
             ref('item', 'priority'), literal('HIGH', 'string')]}),
         {'preserve': True}, {'sequence': {'record': CURRENT_ROW}}),
    branch('completed', {'and': [is_req('complete'), at_version(4),
                                 {'equals': [PENDING_ONE, literal(1, 'integer')]}]},
         {'sole': MATCHED_ROW},
         {'relations': [{'replace_field': {'collection': 'records', 'key': 'id',
                                           'match': fb_id(), 'field': 'status',
                                           'value': literal('completed', 'string')}}]},
         {'record': CURRENT_ROW}),
    branch('invalid_transition', {'and': [is_req('complete'),
                                          {'equals': [DONE_ONE, literal(1, 'integer')]}]},
         literal('invalid_transition', 'string'), {'preserve': True}),
    branch('task_not_found', {'and': [or_([is_req('complete'), is_req('delete')]),
                                      {'equals': [BY_ID, literal(0, 'integer')]}]},
         literal('task_not_found', 'string'), {'preserve': True}),
    branch('deleted', {'and': [is_req('delete'), {'equals': [BY_ID, literal(1, 'integer')]}]},
         {'sole': PRE_MATCHED_ROW},
         {'relations': [{'remove': {'collection': 'records', 'identity': 'id',
                                    'match': fb_id()}}]},
         {'record': CURRENT_ROW}),
    branch('current', is_req('migrate'),
         {'record': {'migrated': literal(0, 'integer')}}, {'preserve': True},
         {'record': {'migrated': 'integer'}}),
    branch('invalid_request', None, literal('invalid_request', 'string'),
         {'preserve': True})]

CURRENT_TASKS = [
    {'id': 't3', 'title': 'Third', 'description': 'x', 'status': 'pending',
     'priority': 'HIGH', 'created_at': '2026-06-03T00:00:00Z', 'due_date': None,
     'tags': ['work', 'Work']},
    {'id': 't1', 'title': 'First', 'description': 'x', 'status': 'completed',
     'priority': 'NORMAL', 'created_at': '2026-06-01T00:00:00Z',
     'due_date': '2020-01-01T00:00:00Z', 'tags': []},
    {'id': 't2', 'title': 'Second', 'description': 'x', 'status': 'pending',
     'priority': 'HIGH', 'created_at': '2026-06-03T00:00:00Z',
     'due_date': '2999-01-01T00:00:00Z', 'tags': ['home']}]


class B02WholeProgramAssembly(unittest.TestCase):
    """Parts 2-4: the complete B02 semantic source through the locked pipeline."""

    def test_complete_document_halts_at_typed_instant_ordering_key(self):
        with self.assertRaises(ValueError) as caught:
            typed(doc(COMPLETE_BRANCHES, STATE_LEGACY))
        # Decisive first whole-program failure: the ordered `list` obligation over
        # the semantically typed creation instant.
        self.assertEqual(str(caught.exception), 'non-orderable key')

    def test_branch_matrix_records_which_compositions_reach_serialization(self):
        expectations = {
            'migration_required': None, 'listed': 'non-orderable key',
            'listed_high': 'equality type mismatch',
            'listed_overdue': 'equality type mismatch',
            'invalid_title': None, 'invalid_tag': None, 'invalid_priority': None,
            'created': 'outcome payload type mismatch',
            'completed': None, 'invalid_transition': None, 'task_not_found': None,
            'deleted': None, 'migrated': None, 'current': None}
        results = {}
        for item in COMPLETE_BRANCHES[:-1]:
            isolated = doc([item, branch('_otherwise', None, literal('x', 'string'),
                                         {'preserve': True})], STATE_LEGACY)
            try:
                typed(isolated)
                render(isolated)
                results[item['tag']] = None
            except Exception as exc:
                results[item['tag']] = str(exc)
        self.assertEqual(results, expectations)

    def test_created_falls_back_to_framed_record_type_conflict_after_value_check(self):
        # With the payload *type* set to the constructed (all-present) record, the
        # decisive create conflict moves to the frame/row type integration.
        contract = doc([
            branch('created', is_req('create'), CREATED_TASK,
                   {'relations': [{'exact_frame': {'collection': 'records', 'identity': 'id',
                                                   'record': CREATED_TASK}}]},
                   {'record': CURRENT_ROW}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})],
            STATE_LEGACY)
        with self.assertRaisesRegex(ValueError, 'framed record type mismatch'):
            typed(contract)

    def test_maximal_integrated_document_types_and_renders(self):
        maximal = doc(MAXIMAL_BRANCHES, STATE_CURRENT)
        self.assertIs(typed(maximal), maximal)
        self.assertTrue(render(maximal))

    def test_clock_and_ordering_type_domains_are_disjoint(self):
        # R5.22 evidence used instant-typed publication fields; R5.20/R5.21 ordering
        # evidence used string timestamps. Neither domain crosses into the other:
        string_row = {**CURRENT_ROW, 'created_at': 'string',
                      'due_date': {'nullable': 'string'}}
        string_state = {'record': {'schema_version': 'integer',
                                   'records': {'sequence': {'record': string_row}}}}
        ordered = doc([branch('listed', is_req('list'), order(ref('pre', 'records'),
                                                              ['created_at', 'id']),
                              {'preserve': True},
                              {'sequence': {'record': string_row}}),
                       branch('_otherwise', None, literal('x', 'string'),
                              {'preserve': True})], string_state)
        typed(ordered)  # control: string created_at orders
        instant = doc([branch('listed', is_req('list'), order(ref('pre', 'records'),
                                                              ['created_at', 'id']),
                              {'preserve': True},
                              {'sequence': {'record': CURRENT_ROW}}),
                       branch('_otherwise', None, literal('x', 'string'),
                              {'preserve': True})], STATE_CURRENT)
        with self.assertRaisesRegex(ValueError, 'non-orderable key'):
            typed(instant)  # typed instant is not an accepted ordering key
        clock_into_string = doc([
            branch('created', is_req('create'), CREATED_TASK,
                   {'relations': [{'exact_frame': {'collection': 'records', 'identity': 'id',
                                                   'record': CREATED_TASK}}]},
                   {'record': string_row}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})],
            string_state)
        with self.assertRaisesRegex(ValueError, 'outcome payload type mismatch'):
            typed(clock_into_string)

    def test_overdue_null_safe_comparison_is_not_lowerable(self):
        # Even with due_date *required-nullable* instant (no optional wrapping), the
        # strict-past predicate rejects: `before` binds only plain instant operands,
        # and the required null exclusion needs a nullable comparison the grammar
        # does not conjunction-guard.
        overdue_required = doc([
            branch('listed_overdue', is_req('list-overdue'),
                   order(sel(ref('pre', 'records'), {'before': [
                       ref('item', 'due_date'), external('utc_clock')]}),
                       ['created_at', 'id']),
                   {'preserve': True}, {'sequence': {'record': CURRENT_ROW}}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})],
            STATE_CURRENT)
        with self.assertRaisesRegex(ValueError, 'before requires two typed instants'):
            typed(overdue_required)

    def test_input_domain_validity_predicates_reject_as_unknown_relations(self):
        # The frozen `invalid_due_date` (and read-time `invalid_state`) obligations
        # need a well-formedness predicate over a supplied optional input; the
        # lowering grammar has no such relation node.
        for kind in ('is_valid_instant', 'provided'):
            probe = doc([branch('probed', {'and': [is_req('create'),
                                                   {kind: ref('input', 'due_date')}]},
                                literal('x', 'string'), {'preserve': True}),
                         branch('_otherwise', None, literal('y', 'string'),
                                {'preserve': True})], STATE_LEGACY)
            with self.assertRaisesRegex(UnsupportedLowering,
                                         'unsupported relation: ' + kind):
                typed(probe)

    def test_version_dependent_row_typing_is_unsupported(self):
        # One contract has one state shape: a row that *requires* tags/priority/due
        # (current v4 reads) cannot simultaneously *permit* their absence (legacy
        # migrate sources), so keyed defaults over the same records reject.
        migrate_current = doc([
            branch('migrated', is_req('migrate'),
                   {'record': {'migrated': {'cardinality': ref('pre', 'records')}}},
                   {'relations': MIGRATE_RELATIONS}, {'record': {'migrated': 'integer'}}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})],
            STATE_CURRENT)
        with self.assertRaisesRegex(ValueError, 'invalid default field or type'):
            typed(migrate_current)

    def test_unversioned_bare_list_state_types_but_cannot_record_version(self):
        # A v1-style bare list migrates as a *sequence* state (probe I), but the
        # versioned post-state equality needs record state; converting bare list to
        # envelope is a storage-shape change no single state declaration permits.
        bare = {'sequence': {'record': LEGACY_ROW}}
        migrate_bare = doc([
            branch('migrated', is_req('migrate'),
                   {'record': {'migrated': {'cardinality': ref('pre')}}},
                   {'relations': [
                       {'default_missing': {'collection': None, 'identity': 'id',
                                            'field': 'priority',
                                            'value': literal('NORMAL', 'string')}},
                       {'default_missing': {'collection': None, 'identity': 'id',
                                            'field': 'due_date',
                                            'value': literal(None, {'nullable': 'instant'})}},
                       {'default_missing': {'collection': None, 'identity': 'id',
                                            'field': 'tags',
                                            'value': literal([], {'sequence': 'string'})}}]},
                   {'record': {'migrated': 'integer'}}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})], bare)
        typed(migrate_bare)  # the transition itself serializes
        with self.assertRaisesRegex(ValueError, 'invalid post equality'):
            typed(doc([
                branch('migrated', is_req('migrate'),
                       {'record': {'migrated': {'cardinality': ref('pre')}}},
                       {'relations': [
                           {'post_equals': {'field': 'schema_version',
                                            'value': literal(4, 'integer')}}]},
                       {'record': {'migrated': 'integer'}}),
                branch('_otherwise', None, literal('x', 'string'),
                       {'preserve': True})], bare))


class B02ExecutableDiagnostics(unittest.TestCase):
    """Parts 9/10/14-18: ground the B02-shaped operations that *do* compose.

    Disposable slices through the same generate -> subprocess -> challenge ->
    conforms path; they ground individual compositions, not a complete candidate.
    """

    def case(self, contract, pre, inp, caps=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe(root, inp, caps=caps)
            verdict = challenge(contract, root, event, public, before, after)
            outcome = json.loads(public['stdout']) if public['exit'] == 0 else None
            return outcome, (json.loads(after) if after else None), verdict, before, after, event

    def test_create_success_full_record_executes_grounds_and_conforms(self):
        single = doc([*CREATE_GUARDS,
                      branch('created', is_req('create'), CREATED_TASK,
                             {'relations': [{'exact_frame': {
                                 'collection': 'records', 'identity': 'id',
                                 'record': CREATED_TASK}}]}, {'record': CURRENT_ROW}),
                      branch('_otherwise', None, literal('x', 'string'),
                             {'preserve': True})], STATE_CURRENT)
        caps = controlled_descriptor({'fresh_unique_id': 'gen-7', 'utc_clock': CLOCK})
        outcome, post, verdict, before, after, event = self.case(
            single, {'schema_version': 4, 'records': []},
            {'request': 'create', 'title': 'Tagged', 'description': 'x',
             'tags': ['  work  ', 'Work', 'work', 'home']}, caps=caps)
        self.assertEqual(outcome, {'kind': 'created', 'value': {
            'id': 'gen-7', 'title': 'Tagged', 'description': 'x', 'status': 'pending',
            'priority': 'NORMAL', 'created_at': CLOCK, 'due_date': None,
            'tags': ['work', 'Work', 'home']}})
        self.assertEqual(post, {'schema_version': 4, 'records': [outcome['value']]})
        self.assertEqual(event['externals'], {'fresh_unique_id': 'gen-7', 'utc_clock': CLOCK})
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        # Real provider: values are typed, recorded and consistent returned/persisted.
        outcome, post, verdict, before, after, event = self.case(
            single, {'schema_version': 4, 'records': []},
            {'request': 'create', 'title': 'Real', 'description': 'x'}, caps=real_descriptor())
        self.assertTrue(verdict['grounded'] and verdict['conformant'])
        self.assertTrue(validate_logged(event['externals']))
        self.assertEqual(outcome['value']['id'], event['externals']['fresh_unique_id'])
        self.assertEqual(outcome['value']['created_at'], event['externals']['utc_clock'])
        self.assertEqual(post['records'][0], outcome['value'])
        self.assertEqual(outcome['value']['tags'], [])

    def test_blank_tag_and_blank_title_fail_with_no_write(self):
        single = doc([*CREATE_GUARDS,
                      branch('created', is_req('create'), CREATED_TASK,
                             {'relations': [{'exact_frame': {
                                 'collection': 'records', 'identity': 'id',
                                 'record': CREATED_TASK}}]}, {'record': CURRENT_ROW}),
                      branch('_otherwise', None, literal('x', 'string'),
                             {'preserve': True})], STATE_CURRENT)
        pre = {'schema_version': 4, 'records': [CURRENT_TASKS[1]]}
        for inp, kind in (({'request': 'create', 'title': 'T', 'description': 'x',
                            'tags': ['  ']}, 'invalid_tag'),
                          ({'request': 'create', 'title': '  ', 'description': 'x'},
                           'invalid_title'),
                          ({'request': 'create', 'title': 'T', 'description': 'x',
                            'priority': 'BANANA'}, 'invalid_priority')):
            outcome, post, verdict, before, after, _ = self.case(single, pre, inp)
            self.assertEqual(outcome['kind'], kind)
            self.assertEqual(before, after)
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_lifecycle_complete_and_delete_execute_over_b02_shaped_envelope(self):
        isolated = COMPLETE_BRANCHES[8]  # completed (envelope replace_field + post sole)
        contract = doc([isolated, branch('_otherwise', None, literal('x', 'string'),
                                         {'preserve': True})], STATE_LEGACY)
        pre = {'schema_version': 4, 'records': [CURRENT_TASKS[2], CURRENT_TASKS[1],
                                                CURRENT_TASKS[0]]}
        outcome, post, verdict, before, after, _ = self.case(
            contract, pre, {'request': 'complete', 'id': 't3'})
        self.assertEqual(outcome['kind'], 'completed')
        self.assertEqual(outcome['value'], {**CURRENT_TASKS[0], 'status': 'completed'})
        self.assertEqual(post, {'schema_version': 4, 'records': [CURRENT_TASKS[2], CURRENT_TASKS[1],
                                                                  {**CURRENT_TASKS[0],
                                                                   'status': 'completed'}]})
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        removed = COMPLETE_BRANCHES[11]  # deleted (keyed remove + pre sole)
        contract = doc([removed, branch('_otherwise', None, literal('x', 'string'),
                                        {'preserve': True})], STATE_LEGACY)
        outcome, post, verdict, before, after, _ = self.case(
            contract, pre, {'request': 'delete', 'id': 't1'})
        self.assertEqual(outcome, {'kind': 'deleted', 'value': CURRENT_TASKS[1]})
        self.assertEqual(post, {'schema_version': 4, 'records': [CURRENT_TASKS[2],
                                                                  CURRENT_TASKS[0]]})
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_envelope_migration_defaults_version_and_count_execute_and_conform(self):
        migrated = COMPLETE_BRANCHES[12]
        contract = doc([migrated, branch('_otherwise', None, literal('x', 'string'),
                                         {'preserve': True})], STATE_LEGACY)
        legacy_rows = [
            {'id': 'm1', 'title': 'Old', 'description': 'x', 'status': 'pending',
             'created_at': '2026-05-01T00:00:00Z'},
            {'id': 'm2', 'title': 'Part', 'description': 'x', 'status': 'pending',
             'created_at': '2026-05-02T00:00:00Z', 'priority': 'HIGH',
             'due_date': None}]
        outcome, post, verdict, before, after, _ = self.case(
            contract, {'schema_version': 1, 'records': legacy_rows}, {'request': 'migrate'})
        self.assertEqual(outcome, {'kind': 'migrated', 'value': {'migrated': 2}})
        self.assertEqual(post, {'schema_version': 4, 'records': [
            {**legacy_rows[0], 'priority': 'NORMAL', 'due_date': None, 'tags': []},
            {**legacy_rows[1], 'tags': []}]})
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        self.assertNotEqual(before, after)

    def test_ordered_read_reconfirms_execution_on_string_typed_b02_rows(self):
        # R5.19/R5.21 transfer reconfirmation on R5.23 fixtures: ordering works only
        # while created_at is string-typed; the semantically instant-typed row is the
        # recorded composition blocker (asserted in the assembly class above).
        ordered_row = {**CURRENT_ROW, 'created_at': 'string', 'due_date': {'nullable': 'string'}}
        state = {'record': {'schema_version': 'integer',
                            'records': {'sequence': {'record': ordered_row}}}}
        contract = doc([
            branch('listed', {'and': [is_req('list'), at_version(4)]},
                   order(ref('pre', 'records'), ['created_at', 'id']), {'preserve': True},
                   {'sequence': {'record': ordered_row}}),
            branch('listed_high', {'and': [is_req('list-high'), at_version(4)]},
                   order(sel(ref('pre', 'records'), {'equals': [
                       ref('item', 'priority'), literal('HIGH', 'string')]}),
                       ['created_at', 'id']),
                   {'preserve': True}, {'sequence': {'record': ordered_row}}),
            branch('_otherwise', None, literal('x', 'string'), {'preserve': True})], state)
        pre = {'schema_version': 4, 'records': [CURRENT_TASKS[0], CURRENT_TASKS[2],
                                                CURRENT_TASKS[1]]}
        outcome, post, verdict, before, after, _ = self.case(
            contract, pre, {'request': 'list'})
        # Storage order differs from semantic order; t2/t3 tie on created_at, id decides.
        self.assertEqual([row['id'] for row in outcome['value']], ['t1', 't2', 't3'])
        self.assertEqual(before, after)
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        outcome, _, verdict, before, after, _ = self.case(
            contract, pre, {'request': 'list-high'})
        self.assertEqual([row['id'] for row in outcome['value']], ['t2', 't3'])
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_migration_required_legacy_read_executes_without_write(self):
        contract = doc([COMPLETE_BRANCHES[0],
                        branch('_otherwise', None, literal('x', 'string'),
                               {'preserve': True})], STATE_LEGACY)
        legacy = {'schema_version': 1, 'records': [CURRENT_TASKS[1]]}
        for command in ('list', 'list-high', 'list-overdue'):
            outcome, post, verdict, before, after, _ = self.case(
                contract, legacy, {'request': command})
            self.assertEqual(outcome, {'kind': 'migration_required',
                                       'value': 'migration_required'})
            self.assertEqual(before, after)
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))


class TransportBindingObservations(unittest.TestCase):
    """Part 19/13: the frozen transport/binding layer, observed on the locked runtime."""

    def maximal_generated(self, folder, cli=False):
        root = Path(folder)
        generate(doc(MAXIMAL_BRANCHES, STATE_CURRENT), root, cli=cli)
        (root / 'state.json').write_bytes(canonical(
            {'schema_version': 4, 'records': CURRENT_TASKS}))
        return root

    def test_frozen_cli_argument_form_is_not_accepted_by_generated_program(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.maximal_generated(folder, cli=True)
            completed = subprocess.run(
                [sys.executable, str(root / 'operation.py'), 'create',
                 '--state', str(root / 'state.json'), '--title', 'T'],
                capture_output=True, text=True, cwd=root, timeout=30)
            # Frozen B02 invokes `APP create --title T ...` positionally; the
            # generic adapter demands named --state/--trace/--invocation/--generation
            # plus one flag per declared input field, so the interface does not match.
            self.assertNotEqual(completed.returncode, 0)

    def test_typed_failure_exits_zero_instead_of_the_frozen_error_envelope(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.maximal_generated(folder)
            event, public, before, after = observe(
                root, {'request': 'create', 'title': 'T', 'description': 'x',
                       'tags': ['  ']})
            self.assertEqual(public['exit'], 0)
            self.assertEqual(json.loads(public['stdout']),
                             {'kind': 'invalid_tag', 'value': 'invalid_tag'})
            # Frozen B02 requires exit 1, empty stdout, stderr {"error":"invalid_tag"}.
            self.assertEqual(public['stderr'], '')

    def test_missing_storage_is_not_treated_as_empty_current_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(doc(MAXIMAL_BRANCHES, STATE_CURRENT), root)
            completed = subprocess.run(
                [sys.executable, str(root / 'operation.py'), str(root / 'state.json'),
                 str(root / 'trace.json'), 'inv', '{}', 'gen'],
                capture_output=True, text=True, cwd=root, timeout=30)
            self.assertNotEqual(completed.returncode, 0)  # baseline: list -> [] no file


class LockIntegrity(unittest.TestCase):
    """Part 20: the locked components are byte-identical after the experiment."""

    def test_locked_components_unchanged_after_experiment(self):
        root = Path(__file__).resolve().parents[2]
        for relative, digest in LOCK_DIGESTS.items():
            with self.subTest(component=relative):
                self.assertEqual(
                    hashlib.sha256((root / relative).read_bytes()).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()
