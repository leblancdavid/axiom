"""Prospective, track-neutral acceptance transitions over frozen prior dispositions.

Pure protocol operation: callers supply the independently composed prior state
and frozen semantic metadata. No application, runner, or classification is read.
"""

import copy

import workspace as w


def compose(prior, amendment):
    """Replace affected active carriers, retaining every unrelated assertion.

    State: {methods: {id: {status, assertions: {root: {dimensions, chain}}}},
            supersessions: {old_id: {replacement, amendment}}}.
    The root is the stable historical assertion identity. A chain lists every
    method that has carried it, starting with its frozen historical source.
    A removed assertion is absent from the active carrier, even if its earlier
    chain remains recorded on a superseded method.

    Amendment: {name, dimensions: [tag, ...], replacements: {active_id: new_id}}.
    A replacement must exist for every affected active carrier; surplus
    declarations are allowed only for already superseded or absent carriers,
    so the same amendment can apply to distinct valid prior histories.
    """
    w.require(isinstance(prior, dict) and set(prior) == {"methods", "supersessions"}
              and isinstance(prior["methods"], dict) and isinstance(prior["supersessions"], dict),
              "invalid prior acceptance state")
    w.require(isinstance(amendment, dict) and set(amendment) ==
              {"name", "dimensions", "replacements"} and
              isinstance(amendment["name"], str) and amendment["name"] and
              isinstance(amendment["dimensions"], list) and
              bool(amendment["dimensions"]) and
              len(amendment["dimensions"]) == len(set(amendment["dimensions"])) and
              all(isinstance(d, str) and d for d in amendment["dimensions"]) and
              isinstance(amendment["replacements"], dict), "invalid amendment")
    result = copy.deepcopy(prior)
    methods = result["methods"]
    supersessions = result["supersessions"]
    w.require(set(supersessions) == {name for name, method in methods.items()
                                    if method.get("status") == "superseded"},
              "inconsistent prior supersessions")
    for name, method in methods.items():
        w.require(isinstance(name, str) and name and isinstance(method, dict)
                  and set(method) == {"status", "assertions"} and
                  method["status"] in ("active", "superseded") and
                  isinstance(method["assertions"], dict) and method["assertions"],
                  "invalid prior method")
        for root, assertion in method["assertions"].items():
            w.require(isinstance(root, str) and root and isinstance(assertion, dict) and
                      set(assertion) == {"dimensions", "chain"} and
                      isinstance(assertion["dimensions"], list) and
                      len(assertion["dimensions"]) == len(set(assertion["dimensions"])) and
                      all(isinstance(d, str) and d for d in assertion["dimensions"]) and
                      isinstance(assertion["chain"], list) and
                      bool(assertion["chain"]) and assertion["chain"][-1] == name,
                      "invalid prior assertion provenance")
    active_roots = [root for name, method in methods.items() if method["status"] == "active"
                    for root in method["assertions"]]
    w.require(len(active_roots) == len(set(active_roots)), "duplicate active assertion")
    for old, edge in supersessions.items():
        w.require(isinstance(edge, dict) and set(edge) == {"replacement", "amendment"}
                  and isinstance(edge["amendment"], str) and
                  (edge["replacement"] is None or edge["replacement"] in methods),
                  "invalid prior replacement edge")
    affected = set(amendment["dimensions"])
    sources = amendment["replacements"]
    w.require(all(isinstance(old, str) and old and isinstance(new, str) and new
                  for old, new in sources.items()) and
              len(set(sources.values())) == len(sources), "invalid replacement mapping")
    for old, new in sources.items():
        w.require(new not in methods and new not in sources and old != new,
                  "replacement ID collision")
    for old, method in list(methods.items()):
        if method["status"] != "active":
            continue
        changed = {root for root, assertion in method["assertions"].items()
                   if affected.intersection(assertion["dimensions"])}
        if not changed:
            continue
        w.require(old in sources, f"missing active replacement: {old}")
        new = sources[old]
        carried = copy.deepcopy(method["assertions"])
        for root, assertion in carried.items():
            assertion["chain"].append(new)
        methods[new] = {"status": "active", "assertions": carried}
        method["status"] = "superseded"
        supersessions[old] = {"replacement": new, "amendment": amendment["name"]}
    # Entries for absent carriers are allowed only as conditional alternatives
    # from another frozen history. They cannot create a method or a skip here.
    return result
