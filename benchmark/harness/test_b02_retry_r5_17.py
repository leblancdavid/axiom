"""Historical R5.17 contract probe; current assertions track the current lowerer.

The locked R5.17 rejection and conclusion remain recorded in its result artifact.
R5.18 superseded that compiler limitation; this is not a B02 candidate.
"""

import unittest

from benchmark.semantic.generative_r5_13 import typed


def ref(*path):
    return {'ref': list(path)}


def literal(value, shape):
    return {'literal': {'value': value, 'type': shape}}


def b02_migration_contract():
    # Three independently required missing-field defaults must act on the SAME
    # legacy records. Splitting them into separate operations would change B02.
    row = {'id': 'string', 'title': 'string', 'description': 'string',
           'status': 'string', 'created_at': 'string',
           'priority': {'optional': 'string'},
           'due_date': {'optional': {'nullable': 'string'}},
           'tags': {'optional': {'sequence': 'string'}}}
    relation = lambda field, value: {'default_missing': {
        'collection': 'records', 'identity': 'id', 'field': field, 'value': value}}
    transition = {'relations': [
        relation('priority', literal('NORMAL', 'string')),
        relation('due_date', literal(None, {'nullable': 'string'})),
        relation('tags', literal([], {'sequence': 'string'})),
        {'post_equals': {'field': 'schema_version', 'value': literal(4, 'integer')}}]}
    count = {'record': {'migrated': {'cardinality': ref('pre', 'records')}}}
    return {'id': 'b02.migrate', 'version': 'r5.17',
            'input': {'record': {'request': 'string'}},
            'state': {'record': {'schema_version': 'integer',
                                 'records': {'sequence': {'record': row}}}},
            'branches': [
                {'tag': 'migrated', 'when': {'equals': [ref('pre', 'schema_version'),
                                                          literal(1, 'integer')]},
                 'value_type': {'record': {'migrated': 'integer'}},
                 'value': count, 'transition': transition},
                {'tag': 'current', 'when': None,
                 'value_type': {'record': {'migrated': 'integer'}},
                 'value': {'record': {'migrated': literal(0, 'integer')}},
                 'transition': {'preserve': True}}]}


class B02RetryGate(unittest.TestCase):
    def test_historical_migration_slice_types_with_current_lowerer(self):
        contract = b02_migration_contract()
        self.assertIs(typed(contract), contract)


if __name__ == '__main__':
    unittest.main()
