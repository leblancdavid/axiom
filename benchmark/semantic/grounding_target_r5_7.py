"""Template for the disposable R5.7 Python target. Replacements are compiler-owned."""

import json
from pathlib import Path
import sys

OPERATION = __OPERATION__
BOUNDARY = __BOUNDARY__
PERSISTENCE = __PERSISTENCE__
PROVENANCE = __PROVENANCE__
FAULT = __FAULT__


def read_durable(path):
    return json.loads(path.read_bytes())


def commit(path, rows):
    # This single-resource prototype has no concurrency or crash-safe fsync claim.
    path.write_bytes(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode())


def invoke(rows, path, invocation):
    pre = read_durable(path)
    attempted = False
    if all('sealed' in row for row in pre):
        classification = 'error'
        if FAULT == 'wrong_failure_kind':
            classification = 'success'
        result = pre
        if FAULT == 'failure_write':
            attempted = True
            commit(path, [{**row, 'sealed': False} for row in pre])
    else:
        classification = 'success'
        result = [{**row, 'sealed': True} for row in pre]
        written = result
        if FAULT == 'wrong_state':
            written = [{**row, 'label': 'corrupted'} for row in result]
        attempted = True
        commit(path, written)
        if FAULT == 'wrong_result':
            result = [{**row, 'label': 'corrupted'} for row in result]
    post = read_durable(path)  # committed readback, not the intended write buffer
    record = {'source': 'execution', 'boundary': BOUNDARY, 'invocation': invocation,
            'sequence': 0, 'operation': 'wrong_op' if FAULT == 'wrong_identity' else OPERATION,
            'provenance': PROVENANCE, 'persistence': PERSISTENCE,
            'classification': classification, 'attempted_write': attempted,
            'facts': {'input': ([{**row, 'label': 'fabricated'} for row in rows]
                                if FAULT == 'false_input' else rows),
                      'pre': pre, 'outcome': result,
                      'post': ([{**row, 'label': 'fabricated'} for row in post]
                               if FAULT == 'false_post' else post)}}
    return record, classification, result


if __name__ == '__main__':
    state, trace, invocation, payload = sys.argv[1:]
    rows = json.loads(payload)
    record, classification, result = invoke(rows, Path(state), invocation)
    Path(trace).write_text(json.dumps(record, sort_keys=True), encoding='utf-8')
    print(json.dumps({'classification': classification, 'result': result}, sort_keys=True))
