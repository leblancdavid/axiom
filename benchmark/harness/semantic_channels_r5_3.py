"""Prospective source-complete inventory of executable acceptance channels.

This is a channel inventory, not a semantic-equivalence certificate. An AST
site in a loop denotes a parameterized family, not a single requirement.
"""

import ast
import inspect
from pathlib import Path
import textwrap

import acceptance_inventory_r5_3 as prior
import assertion_preservation_r5_2_2 as repair
import capability_profile_r5_2 as profiles
import helper_invocations_r5_3 as helper_invocations
import parameterized_roots_r5_3 as parameterized
import replacement_lineage_r5_3 as replacement_lineage
import regression_phase5c_r5_1 as runner
import workspace as w


VERSION = "R5.3-EXECUTABLE-ASSERTION-CHANNELS/1"
BASELINE = runner.original
CALL_NAMES = {"call", "check_task", "upgraded", "check_created", "create"}


def source_path(function):
    return Path(inspect.getfile(function)).resolve().relative_to(w.ROOT).as_posix()


def parse(function):
    source = textwrap.dedent(inspect.getsource(function))
    return ast.parse(source).body[0], function.__code__.co_firstlineno, source


def calls(function):
    node, start, source = parse(function)
    result = []
    # A local function is reached at its invocation, not when its definition
    # executes. Do not count its CLI twice as both an outer and an inner call.
    class Scope(ast.NodeVisitor):
        def __init__(self):
            self.nodes = []

        def visit_FunctionDef(self, item):
            if item is node:
                for statement in item.body:
                    self.visit(statement)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, item):
            self.nodes.append(item)
            self.generic_visit(item)

        def visit_Assert(self, item):
            self.nodes.append(item)
            self.generic_visit(item)

        def visit_Raise(self, item):
            self.nodes.append(item)
            self.generic_visit(item)

    scope = Scope()
    scope.visit(node)
    for item in scope.nodes:
        if not isinstance(item, ast.Call):
            continue
        callee = item.func
        name = callee.attr if isinstance(callee, ast.Attribute) else (
            callee.id if isinstance(callee, ast.Name) else "")
        if name.startswith("assert") or name in CALL_NAMES or name in ("run", "skipTest", "fail"):
            result.append({"line": start + item.lineno - 1, "column": item.col_offset,
                           "kind": name, "expression": ast.unparse(item)})
    for item in scope.nodes:
        if isinstance(item, ast.Assert):
            result.append({"line": start + item.lineno - 1, "column": item.col_offset,
                           "kind": "python_assert", "expression": ast.unparse(item)})
        if isinstance(item, ast.Raise):
            result.append({"line": start + item.lineno - 1, "column": item.col_offset,
                           "kind": "raise", "expression": ast.unparse(item)})
    return sorted(result, key=lambda row: (row["line"], row["column"], row["kind"]))


def helper_for(test, kind, method=None):
    if kind == "call":
        if method is not None and "call" in method.__globals__:
            return method.__globals__["call"]
        return getattr(type(test), "call", None)
    if kind == "check_task":
        return prior.BASE_CHECK_TASK
    if kind == "upgraded":
        return BASELINE.upgraded
    if kind == "check_created":
        return getattr(type(test), "check_created", None)
    if kind == "create":
        return getattr(type(test), "create", None)
    return None


def helper_sites(function, profile, achieved, *, stack=()):
    """Expand reachable assertion sites, retaining loop/branch AST context."""
    w.require(function not in stack, "recursive acceptance helper")
    node, start, source = parse(function)
    rows = []
    for site in calls(function):
        kind = site["kind"]
        if kind.startswith("assert") or kind in ("python_assert", "raise"):
            rows.append(site)
        elif kind == "call" and function is BASELINE.upgraded:
            rows.extend({"via": site, "assertion": leaf}
                        for leaf in helper_sites(BASELINE.call, profile, achieved,
                                                 stack=(*stack, function)))
        elif kind == "check_task" and function is BASELINE.upgraded:
            rows.extend({"via": site, "assertion": leaf}
                        for leaf in helper_sites(prior.BASE_CHECK_TASK, profile, achieved,
                                                 stack=(*stack, function)))
    if function is prior.BASE_CHECK_TASK:
        rows = [{**row, "condition": "B02 achieved" if row["line"] == 68 else "always"}
                for row in rows if row["line"] != 68 or "B02" in achieved]
        # The R5 wrapper is part of the executable helper, independently of the
        # baseline check. One assertion per field, per invocation.
        rows.extend({"kind": "assertIs", "field": field, "type": kind,
                     "condition": "R5 field_types", "source": "regression_phase5c_r5_1.py:92"}
                    for field, kind in sorted(profile["field_types"].items()))
    return rows


