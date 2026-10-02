"""Unfrozen typed order and keyed migration constraints; cases are witnesses."""

from datetime import datetime, timezone
import json

from benchmark.semantic.format import require


KINDS = {"string", "boolean", "instant"}


def validate(rule):
    require(isinstance(rule, dict) and set(rule) == {"schema", "relation", "cases"},
            "invalid state relation")
    schema = rule["schema"]
    require(isinstance(schema, dict) and schema and all(
        isinstance(k, str) and k.isidentifier() and v in KINDS
        for k, v in schema.items()), "invalid record schema")
    relation = rule["relation"]
    require(isinstance(relation, dict) and relation.get("kind") in
            ("lexicographic_order", "default_missing"), "invalid relation kind")
    if relation["kind"] == "lexicographic_order":
        require(set(relation) == {"kind", "keys"} and
                isinstance(relation["keys"], list) and relation["keys"] and
                len(relation["keys"]) == len(set(relation["keys"])) and
                all(k in schema and schema[k] in ("string", "instant")
                    for k in relation["keys"]),
                "invalid ordered keys")
    else:
        require(set(relation) == {"kind", "identity", "field", "value"} and
                relation["identity"] in schema and schema[relation["identity"]] == "string" and
                relation["field"] in schema and relation["field"] != relation["identity"] and
                _typed(relation["value"], schema[relation["field"]]),
                "invalid default relation")
    require(isinstance(rule["cases"], list) and rule["cases"], "missing witnesses")
    ids = set()
    for case in rule["cases"]:
        require(isinstance(case, dict) and set(case) ==
                {"id", "before", "after", "holds"} and
                isinstance(case["id"], str) and case["id"] not in ids and
                type(case["holds"]) is bool and
                _sequence(case["before"], schema, relation) and
                _sequence(case["after"], schema, relation),
                "invalid witness")
        ids.add(case["id"])
    return rule


def _typed(value, kind):
    if kind == "instant":
        if type(value) is not str or not value.endswith("Z"):
            return False
        try:
            instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return instant.utcoffset() == timezone.utc.utcoffset(instant)
        except ValueError:
            return False
    return type(value) is str if kind == "string" else type(value) is bool


def _sequence(rows, schema, relation):
    if not isinstance(rows, list):
        return False
    optional = (relation["field"] if relation["kind"] == "default_missing" else None)
    return all(isinstance(row, dict) and
               (set(row) == set(schema) or
                (optional is not None and set(row) == set(schema) - {optional})) and
               all(_typed(value, schema[key]) for key, value in row.items())
               for row in rows)


def evaluate(rule, case):
    """Compare observable sequences; does not prescribe an application algorithm."""
    relation = rule["relation"]
    before, after = case["before"], case["after"]
    if relation["kind"] == "lexicographic_order":
        keys = relation["keys"]
        # Multiset equality includes occurrence multiplicity and the full record.
        encode = lambda row: json.dumps(row, sort_keys=True)
        def key(row):
            return tuple(datetime.fromisoformat(row[k].replace("Z", "+00:00"))
                         if rule["schema"][k] == "instant" else row[k] for k in keys)
        return (sorted(map(encode, before)) == sorted(map(encode, after)) and
                all(key(a) < key(b) for a, b in zip(after, after[1:])))
    key, field, default = (relation[k] for k in ("identity", "field", "value"))
    old_ids = [row[key] for row in before]
    new_ids = [row[key] for row in after]
    if len(set(old_ids)) != len(old_ids) or len(set(new_ids)) != len(new_ids) or set(old_ids) != set(new_ids):
        return False
    new = {row[key]: row for row in after}
    return all(new[row[key]] == {**row, **({field: default} if field not in row else {})}
               for row in before)


def run_witnesses(rule):
    validate(rule)
    return {case["id"]: evaluate(rule, case) for case in rule["cases"]}
