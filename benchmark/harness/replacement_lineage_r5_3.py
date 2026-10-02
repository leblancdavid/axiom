"""Prospective, fail-closed evidence for the rewritten R4/R5 acceptance bodies.

These are source assertion *sites*, not a certificate for the entire oracle.
In particular, the invocation context and CLI envelope are recorded separately.
"""

import ast
import hashlib
import inspect
import textwrap

import acceptance_inventory_r5_3 as inventory
import acceptance_repaired_r5_3 as repaired
import capability_profile_r5_2 as profiles
import regression_phase5c_r5_1 as runner
import workspace as w


VERSION = "R5.3-REPLACEMENT-LINEAGE-EVIDENCE/1"
R4 = runner.r4.REPLACEMENTS
R5 = runner.load_module("regression_B16_R5", runner.CASE)
FROZEN_INPUTS = {"B04.py": runner.r4.FROZEN["B04"],
                 "B07.py": runner.r4.FROZEN["B07"],
                 "B10.py": "5753a963f1f23932f66be7619cf7232bf3b605b803b6673cb070506777f24851",
                 "B11_R4_replacements.py": runner.r4.REPAIR_CASE_SHA256,
                 "B16_R5_replacements.py": runner.CASE_SHA256}

# Line numbers here are original frozen source coordinates, not semantic IDs.
# A map row is reviewed with its setup and its observation point; unchanged
# statements remain independent even when they live in the same test method.
R4_MAP = {
    "regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations": {
        "replacement": "regression_B11_R4.cases.<locals>.Source.test_verbatim_default_and_mutations_after_b11",
        "preserved": {33: 38, 34: 39, 35: 40, 36: 41, 38: 43, 40: 45, 41: 46},
        "superseded": {43: 53},
        "added": [50, 52],
    },
    "regression_B07.cases.<locals>.Notes.test_append_order_trim_and_failed_append": {
        "replacement": "regression_B11_R4.cases.<locals>.Notes.test_append_order_trim_and_failed_append_after_b11",
        "preserved": {29: 62, 30: 63, 32: 65, 34: 67, 35: 68, 39: 72,
                      40: 73, 41: 74, 43: 76},
        "superseded": {44: 82},
        "added": [79, 81],
    },
}

R5_SPECIAL = {
    "regression_B10.cases.<locals>.Owner.test_trim_reject_and_exact_owner_listing": {
        "preserved": {30: 95, 41: 109, 45: 113, 47: 115, 48: 116},
        "changed": {38: 106},
        "added": [96, 97],
        "amendment": "B16 required registered owners; omitted-owner create becomes --owner system; list-owner additionally queries system",
    },
    "regression_B10.cases.<locals>.Owner.test_migration_defaults_unowned": {
        "preserved": {59: 128, 60: 129, 63: 132, 65: 135},
        "changed": {62: 131, 64: 133},
        "added": [134],
        "amendment": "B16 migrates previously unowned records to system instead of empty owner",
    },
}


def sites(function):
    source = textwrap.dedent(inspect.getsource(function))
    first = function.__code__.co_firstlineno
    nodes = ast.parse(source).body[0]
    result = {}
    for node in ast.walk(nodes):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else (
            node.func.id if isinstance(node.func, ast.Name) else "")
        if name.startswith("assert"):
            line = first + node.lineno - 1
            w.require(line not in result, f"multiple assertions on line {line}")
            result[line] = {"kind": name, "expression": ast.unparse(node),
                            "ast_sha256": hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()}
    return dict(sorted(result.items()))


def equivalent_expression(left, right, *, rename=None):
    """Compare assertion ASTs after an explicitly reviewed local variable rename."""
    rename = rename or {}

    class Rename(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in rename:
                if rename[node.id] == "self.profile":
                    return ast.copy_location(ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                                           attr="profile", ctx=node.ctx), node)
                node.id = rename[node.id]
            return node

    a = Rename().visit(ast.parse(left, mode="eval"))
    b = ast.parse(right, mode="eval")
    return ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)