def invocation(test, method, kind, profile, achieved):
    helper = helper_for(test, kind, method)
    w.require(helper is not None, f"unresolved helper: {test.id()}:{kind}")
    if helper in (BASELINE.call, BASELINE.upgraded, prior.BASE_CHECK_TASK):
        return helper, helper_sites(helper, profile, achieved)
    expanded = [r for r in calls(helper) if r["kind"].startswith("assert")
                or r["kind"] in ("python_assert", "raise")]
    # Frozen R5 adapters execute the original envelope with an added owner.
    if helper.__name__ == "owner_call":
        expanded.extend({"via": "R5 owner_call: create gains --owner system", "assertion": leaf}
                        for leaf in helper_sites(BASELINE.call, profile, achieved))
    elif helper.__name__ == "_call" and hasattr(type(test), "__original_call__"):
        original = type(test).__original_call__
        expanded.extend({"via": "R5 _call: create gains --owner system", "assertion": leaf}
                        for leaf in calls(original) if leaf["kind"].startswith("assert"))
    if kind == "create":
        nested = helper_for(test, "call", helper)
        w.require(nested is not None, "create helper has no call")
        _, leaves = invocation(test, helper, "call", profile, achieved)
        expanded.extend({"via": r, "assertion": leaf}
                        for r in calls(helper) if r["kind"] == "call" for leaf in leaves)
    return helper, expanded


def helper_loops(function):
    """Keep helper-side parameterized sites visible to the completeness gate."""
    node, start, _ = parse(function)
    return [{"source": f"{source_path(function)}:{start + item.lineno - 1}",
             "iterator": ast.unparse(item.iter),
             "assertion_or_helper_sites": [ast.unparse(call) for call in ast.walk(item)
                                           if isinstance(call, ast.Call) and
                                           ((isinstance(call.func, ast.Attribute) and
                                             (call.func.attr.startswith("assert") or call.func.attr in CALL_NAMES)) or
                                            (isinstance(call.func, ast.Name) and call.func.id in CALL_NAMES))]}
            for item in ast.walk(node) if isinstance(item, ast.For)]


