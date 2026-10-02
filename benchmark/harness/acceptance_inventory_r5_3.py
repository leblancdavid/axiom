"""Prospective R5.3 inventory of the *loaded* frozen acceptance methods.

This is evidence collection, not an amendment or a replacement runner. In
particular, an AST assertion is not presumed equivalent to an assertion in a
later method merely because their containing methods have related names.
"""

import ast
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import textwrap
import unittest

import capability_profile_r5_2 as profiles
import regression_phase5c_r5_1 as r5
import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5c"
CHECKPOINTS = ("conventional", "lykoi")
PINNED_INVENTORIES = {
    tuple(f"B{i:02}" for i in range(1, 17)):
        "6706171247d40a725142ded41cf357fd1d7e5bf30f34875153cc2746c661652a",
    ("B01", "B04"):
        "07a5e464e994369fbc000b52bbe4cd037c292a4ff736b3b943db793e17472d0c",
}


def instances(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from instances(item)
        else:
            yield item


def source_method(test, replacements):
    name = test.id()
    if name.startswith("regression_B16_R5."):
        reverse = {replacements.replacement_id(old): old for old in replacements.METHODS}
        w.require(name in reverse, f"unlisted R5 method: {name}")
        old = reverse[name]
        if old in replacements.SPECIAL:
            function = (replacements.registered_trim_reject_and_exact_owner_listing
                        if old.endswith("test_trim_reject_and_exact_owner_listing")
                        else replacements.migration_defaults_system)
            return function, Path(replacements.__file__), "B16-R5"
        # The wrapper executes the original code object verbatim with an owner
        # adapter; inspect the code actually run, not the wrapper's class name.
        return getattr(type(test), test._testMethodName), Path(inspect.getfile(
            getattr(type(test), test._testMethodName))), "B16-R5:original-body"
    function = getattr(type(test), test._testMethodName)
    return function, Path(inspect.getfile(function)), (
        "B11-R4" if name.startswith("regression_B11_R4.") else "frozen")


def method_inventory(test, replacements):
    function, path, version = source_method(test, replacements)
    source = textwrap.dedent(inspect.getsource(function))
    tree = ast.parse(source)
    node = tree.body[0]
    w.require(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)),
              f"uninspectable method: {test.id()}")
    lines = source.splitlines()
    start = function.__code__.co_firstlineno
    # ast.walk visits even conditional branches; the inventory describes the
    # method's frozen body, not a sampled execution path.
    assertions = []
    mutations = []
    user_results = []
    for expression in ast.walk(node):
        if not isinstance(expression, ast.Call):
            continue
        callee = expression.func
        method = callee.attr if isinstance(callee, ast.Attribute) else (
            callee.id if isinstance(callee, ast.Name) else None)
        if method and (method.startswith("assert") or method in ("check_task", "upgraded")):
            fragment = ast.get_source_segment(source, expression)
            w.require(fragment is not None, f"missing assertion source: {test.id()}")
            assertions.append({"id": f"{test.id()}#assert:{expression.lineno}:{expression.col_offset}",
                               "line": start + expression.lineno - 1,
                               "expression_sha256": hashlib.sha256(fragment.encode()).hexdigest(),
                               "kind": method})
        if method in ("call", "upgraded"):
            commands = [arg.value for arg in expression.args if isinstance(arg, ast.Constant)
                        and isinstance(arg.value, str)]
            if method == "upgraded" or any(command in (
                    "create", "complete", "delete", "archive", "append-note",
                    "add-dependency", "migrate") for command in commands):
                mutations.append(start + expression.lineno - 1)
            if any(command in ("create-user", "list-users") for command in commands):
                user_results.append(start + expression.lineno - 1)
    w.require(assertions and mutations, f"no frozen assertion/mutation: {test.id()}")
    ids = [entry["id"] for entry in assertions]
    w.require(len(ids) == len(set(ids)), f"duplicate assertion: {test.id()}")
    return {"source": path.relative_to(w.ROOT).as_posix(),
            "source_sha256": w.file_hash(path), "version": version,
            "body_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "assertions": sorted(assertions, key=lambda entry: entry["id"]),
            "mutation_lines": sorted(set(mutations)),
            "user_result_lines": sorted(set(user_results))}


def collect(achieved):
    """Build the real runner suite without marking skips or invoking the app."""
    replacements = r5.load_module("regression_B16_R5", r5.CASE)
    profile = profiles.compose(achieved)
    suite, active, dispositions = r5.build_suite(
        w.ROOT / "benchmark/conventional/task_manager.py", profile, achieved,
        replacements, mark_skips=False)
    methods = {}
    for test in instances(suite):
        name = test.id()
        w.require(name not in methods, f"duplicate method: {name}")
        methods[name] = method_inventory(test, replacements)
    w.require(set(methods) == set(dispositions), "loaded/disposition method mismatch")
    return dict(sorted(methods.items())), active, dispositions


