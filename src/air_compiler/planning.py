"""Deterministic, ID-addressed semantic transformations and preflight checks."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .generator import generate, VERSION
from .model import Program
from .parser import AirError, _unique_pairs, load
from .semantics import diff, impact, index
from .validator import validate


GROUPS = ("types", "capabilities", "state", "invariants", "behaviors", "commands", "migrations", "errors", "scenarios", "state_machines", "transitions")


def blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_plan(path):
    try:
        plan = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    except json.JSONDecodeError as exc:
        raise AirError(f"invalid plan JSON: {exc}") from exc
    if not isinstance(plan, dict) or set(plan) != {"id", "intent", "model", "baseline", "operations", "anticipated_impacts", "verification"}:
        raise AirError("plan: required keys are id, intent, model, baseline, operations, anticipated_impacts, verification")
    if not isinstance(plan["id"], str) or not plan["id"] or not isinstance(plan["intent"], str) or not plan["intent"].strip():
        raise AirError("plan: id and intent are required")
    if not isinstance(plan["operations"], list) or not plan["operations"]:
        raise AirError("plan: operations must be nonempty")
    return plan


def transform(program, operations):
    document = copy.deepcopy(program.document)
    touched = set()
    for number, operation in enumerate(operations):
        place = f"operations[{number}]"
        if not isinstance(operation, dict) or operation.get("op") not in ("add", "remove", "set", "append"):
            raise AirError(f"{place}: unsupported operation")
        op = operation["op"]
        if op == "add":
            if set(operation) != {"op", "group", "value"} or operation["group"] not in GROUPS or not isinstance(operation["value"], dict) or not isinstance(operation["value"].get("id"), str):
                raise AirError(f"{place}: invalid addition")
            if operation["value"]["id"] in index_ids(document):
                raise AirError(f"{place}: duplicate ID {operation['value']['id']}")
            document.setdefault(operation["group"], []).append(copy.deepcopy(operation["value"]))
            touched.add(operation["value"]["id"])
            continue
        if "id" not in operation or not isinstance(operation["id"], str):
            raise AirError(f"{place}: missing entity ID")
        eid = operation["id"]
        location = next(((group, i, entity) for group in GROUPS for i, entity in enumerate(document.get(group, [])) if entity["id"] == eid), None)
        if location is None:
            raise AirError(f"{place}: nonexistent entity {eid}")
        group, position, entity = location
        touched.add(eid)
        if op == "remove":
            if set(operation) != {"op", "id"}:
                raise AirError(f"{place}: invalid removal")
            del document[group][position]
        else:
            if set(operation) != {"op", "id", "path", "value"} or not isinstance(operation["path"], list) or not operation["path"] or any(not isinstance(k, str) for k in operation["path"]):
                raise AirError(f"{place}: invalid path operation")
            container = entity
            for key in operation["path"][:-1]:
                if not isinstance(container, dict) or key not in container:
                    raise AirError(f"{place}: nonexistent path")
                container = container[key]
            key = operation["path"][-1]
            if not isinstance(container, dict) or (op == "append" and (key not in container or not isinstance(container[key], list))):
                raise AirError(f"{place}: invalid target")
            if op == "append":
                container[key].append(copy.deepcopy(operation["value"]))
            else:
                if key == "id":
                    raise AirError(f"{place}: identity cannot be replaced")
                container[key] = copy.deepcopy(operation["value"])
    return Program(document), touched


def index_ids(document):
    ids = {document["application"]["id"]}
    for group in GROUPS:
        for entity in document.get(group, []):
            ids.add(entity["id"])
            if group == "types":
                ids.update(f["id"] for f in entity.get("fields", []))
            if group == "behaviors":
                ids.update(e["id"] for key in ("inputs", "conditions", "guarantees") for e in entity[key])
    return ids


def evaluate(plan, model_path=None):
    """Return a report and candidate without writing. Errors bar application."""
    diagnostics = []
    path = Path(model_path or plan["model"])
    raw = path.read_bytes()
    if blob_hash(raw) != plan["baseline"]:
        diagnostics.append({"severity": "ERROR", "message": "source model differs from plan baseline"})
    original = validate(load(path))
    candidate = None
    touched = set()
    try:
        candidate, touched = transform(original, plan["operations"])
        validate(candidate)
    except (AirError, KeyError, TypeError, ValueError) as exc:
        diagnostics.append({"severity": "ERROR", "message": str(exc)})
        candidate = None
    old_entities, _ = index(original)
    roots = sorted(eid for eid in touched if eid in old_entities)
    paths = {root: impact(original, root) for root in roots}
    direct = {entry["id"] for graph in paths.values() for entry in graph["impacts"] if entry["depth"] == 1}
    expected = plan["anticipated_impacts"]
    candidate_ids = index(candidate)[0] if candidate is not None else {}
    if not isinstance(expected, list) or any(not isinstance(e, str) or e not in old_entities and e not in candidate_ids for e in expected) or len(expected) != len(set(expected)):
        diagnostics.append({"severity": "ERROR", "message": "anticipated impacts must be unique existing or proposed entity IDs"})
        expected = []
    for missing in sorted(direct - set(expected) - touched):
        diagnostics.append({"severity": "WARNING", "message": f"direct dependent omitted from anticipated impacts: {missing}"})
    verification = plan["verification"]
    if not isinstance(verification, dict) or not isinstance(verification.get("preserve"), list) or not isinstance(verification.get("add"), list) or not verification["preserve"] + verification["add"]:
        diagnostics.append({"severity": "ERROR", "message": "behavioral plan requires verification"})
    if candidate is not None:
        changes = diff(original, candidate)
        changed_ids = {change["entity_id"] for change in changes["changes"]}
        unchanged_expected = sorted(set(expected) - changed_ids)
        if unchanged_expected:
            diagnostics.append({"severity": "INFORMATION", "message":
                                "anticipated dependents without structural edits: " + ", ".join(unchanged_expected)})
        categories = {"contracts": [], "effects": [], "interfaces": [], "persistence": []}
        new_entities, _ = index(candidate)
        for change in changes["changes"]:
            eid = change["entity_id"]
            kind = new_entities.get(eid, old_entities.get(eid))[0]
            if kind in ("precondition", "postcondition", "invariant", "scenario", "transition", "state_machine"):
                categories["contracts"].append(change)
            if kind in ("capability", "transition") or kind == "behavior" and (change["change"] in ("added", "removed") or set(change.get("attributes", [])) & {"effects", "requires", "performs"}):
                categories["effects"].append(change)
            if kind in ("command", "input"):
                categories["interfaces"].append(change)
            if kind in ("state", "migration") or (kind == "field" and change["change"] in ("added", "removed")):
                categories["persistence"].append(change)
    else:
        changes, categories = None, None
    return {"plan_id": plan["id"], "diagnostics": diagnostics, "roots": roots,
            "impact_paths": paths, "anticipated_impacts": expected, "proposed_diff": changes,
            "categories": categories, "verification": verification}, candidate


def apply(plan, model_path=None, artifact_path=None):
    report, candidate = evaluate(plan, model_path)
    if any(d["severity"] == "ERROR" for d in report["diagnostics"]):
        raise AirError("plan validation failed: " + "; ".join(d["message"] for d in report["diagnostics"] if d["severity"] == "ERROR"))
    model = Path(model_path or plan["model"])
    artifact = Path(artifact_path or "generated/task_manager.py")
    manifest = artifact.with_suffix(".manifest.json")
    original = validate(load(model))
    source = generate(candidate)
    ids, _ = index(candidate)
    metadata = {"compiler_version": VERSION, "model_version": candidate.version,
                "application_id": candidate.document["application"]["id"],
                "artifacts": [{"path": artifact.name, "sha256": hashlib.sha256(source.encode()).hexdigest(), "entity_ids": sorted(ids)}]}
    replacements = {model: (json.dumps(candidate.document, indent=2, ensure_ascii=False) + "\n").encode(),
                    artifact: source.encode(), manifest: (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()}
    originals = {path: path.read_bytes() if path.exists() else None for path in replacements}
    with tempfile.TemporaryDirectory(dir=model.parent) as temp:
        staged = {}
        for n, (path, content) in enumerate(replacements.items()):
            target = Path(temp) / str(n)
            target.write_bytes(content)
            staged[path] = target
        if blob_hash(model.read_bytes()) != plan["baseline"]:
            raise AirError("source model changed during planning")
        try:
            for path, staged_path in staged.items():
                os.replace(staged_path, path)
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], capture_output=True, text=True)
            report["verification_result"] = {"exit_code": result.returncode, "output": result.stdout + result.stderr}
            if result.returncode:
                raise AirError("verification failed; model and artifacts rolled back\n" + result.stdout + result.stderr)
        except BaseException:
            for path, content in originals.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    restore = Path(temp) / ("restore_" + path.name)
                    restore.write_bytes(content)
                    os.replace(restore, path)
            raise
    actual = diff(original, candidate)
    changed = {c["entity_id"] for c in actual["changes"]}
    predicted = set(report["anticipated_impacts"]) | set(report["roots"])
    report["actual_diff"] = actual
    report["comparison"] = {category: sorted(values) for category, values in {
        "EXPECTED_AND_CHANGED": predicted & changed,
        "EXPECTED_BUT_UNCHANGED": predicted - changed,
        "UNEXPECTEDLY_CHANGED": changed - predicted}.items()}
    return report
