"""Independent mineral catalogue and specimen lifecycle transport evidence."""

import copy
import json
from pathlib import Path
import sys
import tempfile

from benchmark.semantic import checked_transport_r5_34 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import evolution_study_r5_33 as evolution
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


EARLY = '2026-01-01T01:00:00Z'


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape='string'):
    return {'literal': {'value': value, 'type': shape}}


def application(default='unlabelled'):
    row = {'record': {'code': 'string', 'label': 'string', 'medium': 'string',
                      'quantity': 'integer', 'seen': {'optional': 'instant'}}}
    state = {'sequence': row}
    error_shape = {'record': {'reason': 'string'}}
    yes = {'equals': [lit(1, 'integer'), lit(1, 'integer')]}
    def operation(name, inp, value, shape, transition, guard=None):
        return {'id': 'mineral.' + name, 'version': 'R5.27', 'input': {'record': inp}, 'state': state,
            'branches': [
                {'tag': 'ok', 'when': guard or yes, 'value': value, 'value_type': shape, 'transition': transition},
                {'tag': 'rejected', 'when': None, 'value': {'record': {'reason': lit('rule_not_satisfied')}},
                 'value_type': error_shape, 'transition': {'preserve': True}}]}
    inp = {'code': 'string', 'medium': 'string', 'quantity': 'integer',
           'preferred': {'optional': 'string'}, 'seen': {'optional': 'instant'}}
    record = {'record': {'code': ref('input', 'code'), 'medium': ref('input', 'medium'),
        'quantity': ref('input', 'quantity'), 'seen': ref('input', 'seen'),
        'label': {'fallback': {'value': ref('input', 'preferred'), 'default': lit(default)}}}}
    selected = {'select': {'source': ref('pre'), 'where': {
        'equals': [ref('item', 'code'), ref('input', 'code')]}}}
    matched = {'equals': [{'cardinality': selected}, lit(1, 'integer')]}
    guard = {'and': [{'equals': [ref('input', 'quantity'), lit(7, 'integer')]},
                     {'equals': [ref('input', 'medium'), lit('mineral')]}]}
    create = operation('create', inp, record, row, {'relations': [{'exact_frame': {
        'collection': None, 'identity': 'code', 'record': record}}]}, guard)
    listing = operation('list', {}, ref('pre'), state, {'preserve': True})
    replace = operation('replace', {'code': 'string', 'label': 'string'}, lit('relabelled'), 'string',
        {'relations': [{'replace_field': {'collection': None, 'key': 'code',
            'match': ref('input', 'code'), 'field': 'label', 'value': ref('input', 'label')}}]}, matched)
    remove = operation('remove', {'code': 'string'}, {'cardinality': selected}, 'integer',
        {'relations': [{'remove': {'collection': None, 'identity': 'code',
                                   'match': ref('input', 'code')}}]}, matched)
    return {'id': 'mineral.catalogue', 'state': state,
            'operations': {'create': create, 'list': listing, 'replace': replace, 'remove': remove}}


def specification(model):
    spec = transport.specification(pipeline.checked(model))
    for item in spec:
        if 'rejected' in item['outcomes']:
            item['outcomes']['rejected']['status'] = 'SEMANTIC_FAILURE'
        if item['semantic'] == 'create':
            item['public'] = 'register'
            for arg in item['arguments']:
                if arg['slot'] == 'medium':
                    arg['domain'] = ['mineral', 'gas']
                if arg['slot'] == 'quantity':
                    arg['public'] = 'units'
    return spec


def capture(model, root, spec, argv):
    event, semantic, public, before, after = transport.observe(root, argv)
    verdict = transport.challenge(model, root, spec, event, semantic, public, before, after)
    return {'event': event, 'semantic': semantic, 'public': public,
            'pre_bytes': before.decode(), 'post_bytes': after.decode(),
            'pre_digest': sha(before), 'post_digest': sha(after), 'verdict': verdict}


def fault(root, name):
    """Disposable copied artifact mutations, never authoritative source changes."""
    if name == 'C':
        path = root / 'transport.json'
        descriptor = json.loads(path.read_bytes())
        descriptor['operations']['register']['arguments']['units']['type'] = 'instant'
        path.write_bytes(canonical(descriptor))
    else:
        path = root / 'transport_runtime_r5_34.py'
        source = path.read_text(encoding='utf-8')
        if name == 'A':
            source = source.replace("route = profile['operations'].get(requested)",
                "route = profile['operations'].get('remove' if requested == 'list' else requested)")
        elif name == 'B':
            source = source.replace("            if binding['failures']:",
                "            if 'preferred' in binding['slots']:\n                binding['slots']['preferred']['supplied'] = True\n            if binding['failures']:")
        elif name == 'D':
            source = source.replace("status = descriptor['status']", "status = 'SUCCESS'")
        elif name == 'E':
            source = source.replace("    status = descriptor['status']",
                "    if isinstance(outcome['value'], dict):\n        outcome['value'].pop('label', None)\n    status = descriptor['status']")
        elif name == 'F':
            source = source.replace("    after = Path(state).read_bytes()",
                "    data = json.loads(Path(state).read_bytes())\n    if isinstance(data, list):\n        data.append({'code': 'forbidden', 'label': 'transport', 'medium': 'mineral', 'quantity': 7})\n        Path(state).write_bytes(canonical(data))\n    after = Path(state).read_bytes()")
        else:
            raise ValueError('unknown fault')
        path.write_bytes(source.encode())
    transport.seal(root)


