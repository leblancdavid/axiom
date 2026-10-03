"""Prospective collection conjunction pressure on independent instrument records."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic.generative_r5_13 import canonical, generate, render, sha, typed, UnsupportedLowering
from benchmark.semantic.generative_evidence_r5_13 import challenge, conforms, observe


def ref(*parts):
    return {'ref': list(parts)}


def literal(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def instrument(fields=('calibration', 'cabinet', 'custodian')):
    row = {'serial': 'string', 'model': 'string', 'remarks': 'string',
           **{name: {'optional': 'string'} for name in ('calibration', 'cabinet', 'custodian')}}
    defaults = [{'default_missing': {'collection': 'instruments', 'identity': 'serial',
                                     'field': field, 'value': literal('assigned-' + field)}}
                for field in fields]
    return {'id': 'instrument.inventory.evolution', 'version': '1',
            'input': {'record': {'note': 'string'}},
            'state': {'record': {'edition': 'string', 'instruments': {'sequence': {'record': row}},
                                 'facility': 'string'}},
            'branches': [
                {'tag': 'evolved', 'when': {'equals': [ref('pre', 'edition'), literal('old')]},
                 'value_type': {'record': {'migrated': 'integer', 'receipt': 'string'}},
                 'value': {'record': {'migrated': {'cardinality': ref('pre', 'instruments')},
                                      'receipt': {'trim': ref('input', 'note')}}},
                 'transition': {'relations': [*defaults,
                     {'post_equals': {'field': 'edition', 'value': literal('new')}}]}},
                {'tag': 'current', 'when': None, 'value': literal('already current'),
                 'transition': {'preserve': True}}]}


ROWS = [
    {'serial': 'i1', 'model': 'scope', 'remarks': 'fragile'},
    {'serial': 'i2', 'model': 'meter', 'remarks': 'boxed', 'calibration': 'certified'},
    {'serial': 'i3', 'model': 'lens', 'remarks': 'loaned', 'cabinet': 'east'},
    {'serial': 'i4', 'model': 'sensor', 'remarks': 'spare', 'calibration': 'recent',
     'cabinet': 'west', 'custodian': 'lab'}]


class RelationComposition(unittest.TestCase):
    def case(self, contract, rows=ROWS, fault=None, edition='old'):
        pre = {'edition': edition, 'instruments': copy.deepcopy(rows), 'facility': 'annex'}
        inp = {'note': '  inventoried  '}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            (root / 'state.json').write_bytes(canonical(pre))
            if fault:
                target = root / 'operation.py'
                source = target.read_bytes()
                self.assertIn(fault[0], source)
                target.write_bytes(source.replace(*fault, 1))
                manifest = json.loads((root / 'provenance.json').read_bytes())
                manifest['artifact'] = sha(target.read_bytes())
                manifest['generation'] = sha(canonical([
                    manifest['contract'], manifest['artifact'], manifest['runtime']]))
                (root / 'provenance.json').write_bytes(canonical(manifest))
            event, public, before, after = observe(root, inp)
            return json.loads(after), json.loads(public['stdout']), challenge(
                contract, root, event, public, before, after), pre, inp

    def test_n_way_order_and_joint_state(self):
        for n in (1, 2, 3):
            contract = instrument(('calibration', 'cabinet', 'custodian')[:n])
            post, outcome, verdict, pre, inp = self.case(contract)
            self.assertEqual(outcome, {'kind': 'evolved', 'value':
                {'migrated': 4, 'receipt': 'inventoried'}})
            self.assertEqual(post['facility'], 'annex')
            self.assertEqual(post['edition'], 'new')
            for old, new in zip(ROWS, post['instruments']):
                self.assertEqual(new, {**old, **{field: 'assigned-' + field
                    for field in ('calibration', 'cabinet', 'custodian')[:n] if field not in old}})
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
            self.assertTrue(conforms(contract, inp, pre, outcome,
                {**post, 'instruments': list(reversed(post['instruments']))}, False, True))
            reversed_contract = instrument(tuple(reversed(('calibration', 'cabinet', 'custodian')[:n])))
            self.assertEqual(self.case(reversed_contract)[0:2], (post, outcome))
            self.assertEqual(render(contract), render(reversed_contract))

    def test_semantic_mutation_and_version_boundaries(self):
        contract = instrument(('calibration', 'cabinet'))
        branch = contract['branches'][0]
        branch['transition']['relations'].insert(1, instrument(('custodian',))['branches'][0]['transition']['relations'][0])
        branch['transition']['relations'][0]['default_missing']['value'] = literal('recalibrate')
        post, outcome, verdict, _, _ = self.case(contract, rows=ROWS[:2])
        self.assertEqual(outcome['value']['migrated'], 2)  # records, not field writes
        self.assertEqual(post['instruments'][0]['calibration'], 'recalibrate')
        self.assertEqual(post['instruments'][0]['custodian'], 'assigned-custodian')
        self.assertTrue(verdict['conformant'])
        removed = instrument(('cabinet',))
        post, _, verdict, _, _ = self.case(removed, rows=ROWS[:1])
        self.assertNotIn('calibration', post['instruments'][0])
        self.assertTrue(verdict['conformant'])
        post, outcome, verdict, pre, _ = self.case(contract, edition='new')
        self.assertEqual(post, pre)
        self.assertEqual(outcome['kind'], 'current')
        self.assertTrue(verdict['conformant'])
        self.assertTrue(self.case(contract, rows=[])[2]['conformant'])

    def test_conflict_redundancy_and_unsupported_structure(self):
        contract = instrument(('calibration',))
        relations = contract['branches'][0]['transition']['relations']
        duplicate = copy.deepcopy(relations[0])
        relations.insert(1, duplicate)
        self.assertEqual(self.case(contract)[2]['conformant'], True)
        self.assertEqual(render(contract), render(instrument(('calibration',))))
        relations[1]['default_missing']['value'] = literal('different')
        for pair in (relations[:2], list(reversed(relations[:2]))):
            mutated = instrument(())
            mutated['branches'][0]['transition']['relations'][:0] = copy.deepcopy(pair)
            with self.assertRaisesRegex(ValueError, 'CONFLICTING_RELATIONS'):
                typed(mutated)
        unsupported = instrument(('calibration',))
        unsupported['branches'][0]['transition']['relations'].insert(1, {'exact_frame': {
            'collection': 'instruments', 'identity': 'serial', 'record': {'record': {
                'serial': literal('fresh'), 'model': literal('scope'),
                'remarks': literal('new'),
                'calibration': literal('checked', {'optional': 'string'}),
                'cabinet': literal('bay', {'optional': 'string'}),
                'custodian': literal('crew', {'optional': 'string'})}}}})
        with self.assertRaises(UnsupportedLowering):
            typed(unsupported)
        dependent = instrument(('calibration',))
        dependent['branches'][0]['transition']['relations'].insert(1, {'default_missing': {
            'collection': 'instruments', 'identity': 'serial', 'field': 'calibration',
            'value': ref('pre', 'facility')}})
        with self.assertRaises(UnsupportedLowering):
            typed(dependent)

    def test_faithful_fault_violates_conjunction(self):
        contract = instrument()
        source = render(contract)
        old = b"'cabinet': 'assigned-cabinet'"
        # Remove only the second relation's assignment in disposable output.
        self.assertIn(old, source)
        post, outcome, verdict, pre, inp = self.case(contract, fault=(old, b"'cabinet': 'incorrect'"))
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, False))
        self.assertEqual(post['instruments'][0]['calibration'], 'assigned-calibration')
        self.assertEqual(post['instruments'][0]['custodian'], 'assigned-custodian')
        self.assertFalse(conforms(contract, inp, pre, outcome, post, False, True))


if __name__ == '__main__':
    unittest.main()
