"""Checked transport profile and independent layered public-call challenge.

Static types come from sealed CheckedPlan facts. No transport semantic compiler.
"""

import json
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import public_binding_r5_32 as binding
from benchmark.semantic import transport_runtime_r5_34 as adapter
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


ROOT = Path(__file__).parent
FILES = ('transport.json', 'transport_runtime_r5_34.py', 'input_binding_r5_32.py')


def specification(plans):
    """Convenience default profile: all declared tags are public successes.

    Failure classification is explicit public interface policy, not tag guessing
    or re-evaluation of application predicates. Applications can override it.
    """
    descriptors = binding.metadata(plans)
    return [{'public': name, 'semantic': name,
             'arguments': [{'public': arg, 'slot': field['slot'], 'decoder': field['type'],
                            'representation': 'json' if field['type'] == 'boolean' else 'text',
                            'domain': field['domain']} for arg, field in descriptors['operations'][name].items()],
             'outcomes': {tag: {'encoding': 'json', 'type': shape, 'status': 'SUCCESS'}
                          for tag, shape in plan.outcomes.items()}}
            for name, plan in plans.items()]


def validate(plans, spec):
    """Check interface mapping only, consuming authoritative plan slots/outcomes."""
    if type(spec) is not list or not spec:
        raise ValueError('nonempty transport operation list required')
    operations = {}
    for item in spec:
        if type(item) is not dict or set(item) != {'public', 'semantic', 'arguments', 'outcomes'}:
            raise ValueError('invalid transport operation descriptor')
        public, semantic = item['public'], item['semantic']
        if type(public) is not str or not public or public in operations:
            raise ValueError('duplicate or invalid public operation')
        if type(semantic) is not str or semantic not in plans:
            raise ValueError('unknown semantic operation')
        plan = plans[semantic]
        plan.assert_invariants()
        fields, arguments, slots = plan.slots['input']['record'], {}, set()
        if type(item['arguments']) is not list:
            raise ValueError('argument mappings must be a list')
        for arg in item['arguments']:
            if type(arg) is not dict or set(arg) != {'public', 'slot', 'decoder', 'representation', 'domain'}:
                raise ValueError('invalid argument mapping')
            name, slot = arg['public'], arg['slot']
            if type(name) is not str or not name or type(slot) is not str or name in arguments or slot in slots:
                raise ValueError('duplicate argument binding')
            if slot not in fields:
                raise ValueError('unknown input slot')
            declaration = fields[slot]
            optional = isinstance(declaration, dict) and set(declaration) == {'optional'}
            shape = declaration['optional'] if optional else declaration
            if shape not in ('string', 'integer', 'instant', 'boolean') or arg['decoder'] != shape:
                raise ValueError('incompatible decoder/type')
            if arg['representation'] not in ('text', 'json') or (shape == 'boolean' and arg['representation'] != 'json'):
                raise ValueError('incompatible raw representation')
            # Reuse R5.32's checked finite-domain policy, not operation predicates.
            checked = binding.metadata({semantic: plan}, {'operations': {semantic: {
                slot: {'domain': arg['domain']}}}})
            field = checked['operations'][semantic][slot]
            arguments[name] = {**field, 'representation': arg['representation']}
            slots.add(slot)
        required = {slot for slot, shape in fields.items()
                    if not (isinstance(shape, dict) and set(shape) == {'optional'})}
        if not required <= slots:
            raise ValueError('missing required public argument mapping')
        if type(item['outcomes']) is not dict or set(item['outcomes']) != set(plan.outcomes):
            raise ValueError('wrong operation outcome mapping')
        for tag, desc in item['outcomes'].items():
            if (type(desc) is not dict or set(desc) != {'encoding', 'type', 'status'} or
                    desc['encoding'] != 'json' or desc['type'] != plan.outcomes[tag] or
                    desc['status'] not in ('SUCCESS', 'SEMANTIC_FAILURE')):
                raise ValueError('incompatible output encoding/outcome type')
        operations[public] = {'semantic': semantic, 'contract': plan.digest,
            'arguments': arguments, 'outcomes': item['outcomes'],
            'applicability': {'pre': plan.slots['pre'], 'post': plan.slots['post'],
                              'has_semantic_precondition': plan.applicability is not None},
            'error_codes': {c: c for c in binding.CATEGORIES}}
    return operations


def profile(application, spec, manifest):
    plans = pipeline.checked(application)
    return {'version': 'R5.34', 'id': application['id'],
            'application': sha(canonical(application)), 'generation': manifest['generation'],
            'units': {name: plan.digest for name, plan in plans.items()},
            'operations': validate(plans, spec)}


def seal(root):
    manifest = json.loads((root / 'provenance.json').read_bytes())
    (root / 'transport_provenance.json').write_bytes(canonical({
        'generation': manifest['generation'], 'files': {name: sha((root / name).read_bytes()) for name in FILES}}))


def generate(application, directory, spec=None):
    plans = pipeline.checked(application)
    spec = specification(plans) if spec is None else spec
    # Validate before producing any normal executable artifacts.
    validate(plans, spec)
    root = Path(directory)
    manifest = pipeline.generate(application, root)
    (root / FILES[0]).write_bytes(canonical(profile(application, spec, manifest)))
    for name in FILES[1:]:
        (root / name).write_bytes((ROOT / name).read_bytes())
    seal(root)
    return manifest