def collect(achieved):
    """Inspect every loaded method, including superseded and skipped sources."""
    parent = __import__("acceptance_repaired_r5_3").collect(achieved)
    profile = profiles.compose(achieved)
    with prior.isolated_construction():
        replacements = runner.load_module("regression_B16_R5", runner.CASE)
        suite, _, disposition, _ = repair.build_suite(
            w.ROOT / "benchmark/conventional/task_manager.py", profile,
            achieved, replacements, mark_skips=False)
        methods = {}
        helpers = {}
        helper_functions = {}
        parameterized_roots = {}
        direct_observation_roots = {}
        direct_assertion_roots = {}
        unresolved_loops = {}
        for test in prior.instances(suite):
            name = test.id()
            method = getattr(type(test), test._testMethodName)
            sites = calls(method)
            node, start, source = parse(method)
            local_creators = {item.name: item for item in ast.walk(node)
                              if isinstance(item, ast.FunctionDef) and item is not node}
            # Full body retained: earlier commands, writes, subtests, branches
            # and state transitions must not be discarded when interpreting a
            # later assertion or CLI invocation.
            channel = []
            for site in sites:
                kind = site["kind"]
                if kind in ("run", "fail"):
                    w.require(False, f"unmapped direct acceptance mechanism: {name}:{site['line']}")
                if kind in ("call", "check_task", "upgraded", "check_created") or (
                        kind == "create" and name.startswith(("assertion_preservation_r5_2_1.",
                                                                "assertion_preservation_r5_2_2."))):
                    helper, expanded = invocation(test, method, kind, profile, achieved)
                    helper_functions[f"{source_path(helper)}:{helper.__qualname__}"] = helper
                    if helper not in (BASELINE.call, BASELINE.upgraded, prior.BASE_CHECK_TASK):
                        key = f"{source_path(helper)}:{helper.__qualname__}"
                        if key not in helpers:
                            helpers[key] = {"source_sha256": w.file_hash(Path(inspect.getfile(helper))),
                                            "assertions": calls(helper)}
                    channel.append({**site, "helper": source_path(helper),
                                    "expansion": expanded})
                elif kind in local_creators:
                    # B12's local create helper builds options dynamically. Its
                    # call is inside the nested body, so preserve both sites.
                    inner = local_creators[kind]
                    inner_calls = [item for item in ast.walk(inner) if isinstance(item, ast.Call)
                                   and isinstance(item.func, ast.Attribute) and item.func.attr == "call"]
                    w.require(inner_calls, f"unaccounted local helper: {name}:{kind}")
                    helper, expanded = invocation(test, method, "call", profile, achieved)
                    channel.append({**site, "local_helper": ast.unparse(inner),
                                    "expansion": [{"via": ast.unparse(item), "assertion": leaf}
                                                  for item in inner_calls for leaf in expanded]})
                elif kind.startswith("assert") or kind in ("python_assert", "raise"):
                    channel.append(site)
                elif kind == "skipTest":
                    channel.append(site)
            methods[name] = {"state": disposition.get(name, {}).get("state", "restoration"),
                              "source": source_path(method),
                              "first_line": start,
                              "source_sha256": w.file_hash(Path(inspect.getfile(method))),
                              "body": source, "channels": channel}
            lineage = None
            if name.startswith("regression_B16_R5."):
                old = {replacements.replacement_id(key): key for key in replacements.METHODS}.get(name)
                if old:
                    lineage = {"source_method": old, "carrier": name, "amendment": "B16-R5",
                               "source": "benchmark/harness/cases/B10.py" if old in replacement_lineage.R5_SPECIAL else None,
                               "assertion_lines": replacement_lineage.R5_SPECIAL.get(old, {}).get("preserved", {})}
            restoration = [{"frozen_root": key, **value, "carrier": name}
                           for key, value in parent["restored_roots"].items()
                           if value["chain"][-1] == name or (
                               value["chain"][-1].rsplit(".", 1)[-1] == name.rsplit(".", 1)[-1]
                               and value["chain"][-1].startswith(
                                   source_path(method).rsplit("/", 1)[-1].removesuffix(".py") + "."))]
            expanded = parameterized.expand(method, name, source_path(method),
                                             methods[name]["state"],
                                             lineage={"replacement": lineage, "restoration": restoration}
                                             if restoration else lineage,
                                             achieved=achieved, profile=profile)
            if expanded["roots"]:
                parameterized_roots[name] = expanded["roots"]
            if expanded["observations"]:
                direct_observation_roots[name] = expanded["observations"]
            if expanded["direct_assertions"]:
                direct_assertion_roots[name] = expanded["direct_assertions"]
            if expanded["unresolved"]:
                unresolved_loops[name] = expanded["unresolved"]
        expected = set(parent["parent_methods"]) | set(parent["repair_carrier_ids"])
        w.require(set(methods) == expected, "acceptance method coverage mismatch")
        invocation_roots = helper_invocations.collect(methods, parameterized_roots,
                                                      profile, achieved)
        # The CLI is reached through the runner-global call, the instance call
        # methods, and the R5 owner adapter. Capture those implementations too.
        return {"version": VERSION, "achieved": list(achieved),
                 "repair_inventory_sha256": parent["repair_inventory_sha256"],
                 "methods": dict(sorted(methods.items())), "helpers": dict(sorted(helpers.items())),
                   "parameterized_roots": dict(sorted(parameterized_roots.items())),
                   "direct_observation_roots": dict(sorted(direct_observation_roots.items())),
                   "direct_assertion_roots": dict(sorted(direct_assertion_roots.items())),
                  "helper_invocation_roots": invocation_roots,
                 "unresolved_parameterized_loops": dict(sorted(unresolved_loops.items())),
                 "helper_parameterized_sites": {key: rows for key, helper in sorted(helper_functions.items())
                                                if (rows := helper_loops(helper))},
                 "semantic_equivalence_proven": False}
