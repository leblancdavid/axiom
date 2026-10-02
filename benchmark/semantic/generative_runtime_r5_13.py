"""Generic subprocess/file boundary; no application predicate or transition."""

import json
from pathlib import Path
import sys


def valid(value, shape):
    if shape == 'string':
        return type(value) is str
    if shape == 'integer':
        return type(value) is int
    if shape == 'boolean':
        return type(value) is bool
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


def run(execute, input_shape, state_shape, outcome_shapes=None):
    state, trace, invocation, payload, generation = sys.argv[1:6]
    state = Path(state)
    pre = json.loads(state.read_bytes())
    inp = json.loads(payload)
    if not valid(inp, input_shape) or not valid(pre, state_shape):
        raise ValueError('invalid typed operation values')
    outcome, post, write = execute(inp, pre)
    if (type(outcome) is not dict or set(outcome) != {'kind', 'value'} or
            type(outcome['kind']) is not str or
            not valid(outcome['value'], (outcome_shapes or {}).get(outcome['kind'], 'string'))):
        raise ValueError('invalid typed outcome')
    if not valid(post, state_shape):
        raise ValueError('invalid typed transition')
    if write:
        state.write_text(json.dumps(post, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    event = {'invocation': invocation, 'generation': generation, 'input': inp,
             'pre': pre, 'post': post, 'outcome': outcome, 'attempted_write': write}
    Path(trace).write_text(json.dumps(event, sort_keys=True), encoding='utf-8')
    print(json.dumps(outcome, sort_keys=True))
