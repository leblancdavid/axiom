"""Prospective R5.28 runtime fork for checked-plan chronological key emission.

The capability boundary supplies typed external values (fresh identity, UTC
clock) once per invocation, records the actual supplied value for independent
grounding, and rejects an unknown capability or a value violating its declared
type.  ``sole``/``project``/``instant_lt`` are target-neutral collection and
instant helpers emitted by the general lowerer; none inspects an application
field name or operation.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid

CAPABILITY_TYPES = {'fresh_unique_id': 'string', 'utc_clock': 'instant'}
CAPS_ENV = 'LYKOI_R5_22_CAPS'


def is_instant(value):
    if type(value) is not str or not value.endswith('Z'):
        return False
    try:
        instant = datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError:
        return False
    return instant.tzinfo == timezone.utc


def _typed(value, kind):
    if kind == 'string':
        return type(value) is str and bool(value.strip())
    if kind == 'integer':
        return type(value) is int
    if kind == 'instant':
        return is_instant(value)
    return False


def sole(items):
    if not isinstance(items, list) or len(items) != 1:
        raise ValueError('sole needs exactly one selected element')
    return items[0]


def project(row, fields):
    return {field: row[field] for field in fields}


def instant_lt(left, right):
    if not (is_instant(left) and is_instant(right)):
        raise ValueError('before needs typed UTC instants')
    return (datetime.fromisoformat(left[:-1] + '+00:00') <
            datetime.fromisoformat(right[:-1] + '+00:00'))


def instant_key(value):
    if not is_instant(value):
        raise ValueError('ordering needs typed UTC instant')
    return datetime.fromisoformat(value[:-1] + '+00:00')


class Capabilities:
    """One resolution per named capability, recording the actual value used."""

    def __init__(self, descriptor, shapes=None):
        try:
            config = json.loads(descriptor) if descriptor else {'mode': 'real'}
        except ValueError:
            config = {'mode': 'real'}
        self.mode = config.get('mode', 'real')
        self.fixed = config.get('values', {}) if self.mode == 'controlled' else {}
        self.logged = {}
        self.shapes = CAPABILITY_TYPES if shapes is None else shapes

    def _supply(self, capability):
        if capability not in self.shapes:
            raise ValueError('unknown capability: ' + str(capability))
        if self.mode == 'controlled':
            if capability not in self.fixed:
                raise ValueError('controlled provider missing capability: ' + str(capability))
            value = self.fixed[capability]
        elif capability == 'fresh_unique_id':
            value = uuid.uuid4().hex
        elif capability == 'utc_clock':
            value = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        else:
            raise ValueError('no real provider for capability: ' + str(capability))
        if not _typed(value, self.shapes[capability]):
            raise ValueError('provider value violates capability type: ' + str(capability))
        return value

    def __getitem__(self, capability):
        if capability not in self.logged:
            self.logged[capability] = self._supply(capability)
        return self.logged[capability]


def valid(value, shape):
    if shape == 'string':
        return type(value) is str
    if shape == 'integer':
        return type(value) is int
    if shape == 'boolean':
        return type(value) is bool
    if shape == 'instant':
        return is_instant(value)
    if 'optional' in shape:
        return valid(value, shape['optional'])
    if 'nullable' in shape:
        return value is None or valid(value, shape['nullable'])
    if 'sequence' in shape:
        return type(value) is list and all(valid(row, shape['sequence']) for row in value)
    fields = shape['record']
    required = {key for key, child in fields.items() if not (
        isinstance(child, dict) and set(child) == {'optional'})}
    return type(value) is dict and required <= set(value) <= set(fields) and all(
        valid(value[key], child) for key, child in fields.items() if key in value)


def _invoke(execute, input_shape, state_shape, outcome_shapes, pre, inp, caps_descriptor, capability_shapes=None):
    caps = Capabilities(caps_descriptor, capability_shapes)
    execute.__globals__['EXTERNAL'] = caps
    outcome, post, write = execute(inp, pre)
    if (type(outcome) is not dict or set(outcome) != {'kind', 'value'} or
            type(outcome['kind']) is not str or
            not valid(outcome['value'], (outcome_shapes or {}).get(outcome['kind'], 'string'))):
        raise ValueError('invalid typed outcome')
    if not valid(post, state_shape):
        raise ValueError('invalid typed transition')
    return outcome, post, write, caps.logged


def run(execute, input_shape, state_shape, outcome_shapes=None, capability_shapes=None, post_shape=None, applicable=None):
    state, trace, invocation, payload, generation = sys.argv[1:6]
    state = Path(state)
    pre = json.loads(state.read_bytes())
    inp = json.loads(payload)
    if not valid(inp, input_shape) or not valid(pre, state_shape):
        raise ValueError('invalid typed operation values')
    if applicable is not None and not applicable(inp, pre):
        raise ValueError('operation unavailable for declared pre-state/version')
    outcome, post, write, externals = _invoke(execute, input_shape, post_shape or state_shape,
                                               outcome_shapes, pre, inp,
                                                os.environ.get(CAPS_ENV, ''), capability_shapes)
    if write:
        state.write_text(json.dumps(post, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    event = {'invocation': invocation, 'generation': generation, 'input': inp,
             'pre': pre, 'post': post, 'outcome': outcome, 'attempted_write': write,
             'externals': externals}
    Path(trace).write_text(json.dumps(event, sort_keys=True), encoding='utf-8')
    print(json.dumps(outcome, sort_keys=True))


def run_application(operations, state_shape):
    """Dispatch checked operations through the same durable boundary as run."""
    operation = sys.argv[1]
    if operation not in operations:
        raise ValueError('unknown operation')
    descriptor = operations[operation]
    execute, input_shape, outcome_shapes, capability_shapes = descriptor[:4]
    pre_shape, post_shape, applicable = descriptor[4:] if len(descriptor) == 7 else (state_shape, state_shape, None)
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    run(execute, input_shape, pre_shape, outcome_shapes, capability_shapes, post_shape, applicable)
    trace = Path(sys.argv[2])
    event = json.loads(trace.read_bytes())
    event['operation'] = operation
    trace.write_text(json.dumps(event, sort_keys=True), encoding='utf-8')


def _flag_type(shape):
    inner = shape['optional'] if isinstance(shape, dict) and set(shape) == {'optional'} else shape
    if inner == 'integer':
        return int
    if inner in ('string', 'instant'):
        return str
    return None


def run_cli(execute, input_shape, state_shape, outcome_shapes=None, capability_shapes=None):
    """Generic public CLI adapter derived from checked input-shape binding metadata.

    One positional boundary is the durable file; the operation's public inputs
    are named flags built from the declared input record, never a hand-authored
    per-application parser.  Optional/nullable record fields map to optional
    flags; the presence decision itself belongs to the generated operation.
    """
    fields = input_shape['record']
    parser = argparse.ArgumentParser(prog='generated-operation')
    parser.add_argument('--state', required=True)
    parser.add_argument('--trace', required=True)
    parser.add_argument('--invocation', required=True)
    parser.add_argument('--generation', required=True)
    for name, shape in fields.items():
        optional = isinstance(shape, dict) and set(shape) == {'optional'}
        inner = shape['optional'] if optional else shape
        if inner in ('string', 'integer', 'instant'):
            parser.add_argument('--' + name.replace('_', '-'), type=_flag_type(shape),
                                required=not optional)
        elif inner == 'boolean':
            parser.add_argument('--' + name.replace('_', '-'), action='store_true',
                                required=False)
        elif isinstance(inner, dict) and set(inner) == {'nullable'} and inner['nullable'] in ('string', 'instant'):
            parser.add_argument('--' + name.replace('_', '-'), type=str, required=not optional)
        elif isinstance(inner, dict) and set(inner) == {'sequence'} and inner['sequence'] in ('string',):
            parser.add_argument('--' + name.replace('_', '-'), nargs='*', required=not optional)
        else:
            parser.add_argument('--' + name.replace('_', '-'), type=str, required=not optional)
    parsed = vars(parser.parse_args())
    generation = parsed.pop('generation')
    trace, invocation, state = parsed.pop('trace'), parsed.pop('invocation'), parsed.pop('state')
    state = Path(state)
    pre = json.loads(state.read_bytes())
    inp = {key: value for key, value in parsed.items() if value is not None}
    for name, shape in fields.items():
        inner = shape['optional'] if (isinstance(shape, dict) and set(shape) == {'optional'}) else shape
        if inner == 'boolean' and name not in inp:
            inp[name] = False
    if not valid(inp, input_shape) or not valid(pre, state_shape):
        raise ValueError('invalid typed operation values')
    outcome, post, write, externals = _invoke(execute, input_shape, state_shape,
                                               outcome_shapes, pre, inp,
                                                os.environ.get(CAPS_ENV, ''), capability_shapes)
    if write:
        state.write_text(json.dumps(post, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    event = {'invocation': invocation, 'generation': generation, 'input': inp,
             'pre': pre, 'post': post, 'outcome': outcome, 'attempted_write': write,
             'externals': externals}
    Path(trace).write_text(json.dumps(event, sort_keys=True), encoding='utf-8')
    print(json.dumps(outcome, sort_keys=True))
