"""Prospective B01 black-box capture. External observations are not R5.7 traces."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'benchmark/results/phase5b/snapshot-axiom-B01.tar'
CHECKPOINT = ROOT / 'benchmark/results/phase5b/checkpoint-axiom-B01.json'
MEMBER = 'generated/task_manager.py'
STORE = 'tasks.json'
# Backend-specific metadata: not part of any semantic operation contract.
BOUNDARIES = {
    'create': ('--title', '--description', '--priority', '--due-date'),
    'list': (), 'list-high': (), 'complete': ('--id',),
    'migrate': (),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def deployed_bytes():
    """Verify snapshot member against its recorded checkpoint before executing it."""
    checkpoint = json.loads(CHECKPOINT.read_text(encoding='utf-8'))
    with tarfile.open(SNAPSHOT) as archive:
        raw = archive.extractfile(MEMBER).read()
    if checkpoint['files'][MEMBER] != sha(raw):
        raise ValueError('snapshot artifact drift')
    return raw


def validate_binding(operation, arguments):
    if operation not in BOUNDARIES or not isinstance(arguments, dict):
        raise ValueError('unknown operation or arguments')
    if not all(k in BOUNDARIES[operation] and isinstance(v, str)
               for k, v in arguments.items()):
        raise ValueError('invalid public argument binding')
    if operation == 'create' and not {'--title', '--description'} <= arguments.keys():
        raise ValueError('incomplete create binding')
    if operation == 'complete' and set(arguments) != {'--id'}:
        raise ValueError('incomplete complete binding')
    return operation, arguments


def capture(app, cwd, operation, arguments=None):
    """Capture public envelope and raw durable endpoints without reading an event."""
    arguments = {} if arguments is None else arguments
    validate_binding(operation, arguments)
    app, cwd = Path(app), Path(cwd)
    path = cwd / STORE
    before = path.read_bytes() if path.exists() else None
    argv = [sys.executable, str(app), operation]
    for key in BOUNDARIES[operation]:
        if key in arguments:
            argv.extend((key, arguments[key]))
    completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                               check=False, timeout=30)
    after = path.read_bytes() if path.exists() else None
    return {'operation': operation, 'arguments': arguments.copy(), 'argv': argv[2:],
            'exit': completed.returncode, 'stdout': completed.stdout,
            'stderr': completed.stderr,
            'before_sha256': None if before is None else sha(before),
            'after_sha256': None if after is None else sha(after),
            'before': None if before is None else json.loads(before),
            'after': None if after is None else json.loads(after),
            'internal_event': None}


def run_selected():
    """Selected B01-root calls on the pinned historical Lykoi B01 executable."""
    with tempfile.TemporaryDirectory() as temp:
        cwd = Path(temp)
        app = cwd / 'task_manager.py'
        app.write_bytes(deployed_bytes())
        events = []
        def call(op, args=None):
            event = capture(app, cwd, op, args)
            events.append(event)
            if event['exit'] != 0:
                raise ValueError(f'unexpected public failure: {event["stderr"]}')
            return json.loads(event['stdout'])
        normal = call('create', {'--title': 'Default', '--description': 'x'})
        high = call('create', {'--title': 'High', '--description': 'x', '--priority': 'HIGH'})
        critical = call('create', {'--title': 'Critical', '--description': 'x', '--priority': 'CRITICAL'})
        first_high = call('list-high')
        all_rows = call('list')
        completed = call('complete', {'--id': critical['id']})
        second_high = call('list-high')
        # Public-only diagnostic; a passing check is NOT a grounded #45 verdict.
        observed = (normal['priority'] == 'NORMAL' and high['priority'] == 'HIGH' and
                    critical['priority'] == 'CRITICAL' and first_high == second_high == [high] and
                    all_rows == sorted((normal, high, critical),
                                       key=lambda row: (row['created_at'], row['id'])) and
                    completed == {**critical, 'status': 'completed'})
        return {'artifact_sha256': sha(app.read_bytes()), 'calls': len(events),
                'public_root_observation': observed,
                'independent_public_and_durable_endpoints': all(
                    e['exit'] == 0 and e['stderr'] == '' and e['after'] is not None
                    for e in events),
                'grounding': 'GROUNDING_FAILURE', 'contract_conformant': None,
                'reason': 'no compiler-owned B01 operation/persistence event to challenge'}
