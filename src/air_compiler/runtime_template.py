"""Python backend template. Emitted into a self-contained generated application."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from uuid import uuid4


SPEC = {}  # AXIOM_SPEC_INSERTION_POINT


class Failure(Exception):
    def __init__(self, code):
        self.code = next((e["code"] for e in SPEC.get("errors", []) if e["id"] == code), code)
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
            if value is None and f.get("nullable", False):
                continue
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
                if rule["kind"] == "timestamp_utc" and any(r[name] is not None and not utc_timestamp(r[name]) for r in records):
                    return False
    return True


def decode_state(payload, state):
    if "schema_version" not in state:
        return payload
    if state["schema_version"] == 1 and isinstance(payload, list):
        return payload
    if not isinstance(payload, dict) or payload.get("schema_version") != state["schema_version"]:
        raise Failure("migration_required")
    if set(payload) != {"schema_version", "records"}:
        raise Failure("invalid_state")
    return payload.get("records")


def read_state(state, record_type, path):
    try:
        with path.open(encoding="utf-8") as source:
            records = decode_state(json.load(source), state)
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
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".axiom-", suffix=".tmp", delete=False) as dest:
            temp_path = Path(dest.name)
            payload = {"schema_version": state["schema_version"], "records": records} if "schema_version" in state and state["schema_version"] > 1 else records
            json.dump(payload, dest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
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
    if assignment["source"] == "input_default":
        return inputs.get(assignment["id"], assignment["value"])
    kind = by_id("capabilities", assignment["id"])["kind"]
    if kind == "uuid_v4":
        return str(uuid4())
    if kind == "utc_clock":
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    raise AssertionError("unvalidated capability")


def sorted_records(records, behavior, record_type):
    keys = [field_name(record_type, fid) for fid in behavior["order_by"]]
    return sorted(records, key=lambda record: tuple(record[k] for k in keys))


def clock_value():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def select_records(records, behavior, record_type, now):
    if "filter" not in behavior:
        return records
    spec = behavior["filter"]
    predicates = spec["predicates"] if spec["kind"] == "all" else [spec]
    def matches(record):
        for predicate in predicates:
            value = record[field_name(record_type, predicate["field"])]
            if predicate["kind"] == "field_equals":
                ok = value == predicate["value"]
            elif predicate["kind"] == "field_before_clock":
                ok = value is not None and datetime.fromisoformat(value.replace("Z", "+00:00")) < datetime.fromisoformat(now.replace("Z", "+00:00"))
            else:
                raise AssertionError("unvalidated predicate")
            if not ok:
                return False
        return True
    return [record for record in records if matches(record)]


def check_guarantees(behavior, result, records, state, record_type, inputs, now=None):
    key = field_name(record_type, state["key_field"])
    for guarantee in behavior["guarantees"]:
        kind = guarantee["kind"]
        if kind == "result_field_equals":
            ok = result[field_name(record_type, guarantee["field"])] == guarantee["value"]
        elif kind == "result_field_equals_assignment":
            assignment = next(a for a in behavior["assignments"] if a["field"] == guarantee["field"])
            ok = result[field_name(record_type, guarantee["field"])] == value_of(assignment, inputs)
        elif kind == "result_in_state":
            ok = any(r[key] == result[key] and r == result for r in records)
        elif kind == "result_id_absent_from_state":
            ok = all(r[key] != result[key] for r in records)
        elif kind == "result_equals_state_sorted":
            selection = select_records(records, behavior, record_type, now)
            ok = result == sorted_records(selection, behavior, record_type)
        else:
            raise AssertionError("unvalidated guarantee")
        if not ok:
            raise AssertionError(f"Axiom guarantee violated: {behavior['id']} {kind}")


def execute(behavior, inputs, clock=None):
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
        elif kind == "timestamp_input":
            value = inputs.get(condition["input"])
            ok = value is None or utc_timestamp(value)
        else:
            raise AssertionError("unvalidated condition")
        if not ok:
            raise Failure(condition["failure"])
    kind = behavior["kind"]
    now = (clock or clock_value)() if "clock_read" in behavior["effects"] and kind == "list" else None
    if kind == "list":
        selection = select_records(records, behavior, record_type, now)
        result = sorted_records(selection, behavior, record_type)
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
    check_guarantees(behavior, result, records, state, record_type, inputs, now)
    if kind != "list":
        write_state(records, state, record_type, path)
    return result


def migrate():
    migrations = sorted(SPEC["migrations"], key=lambda item: item["from_version"])
    state = by_id("state", migrations[0]["state"])
    record_type, path = state_layout(state)
    try:
        with path.open(encoding="utf-8") as source:
            payload = json.load(source)
    except FileNotFoundError:
        return {"migrated": 0}
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Failure("invalid_state") from exc
    except OSError as exc:
        raise Failure("persistence_failure") from exc
    if isinstance(payload, dict) and payload.get("schema_version") == state["schema_version"]:
        if set(payload) != {"schema_version", "records"}:
            raise Failure("invalid_state")
        if not valid_state(payload.get("records"), state, record_type):
            raise Failure("invalid_state")
        return {"migrated": 0}
    version = 1 if isinstance(payload, list) else payload.get("schema_version") if isinstance(payload, dict) else None
    records = payload if version == 1 else payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise Failure("invalid_state")
    for migration in migrations:
        if migration["from_version"] != version:
            continue
        added = {field_name(record_type, a["field"]): a["value"] for a in migration["add_fields"]}
        remaining = {field_name(record_type, a["field"]) for step in migrations if step["from_version"] >= version for a in step["add_fields"]}
        old_fields = {f["name"] for f in record_type["fields"]} - remaining
        if any(not isinstance(r, dict) or set(r) != old_fields for r in records):
            raise Failure("invalid_state")
        records = [{**r, **added} for r in records]
        version = migration["to_version"]
    if version != state["schema_version"] or not valid_state(records, state, record_type):
        raise Failure("invalid_state")
    write_state(records, state, record_type, path)
    return {"migrated": len(records)}


def main(argv=None):
    parser = argparse.ArgumentParser(prog=SPEC["application"]["name"])
    commands = parser.add_subparsers(dest="command", required=True)
    for command in SPEC["commands"]:
        sub = commands.add_parser(command["token"])
        if "migration" in command:
            continue
        behavior = by_id("behaviors", command["behavior"])
        for arg in command["arguments"]:
            inp = next(i for i in behavior["inputs"] if i["id"] == arg["input"])
            choices = by_id("types", inp["type"])["values"] if inp["type"] not in ("prim:string", "prim:timestamp") else None
            sub.add_argument(arg["flag"], required=arg["required"], choices=choices)
    parsed = parser.parse_args(argv)
    command = next(c for c in SPEC["commands"] if c["token"] == parsed.command)
    if "migration" in command:
        try:
            result = migrate()
        except Failure as exc:
            print(json.dumps({"error": exc.code}), file=sys.stderr)
            return 1
        print(json.dumps(result, sort_keys=True))
        return 0
    behavior = by_id("behaviors", command["behavior"])
    inputs = {a["input"]: value for a in command["arguments"] if (value := getattr(parsed, a["flag"][2:].replace("-", "_"))) is not None}
    try:
        result = execute(behavior, inputs)
    except Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
