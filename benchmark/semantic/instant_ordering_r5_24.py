"""R5.24 target-independent chronological ordering prototype (not a generator).

R5.23's pinned compiler remains unchanged. This module establishes that the
existing UTC-instant domain admits a checked chronological key and exposes the
gap between a semantic relation and the locked generative #45 pipeline.
"""

from benchmark.semantic.capability_boundary_r5_22 import parse_instant
from benchmark.semantic.typed_lowering_r5_12 import _type


KEY_TYPES = ('string', 'integer', 'instant')


def plan(element, keys):
    """Type-check an ordered sequence of required record-field projections."""
    if (not isinstance(element, dict) or set(element) != {'record'} or
            not isinstance(keys, list) or not keys):
        raise ValueError('invalid ordering')
    fields = element['record']
    result = []
    for key in keys:
        if type(key) is not str or key not in fields or fields[key] not in KEY_TYPES:
            raise ValueError('non-orderable key')
        result.append((key, fields[key]))
    return tuple(result)


def rank(row, keys):
    return tuple(parse_instant(row[name]) if kind == 'instant' else row[name]
                 for name, kind in keys)


def evaluate(rows, element, keys):
    """Interpret the relation for a finite typed collection, never stringify time."""
    checked = plan(element, keys)
    if not _type(rows, {'sequence': element}):
        raise ValueError('ordering needs typed sequence')
    return sorted(rows, key=lambda row: rank(row, checked))
