"""Unfrozen typed, declarative selection relations; finite cases are witnesses only."""

from benchmark.semantic.format import FormatError, require


def _type(node, env, records):
    require(isinstance(node, dict) and len(node) == 1, "invalid selection expression")
    op, arg = next(iter(node.items()))
    if op == "var":
        require(isinstance(arg, str) and arg in env, "undeclared variable")
        return env[arg]
    if op == "literal":
        require(type(arg) in (str, bool), "invalid literal")
        return "boolean" if type(arg) is bool else "string"
    if op == "field":
        require(isinstance(arg, dict) and set(arg) == {"of", "name"}, "invalid field")
        owner = _type(arg["of"], env, records)
        require(owner in records and isinstance(arg["name"], str) and
                arg["name"] in records[owner], "unknown or mistyped field")
        return records[owner][arg["name"]]
    if op == "contains":
        require(isinstance(arg, dict) and set(arg) == {"collection", "element"},
                "invalid membership")
        collection = _type(arg["collection"], env, records)
        require(collection.startswith("sequence[") and
                collection[9:-1] == _type(arg["element"], env, records),
                "membership type mismatch")
        return "boolean"
    if op in ("equals", "and"):
        require(isinstance(arg, list) and len(arg) >= 2, "invalid comparison")
        types = [_type(x, env, records) for x in arg]
        require(all(t == types[0] for t in types) and
                (op != "and" or types[0] == "boolean"), "comparison type mismatch")
        return "boolean"
    if op == "not":
        require(_type(arg, env, records) == "boolean", "not needs boolean")
        return "boolean"
    raise FormatError(f"unknown selection expression {op}")


def _value(value, kind, records):
    if kind == "string":
        return type(value) is str
    if kind == "boolean":
        return type(value) is bool
    if kind.startswith("sequence["):
        return isinstance(value, list) and all(
            _value(x, kind[9:-1], records) for x in value)
    return (kind in records and isinstance(value, dict) and
            set(value) == set(records[kind]) and all(
                _value(value[k], t, records) for k, t in records[kind].items()))


def validate(document):
    require(isinstance(document, dict) and set(document) == {"status", "rules"} and
            document["status"] == "prototype" and isinstance(document["rules"], list) and
            document["rules"], "invalid selection document")
    ids = set()
    for rule in document["rules"]:
        require(isinstance(rule, dict) and set(rule) ==
                {"id", "origin", "depends_on", "records", "bindings", "selection", "cases"},
                "invalid selection rule")
        require(isinstance(rule["id"], str) and rule["id"] not in ids, "duplicate rule ID")
        ids.add(rule["id"])
        require(rule["origin"] in {f"B{i:02}" for i in range(1, 17)},
                "invalid frozen origin")
        require(isinstance(rule["depends_on"], list) and
                len(rule["depends_on"]) == len(set(rule["depends_on"])) and
                all(isinstance(x, str) and x in
                    {"B02.ordered_normalization"} for x in rule["depends_on"]),
                "unknown selection dependency")
        records = rule["records"]
        require(isinstance(records, dict) and all(
            isinstance(name, str) and name.isidentifier() and
            name not in ("string", "boolean") and isinstance(fields, dict) and fields and
            all(isinstance(k, str) and k.isidentifier() and
                v in ("string", "boolean", "sequence[string]")
                for k, v in fields.items()) for name, fields in records.items()),
                "invalid record schema")
        types = {"string", "boolean", "sequence[string]", *records,
                 *(f"sequence[{name}]" for name in records)}
        env = rule["bindings"]
        require(isinstance(env, dict) and env and all(
            isinstance(k, str) and k.isidentifier() and v in types
            for k, v in env.items()), "invalid bindings")
        relation = rule["selection"]
        require(isinstance(relation, dict) and set(relation) ==
                {"source", "bind", "predicate", "result", "ordering", "exactness"},
                "invalid selection relation")
        require(relation["ordering"] == "source_relative" and
                relation["exactness"] in ("exact", "sound_only"),
                "invalid ordering or exactness")
        source = _type(relation["source"], env, records)
        require(source.startswith("sequence[") and
                _type(relation["result"], env, records) == source,
                "selection source/result type mismatch")
        bind = relation["bind"]
        require(isinstance(bind, str) and bind.isidentifier() and bind not in env,
                "invalid bound element")
        require(_type(relation["predicate"], {**env, bind: source[9:-1]}, records)
                == "boolean", "predicate must be boolean")
        cases = rule["cases"]
        require(isinstance(cases, list) and cases, "missing selection witnesses")
        seen = set()
        for case in cases:
            require(isinstance(case, dict) and set(case) == {"id", "bindings", "holds"} and
                    isinstance(case["id"], str) and case["id"] not in seen and
                    type(case["holds"]) is bool and
                    isinstance(case["bindings"], dict) and
                    set(case["bindings"]) == set(env) and
                    all(_value(case["bindings"][k], t, records) for k, t in env.items()),
                    "invalid selection witness")
            seen.add(case["id"])
    return document


def _eval(node, env):
    op, arg = next(iter(node.items()))
    if op == "field":
        return _eval(arg["of"], env)[arg["name"]]
    if op == "contains":
        return _eval(arg["element"], env) in _eval(arg["collection"], env)
    if op == "var":
        return env[arg]
    if op == "literal":
        return arg
    if op == "equals":
        values = [_eval(x, env) for x in arg]
        return all(v == values[0] for v in values[1:])
    if op == "and":
        return all(_eval(x, env) for x in arg)
    if op == "not":
        return not _eval(arg, env)
    raise FormatError(f"unknown selection expression {op}")


def evaluate(rule, bindings):
    """Check an observation against the ordered exact/sound-only relation."""
    relation = rule["selection"]
    source = _eval(relation["source"], bindings)
    result = _eval(relation["result"], bindings)
    selected = [item for item in source if _eval(
        relation["predicate"], {**bindings, relation["bind"]: item})]
    if relation["exactness"] == "exact":
        return result == selected
    # Sound-only is a positional subsequence of qualifying source occurrences.
    it = iter(selected)
    return all(any(candidate == item for candidate in it) for item in result)


def run_witnesses(document):
    validate(document)
    return {(rule["id"], case["id"]): evaluate(rule, case["bindings"])
            for rule in document["rules"] for case in rule["cases"]}
