"""Backend-independent entity index, relationships and structural changesets."""

from collections import defaultdict, deque

from .parser import AirError
from .validator import validate


def index(program):
    validate(program)
    d = program.document
    entities = {d["application"]["id"]: ("application", d["application"])}
    owners = {}
    for group in ("types", "capabilities", "state", "invariants", "behaviors", "commands", "migrations", "errors", "scenarios", "state_machines", "transitions"):
        for entity in d.get(group, []):
            entities[entity["id"]] = ({"types": "type", "capabilities": "capability", "state": "state", "invariants": "invariant", "behaviors": "behavior", "commands": "command", "migrations": "migration", "errors": "error", "scenarios": "scenario", "state_machines": "state_machine", "transitions": "transition"}[group], entity)
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
            link(eid, "constrains_field", entity.get("predicate", {}).get("field"))
            link(eid, "constrains_query", entity.get("behavior"))
            link(eid, "constrains_lifecycle", entity.get("predicate", {}).get("machine"))
        if kind == "state_machine":
            link(eid, "lifecycle_field", entity["field"])
            for transition in entity["transitions"]:
                link(eid, "declares_transition", transition)
        if kind == "transition":
            link(eid, "machine", entity["machine"])
            link(eid, "guard", entity.get("guard"))
            link(eid, "trigger", entity["trigger"])
        if kind == "behavior":
            link(eid, "performs", entity.get("performs"))
            for grant in entity.get("requires", []):
                link(eid, "authorized_by", grant)
            link(eid, "state", entity["state"])
            link(eid, "output", entity["output"])
            if entity["kind"] == "create":
                link(eid, "creates", entity["output"])
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
                predicates = entity["filter"].get("predicates", [entity["filter"]])
                for predicate in predicates:
                    link(eid, "filters_by", predicate["field"])
                    if predicate["kind"] == "field_before_clock":
                        link(eid, "depends_on", predicate["clock"])
            if "lookup" in entity:
                link(eid, "looks_up", entity["lookup"]["field"])
                link(eid, "uses", entity["lookup"]["input"])
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
            for grant in entity.get("requires", []):
                link(eid, "authorized_by", grant)
            link(eid, "migrates", entity["state"])
            state = next(s for s in d["state"] if s["id"] == entity["state"])
            link(eid, "depends_on", state["storage"])
            for addition in entity["add_fields"]:
                link(eid, "adds_field", addition["field"])
        if kind == "scenario":
            link(eid, "tests", entity.get("behavior", entity.get("transition")))
            for field in (entity["record"] if "transition" in entity else entity["records"][0] if entity["records"] else ()):
                link(eid, "fixtures_field", field)
        if kind == "capability" and entity.get("kind") == "resource_access":
            link(eid, "authorizes_resource", entity["resource"])
    return entities, edges


def impact(program, eid):
    """Breadth-first reverse dependency traversal with one shortest path per entity.

    Ownership is traversed from child to parent: a field affects its record,
    never every sibling merely because the record owns them. Other edges are
    followed from target to source. Paths always point back to the root.
    """
    entities, edges = index(program)
    if eid not in entities:
        raise AirError(f"unknown entity ID: {eid}")
    reverse = defaultdict(list)
    for source, links in edges.items():
        for relation, target in links:
            reverse[target].append((source, relation))
    paths = {eid: []}
    queue = deque([eid])
    while queue:
        target = queue.popleft()
        for source, relation in sorted(reverse[target]):
            if source not in paths:
                paths[source] = [{"from": source, "relation": relation, "to": target}] + paths[target]
                queue.append(source)
    return {"root": eid, "impacts": [
        {"id": node, "kind": entities[node][0], "depth": len(path), "path": path,
         "classification": "direct" if len(path) == 1 else "indirect",
         "semantic_classification": classify(path)}
        for node, path in sorted(paths.items(), key=lambda pair: (len(pair[1]), pair[0])) if node != eid
    ]}


def classify(path):
    relations = {step["relation"] for step in path}
    if relations & {"performs", "declares_transition", "lifecycle_field", "machine", "trigger", "guard"}:
        return "TRANSITION_IMPACT"
    if relations & {"constrained_by", "constrains_field", "constrains_lifecycle", "constrains_query", "precondition_field"}:
        return "CONTRACT_IMPACT"
    if relations & {"authorized_by", "authorizes_resource"}:
        return "CAPABILITY_IMPACT"
    return "DIRECT_SEMANTIC_IMPACT" if len(path) == 1 else "DEPENDENCY_IMPACT"


def safety(program):
    """Evidence labels describe what was checked, never a numeric safety score."""
    validate(program)
    d = program.document
    findings = []
    for inv in d["invariants"]:
        kind = inv["kind"]
        evidence = "RUNTIME_ENFORCED"
        if kind == "query_exclusion":
            evidence = "STRUCTURALLY_GUARANTEED"  # Validator checks the closed-world equality filter.
        findings.append({"id": inv["id"], "evidence": evidence})
    relevant = []
    for behavior in d["behaviors"]:
        if not behavior["writes"]:
            continue
        mutated = {a["field"] for a in behavior["assignments"]}
        if behavior["kind"] in ("create", "delete"):
            mutated = {f["id"] for t in d["types"] if t["kind"] == "record" and t["id"] == behavior["output"] for f in t["fields"]}
        affected = [inv["id"] for inv in d["invariants"] if inv["state"] == behavior["state"] and (inv["kind"] in ("all_records_valid", "unique_field") and (inv.get("field") in mutated or any(r["field"] in mutated for r in inv.get("field_rules", []))) or inv["kind"] == "predicate" and inv["predicate"]["field"] in mutated or inv["kind"] == "query_exclusion" and inv["field"] in mutated)]
        relevant.append({"behavior": behavior["id"], "mutates": sorted(mutated), "relevant_invariants": affected})
    counts = {label: sum(f["evidence"] == label for f in findings) for label in ("STRUCTURALLY_GUARANTEED", "RUNTIME_ENFORCED", "SCENARIO_VERIFIED", "UNVERIFIED")}
    return {"state_machines": len(d.get("state_machines", [])), "declared_transitions": len(d.get("transitions", [])), "invalid_transitions": 0,
            "protected_resources": sum(c["kind"] == "json_file" for c in d["capabilities"]), "capability_violations": 0,
            "invariants": len(findings), "evidence_counts": counts, "findings": findings, "mutations": relevant}


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
