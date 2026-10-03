"""Independent public/file observer, R5.7-style challenge, and case verifier."""

import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic.generative_r5_13 import canonical, ordering_plan, sha, typed, RUNTIME
from benchmark.semantic.typed_lowering_r5_12 import _compile, _type
from benchmark.semantic.capability_boundary_r5_22 import CAPS_ENV, validate_logged


def observe(directory, inp, caps=None):
    root = Path(directory)
    state, trace = root / 'state.json', root / 'trace.json'
    before = state.read_bytes()
    invocation = uuid.uuid4().hex
    manifest = json.loads((root / 'provenance.json').read_bytes())
    env = os.environ
    if caps is not None:
        env = {**os.environ, CAPS_ENV: caps}
    completed = subprocess.run([sys.executable, str(root / 'operation.py'), str(state),
                                str(trace), invocation, canonical(inp).decode(),
                                manifest['generation']], capture_output=True, text=True, env=env)
    after = state.read_bytes()
    public = {'input': inp, 'invocation': invocation, 'stdout': completed.stdout,
              'stderr': completed.stderr, 'exit': completed.returncode}
    internal = json.loads(trace.read_bytes()) if trace.exists() else None
    return internal, public, before, after


def observe_cli(directory, inp, caps=None):
    """Independent observer for the metadata-derived public CLI binding.

    Arguments are named flags reconstructed from the input record; the generated
    program parses them through the generic ``run_cli`` adapter (no per-application
    parser), then the same challenge/grounding path applies.
    """
    root = Path(directory)
    state, trace = root / 'state.json', root / 'trace.json'
    before = state.read_bytes()
    invocation = uuid.uuid4().hex
    manifest = json.loads((root / 'provenance.json').read_bytes())
    argv = [sys.executable, str(root / 'operation.py'), '--state', str(state),
            '--trace', str(trace), '--invocation', invocation,
            '--generation', manifest['generation']]
    for key, value in inp.items():
        argv.append('--' + key.replace('_', '-'))
        argv.extend(str(item) for item in value) if isinstance(value, list) else argv.append(str(value))
    env = {**os.environ, CAPS_ENV: caps} if caps is not None else os.environ
    completed = subprocess.run(argv, capture_output=True, text=True, env=env)
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
        external = internal.get('externals', {})
        grounded = (public['exit'] == 0 and public['stderr'] == '' and
                    internal['generation'] == manifest['generation'] and
                    internal['invocation'] == public['invocation'] and
                    internal['input'] == public['input'] and
                    internal['pre'] == json.loads(before) and
                    internal['post'] == json.loads(after) and
                    internal['outcome'] == visible and
                    type(internal['attempted_write']) is bool and
                    (internal['attempted_write'] or before == after) and
                    validate_logged(external))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        grounded = False
    if not grounded:
        return verdict
    verdict['grounded'] = True
    verdict['conformant'] = conforms(contract, public['input'], json.loads(before),
                                     visible, json.loads(after), before == after,
                                     internal['attempted_write'], external)
    return verdict


def _ordered_relation_holds(order, facts, slots, value):
    """Interpret the ordering relation itself: exact multiset, nondecreasing keys.

    A fully tied pair of records may appear in any permutation. The stable
    source-order choice belongs to the validating interpreter's determinism,
    not to the semantic contract, so it is not required here.
    """
    try:
        plan = ordering_plan(order, slots)
    except ValueError:
        return False
    source = _compile(order['source'], slots)[1](facts)
    if not _type(value, {'sequence': plan['element']}):
        return False
    if sorted(map(canonical, value)) != sorted(map(canonical, source)):
        return False
    keys = [key for key, _ in plan['keys']]
    rank = [tuple(row[key] for key in keys) for row in value]
    return rank == sorted(rank)


