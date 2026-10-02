"""Unfrozen, declarative universal-rule prototype; independent of CLI scenarios.

Finite cases exercise rules, but never establish their universal truth.
"""

from benchmark.semantic.format import FormatError, identifier, require
from benchmark.semantic import relationships


TYPES = {"string", "boolean", "sequence[string]", "graph[string]"}
DOMAINS = {"finite_sequence", "finite_directed_graph"}


def _expr(node, variables, where):
    require(isinstance(node, dict) and len(node) == 1, f"{where}: invalid expression")
    op, arg = next(iter(node.items()))
    if op == "var":
        require(isinstance(arg, str) and arg in variables, f"{where}: undeclared variable")
        return variables[arg]
    if op == "literal":
        require(type(arg) in (str, bool), f"{where}: invalid literal")
        return "boolean" if type(arg) is bool else "string"
    if op == "trim":
        require(_expr(arg, variables, where) == "string", f"{where}: trim needs string")
        return "string"
    if op == "map":
        require(isinstance(arg, dict) and set(arg) == {"sequence", "transform"} and
                arg["transform"] == "trim", f"{where}: invalid collection operation")
        require(_expr(arg["sequence"], variables, where) == "sequence[string]",
                f"{where}: map needs string sequence")
        return "sequence[string]"
    if op == "stable_unique":
        require(isinstance(arg, dict) and set(arg) == {"sequence", "equality"} and
                arg["equality"] == "case_sensitive_string",
                f"{where}: invalid comparison")
        require(_expr(arg["sequence"], variables, where) == "sequence[string]",
                f"{where}: stable_unique needs string sequence")
        return "sequence[string]"
    if op == "nonblank":
        require(_expr(arg, variables, where) == "string", f"{where}: nonblank needs string")
        return "boolean"
    if op == "for_each":
        require(isinstance(arg, dict) and set(arg) == {"sequence", "bind", "property"},
                f"{where}: malformed quantifier scope")
        require(_expr(arg["sequence"], variables, where) == "sequence[string]",
                f"{where}: quantifier needs sequence")
        identifier(arg["bind"], where)
        require("." not in arg["bind"] and arg["bind"] not in variables,
                f"{where}: duplicate bound variable")
        require(_expr(arg["property"], {**variables, arg["bind"]: "string"}, where)
                == "boolean", f"{where}: quantifier needs property")
        return "boolean"
    if op in ("equals", "and"):
        require(isinstance(arg, list) and len(arg) >= 2, f"{where}: invalid {op}")
        types = [_expr(item, variables, where) for item in arg]
        require(all(t == types[0] for t in types) and
                (op != "and" or types[0] == "boolean"),
                f"{where}: invalid comparison")
        return "boolean"
    if op == "not":
        require(_expr(arg, variables, where) == "boolean", f"{where}: not needs boolean")
        return "boolean"
    if op == "add_edge":
        require(isinstance(arg, dict) and set(arg) == {"graph", "from", "to"},
                f"{where}: invalid graph expression")
        require(_expr(arg["graph"], variables, where) == "graph[string]" and
                _expr(arg["from"], variables, where) == "string" and
                _expr(arg["to"], variables, where) == "string",
                f"{where}: invalid relation")
        return "graph[string]"
    if op == "acyclic":
        require(_expr(arg, variables, where) == "graph[string]",
                f"{where}: acyclic needs directed graph")
        return "boolean"
    raise FormatError(f"{where}: unknown expression {op}")


def _value(value, kind):
    if kind == "string":
        return type(value) is str
    if kind == "boolean":
        return type(value) is bool
    if kind == "sequence[string]":
        return isinstance(value, list) and all(type(x) is str for x in value)
    return (isinstance(value, dict) and set(value) == {"nodes", "edges"} and
            isinstance(value["nodes"], list) and
            all(type(n) is str for n in value["nodes"]) and
            len(value["nodes"]) == len(set(value["nodes"])) and
            isinstance(value["edges"], list) and
            all(isinstance(e, list) and len(e) == 2 and
                all(type(n) is str and n in value["nodes"] for n in e)
                for e in value["edges"]) and
            len({tuple(e) for e in value["edges"]}) == len(value["edges"]))


