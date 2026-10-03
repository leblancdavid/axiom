"""Independent specimen sources and actual current-pipeline observations.

This is study/evidence machinery, not a compiler or a migration implementation.
"""

import argparse
import copy
import json
from pathlib import Path
import tempfile

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def lit(value, shape=None):
    return {'literal': {'type': shape or ('integer' if type(value) is int else 'string'), 'value': value}}


def ref(*path):
    return {'ref': list(path)}


ROW_A = {'record': {'accession': 'string', 'designation': 'string',
                    'provenance': {'optional': 'string'}, 'medium': {'optional': 'string'}}}
ROW_B = {'record': {**ROW_A['record'], 'medium': 'string'}}
ROWS_A, ROWS_B = {'sequence': ROW_A}, {'sequence': ROW_B}
ENVELOPE_B = {'record': {'revision': 'integer', 'specimens': ROWS_B,
                         'metadata': {'record': {'collection': 'string'}}}}
STATE_A = {'record': {'revision': 'integer', 'specimens': ROWS_A,
                     'metadata': {'record': {'collection': 'string'}}}}


def rows():
    # Both variants obey V1: optional medium may already carry equivalent data.
    return [{'accession': 'M-1', 'designation': 'Quartz', 'provenance': 'ridge'},
            {'accession': 'M-2', 'designation': 'Basalt', 'medium': 'rock'},
            {'accession': 'M-3', 'designation': 'Calcite'}]


def operation(name, pre, post, value, shape, transition, requires=None):
    yes = {'equals': [lit(1), lit(1)]}
    return {'id': 'specimen.' + name, 'version': 'R5.33', 'input': {'record': {}},
            'state': {'pre': pre, 'post': post}, 'requires': requires or copy.deepcopy(yes),
            'branches': [
                {'tag': 'ok', 'when': yes, 'value': copy.deepcopy(value), 'value_type': shape,
                 'transition': copy.deepcopy(transition)},
                {'tag': 'ok_otherwise', 'when': None, 'value': copy.deepcopy(value), 'value_type': shape,
                 'transition': copy.deepcopy(transition)}]}


def application(envelope=True, default='mineral', collection='mineral-register'):
    pre = ROWS_A if envelope else STATE_A
    source = [] if envelope else ['specimens']
    requires = None if envelope else {'equals': [ref('pre', 'revision'), lit(1)]}
    transition = {'relations': [
        {'default_missing': {'source': source, 'target': ['specimens'],
                             'identity': 'accession', 'field': 'medium', 'value': lit(default)}},
        {'post_equals': {'field': 'revision', 'value': lit(2)}},
        {'post_equals': {'field': 'metadata', 'value': {'record': {'collection': lit(collection)}}}}]}
    migrate = operation('promote' if envelope else 'upgrade', pre, ENVELOPE_B,
                        {'cardinality': ref('pre', *source)}, 'integer', transition, requires)
    # Version-specific read operations are generated in this same application.
    legacy = operation('legacy', pre, pre, ref('pre', *source), ROWS_A,
                       {'preserve': True}, requires)
    current = operation('current', ENVELOPE_B, ENVELOPE_B, ref('pre', 'specimens'), ROWS_B,
                        {'preserve': True}, {'equals': [ref('pre', 'revision'), lit(2)]})
    inserts = {}
    for name, state, row_shape, path, guard, record in (
            ('legacy_insert', pre, ROW_A, None if envelope else 'specimens', requires,
             {'accession': 'M-4', 'designation': 'Olivine'}),
            ('current_insert', ENVELOPE_B, ROW_B, 'specimens', {'equals': [ref('pre', 'revision'), lit(2)]},
             {'accession': 'M-5', 'designation': 'Feldspar', 'medium': 'mineral'})):
        inserts[name] = operation(name, state, state, lit('inserted'), 'string',
            {'relations': [{'exact_frame': {'collection': path, 'identity': 'accession',
                                           'record': lit(record, row_shape)}}]}, guard)
    return copy.deepcopy({'id': 'specimen-register', 'state': {'versions': {'V1': pre, 'V2': ENVELOPE_B}},
                          'operations': {'legacy': legacy, 'migrate': migrate, 'current': current, **inserts}})


