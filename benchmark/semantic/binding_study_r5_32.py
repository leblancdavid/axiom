"""Non-task observatory console and reproducible public binding pressure study."""

import json
from pathlib import Path
import sys
import tempfile

from benchmark.semantic import public_binding_r5_32 as public
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


EARLY = '2026-01-01T01:00:00Z'
LATE = '2026-01-01T02:00:00Z'


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape):
    return {'literal': {'value': value, 'type': shape}}


def application(default='quiet', scalar='integer', allowed='acquire'):
    last = {'record': {'note': {'optional': 'string'}, 'seen': {'optional': 'instant'}}}
    state = {'record': {'label': 'string', 'at': 'instant', 'mode': 'string', 'quota': scalar, 'last': last}}
    def branch(tag, when, value, shape, changes=None):
        transition = {'relations': [{'post_equals': {'field': key, 'value': expr}}
                                   for key, expr in changes.items()]} if changes else {'preserve': True}
        return {'tag': tag, 'when': when, 'value': value, 'value_type': shape, 'transition': transition}
    def operation(name, inp, branches):
        return {'id': 'observatory.' + name, 'version': 'R5.27', 'input': {'record': inp},
                'state': state, 'branches': branches}
    fallback = {'fallback': {'value': ref('input', 'preferred'), 'default': lit(default, 'string')}}
    record = {'record': {'note': ref('input', 'preferred'), 'seen': ref('input', 'seen')}}
    changes = {'label': fallback, 'last': record}
    configure = operation('configure', {'preferred': {'optional': 'string'}, 'seen': {'optional': 'instant'}}, [
        branch('supplied', {'present': ref('input', 'preferred')}, fallback, 'string', changes),
        branch('omitted', None, fallback, 'string', changes)])
    schedule = operation('schedule', {'when': 'instant'}, [
        branch('ok', {'before': [ref('input', 'when'), lit(LATE, 'instant')]}, ref('input', 'when'),
               'instant', {'at': ref('input', 'when')}),
        branch('rule_rejected', None, lit('window_closed', 'string'), 'string')])
    mode = operation('mode', {'value': 'string'}, [
        branch('ok', {'and': [{'equals': [ref('input', 'value'), lit(allowed, 'string')]},
                              {'equals': [ref('pre', 'mode'), lit('idle', 'string')]}]},
               ref('input', 'value'), 'string', {'mode': ref('input', 'value')}),
        branch('rule_rejected', None, lit('mode_forbidden', 'string'), 'string')])
    quota = operation('quota', {'amount': scalar}, [
        branch('ok', {'equals': [ref('input', 'amount'), lit(7 if scalar == 'integer' else '7', scalar)]},
               ref('input', 'amount'), scalar, {'quota': ref('input', 'amount')}),
        branch('rule_rejected', None, lit('quota_forbidden', 'string'), 'string')])
    return {'id': 'observatory.console', 'state': state,
            'operations': {'configure': configure, 'schedule': schedule, 'mode': mode, 'quota': quota}}


def policy():
    return {'operations': {'mode': {'value': {'argument': 'setting', 'domain': ['idle', 'acquire', 'calibrate']}},
                           'quota': {'amount': {'argument': 'units'}}},
            'error_codes': {category: 'input.' + category for category in public.CATEGORIES}}


def initial(scalar='integer'):
    return {'label': 'initial', 'at': LATE, 'mode': 'idle', 'quota': 0 if scalar == 'integer' else '0', 'last': {}}


def step(model, root, operation, raw):
    binding, semantic, observed, before, after = public.observe(root, operation, raw)
    verdict = public.challenge(model, root, binding, semantic, observed, before, after, policy())
    return {'operation': operation, 'raw': raw, 'public': json.loads(observed['stdout']),
            'exit': observed['exit'], 'binding': binding['binding'], 'semantic_invoked': semantic is not None,
            'semantic_input': semantic['input'] if semantic else None,
            'before': json.loads(before), 'after': json.loads(after), 'bytes_equal': before == after,
            'before_digest': sha(before), 'after_digest': sha(after),
            'observation': observed, 'binding_event': binding, 'semantic_event': semantic,
            'verdict': verdict}


