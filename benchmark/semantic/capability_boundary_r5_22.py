"""Typed external-value capability boundary (R5.22).

A semantic ``external`` reference identifies an existing inherited obligation:
the operation depends on a value the core semantic model does not itself supply
(a fresh identity, the UTC clock).  This module is the *checked* side of that
boundary: a small registry of typed capability sources, provider-descriptor
construction for the disposable runtime, and re-validation of the actual value
the runtime supplied.  It adds no core construct and embeds no application or
external-benchmark behavior; a generated program requests a capability by name
and receives a concrete typed value from a runtime provider.

The runtime side (``generative_runtime_r5_13``) is deliberately self-contained
and re-declares the same capability set and instant form, because the generated
program is copied into an isolated directory with only the runtime module.
"""

import json
from datetime import datetime, timezone

CAPABILITY_TYPES = {
    'fresh_unique_id': 'string',
    'utc_clock': 'instant',
}
CAPS_ENV = 'LYKOI_R5_22_CAPS'


def is_instant(value):
    if type(value) is not str or not value.endswith('Z'):
        return False
    try:
        instant = datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError:
        return False
    return instant.tzinfo == timezone.utc


def parse_instant(value):
    if not is_instant(value):
        raise ValueError('not a UTC instant')
    return datetime.fromisoformat(value[:-1] + '+00:00')


def capability_type(capability):
    if capability not in CAPABILITY_TYPES:
        raise ValueError('unknown capability: ' + str(capability))
    return CAPABILITY_TYPES[capability]


def matches(value, capability):
    """Whether a supplied value satisfies the capability's declared type."""
    kind = capability_type(capability)
    if kind == 'string':
        return type(value) is str and bool(value.strip())
    if kind == 'instant':
        return is_instant(value)
    return type(value) is int


def real_descriptor():
    return json.dumps({'mode': 'real'}, sort_keys=True)


def controlled_descriptor(values):
    if not isinstance(values, dict) or not values:
        raise ValueError('controlled capabilities need at least one value')
    for capability, value in values.items():
        if not matches(value, capability):
            raise ValueError('controlled value violates capability type: ' + str(capability))
    return json.dumps({'mode': 'controlled', 'values': dict(values)}, sort_keys=True)


def validate_logged(externals):
    """Independent re-check that every actually supplied value honors its type."""
    if not isinstance(externals, dict):
        return False
    return all(capability in CAPABILITY_TYPES and matches(value, capability)
               for capability, value in externals.items())
