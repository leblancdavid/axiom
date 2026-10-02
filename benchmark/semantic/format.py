"""Prospective semantic-requirement *prototype*, not an acceptance runner.

The JSON format describes black-box scenarios as ordered operations and
observations. Validation/compilation never imports an application or infers
requirements from Python tests. Frozen acceptance remains R5.2.2.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


VERSION = "LYKOI-BENCHMARK-SEMANTIC-PROTOTYPE/2"
LEGACY_VERSION = "LYKOI-BENCHMARK-SEMANTIC-PROTOTYPE/1"
COMMANDS = frozenset({"create", "complete", "delete", "archive", "migrate",
                      "list", "list-high", "list-overdue", "list-tag",
                      "list-status", "list-category", "list-archived", "list-due",
                      "list-owner", "list-urgent", "list-users", "create-user",
                      "add-dependency", "append-note", "list-audit",
                      "create-project", "add-project-member", "list-project",
                      "list-projects"})


class FormatError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise FormatError(message)


def keys(value, expected, where):
    require(isinstance(value, dict) and set(value) == set(expected),
            f"{where}: expected {sorted(expected)}")


def identifier(value, where):
    require(isinstance(value, str) and bool(value) and
            all(part.isidentifier() for part in value.split(".")),
             f"{where}: invalid identifier")


def utc_instant(value, where):
    require(isinstance(value, str) and value.endswith("Z"),
            f"{where}: expected UTC timestamp with Z")
    try:
        instant = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise FormatError(f"{where}: invalid UTC timestamp") from exc
    require(instant.tzinfo == timezone.utc, f"{where}: invalid UTC timestamp")
    return instant


def expression(value, bound, where):
    require(isinstance(value, dict) and len(value) == 1,
            f"{where}: expected expression")
    kind, operand = next(iter(value.items()))
    if kind == "literal":
        # JSON values only: loading from JSON already excludes host expressions.
        return "json"
    if kind == "ref":
        require(isinstance(operand, str) and operand and
                operand.split(".")[0].isidentifier() and
                all(part.isidentifier() or part.isdecimal()
                    for part in operand.split(".")[1:]),
                f"{where}: invalid reference")
        require(operand.split(".")[0] in bound, f"{where}: unbound {operand}")
        return "json"
    if kind == "instant":
        # An explicitly typed projection of an application result or a UTC literal.
        require(isinstance(operand, dict) and len(operand) == 1,
                f"{where}: invalid instant")
        if "literal" in operand:
            utc_instant(operand["literal"], where)
        else:
            require("ref" in operand, f"{where}: instant needs literal or ref")
            expression(operand, bound, where)
        return "instant"
    if kind == "clock_ref":
        require(isinstance(operand, str) and bound.get(operand) == "instant",
                f"{where}: undeclared clock reference")
        return "instant"
    if kind == "offset":
        keys(operand, ("from", "seconds"), where)
        require(isinstance(operand["seconds"], int) and
                not isinstance(operand["seconds"], bool),
                f"{where}: offset must be integral seconds")
        require(expression(operand["from"], bound, where) == "instant",
                f"{where}: offset needs instant")
        return "instant"
    if kind == "list":
        require(isinstance(operand, list), f"{where}: expected list")
        for item in operand:
            expression(item, bound, where)
        return "json"
    if kind == "sorted":
        keys(operand, ("items", "by"), where)
        expression(operand["items"], bound, where)
        require(isinstance(operand["by"], list) and operand["by"] and
                len(operand["by"]) == len(set(operand["by"])) and
                all(isinstance(field, str) and field.isidentifier()
                    for field in operand["by"]), f"{where}: invalid sort keys")
        return "json"
    raise FormatError(f"{where}: unknown expression {kind}")


def validate(document):
    keys(document, ("version", "status", "scenarios"), "document")
    require(document["version"] in (LEGACY_VERSION, VERSION) and
            document["status"] == "prototype",
            "unrecognized prototype version/status")
    require(isinstance(document["scenarios"], list) and document["scenarios"],
            "empty scenarios")
    scenario_ids = set()
    observation_ids = set()
    for scenario in document["scenarios"]:
        keys(scenario, ("id", "origin", "lineage", "variants"), "scenario")
        identifier(scenario["id"], "scenario ID")
        require(scenario["id"] not in scenario_ids, "duplicate scenario ID")
        scenario_ids.add(scenario["id"])
        origin = scenario["origin"]
        keys(origin, ("requirement", "source", "note"), "origin")
        require(isinstance(origin["requirement"], str) and
                origin["requirement"] in {f"B{i:02}" for i in range(1, 21)} and
                origin["source"] == f"benchmark/requirements/{origin['requirement']}.md" and
                isinstance(origin["note"], str) and origin["note"].strip(),
                "invalid frozen origin")
        lineage = scenario["lineage"]
        keys(lineage, ("kind", "prior"), "lineage")
        require(lineage["kind"] in ("adds", "retains", "replaces") and
                isinstance(lineage["prior"], list) and
                len(lineage["prior"]) == len(set(lineage["prior"])) and
                all(isinstance(root, str) and root for root in lineage["prior"]) and
                bool(lineage["prior"]) == (lineage["kind"] != "adds"),
                "invalid lineage")
        require(isinstance(scenario["variants"], list) and scenario["variants"],
                "missing variants")
        variant_ids = set()
        guards = []
        for variant in scenario["variants"]:
            require(isinstance(variant, dict) and set(variant) in
                    ({"id", "when", "steps"}, {"id", "when", "steps", "carrier"}),
                    "invalid variant")
            if "carrier" in variant:
                require(isinstance(variant["carrier"], str) and variant["carrier"],
                        "invalid historical carrier")
            identifier(variant["id"], "variant ID")
            require(variant["id"] not in variant_ids, "duplicate variant ID")
            variant_ids.add(variant["id"])
            keys(variant["when"], ("requires", "forbids"), "when")
            required, forbidden = (variant["when"][key] for key in ("requires", "forbids"))
            for names in (required, forbidden):
                require(isinstance(names, list) and len(names) == len(set(names)) and
                        all(isinstance(n, str) and n in
                            {f"B{i:02}" for i in range(1, 21)} for n in names),
                        "invalid achieved-history guard")
            require(origin["requirement"] in required and
                    not set(required) & set(forbidden), "inconsistent origin/guard")
            for old_required, old_forbidden in guards:
                require(bool(set(required) & old_forbidden or
                             old_required & set(forbidden)),
                        "overlapping variants for one semantic ID")
            guards.append((set(required), set(forbidden)))
            steps = variant["steps"]
            require(isinstance(steps, list) and steps, "empty scenario variant")
            bound = {}
            observed = False
            for step in steps:
                require(isinstance(step, dict) and len(step) == 1,
                        "expected one step kind")
                kind, body = next(iter(step.items()))
                if kind == "invoke":
                    require(isinstance(body, dict) and set(body) in
                            ({"command", "args", "bind"}, {"command", "args", "error"}),
                            "invalid invocation")
                    require(body["command"] in COMMANDS and
                            isinstance(body["args"], list), "unknown command/arguments")
                    for arg in body["args"]:
                        expression(arg, bound, "argument")
                        require("literal" not in arg or isinstance(arg["literal"], str),
                                "CLI literal must be a string")
                    if "error" in body:
                        require(isinstance(body["error"], str) and body["error"],
                                "invalid error")
                    else:
                        identifier(body["bind"], "result binding")
                        require("." not in body["bind"] and body["bind"] not in bound,
                                "duplicate result binding")
                        bound[body["bind"]] = "json"
                elif kind == "clock":
                    keys(body, ("bind", "source"), "clock")
                    identifier(body["bind"], "clock binding")
                    require(body["source"] == "utc_now" and
                            "." not in body["bind"] and body["bind"] not in bound,
                            "invalid or duplicate clock binding")
                    bound[body["bind"]] = "instant"
                elif kind == "snapshot":
                    keys(body, ("path", "bind"), "snapshot")
                    require(body["path"] == "tasks.json", "unknown storage observation")
                    identifier(body["bind"], "snapshot binding")
                    require("." not in body["bind"] and body["bind"] not in bound,
                            "duplicate snapshot binding")
                    bound[body["bind"]] = "json"
                elif kind == "seed":
                    keys(body, ("path", "value"), "seed")
                    require(body["path"] == "tasks.json" and
                            isinstance(body["value"], (dict, list)), "invalid storage seed")
                elif kind == "observe":
                    require(isinstance(body, dict) and set(body) in
                            ({"id", "relation", "actual", "expected"},
                             {"id", "relation", "values"},
                             {"id", "relation", "actual", "expected", "result"}),
                            "invalid observation")
                    identifier(body["id"], "observation ID")
                    require(body["id"] not in observation_ids, "duplicate observation ID")
                    observation_ids.add(body["id"])
                    if body["relation"] == "equals":
                        require(set(body) == {"id", "relation", "actual", "expected"},
                                "equals needs actual and expected")
                        expression(body["actual"], bound, "actual")
                        expression(body["expected"], bound, "expected")
                    elif body["relation"] == "distinct":
                        require(set(body) == {"id", "relation", "values"} and
                                isinstance(body["values"], list) and
                                len(body["values"]) >= 2, "distinct needs values")
                        for item in body["values"]:
                            expression(item, bound, "distinct value")
                    elif body["relation"] == "before":
                        require(set(body) == {"id", "relation", "actual", "expected", "result"}
                                and type(body["result"]) is bool,
                                "before needs two instants and boolean result")
                        require(expression(body["actual"], bound, "actual") == "instant" and
                                expression(body["expected"], bound, "expected") == "instant",
                                "before requires two typed instants")
                    else:
                        raise FormatError("unknown observation relation")
                    observed = True
                else:
                    raise FormatError(f"unknown step: {kind}")
            require(observed, "variant has no observation")
    return document


def load(path):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))


def compile_plan(document, achieved):
    """Deterministically select scenario plans; does not execute or attest them."""
    validate(document)
    require(isinstance(achieved, list) and len(achieved) == len(set(achieved)) and
            all(isinstance(item, str) and item in {f"B{i:02}" for i in range(1, 21)}
                for item in achieved), "invalid achieved history")
    active = set(achieved)
    result = []
    for scenario in document["scenarios"]:
        for variant in scenario["variants"]:
            when = variant["when"]
            if set(when["requires"]) <= active and not set(when["forbids"]) & active:
                result.append({"semantic_id": scenario["id"], "variant": variant["id"],
                               "steps": variant["steps"]})
    return result
