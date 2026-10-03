"""Generic CLI/raw binding/invocation/encoding boundary; no semantic AST access."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

if __package__:
    from benchmark.semantic.input_binding_r5_32 import bind, public_failure
    from benchmark.semantic.refined_runtime_r5_28 import valid
else:
    from input_binding_r5_32 import bind, public_failure
    from refined_runtime_r5_28 import valid


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load(root):
    """Reject stale profile/artifacts before binding or touching application state.

    Digests are revision/integrity checks, not signatures against a hostile writer.
    Authoritative static validation happens at generation against CheckedPlans.
    """
    profile = json.loads((root / 'transport.json').read_bytes())
    manifest = json.loads((root / 'provenance.json').read_bytes())
    seal = json.loads((root / 'transport_provenance.json').read_bytes())
    if (profile['generation'] != manifest['generation'] or
            profile['application'] != manifest['application'] or
            profile['units'] != manifest['units'] or
            sha((root / 'operation.py').read_bytes()) != manifest['artifact'] or
            sha((root / 'refined_runtime_r5_28.py').read_bytes()) != manifest['runtime'] or
            sha(canonical({k: v for k, v in manifest.items() if k != 'generation'})) != manifest['generation'] or
            seal != {'generation': manifest['generation'], 'files': {
                name: sha((root / name).read_bytes()) for name in
                ('transport.json', 'transport_runtime_r5_34.py', 'input_binding_r5_32.py')}}):
        raise ValueError('stale or corrupt transport profile/artifact')
    return profile


def raw_arguments(argv, route):
    """Text or generic JSON representation only; never convert semantic scalars."""
    raw = {}
    if len(argv) % 2:
        raise ValueError('arguments require flag/value pairs')
    for flag, text in zip(argv[::2], argv[1::2]):
        if not flag.startswith('--') or flag[2:] in raw:
            raise ValueError('invalid or duplicate public argument')
        name = flag[2:]
        descriptor = route['arguments'].get(name)
        raw[name] = json.loads(text) if descriptor and descriptor['representation'] == 'json' else text
    return raw


def binding_metadata(route):
    return {'operations': {route['semantic']: {
        name: {key: field[key] for key in ('slot', 'type', 'optional', 'domain')}
        for name, field in route['arguments'].items()}},
        'error_codes': route['error_codes']}


def encode(outcome, route):
    """Shape checked generic JSON encoding, including nested records/collections."""
    if type(outcome) is not dict or set(outcome) != {'kind', 'value'}:
        raise ValueError('invalid tagged result')
    descriptor = route['outcomes'].get(outcome['kind'])
    if descriptor is None or not valid(outcome['value'], descriptor['type']):
        raise ValueError('result does not match checked encoding shape')
    status = descriptor['status']
    return {'status': status, 'outcome': outcome}, 0 if status == 'SUCCESS' else 1


def main():
    # Infrastructure paths are separate from public argv, never semantic inputs.
    state, trace, transport_trace, invocation, *argv = sys.argv[1:]
    root = Path(__file__).parent
    try:
        profile = load(root)
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'TRANSPORT_FAILURE', 'error': str(exc)}), file=sys.stderr)
        return 4
    before = Path(state).read_bytes()
    requested = argv[0] if argv else None
    route = profile['operations'].get(requested)
    binding, raw, semantic_result = None, None, None
    invoked = False
    if route is None:
        visible, exit_code = {'status': 'TRANSPORT_FAILURE', 'error': 'unknown public operation'}, 4
    else:
        try:
            raw = raw_arguments(argv[1:], route)
        except (ValueError, TypeError):
            visible, exit_code = {'status': 'TRANSPORT_FAILURE', 'error': 'malformed public arguments'}, 4
        else:
            operation = route['semantic']
            binding = bind(operation, json.dumps(raw), binding_metadata(route))
            if binding['failures']:
                visible = public_failure(binding, binding_metadata(route))
                visible['status'] = 'BINDING_FAILURE'
                exit_code = 2
            else:
                invoked = True
                completed = subprocess.run([sys.executable, str(root / 'operation.py'), operation,
                    state, trace, invocation, json.dumps(binding['input']), profile['generation']],
                    capture_output=True, text=True)
                semantic_result = {'stdout': completed.stdout, 'stderr': completed.stderr,
                                   'exit': completed.returncode}
                if completed.returncode:
                    # Runtime/applicability rejection is not a declared typed outcome.
                    visible, exit_code = {'status': 'INVOCATION_FAILURE', 'error': 'generated execution rejected'}, 3
                else:
                    visible, exit_code = encode(json.loads(completed.stdout), route)
    after = Path(state).read_bytes()
    event = {'argv': argv, 'requested': requested, 'raw': raw,
             'operation': route['semantic'] if route else None, 'binding': binding,
             'semantic_invoked': invoked, 'semantic_result': semantic_result,
             'invocation': invocation, 'generation': profile['generation'],
             'public': visible, 'exit': exit_code, 'pre_digest': sha(before), 'post_digest': sha(after)}
    Path(transport_trace).write_bytes(canonical(event))
    print(json.dumps(visible, sort_keys=True))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