def inject(root, fault):
    """Only disposable copied adapters/binders change; re-seal their real bytes."""
    if fault == 'A':
        path = root / 'input_binding_r5_32.py'
        text = path.read_text(encoding='utf-8').replace(
            '    if not valid(raw, shape):',
            "    if shape == 'instant' and raw == 'not-a-date':\n        return True, '2026-01-01T01:00:00Z'\n    if not valid(raw, shape):")
    else:
        path = root / 'public_adapter_r5_32.py'
        text = path.read_text(encoding='utf-8')
        if fault == 'B':
            text = text.replace('    invoked = False',
                "    if 'preferred' in result['slots']:\n        result['slots']['preferred'] = {'supplied': False, 'state': 'OMITTED'}\n    invoked = False")
        elif fault == 'C':
            text = text.replace("    if result['failures']:",
                "    if result['failures']:\n        invoked = True\n        subprocess.run([sys.executable, str(root / 'operation.py'), operation, state, trace, invocation,\n            json.dumps({'when': '2026-01-01T01:00:00Z'}), generation], capture_output=True, text=True)")
        elif fault == 'D':
            text = text.replace('    invoked = False',
                "    if operation == 'quota' and result['input'] == {'amount': 8}:\n        result = {'slots': {'amount': {'supplied': True, 'state': 'BINDING_FAILED'}},\n                  'input': None, 'failures': [{'argument': 'units', 'slot': 'amount',\n                  'expected': 'integer', 'category': 'malformed_scalar'}]}\n    invoked = False")
        else:
            raise ValueError('unknown fault')
    path.write_text(text, encoding='utf-8', newline='\n')
    public.seal(root)


def study():
    model = application()
    cases = [('omitted', 'configure', {}),
             ('fallback_equivalent', 'configure', {'preferred': 'quiet'}),
             ('optional_explicit', 'configure', {'preferred': 'bright', 'seen': EARLY}),
             ('valid_instant', 'schedule', {'when': EARLY}),
             ('malformed_instant', 'schedule', {'when': 'not-a-date'}),
             ('invalid_domain', 'mode', {'setting': 'broken'}),
             ('valid_domain_forbidden', 'mode', {'setting': 'calibrate'}),
             ('valid_domain', 'mode', {'setting': 'acquire'}),
             ('state_forbidden', 'mode', {'setting': 'acquire'}),
             ('malformed_integer', 'quota', {'units': '7x'}),
             ('semantic_integer_failure', 'quota', {'units': '8'}),
             ('valid_integer', 'quota', {'units': '7'}),
             ('semantic_instant_failure', 'schedule', {'when': LATE}),
             ('missing_required', 'schedule', {}),
             ('malformed_string', 'configure', {'preferred': 5}),
             ('malformed_payload', 'configure', '{'),
             ('unknown_argument', 'configure', {'extra': 'x'}),
             ('unknown_operation', 'absent', {})]
    results = {}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        public.generate(model, root, policy())
        (root / 'state.json').write_bytes(canonical(initial()))
        for name, operation, raw in cases:
            results[name] = step(model, root, operation, raw)
    faults = {}
    for fault, operation, raw in [('A', 'schedule', {'when': 'not-a-date'}),
                                  ('B', 'configure', {'preferred': 'quiet'}),
                                  ('C', 'schedule', {'when': 'not-a-date'}),
                                  ('D', 'quota', {'units': '8'})]:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public.generate(model, root, policy())
            (root / 'state.json').write_bytes(canonical(initial()))
            inject(root, fault)
            faults[fault] = step(model, root, operation, raw)
    mutations = {}
    for name, changed, operation, raw in [
            ('default', application(default='bright'), 'configure', {}),
            ('type', application(scalar='string'), 'quota', {'units': '7x'}),
            ('constraint', application(allowed='calibrate'), 'mode', {'setting': 'calibrate'})]:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public.generate(changed, root, policy())
            (root / 'state.json').write_bytes(canonical(initial('string' if name == 'type' else 'integer')))
            mutations[name] = step(changed, root, operation, raw)
    return {'version': 'R5.32', 'domain': model['id'], 'core_constructs': 30,
            'cases': results, 'faults': faults, 'semantic_mutations': mutations}


if __name__ == '__main__':
    result = study()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_bytes(canonical(result) + b'\n')
    else:
        print(json.dumps(result, indent=2))
