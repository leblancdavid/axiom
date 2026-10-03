"""R5.22 known general lowering-coverage completion: independent non-task domains.

Two structurally different application domains (environmental sensor readings and
a publication archive) exercise every already-known semantic relation/composition
required by the frozen B02 contract *generatively*: external values through a typed
capability boundary, omitted-input fallback, typed instant comparison, matched-row
and post-transition projection, keyed removal, envelope-shaped keyed replacement,
integrated AST contracts and a metadata-derived CLI binding.  No B02 task, command,
field name, fixture value, version constant or expected output participates; the
lowerer receives domain data only through typed contracts.  No compiler edit occurs
between the two end-to-end operations.
"""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import generative_r5_13
from benchmark.semantic.capability_boundary_r5_22 import (
    CAPABILITY_TYPES, controlled_descriptor, real_descriptor, validate_logged)
from benchmark.semantic.generative_evidence_r5_13 import (
    challenge, conforms, observe, observe_cli)
from benchmark.semantic.generative_r5_13 import (
    canonical, generate, render, sha, typed, UnsupportedLowering)


CLOCK = '2026-07-01T00:00:00Z'
READ_ROW = {'reading_id': 'string', 'station': 'string', 'value': 'integer',
            'unit': 'string', 'recorded_at': 'instant'}
PUB_ROW = {'pub_id': 'string', 'title': 'string', 'published_at': 'instant',
           'stage': 'string'}


def ref(*parts):
    return {'ref': list(parts)}


def literal(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def external(source):
    return {'external': {'source': source}}


def fallback(value, default, shape='string'):
    return {'fallback': {'value': value, 'default': literal(default, shape)}}


def ordered(source, keys):
    return {'order': {'source': source, 'keys': list(keys)}}


# --- sensor domain: external identity + clock, omitted-input fallback, insertion,
#     projected post-transition record, cardinality ---------------------------------

def sensor_reading(input_ref=None, outcome=None):
    return {'record': {
        'reading_id': external('fresh_unique_id'),
        'station': input_ref or ref('input', 'station'),
        'value': ref('input', 'value'),
        'unit': fallback(ref('input', 'unit'), 'celsius'),
        'recorded_at': external('utc_clock')}}


def sensor_register():
    reading = sensor_reading()
    return {'id': 'sensor.reading.register', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'station': 'string',
                                 'value': 'integer', 'unit': {'optional': 'string'}}},
            'state': {'sequence': {'record': READ_ROW}},
            'branches': [
                {'tag': 'recorded', 'when': {'equals': [ref('input', 'request'),
                                                        literal('register')]},
                 'value_type': {'record': READ_ROW}, 'value': reading,
                 'transition': {'relations': [{'exact_frame': {
                     'collection': None, 'identity': 'reading_id', 'record': reading}}]}},
                {'tag': 'unavailable', 'when': None, 'value': literal('unavailable'),
                 'transition': {'preserve': True}}]}


def sensor_reported():
    # Outcome projects the *persisted* row by the actual generated identity.
    reading = sensor_reading()
    return {'id': 'sensor.reading.reported', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'station': 'string',
                                 'value': 'integer', 'unit': {'optional': 'string'}}},
            'state': {'sequence': {'record': READ_ROW}},
            'branches': [
                {'tag': 'recorded', 'when': {'equals': [ref('input', 'request'),
                                                        literal('register')]},
                 'value_type': {'record': {'reading_id': 'string',
                                           'recorded_at': 'instant'}},
                 'value': {'project': {'row': {'sole': {'select': {
                     'source': ref('post'),
                     'where': {'equals': [ref('item', 'reading_id'),
                                          external('fresh_unique_id')]}}}},
                     'fields': ['reading_id', 'recorded_at']}},
                 'transition': {'relations': [{'exact_frame': {
                     'collection': None, 'identity': 'reading_id', 'record': reading}}]}},
                {'tag': 'unavailable', 'when': None, 'value': literal('unavailable'),
                 'transition': {'preserve': True}}]}


# --- archive domain: typed instant comparison, removal, envelope replacement,
#     matched-row and post projection -------------------------------------------------

