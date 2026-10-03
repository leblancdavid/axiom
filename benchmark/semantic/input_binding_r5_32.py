"""Generic raw-data decoding; consumes checked descriptors, never semantic ASTs.

Optional absence stays absent. Fallback and application validity belong to the
generated operation. Failure diagnostics deliberately contain no supplied data.
"""

import json
import re

if __package__:
    from benchmark.semantic.refined_runtime_r5_28 import valid
else:
    from refined_runtime_r5_28 import valid


CATEGORIES = ('malformed_payload', 'unknown_operation', 'unknown_argument',
              'missing_required', 'malformed_scalar', 'outside_domain')


def failure(argument, slot, expected, category):
    return {'argument': argument, 'slot': slot, 'expected': expected, 'category': category}


def decode(raw, shape):
    if shape == 'integer' and type(raw) is str and re.fullmatch(r'[+-]?[0-9]+', raw):
        try:
            raw = int(raw)
        except ValueError:
            return False, None
    if not valid(raw, shape):
        return False, None
    return True, raw


def bind(operation, payload, metadata):
    """All-or-failure binding. No invalid value escapes as a typed invocation."""
    try:
        raw = json.loads(payload)
    except (ValueError, TypeError):
        raw = None
    if type(raw) is not dict:
        return {'slots': {}, 'input': None, 'failures': [
            failure(None, None, 'argument_object', 'malformed_payload')]}
    if operation not in metadata['operations']:
        return {'slots': {}, 'input': None, 'failures': [
            failure(None, None, None, 'unknown_operation')]}
    descriptors = metadata['operations'][operation]
    inp, slots, failures = {}, {}, []
    for argument in sorted(set(raw) - set(descriptors)):
        failures.append(failure(argument, None, None, 'unknown_argument'))
    for argument, descriptor in sorted(descriptors.items()):
        slot, shape = descriptor['slot'], descriptor['type']
        if argument not in raw:
            slots[slot] = {'supplied': False, 'state': 'OMITTED'}
            if not descriptor['optional']:
                failures.append(failure(argument, slot, shape, 'missing_required'))
            continue
        ok, value = decode(raw[argument], shape)
        category = None if ok else 'malformed_scalar'
        if ok and descriptor['domain'] is not None and value not in descriptor['domain']:
            category = 'outside_domain'
        slots[slot] = {'supplied': True, 'state': 'BOUND_TYPED' if category is None else 'BINDING_FAILED'}
        if category is not None:
            failures.append(failure(argument, slot, shape, category))
        else:
            inp[slot] = value
    return {'slots': slots, 'input': None if failures else inp, 'failures': failures}


def public_failure(result, metadata):
    return {'status': 'binding_failure', 'errors': [
        {**item, 'code': metadata['error_codes'][item['category']]}
        for item in result['failures']]}
