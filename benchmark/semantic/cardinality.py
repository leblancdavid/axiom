"""Prospective #30: typed finite-collection cardinality, independent of migration."""

from benchmark.semantic.format import require


def validate(relation):
    """A collection type and an integer-valued term; no arithmetic operators."""
    require(isinstance(relation, dict) and set(relation) == {"element", "fields", "optional"},
            "invalid cardinality relation")
    require(relation["element"] in ("string", "boolean") or
            (isinstance(relation["element"], dict) and relation["element"] and
             all(isinstance(name, str) and name.isidentifier() and
                 kind in ("string", "boolean")
                 for name, kind in relation["element"].items())),
            "invalid cardinality element type")
    require(isinstance(relation["optional"], list) and
            all(isinstance(name, str) for name in relation["optional"]) and
            len(relation["optional"]) == len(set(relation["optional"])) and
            (not relation["optional"] or isinstance(relation["element"], dict)) and
            all(name in relation["element"] for name in relation["optional"]),
            "invalid optional fields")
    require(isinstance(relation["fields"], dict) and relation["fields"] and
            all(isinstance(name, str) and name.isidentifier() and
                kind in ("integer", "string", "boolean")
                for name, kind in relation["fields"].items()) and
            "integer" in relation["fields"].values(), "invalid scalar record type")
    return relation


def _typed(value, kind):
    if kind == "integer":
        return type(value) is int
    if kind == "string":
        return type(value) is str
    return type(value) is bool


def evaluate(relation, collection, outcome, field):
    """Relate an arbitrary finite sequence to one projected integer field."""
    validate(relation)
    require(isinstance(field, str) and field in relation["fields"] and
            relation["fields"][field] == "integer",
            "count field must be integer")
    element = relation["element"]
    require(isinstance(collection, list) and all(
        (isinstance(item, dict) and
         set(element) - set(relation["optional"]) <= set(item) <= set(element) and
         all(_typed(value, element[name]) for name, value in item.items()))
        if isinstance(element, dict) else _typed(item, element)
        for item in collection), "invalid finite collection")
    require(isinstance(outcome, dict) and set(outcome) == set(relation["fields"]) and
            all(_typed(outcome[name], kind) for name, kind in relation["fields"].items()),
            "invalid typed outcome")
    return len(collection) == outcome[field]
