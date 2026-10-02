"""Prospective B01 compiler, independent subprocess observer, and case challenge."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import cardinality
from benchmark.semantic.typed_lowering_r5_12 import lower


TEMPLATE = Path(__file__).with_name('b01_target_r5_11.py')
OPERATIONS = ('create', 'list', 'list-high', 'list-overdue', 'complete', 'delete', 'migrate')
CONTRACT = {
    'identity': 'B01-v3-prospective', 'priority': ['LOW', 'NORMAL', 'HIGH', 'CRITICAL'],
    'operations': {
        'create': ['conditional_outcome', 'exact_selection', 'state_frame'],
        'list': ['complete_population', 'lexicographic_order', 'state_identity'],
        'list-high': ['exact_HIGH_selection', 'lexicographic_order', 'state_identity'],
        'list-overdue': ['exact_predicate_selection', 'lexicographic_order', 'state_identity'],
        'complete': ['conditional_outcome', 'keyed_target', 'state_frame'],
        'delete': ['conditional_outcome', 'keyed_target', 'state_frame'],
        'migrate': ['version_applicability', 'keyed_defaults', 'cardinality', 'state_frame'],
    },
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build(directory, variant='none'):
    """Generate a new artifact from a template; never touch the historical snapshot."""
    if variant not in ('none', 'wrong_count', 'false_post'):
        raise ValueError('unknown disposable variant')
    directory = Path(directory)
    template = TEMPLATE.read_bytes()
    contract_sha = sha(canonical(CONTRACT))
    generation = sha(canonical([sha(template), contract_sha, variant]))
    text = template.decode('utf-8').replace('__GENERATION__', repr(generation)).replace('__VARIANT__', repr(variant))
    app = directory / 'task_manager.py'
    app.write_text(text, encoding='utf-8')
    manifest = {'schema': 1, 'generation': generation, 'variant': variant,
                'template_sha256': sha(template), 'contract_sha256': contract_sha,
                'artifact_sha256': sha(app.read_bytes()),
                'operations': operation_map()}
    (directory / 'provenance.json').write_bytes(canonical(manifest))
    return app


def snapshot(path):
    raw = path.read_bytes() if path.exists() else None
    try:
        value = json.loads(raw) if raw is not None else None
    except (ValueError, UnicodeError):
        value = None
    return {'raw_sha256': sha(raw) if raw is not None else None, 'value': value}


def capture(app, cwd, command, arguments=()):
    """Caller owns argv and file readback; internal event is loaded only afterward."""
    cwd, app = Path(cwd), Path(app).resolve()
    invocation = uuid.uuid4().hex
    trace = cwd / ('event-' + invocation + '.json')
    before = snapshot(cwd / 'tasks.json')
    argv = [command, *arguments]
    completed = subprocess.run([sys.executable, str(app), *argv], cwd=cwd,
                               env={**os.environ, 'LYKOI_R5_11_TRACE': str(trace),
                                    'LYKOI_R5_11_INVOCATION': invocation,
                                    'PYTHONDONTWRITEBYTECODE': '1'},
                               capture_output=True, text=True, timeout=30, check=False)
    after = snapshot(cwd / 'tasks.json')
    public = {'command': command, 'argv': argv, 'invocation': invocation,
              'exit': completed.returncode, 'stdout': completed.stdout,
              'stderr': completed.stderr}
    event = json.loads(trace.read_text(encoding='utf-8')) if trace.exists() else None
    return event, public, before, after


def provenance(app):
    app = Path(app)
    try:
        meta = json.loads((app.parent / 'provenance.json').read_text(encoding='utf-8'))
        return (meta, meta['schema'] == 1 and meta['template_sha256'] == sha(TEMPLATE.read_bytes()) and
                meta['contract_sha256'] == sha(canonical(CONTRACT)) and
                meta['generation'] == sha(canonical([meta['template_sha256'], meta['contract_sha256'], meta['variant']])) and
                meta['artifact_sha256'] == sha(app.read_bytes()) and
                meta['operations'] == operation_map())
    except (KeyError, OSError, ValueError, TypeError):
        return None, False


def operation_map():
    return {op: {'semantic': op, 'boundary': 'unit_' + op,
                 'persistence': 'store_tasks',
                 'contract_sha256': sha(canonical(CONTRACT['operations'][op]))}
            for op in OPERATIONS}


def rows(state):
    return [] if state is None else state['records'] if isinstance(state, dict) else state


def ordered(items):
    return sorted(items, key=lambda r: (r['created_at'], r['id']))


def keyed(items):
    return {r['id']: r for r in items}


def _read_contract(priority=None):
    """Prospective B01 adapter data; the evaluator contains no task vocabulary."""
    row = {'record': {'id': 'string', 'title': 'string', 'description': 'string',
                      'status': 'string', 'priority': 'string', 'created_at': 'string',
                      'due_date': {'nullable': 'string'}}}
    source = {'ref': ['pre']}
    if priority is not None:
        source = {'select': {'source': source, 'where': {'equals': [
            {'ref': ['item', 'priority']}, {'literal': {'type': 'string', 'value': priority}}]}}}
    return {'input': {'record': {}}, 'state': {'sequence': row},
            'outcomes': {'success': {'value': {'sequence': row}, 'constraints': [
                {'equals': [{'ref': ['post']}, {'ref': ['pre']}]},
                {'equals': [{'ref': ['outcome']},
                            {'order': {'source': source, 'keys': ['created_at', 'id']}}]}
            ]}}}


def conforms(command, inputs, outcome, before, after, raw_before, raw_after):
    """Compose existing typed equality, exact selection, ordering, frames and #30.

    Invalid fixtures are outside this selected valid-state case checker. A read-only
    or failed operation must also preserve the independently observed raw endpoint.
    """
    kind, value = outcome['kind'], outcome['value']
    if kind == 'error':
        if raw_before != raw_after:
            return False
        if command == 'create':
            return value == {'error': 'invalid_title'} and not inputs['title'].strip() or (
                value == {'error': 'invalid_due_date'} and inputs['due_date'] is not None)
        if command in ('complete', 'delete'):
            old = keyed(rows(before)).get(inputs['id'])
            return (value == {'error': 'task_not_found'} and old is None or
                    command == 'complete' and value == {'error': 'invalid_transition'} and
                    old is not None and old['status'] == 'completed')
        return False
    if kind != 'success':
        return False
    old, new = rows(before), rows(after)
    if command == 'create':
        if not isinstance(value, dict) or set(value) != {'id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date'}:
            return False
        try:
            from datetime import datetime
            stamp = datetime.fromisoformat(value['created_at'].replace('Z', '+00:00'))
            timestamp_valid = value['created_at'].endswith('Z') and stamp.utcoffset().total_seconds() == 0
        except (ValueError, AttributeError, TypeError):
            return False
        return (timestamp_valid and bool(value['id'].strip()) and value['id'] not in keyed(old) and
                value['title'] == inputs['title'] and value['description'] == inputs['description'] and
                value['priority'] == (inputs['priority'] or 'NORMAL') and value['status'] == 'pending' and
                value['due_date'] == inputs['due_date'] and len(new) == len(old) + 1 and
                keyed(new).get(value['id']) == value and
                {k: v for k, v in keyed(new).items() if k != value['id']} == keyed(old))
    if command in ('list', 'list-high', 'list-overdue'):
        if raw_before != raw_after:
            return False
        if command in ('list', 'list-high'):
            return lower(_read_contract('HIGH' if command == 'list-high' else None))(
                {}, old, outcome, new)
        selected = old
        if command == 'list-overdue':
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            selected = [r for r in old if r['status'] == 'pending' and r['due_date'] is not None and
                        datetime.fromisoformat(r['due_date'].replace('Z', '+00:00')) < now]
        return value == ordered(selected)
    if command in ('complete', 'delete'):
        target = keyed(old).get(inputs['id'])
        if target is None:
            return False
        if command == 'complete':
            expected = {**target, 'status': 'completed'}
            return (target['status'] == 'pending' and value == expected and len(new) == len(old) and
                    keyed(new).get(inputs['id']) == expected and
                    {k: v for k, v in keyed(new).items() if k != inputs['id']} ==
                    {k: v for k, v in keyed(old).items() if k != inputs['id']})
        return value == target and keyed(new) == {k: v for k, v in keyed(old).items() if k != inputs['id']}
    if command == 'migrate':
        legacy = isinstance(before, list) or isinstance(before, dict) and before.get('schema_version') == 2
        candidates = old if legacy else []
        if not isinstance(value, dict) or set(value) != {'migrated'} or type(value['migrated']) is not int:
            return False
        # #30: count *all* applicable legacy rows, including rows already prioritized.
        if not cardinality.evaluate({'element': 'string', 'fields': {'migrated': 'integer'},
                                     'optional': []}, [r['id'] for r in candidates], value, 'migrated'):
            return False
        if not legacy:
            return raw_before == raw_after
        version = 1 if isinstance(before, list) else 2
        expected = [{**r, **({'priority': 'NORMAL'} if version == 1 else {}), 'due_date': None} for r in old]
        return isinstance(after, dict) and after.get('schema_version') == 3 and keyed(new) == keyed(expected) and len(new) == len(old)
    return False


def challenge(app, captured):
    event, public, before, after = captured
    meta, valid = provenance(app)
    verdict = {'provenance_valid': valid, 'grounding': 'GROUNDING_FAILED',
               'conformance': None}
    if not valid:
        return verdict
    try:
        visible = json.loads(public['stdout'] if public['exit'] == 0 else public['stderr'])
        success = public['exit'] == 0 and not public['stderr'] and event['outcome']['kind'] == 'success'
        failure = public['exit'] == 1 and not public['stdout'] and event['outcome']['kind'] == 'error'
        input_args = event['input']
        expected_argv = [public['command']]
        if public['command'] == 'create':
            for field, flag in (('title', '--title'), ('description', '--description'),
                                ('priority', '--priority'), ('due_date', '--due-date')):
                if input_args[field] is not None:
                    expected_argv.extend((flag, input_args[field]))
        if public['command'] in ('complete', 'delete'):
            expected_argv.extend(('--id', input_args['id']))
        grounded = (success or failure) and event['operation'] == public['command'] and public['argv'] == expected_argv and (
            event['boundary'] == meta['operations'][public['command']]['boundary'] and
            event['persistence'] == 'store_tasks' and event['generation'] == meta['generation'] and
            event['invocation'] == public['invocation'] and event['pre'] == before['value'] and
            event['post'] == after['value'] and event['outcome']['value'] == visible and
            type(event['attempted_write']) is bool and
            (event['attempted_write'] or before['raw_sha256'] == after['raw_sha256']))
    except (KeyError, TypeError, ValueError, AttributeError):
        grounded = False
    if grounded:
        verdict['grounding'] = 'GROUNDED'
        try:
            verdict['conformance'] = ('CONFORMANT' if conforms(public['command'], input_args,
                event['outcome'], before['value'], after['value'], before['raw_sha256'], after['raw_sha256'])
                else 'NON_CONFORMANT')
        except (KeyError, TypeError, ValueError, AttributeError):
            verdict['conformance'] = 'NON_CONFORMANT'
    return verdict
