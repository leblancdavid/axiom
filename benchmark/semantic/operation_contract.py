"""Unfrozen typed operation-tuple witnesses; no application adapter or proof."""

from benchmark.semantic.format import require
from benchmark.semantic import state_relations


SLOTS = {"input.rows", "pre.records", "result", "post.records"}


def validate(document):
    require(isinstance(document, dict) and set(document) ==
            {"status", "schema", "operation", "checks", "cases"} and
            document["status"] == "prototype" and
            isinstance(document["operation"], str) and
            document["operation"].isidentifier(), "invalid operation contract")
    schema = document["schema"]
    checks = document["checks"]
    require(isinstance(checks, list) and checks, "missing checks")
    for check in checks:
        require(isinstance(check, dict) and set(check) == {"kind", "left", "right"} and
                check["kind"] in ("equals", "default_missing") and
                check["left"] in SLOTS and check["right"] in SLOTS,
                "invalid typed binding")
    # Reuse the existing relation's schema/default validation, including types.
    default = [c for c in checks if c["kind"] == "default_missing"]
    require(len(default) == 1 and default[0]["left"] == "pre.records" and
            default[0]["right"] == "post.records" and
            isinstance(schema, dict) and set(schema) == {"record", "default"},
            "invalid transition binding")
    rule = {"schema": schema["record"], "relation": schema["default"],
            "cases": [{"id": "type_probe", "before": [], "after": [], "holds": True}]}
    state_relations.validate(rule)
    require(isinstance(document["cases"], list) and document["cases"], "missing witnesses")
    ids = set()
    for case in document["cases"]:
        require(isinstance(case, dict) and set(case) ==
                {"id", "input", "pre", "result", "post", "holds"} and
                isinstance(case["id"], str) and case["id"] not in ids and
                type(case["holds"]) is bool and
                isinstance(case["input"], dict) and set(case["input"]) == {"rows"} and
                isinstance(case["pre"], dict) and set(case["pre"]) == {"records"} and
                isinstance(case["post"], dict) and set(case["post"]) == {"records"} and
                all(state_relations._sequence(rows, schema["record"], schema["default"])
                    for rows in (case["input"]["rows"], case["pre"]["records"],
                                 case["result"], case["post"]["records"])),
                "invalid operation witness")
        ids.add(case["id"])
    return document


def evaluate(document, case):
    values = {"input.rows": case["input"]["rows"],
              "pre.records": case["pre"]["records"],
              "result": case["result"], "post.records": case["post"]["records"]}
    for check in document["checks"]:
        left, right = values[check["left"]], values[check["right"]]
        if check["kind"] == "equals":
            if left != right:
                return False
        elif not state_relations.evaluate(
                {"schema": document["schema"]["record"],
                 "relation": document["schema"]["default"]},
                {"before": left, "after": right}):
            return False
    return True


def run_witnesses(document):
    validate(document)
    return {case["id"]: evaluate(document, case) for case in document["cases"]}
