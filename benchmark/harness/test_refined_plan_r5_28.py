"""Prospective independent archive-state checks for the checked general path."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.harness.test_unified_types_r5_27 import contract, ref
from benchmark.semantic import refined_generator_r5_28 as general
from benchmark.semantic import unified_types_r5_27 as unified
from benchmark.semantic.refined_evidence_r5_28 import challenge, observe, conforms
from benchmark.semantic.capability_boundary_r5_22 import controlled_descriptor


EARLY = '2026-01-01T01:00:00Z'
LATE = '2026-01-01T02:00:00Z'
CUTOFF = '2026-01-02T00:00:00Z'
ROWS = [{'code': 'z', 'seen': LATE, 'label': 'old'},
        {'code': 'go', 'seen': EARLY, 'label': 'old'},
        {'code': 'absent', 'label': 'old'},
        {'code': 'a', 'seen': EARLY, 'label': 'old'}]
INPUT = {'target': 'go', 'cutoff': CUTOFF, 'label': 'new'}


class RefinedPlanR528(unittest.TestCase):
    def execute_case(self, model, rows=ROWS, inp=INPUT, fault=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            unified.generate(model, root, fault=fault)
            (root / 'state.json').write_bytes(general.canonical(rows))
            event, public, before, after = observe(root, inp)
            return challenge(model, root, event, public, before, after), json.loads(public['stdout']), json.loads(after)

    def test_refined_ordered_read_and_scope(self):
        for reverse in (False, True):
            model = contract(reverse=reverse)
            verdict, result, after = self.execute_case(model)
            self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True, 'conformant': True})
            self.assertEqual([r['code'] for r in result['value']], ['a', 'go', 'z'])
            self.assertEqual(after, ROWS)
        exact = copy.deepcopy(contract())
        exact['branches'][0]['value']['order']['source']['select']['where']['and'].append({
            'equals': [ref('item', 'code'), ref('input', 'target')]})
        verdict, result, _ = self.execute_case(exact)
        self.assertTrue(verdict['conformant'])
        self.assertEqual([row['code'] for row in result['value']], ['go'])
        unsafe = contract()
        unsafe['branches'][0]['value']['order']['source']['select']['where']['and'][0] = {
            'present': ref('item', 'other')}
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            unified.checked_plan(unsafe)
        with self.assertRaisesRegex(ValueError, 'optional operand'):
            conforms(unsafe, INPUT, ROWS, {'kind': 'ok', 'value': []}, ROWS, True, False)
        plan = unified.checked_plan(contract())
        plan.contract['branches'][0]['value']['order']['keys'].reverse()
        with self.assertRaisesRegex(ValueError, 'typed plan source changed'):
            plan.assert_current()

    def test_refined_write_shapes_and_mutation(self):
        for kind in ('replace', 'remove'):
            model = contract(kind)
            verdict, result, after = self.execute_case(model)
            self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True, 'conformant': True})
            self.assertEqual(result['value'], 1)
            self.assertEqual([row['code'] for row in after],
                             ['z', 'go', 'absent', 'a'] if kind == 'replace' else ['z', 'absent', 'a'])
            if kind == 'replace':
                self.assertEqual(after[1]['label'], 'new')
        altered = copy.deepcopy(contract('replace'))
        altered['branches'][0]['transition']['relations'][0]['replace_field']['value'] = {
            'literal': {'type': 'string', 'value': 'changed'}}
        verdict, _, after = self.execute_case(altered)
        self.assertTrue(verdict['conformant'])
        self.assertEqual(after[1]['label'], 'changed')

    def test_semantic_only_refinement_cutoff_order_and_remove_mutations(self):
        earlier = copy.deepcopy(contract())
        earlier['branches'][0]['value']['order']['source']['select']['where']['and'][0] = {
            'present': ref('item', 'other')}
        earlier['branches'][0]['value']['order']['source']['select']['where']['and'][1]['before'][0] = ref('item', 'other')
        # A changed refinement target needs the ordered key changed as well.
        earlier['branches'][0]['value']['order']['keys'] = ['other', 'code']
        verdict, value, _ = self.execute_case(earlier, rows=[
            {'code': 'go', 'other': EARLY, 'label': 'old'},
            {'code': 'z', 'other': LATE, 'label': 'old'}])
        self.assertTrue(verdict['conformant'])
        self.assertEqual([row['code'] for row in value['value']], ['go', 'z'])
        later_cutoff = copy.deepcopy(contract('remove'))
        later_cutoff['branches'][0]['when']['equals'][0]['cardinality']['select']['where']['and'][1]['before'][1] = {
            'literal': {'type': 'instant', 'value': EARLY}}
        verdict, value, after = self.execute_case(later_cutoff)
        self.assertTrue(verdict['conformant'])
        self.assertEqual(value['kind'], 'skip')
        self.assertEqual(after, ROWS)
        changed_predicate = copy.deepcopy(contract('remove'))
        changed_predicate['branches'][0]['when']['equals'][0]['cardinality']['select']['where']['and'][2]['equals'][1] = {
            'literal': {'type': 'string', 'value': 'a'}}
        changed_predicate['branches'][0]['transition']['relations'][0]['remove']['match'] = {
            'literal': {'type': 'string', 'value': 'a'}}
        verdict, _, after = self.execute_case(changed_predicate)
        self.assertTrue(verdict['conformant'])
        self.assertNotIn('a', [row['code'] for row in after])

    def test_external_insertion_integrated(self):
        model = contract('insert')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            unified.generate(model, root)
            (root / 'state.json').write_bytes(general.canonical([]))
            event, public, before, after = observe(root, INPUT,
                controlled_descriptor({'utc_clock': EARLY}))
            self.assertEqual(challenge(model, root, event, public, before, after),
                             {'provenance_valid': True, 'grounded': True, 'conformant': True})
            self.assertEqual(json.loads(after)[0]['seen'], EARLY)

    def test_disposable_order_and_replacement_faults(self):
        # The existing disposable emitter fault drops secondary ordering keys
        # and retains an old replacement value; observations still ground.
        for kind in ('read', 'replace'):
            verdict, _, _ = self.execute_case(contract(kind), fault=True)
            self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True,
                                       'conformant': False})

    def faulty_case(self, model, rewrite, rows=ROWS, caps=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            unified.generate(model, root)
            artifact = root / 'operation.py'
            original = artifact.read_text(encoding='utf-8')
            faulty = rewrite(original)
            self.assertNotEqual(original, faulty)
            artifact.write_bytes(faulty.encode())
            manifest_path = root / 'provenance.json'
            manifest = json.loads(manifest_path.read_bytes())
            manifest['artifact'] = general.sha(artifact.read_bytes())
            manifest['generation'] = general.sha(general.canonical([
                manifest['contract'], manifest['artifact'], manifest['runtime']]))
            manifest_path.write_bytes(general.canonical(manifest))
            (root / 'state.json').write_bytes(general.canonical(rows))
            event, public, before, after = observe(root, INPUT, caps)
            return challenge(model, root, event, public, before, after)

    def test_four_fault_matrix(self):
        absent = contract()
        selected = absent['branches'][0]['value']['order']['source']
        absent['branches'][0]['value'] = selected
        where = selected['select']['where']
        plan = unified.checked_plan(absent)
        predicate = general.expression(where, {'post': 'post', 'item': '_element_1'},
            {'input': absent['input'], 'pre': absent['state']}, plan=plan)
        # Fault A includes absent rows without evaluating their missing instant.
        a = self.faulty_case(absent, lambda code: code.replace(
            ' if ' + predicate + ']',
            " if (('seen' not in _element_1) or " + predicate + ')]'))
        b, _, _ = self.execute_case(contract(), fault=True)
        # Fault C updates another valid string column on the correct selected row.
        c = self.faulty_case(contract('replace'), lambda code: code.replace(
            "{**item, 'label': input['label']}", "{**item, 'code': input['label']}"))
        insertion = contract('insert')
        # Fault D uses the provider instant in the public result but persists another.
        d = self.faulty_case(insertion, lambda code: code.replace(
            "        _new = {'code': input['target'], 'seen': EXTERNAL['utc_clock'], 'label': input['label']}",
            "        _new = {'code': input['target'], 'seen': '2026-01-01T02:00:00Z', 'label': input['label']}"),
            rows=[], caps=controlled_descriptor({'utc_clock': EARLY}))
        for label, verdict in zip('ABCD', (a, b, c, d)):
            with self.subTest(fault=label):
                self.assertEqual(verdict, {'provenance_valid': True, 'grounded': True,
                                           'conformant': False})


if __name__ == '__main__':
    unittest.main()