def validate_sources(methods):
    for name, entry in methods.items():
        path = w.ROOT / entry["source"]
        w.require(w.file_hash(path) == entry["source_sha256"], f"source drift: {name}")
        w.require(len(entry["assertions"]) == len({a["id"] for a in entry["assertions"]}),
                  f"duplicate assertion ID: {name}")
        w.require(entry["mutation_lines"], f"missing mutation: {name}")


def reconstruct(methods, achieved):
    """Independently select frozen *method* dispositions from amendment inputs.

    This is deliberately not a claim of assertion-level semantic equivalence:
    replacements with rewritten bodies need separately reviewed assertion maps.
    """
    achieved = frozenset(achieved)
    replacement_module = r5.load_module("regression_B16_R5", r5.CASE)
    fragment = json.loads((profiles.FRAGMENTS / "B11.json").read_text(encoding="utf-8"))
    old = {}
    if "B11" in achieved:
        for name, rule in fragment["supersedes_cases"].items():
            if rule["origin"] == "baseline" or rule["origin"] in achieved:
                old[name] = {"amendment": "B11", "replacement": "B11"}
        for name, rule in r5.r4.REPLACEMENTS.items():
            if rule["origin"] in achieved:
                w.require(name not in old, f"R4 conflict: {name}")
                old[name] = {"amendment": "B11-R4", "replacement": "B11"}
    if "B16" in achieved:
        for name, (origin, _, _) in replacement_module.METHODS.items():
            if (origin == "baseline" or origin in achieved) and name not in old:
                old[name] = {"amendment": "B16-R5",
                             "replacement": replacement_module.replacement_id(name)}
    w.require(set(old) <= set(methods), "supersession source not loaded")
    r5_targets = {edge["replacement"] for edge in old.values()
                  if edge["amendment"] == "B16-R5"}
    w.require(r5_targets <= set(methods), "R5 replacement not loaded")
    missing = r5.profile_skips(achieved)
    w.require(missing <= set(methods), "prerequisite skip not loaded")
    states = {}
    for name in methods:
        if name in old:
            states[name] = "superseded"
        elif name in missing:
            states[name] = "skipped"
        elif name in r5_targets or name.startswith("regression_B11_R4."):
            states[name] = "replacement"
        else:
            states[name] = "active"
    return {"dispositions": dict(sorted(states.items())), "edges": dict(sorted(old.items()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.output_dir:
        w.require(args.output_dir.is_dir(), "output directory absent")
    # Evidence only: a checkpoint provides achieved history, never a track
    # label as input to collection/composition.
    for label in CHECKPOINTS:
        record = json.loads((RESULTS / f"checkpoint-{label}-B16-r5_2.json").read_text(
            encoding="utf-8"))
        methods, active, dispositions = collect(record["achieved"])
        validate_sources(methods)
        inventory = {"achieved": record["achieved"], "methods": methods}
        digest = w.digest(w.encoded(inventory))
        w.require(digest == PINNED_INVENTORIES[tuple(record["achieved"])],
                  f"pinned assertion inventory mismatch: {label}")
        reconstructed = reconstruct(methods, record["achieved"])
        observed = {name: item["state"] for name, item in dispositions.items()}
        diff = {name: {"reconstructed": reconstructed["dispositions"].get(name),
                       "runner": observed.get(name)}
                for name in sorted(set(observed) | set(reconstructed["dispositions"]))
                if observed.get(name) != reconstructed["dispositions"].get(name)}
        evidence = {"achieved": record["achieved"], "inventory_sha256": digest,
                    "reconstruction_sha256": w.digest(w.encoded(reconstructed)),
                    "method_disposition_diff": diff,
                    "reconstructed": reconstructed, "observed": dict(sorted(observed.items())),
                    "assertion_equivalence_proven": False}
        if args.output_dir:
            (args.output_dir / f"R5_3-{label}-assertion-inventory.json").write_bytes(
                w.encoded(inventory))
            (args.output_dir / f"R5_3-{label}-method-diff.json").write_bytes(
                w.encoded(evidence))
        print(json.dumps({"checkpoint": label,
                          "inventory_sha256": digest,
                          "reconstruction_sha256": evidence["reconstruction_sha256"],
                          "method_disposition_diff": diff,
                          "methods": len(methods),
                          "assertions": sum(len(m["assertions"]) for m in methods.values()),
                          "active": sum(d["state"] in ("active", "replacement")
                                        for d in dispositions.values()),
                          "superseded": len(active)}, sort_keys=True))


if __name__ == "__main__":
    main()