def initial(envelope=True):
    return rows() if envelope else {'revision': 1, 'specimens': rows(),
                                   'metadata': {'collection': 'legacy-register'}}


def capture(model, root, name):
    event, public, before, after = pipeline.observe(root, name, {})
    verdict = pipeline.challenge(model, root, event, public, before, after) if event else None
    return {'public': public, 'pre_bytes': before.decode(), 'post_bytes': after.decode(),
            'pre_digest': sha(before), 'post_digest': sha(after),
            'event': event, 'verdict': verdict}


def reseal(root):
    path = root / 'provenance.json'
    manifest = json.loads(path.read_bytes())
    manifest['artifact'] = sha((root / 'operation.py').read_bytes())
    manifest['generation'] = sha(canonical({k: v for k, v in manifest.items() if k != 'generation'}))
    path.write_bytes(canonical(manifest))


FAULTS = {
    'A': "post['specimens'] = [{**row, 'medium': 'wrong'} for row in post['specimens']]",
    'B': "post['specimens'] = [{**row, 'accession': 'wrong'} if i == 0 else row for i, row in enumerate(post['specimens'])]",
    'C': "post['revision'] = 1",
    'D': "post['metadata'] = {'collection': 'wrong-envelope'}",
    'E': "post['specimens'] = [row if i != 2 else {k: v for k, v in row.items() if k != 'medium'} for i, row in enumerate(post['specimens'])]",
}


def fault_artifact(root, name):
    artifact = root / 'operation.py'
    source = artifact.read_text(encoding='utf-8')
    start, end = source.index('def execute_1('), source.index('def execute_2(')
    body = source[start:end]
    body = body.replace('        return {', '        ' + FAULTS[name] + '\n        return {')
    source = source[:start] + body + source[end:]
    if name == 'E':
        # Disposable target descriptor fault permits the partial value to reach
        # durability. The source/CheckedPlan/verifier retain required V2 medium.
        descriptor_start = source.index("    'migrate': (")
        descriptor_end = source.index("    'current': (", descriptor_start)
        descriptor = source[descriptor_start:descriptor_end]
        descriptor = descriptor.replace("'medium': 'string'", "'medium': {'optional': 'string'}")
        source = source[:descriptor_start] + descriptor + source[descriptor_end:]
    artifact.write_bytes(source.encode())
    reseal(root)


def run_study():
    report = {'entry_point': 'benchmark.semantic.current_pipeline', 'candidate_core_constructs': 30,
              'lifecycles': {}, 'mutations': {}, 'faults': {}}
    for envelope in (False, True):
        model = application(envelope)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical(initial(envelope)))
            calls = [capture(model, root, name) for name in (
                'legacy', 'legacy_insert', 'legacy', 'migrate', 'current', 'current_insert', 'current')]
            rejected = [capture(model, root, name) for name in ('legacy', 'migrate', 'legacy_insert')]
            report['lifecycles']['envelope' if envelope else 'rows'] = {
                'source': model, 'manifest': manifest, 'calls': calls, 'unavailable_after': rejected}
    for key, args in {'default': {'default': 'crystal'},
                      'metadata': {'collection': 'curated-register'}}.items():
        model = application(**args)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical(initial()))
            report['mutations'][key] = capture(model, root, 'migrate')
    for name in FAULTS:
        model = application()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            (root / 'state.json').write_bytes(canonical(initial()))
            fault_artifact(root, name)
            report['faults'][name] = capture(model, root, 'migrate')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = run_study()
    data = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_bytes(data.encode())
        print(json.dumps({'lifecycles': len(report['lifecycles']), 'mutations': len(report['mutations']),
                          'faults': len(report['faults']), 'output': str(args.output)}))
    else:
        print(data)
