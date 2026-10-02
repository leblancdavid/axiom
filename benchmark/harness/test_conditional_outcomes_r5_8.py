"""Small semantic fixtures for the unfrozen generalized operation contract."""

import copy
import unittest

from benchmark.semantic import contracts, grounding_r5_7
from benchmark.semantic.format import FormatError


class ConditionalOutcomeSemantics(unittest.TestCase):
    def setUp(self):
        self.contract = grounding_r5_7.contract()
        self.ready = [{'id': 'item', 'label': 'sample', 'sealed': True}]
        self.pending = [{'id': 'item', 'label': 'sample'}]

    def values(self, pre, kind, post):
        return {'input.rows': pre, 'pre.records': pre, 'result':
                {'kind': kind, 'value': post}, 'post.records': post}

    def test_conditional_error_and_success_are_one_relation(self):
        for pre, kind, post, expected in (
            (self.ready, 'error', self.ready, True),
            (self.pending, 'success', self.ready, True),
            (self.ready, 'success', self.ready, False),
            (self.pending, 'error', self.pending, False),
            (self.ready, 'error', [{**self.ready[0], 'label': 'changed'}], False),
        ):
            with self.subTest(pre=pre, kind=kind, post=post):
                self.assertIs(contracts.evaluate(self.contract, self.values(pre, kind, post)),
                              expected)

    def test_closed_outcome_and_typed_boolean_checks(self):
        for kind in ('permission_error', 1):
            with self.subTest(kind=kind), self.assertRaises(FormatError):
                contracts.evaluate(self.contract, self.values(self.ready, kind, self.ready))
        invalid = copy.deepcopy(self.contract)
        invalid['checks'].append({'equals': [{'ref': 'result.kind'},
                                              {'ref': 'post.records'}]})
        with self.assertRaises(FormatError):
            contracts.validate(invalid)
        invalid = copy.deepcopy(self.contract)
        invalid['checks'].append({'execute': 'write'})
        with self.assertRaises(FormatError):
            contracts.validate(invalid)

    def test_common_payload_is_typed_even_on_failure(self):
        invalid = self.values(self.ready, 'error', self.ready)
        invalid['result']['value'] = 'untyped'
        with self.assertRaises(FormatError):
            contracts.evaluate(self.contract, invalid)


if __name__ == '__main__':
    unittest.main()
