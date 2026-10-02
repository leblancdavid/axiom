"""Prospective state-relative capability composition; legacy composer stays frozen."""

import copy
import json

import capability_profile as legacy
import workspace as w


FRAGMENTS = legacy.FRAGMENTS


def apply_fragment(prior, request, data):
    """Apply a frozen declaration to an independently achieved prior contract."""
    result = copy.deepcopy(prior)
    allowed = {"schema_increment", "requires", "add_fields", "change_defaults",
               "supersedes_cases", "ensure_fields"}
    w.require(isinstance(data, dict) and {"schema_increment", "requires", "add_fields"} <= set(data)
              and set(data) <= allowed and type(data["schema_increment"]) is int
              and data["schema_increment"] >= 0 and isinstance(data["requires"], list)
              and len(data["requires"]) == len(set(data["requires"]))
              and all(isinstance(dep, str) and dep in prior["achieved"] for dep in data["requires"])
              and isinstance(data["add_fields"], dict),
              f"invalid capability fragment: {request}")
    added = data["add_fields"]
    changed = data.get("change_defaults", {})
    ensured = data.get("ensure_fields", {})
    w.require(isinstance(changed, dict) and isinstance(ensured, dict) and
              not (set(added) & set(changed) or set(added) & set(ensured) or
                   set(changed) & set(ensured)), f"conflicting field operations: {request}")
    for field, contribution in added.items():
        w.require(isinstance(field, str) and field.isidentifier() and field not in result["fields"]
                  and isinstance(contribution, dict) and set(contribution) == {"default", "type"}
                  and contribution["type"] in legacy.TYPES
                  and type(contribution["default"]) is legacy.TYPES[contribution["type"]],
                  f"conflicting or invalid field contribution: {request}:{field}")
        result["fields"].append(field)
        result["migration_defaults"][field] = contribution["default"]
        result["field_types"][field] = contribution["type"]
    for field, change in changed.items():
        defaults = result["migration_defaults"]
        w.require(field in defaults and isinstance(change, dict) and
                  set(change) == {"from", "to"} and defaults[field] == change["from"]
                  and type(defaults[field]) is type(change["to"]),
                  f"conflicting default change: {request}:{field}")
        defaults[field] = change["to"]
    for field, rule in ensured.items():
        w.require(isinstance(field, str) and field.isidentifier() and
                  isinstance(rule, dict) and set(rule) == {"type", "default", "from"}
                  and rule["type"] in legacy.TYPES and
                  type(rule["default"]) is legacy.TYPES[rule["type"]] and
                  isinstance(rule["from"], list) and len(rule["from"]) ==
                  len({json.dumps(value, sort_keys=True) for value in rule["from"]}) and
                  all(type(value) is legacy.TYPES[rule["type"]] for value in rule["from"]),
                  f"invalid state-relative declaration: {request}:{field}")
        if field in result["fields"]:
            w.require(field in result["migration_defaults"] and
                      result["field_types"].get(field) == rule["type"] and
                      any(type(result["migration_defaults"][field]) is type(value) and
                          result["migration_defaults"][field] == value for value in rule["from"]),
                      f"incompatible achieved field: {request}:{field}")
        else:
            result["fields"].append(field)
            result["field_types"][field] = rule["type"]
        result["migration_defaults"][field] = copy.deepcopy(rule["default"])
    supersessions = data.get("supersedes_cases", {})
    w.require(isinstance(supersessions, dict), f"invalid supersessions: {request}")
    for test_id, replacement in supersessions.items():
        w.require(isinstance(test_id, str) and test_id and
                  test_id not in result["superseded_cases"] and
                  isinstance(replacement, dict) and
                  set(replacement) == {"reason", "replacement", "origin"} and
                  isinstance(replacement["reason"], str) and replacement["reason"].strip() and
                  replacement["replacement"] == request and
                  (replacement["origin"] == "baseline" or
                   (replacement["origin"] in w.load_manifest()["requirements"] and
                    replacement["origin"] < request)),
                  f"invalid or conflicting case supersession: {request}:{test_id}")
        result["superseded_cases"][test_id] = copy.deepcopy(replacement)
    result["schema_version"] += data["schema_increment"]
    result["achieved"].append(request)
    return result


def compose(achieved):
    w.require(isinstance(achieved, list) and len(achieved) == len(set(achieved)) and
              achieved == sorted(achieved) and
              all(name in w.load_manifest()["requirements"] for name in achieved),
              "invalid achieved capability history")
    first = next((index for index, name in enumerate(achieved)
                  if "ensure_fields" in json.loads((FRAGMENTS / f"{name}.json").read_text(encoding="utf-8"))),
                 len(achieved))
    if first == len(achieved):
        return legacy.compose(achieved)
    result = legacy.compose(achieved[:first])
    for request in achieved[first:]:
        data = json.loads((FRAGMENTS / f"{request}.json").read_text(encoding="utf-8"))
        result = apply_fragment(result, request, data)
    return result


def identity(achieved):
    profile = compose(achieved)
    return {"capability_hashes": legacy.fragment_hashes(achieved),
            "baseline_profile_sha256": w.file_hash(legacy.BASELINE),
            "expectation": profile, "expectation_sha256": w.digest(w.encoded(profile))}
