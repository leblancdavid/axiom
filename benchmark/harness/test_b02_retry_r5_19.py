"""Locked R5.19 lowering gate probes, never a replacement B02 implementation.

The historical R5.19 result remains recorded in its artifact: at that lock the
unchanged generator rejected `order`. R5.20 independently superseded that
generator limitation on non-task domains; the current-lowerer assertions below
are test lifecycle only. They generate nothing to disk, execute nothing, and
are not a B02 retry, candidate, acceptance, grounding or conformance result.
"""

import unittest

from benchmark.harness.test_b02_retry_r5_17 import b02_migration_contract, literal, ref
from benchmark.semantic.generative_r5_13 import render, typed


def b02_ordered_list_contract():
    # The frozen baseline requires (created_at, id) ordering even on a plain
    # list. This is a read-only projection of the complete B02 row shape.
    row = b02_migration_contract()['state']['record']['records']['sequence']['record']
    return {'id': 'b02.list', 'version': 'r5.19',
            'input': {'record': {'request': 'string'}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': row}}}},
            'branches': [
                {'tag': 'listed',
                 'when': {'equals': [ref('pre', 'schema_version'), literal(4, 'integer')]},
                 'value_type': {'sequence': {'record': row}},
                 'value': {'order': {'source': ref('pre', 'records'),
                                     'keys': ['created_at', 'id']}},
                 'transition': {'preserve': True}},
                {'tag': 'migration_required', 'when': None,
                 'value': literal('migration_required', 'string'),
                 'transition': {'preserve': True}}]}


class SecondB02RetryGate(unittest.TestCase):
    def test_overlap_and_ordering_type_and_render_on_current_lowerer(self):
        migration_slice = b02_migration_contract()
        self.assertIs(typed(migration_slice), migration_slice)
        generated_slice = render(migration_slice)
        for field in (b"'priority'", b"'due_date'", b"'tags'"):
            self.assertIn(field, generated_slice)
        # The historical slice is not the full frozen migration contract.
        ordered_list = b02_ordered_list_contract()
        self.assertIs(typed(ordered_list), ordered_list)
        # Historical R5.19 observed UNSUPPORTED_LOWERING_CAPABILITY: order here.
        # R5.20 general ordering lowering supersedes that current-lowerer
        # expectation; rendering bytes in memory is not generating, executing,
        # accepting, grounding or conforming a B02 candidate.
        self.assertIn(b"sorted(pre['records']", render(ordered_list))


if __name__ == '__main__':
    unittest.main()