def collect(achieved):
    """Inventory all selected R4/R5 bodies, independent of implementation/track."""
    for name, expected in FROZEN_INPUTS.items():
        w.require(w.file_hash(w.CASES / name) == expected, f"replacement audit input drift: {name}")
    parent = repaired.collect(achieved)
    methods = parent["parent_methods"]
    dispositions = inventory.reconstruct(methods, achieved)["dispositions"]
    with inventory.isolated_construction():
        suite, _, observed = runner.build_suite(
            w.ROOT / "benchmark/conventional/task_manager.py",
            profiles.compose(achieved), achieved, R5,
            mark_skips=False)
        w.require(dispositions == {key: row["state"] for key, row in observed.items()},
                  "method disposition drift")
        loaded = {test.id(): test for test in inventory.instances(suite)}
        evidence = {}
        for old, rule in R4_MAP.items():
            if old not in loaded:
                continue
            new = rule["replacement"]
            before = sites(getattr(type(loaded[old]), loaded[old]._testMethodName))
            after = sites(getattr(type(loaded[new]), loaded[new]._testMethodName)) if new in loaded else {}
            w.require(set(before) == set(rule["preserved"]) | set(rule["superseded"]),
                      f"unaccounted original R4 assertion: {old}")
            if after:
                w.require(set(after) == set(rule["preserved"].values()) |
                          set(rule["superseded"].values()) | set(rule["added"]),
                          f"unaccounted replacement R4 assertion: {new}")
                for a, b in rule["preserved"].items():
                    w.require(equivalent_expression(before[a]["expression"],
                                                    after[b]["expression"],
                                                    rename={"task": "t"}),
                              f"R4 preserved assertion changed: {old}:{a}")
            evidence[old] = {"replacement": new if after else None,
                             "disposition": dispositions[old],
                             "preserved": [{"source_line": a, "carrier_line": b,
                                            "source": before[a], "carrier": after.get(b)}
                                           for a, b in rule["preserved"].items()],
                             "superseded": [{"source_line": a, "carrier_line": b,
                                              "source": before[a], "carrier": after.get(b)}
                                             for a, b in rule["superseded"].items()],
                             "added": [{"line": line, "carrier": after[line]}
                                       for line in rule["added"]] if after else []}
        for old, (_, _, _) in R5.METHODS.items():
            if (old not in loaded or observed[old].get("replacement") != "B16-R5"
                    or old in R4_MAP):
                continue
            new = R5.replacement_id(old)
            w.require(new in loaded, f"missing R5 carrier: {old}")
            source = getattr(type(loaded[old]), loaded[old]._testMethodName)
            carrier = getattr(type(loaded[new]), loaded[new]._testMethodName)
            if old in R5_SPECIAL:
                rule = R5_SPECIAL[old]
                before, after = sites(source), sites(carrier)
                w.require(set(before) == set(rule["preserved"]) | set(rule["changed"]),
                          f"unaccounted B10 source assertion: {old}")
                w.require(set(after) == set(rule["preserved"].values()) |
                          set(rule["changed"].values()) | set(rule["added"]),
                          f"unaccounted B10 replacement assertion: {old}")
                for a, b in rule["preserved"].items():
                    w.require(equivalent_expression(before[a]["expression"],
                                                    after[b]["expression"],
                                                    rename={"profile": "self.profile"}
                                                    if a == 65 and old.endswith("test_migration_defaults_unowned")
                                                    else {}),
                              f"B10 preserved assertion changed: {old}:{a}")
                evidence[old] = {"replacement": new, "mechanism": "rewritten_B10",
                                 "source": before, "carrier": after, **rule}
            else:
                w.require(source.__code__ is carrier.__code__,
                          f"R5 does not replay frozen code object: {old}")
                evidence[old] = {"replacement": new, "mechanism": "same_code_object",
                                 "assertions": sites(source),
                                 "owner_adapter": "create gains --owner system"}
        return {"version": VERSION, "achieved": list(achieved),
                "parent_inventory_sha256": parent["parent_inventory_sha256"],
                "repair_inventory_sha256": parent["repair_inventory_sha256"],
                "replacements": dict(sorted(evidence.items())),
                "full_prior_assertion_equivalence_proven": False}
