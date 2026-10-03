"""Checked public metadata, independent binding grounding and current entry glue.

This is not another semantic compiler. Static slot shapes originate solely in
current_pipeline.checked; concrete decode expectations are independently checked
here, without calling the binder or evaluating generated code.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import refined_runtime_r5_28 as runtime


ROOT = Path(__file__).parent
FILES = ('input_binding_r5_32.py', 'public_adapter_r5_32.py', 'public_binding.json')
CATEGORIES = ('malformed_payload', 'unknown_operation', 'unknown_argument',
              'missing_required', 'malformed_scalar', 'outside_domain')


def metadata(plans, policy=None):
    """Validate interface metadata against sealed authoritative input slots.

    Aliases and finite decode domains are explicit interface policy, not inferred
    from application guards. Domain entries must already be valid concrete values
    of the checked base type. No defaults are installed by this layer.
    """
    policy = policy or {}
    if set(policy) - {'operations', 'error_codes'}:
        raise ValueError('unknown binding policy')
    if set(policy.get('operations', {})) - set(plans):
        raise ValueError('unknown binding operation')
    codes = policy.get('error_codes', {category: category for category in CATEGORIES})
    if set(codes) != set(CATEGORIES) or any(type(v) is not str or not v for v in codes.values()):
        raise ValueError('complete public failure mapping required')
    operations = {}
    for name, plan in plans.items():
        plan.assert_invariants()
        fields = plan.slots['input']['record']
        rules = policy.get('operations', {}).get(name, {})
        if set(rules) - set(fields):
            raise ValueError('unknown checked input slot')
        descriptors = {}
        for slot, declaration in fields.items():
            optional = isinstance(declaration, dict) and set(declaration) == {'optional'}
            shape = declaration['optional'] if optional else declaration
            if shape not in ('string', 'integer', 'instant', 'boolean'):
                raise ValueError('unsupported public binding shape')
            rule = rules.get(slot, {})
            if not isinstance(rule, dict) or set(rule) - {'argument', 'domain'}:
                raise ValueError('invalid slot binding metadata')
            argument, domain = rule.get('argument', slot), rule.get('domain')
            if type(argument) is not str or not argument or argument in descriptors:
                raise ValueError('invalid or duplicate public argument')
            if domain is not None and (type(domain) is not list or not domain or
                    any(not runtime.valid(v, shape) for v in domain) or
                    len({emitter.canonical(v) for v in domain}) != len(domain)):
                raise ValueError('domain must contain distinct typed values')
            descriptors[argument] = {'slot': slot, 'type': shape, 'optional': optional, 'domain': domain}
        operations[name] = descriptors
    return {'version': 'R5.32', 'operations': operations, 'error_codes': codes}


def seal(directory):
    """Artifact identity; also usable for faithfully reported disposable faults."""
    root = Path(directory)
    source = json.loads((root / 'provenance.json').read_bytes())
    manifest = {'generation': source['generation'], 'files': {
        name: emitter.sha((root / name).read_bytes()) for name in FILES}}
    (root / 'public_provenance.json').write_bytes(emitter.canonical(manifest))
    return manifest


def generate(application, directory, policy=None):
    plans = pipeline.checked(application)
    descriptor = metadata(plans, policy)
    manifest = pipeline.generate(application, directory)
    root = Path(directory)
    for name in FILES[:2]:
        (root / name).write_bytes((ROOT / name).read_bytes())
    (root / FILES[2]).write_bytes(emitter.canonical(descriptor))
    seal(root)
    return manifest


def observe(directory, operation, raw):
    """External subprocess/output/file observation, not adapter self-report."""
    root = Path(directory)
    state = root / 'state.json'
    invocation = uuid.uuid4().hex
    trace = root / (invocation + '.semantic.json')
    binding_trace = root / (invocation + '.binding.json')
    before = state.read_bytes()
    generation = json.loads((root / 'provenance.json').read_bytes())['generation']
    payload = raw if type(raw) is str else emitter.canonical(raw).decode()
    completed = subprocess.run([sys.executable, str(root / FILES[1]), operation, str(state),
        str(trace), str(binding_trace), invocation, payload, generation], capture_output=True, text=True)
    public = {'operation': operation, 'payload': payload, 'invocation': invocation,
              'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode}
    return (json.loads(binding_trace.read_bytes()) if binding_trace.exists() else None,
            json.loads(trace.read_bytes()) if trace.exists() else None,
            public, before, state.read_bytes())


def expected_binding(operation, payload, descriptor):
    """Independent concrete binding oracle, deliberately not a call to bind/decode.

    It uses the same checked types but a separate scalar conversion and membership
    evaluation. It contains no application precondition or state inspection.
    """
    def fail(argument, slot, shape, category):
        return {'argument': argument, 'slot': slot, 'expected': shape, 'category': category}
    try:
        raw = json.loads(payload)
    except (ValueError, TypeError):
        raw = None
    if type(raw) is not dict:
        return {'slots': {}, 'input': None, 'failures': [fail(None, None, 'argument_object', 'malformed_payload')]}
    if operation not in descriptor['operations']:
        return {'slots': {}, 'input': None, 'failures': [fail(None, None, None, 'unknown_operation')]}
    fields = descriptor['operations'][operation]
    slots, inp = {}, {}
    failures = [fail(key, None, None, 'unknown_argument') for key in sorted(set(raw) - set(fields))]
    for argument, field in sorted(fields.items()):
        slot, shape = field['slot'], field['type']
        supplied = argument in raw
        status = 'OMITTED'
        if not supplied:
            if not field['optional']:
                failures.append(fail(argument, slot, shape, 'missing_required'))
        else:
            value = raw[argument]
            category = None
            if shape == 'integer' and type(value) is str:
                digits = value[1:] if value[:1] in ('+', '-') else value
                if not digits or any(c not in '0123456789' for c in digits):
                    category = 'malformed_scalar'
                else:
                    try:
                        value = int(value, 10)
                    except ValueError:
                        category = 'malformed_scalar'
            if shape == 'instant':
                try:
                    ok = (type(value) is str and value.endswith('Z') and
                          datetime.fromisoformat(value[:-1] + '+00:00').tzinfo == timezone.utc)
                except ValueError:
                    ok = False
            else:
                ok = type(value) is {'string': str, 'integer': int, 'boolean': bool}[shape]
            if not ok:
                category = 'malformed_scalar'
            if category is None and field['domain'] is not None and not any(
                    type(value) is type(member) and value == member for member in field['domain']):
                category = 'outside_domain'
            status = 'BOUND_TYPED' if category is None else 'BINDING_FAILED'
            if category is None:
                inp[slot] = value
            else:
                failures.append(fail(argument, slot, shape, category))
        slots[slot] = {'supplied': supplied, 'state': status}
    return {'slots': slots, 'input': None if failures else inp, 'failures': failures}


def challenge(application, directory, binding, semantic, public, before, after, policy=None):
    root = Path(directory)
    verdict = {'provenance_valid': False, 'binding_grounded': False,
               'binding_conformant': None, 'semantic_grounded': False, 'semantic_conformant': None}
    try:
        descriptor = metadata(pipeline.checked(application), policy)
        source = json.loads((root / 'provenance.json').read_bytes())
        public_manifest = json.loads((root / 'public_provenance.json').read_bytes())
        expected_manifest = {'generation': source['generation'], 'files': {
            name: emitter.sha((root / name).read_bytes()) for name in FILES}}
        if (public_manifest != expected_manifest or
                json.loads((root / FILES[2]).read_bytes()) != descriptor):
            return verdict
        expected_source = {'application': emitter.sha(emitter.canonical(application)), 'id': application['id'],
            'artifact': emitter.sha((root / 'operation.py').read_bytes()),
            'runtime': emitter.sha((root / emitter.RUNTIME.name).read_bytes()),
            'units': {name: emitter.sha(emitter.canonical(contract)) for name, contract in application['operations'].items()}}
        verdict['provenance_valid'] = (all(source.get(k) == v for k, v in expected_source.items()) and
            expected_source['runtime'] == emitter.sha(emitter.RUNTIME.read_bytes()) and
            source['generation'] == emitter.sha(emitter.canonical(expected_source)))
        if not verdict['provenance_valid']:
            return verdict
        visible = json.loads(public['stdout'])
        grounded = (binding['operation'] == public['operation'] and binding['invocation'] == public['invocation'] and
            binding['generation'] == source['generation'] and binding['public'] == visible and public['stderr'] == '' and
            binding['pre_digest'] == emitter.sha(before) and binding['post_digest'] == emitter.sha(after) and
            type(binding['semantic_invoked']) is bool and binding['semantic_invoked'] == (semantic is not None))
        verdict['binding_grounded'] = grounded
        if not grounded:
            return verdict
        expected = expected_binding(public['operation'], public['payload'], descriptor)
        failed = bool(expected['failures'])
        if failed:
            expected_public = {'status': 'binding_failure', 'errors': [
                {**item, 'code': descriptor['error_codes'][item['category']]} for item in expected['failures']]}
            verdict['binding_conformant'] = (binding['binding'] == expected and not binding['semantic_invoked'] and
                semantic is None and visible == expected_public and public['exit'] == 2 and
                json.loads(before) == json.loads(after))
        else:
            verdict['binding_conformant'] = (binding['binding'] == expected and binding['semantic_invoked'] and
                semantic is not None and semantic['input'] == expected['input'] and
                visible['status'] == 'semantic_outcome' and public['exit'] == 0)
            if verdict['binding_conformant']:
                semantic_public = {'operation': public['operation'], 'invocation': public['invocation'],
                    'input': expected['input'], 'exit': 0, 'stderr': '',
                    'stdout': json.dumps(visible['outcome'])}
                checked = pipeline.challenge(application, root, semantic, semantic_public, before, after)
                verdict['semantic_grounded'] = checked['grounded']
                verdict['semantic_conformant'] = checked['conformant']
    except (ValueError, KeyError, TypeError, OSError):
        pass
    return verdict
