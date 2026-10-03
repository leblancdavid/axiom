"""Independent specimen/registry contracts; no task application fixtures."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic.generative_r5_13 import canonical, generate, sha, typed, UnsupportedLowering
from benchmark.semantic.generative_evidence_r5_13 import challenge, conforms, observe


def ref(*parts):
    return {'ref': list(parts)}


def literal(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def specimen():
    row = {'code': 'string', 'label': 'string', 'origin': 'string', 'notes': 'string'}
    record = {'record': {k: ref('input', k) for k in row}}
    return {'id': 'specimen.registry', 'version': '1',
            'input': {'record': row}, 'state': {'sequence': {'record': row}},
            'branches': [
                {'tag': 'registered', 'when': {'equals': [
                    {'cardinality': {'select': {'source': ref('pre'), 'where':
                        {'equals': [ref('item', 'code'), ref('input', 'code')]}}}}, literal(0, 'integer')]},
                 'value_type': {'record': row}, 'value': record,
                 'transition': {'relations': [{'exact_frame': {
                     'collection': None, 'identity': 'code', 'record': record}}]}},
                {'tag': 'duplicate', 'when': None, 'value': literal('already registered'),
                 'transition': {'preserve': True}}]}


def registry():
    row = {'seal': 'string', 'title': 'string', 'category': 'string',
           'aisle': {'optional': 'string'}}
    return {'id': 'archive.registry.evolution', 'version': '1',
            'input': {'record': {'request': 'string'}},
            'state': {'record': {'format': 'string', 'entries': {'sequence': {'record': row}},
                                 'owner': 'string'}},
            'branches': [
                {'tag': 'evolved', 'when': {'equals': [ref('pre', 'format'), literal('V1')]},
                 'value_type': {'record': {'migrated': 'integer'}},
                 'value': {'record': {'migrated': {'cardinality': ref('pre', 'entries')}}},
                 'transition': {'relations': [
                     {'default_missing': {'collection': 'entries', 'identity': 'seal',
                                          'field': 'aisle', 'value': literal('cold-storage')}},
                     {'post_equals': {'field': 'format', 'value': literal('V2')}}]}},
                {'tag': 'current', 'when': {'equals': [ref('pre', 'format'), literal('V2')]},
                 'value_type': {'record': {'migrated': 'integer'}},
                 'value': {'record': {'migrated': literal(0, 'integer')}},
                 'transition': {'preserve': True}},
                {'tag': 'unsupported', 'when': None, 'value': literal('unknown format'),
                 'transition': {'preserve': True}}]}


class FramedMigration(unittest.TestCase):
    def case(self, contract, pre, inp, corrupt=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generate(contract, root)
            (root / 'state.json').write_bytes(canonical(pre))
            if corrupt:
                target = root / 'operation.py'
                source = target.read_bytes()
                old, new = corrupt
                self.assertIn(old, source)
                target.write_bytes(source.replace(old, new, 1))
                manifest = json.loads((root / 'provenance.json').read_bytes())
                manifest['artifact'] = sha(target.read_bytes())
                manifest['generation'] = sha(canonical([
                    manifest['contract'], manifest['artifact'], manifest['runtime']]))
                (root / 'provenance.json').write_bytes(canonical(manifest))
            event, public, before, after = observe(root, inp)
            return (json.loads(public['stdout']) if public['exit'] == 0 else None,
                    json.loads(after), challenge(contract, root, event, public, before, after),
                    before, after, public)

    def test_framed_insertion_and_semantic_mutation(self):
        contract = specimen()
        old = [{'code': 's1', 'label': 'Quartz', 'origin': 'ridge', 'notes': 'fragile'},
               {'code': 's2', 'label': 'Basalt', 'origin': 'coast', 'notes': 'keep dry'}]
        inp = {'code': 's3', 'label': 'Amber', 'origin': 'forest', 'notes': 'sealed'}
        for rows in ([], old):
            result, post, verdict, _, _, _ = self.case(contract, rows, inp)
            self.assertEqual(result, {'kind': 'registered', 'value': inp})
            self.assertEqual(post, rows + [inp])
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
            self.assertTrue(conforms(contract, inp, rows, result, [post[-1], *rows], False, True))
        result, post, verdict, before, after, _ = self.case(contract, old, {**inp, 'code': 's1'})
        self.assertEqual(result['kind'], 'duplicate')
        self.assertEqual(before, after)
        self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        changed = copy.deepcopy(contract)
        changed['branches'][0]['transition']['relations'][0]['exact_frame']['record']['record']['origin'] = ref('input', 'notes')
        result, post, verdict, _, _, _ = self.case(changed, old, inp)
        self.assertEqual(post[-1]['origin'], 'sealed')
        self.assertTrue(verdict['conformant'])  # outcome and stored row have independent projections
        changed['branches'][0]['value']['record']['origin'] = ref('input', 'notes')
        self.assertTrue(self.case(changed, old, inp)[2]['conformant'])

    def test_insertion_composition_and_faults(self):
        contract = specimen()
        # Existing #13 trim composes inside the full-record frame and outcome.
        for place in ('value', 'transition'):
            record = (contract['branches'][0]['value'] if place == 'value' else
                      contract['branches'][0]['transition']['relations'][0]['exact_frame']['record'])
            record['record']['label'] = {'trim': ref('input', 'label')}
        inp = {'code': 's3', 'label': ' Amber ', 'origin': 'forest', 'notes': 'sealed'}
        old = [{'code': 's1', 'label': 'Quartz', 'origin': 'ridge', 'notes': 'fragile'}]
        result, post, verdict, _, _, _ = self.case(contract, old, inp)
        self.assertEqual(result['value']['label'], 'Amber')
        self.assertEqual(post[-1]['label'], 'Amber')
        self.assertTrue(verdict['conformant'])
        # Disposable compiler-output faults, with a recalculated provenance
        # manifest: independently observed output and storage remain truthful.
        for replacement in (
            (b'[*post, _new]', b'[*post[1:], _new]'),  # deletion
            (b'[*post, _new]', b'[*post[:0], _new, *post[1:]]'),  # replacement
            (b'[*post, _new]', b'[*post, _new, dict(_new, code="extra")]'),
            (b'[*post, _new]', b'[*post, dict(_new, origin="wrong")]')):
            _, _, verdict, _, _, _ = self.case(contract, old, inp, replacement)
            self.assertTrue(verdict['grounded'], (replacement, verdict))
            self.assertFalse(verdict['conformant'], (replacement, verdict))
        unsupported = copy.deepcopy(contract)
        unsupported['branches'][0]['transition']['relations'].append(
            {'default_missing': {'collection': None, 'identity': 'code',
                                 'field': 'notes', 'value': literal('x')}})
        with self.assertRaises(UnsupportedLowering):
            typed(unsupported)

    def test_durable_migration_applicability_cardinality_mutation_and_faults(self):
        contract = registry()
        rows = [{'seal': 'a', 'title': 'Folio', 'category': 'rare'},
                {'seal': 'b', 'title': 'Map', 'category': 'reference', 'aisle': 'north'}]
        for subset in ([], rows[:1], rows):
            pre = {'format': 'V1', 'entries': subset, 'owner': 'public archive'}
            result, post, verdict, _, _, _ = self.case(contract, pre, {'request': 'evolve'})
            self.assertEqual(result, {'kind': 'evolved', 'value': {'migrated': len(subset)}})
            self.assertEqual(post, {**pre, 'format': 'V2', 'entries': [
                {**r, 'aisle': r.get('aisle', 'cold-storage')} for r in subset]})
            self.assertEqual((verdict['grounded'], verdict['conformant']), (True, True))
        for version, kind in (('V2', 'current'), ('V0', 'unsupported')):
            pre = {'format': version, 'entries': rows, 'owner': 'public archive'}
            result, post, verdict, before, after, _ = self.case(contract, pre, {'request': 'evolve'})
            self.assertEqual(result['kind'], kind)
            self.assertEqual(post, pre)
            self.assertEqual(before, after)
            self.assertTrue(verdict['conformant'])
        mutation = copy.deepcopy(contract)
        mutation['branches'][0]['transition']['relations'][0]['default_missing']['value'] = literal('vault')
        result, post, verdict, _, _, _ = self.case(mutation, {'format': 'V1', 'entries': rows,
            'owner': 'public archive'}, {'request': 'evolve'})
        self.assertEqual(post['entries'][0]['aisle'], 'vault')
        self.assertEqual(post['entries'][1]['aisle'], 'north')
        self.assertTrue(verdict['conformant'])
        self.assertTrue(conforms(contract, {'request': 'evolve'},
            {'format': 'V1', 'entries': rows, 'owner': 'public archive'},
            {'kind': 'evolved', 'value': {'migrated': 2}},
            {'format': 'V2', 'entries': [post['entries'][1],
                                      {**rows[0], 'aisle': 'cold-storage'}],
             'owner': 'public archive'}, False, True))
        pre = {'format': 'V1', 'entries': rows, 'owner': 'public archive'}
        for old, new in ((b"'cold-storage'", b"'wrong-default'"),
                         (b"'V2'", b"'V0'"),
                         (b"len(pre['entries'])", b"0"),
                         (b"for item in post['entries']]", b"for item in post['entries'][1:]]"),
                         (b"post = {**post, 'format': 'V2'}", b"post = {**post, 'format': 'V2', 'owner': 'someone else'}"),
                         (b"else item for item in post['entries']]", b"else {**item, 'category': 'changed'} for item in post['entries']]")):
            _, _, verdict, _, _, _ = self.case(contract, pre, {'request': 'evolve'}, (old, new))
            self.assertTrue(verdict['grounded'], (old, new, verdict))
            self.assertFalse(verdict['conformant'], (old, new, verdict))

    def test_migration_composes_with_typed_normalized_outcome(self):
        contract = registry()
        branch = contract['branches'][0]
        branch['value_type']['record']['receipt'] = 'string'
        branch['value']['record']['receipt'] = {'trim': ref('input', 'request')}
        pre = {'format': 'V1', 'entries': [{'seal': 'a', 'title': 'Map',
               'category': 'reference'}], 'owner': 'public archive'}
        result, post, verdict, _, _, _ = self.case(contract, pre, {'request': '  upgrade  '})
        self.assertEqual(result['value'], {'migrated': 1, 'receipt': 'upgrade'})
        self.assertEqual(post['format'], 'V2')
        self.assertTrue(verdict['conformant'])


if __name__ == '__main__':
    unittest.main()
