"""Closed-world semantic checks for the intentionally small AIR v0.1 algebra."""

from .model import Program
from .parser import AirError


def check(value, keys, place):
    if not isinstance(value, dict):
        raise AirError(f"{place}: expected object")
    missing = set(keys) - value.keys()
    if missing:
        raise AirError(f"{place}: missing {sorted(missing)}")


def only(value, keys, place):
    extra = value.keys() - set(keys)
    if extra:
        raise AirError(f"{place}: unknown fields {sorted(extra)}")


def sequence(value, place):
    if not isinstance(value, list):
        raise AirError(f"{place}: expected array")
    return value


def same(actual, expected, place):
    if set(actual) != set(expected) or len(actual) != len(set(actual)):
        raise AirError(f"{place}: declared {actual!r}; inferred {sorted(expected)!r}")


def validate(program: Program) -> Program:
    d = program.document
    only(d, ("air_version", "application", "types", "capabilities", "state", "invariants", "behaviors", "commands"), "root")
    if d["air_version"] != "0.1":
        raise AirError("unsupported AIR version")
    check(d["application"], ("id", "name"), "application")
    only(d["application"], ("id", "name"), "application")
    groups = ("types", "capabilities", "state", "invariants", "behaviors", "commands")
    entities = {}
    for group in groups:
        for index, entity in enumerate(sequence(d[group], group)):
            place = f"{group}[{index}]"
            check(entity, ("id",), place)
            eid = entity["id"]
            if not isinstance(eid, str) or not eid or eid in entities or eid == d["application"]["id"]:
                raise AirError(f"{place}: duplicate or invalid ID {eid!r}")
            entities[eid] = entity
    types = {x["id"]: x for x in d["types"]}
    caps = {x["id"]: x for x in d["capabilities"]}
    states = {x["id"]: x for x in d["state"]}
    behaviors = {x["id"]: x for x in d["behaviors"]}
    fields = {}
    nested_ids = set(entities) | {d["application"]["id"]}

    def unique_nested(item, place):
        check(item, ("id",), place)
        eid = item["id"]
        if not isinstance(eid, str) or not eid or eid in nested_ids:
            raise AirError(f"{place}: duplicate or invalid ID {eid!r}")
        nested_ids.add(eid)

    def ref(eid, collection, place):
        if not isinstance(eid, str) or eid not in collection:
            raise AirError(f"{place}: nonexistent reference {eid!r}")
        return collection[eid]

    def type_ref(eid, place):
        if eid not in ("prim:string", "prim:timestamp"):
            ref(eid, types, place)

    for t in d["types"]:
        p = t["id"]
        check(t, ("id", "name", "kind"), p)
        if t["kind"] == "enum":
            only(t, ("id", "name", "kind", "values"), p)
            vals = sequence(t["values"], p)
            if not vals or any(not isinstance(v, str) for v in vals) or len(set(vals)) != len(vals):
                raise AirError(f"{p}: invalid enum values")
        elif t["kind"] == "record":
            only(t, ("id", "name", "kind", "fields"), p)
            if not sequence(t["fields"], p):
                raise AirError(f"{p}: empty record")
            names = set()
            for field in t["fields"]:
                check(field, ("id", "name", "type"), p)
                only(field, ("id", "name", "type"), p)
                unique_nested(field, p)
                if field["name"] in names:
                    raise AirError(f"{p}: duplicate field name {field['name']}")
                names.add(field["name"])
                fields[field["id"]] = field
        elif t["kind"] == "list":
            check(t, ("item_type",), p)
            only(t, ("id", "name", "kind", "item_type"), p)
        else:
            raise AirError(f"{p}: unsupported type kind")
    for t in d["types"]:
        if t["kind"] == "record":
            for f in t["fields"]:
                type_ref(f["type"], f["id"])
                if f["type"] in types and types[f["type"]]["kind"] != "enum":
                    raise AirError(f"{f['id']}: v0.1 record fields must be primitive or enum")
        if t["kind"] == "list":
            if ref(t["item_type"], types, t["id"])["kind"] != "record":
                raise AirError(f"{t['id']}: list item must be record")

    for cap in d["capabilities"]:
        p = cap["id"]
        check(cap, ("kind",), p)
        if cap["kind"] == "json_file":
            check(cap, ("path", "missing_file"), p)
            only(cap, ("id", "kind", "path", "missing_file"), p)
            if not isinstance(cap["path"], str) or not cap["path"] or cap["missing_file"] != "empty_collection":
                raise AirError(f"{p}: invalid storage policy")
        elif cap["kind"] in ("utc_clock", "uuid_v4"):
            only(cap, ("id", "kind"), p)
        else:
            raise AirError(f"{p}: unsupported capability")

    if len(states) != 1:
        raise AirError("v0.1 requires exactly one state")
    for state in d["state"]:
        p = state["id"]
        check(state, ("name", "type", "storage", "key_field", "invariants"), p)
        only(state, ("id", "name", "type", "storage", "key_field", "invariants"), p)
        list_type = ref(state["type"], types, p)
        if list_type["kind"] != "list":
            raise AirError(f"{p}: state must be a list")
        record = types[list_type["item_type"]]
        local_fields = {f["id"]: f for f in record["fields"]}
        key = ref(state["key_field"], local_fields, p)
        if key["type"] != "prim:string" or caps[ref(state["storage"], caps, p)["id"]]["kind"] != "json_file":
            raise AirError(f"{p}: key must be string and storage must be json_file")
        invariant_ids = [i["id"] for i in d["invariants"]]
        same(state["invariants"], invariant_ids, f"{p}.invariants")
        for inv in d["invariants"]:
            q = inv["id"]
            if inv.get("state") != p:
                raise AirError(f"{q}: invariant state mismatch")
            if inv.get("kind") == "unique_field":
                check(inv, ("field",), q)
                only(inv, ("id", "kind", "state", "field"), q)
                ref(inv["field"], local_fields, q)
            elif inv.get("kind") == "all_records_valid":
                check(inv, ("field_rules",), q)
                only(inv, ("id", "kind", "state", "field_rules"), q)
                for rule in sequence(inv["field_rules"], q):
                    check(rule, ("kind", "field"), q)
                    only(rule, ("kind", "field"), q)
                    field = ref(rule["field"], local_fields, q)
                    expected = {"nonblank": "prim:string", "timestamp_utc": "prim:timestamp"}.get(rule["kind"])
                    if expected is None or field["type"] != expected:
                        raise AirError(f"{q}: invalid field rule")
            else:
                raise AirError(f"{q}: unsupported invariant")
        if not any(i["kind"] == "unique_field" and i["field"] == state["key_field"] for i in d["invariants"]):
            raise AirError(f"{p}: key requires uniqueness invariant")

    def field_for(state, eid, place):
        record = types[types[state["type"]]["item_type"]]
        return ref(eid, {f["id"]: f for f in record["fields"]}, place)

    def literal(value, typ, place):
        if typ in ("prim:string", "prim:timestamp"):
            if not isinstance(value, str):
                raise AirError(f"{place}: expected string literal")
        elif value not in types[typ]["values"]:
            raise AirError(f"{place}: invalid enum literal {value!r}")

    for b in d["behaviors"]:
        p = b["id"]
        check(b, ("name", "kind", "state", "inputs", "output", "dependencies", "reads", "writes", "effects", "conditions", "assignments", "guarantees", "failures"), p)
        only(b, ("id", "name", "kind", "state", "inputs", "output", "dependencies", "reads", "writes", "effects", "conditions", "assignments", "guarantees", "failures", "lookup", "order_by"), p)
        kind = b["kind"]
        if kind not in ("create", "list", "update", "delete"):
            raise AirError(f"{p}: unsupported behavior")
        state = ref(b["state"], states, p)
        record_id = types[state["type"]]["item_type"]
        if b["output"] != (state["type"] if kind == "list" else record_id):
            raise AirError(f"{p}: output type mismatch")
        inputs = {}
        for inp in sequence(b["inputs"], p):
            check(inp, ("id", "name", "type"), p)
            only(inp, ("id", "name", "type"), p)
            unique_nested(inp, p)
            type_ref(inp["type"], inp["id"])
            if inp["type"] != "prim:string" or inp["id"] in inputs:
                raise AirError(f"{p}: v0.1 CLI inputs must be strings")
            inputs[inp["id"]] = inp
        if kind in ("update", "delete"):
            check(b.get("lookup"), ("field", "input"), p)
            only(b["lookup"], ("field", "input"), p)
            if b["lookup"]["field"] != state["key_field"] or b["lookup"]["input"] not in inputs:
                raise AirError(f"{p}: lookup must bind the state key to an input")
        elif "lookup" in b:
            raise AirError(f"{p}: unexpected lookup")
        if kind == "list":
            if inputs or b["assignments"] or b["conditions"]:
                raise AirError(f"{p}: list cannot mutate or take inputs")
            order = sequence(b.get("order_by"), p)
            if not order or len(set(order)) != len(order):
                raise AirError(f"{p}: invalid ordering")
            for eid in order:
                field_for(state, eid, p)
        elif "order_by" in b:
            raise AirError(f"{p}: unexpected order_by")
        expected_deps = {state["id"], state["storage"]}
        assignments = {}
        for a in sequence(b["assignments"], p):
            check(a, ("field", "source"), p)
            field = field_for(state, a["field"], p)
            if a["field"] in assignments or kind in ("list", "delete") or (kind == "update" and a["field"] == state["key_field"]):
                raise AirError(f"{p}: invalid state mutation {a['field']}")
            assignments[a["field"]] = a
            source = a["source"]
            if source == "literal":
                check(a, ("value",), p)
                only(a, ("field", "source", "value"), p)
                literal(a["value"], field["type"], p)
            elif source == "input":
                check(a, ("id",), p)
                only(a, ("field", "source", "id"), p)
                inp = ref(a["id"], inputs, p)
                if inp["type"] != field["type"]:
                    raise AirError(f"{p}: assignment type mismatch")
            elif source == "capability":
                check(a, ("id",), p)
                only(a, ("field", "source", "id"), p)
                cap = ref(a["id"], caps, p)
                if {"uuid_v4": "prim:string", "utc_clock": "prim:timestamp"}.get(cap["kind"]) != field["type"]:
                    raise AirError(f"{p}: capability assignment type mismatch")
                expected_deps.add(cap["id"])
            else:
                raise AirError(f"{p}: unknown assignment source")
        if kind == "create":
            record_fields = {f["id"] for f in types[record_id]["fields"]}
            same(list(assignments), record_fields, f"{p}.assignments")
            if assignments[state["key_field"]]["source"] != "capability" or caps[assignments[state["key_field"]]["id"]]["kind"] != "uuid_v4":
                raise AirError(f"{p}: create key must come from uuid_v4")
        if kind == "update" and not assignments:
            raise AirError(f"{p}: update requires a mutation")
        conditions = sequence(b["conditions"], p)
        condition_failures = set()
        for index, c in enumerate(conditions):
            check(c, ("kind", "failure"), p)
            if not isinstance(c["failure"], str) or not c["failure"]:
                raise AirError(f"{p}: invalid failure")
            condition_failures.add(c["failure"])
            if c["kind"] == "nonblank_input":
                check(c, ("input",), p)
                only(c, ("kind", "failure", "input"), p)
                ref(c["input"], inputs, p)
            elif c["kind"] == "record_exists" and kind in ("update", "delete"):
                only(c, ("kind", "failure"), p)
                if index != 0:
                    raise AirError(f"{p}: record_exists must be first")
            elif c["kind"] == "record_field_equals" and kind in ("update", "delete"):
                check(c, ("field", "value"), p)
                only(c, ("kind", "failure", "field", "value"), p)
                literal(c["value"], field_for(state, c["field"], p)["type"], p)
            else:
                raise AirError(f"{p}: unsupported condition")
        if kind in ("update", "delete") and (not conditions or conditions[0]["kind"] != "record_exists"):
            raise AirError(f"{p}: missing record_exists condition")
        inferred_effects = {"file_read"}
        if kind != "list":
            inferred_effects.add("file_write")
        for a in assignments.values():
            if a["source"] == "capability":
                inferred_effects.add({"uuid_v4": "random_id", "utc_clock": "clock_read"}[caps[a["id"]]["kind"]])
        same(b["dependencies"], expected_deps, f"{p}.dependencies")
        same(b["reads"], {state["id"]}, f"{p}.reads")
        same(b["writes"], set() if kind == "list" else {state["id"]}, f"{p}.writes")
        same(b["effects"], inferred_effects, f"{p}.effects")
        same(b["failures"], condition_failures | {"invalid_state", "persistence_failure"} | ({"id_collision"} if kind == "create" else set()), f"{p}.failures")
        expected_guarantees = {"create": {"result_field_equals", "result_in_state"}, "list": {"result_equals_state_sorted"}, "update": {"result_field_equals", "result_in_state"}, "delete": {"result_id_absent_from_state"}}[kind]
        guarantees = sequence(b["guarantees"], p)
        same([g.get("kind") for g in guarantees if isinstance(g, dict)], expected_guarantees, f"{p}.guarantees")
        for g in guarantees:
            q = g["kind"]
            if q == "result_field_equals":
                check(g, ("field", "value"), p)
                only(g, ("kind", "field", "value"), p)
                literal(g["value"], field_for(state, g["field"], p)["type"], p)
                assignment = assignments.get(g["field"])
                if assignment is None or assignment["source"] != "literal" or assignment["value"] != g["value"]:
                    raise AirError(f"{p}: impossible or unproven result guarantee")
            else:
                check(g, ("state",), p)
                only(g, ("kind", "state"), p)
                if g["state"] != state["id"]:
                    raise AirError(f"{p}: guarantee state mismatch")

    tokens = set()
    for cmd in d["commands"]:
        p = cmd["id"]
        check(cmd, ("token", "behavior", "arguments"), p)
        only(cmd, ("id", "token", "behavior", "arguments"), p)
        if not isinstance(cmd["token"], str) or not cmd["token"].isidentifier() or cmd["token"] in tokens:
            raise AirError(f"{p}: duplicate or invalid command token")
        tokens.add(cmd["token"])
        b = ref(cmd["behavior"], behaviors, p)
        arguments = sequence(cmd["arguments"], p)
        for arg in arguments:
            check(arg, ("flag", "input", "required"), p)
            only(arg, ("flag", "input", "required"), p)
            if not isinstance(arg["flag"], str) or not arg["flag"].startswith("--") or arg["required"] is not True:
                raise AirError(f"{p}: v0.1 requires named, required flags")
        same([a["input"] for a in arguments], {i["id"] for i in b["inputs"]}, f"{p}.arguments")
        if len({a["flag"] for a in arguments}) != len(arguments):
            raise AirError(f"{p}: duplicate flag")
    same([c["behavior"] for c in d["commands"]], set(behaviors), "commands.behaviors")
    return program