def study():
    model = application()
    spec = specification(model)
    base = ['register', '--code', 'M-1', '--medium', 'mineral', '--units', '7']
    cases = [('omitted', base), ('list', ['list']),
        ('explicit', ['register', '--code', 'M-2', '--medium', 'mineral', '--units', '7',
                      '--preferred', 'quartz', '--seen', EARLY]),
        ('malformed_instant', ['register', '--code', 'M-3', '--medium', 'mineral', '--units', '7', '--seen', 'bad-date']),
        ('invalid_domain', ['register', '--code', 'M-3', '--medium', 'broken', '--units', '7']),
        ('malformed_scalar', ['register', '--code', 'M-3', '--medium', 'mineral', '--units', '7x']),
        ('semantic_rejection', ['register', '--code', 'M-3', '--medium', 'gas', '--units', '7']),
        ('missing_required', ['register']), ('unknown_argument', ['list', '--extra', 'x']),
        ('unknown_operation', ['absent']), ('duplicate_argument', ['list', '--x', 'a', '--x', 'b']),
        ('replace', ['replace', '--code', 'M-1', '--label', 'new']),
        ('read_after_replace', ['list']), ('remove', ['remove', '--code', 'M-2']),
        ('read_after_remove', ['list'])]
    report = {'version': 'R5.34', 'entry_point': 'benchmark.semantic.current_pipeline',
              'candidate_core_constructs': 30, 'A': {}, 'B': {}, 'faults': {}, 'mutations': {}}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        manifest = transport.generate(model, root, spec)
        report['A'] = {'source': model, 'specification': spec, 'manifest': manifest, 'calls': {}}
        (root / 'state.json').write_bytes(canonical([]))
        for name, argv in cases:
            report['A']['calls'][name] = capture(model, root, spec, argv)
    for envelope in (False, True):
        model_b = evolution.application(envelope)
        spec_b = transport.specification(pipeline.checked(model_b))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = transport.generate(model_b, root, spec_b)
            (root / 'state.json').write_bytes(canonical(evolution.initial(envelope)))
            unavailable_before = [capture(model_b, root, spec_b, [name])
                                  for name in ('current', 'current_insert')]
            calls = [capture(model_b, root, spec_b, [name]) for name in (
                'legacy', 'legacy_insert', 'migrate', 'current_insert', 'current')]
            rejected = [capture(model_b, root, spec_b, [name]) for name in ('legacy', 'migrate', 'legacy_insert')]
            report['B']['envelope' if envelope else 'rows'] = {
                'source': model_b, 'specification': spec_b, 'manifest': manifest,
                'calls': calls, 'unavailable_before': unavailable_before, 'unavailable_after': rejected}
    for name, argv in [('A', ['list']), ('B', base), ('C', base),
                      ('D', ['register', '--code', 'M-1', '--medium', 'gas', '--units', '7']),
                      ('E', base), ('F', ['list'])]:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec)
            (root / 'state.json').write_bytes(canonical([]))
            fault(root, name)
            report['faults'][name] = capture(model, root, spec, argv)
    for name in ('rename', 'optional_mapping', 'default', 'projection', 'domain'):
        changed = application(default='curated' if name == 'default' else 'unlabelled')
        if name == 'projection':
            changed['operations']['create']['branches'][0]['value'] = ref('input', 'code')
            changed['operations']['create']['branches'][0]['value_type'] = 'string'
        changed_spec = specification(changed)
        argv = list(base)
        if name == 'rename':
            changed_spec[0]['public'] = argv[0] = 'enrol'
        elif name == 'optional_mapping':
            changed_spec[0]['arguments'] = [a for a in changed_spec[0]['arguments'] if a['slot'] != 'preferred']
        elif name == 'domain':
            next(a for a in changed_spec[0]['arguments'] if a['slot'] == 'medium')['domain'] = ['mineral']
            argv[4] = 'gas'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(changed, root, changed_spec)
            (root / 'state.json').write_bytes(canonical([]))
            report['mutations'][name] = capture(changed, root, changed_spec, argv)
            report['mutations'][name]['adapter_digest'] = sha((root / 'transport_runtime_r5_34.py').read_bytes())
    return report


if __name__ == '__main__':
    result = study()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_bytes(canonical(result) + b'\n')
        print(json.dumps({'output': sys.argv[1], 'A_calls': len(result['A']['calls']),
            'B_lifecycle_calls': sum(len(b['calls']) for b in result['B'].values()),
            'availability_rejections': sum(len(b['unavailable_before']) + len(b['unavailable_after'])
                                           for b in result['B'].values()),
            'mutations': len(result['mutations']),
            'fault_layers': {name: call['verdict'] for name, call in result['faults'].items()}}, sort_keys=True))
    else:
        print(json.dumps(result, indent=2))