def observe(root, argv):
    invocation = uuid.uuid4().hex
    state = root / 'state.json'
    trace, transport_trace = root / (invocation + '.semantic.json'), root / (invocation + '.transport.json')
    before = state.read_bytes()
    command = [sys.executable, str(root / FILES[1]), str(state), str(trace),
               str(transport_trace), invocation, *argv]
    completed = subprocess.run(command, capture_output=True, text=True)
    public = {'command': command, 'argv': argv, 'invocation': invocation,
              'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode}
    return (json.loads(transport_trace.read_bytes()) if transport_trace.exists() else None,
            json.loads(trace.read_bytes()) if trace.exists() else None,
            public, before, state.read_bytes())


def expected_raw(argv, route):
    """Independent argv/suppliedness oracle; does not call adapter parsing."""
    if (len(argv) - 1) % 2:
        raise ValueError('unpaired argv')
    raw = {}
    for index in range(1, len(argv), 2):
        name = argv[index]
        if not name.startswith('--') or name[2:] in raw:
            raise ValueError('bad argv')
        name = name[2:]
        field = route['arguments'].get(name)
        raw[name] = json.loads(argv[index + 1]) if field and field['representation'] == 'json' else argv[index + 1]
    return raw


def challenge(application, root, spec, event, semantic, public, before, after):
    verdict = {'profile_integrity': False, 'transport_grounded': False,
               'TRANSPORT_BINDING_CONFORMANT': None, 'INPUT_BINDING_CONFORMANT': None,
               'SEMANTIC_EXECUTION_CONFORMANT': None, 'TRANSPORT_OUTPUT_CONFORMANT': None}
    try:
        manifest = json.loads((root / 'provenance.json').read_bytes())
        expected_profile = profile(application, spec, manifest)
        verdict['profile_integrity'] = (adapter.load(root) == expected_profile and
            manifest['application'] == sha(canonical(application)))
        if not verdict['profile_integrity']:
            return verdict
        visible = json.loads(public['stdout'])
        grounded = (event['argv'] == public['argv'] and event['invocation'] == public['invocation'] and
            event['generation'] == manifest['generation'] and event['public'] == visible and
            event['exit'] == public['exit'] and public['stderr'] == '' and
            event['pre_digest'] == sha(before) and event['post_digest'] == sha(after))
        verdict['transport_grounded'] = grounded
        if not grounded:
            return verdict
        requested = public['argv'][0] if public['argv'] else None
        route = expected_profile['operations'].get(requested)
        if route is None:
            verdict['TRANSPORT_BINDING_CONFORMANT'] = (event['requested'] == requested and
                event['operation'] is None and event['binding'] is None and not event['semantic_invoked'] and
                semantic is None and before == after)
            verdict['TRANSPORT_OUTPUT_CONFORMANT'] = (visible == {
                'status': 'TRANSPORT_FAILURE', 'error': 'unknown public operation'} and public['exit'] == 4)
            return verdict
        try:
            raw = expected_raw(public['argv'], route)
        except (ValueError, TypeError):
            verdict['TRANSPORT_BINDING_CONFORMANT'] = (event['raw'] is None and event['binding'] is None and
                not event['semantic_invoked'] and semantic is None and before == after)
            verdict['TRANSPORT_OUTPUT_CONFORMANT'] = (visible == {
                'status': 'TRANSPORT_FAILURE', 'error': 'malformed public arguments'} and public['exit'] == 4)
            return verdict
        operation = route['semantic']
        metadata = adapter.binding_metadata(route)
        expected = binding.expected_binding(operation, json.dumps(raw), metadata)
        verdict['TRANSPORT_BINDING_CONFORMANT'] = (event['requested'] == requested and
            event['operation'] == operation and event['raw'] == raw and
            event['binding']['slots'] == expected['slots'] and
            event['semantic_invoked'] == (not expected['failures']))
        verdict['INPUT_BINDING_CONFORMANT'] = event['binding'] == expected
        if expected['failures']:
            wanted = {'status': 'BINDING_FAILURE', 'errors': [
                {**f, 'code': route['error_codes'][f['category']]} for f in expected['failures']]}
            verdict['TRANSPORT_OUTPUT_CONFORMANT'] = visible == wanted and public['exit'] == 2
            verdict['TRANSPORT_BINDING_CONFORMANT'] &= semantic is None and before == after
            return verdict
        if semantic is None:
            # No typed outcome/event for runtime precondition rejection. Do not
            # manufacture semantic conformance from a public error envelope.
            rejected = event['semantic_result']
            verdict['TRANSPORT_OUTPUT_CONFORMANT'] = (rejected is not None and rejected['exit'] != 0 and
                visible == {'status': 'INVOCATION_FAILURE', 'error': 'generated execution rejected'} and
                public['exit'] == 3 and before == after)
            return verdict
        result = event['semantic_result']
        internal_public = {'operation': operation, 'invocation': public['invocation'],
            'input': expected['input'], **result}
        checked = pipeline.challenge(application, root, semantic, internal_public, before, after)
        verdict['SEMANTIC_EXECUTION_CONFORMANT'] = checked['grounded'] and checked['conformant']
        outcome = json.loads(result['stdout'])
        descriptor = route['outcomes'][outcome['kind']]
        wanted = {'status': descriptor['status'], 'outcome': outcome}
        verdict['TRANSPORT_OUTPUT_CONFORMANT'] = (visible == wanted and
            public['exit'] == (0 if descriptor['status'] == 'SUCCESS' else 1))
        # Independent durable snapshots already challenge semantic event pre/post.
        verdict['TRANSPORT_BINDING_CONFORMANT'] &= (semantic['operation'] == operation and
            semantic['input'] == expected['input'] and checked['grounded'])
    except (ValueError, KeyError, TypeError, OSError):
        pass
    return verdict