def conforms(contract, inp, pre, outcome, post, bytes_equal, attempted_write, external=None):
    """Interpret the originating typed contract, independently of emitted Python."""
    typed(contract)
    if not (_type(inp, contract['input']) and _type(pre, contract['state']) and
            _type(post, contract['state']) and isinstance(outcome, dict) and
             set(outcome) == {'kind', 'value'}):
        return False
    slots = {'input': contract['input'], 'pre': contract['state'], 'post': contract['state']}
    facts = {'input': inp, 'pre': pre, 'post': post, 'external': external or {}}
    base = {'input': contract['input'], 'pre': contract['state']}
    branch = next((b for b in contract['branches'] if b['when'] is None or
                   _compile(b['when'], base)[1](facts)), None)
    if branch is None or not _type(outcome['value'], branch.get('value_type', 'string')):
        return False
    if outcome['kind'] != branch['tag']:
        return False
    if isinstance(branch['value'], dict) and set(branch['value']) == {'order'}:
        return _ordered_relation_holds(branch['value']['order'], facts, slots, outcome['value'])
    if outcome != {'kind': branch['tag'], 'value': _compile(branch['value'], slots)[1](facts)}:
        return False
    transition = branch['transition']
    if transition == {'preserve': True}:
        return post == pre and bytes_equal and not attempted_write
    if 'relations' in transition:
        touched = set()
        expected_collections = {}
        for relation in transition['relations']:
            kind, rule = next(iter(relation.items()))
            if kind == 'post_equals':
                touched.add(rule['field'])
                if post[rule['field']] != _compile(rule['value'], slots)[1](facts):
                    return False
                continue
            name = rule['collection']
            touched.add(name)
            rows = pre if name is None else pre[name]
            new = post if name is None else post[name]
            identity = rule['identity'] if 'identity' in rule else rule['key']
            if (len({row[identity] for row in rows}) != len(rows) or
                    len({row[identity] for row in new}) != len(new)):
                return False
            if kind == 'exact_frame':
                record = _compile(rule['record'], slots)[1](facts)
                if record[identity] in {row[identity] for row in rows}:
                    return False
                # Exact singleton selection and full-record equality of the
                # outside-target multiset; storage order is not a constraint.
                if ([row for row in new if row[identity] == record[identity]] != [record] or
                        len(new) != len(rows) + 1 or
                        sorted(canonical(row) for row in new if row[identity] != record[identity]) !=
                        sorted(canonical(row) for row in rows)):
                    return False
            elif kind == 'remove':
                match = _compile(rule['match'], slots)[1](facts)
                expected = [row for row in rows if row[identity] != match]
                if sorted(canonical(row) for row in new) != sorted(canonical(row) for row in expected):
                    return False
            elif kind == 'replace_field':
                key = rule['key']
                match = _compile(rule['match'], slots)[1](facts)
                value = _compile(rule['value'], slots)[1](facts)
                expected = [{**row, rule['field']: value} if row[key] == match else row
                            for row in rows]
                if sorted(canonical(row) for row in new) != sorted(canonical(row) for row in expected):
                    return False
            else:
                value = _compile(rule['value'], slots)[1](facts)
                # Interpret all compatible defaults against one pre-state and
                # compare their joint post-state, not each intermediate result.
                expected_collections.setdefault(name, rows)
                expected_collections[name] = [
                    {**row, rule['field']: value} if rule['field'] not in row else row
                    for row in expected_collections[name]]
        for name, expected in expected_collections.items():
            actual = post if name is None else post[name]
            if sorted(canonical(row) for row in actual) != sorted(canonical(row) for row in expected):
                return False
        if isinstance(pre, dict) and (set(pre) != set(post) or
                any(pre[key] != post[key] for key in pre if key not in touched)):
            return False
        return attempted_write
    if 'default_missing' in transition:
        rule = transition['default_missing']
        identity, field = rule['identity'], rule['field']
        if len({row[identity] for row in pre}) != len(pre):
            return False
        value = _compile(rule['value'], base)[1](facts)
        expected = [{**row, field: value} if field not in row else row for row in pre]
        return post == expected and attempted_write
    update = transition['replace_field']
    key = _compile(update['match'], base)[1](facts)
    value = _compile(update['value'], base)[1](facts)
    expected = [{**row, update['field']: value} if row[update['key']] == key else row
                for row in pre]
    return post == expected and attempted_write
