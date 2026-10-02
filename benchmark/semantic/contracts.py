"""Unfrozen abstract operation relations. No implementation or evidence here."""

from benchmark.semantic.format import require
from benchmark.semantic import state_relations


SLOTS = frozenset(("input.rows", "pre.records", "result", "post.records"))


def validate(contract):
    require(isinstance(contract, dict) and set(contract) ==
            {"operation", "schema", "checks"} and
            isinstance(contract["operation"], str) and
            contract["operation"].isidentifier(), "invalid abstract contract")
    schema, checks = contract["schema"], contract["checks"]
    require(isinstance(schema, dict) and set(schema) == {"record", "default"} and
            isinstance(checks, list) and checks, "invalid contract schema or checks")
    state_relations.validate({"schema": schema["record"],
                              "relation": schema["default"],
                              "cases": [{"id": "type_probe", "before": [],
                                         "after": [], "holds": True}]})
    for check in checks:
        require(isinstance(check, dict) and set(check) == {"kind", "left", "right"} and
                check["kind"] in ("equals", "default_missing") and
                check["left"] in SLOTS and check["right"] in SLOTS,
                "invalid contract check")
        if check["kind"] == "default_missing":
            require(check["left"] == "pre.records" and
                    check["right"] == "post.records", "invalid transition slots")
    return contract


def validate_values(contract, values):
    validate(contract)
    require(isinstance(values, dict) and set(values) == SLOTS and
            all(state_relations._sequence(rows, contract["schema"]["record"],
                                          contract["schema"]["default"])
                for rows in values.values()), "invalid typed operation values")
    return values


def evaluate(contract, values):
    validate_values(contract, values)
    for check in contract["checks"]:
        left, right = values[check["left"]], values[check["right"]]
        if check["kind"] == "equals":
            if left != right:
                return False
        elif not state_relations.evaluate(
                {"schema": contract["schema"]["record"],
                 "relation": contract["schema"]["default"]},
                {"before": left, "after": right}):
            return False
    return True
