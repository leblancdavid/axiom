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
    require(isinstance(schema, dict) and set(schema) in
            ({"record", "default"}, {"record", "default", "outcome"}) and
            isinstance(checks, list) and checks, "invalid contract schema or checks")
    state_relations.validate({"schema": schema["record"],
                              "relation": schema["default"],
                              "cases": [{"id": "type_probe", "before": [],
                                         "after": [], "holds": True}]})
    if "outcome" in schema:
        outcome = schema["outcome"]
        require(isinstance(outcome, dict) and set(outcome) == {"variants", "value"} and
                isinstance(outcome["variants"], list) and outcome["variants"] and
                all(isinstance(v, str) and v.isidentifier() for v in outcome["variants"]) and
                len(set(outcome["variants"])) == len(outcome["variants"]) and
                outcome["value"] == "records", "invalid typed outcome domain")
        for check in checks:
            require(_predicate_type(check, True) == "boolean", "invalid contract predicate")
    else:
        for check in checks:
            require(isinstance(check, dict) and set(check) == {"kind", "left", "right"} and
                    check["kind"] in ("equals", "default_missing") and
                    check["left"] in SLOTS and check["right"] in SLOTS,
                    "invalid contract check")
            if check["kind"] == "default_missing":
                require(check["left"] == "pre.records" and
                        check["right"] == "post.records", "invalid transition slots")
    return contract


def _term_type(term):
    require(isinstance(term, dict) and len(term) == 1, "invalid typed term")
    if "ref" in term:
        require(type(term["ref"]) is str, "invalid term reference")
        return {"input.rows": "records", "pre.records": "records",
                "post.records": "records", "result.kind": "string",
                "result.value": "records"}.get(term["ref"])
    if "literal" in term and type(term["literal"]) is str:
        return "string"
    return None


def _predicate_type(expr, typed_outcome):
    require(isinstance(expr, dict) and len(expr) == 1, "invalid contract predicate")
    kind, args = next(iter(expr.items()))
    if kind == "and":
        require(isinstance(args, list) and len(args) >= 2 and
                all(_predicate_type(arg, typed_outcome) == "boolean" for arg in args),
                "invalid conjunction")
    elif kind == "not":
        require(_predicate_type(args, typed_outcome) == "boolean", "invalid negation")
    elif kind in ("equals", "default_missing"):
        require(isinstance(args, list) and len(args) == 2, "invalid relation operands")
        types = [_term_type(arg) for arg in args]
        require(types[0] is not None and types[0] == types[1] and
                (kind != "default_missing" or
                 args == [{"ref": "pre.records"}, {"ref": "post.records"}] or
                 args == [{"ref": "pre.records"}, {"ref": "pre.records"}]),
                "invalid typed relation")
    else:
        require(False, "unknown contract predicate")
    return "boolean"


def validate_values(contract, values):
    validate(contract)
    require(isinstance(values, dict) and set(values) == SLOTS,
            "invalid typed operation values")
    schema = contract["schema"]
    outcome = values["result"]
    if "outcome" in schema:
        require(isinstance(outcome, dict) and set(outcome) == {"kind", "value"} and
                type(outcome["kind"]) is str and
                outcome["kind"] in schema["outcome"]["variants"],
                "invalid typed outcome")
        outcome = outcome["value"]
    require(all(state_relations._sequence(rows, schema["record"], schema["default"])
                for rows in (values["input.rows"], values["pre.records"],
                             outcome, values["post.records"])),
            "invalid typed operation values")
    return values


def _term(term, values):
    if "literal" in term:
        return term["literal"]
    if term["ref"] == "result.kind":
        return values["result"]["kind"]
    if term["ref"] == "result.value":
        return values["result"]["value"]
    return values[term["ref"]]


def _predicate(expr, contract, values):
    kind, args = next(iter(expr.items()))
    if kind == "and":
        return all(_predicate(arg, contract, values) for arg in args)
    if kind == "not":
        return not _predicate(args, contract, values)
    left, right = (_term(arg, values) for arg in args)
    if kind == "equals":
        return left == right
    return state_relations.evaluate(
        {"schema": contract["schema"]["record"],
         "relation": contract["schema"]["default"]},
        {"before": left, "after": right})


def evaluate(contract, values):
    validate_values(contract, values)
    if "outcome" in contract["schema"]:
        return all(_predicate(check, contract, values) for check in contract["checks"])
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
