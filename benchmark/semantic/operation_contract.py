"""R5.4 combined fixture compatibility; R5.5 keeps its cases as synthetic evidence."""

from benchmark.semantic.format import require
from benchmark.semantic import contracts


SLOTS = contracts.SLOTS


def abstract_contract(document):
    """Explicit migration of the R5.4 mixed document; never reinterpret cases as traces."""
    return {key: document[key] for key in ("operation", "schema", "checks")}


def values(case):
    return {"input.rows": case["input"]["rows"],
            "pre.records": case["pre"]["records"],
            "result": case["result"], "post.records": case["post"]["records"]}


def validate(document):
    require(isinstance(document, dict) and set(document) ==
            {"status", "schema", "operation", "checks", "cases"} and
            document["status"] == "prototype" and
            isinstance(document["operation"], str) and
            document["operation"].isidentifier(), "invalid operation contract")
    contract = abstract_contract(document)
    contracts.validate(contract)
    default = [c for c in contract["checks"] if c["kind"] == "default_missing"]
    require(len(default) == 1 and default[0]["left"] == "pre.records" and
            default[0]["right"] == "post.records",
            "invalid transition binding")
    require(isinstance(document["cases"], list) and document["cases"], "missing witnesses")
    ids = set()
    for case in document["cases"]:
        require(isinstance(case, dict) and set(case) ==
                {"id", "input", "pre", "result", "post", "holds"} and
                isinstance(case["id"], str) and case["id"] not in ids and
                type(case["holds"]) is bool and
                isinstance(case["input"], dict) and set(case["input"]) == {"rows"} and
                isinstance(case["pre"], dict) and set(case["pre"]) == {"records"} and
                isinstance(case["post"], dict) and set(case["post"]) == {"records"},
                "invalid operation witness")
        contracts.validate_values(contract, values(case))
        ids.add(case["id"])
    return document


def evaluate(document, case):
    return contracts.evaluate(abstract_contract(document), values(case))


def run_witnesses(document):
    validate(document)
    return {case["id"]: evaluate(document, case) for case in document["cases"]}
