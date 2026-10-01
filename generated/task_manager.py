# THIS FILE IS GENERATED.
# DO NOT MODIFY DIRECTLY.
# MODIFY THE AIR REPRESENTATION INSTEAD.
"""Python backend template. Emitted into a self-contained generated application."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from uuid import uuid4


SPEC = json.loads('{"air_version":"0.1","application":{"id":"app_tasks","name":"task_manager"},"behaviors":[{"assignments":[{"field":"field_id","id":"cap_ids","source":"capability"},{"field":"field_title","id":"arg_title","source":"input"},{"field":"field_description","id":"arg_description","source":"input"},{"field":"field_status","source":"literal","value":"pending"},{"field":"field_created_at","id":"cap_clock","source":"capability"}],"conditions":[{"failure":"invalid_title","input":"arg_title","kind":"nonblank_input"}],"dependencies":["state_tasks","cap_store","cap_clock","cap_ids"],"effects":["file_read","file_write","clock_read","random_id"],"failures":["invalid_title","id_collision","invalid_state","persistence_failure"],"guarantees":[{"field":"field_status","kind":"result_field_equals","value":"pending"},{"kind":"result_in_state","state":"state_tasks"}],"id":"fn_create","inputs":[{"id":"arg_title","name":"title","type":"prim:string"},{"id":"arg_description","name":"description","type":"prim:string"}],"kind":"create","name":"create_task","output":"type_task","reads":["state_tasks"],"state":"state_tasks","writes":["state_tasks"]},{"assignments":[],"conditions":[],"dependencies":["state_tasks","cap_store"],"effects":["file_read"],"failures":["invalid_state","persistence_failure"],"guarantees":[{"kind":"result_equals_state_sorted","state":"state_tasks"}],"id":"fn_list","inputs":[],"kind":"list","name":"list_tasks","order_by":["field_created_at","field_id"],"output":"type_task_list","reads":["state_tasks"],"state":"state_tasks","writes":[]},{"assignments":[{"field":"field_status","source":"literal","value":"completed"}],"conditions":[{"failure":"task_not_found","kind":"record_exists"},{"failure":"invalid_transition","field":"field_status","kind":"record_field_equals","value":"pending"}],"dependencies":["state_tasks","cap_store"],"effects":["file_read","file_write"],"failures":["task_not_found","invalid_transition","invalid_state","persistence_failure"],"guarantees":[{"field":"field_status","kind":"result_field_equals","value":"completed"},{"kind":"result_in_state","state":"state_tasks"}],"id":"fn_complete","inputs":[{"id":"arg_complete_id","name":"id","type":"prim:string"}],"kind":"update","lookup":{"field":"field_id","input":"arg_complete_id"},"name":"complete_task","output":"type_task","reads":["state_tasks"],"state":"state_tasks","writes":["state_tasks"]},{"assignments":[],"conditions":[{"failure":"task_not_found","kind":"record_exists"}],"dependencies":["state_tasks","cap_store"],"effects":["file_read","file_write"],"failures":["task_not_found","invalid_state","persistence_failure"],"guarantees":[{"kind":"result_id_absent_from_state","state":"state_tasks"}],"id":"fn_delete","inputs":[{"id":"arg_delete_id","name":"id","type":"prim:string"}],"kind":"delete","lookup":{"field":"field_id","input":"arg_delete_id"},"name":"delete_task","output":"type_task","reads":["state_tasks"],"state":"state_tasks","writes":["state_tasks"]}],"capabilities":[{"id":"cap_store","kind":"json_file","missing_file":"empty_collection","path":"tasks.json"},{"id":"cap_clock","kind":"utc_clock"},{"id":"cap_ids","kind":"uuid_v4"}],"commands":[{"arguments":[{"flag":"--title","input":"arg_title","required":true},{"flag":"--description","input":"arg_description","required":true}],"behavior":"fn_create","id":"cmd_create","token":"create"},{"arguments":[],"behavior":"fn_list","id":"cmd_list","token":"list"},{"arguments":[{"flag":"--id","input":"arg_complete_id","required":true}],"behavior":"fn_complete","id":"cmd_complete","token":"complete"},{"arguments":[{"flag":"--id","input":"arg_delete_id","required":true}],"behavior":"fn_delete","id":"cmd_delete","token":"delete"}],"invariants":[{"field":"field_id","id":"inv_unique_ids","kind":"unique_field","state":"state_tasks"},{"field_rules":[{"field":"field_id","kind":"nonblank"},{"field":"field_title","kind":"nonblank"},{"field":"field_created_at","kind":"timestamp_utc"}],"id":"inv_valid_tasks","kind":"all_records_valid","state":"state_tasks"}],"state":[{"id":"state_tasks","invariants":["inv_unique_ids","inv_valid_tasks"],"key_field":"field_id","name":"tasks","storage":"cap_store","type":"type_task_list"}],"types":[{"id":"type_status","kind":"enum","name":"TaskStatus","values":["pending","completed"]},{"fields":[{"id":"field_id","name":"id","type":"prim:string"},{"id":"field_title","name":"title","type":"prim:string"},{"id":"field_description","name":"description","type":"prim:string"},{"id":"field_status","name":"status","type":"type_status"},{"id":"field_created_at","name":"created_at","type":"prim:timestamp"}],"id":"type_task","kind":"record","name":"Task"},{"id":"type_task_list","item_type":"type_task","kind":"list","name":"TaskList"}]}')


class Failure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def by_id(group, eid):
    return next(item for item in SPEC[group] if item["id"] == eid)


def field_name(record_type, field_id):
    return next(f["name"] for f in record_type["fields"] if f["id"] == field_id)


def state_layout(state):
    list_type = by_id("types", state["type"])
    record_type = by_id("types", list_type["item_type"])
    return record_type, Path(by_id("capabilities", state["storage"])["path"])


def utc_timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0
    except ValueError:
        return False


def valid_state(records, state, record_type):
    if not isinstance(records, list):
        return False
    fields = record_type["fields"]
    for record in records:
        if not isinstance(record, dict) or set(record) != {f["name"] for f in fields}:
            return False
        for f in fields:
            value = record[f["name"]]
            typ = f["type"]
            if typ in ("prim:string", "prim:timestamp"):
                if not isinstance(value, str) or (typ == "prim:timestamp" and not utc_timestamp(value)):
                    return False
            elif value not in by_id("types", typ)["values"]:
                return False
    for iid in state["invariants"]:
        inv = by_id("invariants", iid)
        if inv["kind"] == "unique_field":
            name = field_name(record_type, inv["field"])
            if len({r[name] for r in records}) != len(records):
                return False
        elif inv["kind"] == "all_records_valid":
            for rule in inv["field_rules"]:
                name = field_name(record_type, rule["field"])
                if rule["kind"] == "nonblank" and any(not r[name].strip() for r in records):
                    return False
                if rule["kind"] == "timestamp_utc" and any(not utc_timestamp(r[name]) for r in records):
                    return False
    return True


def read_state(state, record_type, path):
    try:
        with path.open(encoding="utf-8") as source:
            records = json.load(source)
    except FileNotFoundError:
        if path.exists():
            raise Failure("persistence_failure")
        records = []
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Failure("invalid_state") from exc
    except OSError as exc:
        raise Failure("persistence_failure") from exc
    if not valid_state(records, state, record_type):
        raise Failure("invalid_state")
    return records


def write_state(records, state, record_type, path):
    if not valid_state(records, state, record_type):
        raise Failure("invalid_state")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".air-", suffix=".tmp", delete=False) as dest:
            temp_path = Path(dest.name)
            json.dump(records, dest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            dest.write("\n")
        os.replace(temp_path, path)
    except OSError as exc:
        raise Failure("persistence_failure") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def value_of(assignment, inputs):
    if assignment["source"] == "literal":
        return assignment["value"]
    if assignment["source"] == "input":
        return inputs[assignment["id"]]
    kind = by_id("capabilities", assignment["id"])["kind"]
    if kind == "uuid_v4":
        return str(uuid4())
    if kind == "utc_clock":
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    raise AssertionError("unvalidated capability")


def sorted_records(records, behavior, record_type):
    keys = [field_name(record_type, fid) for fid in behavior["order_by"]]
    return sorted(records, key=lambda record: tuple(record[k] for k in keys))


def check_guarantees(behavior, result, records, state, record_type):
    key = field_name(record_type, state["key_field"])
    for guarantee in behavior["guarantees"]:
        kind = guarantee["kind"]
        if kind == "result_field_equals":
            ok = result[field_name(record_type, guarantee["field"])] == guarantee["value"]
        elif kind == "result_in_state":
            ok = any(r[key] == result[key] and r == result for r in records)
        elif kind == "result_id_absent_from_state":
            ok = all(r[key] != result[key] for r in records)
        elif kind == "result_equals_state_sorted":
            ok = result == sorted_records(records, behavior, record_type)
        else:
            raise AssertionError("unvalidated guarantee")
        if not ok:
            raise AssertionError(f"AIR guarantee violated: {behavior['id']} {kind}")


def execute(behavior, inputs):
    state = by_id("state", behavior["state"])
    record_type, path = state_layout(state)
    records = read_state(state, record_type, path)
    key = field_name(record_type, state["key_field"])
    target = None
    if "lookup" in behavior:
        lookup = behavior["lookup"]
        target = next((r for r in records if r[key] == inputs[lookup["input"]]), None)
    for condition in behavior["conditions"]:
        kind = condition["kind"]
        if kind == "nonblank_input":
            ok = bool(inputs[condition["input"]].strip())
        elif kind == "record_exists":
            ok = target is not None
        elif kind == "record_field_equals":
            ok = target[field_name(record_type, condition["field"])] == condition["value"]
        else:
            raise AssertionError("unvalidated condition")
        if not ok:
            raise Failure(condition["failure"])
    kind = behavior["kind"]
    if kind == "list":
        result = sorted_records(records, behavior, record_type)
    elif kind == "create":
        result = {field_name(record_type, a["field"]): value_of(a, inputs) for a in behavior["assignments"]}
        if any(r[key] == result[key] for r in records):
            raise Failure("id_collision")
        records.append(result)
    elif kind == "update":
        for a in behavior["assignments"]:
            target[field_name(record_type, a["field"])] = value_of(a, inputs)
        result = target.copy()
    elif kind == "delete":
        result = target.copy()
        records.remove(target)
    else:
        raise AssertionError("unvalidated behavior")
    if not valid_state(records, state, record_type):
        raise Failure("invalid_state")
    check_guarantees(behavior, result, records, state, record_type)
    if kind != "list":
        write_state(records, state, record_type, path)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog=SPEC["application"]["name"])
    commands = parser.add_subparsers(dest="command", required=True)
    for command in SPEC["commands"]:
        sub = commands.add_parser(command["token"])
        for arg in command["arguments"]:
            sub.add_argument(arg["flag"], required=arg["required"])
    parsed = parser.parse_args(argv)
    command = next(c for c in SPEC["commands"] if c["token"] == parsed.command)
    behavior = by_id("behaviors", command["behavior"])
    inputs = {a["input"]: getattr(parsed, a["flag"][2:].replace("-", "_")) for a in command["arguments"]}
    try:
        result = execute(behavior, inputs)
    except Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
