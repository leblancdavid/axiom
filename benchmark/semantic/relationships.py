"""Prospective requirement-ID relationships; independent of executable carriers.

Records here are *not* a reconstructed B01–B16 inventory. They describe the
small checked vocabulary available to a future clause-first bridge.
"""

from benchmark.semantic.format import FormatError, identifier, require


def _request(value):
    return isinstance(value, str) and (
        value == "BASELINE" or value in {f"B{i:02}" for i in range(1, 21)})


def _rank(value):
    return 0 if value == "BASELINE" else int(value[1:])


def validate(records):
    require(isinstance(records, list) and records, "missing semantic records")
    by_id = {}
    for record in records:
        require(isinstance(record, dict) and set(record) ==
                {"id", "origin", "when", "depends_on", "replaces"},
                "invalid semantic record")
        identifier(record["id"], "semantic record ID")
        require(record["id"] not in by_id, "duplicate semantic record ID")
        require(_request(record["origin"]), "invalid originating request")
        when = record["when"]
        require(isinstance(when, dict) and set(when) == {"requires", "forbids"},
                "invalid achieved-history guard")
        for key in ("requires", "forbids"):
            names = when[key]
            require(isinstance(names, list) and
                    all(_request(name) and name != "BASELINE" for name in names) and
                    len(names) == len(set(names)),
                    "invalid achieved-history guard")
        require(not set(when["requires"]) & set(when["forbids"]) and
                (record["origin"] == "BASELINE" or
                 record["origin"] in when["requires"]), "inconsistent guard")
        for field in ("depends_on", "replaces"):
            targets = record[field]
            require(isinstance(targets, list) and all(isinstance(t, str) for t in targets)
                    and len(targets) == len(set(targets)),
                    f"invalid {field}")
            for target in targets:
                identifier(target, f"{field} target")
        require(len(record["replaces"]) <= 1,
                "one semantic record replaces at most one root")
        by_id[record["id"]] = record

    for record in records:
        for target in record["depends_on"]:
            require(target in by_id and target != record["id"],
                    "unknown or self dependency target")
            require(_rank(by_id[target]["origin"]) <= _rank(record["origin"]),
                    "dependency must not originate in a future request")
        for target in record["replaces"]:
            require(target in by_id and target != record["id"],
                    "unknown or self replacement target")
            require(_rank(by_id[target]["origin"]) < _rank(record["origin"]),
                    "replacement needs a prior semantic root")
            require(not by_id[target]["replaces"],
                    "replacement target must name a root, not a descendant")
    visiting, visited = set(), set()

    def visit(key):
        require(key not in visiting, "cyclic semantic dependency")
        if key in visited:
            return
        visiting.add(key)
        for target in by_id[key]["depends_on"]:
            visit(target)
        visiting.remove(key)
        visited.add(key)

    for key in sorted(by_id):
        visit(key)
    return by_id


def compose(records, achieved):
    """Select exact active IDs from achieved history; never inspect track identity."""
    by_id = validate(records)
    require(isinstance(achieved, list) and len(achieved) == len(set(achieved)) and
            all(_request(item) and item != "BASELINE" for item in achieved),
            "invalid achieved history")
    history = set(achieved)
    applicable = {key: record for key, record in by_id.items()
                  if set(record["when"]["requires"]) <= history and
                  not set(record["when"]["forbids"]) & history}
    active = {}  # semantic root -> current active semantic assertion ID
    pending = dict(applicable)
    while pending:
        ready = sorted((record for record in pending.values()
                        if all(target not in pending for target in record["depends_on"])),
                       key=lambda record: (_rank(record["origin"]), record["id"]))
        require(ready, "missing required dependency or cyclic active relationships")
        record = ready[0]
        key = record["id"]
        for target in record["depends_on"]:
            require(target in active.values(), f"missing active dependency: {key} -> {target}")
        if record["replaces"]:
            root = record["replaces"][0]
            require(root in active, f"unknown or inactive replacement root: {key} -> {root}")
            require(_rank(by_id[active[root]]["origin"]) < _rank(record["origin"]),
                    f"duplicate active replacement: {key} -> {root}")
            active[root] = key
        else:
            active[key] = key
        del pending[key]
    return dict(sorted(active.items()))
