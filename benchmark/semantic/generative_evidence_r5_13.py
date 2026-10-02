"""Independent public/file observer, R5.7-style challenge, and case verifier."""

import json
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic.generative_r5_13 import canonical, sha, typed, RUNTIME
from benchmark.semantic.typed_lowering_r5_12 import _compile, _type


def observe(directory, inp):
    root = Path(directory)
    state, trace = root / 'state.json', root / 'trace.json'
    before = state.read_bytes()
    invocation = uuid.uuid4().hex
    manifest = json.loads((root / 'provenance.json').read_bytes())
    completed = subprocess.run([sys.executable, str(root / 'operation.py'), str(state),
                                str(trace), invocation, canonical(inp).decode(),
                                manifest['generation']], capture_output=True, text=True)
    after = state.read_bytes()
    public = {'input': inp, 'invocation': invocation, 'stdout': completed.stdout,
              'stderr': completed.stderr, 'exit': completed.returncode}
    internal = json.loads(trace.read_bytes()) if trace.exists() else None
    return internal, public, before, after


def challenge(contract, directory, internal, public, before, after):
    root = Path(directory)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    expected = {'contract': sha(canonical(contract)), 'id': contract['id'],
                'version': contract['version'],
                'artifact': sha((root / 'operation.py').read_bytes()),
                'runtime': sha((root / RUNTIME.name).read_bytes())}
    integrity = (all(manifest.get(k) == v for k, v in expected.items()) and
                 expected['runtime'] == sha(RUNTIME.read_bytes()) and
                 manifest.get('generation') == sha(canonical([
                     expected['contract'], expected['artifact'], expected['runtime']])))
    verdict = {'provenance_valid': integrity, 'grounded': False, 'conformant': None}
    if not integrity:
        return verdict
    try:
        visible = json.loads(public['stdout'])
        grounded = (public['exit'] == 0 and public['stderr'] == '' and
                    internal['generation'] == manifest['generation'] and
                    internal['invocation'] == public['invocation'] and
                    internal['input'] == public['input'] and
                    internal['pre'] == json.loads(before) and
                    internal['post'] == json.loads(after) and
                    internal['outcome'] == visible and
                    type(internal['attempted_write']) is bool and
                    (internal['attempted_write'] or before == after))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        grounded = False
    if not grounded:
        return verdict
    verdict['grounded'] = True
    verdict['conformant'] = conforms(contract, public['input'], json.loads(before),
                                     visible, json.loads(after), before == after,
                                     internal['attempted_write'])
    return verdict


def conforms(contract, inp, pre, outcome, post, bytes_equal, attempted_write):
    """Interpret the originating typed contract, independently of emitted Python."""
    typed(contract)
    if not (_type(inp, contract['input']) and _type(pre, contract['state']) and
            _type(post, contract['state']) and isinstance(outcome, dict) and
             set(outcome) == {'kind', 'value'}):
        return False
    slots = {'input': contract['input'], 'pre': contract['state']}
    facts = {'input': inp, 'pre': pre}
    branch = next((b for b in contract['branches'] if b['when'] is None or
                   _compile(b['when'], slots)[1](facts)), None)
    if branch is None or not _type(outcome['value'], branch.get('value_type', 'string')) or outcome != {'kind': branch['tag'],
                                     'value': _compile(branch['value'], slots)[1](facts)}:
        return False
    transition = branch['transition']
    if transition == {'preserve': True}:
        return post == pre and bytes_equal and not attempted_write
    if 'default_missing' in transition:
        rule = transition['default_missing']
        identity, field = rule['identity'], rule['field']
        if len({row[identity] for row in pre}) != len(pre):
            return False
        value = _compile(rule['value'], slots)[1](facts)
        expected = [{**row, field: value} if field not in row else row for row in pre]
        return post == expected and attempted_write
    update = transition['replace_field']
    key = _compile(update['match'], slots)[1](facts)
    value = _compile(update['value'], slots)[1](facts)
    expected = [{**row, update['field']: value} if row[update['key']] == key else row
                for row in pre]
    return post == expected and attempted_write