def validate(document):
    require(isinstance(document, dict) and set(document) ==
            {"status", "invariants", "scenarios"} and document["status"] == "prototype",
            "invalid invariant document")
    require(isinstance(document["invariants"], list) and document["invariants"],
            "missing invariants")
    require(isinstance(document["scenarios"], list), "invalid witness scenarios")
    scenarios, cases = set(), set()
    for scenario in document["scenarios"]:
        require(isinstance(scenario, dict) and set(scenario) == {"id", "cases"} and
                isinstance(scenario["cases"], list) and scenario["cases"],
                "invalid witness scenario")
        identifier(scenario["id"], "scenario ID")
        require(scenario["id"] not in scenarios, "duplicate scenario ID")
        scenarios.add(scenario["id"])
        for case in scenario["cases"]:
            require(isinstance(case, dict) and set(case) == {"id", "bindings"} and
                    isinstance(case["bindings"], dict), "invalid derived case")
            identifier(case["id"], "case ID")
            require(case["id"] not in cases, "duplicate case ID")
            cases.add(case["id"])
    records, links = [], set()
    for rule in document["invariants"]:
        require(isinstance(rule, dict) and set(rule) ==
                {"id", "scope", "bindings", "precondition", "transition", "property",
                 "origin", "when", "depends_on", "replaces", "witnesses"},
                "invalid invariant record")
        require(isinstance(rule["origin"], dict) and set(rule["origin"]) ==
                {"requirement", "source", "note"}, "invalid provenance")
        origin = rule["origin"]
        require(isinstance(origin["requirement"], str) and
                origin["requirement"] in {f"B{i:02}" for i in range(1, 17)} and
                origin["source"] == f"benchmark/requirements/{origin['requirement']}.md" and
                isinstance(origin["note"], str) and origin["note"].strip(),
                "invalid frozen provenance")
        require(isinstance(rule["scope"], dict) and set(rule["scope"]) ==
                {"kind", "domain"} and rule["scope"]["kind"] == "transition" and
                isinstance(rule["scope"]["domain"], str) and
                rule["scope"]["domain"] in DOMAINS, "invalid quantifier scope")
        variables = rule["bindings"]
        require(isinstance(variables, dict) and variables and
                all(isinstance(k, str) and k.isidentifier() and
                    isinstance(v, str) and v in TYPES
                    for k, v in variables.items()), "unknown type or invalid bound variables")
        require(isinstance(rule["transition"], dict) and
                set(rule["transition"]) == {"before", "after"} and
                all(isinstance(v, str) and v in variables
                    for v in rule["transition"].values()),
                "invalid transition")
        before, after = (variables[rule["transition"][k]] for k in ("before", "after"))
        domain_type = ("sequence[string]" if rule["scope"]["domain"] ==
                       "finite_sequence" else "graph[string]")
        require(before == after == domain_type, "transition/domain type mismatch")
        if rule["precondition"] is not None:
            require(_expr(rule["precondition"], variables, "precondition") == "boolean",
                    "invalid precondition")
        require(_expr(rule["property"], variables, "property") == "boolean",
                "invalid postcondition")
        require(isinstance(rule["witnesses"], list) and rule["witnesses"],
                "missing executable witness links")
        for link in rule["witnesses"]:
            require(isinstance(link, dict) and set(link) == {"scenario", "case"} and
                    isinstance(link["scenario"], str) and
                    isinstance(link["case"], str) and
                    link["scenario"] in scenarios and link["case"] in cases and
                    any(s["id"] == link["scenario"] and
                        any(c["id"] == link["case"] for c in s["cases"])
                        for s in document["scenarios"]), "unknown semantic witness reference")
            require((rule["id"], link["case"]) not in links, "duplicate witness link")
            links.add((rule["id"], link["case"]))
        records.append({"id": rule["id"], "origin": origin["requirement"],
                        "when": rule["when"], "depends_on": rule["depends_on"],
                        "replaces": rule["replaces"]})
    relationships.validate(records)
    for scenario in document["scenarios"]:
        for case in scenario["cases"]:
            linked = [r for r in document["invariants"] if
                      (r["id"], case["id"]) in links]
            require(linked, "unlinked executable case")
            for rule in linked:
                require(set(case["bindings"]) == set(rule["bindings"]) and
                        all(_value(case["bindings"][k], t)
                            for k, t in rule["bindings"].items()),
                        "invalid witness bindings")
    return document


def evaluate(node, env):
    """Small fixture interpreter, never an application or proof procedure."""
    op, arg = next(iter(node.items()))
    if op == "var":
        return env[arg]
    if op == "literal":
        return arg
    if op == "trim":
        return evaluate(arg, env).strip()
    if op == "map":
        return [s.strip() for s in evaluate(arg["sequence"], env)]
    if op == "stable_unique":
        return list(dict.fromkeys(evaluate(arg["sequence"], env)))
    if op == "nonblank":
        return bool(evaluate(arg, env).strip())
    if op == "for_each":
        return all(evaluate(arg["property"], {**env, arg["bind"]: item})
                   for item in evaluate(arg["sequence"], env))
    if op == "equals":
        values = [evaluate(v, env) for v in arg]
        if all(isinstance(v, dict) and set(v) == {"nodes", "edges"} for v in values):
            return all(set(v["nodes"]) == set(values[0]["nodes"]) and
                       {tuple(e) for e in v["edges"]} ==
                       {tuple(e) for e in values[0]["edges"]}
                       for v in values[1:])
        return all(v == values[0] for v in values[1:])
    if op == "and":
        return all(evaluate(v, env) for v in arg)
    if op == "not":
        return not evaluate(arg, env)
    if op == "add_edge":
        graph = evaluate(arg["graph"], env)
        source, target = evaluate(arg["from"], env), evaluate(arg["to"], env)
        require(source in graph["nodes"] and target in graph["nodes"],
                "edge endpoint outside graph")
        edge = [source, target]
        return {"nodes": graph["nodes"],
                "edges": graph["edges"] + ([] if edge in graph["edges"] else [edge])}
    if op == "acyclic":
        graph = evaluate(arg, env)
        edges = graph["edges"]
        reach = {(a, b) for a, b in edges}
        for middle in graph["nodes"]:
            reach |= {(a, b) for a, mid in reach for mid2, b in reach
                      if mid == middle == mid2}
        return not any((n, n) in reach for n in graph["nodes"])
    raise FormatError(f"unknown expression {op}")


def run_witnesses(document):
    """Return linked case results; a true result only witnesses that finite case."""
    validate(document)
    cases = {case["id"]: case for s in document["scenarios"] for case in s["cases"]}
    results = {}
    for rule in document["invariants"]:
        for link in rule["witnesses"]:
            env = cases[link["case"]]["bindings"]
            applicable = (rule["precondition"] is None or
                          evaluate(rule["precondition"], env))
            results[(rule["id"], link["scenario"], link["case"])] = (
                applicable, evaluate(rule["property"], env) if applicable else None)
    return results
