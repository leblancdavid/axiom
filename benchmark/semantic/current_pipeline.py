"""Current general checked-plan entry point for non-task semantic applications.

The R5.23 locked modules are historical. R5.27 analysis and the R5.28 checked
emitter/verifier are implementation components of this single entry point.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import refined_evidence_r5_28 as evidence
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic.capability_boundary_r5_22 import CAPS_ENV, validate_logged


def checked(application):
    if (not isinstance(application, dict) or set(application) != {'id', 'state', 'operations'} or
            type(application['id']) is not str or not application['id'] or
            not isinstance(application['operations'], dict) or not application['operations']):
        raise ValueError('application requires identity, state and operations')
    plans = {}
    for name, contract in application['operations'].items():
        if type(name) is not str or not name or contract['state'] != application['state']:
            raise ValueError('operation state or identity mismatch')
        plans[name] = types.checked_plan(contract)
    return plans


def generate(application, directory):
    plans = checked(application)
    root = Path(directory)
    runtime = emitter.RUNTIME.read_bytes()
    lines = ['# Generated from checked semantic application; do not edit.',
             'from refined_runtime_r5_28 import instant_key, instant_lt, project, run_application, sole', '']
    units = [emitter.generated_unit(contract, plans[name], f'execute_{index}')
             for index, (name, contract) in enumerate(application['operations'].items())]
    for unit in units:
        lines.extend(unit.declaration)
        lines.append('')
    lines.append('OPERATIONS = {')
    for index, (name, unit) in enumerate(zip(application['operations'], units)):
        lines.append(f'    {name!r}: (execute_{index}, {unit.input_shape!r}, '
                     f'{unit.outcome_shapes!r}),')
    lines.extend(['}', '', 'if __name__ == "__main__":',
                  f'    run_application(OPERATIONS, {application["state"]!r})', ''])
    artifact = '\n'.join(lines).encode()
    identity = emitter.sha(emitter.canonical(application))
    manifest = {'application': identity, 'id': application['id'], 'artifact': emitter.sha(artifact),
                 'runtime': emitter.sha(runtime)}
    manifest['units'] = {name: unit.contract_digest for name, unit in zip(application['operations'], units)}
    manifest['generation'] = emitter.sha(emitter.canonical(manifest))
    (root / 'operation.py').write_bytes(artifact)
    (root / emitter.RUNTIME.name).write_bytes(runtime)
    (root / 'provenance.json').write_bytes(emitter.canonical(manifest))
    return manifest


def observe(directory, operation, inp, caps=None):
    root = Path(directory)
    state, trace = root / 'state.json', root / 'trace.json'
    before = state.read_bytes()
    invocation = uuid.uuid4().hex
    manifest = json.loads((root / 'provenance.json').read_bytes())
    env = {**os.environ, CAPS_ENV: caps} if caps is not None else os.environ
    completed = subprocess.run([sys.executable, str(root / 'operation.py'), operation,
                                str(state), str(trace), invocation, emitter.canonical(inp).decode(),
                                manifest['generation']], capture_output=True, text=True, env=env)
    after = state.read_bytes()
    public = {'operation': operation, 'input': inp, 'invocation': invocation,
              'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode}
    return json.loads(trace.read_bytes()) if completed.returncode == 0 else None, public, before, after


def challenge(application, directory, event, public, before, after):
    root = Path(directory)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    expected = {'application': emitter.sha(emitter.canonical(application)), 'id': application['id'],
                 'artifact': emitter.sha((root / 'operation.py').read_bytes()),
                 'runtime': emitter.sha((root / emitter.RUNTIME.name).read_bytes()),
                 'units': {name: emitter.sha(emitter.canonical(contract))
                           for name, contract in application['operations'].items()}}
    integrity = (all(manifest.get(k) == v for k, v in expected.items()) and
                 expected['runtime'] == emitter.sha(emitter.RUNTIME.read_bytes()) and
                 manifest.get('generation') == emitter.sha(emitter.canonical(expected)))
    result = {'provenance_valid': integrity, 'grounded': False, 'conformant': None}
    if not integrity:
        return result
    try:
        outcome = json.loads(public['stdout'])
        grounded = (public['operation'] in application['operations'] and public['exit'] == 0 and
                    public['stderr'] == '' and event['operation'] == public['operation'] and
                    event['generation'] == manifest['generation'] and
                    event['invocation'] == public['invocation'] and event['input'] == public['input'] and
                    event['pre'] == json.loads(before) and event['post'] == json.loads(after) and
                    event['outcome'] == outcome and type(event['attempted_write']) is bool and
                    (event['attempted_write'] or before == after) and
                    validate_logged(event['externals']))
    except (TypeError, KeyError, ValueError):
        grounded = False
    if grounded:
        result['grounded'] = True
        result['conformant'] = evidence.conforms(application['operations'][public['operation']],
                                                 public['input'], json.loads(before), outcome,
                                                 json.loads(after), before == after,
                                                 event['attempted_write'], event['externals'],
                                                 plan=types.checked_plan(application['operations'][public['operation']]))
    return result