def archive_select():
    selection = {'select': {'source': ref('pre'), 'where': {
        'before': [ref('item', 'published_at'), ref('input', 'cutoff')]}}}
    return {'id': 'archive.publication.stale', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'cutoff': 'instant'}},
            'state': {'sequence': {'record': PUB_ROW}},
            'branches': [
                {'tag': 'listed', 'when': {'equals': [ref('input', 'request'),
                                                      literal('stale')]},
                 'value_type': {'sequence': {'record': PUB_ROW}},
                 'value': selection, 'transition': {'preserve': True}},
                {'tag': 'none', 'when': None, 'value': literal('none'),
                 'transition': {'preserve': True}}]}


def archive_retire():
    match = {'select': {'source': ref('pre'), 'where': {
        'equals': [ref('item', 'pub_id'), ref('input', 'pub_id')]}}}
    return {'id': 'archive.publication.retire', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'pub_id': 'string'}},
            'state': {'sequence': {'record': PUB_ROW}},
            'branches': [
                {'tag': 'retired', 'when': {'equals': [
                    {'cardinality': match}, literal(1, 'integer')]},
                 'value_type': {'record': {'remaining': 'integer'}},
                 'value': {'record': {'remaining': {'cardinality': ref('post')}}},
                 'transition': {'relations': [{'remove': {
                     'collection': None, 'identity': 'pub_id',
                     'match': ref('input', 'pub_id')}}]}},
                {'tag': 'missing', 'when': None, 'value': literal('missing', 'string'),
                 'transition': {'preserve': True}}]}


def archive_reclassify():
    # Envelope-shaped keyed replacement + projected post-transition record outcome.
    selection = {'select': {'source': ref('pre', 'records'), 'where': {
        'and': [{'equals': [ref('item', 'pub_id'), ref('input', 'pub_id')]},
                {'before': [ref('item', 'published_at'), ref('input', 'cutoff')]}]}}}
    return {'id': 'archive.publication.reclassify', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'pub_id': 'string',
                                 'cutoff': 'instant'}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': PUB_ROW}}}},
            'branches': [
                {'tag': 'reclassified', 'when': {'equals': [
                    {'cardinality': selection}, literal(1, 'integer')]},
                 'value_type': {'record': {'pub_id': 'string', 'stage': 'string'}},
                 'value': {'project': {'row': {'sole': {'select': {
                     'source': ref('post', 'records'),
                     'where': {'equals': [ref('item', 'pub_id'),
                                          ref('input', 'pub_id')]}}}},
                     'fields': ['pub_id', 'stage']}},
                 'transition': {'relations': [
                     {'replace_field': {'collection': 'records', 'key': 'pub_id',
                                        'match': ref('input', 'pub_id'),
                                        'field': 'stage',
                                        'value': literal('archived', 'string')}}]}},
                {'tag': 'unaffected', 'when': None, 'value': literal('unaffected', 'string'),
                 'transition': {'preserve': True}}]}


def guarded_single_relation(node, shape):
    # A minimal AST for one relation node used as a branch outcome.
    return {'id': 'probe.relation', 'version': 'r5.22',
            'input': {'record': {'request': 'string', 'a': 'string',
                                 'b': 'string', 'when': {'optional': 'string'}}},
            'state': {'sequence': {'record': READ_ROW}},
            'branches': [
                {'tag': 'probed', 'when': {'equals': [ref('input', 'request'),
                                                      literal('probe')]},
                 'value_type': shape, 'value': node, 'transition': {'preserve': True}},
                {'tag': 'otherwise', 'when': None, 'value': literal('otherwise', 'string'),
                 'transition': {'preserve': True}}]}


READINGS = [{'reading_id': 'r1', 'station': 'north', 'value': 10, 'unit': 'celsius',
             'recorded_at': '2026-06-01T00:00:00Z'},
            {'reading_id': 'r2', 'station': 'south', 'value': 20, 'unit': 'fahrenheit',
             'recorded_at': '2026-06-02T00:00:00Z'}]

PUBLICATIONS = [{'pub_id': 'p1', 'title': 'Early', 'published_at': '2020-01-01T00:00:00Z',
                 'stage': 'live'},
                {'pub_id': 'p2', 'title': 'Equal', 'published_at': '2021-01-01T00:00:00Z',
                 'stage': 'live'},
                {'pub_id': 'p3', 'title': 'Late', 'published_at': '2022-01-01T00:00:00Z',
                 'stage': 'live'}]


