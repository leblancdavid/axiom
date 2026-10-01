"""Closed-world semantic checks for the intentionally small Axiom algebra."""

from datetime import datetime

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
    only(d, ("air_version", "axiom_version", "application", "types", "capabilities", "state", "state_machines", "transitions", "invariants", "behaviors", "commands", "migrations", "errors", "scenarios"), "root")
    if program.version not in ("0.1", "0.2", "0.3") or ("air_version" in d and "axiom_version" in d):
        raise AirError("unsupported or ambiguous Axiom version")
    modern = program.version != "0.1"
    safety = program.version == "0.3"
    if safety and ("state_machines" not in d or "transitions" not in d):
        raise AirError("v0.3 requires state_machines and transitions")
    if not safety and ("state_machines" in d or "transitions" in d):
        raise AirError("state machines require v0.3")
    if modern and ("axiom_version" not in d or "migrations" not in d or "errors" not in d):
        raise AirError("v0.2 requires axiom_version, migrations and errors")
    if not modern and ("migrations" in d or "errors" in d):
        raise AirError("v0.1 does not support migrations or errors")
    check(d["application"], ("id", "name"), "application")
    only(d["application"], ("id", "name"), "application")
    groups = ("types", "capabilities", "state", "invariants", "behaviors", "commands") + (("migrations", "errors") if modern else ()) + (("scenarios",) if "scenarios" in d else ()) + (("state_machines", "transitions") if safety else ())
    entities = {}
    for group in groups:
        for index, entity in enumerate(sequence(d[group], group)):
            place = f"{group}[{index}]"
            check(entity, ("id",), place)
            eid = entity["id"]
            if not isinstance(eid, str) or not eid or eid in entities or eid == d["application"]["id"] or eid in ("prim:string", "prim:timestamp"):
                raise AirError(f"{place}: duplicate or invalid ID {eid!r}")
            entities[eid] = entity
    types = {x["id"]: x for x in d["types"]}
    caps = {x["id"]: x for x in d["capabilities"]}
    states = {x["id"]: x for x in d["state"]}
    behaviors = {x["id"]: x for x in d["behaviors"]}
    errors = {x["id"]: x for x in d.get("errors", [])}
    machines = {x["id"]: x for x in d.get("state_machines", [])}
    transitions = {x["id"]: x for x in d.get("transitions", [])}
    codes = set()
    for error in d.get("errors", []):
        check(error, ("id", "code"), error["id"])
        only(error, ("id", "code"), error["id"])
        if not isinstance(error["code"], str) or not error["code"] or error["code"] in codes:
            raise AirError(f"{error['id']}: duplicate or invalid error code")
        codes.add(error["code"])
    fields = {}
    nested_ids = set(entities) | {d["application"]["id"]}
    if not isinstance(d["application"]["id"], str) or not d["application"]["id"] or d["application"]["id"] in ("prim:string", "prim:timestamp"):
        raise AirError("application: invalid ID")

    def unique_nested(item, place):
        check(item, ("id",), place)
        eid = item["id"]
        if not isinstance(eid, str) or not eid or eid in nested_ids or eid in ("prim:string", "prim:timestamp"):
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
                only(field, ("id", "name", "type", "nullable"), p)
                if "nullable" in field and (not modern or field["type"] != "prim:timestamp" or field["nullable"] is not True):
                    raise AirError(f"{p}: only timestamp fields can be nullable")
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
        elif safety and cap["kind"] == "resource_access":
            check(cap, ("resource", "action"), p)
            only(cap, ("id", "kind", "resource", "action"), p)
            if ref(cap["resource"], caps, p).get("kind") != "json_file" or cap["action"] not in ("read", "write"):
                raise AirError(f"{p}: invalid resource authority")
        else:
            raise AirError(f"{p}: unsupported capability")
    if safety:
        if len({(c["resource"], c["action"]) for c in caps.values() if c["kind"] == "resource_access"}) != sum(c["kind"] == "resource_access" for c in caps.values()):
            raise AirError("duplicate resource authority")
        for resource in (c for c in caps.values() if c["kind"] == "json_file"):
            if {c["action"] for c in caps.values() if c["kind"] == "resource_access" and c["resource"] == resource["id"]} != {"read", "write"}:
                raise AirError(f"{resource['id']}: read and write authorities required")
        for machine in d["state_machines"]:
            p = machine["id"]
            check(machine, ("name", "field", "initial", "transitions"), p)
            only(machine, ("id", "name", "field", "initial", "transitions"), p)
            field = ref(machine["field"], fields, p)
            typ = ref(field["type"], types, p)
            if typ["kind"] != "enum" or machine["initial"] not in typ["values"]:
                raise AirError(f"{p}: initial state must belong to field enum")
            owned = [t for t in d["transitions"] if t.get("machine") == p]
            same(machine["transitions"], {t["id"] for t in owned}, f"{p}.transitions")
            seen, reachable = set(), {machine["initial"]}
            for transition in owned:
                q = transition["id"]
                check(transition, ("source", "target", "trigger"), q)
                only(transition, ("id", "machine", "source", "target", "trigger", "guard", "effects"), q)
                if transition["source"] not in typ["values"] or transition["target"] not in typ["values"]:
                    raise AirError(f"{q}: unknown lifecycle state")
                ref(transition["trigger"], behaviors, q)
                if not isinstance(transition.get("guard"), str):
                    raise AirError(f"{q}: source guard ID required")
                if "effects" in transition:
                    same(transition["effects"], {"state_write"}, f"{q}.effects")
                signature = (transition["source"], transition["target"], transition["trigger"])
                if signature in seen:
                    raise AirError(f"{q}: duplicate transition")
                seen.add(signature)
            while True:
                next_states = reachable | {t["target"] for t in owned if t["source"] in reachable}
                if next_states == reachable:
                    break
                reachable = next_states
            if set(typ["values"]) - reachable:
                raise AirError(f"{p}: unreachable lifecycle states {sorted(set(typ['values']) - reachable)}")
        for t in d["transitions"]:
            ref(t.get("machine"), machines, t["id"])
            if behaviors[t["trigger"]].get("performs") != t["id"]:
                raise AirError(f"{t['id']}: trigger does not perform transition")

    if len(states) != 1:
        raise AirError("v0.1 requires exactly one state")
    for state in d["state"]:
        p = state["id"]
        check(state, ("name", "type", "storage", "key_field", "invariants"), p)
        only(state, ("id", "name", "type", "storage", "key_field", "invariants", "schema_version"), p)
        if modern and (not isinstance(state.get("schema_version"), int) or isinstance(state.get("schema_version"), bool) or state["schema_version"] < 1):
            raise AirError(f"{p}: invalid schema_version")
        list_type = ref(state["type"], types, p)
        if list_type["kind"] != "list":
            raise AirError(f"{p}: state must be a list")
        record = types[list_type["item_type"]]
        local_fields = {f["id"]: f for f in record["fields"]}
        if safety and any(m["field"] not in local_fields for m in machines.values()):
            raise AirError(f"{p}: lifecycle field must belong to state record")
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
            elif safety and inv.get("kind") == "predicate":
                check(inv, ("predicate",), q)
                only(inv, ("id", "kind", "state", "predicate"), q)
                pred = inv["predicate"]
                check(pred, ("operator", "field"), q)
                field = ref(pred["field"], local_fields, q)
                if pred["operator"] == "NOT_EMPTY":
                    only(pred, ("operator", "field"), q)
                    if field["type"] != "prim:string":
                        raise AirError(f"{q}: NOT_EMPTY requires string")
                elif pred["operator"] == "IN":
                    check(pred, ("values",), q)
                    only(pred, ("operator", "field", "values"), q)
                    typ = ref(field["type"], types, q)
                    if typ["kind"] != "enum" or not pred["values"] or len(set(pred["values"])) != len(pred["values"]) or set(pred["values"]) != set(typ["values"]):
                        raise AirError(f"{q}: IN must enumerate the field's valid states")
                elif pred["operator"] == "LIFECYCLE_STATE":
                    check(pred, ("machine",), q)
                    only(pred, ("operator", "field", "machine"), q)
                    if ref(pred["machine"], machines, q)["field"] != field["id"]:
                        raise AirError(f"{q}: lifecycle field mismatch")
                else:
                    raise AirError(f"{q}: unsupported predicate")
            elif safety and inv.get("kind") == "query_exclusion":
                check(inv, ("behavior", "field", "value"), q)
                only(inv, ("id", "kind", "state", "behavior", "field", "value"), q)
                field = ref(inv["field"], local_fields, q)
                if field["type"] not in types or types[field["type"]]["kind"] != "enum" or inv["value"] not in types[field["type"]]["values"]:
                    raise AirError(f"{q}: invalid exclusion value")
                behavior = ref(inv["behavior"], behaviors, q)
                predicates = behavior.get("filter", {}).get("predicates", [behavior.get("filter", {})])
                if behavior["kind"] != "list" or behavior["state"] != p or not any(x.get("kind") == "field_equals" and x.get("field") == field["id"] and x.get("value") != inv["value"] for x in predicates):
                    raise AirError(f"{q}: query does not guarantee exclusion")
            else:
                raise AirError(f"{q}: unsupported invariant")
        if not any(i["kind"] == "unique_field" and i["field"] == state["key_field"] for i in d["invariants"]):
            raise AirError(f"{p}: key requires uniqueness invariant")

    def field_for(state, eid, place):
        record = types[types[state["type"]]["item_type"]]
        return ref(eid, {f["id"]: f for f in record["fields"]}, place)

    def literal(value, typ, place, nullable=False):
        if value is None and nullable:
            return
        if typ in ("prim:string", "prim:timestamp"):
            if not isinstance(value, str):
                raise AirError(f"{place}: expected string literal")
            if typ == "prim:timestamp" and not timestamp(value):
                raise AirError(f"{place}: invalid UTC timestamp literal")
        elif value not in types[typ]["values"]:
            raise AirError(f"{place}: invalid enum literal {value!r}")

    def timestamp(value):
        if not isinstance(value, str) or not value.endswith("Z"):
            return False
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset().total_seconds() == 0
        except ValueError:
            return False

    for migration in sequence(d.get("migrations", []), "migrations"):
        p = migration["id"]
        check(migration, ("state", "from_version", "to_version", "add_fields", "effects"), p)
        only(migration, ("id", "state", "from_version", "to_version", "add_fields", "effects", "requires") if safety else ("id", "state", "from_version", "to_version", "add_fields", "effects"), p)
        same(migration["effects"], {"state_read", "state_write", "file_read", "file_write"}, f"{p}.effects")
        state = ref(migration["state"], states, p)
        if safety:
            required = {c["id"] for c in caps.values() if c["kind"] == "resource_access" and c["resource"] == state["storage"]}
            same(migration.get("requires", []), required, f"{p}.requires")
        before, after = migration["from_version"], migration["to_version"]
        if not isinstance(before, int) or isinstance(before, bool) or before < 1 or after != before + 1 or after > state["schema_version"]:
            raise AirError(f"{p}: invalid migration versions")
        additions = sequence(migration["add_fields"], p)
        if not additions:
            raise AirError(f"{p}: migration needs added fields")
        seen = set()
        for addition in additions:
            check(addition, ("field", "value"), p)
            only(addition, ("field", "value"), p)
            record = types[types[state["type"]]["item_type"]]
            field = ref(addition["field"], {f["id"]: f for f in record["fields"]}, p)
            if field["id"] in seen or field["id"] == state["key_field"]:
                raise AirError(f"{p}: duplicate or key migration field")
            seen.add(field["id"])
            literal(addition["value"], field["type"], p, field.get("nullable", False))
    for state in d["state"]:
        migrations = [m for m in d.get("migrations", []) if m["state"] == state["id"]]
        if modern and sorted(m["to_version"] for m in migrations) != list(range(2, state["schema_version"] + 1)):
            raise AirError(f"{state['id']}: migration chain incomplete or duplicated")

    for b in d["behaviors"]:
        p = b["id"]
        check(b, ("name", "kind", "state", "inputs", "output", "dependencies", "reads", "writes", "effects", "conditions", "assignments", "guarantees", "failures"), p)
        only(b, ("id", "name", "kind", "state", "inputs", "output", "dependencies", "reads", "writes", "effects", "conditions", "assignments", "guarantees", "failures", "lookup", "order_by", "filter", "requires", "performs") if safety else ("id", "name", "kind", "state", "inputs", "output", "dependencies", "reads", "writes", "effects", "conditions", "assignments", "guarantees", "failures", "lookup", "order_by", "filter"), p)
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
            only(inp, ("id", "name", "type", "nullable"), p)
            if "nullable" in inp and (not modern or inp["type"] != "prim:timestamp" or inp["nullable"] is not True):
                raise AirError(f"{p}: invalid nullable input")
            unique_nested(inp, p)
            type_ref(inp["type"], inp["id"])
            if (not modern and inp["type"] != "prim:string") or (modern and inp["type"] not in ("prim:string", "prim:timestamp") and (inp["type"] not in types or types[inp["type"]]["kind"] != "enum")) or inp["id"] in inputs:
                raise AirError(f"{p}: inputs must be strings or v0.2 enums")
            inputs[inp["id"]] = inp
        if kind in ("update", "delete"):
            check(b.get("lookup"), ("field", "input"), p)
            only(b["lookup"], ("field", "input"), p)
            if b["lookup"]["field"] != state["key_field"] or b["lookup"]["input"] not in inputs:
                raise AirError(f"{p}: lookup must bind the state key to an input")
        elif "lookup" in b:
            raise AirError(f"{p}: unexpected lookup")
        if kind == "list":
            if b["assignments"] or b["conditions"]:
                raise AirError(f"{p}: list cannot mutate")
            if inputs or ("filter" in b and not modern):
                raise AirError(f"{p}: unsupported list inputs or filter")
            if "filter" in b:
                spec = b["filter"]
                if spec.get("kind") == "all":
                    check(spec, ("predicates",), p)
                    only(spec, ("kind", "predicates"), p)
                    predicates = sequence(spec["predicates"], p)
                    if len(predicates) < 2:
                        raise AirError(f"{p}: all requires two or more predicates")
                else:
                    predicates = [spec]
                for predicate in predicates:
                    check(predicate, ("kind", "field"), p)
                    field = field_for(state, predicate["field"], p)
                    if predicate["kind"] == "field_equals":
                        check(predicate, ("value",), p)
                        only(predicate, ("kind", "field", "value"), p)
                        literal(predicate["value"], field["type"], p, field.get("nullable", False))
                    elif predicate["kind"] == "field_before_clock" and modern:
                        check(predicate, ("clock",), p)
                        only(predicate, ("kind", "field", "clock"), p)
                        if field["type"] != "prim:timestamp" or caps[ref(predicate["clock"], caps, p)["id"]]["kind"] != "utc_clock":
                            raise AirError(f"{p}: before_clock requires timestamp and utc_clock")
                    else:
                        raise AirError(f"{p}: unsupported filter")
            order = sequence(b.get("order_by"), p)
            if not order or len(set(order)) != len(order):
                raise AirError(f"{p}: invalid ordering")
            for eid in order:
                field_for(state, eid, p)
        elif "order_by" in b:
            raise AirError(f"{p}: unexpected order_by")
        if kind != "list" and "filter" in b:
            raise AirError(f"{p}: unexpected filter")
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
                if inp["type"] != field["type"] or inp.get("nullable", False) != field.get("nullable", False):
                    raise AirError(f"{p}: assignment type mismatch")
            elif source == "input_default" and modern and kind == "create":
                check(a, ("id", "value"), p)
                only(a, ("field", "source", "id", "value"), p)
                inp = ref(a["id"], inputs, p)
                if inp["type"] != field["type"] or inp.get("nullable", False) != field.get("nullable", False):
                    raise AirError(f"{p}: assignment type mismatch")
                literal(a["value"], field["type"], p, field.get("nullable", False))
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
        if safety:
            relevant = [m for m in machines.values() if m["field"] in {f["id"] for f in types[record_id]["fields"]}]
            for machine in relevant:
                fid = machine["field"]
                if kind == "create" and (assignments[fid]["source"] != "literal" or assignments[fid]["value"] != machine["initial"]):
                    raise AirError(f"{p}: invalid initial lifecycle state")
                if kind == "update" and fid in assignments:
                    transition = ref(b.get("performs"), transitions, f"{p}.performs")
                    if transition["machine"] != machine["id"] or transition["trigger"] != p or assignments[fid]["source"] != "literal" or assignments[fid]["value"] != transition["target"]:
                        raise AirError(f"{p}: undeclared or mismatched transition")
                elif b.get("performs") in transitions and transitions[b["performs"]]["machine"] == machine["id"]:
                    raise AirError(f"{p}: transition without lifecycle mutation")
            if "performs" in b and b["performs"] not in transitions:
                raise AirError(f"{p}: undeclared transition {b['performs']}")
        conditions = sequence(b["conditions"], p)
        condition_failures = set()
        for index, c in enumerate(conditions):
            check(c, ("kind", "failure"), p)
            if modern:
                unique_nested(c, p)
            if not isinstance(c["failure"], str) or not c["failure"]:
                raise AirError(f"{p}: invalid failure")
            if modern:
                ref(c["failure"], errors, p)
            condition_failures.add(c["failure"])
            if c["kind"] == "nonblank_input":
                check(c, ("input",), p)
                only(c, ("id", "kind", "failure", "input"), p)
                ref(c["input"], inputs, p)
            elif c["kind"] == "record_exists" and kind in ("update", "delete"):
                only(c, ("id", "kind", "failure"), p)
                if index != 0:
                    raise AirError(f"{p}: record_exists must be first")
            elif c["kind"] == "record_field_equals" and kind in ("update", "delete"):
                check(c, ("field", "value"), p)
                only(c, ("id", "kind", "failure", "field", "value"), p)
                literal(c["value"], field_for(state, c["field"], p)["type"], p)
            elif c["kind"] == "timestamp_input" and modern:
                check(c, ("input",), p)
                only(c, ("id", "kind", "failure", "input"), p)
                if ref(c["input"], inputs, p)["type"] != "prim:timestamp":
                    raise AirError(f"{p}: timestamp_input requires timestamp")
            else:
                raise AirError(f"{p}: unsupported condition")
        if kind in ("update", "delete") and (not conditions or conditions[0]["kind"] != "record_exists"):
            raise AirError(f"{p}: missing record_exists condition")
        if safety and "performs" in b:
            t = transitions[b["performs"]]
            fid = machines[t["machine"]]["field"]
            matching = [c for c in conditions if c["kind"] == "record_field_equals" and c["field"] == fid and c["value"] == t["source"]]
            if not matching or ("guard" in t and t["guard"] not in [c["id"] for c in matching]):
                raise AirError(f"{p}: transition source guard missing or invalid")
        inferred_effects = {"file_read"}
        if modern:
            inferred_effects.add("state_read")
        if kind != "list":
            inferred_effects.add("file_write")
            if modern:
                inferred_effects.add("state_write")
        for a in assignments.values():
            if a["source"] == "capability":
                inferred_effects.add({"uuid_v4": "random_id", "utc_clock": "clock_read"}[caps[a["id"]]["kind"]])
        if "filter" in b:
            predicates = b["filter"].get("predicates", [b["filter"]])
            for predicate in predicates:
                if predicate["kind"] == "field_before_clock":
                    expected_deps.add(predicate["clock"])
                    inferred_effects.add("clock_read")
        same(b["dependencies"], expected_deps, f"{p}.dependencies")
        same(b["reads"], {state["id"]}, f"{p}.reads")
        same(b["writes"], set() if kind == "list" else {state["id"]}, f"{p}.writes")
        same(b["effects"], inferred_effects, f"{p}.effects")
        if safety:
            required = {c["id"] for c in caps.values() if c["kind"] == "resource_access" and c["resource"] == state["storage"] and (c["action"] == "read" or kind != "list")}
            required |= {a["id"] for a in assignments.values() if a["source"] == "capability"}
            required |= {predicate["clock"] for predicate in b.get("filter", {}).get("predicates", [b.get("filter", {})]) if predicate.get("kind") == "field_before_clock"}
            same(b.get("requires", []), required, f"{p}.requires (capability violation)")
            for grant in b.get("requires", []):
                ref(grant, caps, p)
        builtin = {"invalid_state", "persistence_failure"} | ({"migration_required"} if modern and state["schema_version"] > 1 else set()) | ({"id_collision"} if kind == "create" else set())
        if modern:
            builtin = {ref(next((eid for eid, error in errors.items() if error["code"] == code), None), errors, p)["id"] for code in builtin}
            for failure in b["failures"]:
                ref(failure, errors, p)
        same(b["failures"], condition_failures | builtin, f"{p}.failures")
        expected_guarantees = {"create": {"result_field_equals", "result_in_state"}, "list": {"result_equals_state_sorted"}, "update": {"result_field_equals", "result_in_state"}, "delete": {"result_id_absent_from_state"}}[kind]
        guarantees = sequence(b["guarantees"], p)
        guarantee_kinds = [g.get("kind") for g in guarantees if isinstance(g, dict)]
        same([k for k in guarantee_kinds if k != "result_field_equals_assignment" or not modern], expected_guarantees, f"{p}.guarantees")
        if modern and len({g["field"] for g in guarantees if g["kind"] == "result_field_equals_assignment"}) != guarantee_kinds.count("result_field_equals_assignment"):
            raise AirError(f"{p}: duplicate assignment guarantee")
        for g in guarantees:
            q = g["kind"]
            if modern:
                unique_nested(g, p)
            if q == "result_field_equals":
                check(g, ("field", "value"), p)
                only(g, ("id", "kind", "field", "value"), p)
                literal(g["value"], field_for(state, g["field"], p)["type"], p)
                assignment = assignments.get(g["field"])
                if assignment is None or assignment["source"] != "literal" or assignment["value"] != g["value"]:
                    raise AirError(f"{p}: impossible or unproven result guarantee")
            elif q == "result_field_equals_assignment" and modern:
                check(g, ("field",), p)
                only(g, ("id", "kind", "field"), p)
                field_for(state, g["field"], p)
                if g["field"] not in assignments or assignments[g["field"]]["source"] not in ("literal", "input", "input_default"):
                    raise AirError(f"{p}: unproven assignment guarantee")
            else:
                check(g, ("state",), p)
                only(g, ("id", "kind", "state"), p)
                if g["state"] != state["id"]:
                    raise AirError(f"{p}: guarantee state mismatch")

    tokens = set()
    migration_commands = []
    for cmd in d["commands"]:
        p = cmd["id"]
        check(cmd, ("token", "arguments"), p)
        only(cmd, ("id", "token", "behavior", "migration", "arguments"), p)
        if not isinstance(cmd["token"], str) or not cmd["token"].replace("-", "_").isidentifier() or cmd["token"] in tokens:
            raise AirError(f"{p}: duplicate or invalid command token")
        tokens.add(cmd["token"])
        if "migration" in cmd:
            if not modern or "behavior" in cmd or cmd["token"] != "migrate" or cmd["arguments"] != []:
                raise AirError(f"{p}: invalid migration command")
            ref(cmd["migration"], {m["id"]: m for m in d["migrations"]}, p)
            migration_commands.append(cmd["migration"])
            continue
        check(cmd, ("behavior",), p)
        b = ref(cmd["behavior"], behaviors, p)
        arguments = sequence(cmd["arguments"], p)
        for arg in arguments:
            check(arg, ("flag", "input", "required"), p)
            only(arg, ("flag", "input", "required"), p)
            if not isinstance(arg["flag"], str) or not arg["flag"].startswith("--") or type(arg["required"]) is not bool or (not modern and not arg["required"]):
                raise AirError(f"{p}: invalid command flag")
            if not arg["required"] and not any(a["source"] == "input_default" and a["id"] == arg["input"] for a in b["assignments"]):
                raise AirError(f"{p}: optional input requires a default assignment")
        same([a["input"] for a in arguments], {i["id"] for i in b["inputs"]}, f"{p}.arguments")
        if len({a["flag"] for a in arguments}) != len(arguments):
            raise AirError(f"{p}: duplicate flag")
    same([c["behavior"] for c in d["commands"] if "behavior" in c], set(behaviors), "commands.behaviors")
    if modern:
        same(migration_commands, {max((m for m in d["migrations"] if m["state"] == state["id"]), key=lambda m: m["to_version"])["id"] for state in d["state"] if any(m["state"] == state["id"] for m in d["migrations"])}, "commands.migrations")
    for scenario in d.get("scenarios", []):
        p = scenario["id"]
        if safety and "transition" in scenario:
            check(scenario, ("record", "lookup_value"), p)
            only(scenario, ("id", "transition", "record", "lookup_value"), p)
            transition = ref(scenario["transition"], transitions, p)
            behavior = behaviors[transition["trigger"]]
            if behavior["kind"] != "update" or "lookup" not in behavior:
                raise AirError(f"{p}: transition scenario requires update behavior")
            state = states[behavior["state"]]
            record = types[types[state["type"]]["item_type"]]
            fields_by_id = {f["id"]: f for f in record["fields"]}
            row = scenario["record"]
            if not isinstance(row, dict) or set(row) != set(fields_by_id):
                raise AirError(f"{p}: incomplete transition record")
            for eid, value in row.items():
                literal(value, fields_by_id[eid]["type"], p, fields_by_id[eid].get("nullable", False))
            if row[states[behavior["state"]]["key_field"]] != scenario["lookup_value"] or row[machines[transition["machine"]]["field"]] != transition["source"]:
                raise AirError(f"{p}: transition fixture does not match source and lookup")
            continue
        check(scenario, ("behavior", "clock", "records", "expected_ids"), p)
        only(scenario, ("id", "behavior", "clock", "records", "expected_ids"), p)
        behavior = ref(scenario["behavior"], behaviors, p)
        if behavior["kind"] != "list" or "clock_read" not in behavior["effects"]:
            raise AirError(f"{p}: scenario requires clock-aware list behavior")
        if not timestamp(scenario["clock"]):
            raise AirError(f"{p}: invalid clock instant")
        state = states[behavior["state"]]
        record = types[types[state["type"]]["item_type"]]
        fields_by_id = {f["id"]: f for f in record["fields"]}
        ids = []
        for row in sequence(scenario["records"], p):
            if not isinstance(row, dict) or set(row) != set(fields_by_id):
                raise AirError(f"{p}: incomplete scenario record")
            for eid, value in row.items():
                literal(value, fields_by_id[eid]["type"], p, fields_by_id[eid].get("nullable", False))
                if eid == state["key_field"]:
                    ids.append(value)
        if len(ids) != len(set(ids)) or any(eid not in ids for eid in sequence(scenario["expected_ids"], p)) or len(scenario["expected_ids"]) != len(set(scenario["expected_ids"])):
            raise AirError(f"{p}: invalid expected IDs")
    return program
