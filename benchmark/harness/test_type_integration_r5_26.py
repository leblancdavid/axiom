"""Independent R5.26 read-only generated integration witnesses."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import generative_r5_13 as historical
from benchmark.semantic.generative_evidence_r5_13 import observe
from benchmark.semantic import type_integration_r5_26 as integrated


def ref(*path):
    return {'ref': list(path)}


def literal(value, shape):
    return {'literal': {'type': shape, 'value': value}}


def contract(kind='instant', field='released', cutoff=None, keys=None, reversed_guard=False):
    fields = {'code': 'string', 'released': {'optional': kind},
              'alternate': {'optional': kind}, 'label': 'string', 'edition': 'integer'}
    presence = {'present': ref('item', field)}
    compare = ({'before': [ref('item', field), ref('input', 'cutoff')]} if kind == 'instant' else
               {'equals': [ref('item', field), ref('input', 'cutoff')]})
    where = {'and': [compare, presence] if reversed_guard else [presence, compare]}
    selection = {'select': {'source': ref('pre'), 'where': where}}
    value = {'order': {'source': selection, 'keys': list(keys)}} if keys else selection
    return {'id': 'publication.archive.find', 'version': 'R5.26',
            'input': {'record': {'cutoff': kind, 'action': 'string'}},
            'state': {'sequence': {'record': fields}},
            'branches': [
                {'tag': 'found', 'when': {'equals': [ref('input', 'action'), literal('find', 'string')]},
                 'value': value, 'value_type': {'sequence': {'record': fields}},
                 'transition': {'preserve': True}},
                {'tag': 'ignored', 'when': None, 'value': literal('ignored', 'string'),
                 'value_type': 'string', 'transition': {'preserve': True}}]}


EARLY = '2026-05-01T00:00:00Z'
CUTOFF = '2026-05-10T00:00:00Z'
LATE = '2026-05-20T00:00:00Z'
ROWS = [
    {'code': 'absent', 'label': 'x', 'edition': 4},
    {'code': 'late', 'label': 'b', 'edition': 2, 'released': LATE},
    {'code': 'early-b', 'label': 'b', 'edition': 3, 'released': EARLY},
    {'code': 'equal', 'label': 'x', 'edition': 0, 'released': CUTOFF},
    {'code': 'early-a', 'label': 'a', 'edition': 1, 'released': EARLY},
]


class TypeIntegrationR526(unittest.TestCase):
    def case(self, model, rows=ROWS, fault=None, cutoff=CUTOFF):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            integrated.generate(model, root, fault=fault)
            (root / 'state.json').write_bytes(integrated.base.canonical(rows))
            internal, public, before, after = observe(root, {'action': 'find', 'cutoff': cutoff})
            verdict = integrated.challenge(model, root, internal, public, before, after)
            self.assertEqual(before, after)
            return json.loads(public['stdout']), verdict

    def test_refinement_orders_exact_selection_and_fault(self):
        for reverse in (False, True):
            model = contract(reversed_guard=reverse)
            outcome, verdict = self.case(model)
            self.assertEqual([r['code'] for r in outcome['value']], ['early-b', 'early-a'])
            self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True, 'conformant': True})
        wrong, verdict = self.case(contract(), fault='absent')
        self.assertIn('absent', [r['code'] for r in wrong['value']])
        self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True, 'conformant': False})

    def test_wrong_target_unguarded_scope_and_post_state(self):
        source = contract()
        variants = []
        bare = copy.deepcopy(source)
        bare['branches'][0]['value']['select']['where'] = {'before': [ref('item', 'released'), ref('input', 'cutoff')]}
        variants.append(bare)
        wrong = copy.deepcopy(source)
        wrong['branches'][0]['value']['select']['where']['and'][0] = {'present': ref('item', 'alternate')}
        variants.append(wrong)
        other_record = copy.deepcopy(source)
        other_record['input']['record']['released'] = {'optional': 'instant'}
        other_record['branches'][0]['value']['select']['where']['and'][0] = {'present': ref('input', 'released')}
        variants.append(other_record)
        required = copy.deepcopy(source)
        required['branches'][0]['value']['select']['where']['and'][0] = {'present': ref('item', 'code')}
        with self.assertRaisesRegex(ValueError, 'presence requires optional field'):
            integrated.typed(required)
        escaped = copy.deepcopy(source)
        where = escaped['branches'][0]['value']['select']['where']
        escaped['branches'][0]['value']['select']['where'] = {'and': [
            where, {'before': [ref('item', 'released'), ref('input', 'cutoff')]}]}
        variants.append(escaped)
        post = copy.deepcopy(source)
        post['branches'][0]['value']['select']['where']['and'][1]['before'][0] = ref('post', 'released')
        variants.append(post)
        for model in variants:
            with self.subTest(model=model), self.assertRaisesRegex(ValueError, 'optional operand|invalid reference'):
                integrated.typed(model)
        # A guard cannot authorize an independent operation's predicate.
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            integrated.typed(bare)

    def test_string_integer_and_identity_mutations(self):
        for kind, match, other in [('string', 'signed', 'draft'), ('integer', 7, 8)]:
            rows = [{'code': 'missing', 'label': 'x', 'edition': 0},
                    {'code': 'yes', 'label': 'y', 'edition': 1, 'released': match},
                    {'code': 'no', 'label': 'z', 'edition': 2, 'released': other}]
            model = contract(kind=kind)
            outcome, verdict = self.case(model, rows, cutoff=match)
            self.assertEqual([r['code'] for r in outcome['value']], ['yes'])
            self.assertTrue(verdict['conformant'])
            for row in rows:
                row['alternate'] = other
            changed = contract(kind=kind, field='alternate')
            outcome, verdict = self.case(changed, rows, cutoff=other)
            self.assertEqual([r['code'] for r in outcome['value']], ['missing', 'yes', 'no'])
            self.assertTrue(verdict['conformant'])

    def test_instant_order_ties_secondary_and_fault(self):
        rows = [{**row, 'released': row.get('released', EARLY)} for row in ROWS]
        for keys in [('released',), ('released', 'label'), ('released', 'edition')]:
            model = contract(keys=keys, cutoff=None)
            model['branches'][0]['value']['order']['source'] = ref('pre')
            model['state']['sequence']['record']['released'] = 'instant'
            model['branches'][0]['value_type']['sequence']['record']['released'] = 'instant'
            outcome, verdict = self.case(model, rows, cutoff=LATE)
            self.assertTrue(verdict['conformant'])
            self.assertEqual([tuple(r[k] for k in keys) for r in outcome['value']],
                             sorted(tuple(r[k] for k in keys) for r in rows))
        model = contract(keys=('released',))
        outcome, verdict = self.case(model, fault='reverse', cutoff=LATE)
        self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True, 'conformant': False})
        model = contract(keys=('released', 'label'))
        outcome, verdict = self.case(model, cutoff=LATE)
        self.assertEqual([r['code'] for r in outcome['value']], ['early-a', 'early-b', 'equal'])
        self.assertTrue(verdict['conformant'])
        changed_rows = copy.deepcopy(ROWS)
        changed_rows[2]['edition'], changed_rows[4]['edition'] = 1, 3
        by_label, verdict = self.case(model, changed_rows, cutoff=LATE)
        self.assertEqual([r['code'] for r in by_label['value']], ['early-a', 'early-b', 'equal'])
        self.assertTrue(verdict['conformant'])
        model['branches'][0]['value']['order']['keys'][1] = 'edition'
        outcome, verdict = self.case(model, changed_rows, cutoff=LATE)
        self.assertEqual([r['code'] for r in outcome['value']], ['early-b', 'early-a', 'equal'])
        self.assertTrue(verdict['conformant'])
        # Ties under the declared key are unconstrained, including in the verifier.
        one = contract(keys=('released',))
        source = {'input': one['input'], 'pre': one['state']}
        order = one['branches'][0]['value']['order']
        facts = {'input': {'action': 'find', 'cutoff': LATE}, 'pre': ROWS}
        self.assertTrue(integrated._ordered_holds(order, facts, source,
                        [ROWS[4], ROWS[2], ROWS[3]]))

    def test_mutations_and_version_boundary(self):
        model = contract()
        outcome, _ = self.case(model, cutoff=LATE)
        self.assertEqual([r['code'] for r in outcome['value']], ['early-b', 'equal', 'early-a'])
        outcome, _ = self.case(model, cutoff=EARLY)
        self.assertEqual(outcome['value'], [])
        changed = copy.deepcopy(model)
        changed['branches'][0]['value']['select']['where']['and'][1]['before'][1] = literal(LATE, 'instant')
        outcome, verdict = self.case(changed)
        self.assertEqual([r['code'] for r in outcome['value']], ['early-b', 'equal', 'early-a'])
        self.assertTrue(verdict['conformant'])
        with self.assertRaisesRegex(ValueError, 'unsupported relation: present'):
            historical.typed(model)
        old = copy.deepcopy(model)
        old['version'] = 'R5.23'
        with self.assertRaisesRegex(ValueError, 'versioned identity'):
            integrated.typed(old)

    def test_checker_verifier_agreement_on_optional_and_order_capabilities(self):
        model = contract(keys=('released',))
        self.assertIs(integrated.typed(model), model)
        selected = [ROWS[2], ROWS[4]]
        self.assertTrue(integrated.conforms(model, {'action': 'find', 'cutoff': CUTOFF}, ROWS,
                        {'kind': 'found', 'value': selected}, ROWS, True, False))
        unsafe = copy.deepcopy(model)
        unsafe['branches'][0]['value']['order']['source'] = ref('pre')
        with self.assertRaisesRegex(ValueError, 'optional key needs selection presence'):
            integrated.typed(unsafe)
        nested = copy.deepcopy(model)
        nested['branches'][0]['value']['order']['source'] = {
            'order': {'source': ref('pre'), 'keys': ['label']}}
        with self.assertRaisesRegex(ValueError, 'nested order'):
            integrated.typed(nested)
        nullable = copy.deepcopy(model)
        nullable['state']['sequence']['record']['released'] = {'optional': {'nullable': 'instant'}}
        nullable['branches'][0]['value_type']['sequence']['record']['released'] = {'optional': {'nullable': 'instant'}}
        with self.assertRaisesRegex(ValueError, 'before requires two typed instants'):
            integrated.typed(nullable)
        # Two distinct optional fields of the same type retain distinct identities.
        mismatch = copy.deepcopy(model)
        where = mismatch['branches'][0]['value']['order']['source']['select']['where']
        where['and'][0] = {'present': ref('item', 'alternate')}
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            integrated.typed(mismatch)


if __name__ == '__main__':
    unittest.main()
