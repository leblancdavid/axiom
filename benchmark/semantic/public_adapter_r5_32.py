"""Synthetic JSON-object public CLI around current_pipeline's generated program."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from input_binding_r5_32 import bind, public_failure


def main():
    operation, state, trace, binding_trace, invocation, payload, generation = sys.argv[1:8]
    root = Path(__file__).parent
    metadata = json.loads((root / 'public_binding.json').read_bytes())
    before = Path(state).read_bytes()
    result = bind(operation, payload, metadata)
    invoked = False
    if result['failures']:
        visible = public_failure(result, metadata)
        exit_code = 2
    else:
        invoked = True
        completed = subprocess.run([sys.executable, str(root / 'operation.py'), operation,
            state, trace, invocation, json.dumps(result['input']), generation],
            capture_output=True, text=True)
        if completed.returncode:
            sys.stderr.write(completed.stderr)
            return completed.returncode
        visible = {'status': 'semantic_outcome', 'outcome': json.loads(completed.stdout)}
        exit_code = 0
    after = Path(state).read_bytes()
    event = {'operation': operation, 'invocation': invocation, 'generation': generation,
             'binding': result, 'semantic_invoked': invoked, 'public': visible,
             'pre_digest': hashlib.sha256(before).hexdigest(),
             'post_digest': hashlib.sha256(after).hexdigest()}
    Path(binding_trace).write_text(json.dumps(event, sort_keys=True), encoding='utf-8')
    print(json.dumps(visible, sort_keys=True))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
