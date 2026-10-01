"""Backend-independent entity index, relationships and structural changesets."""

from collections import defaultdict

from .parser import AirError
from .validator import validate


def index(program):
    validate(program)
    d = program.document
    entities = {d["application"]["id"]: ("application", d["application"])}
    owners = {}
    for group in ("types", "capabilities", "state", "invariants", "behaviors", "commands", "migrations", "errors"):
        for entity in d.get(group, []):
            entities[entity["id"]] = ({"types": "type", "capabilities": "capability", "state": "state", "invariants": "invariant", "behaviors": "behavior", "commands": "command", "migrations": "migration", "errors": "error"}[group], entity)
            if group == "types":
                for field in entity.get("fields", []):
                    entities[field["id"]] = ("field", field)
                    owners[field["id"]] = entity["id"]
            if group == "behaviors":
                for inp in entity["inputs"]:
                    entities[inp["id"]] = ("input", inp)
                    owners[inp["id"]] = entity["id"]
                for contract in entity["guarantees"]:
                    if "id" in contract:
                        entities[contract["id"]] = ("postcondition", contract)
                        owners[contract["id"]] = entity["id"]
                for contract in entity["conditions"]:
                    if "id" in contract:
                        entities[contract["id"]] = ("precondition", contract)
                        owners[contract["id"]] = entity["id"]
    edges = defaultdict(set)

    def link(source, relation, target):
        if target in entities:
            edges[source].add((relation, target))

    for child, owner in owners.items():
        link(owner, "owns", child)
    for eid, (kind, entity) in entities.items():
        if kind in ("field", "input", "state"):
            link(eid, "type", entity["type"])
        if kind == "type":
            link(eid, "item_type", entity.get("item_type"))
        if kind == "state":
            link(eid, "storage", entity["storage"])
            link(eid, "key_field", entity["key_field"])
            for target in entity["invariants"]:
                link(eid, "constrained_by", target)
        if kind == "invariant":
            link(eid, "state", entity["state"])
            for target in [entity.get("field")] + [r["field"] for r in entity.get("field_rules", [])]:
                link(eid, "constrains_field", target)
        if kind == "behavior":
            link(eid, "state", entity["state"])
            link(eid, "output", entity["output"])
            for target in entity["dependencies"]:
                link(eid, "depends_on", target)
            for relation in ("reads", "writes"):
                for target in entity[relation]:
                    link(eid, relation, target)
            for assignment in entity["assignments"]:
                link(eid, "assigns", assignment["field"])
                link(eid, "uses", assignment.get("id"))
            for target in entity.get("order_by", []):
                link(eid, "orders_by", target)
            if "filter" in entity:
                link(eid, "filters_by", entity["filter"]["field"])
            for condition in entity["conditions"]:
                link(eid, "precondition_field", condition.get("field"))
                link(eid, "precondition_input", condition.get("input"))
        if kind == "postcondition":
            for relation in ("field", "state"):
                link(eid, relation, entity.get(relation))
        if kind == "precondition":
            for relation in ("field", "input"):
                link(eid, relation, entity.get(relation))
            link(eid, "fails_with", entity.get("failure"))
        if kind == "behavior":
            for failure in entity["failures"]:
                link(eid, "may_fail_with", failure)
        if kind == "command":
            link(eid, "exposes", entity.get("behavior", entity.get("migration")))
            for argument in entity["arguments"]:
                link(eid, "binds", argument["input"])
        if kind == "migration":
            link(eid, "migrates", entity["state"])
            state = next(s for s in d["state"] if s["id"] == entity["state"])
            link(eid, "depends_on", state["storage"])
            for addition in entity["add_fields"]:
                link(eid, "adds_field", addition["field"])
    return entities, edges


def inspect(program, eid):
    entities, edges = index(program)
    if eid not in entities:
        raise AirError(f"unknown entity ID: {eid}")
    kind, entity = entities[eid]
    return {"id": eid, "kind": kind, "entity": entity,
            "dependencies": [{"relation": r, "id": t} for r, t in sorted(edges[eid])],
            "references": [{"relation": r, "id": source} for source, links in sorted(edges.items()) for r, t in sorted(links) if t == eid],
            "effects": entity.get("effects", []) if kind in ("behavior", "migration") else []}


def diff(before, after):
    left, left_edges = index(before)
    right, right_edges = index(after)
    changes = []
    for eid in sorted(left.keys() | right.keys()):
        if eid not in left:
            changes.append({"entity_id": eid, "kind": right[eid][0], "change": "added"})
        elif eid not in right:
            changes.append({"entity_id": eid, "kind": left[eid][0], "change": "removed"})
        elif left[eid] != right[eid]:
            old, new = left[eid][1], right[eid][1]
            attributes = sorted(key for key in old.keys() | new.keys() if old.get(key) != new.get(key))
            changes.append({"entity_id": eid, "kind": right[eid][0], "change": "modified", "attributes": attributes})
    for eid in sorted(left.keys() & right.keys()):
        for relation, target in sorted(right_edges[eid] - left_edges[eid]):
            changes.append({"entity_id": eid, "change": "dependency_added", "relation": relation, "target": target})
        for relation, target in sorted(left_edges[eid] - right_edges[eid]):
            changes.append({"entity_id": eid, "change": "dependency_removed", "relation": relation, "target": target})
    changed = {c["entity_id"] for c in changes}
    affected = {}
    for eid in sorted(right):
        causes = sorted({target for _, target in right_edges[eid] if target in changed})
        if eid in changed or causes:
            affected[eid] = {"direct": eid in changed, "via": causes}
    return {"before_version": before.version, "after_version": after.version,
            "changes": changes, "affected": affected}
