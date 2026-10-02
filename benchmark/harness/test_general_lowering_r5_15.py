"""Prospective independent synthetic lowering; no benchmark application execution."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic.generative_r5_13 import canonical, generate, typed, UnsupportedLowering
from benchmark.semantic.generative_evidence_r5_13 import observe, challenge


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def media():
    sequence = ref('input', 'titles')
    normalized = {'stable_unique': {'sequence': {'map': {'sequence': sequence,
                                                          'transform': 'trim'}},
                                    'equality': 'case_sensitive_string'}}
    return {'id': 'media.catalogue', 'version': '1',
            'input': {'record': {'titles': {'sequence': 'string'}, 'edition': 'string'}},
            'state': {'sequence': {'record': {'edition': 'string', 'titles': {'sequence': 'string'}}}},
            'branches': [
                {'tag': 'stored', 'when': {'for_each': {'sequence': sequence, 'bind': 'entry',
                    'property': {'nonblank': {'trim': ref('entry')}}}},
                 'value_type': {'record': {'edition': 'string', 'titles': {'sequence': 'string'}}},
                 'value': {'record': {'edition': ref('input', 'edition'), 'titles': normalized}},
                 'transition': {'preserve': True}},
                {'tag': 'rejected', 'when': None, 'value': lit('empty entry'),
                 'transition': {'preserve': True}}]}


def devices():
    return {'id': 'device.service', 'version': '1',
            'input': {'record': {'serial': 'string', 'location': 'string'}},
            'state': {'sequence': {'record': {'serial': 'string', 'location': 'string', 'status': 'string'}}},
            'branches': [
                {'tag': 'updated', 'when': {'equals': [
                    {'cardinality': {'select': {'source': ref('pre'), 'where': {'equals': [
                        ref('item', 'serial'), ref('input', 'serial')]}}}}, lit(1, 'integer')]},
                 'value_type': {'record': {'serial': 'string', 'location': 'string'}},
                 'value': {'record': {'serial': ref('input', 'serial'),
                                      'location': ref('input', 'location')}},
                 'transition': {'replace_field': {'key': 'serial', 'match': ref('input', 'serial'),
                     'field': 'location', 'value': ref('input', 'location')}}},
                {'tag': 'missing', 'when': None, 'value': lit('not registered'),
                 'transition': {'preserve': True}}]}


def holdings():
    return {'id': 'library.holdings', 'version': '1',
            'input': {'record': {'edition': 'string'}},
            'state': {'sequence': {'record': {'accession': 'string', 'title': 'string',
                                              'shelf': {'optional': 'string'}}}},
            'branches': [
                {'tag': 'upgraded', 'when': {'equals': [ref('input', 'edition'), lit('old')]},
                 'value_type': 'integer', 'value': {'cardinality': ref('pre')},
                 'transition': {'default_missing': {'identity': 'accession', 'field': 'shelf',
                                                     'value': lit('reserve')}}},
                {'tag': 'unchanged', 'when': None, 'value_type': 'integer',
                 'value': lit(0, 'integer'), 'transition': {'preserve': True}}]}


class GeneralLowering(unittest.TestCase):
    def case(self, contract, pre, inp, fault=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root, fault=fault)
            (root / 'state.json').write_bytes(canonical(pre))
            event, public, before, after = observe(root, inp)
            verdict = challenge(contract, root, event, public, before, after)
            return json.loads(public['stdout']), json.loads(after), verdict, before, after

    def test_normalization_arbitrary_lengths_order_case_and_mutation(self):
        contract = media()
        for n in (0, 1, 3, 43):
            values = ['  Volume ' if i % 3 == 0 else 'volume' if i % 3 == 1 else 'Volume'
                      for i in range(n)]
            outcome, _, verdict, _, _ = self.case(contract, [], {'titles': values, 'edition': 'E'})
            self.assertEqual(outcome['value']['titles'], list(dict.fromkeys(s.strip() for s in values)))
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        rejected = self.case(contract, [], {'titles': ['a', '  '], 'edition': 'E'})
        self.assertEqual(rejected[0]['kind'], 'rejected')
        self.assertEqual(rejected[3], rejected[4])
        mutation = copy.deepcopy(contract)
        mutation['version'] = '2'
        mutation['branches'][0]['value']['record']['titles']['stable_unique']['sequence'] = ref('input', 'titles')
        original = self.case(contract, [], {'titles': [' X ', 'X'], 'edition': 'E'})[0]
        changed = self.case(mutation, [], {'titles': [' X ', 'X'], 'edition': 'E'})[0]
        self.assertEqual(original['value']['titles'], ['X'])
        self.assertEqual(changed['value']['titles'], [' X ', 'X'])
        # Semantic bind names are data, including target-language reserved words.
        renamed = copy.deepcopy(contract)
        renamed['branches'][0]['when']['for_each']['bind'] = 'class'
        renamed['branches'][0]['when']['for_each']['property'] = {'nonblank': {'trim': ref('class')}}
        self.assertEqual(self.case(renamed, [], {'titles': ['a'], 'edition': 'E'})[0]['kind'], 'stored')

    def test_record_outcome_state_and_fault(self):
        contract = devices()
        rows = [{'serial': 'A', 'location': 'west', 'status': 'active'},
                {'serial': 'B', 'location': 'north', 'status': 'idle'}]
        inp = {'serial': 'A', 'location': 'east'}
        outcome, post, verdict, _, _ = self.case(contract, rows, inp)
        self.assertEqual(outcome, {'kind': 'updated', 'value': {'serial': 'A', 'location': 'east'}})
        self.assertEqual(post[1], rows[1])
        self.assertEqual((verdict['provenance_valid'], verdict['grounded'], verdict['conformant']),
                         (True, True, True))
        self.assertEqual(self.case(contract, rows, {'serial': 'C', 'location': 'east'})[0]['kind'], 'missing')
        self.assertEqual(self.case(contract, rows, inp, fault=True)[2]['conformant'], False)
        mutation = copy.deepcopy(contract)
        mutation['version'] = '2'
        mutation['branches'][0]['value']['record']['location'] = ref('input', 'serial')
        self.assertEqual(self.case(mutation, rows, inp)[0]['value']['location'], 'A')
        # Disposable malformed target: runtime must check the payload before persistence.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            target = root / 'operation.py'
            source = target.read_bytes()
            self.assertIn(b"'location': input['location']", source)
            target.write_bytes(source.replace(b"'location': input['location']",
                                              b"'location': 7", 1))
            (root / 'state.json').write_bytes(canonical(rows))
            event, public, before, after = observe(root, inp)
            self.assertNotEqual(public['exit'], 0)
            self.assertIsNone(event)
            self.assertEqual(before, after)

    def test_default_preserves_identity_existing_fields_and_cardinality(self):
        contract = holdings()
        rows = [{'accession': 'L1', 'title': 'Atlas'},
                {'accession': 'L2', 'title': 'Manual', 'shelf': 'reference'}]
        outcome, post, verdict, _, _ = self.case(contract, rows, {'edition': 'old'})
        self.assertEqual(outcome, {'kind': 'upgraded', 'value': 2})
        self.assertEqual(post, [{**rows[0], 'shelf': 'reserve'}, rows[1]])
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        self.assertEqual(self.case(contract, [], {'edition': 'old'})[0]['value'], 0)
        unchanged = self.case(contract, rows, {'edition': 'current'})
        self.assertEqual(unchanged[0], {'kind': 'unchanged', 'value': 0})
        self.assertEqual(unchanged[3], unchanged[4])
        mutation = copy.deepcopy(contract)
        mutation['version'] = '2'
        mutation['branches'][0]['transition']['default_missing']['value'] = lit('archive')
        self.assertEqual(self.case(mutation, rows, {'edition': 'old'})[1][0]['shelf'], 'archive')
        invalid = copy.deepcopy(contract)
        invalid['branches'][0]['transition']['default_missing']['value'] = lit(7, 'integer')
        with self.assertRaisesRegex(ValueError, 'incompatible default'):
            typed(invalid)
        invalid = copy.deepcopy(contract)
        invalid['branches'][0]['transition']['default_missing']['identity'] = 'title'
        duplicate = [{'accession': 'L1', 'title': 'same'}, {'accession': 'L2', 'title': 'same'}]
        # Uniqueness is a precondition for the keyed relation; rejected before a write.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(invalid, root)
            (root / 'state.json').write_bytes(canonical(duplicate))
            event, public, before, after = observe(root, {'edition': 'old'})
            self.assertNotEqual(public['exit'], 0)
            self.assertIsNone(event)
            self.assertEqual(before, after)

    def test_reject_types_and_unimplemented_relations(self):
        contract = media()
        malformed = copy.deepcopy(contract)
        malformed['branches'][0]['value']['record']['titles'] = lit('scalar')
        with self.assertRaisesRegex(ValueError, 'payload type mismatch'):
            typed(malformed)
        malformed = copy.deepcopy(contract)
        malformed['branches'][0]['value_type']['record']['titles'] = 'integer'
        with self.assertRaisesRegex(ValueError, 'payload type mismatch'):
            typed(malformed)
        malformed = copy.deepcopy(contract)
        malformed['branches'][0]['value']['record']['titles']['stable_unique']['sequence'] = ref('input', 'edition')
        with self.assertRaisesRegex(ValueError, 'string sequence'):
            typed(malformed)
        malformed = copy.deepcopy(contract)
        malformed['branches'][0]['when'] = {'cardinality': ref('input', 'edition')}
        with self.assertRaisesRegex(ValueError, 'cardinality needs a sequence'):
            typed(malformed)
        unsupported = copy.deepcopy(contract)
        unsupported['branches'][0]['transition'] = {'insert': {'record': ref('input')}}
        with self.assertRaisesRegex(UnsupportedLowering, 'state relation'):
            typed(unsupported)
        unsupported['branches'][0]['transition'] = {'default_missing': {'field': 'location'}}
        with self.assertRaisesRegex(UnsupportedLowering, 'state relation'):
            typed(unsupported)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            (root / 'state.json').write_bytes(canonical([]))
            event, public, before, after = observe(root, {'titles': [17], 'edition': 'E'})
            self.assertNotEqual(public['exit'], 0)
            self.assertIsNone(event)
            self.assertEqual(before, after)
            (root / 'state.json').write_bytes(canonical([{'edition': 'E', 'titles': [17]}]))
            event, public, before, after = observe(root, {'titles': [], 'edition': 'E'})
            self.assertNotEqual(public['exit'], 0)
            self.assertIsNone(event)
            self.assertEqual(before, after)

    def test_unanticipated_nested_normalization_selection_and_record_result(self):
        # A structural combination absent from either first synthetic fixture.
        contract = devices()
        contract['version'] = 'novel'
        contract['input']['record']['aliases'] = {'sequence': 'string'}
        unique = {'stable_unique': {'sequence': {'map': {
            'sequence': ref('input', 'aliases'), 'transform': 'trim'}},
            'equality': 'case_sensitive_string'}}
        contract['branches'][0]['when'] = {'and': [contract['branches'][0]['when'],
            {'equals': [{'cardinality': unique}, lit(2, 'integer')]}]}
        contract['branches'][0]['value_type']['record']['aliases'] = {'sequence': 'string'}
        contract['branches'][0]['value']['record']['aliases'] = unique
        outcome, post, verdict, _, _ = self.case(contract, [
            {'serial': 'A', 'location': 'west', 'status': 'active'}],
            {'serial': 'A', 'location': 'east', 'aliases': [' one ', 'two', 'one']})
        self.assertEqual(outcome['value']['aliases'], ['one', 'two'])
        self.assertEqual(post[0]['location'], 'east')
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))

    def test_three_new_capabilities_compose_without_compiler_changes(self):
        contract = holdings()
        contract['version'] = 'composition'
        contract['input']['record']['marks'] = {'sequence': 'string'}
        normalized = {'stable_unique': {'sequence': {'map': {
            'sequence': ref('input', 'marks'), 'transform': 'trim'}},
            'equality': 'case_sensitive_string'}}
        contract['branches'][0]['when'] = {'and': [contract['branches'][0]['when'],
            {'for_each': {'sequence': ref('input', 'marks'), 'bind': 'mark',
                          'property': {'nonblank': {'trim': ref('mark')}}}}]}
        contract['branches'][0]['value_type'] = {'record': {
            'total': 'integer', 'marks': {'sequence': 'string'}}}
        contract['branches'][0]['value'] = {'record': {
            'total': {'cardinality': ref('pre')}, 'marks': normalized}}
        rows = [{'accession': 'L1', 'title': 'Atlas'}]
        inp = {'edition': 'old', 'marks': [' A ', 'B', 'A']}
        outcome, post, verdict, _, _ = self.case(contract, rows, inp)
        self.assertEqual(outcome, {'kind': 'upgraded', 'value': {'total': 1, 'marks': ['A', 'B']}})
        self.assertEqual(post[0]['shelf'], 'reserve')
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        rejected = self.case(contract, rows, {'edition': 'old', 'marks': [' ']})
        self.assertEqual(rejected[0]['kind'], 'unchanged')
        self.assertEqual(rejected[3], rejected[4])


if __name__ == '__main__':
    unittest.main()
