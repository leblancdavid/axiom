"""Compose a track-neutral regression contract from achieved capabilities only.

Fragments are frozen per request before the request is given to either track.
Historical profiles are read-only; this module does not import either application.
"""

import json
from pathlib import Path

import workspace as w


FRAGMENTS = Path(__file__).resolve().parent / "capabilities"
BASELINE = w.PROFILES / "baseline.json"
TYPES = {"str": str, "list": list, "int": int, "bool": bool}


def fragment_hashes(achieved):
    result = {}
    for request in achieved:
        path = FRAGMENTS / f"{request}.json"
        w.require(path.is_file(), f"missing frozen capability fragment: {request}")
        result[request] = w.file_hash(path)
    return result


def compose(achieved):
    """Deterministic composition; rejects conflicting or malformed contributions."""
    w.require(isinstance(achieved, list) and len(achieved) == len(set(achieved)) and
              achieved == sorted(achieved) and
              all(name in w.load_manifest()["requirements"] for name in achieved),
              "invalid achieved capability history")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    w.require(set(baseline) == {"schema_version", "fields", "migration_defaults"} and
              set(baseline["fields"]) == set(baseline["migration_defaults"]) | {
                  "id", "title", "description", "status", "created_at"},
              "baseline profile malformed")
    fields = list(baseline["fields"])
    defaults = dict(baseline["migration_defaults"])
    types = {}
    superseded = {}
    version = baseline["schema_version"]
    seen = set()
    for request in achieved:
        data = json.loads((FRAGMENTS / f"{request}.json").read_text(encoding="utf-8"))
        w.require({"schema_increment", "add_fields", "requires"} <= set(data) <=
                  {"schema_increment", "add_fields", "requires", "change_defaults", "supersedes_cases"} and
                  type(data["schema_increment"]) is int and data["schema_increment"] >= 0 and
                  isinstance(data["add_fields"], dict) and isinstance(data["requires"], list) and
                  all(isinstance(dep, str) and dep in seen for dep in data["requires"]),
                  f"invalid capability fragment: {request}")
        for field, contribution in data["add_fields"].items():
            w.require(isinstance(field, str) and field.isidentifier() and field not in fields and
                      isinstance(contribution, dict) and set(contribution) == {"default", "type"} and
                      contribution["type"] in TYPES and
                      type(contribution["default"]) is TYPES[contribution["type"]],
                      f"conflicting or invalid field contribution: {request}:{field}")
            fields.append(field)
            defaults[field] = contribution["default"]
            types[field] = contribution["type"]
        changes = data.get("change_defaults", {})
        w.require(isinstance(changes, dict), f"invalid default changes: {request}")
        for field, change in changes.items():
            w.require(field in defaults and isinstance(change, dict) and
                      set(change) == {"from", "to"} and defaults[field] == change["from"] and
                      type(defaults[field]) is type(change["to"]),
                      f"conflicting default change: {request}:{field}")
            defaults[field] = change["to"]
        supersessions = data.get("supersedes_cases", {})
        w.require(isinstance(supersessions, dict), f"invalid supersessions: {request}")
        for test_id, replacement in supersessions.items():
            w.require(isinstance(test_id, str) and test_id and test_id not in superseded and
                      isinstance(replacement, dict) and
                      set(replacement) == {"reason", "replacement", "origin"} and
                      isinstance(replacement["reason"], str) and replacement["reason"].strip() and
                      replacement["replacement"] == request and
                      (replacement["origin"] == "baseline" or
                       (replacement["origin"] in w.load_manifest()["requirements"] and
                        replacement["origin"] < request)),
                      f"invalid or conflicting case supersession: {request}:{test_id}")
            superseded[test_id] = {"reason": replacement["reason"], "replacement": request,
                                   "origin": replacement["origin"]}
        version += data["schema_increment"]
        seen.add(request)
    return {"schema_version": version, "fields": fields, "migration_defaults": defaults,
            "field_types": types, "achieved": achieved, "superseded_cases": superseded}


def identity(achieved):
    profile = compose(achieved)
    return {"capability_hashes": fragment_hashes(achieved),
            "baseline_profile_sha256": w.file_hash(BASELINE),
            "expectation": profile, "expectation_sha256": w.digest(w.encoded(profile))}
