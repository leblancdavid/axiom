"""Prospective R5.7 compiler/runner/challenge; not the frozen v0.3 backend."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import binding, conformance, contracts


OPERATION = 'seal_vials'
BOUNDARY = 'unit_0'
PERSISTENCE = 'store_0'
SLOTS = {'input.rows': 'input', 'pre.records': 'pre',
         'result': 'outcome', 'post.records': 'post'}
TEMPLATE = Path(__file__).with_name('grounding_target_r5_7.py')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contract():
    def ref(name):
        return {'ref': name}

    def eq(left, right):
        return {'equals': [left, right]}

    complete = {'default_missing': [ref('pre.records'), ref('pre.records')]}
    failure = {'and': [eq(ref('result.kind'), {'literal': 'error'}),
                       eq(ref('post.records'), ref('pre.records'))]}
    success = {'and': [eq(ref('result.kind'), {'literal': 'success'}),
                       {'default_missing': [ref('pre.records'), ref('post.records')]}]}
    def implies(premise, conclusion):
        return {'not': {'and': [premise, {'not': conclusion}]}}

    value = {'operation': OPERATION,
             'schema': {'record': {'id': 'string', 'label': 'string', 'sealed': 'boolean'},
                         'default': {'kind': 'default_missing', 'identity': 'id',
                                     'field': 'sealed', 'value': True},
                         'outcome': {'variants': ['success', 'error'], 'value': 'records'}},
              'checks': [eq(ref('input.rows'), ref('pre.records')),
                         eq(ref('result.value'), ref('post.records')),
                         implies(complete, failure),
                         implies({'not': complete}, success)]}
    return contracts.validate(value)


def mapping():
    value = {'operation': OPERATION, 'boundary': BOUNDARY, 'slots': SLOTS.copy()}
    return binding.validate(contract(), value)


def compile_target(directory, fault='none'):
    """Compile a synthetic operation into an isolated executable and manifest."""
    if fault not in {'none', 'wrong_result', 'wrong_state', 'false_post',
                     'false_input', 'wrong_identity', 'failure_write',
                     'wrong_failure_kind'}:
        raise ValueError('unknown prototype variant')
    directory = Path(directory)
    source_bytes = TEMPLATE.read_bytes()
    source = source_bytes.decode('utf-8')
    contract_hash = digest(canonical(contract()))
    binding_hash = digest(canonical(mapping()))
    generation = digest(canonical([contract_hash, binding_hash, digest(source_bytes), fault]))
    substitutions = {'__OPERATION__': OPERATION, '__BOUNDARY__': BOUNDARY,
                     '__PERSISTENCE__': PERSISTENCE, '__PROVENANCE__': generation,
                     '__FAULT__': fault}
    for token, value in substitutions.items():
        source = source.replace(token, repr(value))
    artifact = directory / 'operation.py'
    artifact.write_text(source, encoding='utf-8')
    provenance = {'schema': 1, 'operation': OPERATION, 'boundary': BOUNDARY,
                  'persistence': PERSISTENCE, 'generation': generation,
                  'contract_sha256': contract_hash, 'binding_sha256': binding_hash,
                  'template_sha256': digest(source_bytes),
                  'artifact_sha256': digest(artifact.read_bytes()), 'variant': fault}
    (directory / 'provenance.json').write_bytes(canonical(provenance))
    return provenance


def inspect_state(path):
    raw = Path(path).read_bytes()
    return {'sha256': digest(raw), 'rows': json.loads(raw)}


def run_case(directory, rows):
    """Independent subprocess caller: no access to internal event during capture."""
    directory = Path(directory)
    state = directory / 'state.json'
    trace = directory / 'trace.json'
    invocation = uuid.uuid4().hex
    before = inspect_state(state)
    payload = canonical(rows).decode('utf-8')
    completed = subprocess.run([sys.executable, str(directory / 'operation.py'),
                                str(state), str(trace), invocation, payload],
                               capture_output=True, text=True, check=False)
    after = inspect_state(state)
    public = {'entry': 'operation.py', 'invocation': invocation, 'input': rows,
              'exit': completed.returncode, 'stdout': completed.stdout,
              'stderr': completed.stderr}
    internal = json.loads(trace.read_text(encoding='utf-8')) if trace.exists() else None
    return internal, public, before, after


def challenge(directory, internal, public, before, after):
    """Reject divergence before R5.5 ever sees a record; retain separate statuses."""
    directory = Path(directory)
    provenance = json.loads((directory / 'provenance.json').read_text(encoding='utf-8'))
    expected = {'schema': 1, 'operation': OPERATION, 'boundary': BOUNDARY,
                'persistence': PERSISTENCE, 'contract_sha256': digest(canonical(contract())),
                'binding_sha256': digest(canonical(mapping())),
                'template_sha256': digest(TEMPLATE.read_bytes())}
    provenance_valid = (all(provenance.get(k) == v for k, v in expected.items()) and
                        provenance.get('artifact_sha256') == digest((directory / 'operation.py').read_bytes()) and
                        provenance.get('generation') == digest(canonical([
                            expected['contract_sha256'], expected['binding_sha256'],
                            expected['template_sha256'], provenance.get('variant')])))
    result = {'provenance_valid': provenance_valid, 'grounding_challenge_passed': False,
              'contract_conformant': None, 'reason': 'provenance_mismatch'}
    if not provenance_valid:
        return result
    try:
        visible = json.loads(public['stdout'])
        consistent = (internal is not None and public['entry'] == 'operation.py' and
                      public['exit'] == 0 and public['stderr'] == '' and
                      set(visible) == {'classification', 'result'} and
                      visible['classification'] in ('success', 'error') and
                      internal['operation'] == OPERATION and internal['boundary'] == BOUNDARY and
                      internal['persistence'] == PERSISTENCE and
                      internal['provenance'] == provenance['generation'] and
                      internal['invocation'] == public['invocation'] and
                      internal['classification'] == visible['classification'] and
                      internal['facts']['input'] == public['input'] and
                       internal['facts']['outcome'] == visible['result'] and
                      internal['facts']['pre'] == before['rows'] and
                      internal['facts']['post'] == after['rows'] and
                      # A failure path with a write is a behavior failure, not
                      # necessarily an observation failure: endpoints remain grounded.
                      type(internal['attempted_write']) is bool and
                      (internal['attempted_write'] or before['sha256'] == after['sha256']))
    except (KeyError, TypeError, ValueError):
        consistent = False
    if not consistent:
        result['reason'] = 'grounding_mismatch'
        return result
    result['grounding_challenge_passed'] = True
    record = {key: internal[key] for key in ('source', 'boundary', 'invocation', 'sequence', 'facts')}
    # The challenged public envelope supplies the typed outcome to the abstract
    # slot; classification is not supplied by an unchallenged internal claim.
    record['facts'] = {**record['facts'], 'outcome':
                       {'kind': visible['classification'], 'value': visible['result']}}
    try:
        verdict = conformance.evaluate(contract(), mapping(), record)
        result['contract_conformant'] = verdict['conforms']
        result['reason'] = 'conformant' if result['contract_conformant'] else 'semantic_nonconformance'
    except (KeyError, TypeError, ValueError) as exc:
        result['contract_conformant'] = False
        result['reason'] = 'invalid_conformance_values'
    return result
