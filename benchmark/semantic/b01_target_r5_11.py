"""R5.11 generated target template. Substituted constants are compiler metadata."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from uuid import uuid4


GENERATION = __GENERATION__
VARIANT = __VARIANT__
STORE = Path('tasks.json')
FIELDS = {'id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date'}
PRIORITIES = {'LOW', 'NORMAL', 'HIGH', 'CRITICAL'}


class Failure(Exception):
    pass


def utc(value):
    if type(value) is not str or not value.endswith('Z'):
        raise ValueError('UTC required')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
        raise ValueError('UTC required')
    return stamp


def checked(rows):
    if type(rows) is not list:
        raise Failure('invalid_state')
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != FIELDS:
            raise Failure('invalid_state')
        if (type(row['id']) is not str or not row['id'].strip() or row['id'] in seen or
                type(row['title']) is not str or not row['title'].strip() or
                type(row['description']) is not str or
                type(row['status']) is not str or row['status'] not in ('pending', 'completed') or
                type(row['priority']) is not str or row['priority'] not in PRIORITIES):
            raise Failure('invalid_state')
        seen.add(row['id'])
        try:
            utc(row['created_at'])
            if row['due_date'] is not None:
                utc(row['due_date'])
        except (ValueError, TypeError, OverflowError) as exc:
            raise Failure('invalid_state') from exc
    return rows


def read():
    if not STORE.exists():
        return None
    try:
        return json.loads(STORE.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as exc:
        raise Failure('invalid_state') from exc


def current():
    data = read()
    if data is None:
        return []
    if type(data) is not dict:
        if type(data) is list:
            raise Failure('migration_required')
        raise Failure('invalid_state')
    if data.get('schema_version') in (1, 2):
        raise Failure('migration_required')
    if set(data) != {'schema_version', 'records'} or type(data['schema_version']) is not int or data['schema_version'] != 3:
        raise Failure('invalid_state')
    return checked(data['records'])


def commit(rows):
    checked(rows)
    STORE.write_text(json.dumps({'schema_version': 3, 'records': rows}, sort_keys=True,
                                ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')


def ordered(rows):
    return sorted(rows, key=lambda row: (row['created_at'], row['id']))


def execute(command, args):
    if command == 'migrate':
        data = read()
        if data is None:
            return {'migrated': 0}, False
        if type(data) is dict and data.get('schema_version') == 3:
            current()
            return {'migrated': 0}, False
        if type(data) is list:
            version, rows = 1, data
        elif type(data) is dict and set(data) == {'schema_version', 'records'} and type(data['schema_version']) is int and data['schema_version'] == 2:
            version, rows = 2, data['records']
        else:
            raise Failure('invalid_state')
        if type(rows) is not list:
            raise Failure('invalid_state')
        missing = {'priority', 'due_date'} if version == 1 else {'due_date'}
        converted = []
        for row in rows:
            if type(row) is not dict or set(row) != FIELDS - missing:
                raise Failure('invalid_state')
            converted.append({**row, **({'priority': 'NORMAL'} if version == 1 else {}), 'due_date': None})
        commit(converted)
        count = len(rows) + (1 if VARIANT == 'wrong_count' else 0)
        return {'migrated': count}, True

    rows = current()
    if command == 'create':
        if not args.title.strip():
            raise Failure('invalid_title')
        if args.due_date is not None:
            try:
                utc(args.due_date)
            except (ValueError, TypeError, OverflowError) as exc:
                raise Failure('invalid_due_date') from exc
        identifier = str(uuid4())
        if any(r['id'] == identifier for r in rows):
            raise Failure('id_collision')
        task = {'id': identifier, 'title': args.title, 'description': args.description,
                'status': 'pending', 'priority': args.priority or 'NORMAL',
                'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'due_date': args.due_date}
        commit([*rows, task])
        return task, True
    if command in ('list', 'list-high', 'list-overdue'):
        if command == 'list-high':
            rows = [r for r in rows if r['priority'] == 'HIGH']
        if command == 'list-overdue':
            now = datetime.now(timezone.utc)
            rows = [r for r in rows if r['status'] == 'pending' and r['due_date'] is not None
                    and utc(r['due_date']) < now]
        return ordered(rows), False
    target = next((r for r in rows if r['id'] == args.id), None)
    if target is None:
        raise Failure('task_not_found')
    if command == 'complete':
        if target['status'] != 'pending':
            raise Failure('invalid_transition')
        changed = {**target, 'status': 'completed'}
        commit([changed if r['id'] == args.id else r for r in rows])
        return changed, True
    commit([r for r in rows if r['id'] != args.id])
    return target, True


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create')
    create.add_argument('--title', required=True)
    create.add_argument('--description', required=True)
    create.add_argument('--priority', choices=sorted(PRIORITIES))
    create.add_argument('--due-date')
    for name in ('list', 'list-high', 'list-overdue', 'migrate'):
        commands.add_parser(name)
    for name in ('complete', 'delete'):
        commands.add_parser(name).add_argument('--id', required=True)
    args = parser.parse_args()
    before = read_bytes()
    try:
        value, wrote = execute(args.command, args)
        outcome = {'kind': 'success', 'value': value}
        exit_code = 0
    except Failure as exc:
        outcome = {'kind': 'error', 'value': {'error': str(exc)}}
        wrote = False
        exit_code = 1
    after = read_bytes()
    trace = os.environ.get('LYKOI_R5_11_TRACE')
    if trace:
        pre = json.loads(before) if before is not None and valid_json(before) else None
        post = json.loads(after) if after is not None and valid_json(after) else None
        if VARIANT == 'false_post':
            post = pre
        event = {'operation': args.command, 'boundary': 'unit_' + args.command,
                 'persistence': 'store_tasks', 'generation': GENERATION,
                 'invocation': os.environ.get('LYKOI_R5_11_INVOCATION'),
                 'input': vars(args), 'pre': pre, 'post': post, 'outcome': outcome,
                 'attempted_write': wrote}
        Path(trace).write_text(json.dumps(event, sort_keys=True), encoding='utf-8')
    print(json.dumps(outcome['value'], sort_keys=True, ensure_ascii=False),
          file=sys.stderr if exit_code else sys.stdout)
    return exit_code


def read_bytes():
    return STORE.read_bytes() if STORE.exists() else None


def valid_json(raw):
    try:
        json.loads(raw)
        return True
    except (ValueError, UnicodeError):
        return False


if __name__ == '__main__':
    sys.exit(main())