class LoweringCoverageR5_22(unittest.TestCase):
    def case(self, contract, pre, inp, caps=None, fault=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root, fault=fault)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe(root, inp, caps=caps)
            verdict = challenge(contract, root, event, public, before, after)
            outcome = json.loads(public['stdout']) if public['exit'] == 0 else None
            return outcome, json.loads(after) if after else pre, before, after, verdict, event

    # ---- Part 2/3/5/19: external + fallback + framed insertion, controlled provider
    def test_external_and_fallback_frame_insertion_executes_grounds_and_conforms(self):
        caps = controlled_descriptor({'fresh_unique_id': 'gen-7', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict, event = self.case(
            sensor_register(), [READINGS[0]], {'request': 'register', 'station': 'east',
                                               'value': 42}, caps=caps)
        self.assertEqual(outcome, {'kind': 'recorded', 'value': {
            'reading_id': 'gen-7', 'station': 'east', 'value': 42,
            'unit': 'celsius', 'recorded_at': CLOCK}})
        self.assertEqual(post, [READINGS[0], outcome['value']])
        self.assertEqual(event['externals'], {'fresh_unique_id': 'gen-7', 'utc_clock': CLOCK})
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        self.assertNotEqual(before, after)

    def test_explicit_input_wins_over_fallback(self):
        caps = controlled_descriptor({'fresh_unique_id': 'gen-8', 'utc_clock': CLOCK})
        outcome, _, _, _, verdict, _ = self.case(
            sensor_register(), [], {'request': 'register', 'station': 'west',
                                    'value': 1, 'unit': 'kelvin'}, caps=caps)
        self.assertEqual(outcome['value']['unit'], 'kelvin')
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_real_provider_supplies_typed_external_values(self):
        outcome, post, _, _, verdict, event = self.case(
            sensor_register(), [], {'request': 'register', 'station': 'core',
                                    'value': 5}, caps=real_descriptor())
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        self.assertTrue(validate_logged(event['externals']))
        self.assertEqual(len(post), 1)
        # The persisted row's identity equals the actually supplied external value.
        self.assertEqual(post[0]['reading_id'], event['externals']['fresh_unique_id'])
        self.assertEqual(post[0]['recorded_at'], event['externals']['utc_clock'])

    # ---- Part 6: faithful grounded external lowering fault breaks returned/persisted
    def test_external_fault_grounds_but_breaks_recorded_persisted_fidelity(self):
        caps = controlled_descriptor({'fresh_unique_id': 'gen-9', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict, event = self.case(
            sensor_register(), [], {'request': 'register', 'station': 'n', 'value': 2},
            caps=caps, fault=True)
        self.assertEqual(outcome['value']['reading_id'], '__injected_stale_identity__')
        self.assertEqual(post[0]['reading_id'], 'gen-9')  # persisted uses the actual value
        self.assertEqual((verdict['provenance_valid'], verdict['grounded']), (True, True))
        self.assertFalse(verdict['conformant'])

    # ---- Part 3/4: capability boundary rejects wrong type / unknown / missing provider
    def test_capability_boundary_rejects_incompatible_and_unknown_use(self):
        with self.assertRaisesRegex(ValueError, 'unknown capability'):
            typed(guarded_single_relation(external('bogus'), 'string'))
        # A clock capability (instant) used where a plain string is required.
        with self.assertRaisesRegex(ValueError, 'outcome payload type mismatch'):
            typed(guarded_single_relation(external('utc_clock'), 'string'))
        with self.assertRaisesRegex(ValueError, 'violates capability type'):
            controlled_descriptor({'utc_clock': 'not-a-timestamp'})

    def test_controlled_provider_missing_capability_fails_to_ground(self):
        # Freshness/typing cannot be silently fabricated; an absent controlled value
        # makes the generated program refuse to run, so grounding (faithfully) fails.
        outcome, post, before, after, verdict, event = self.case(
            sensor_register(), [], {'request': 'register', 'station': 'n', 'value': 2},
            caps=controlled_descriptor({'utc_clock': CLOCK}))
        self.assertFalse(verdict['grounded'])

    # ---- Part 7/8: fallback semantic-only mutation changes generated behavior
    def test_fallback_semantic_only_default_mutation_changes_generated_behavior(self):
        base = sensor_register()
        outcome, _, _, _, verdict, _ = self.case(
            base, [], {'request': 'register', 'station': 's', 'value': 3},
            caps=controlled_descriptor({'fresh_unique_id': 'x1', 'utc_clock': CLOCK}))
        self.assertEqual(outcome['value']['unit'], 'celsius')
        mutated = copy.deepcopy(base)
        mutated['branches'][0]['value']['record']['unit'] = fallback(
            ref('input', 'unit'), 'kelvin')
        outcome, _, _, _, verdict, _ = self.case(
            mutated, [], {'request': 'register', 'station': 's', 'value': 3},
            caps=controlled_descriptor({'fresh_unique_id': 'x2', 'utc_clock': CLOCK}))
        self.assertEqual(outcome['value']['unit'], 'kelvin')
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertNotEqual(sha(canonical(base)), sha(canonical(mutated)))

    def test_incompatible_fallback_default_is_rejected_by_typing(self):
        bad = sensor_register()
        bad['branches'][0]['value']['record']['unit'] = {
            'fallback': {'value': ref('input', 'unit'),
                         'default': literal(7, 'integer')}}
        with self.assertRaisesRegex(ValueError, 'incompatible fallback default'):
            typed(bad)

    # ---- Part 9: typed instant before/equal/after via general selection
    def test_before_comparison_selects_strict_earlier_ignoring_equal_and_later(self):
        contract = archive_select()
        self.assertIsNotNone(typed(contract))
        outcome, post, before, after, verdict, _ = self.case(
            contract, PUBLICATIONS, {'request': 'stale', 'cutoff': '2021-01-01T00:00:00Z'})
        self.assertEqual([row['pub_id'] for row in outcome['value']], ['p1'])
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        after_all = self.case(contract, PUBLICATIONS,
                              {'request': 'stale', 'cutoff': '2025-01-01T00:00:00Z'})[0]
        self.assertEqual([row['pub_id'] for row in after_all['value']], ['p1', 'p2', 'p3'])
        none = self.case(contract, PUBLICATIONS,
                         {'request': 'stale', 'cutoff': '2000-01-01T00:00:00Z'})[0]
        self.assertEqual(none['value'], [])

    def test_before_requires_typed_instants_and_rejects_plain_strings(self):
        with self.assertRaisesRegex(ValueError, 'before requires two typed instants'):
            typed(guarded_single_relation({'before': [ref('input', 'a'), ref('input', 'b')]},
                                          'boolean'))

    # ---- Part 10/11: matched-row and post-transition projection preserve durable state
    def test_projected_post_record_matches_persisted_row_without_rewriting_storage(self):
        caps = controlled_descriptor({'fresh_unique_id': 'g5', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict, event = self.case(
            sensor_reported(), [READINGS[0]], {'request': 'register', 'station': 'q',
                                               'value': 9}, caps=caps)
        self.assertEqual(outcome, {'kind': 'recorded',
                                   'value': {'reading_id': 'g5', 'recorded_at': CLOCK}})
        self.assertEqual(post[1]['reading_id'], 'g5')
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertNotEqual(before, after)

    # ---- Part 12/13: keyed removal preserves unrelated records, drops the target
    def test_remove_targets_only_the_keyed_element_and_preserves_the_rest(self):
        contract = archive_retire()
        self.assertIsNotNone(typed(contract))
        outcome, post, before, after, verdict, _ = self.case(
            contract, PUBLICATIONS, {'request': 'retire', 'pub_id': 'p2'})
        self.assertEqual(outcome, {'kind': 'retired', 'value': {'remaining': 2}})
        self.assertEqual([row['pub_id'] for row in post], ['p1', 'p3'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertNotEqual(before, after)

    def test_remove_absent_target_selects_guarded_not_found_and_writes_nothing(self):
        outcome, post, before, after, verdict, _ = self.case(
            archive_retire(), PUBLICATIONS, {'request': 'retire', 'pub_id': 'zzz'})
        self.assertEqual(outcome, {'kind': 'missing', 'value': 'missing'})
        self.assertEqual(post, PUBLICATIONS)
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    # ---- Part 14: faithfully grounded removal faults fail semantic conformance
    def test_removal_faults_ground_but_fail_semantic_conformance(self):
        # A disposable lowering fault drops the first element by position instead of
        # the keyed target: the run still grounds faithfully, but the contract is broken.
        outcome, post, before, after, verdict, _ = self.case(
            archive_retire(), PUBLICATIONS, {'request': 'retire', 'pub_id': 'p2'}, fault=True)
        self.assertEqual([row['pub_id'] for row in post], ['p2', 'p3'])
        self.assertEqual((verdict['provenance_valid'], verdict['grounded']), (True, True))
        self.assertFalse(verdict['conformant'])

    # ---- Part 15/16: envelope-shaped keyed replacement + composition
    def test_envelope_keyed_replacement_and_projected_post_result(self):
        envelope = [dict(row) for row in PUBLICATIONS]
        pre = {'schema_version': 2, 'records': envelope}
        contract = archive_reclassify()
        self.assertIsNotNone(typed(contract))
        outcome, post, before, after, verdict, _ = self.case(
            contract, pre, {'request': 'reclassify', 'pub_id': 'p1',
                            'cutoff': '2021-06-01T00:00:00Z'})
        self.assertEqual(outcome, {'kind': 'reclassified',
                                   'value': {'pub_id': 'p1', 'stage': 'archived'}})
        self.assertEqual(post['schema_version'], 2)
        self.assertEqual([row['stage'] for row in post['records']],
                         ['archived', 'live', 'live'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_envelope_replacement_rejects_when_guard_not_satisfied(self):
        pre = {'schema_version': 2, 'records': [dict(row) for row in PUBLICATIONS]}
        outcome, post, before, after, verdict, _ = self.case(
            archive_reclassify(), pre,
            {'request': 'reclassify', 'pub_id': 'p3', 'cutoff': '2021-06-01T00:00:00Z'})
        self.assertEqual(outcome, {'kind': 'unaffected', 'value': 'unaffected'})
        self.assertEqual(post, pre)
        self.assertEqual(before, after)
        self.assertTrue(verdict['conformant'])

    def test_replace_field_fault_grounds_but_keeps_old_value(self):
        pre = {'schema_version': 2, 'records': [dict(row) for row in PUBLICATIONS]}
        outcome, post, _, _, verdict, _ = self.case(
            archive_reclassify(), pre,
            {'request': 'reclassify', 'pub_id': 'p1', 'cutoff': '2021-06-01T00:00:00Z'},
            fault=True)
        self.assertTrue(verdict['grounded'])
        self.assertFalse(verdict['conformant'])

    # ---- Part 24: unknown relation still rejects explicitly (safe unsupported)
    def test_unknown_relations_reject_explicitly_never_silently(self):
        for node, message in (({'aggregate': {'op': 'sum'}}, 'aggregate'),
                              ({'unregistered': {'x': 1}}, 'unregistered')):
            with self.assertRaisesRegex(UnsupportedLowering, message):
                typed(guarded_single_relation(node, 'string'))

    def test_overlapping_collection_transforms_still_reject(self):
        # a frame and a removal on one collection are noncommuting and reject.
        reading = sensor_reading()
        contract = {'id': 'overlap', 'version': 'r5.22',
                    'input': {'record': {'request': 'string', 'station': 'string',
                                         'value': 'integer', 'unit': {'optional': 'string'},
                                         'pub_id': 'string'}},
                    'state': {'sequence': {'record': READ_ROW}},
                    'branches': [
                        {'tag': 'x', 'when': {'equals': [ref('input', 'request'),
                                                          literal('x')]},
                         'value_type': 'string', 'value': literal('x', 'string'),
                         'transition': {'relations': [
                             {'exact_frame': {'collection': None, 'identity': 'reading_id',
                                              'record': reading}},
                             {'remove': {'collection': None, 'identity': 'reading_id',
                                         'match': ref('input', 'station')}}]}},
                        {'tag': 'y', 'when': None, 'value': literal('y', 'string'),
                         'transition': {'preserve': True}}]}
        with self.assertRaisesRegex(UnsupportedLowering, 'overlapping collection'):
            typed(contract)

    # ---- Part 18: same generated operation reached through a metadata-derived CLI
    def cli_case(self, contract, pre, inp, caps=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root, cli=True)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe_cli(root, inp, caps=caps)
            verdict = challenge(contract, root, event, public, before, after)
            outcome = json.loads(public['stdout']) if public['exit'] == 0 else None
            return outcome, json.loads(after) if after else pre, before, after, verdict

    def test_generated_operation_uses_a_generic_cli_binding_not_domain_dispatch(self):
        caps = controlled_descriptor({'fresh_unique_id': 'cli-1', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict = self.cli_case(
            sensor_register(), [], {'request': 'register', 'station': 'depot',
                                    'value': 33}, caps=caps)
        self.assertEqual(outcome, {'kind': 'recorded', 'value': {
            'reading_id': 'cli-1', 'station': 'depot', 'value': 33,
            'unit': 'celsius', 'recorded_at': CLOCK}})
        self.assertEqual(post, [outcome['value']])
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'],
                          verdict['conformant']), (True, True, True))
        # The CLI adapter derives flags from checked binding metadata; no per-command
        # parser lives in the generic runtime.
        self.assertIn(b'run_cli(', render(sensor_register(), cli=True))
        self.assertNotIn(b'argparse', render(sensor_register(), cli=True))

    # ---- Part 23: fallback lowering fault grounds faithfully but breaks the contract
    def test_fallback_fault_ignores_present_input_grounds_but_fails_conformance(self):
        caps = controlled_descriptor({'fresh_unique_id': 'fb-1', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict, _ = self.case(
            sensor_register(), [], {'request': 'register', 'station': 's',
                                    'value': 4, 'unit': 'kelvin'}, caps=caps, fault=True)
        self.assertEqual(outcome['value']['unit'], 'celsius')  # returned ignored explicit
        self.assertEqual(post[0]['unit'], 'kelvin')            # persisted honored it
        self.assertEqual((verdict['provenance_valid'], verdict['grounded']), (True, True))
        self.assertFalse(verdict['conformant'])

    # ---- Part 11: read-only projection never rewrites durable state
    def test_read_only_subset_projection_preserves_durable_bytes(self):
        contract = {'id': 'archive.publication.digest', 'version': 'r5.22',
                    'input': {'record': {'request': 'string', 'pub_id': 'string'}},
                    'state': {'sequence': {'record': PUB_ROW}},
                    'branches': [
                        {'tag': 'digest', 'when': {'equals': [ref('input', 'request'),
                                                              literal('digest')]},
                         'value_type': {'record': {'pub_id': 'string', 'stage': 'string'}},
                         'value': {'project': {'row': {'sole': {'select': {
                             'source': ref('pre'),
                             'where': {'equals': [ref('item', 'pub_id'),
                                                  ref('input', 'pub_id')]}}}},
                             'fields': ['pub_id', 'stage']}},
                         'transition': {'preserve': True}},
                        {'tag': 'none', 'when': None, 'value': literal('none'),
                         'transition': {'preserve': True}}]}
        outcome, post, before, after, verdict, _ = self.case(
            contract, PUBLICATIONS, {'request': 'digest', 'pub_id': 'p2'})
        self.assertEqual(outcome, {'kind': 'digest',
                                   'value': {'pub_id': 'p2', 'stage': 'live'}})
        self.assertEqual(post, PUBLICATIONS)
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    # ---- Part 19/20/21: two operations, then change only semantics and regenerate
    def test_operation_one_semantic_mutation_changes_behavior_without_lowerer_edit(self):
        caps = controlled_descriptor({'fresh_unique_id': 'm1', 'utc_clock': CLOCK})
        before_shape = self.case(sensor_reported(), [], {'request': 'register',
                                                         'station': 'a', 'value': 1},
                                 caps=caps)[0]['value']
        self.assertEqual(set(before_shape), {'reading_id', 'recorded_at'})
        mutated = copy.deepcopy(sensor_reported())
        mutated['branches'][0]['value']['project']['fields'] = ['station', 'unit']
        mutated['branches'][0]['value_type'] = {'record': {'station': 'string',
                                                            'unit': 'string'}}
        outcome, _, _, _, verdict, _ = self.case(
            mutated, [], {'request': 'register', 'station': 'b', 'value': 2},
            caps=controlled_descriptor({'fresh_unique_id': 'm2', 'utc_clock': CLOCK}))
        self.assertEqual(set(outcome['value']), {'station', 'unit'})
        self.assertEqual(outcome['value'], {'station': 'b', 'unit': 'celsius'})
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_operation_two_semantic_mutation_changes_behavior_without_lowerer_edit(self):
        pre = {'schema_version': 2, 'records': [dict(row) for row in PUBLICATIONS]}
        base = archive_reclassify()
        _, post, _, _, verdict, _ = self.case(
            base, pre, {'request': 'reclassify', 'pub_id': 'p1',
                        'cutoff': '2021-06-01T00:00:00Z'})
        self.assertEqual([row['stage'] for row in post['records']], ['archived', 'live', 'live'])
        self.assertTrue(verdict['conformant'])
        # Change only the semantic replacement value (target stage), not the lowerer.
        mutated = copy.deepcopy(base)
        mutated['branches'][0]['transition']['relations'][0]['replace_field']['value'] = \
            literal('retired', 'string')
        _, post, _, _, verdict, _ = self.case(
            mutated, pre, {'request': 'reclassify', 'pub_id': 'p1',
                            'cutoff': '2021-06-01T00:00:00Z'})
        self.assertEqual([row['stage'] for row in post['records']], ['retired', 'live', 'live'])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    # ---- Part 9: `before` as a typed boolean outcome over before/equal/after
    def test_before_yields_typed_boolean_outcome(self):
        def compare(cutoff_shape='instant'):
            return {'id': 'clock.compare', 'version': 'r5.22',
                    'input': {'record': {'request': 'string', 'cutoff': cutoff_shape}},
                    'state': {'sequence': {'record': READ_ROW}},
                    'branches': [
                        {'tag': 'compared', 'when': {'equals': [ref('input', 'request'),
                                                                literal('compare')]},
                         'value_type': 'boolean',
                         'value': {'before': [literal('2020-01-01T00:00:00Z', 'instant'),
                                              ref('input', 'cutoff')]},
                         'transition': {'preserve': True}},
                        {'tag': 'none', 'when': None, 'value': literal('none'),
                         'transition': {'preserve': True}}]}
        for cutoff, expected in (('2021-01-01T00:00:00Z', True),   # literal is before
                                 ('2020-01-01T00:00:00Z', False),  # equal: strict fails
                                 ('2019-01-01T00:00:00Z', False)):  # literal is after
            outcome, _, before, after, verdict, _ = self.case(compare(), [], {'request': 'compare',
                                                                               'cutoff': cutoff})
            self.assertEqual(outcome, {'kind': 'compared', 'value': expected})
            self.assertEqual(before, after)
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    # ---- Part 6: freshness is enforced, not fabricated, on a reused identity
    def test_external_stale_reused_identity_is_rejected_by_generated_freshness(self):
        # The controlled provider hands back an identity already present; the exact-frame
        # structural guard refuses to insert a duplicate, so the run does not ground.
        caps = controlled_descriptor({'fresh_unique_id': 'r1', 'utc_clock': CLOCK})
        outcome, post, before, after, verdict, event = self.case(
            sensor_register(), [READINGS[0]], {'request': 'register', 'station': 'n',
                                               'value': 1}, caps=caps)
        self.assertIsNone(outcome)
        self.assertFalse(verdict['grounded'])
        self.assertEqual(before, after)  # nothing was written

    # ---- Part 25: no behavioral dependency on B02 vocabulary in any changed module.
    def test_changed_modules_contain_no_task_b02_or_benchmark_vocabulary(self):
        tokens = ("'created_at'", "'task'", "'b02'", 'B02', "'priority'", "'due_date'",
                  "'critical'", "'CRITICAL'", "'NORMAL'", "'HIGH'", "'tags'", "'status'",
                  "'title'", 'insert_task', 'tasks.json', 'schema_version', 'migrate',
                  'delete_task', 'list-high', 'list-overdue')
        for module in (generative_r5_13, 'benchmark.semantic.typed_lowering_r5_12',
                       'benchmark.semantic.capability_boundary_r5_22',
                       'benchmark.semantic.generative_runtime_r5_13',
                       'benchmark.semantic.generative_evidence_r5_13'):
            path = Path(module.__file__) if hasattr(module, '__file__') else Path(
                __import__(module, fromlist=['x']).__file__)
            text = path.read_text(encoding='utf-8')
            for token in tokens:
                self.assertNotIn(token, text, f'{path.name} leaks {token}')


if __name__ == '__main__':
    unittest.main()
