"""Prospective invocation-specific expansion of the two frozen looping helpers.

The fixture values come from the frozen caller and the composed profile, never
from an application under test. This is a helper-channel reconstruction; it
does not by itself certify all other assertion and CLI channels.
"""

import copy
import ast
import inspect
import textwrap

import regression
import assertion_preservation_r5_2_1 as preservation
import workspace as w


VERSION = "R5.3-HELPER-INVOCATIONS/1"
BASE_CHECK_TASK = regression.check_task


def _assert_helper_sites():
    """Reject unreviewed additions to either helper's assertion/call graph."""
    for function, expected in (
        (BASE_CHECK_TASK, {61: "assertEqual", 62: "assertIsInstance",
                                 63: "assertTrue", 64: "assertIsInstance",
                                 65: "assertTrue", 66: "assertEqual",
                                 68: "assertIsInstance"}),
        (regression.upgraded, {75: "assertIsNone", 76: "assertEqual",
                               77: "assertEqual", 78: "call", 79: "assertEqual",
                               81: "check_task", 82: "assertEqual"}),
    ):
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        first = function.__code__.co_firstlineno
        sites = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            kind = node.func.attr if isinstance(node.func, ast.Attribute) else (
                node.func.id if isinstance(node.func, ast.Name) else "")
            if kind.startswith("assert") or kind in ("check_task", "call") and not any(
                    isinstance(other, ast.Call) and other is not node and node in ast.walk(other)
                    and isinstance(other.func, ast.Attribute) and other.func.attr.startswith("assert")
                    for other in ast.walk(tree)):
                sites[first + node.lineno - 1] = kind
        w.require(sites == expected, f"unreviewed upgraded helper site: {sites}")
    # The frozen class-local helper is created inside cases(), so its source is
    # inspected through the frozen outer function without constructing a suite.
    tree = ast.parse(textwrap.dedent(inspect.getsource(preservation.cases)))
    helper = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                  and node.name == "check_created")
    first = preservation.cases.__code__.co_firstlineno - 1
    sites = {first + node.lineno: node.func.attr for node in ast.walk(helper)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and node.func.attr.startswith("assert")}
    w.require(sites == {96: "assertEqual", 97: "assertIsInstance", 98: "assertTrue",
                        99: "assertIsInstance", 100: "assertTrue", 101: "assertEqual",
                        104: "assertIsInstance", 106: "assertIs"},
              f"unreviewed check_created helper site: {sites}")


def _root(method, caller, invocation, helper, assertion, case, expectation, precondition):
    identity = {"method": method, "caller": caller, "invocation": invocation,
                "helper": helper, "assertion": assertion, "case": case}
    return {"id": w.digest(w.encoded(identity)), **identity,
            "expectation": copy.deepcopy(expectation),
            "precondition": copy.deepcopy(precondition),
            "provenance": [caller, invocation, helper, assertion]}


def _defaults(record, profile):
    return {**record, **{key: copy.deepcopy(value)
                       for key, value in profile["migration_defaults"].items()
                       if key not in record}}


def _migration_cases(name, site, loop, profile):
    """Resolve the finite source fixtures used by regression.upgraded.

    Check the caller expression and loop binding before applying each source
    fixture recipe. Unknown callers fail closed instead of inheriting a recipe.
    """
    line = site["line"]
    expression = site["expression"]
    if name.endswith(".test_baseline_migration_corruption") or name.endswith(
            ".test_baseline_migration_corruption_with_owner"):
        w.require(line == 135, "baseline migration source line drift")
        w.require(expression == "upgraded(self, cwd, payload, [with_defaults(expected)])" and
                  len(loop) == 1 and loop[0]["source"].endswith(":123") and
                  loop[0]["bindings"]["version"] in (1, 2), "baseline migration invocation drift")
        version = loop[0]["bindings"]["version"]
        old = regression.row("legacy")
        if version == 1:
            old = {key: value for key, value in old.items() if key not in ("priority", "due_date")}
            payload = [old]
            expected = {**old, "priority": "NORMAL", "due_date": None}
        else:
            old.pop("due_date")
            payload = {"schema_version": 2, "records": [old]}
            expected = {**old, "due_date": None}
        return payload, [_defaults(expected, profile)], 1
    if name == "regression.Regression.test_b01_historical_priorities":
        rows = [regression.row(priority.lower(), priority)
                for priority in ("HIGH", "LOW", "NORMAL")]
        if line == 187:
            w.require(expression == "upgraded(self, cwd, {'schema_version': 3, 'records': rows}, [with_defaults(r) for r in rows], count=3)"
                      and profile["schema_version"] > 3 and not loop,
                      "B01 current-schema branch drift")
            return {"schema_version": 3, "records": rows}, [
                _defaults(row, profile) for row in rows], 3
        if line == 195:
            w.require(expression == "upgraded(self, Path(folder), {'schema_version': 2, 'records': older}, [with_defaults(r) for r in rows], count=3)"
                      and not loop, "B01 old-schema branch drift")
            older = [{key: value for key, value in row.items() if key != "due_date"}
                     for row in rows]
            return {"schema_version": 2, "records": older}, [
                _defaults(row, profile) for row in rows], 3
    if name == "regression.Regression.test_b02_explicit_migration" and line == 223:
        w.require(expression == "upgraded(self, Path(folder), payload, [with_defaults(expected)])"
                  and len(loop) == 1 and loop[0]["source"].endswith(":218") and
                  loop[0]["index"] in (0, 1), "B02 migration invocation drift")
        binding = loop[0]["bindings"]
        return binding["payload"], [_defaults(binding["expected"], profile)], 1
    raise ValueError(f"unreconstructed upgraded caller: {name}:{line}:{loop}")


def _check_task(method, caller, invocation, task, index, profile, achieved, precondition):
    helper = "benchmark/harness/regression.py:60-68"
    case = f"row[{index}]"
    checks = [(61, "fields", {"fields": profile["fields"]}),
              (62, "id-type", {"field": "id", "type": "str"}),
              (63, "id-nonblank", {"field": "id", "nonblank": True}),
              (64, "created-at-type", {"field": "created_at", "type": "str"}),
              (65, "created-at-utc-suffix", {"field": "created_at", "suffix": "Z"}),
              (66, "created-at-utc-offset", {"field": "created_at", "offset_seconds": 0})]
    if "B02" in achieved:
        checks.append((68, "tags-list", {"field": "tags", "type": "list"}))
    for line, label, expectation in checks:
        yield _root(method, caller, invocation, helper,
                    f"benchmark/harness/regression.py:{line}", f"{case}:{label}",
                    {"task": task, **expectation}, precondition)
    # The R5 runner wraps check_task with an assertion per profile field.
    for field, kind in sorted(profile["field_types"].items()):
        yield _root(method, caller, invocation,
                    "benchmark/harness/regression_phase5c_r5_1.py:92",
                    "benchmark/harness/regression_phase5c_r5_1.py:92",
                    f"{case}:type:{field}",
                    {"task": task, "field": field, "exact_type": kind}, precondition)


def upgraded(method, sites, parameterized_roots, profile, achieved):
    result = []
    for site in sites:
        if site["kind"] != "upgraded":
            continue
        caller = f"benchmark/harness/regression.py:{site['line']}"
        loops = [root["loop"] for root in parameterized_roots
                 if root["kind"] == "upgraded" and root["site"] == caller]
        if not loops:
            loops = [[]]
        w.require(len(loops) == len({w.encoded(loop) for loop in loops}),
                  f"duplicate upgraded invocation: {method}:{caller}")
        for loop in loops:
            payload, expected, count = _migration_cases(method, site, loop, profile)
            invocation = f"{caller}#" + w.digest(w.encoded(loop))[:16]
            ordered = sorted(expected, key=lambda row: (row["created_at"], row["id"]))
            precondition = {"caller_loop": loop, "input_file": "tasks.json",
                            "input_payload": payload, "expected_rows": ordered,
                            "migration_count": count, "profile_fields": profile["fields"],
                            "caller_body": method}
            helper = "benchmark/harness/regression.py:71-83"
            # A failed CLI call has two envelope rejection checks; successful
            # calls check exit/stderr and JSON parsing before comparing content.
            for line, label, expectation in (
                (75, "migration-required", {"command": ["list"], "error": "migration_required",
                                            "exit": 1, "stdout": "empty", "stderr_json": {"error": "migration_required"}}),
                (76, "rejection-no-write", {"file_bytes": "unchanged from input_payload"}),
                (77, "migrate", {"command": ["migrate"], "exit": 0,
                                 "stderr": "empty", "stdout_json": {"migrated": count}}),
                (78, "list", {"command": ["list"], "exit": 0,
                              "stderr": "empty", "stdout_json_shape": "list of task rows"}),
                (79, "sorted-rows", {"rows": ordered, "order": ["created_at", "id"]}),
                (82, "idempotent-migrate", {"command": ["migrate"], "exit": 0,
                                            "stderr": "empty", "stdout_json": {"migrated": 0}})):
                result.append(_root(method, caller, invocation, helper,
                                    f"benchmark/harness/regression.py:{line}", label,
                                    expectation, precondition))
            for index, row in enumerate(ordered):
                result.extend(_check_task(method, caller, invocation, row, index,
                                          profile, achieved, precondition))
    return result


def check_created(method, sites, parameterized_roots, profile):
    result = []
    for site in sites:
        if site["kind"] != "check_created":
            continue
        caller = f"benchmark/harness/assertion_preservation_r5_2_1.py:{site['line']}"
        calls = [root for root in parameterized_roots if root["kind"] == "check_created"
                 and root["site"] == caller]
        w.require(len(calls) == 3 and [row["loop"][0]["bindings"]["task"]["title"]
                  for row in calls] == ["normal", "high", "low"],
                  "R5.2.1 check_created invocation drift")
        for index, call in enumerate(calls):
            task = call["loop"][0]["bindings"]["task"]
            invocation = f"{caller}#task[{index}]"
            precondition = {"caller_loop": call["loop"],
                            "prior_steps": call["prior_steps"],
                            "created_task": task, "profile_fields": profile["fields"],
                            "profile_defaults": profile["migration_defaults"]}
            helper = "benchmark/harness/assertion_preservation_r5_2_1.py:93-106"
            for line, label, expectation in (
                (96, "fields", {"fields": profile["fields"]}),
                (97, "id-type", {"field": "id", "type": "str"}),
                (98, "id-nonblank", {"field": "id", "nonblank": True}),
                (99, "created-at-type", {"field": "created_at", "type": "str"}),
                (100, "created-at-utc-suffix", {"field": "created_at", "suffix": "Z"}),
                (101, "created-at-utc-offset", {"field": "created_at", "offset_seconds": 0}),
            ):
                result.append(_root(method, caller, invocation, helper,
                                    f"benchmark/harness/assertion_preservation_r5_2_1.py:{line}",
                                    label, {"task": task, **expectation}, precondition))
            if "tags" in profile["fields"]:
                result.append(_root(method, caller, invocation, helper,
                                    "benchmark/harness/assertion_preservation_r5_2_1.py:104",
                                    "tags-list", {"task": task, "field": "tags", "type": "list"},
                                    precondition))
            for field, kind in profile["field_types"].items():
                result.append(_root(method, caller, invocation, helper,
                                    "benchmark/harness/assertion_preservation_r5_2_1.py:106",
                                    f"field:{field}",
                                    {"task": task, "field": field, "exact_type": kind},
                                    precondition))
    return result


def collect(methods, parameterized_roots, profile, achieved):
    """Only applicable live invocations; skipped/superseded sites are lineage."""
    _assert_helper_sites()
    output = {}
    for name, entry in methods.items():
        if entry["state"] not in ("active", "replacement", "restoration"):
            continue
        sites = entry["channels"]
        roots = upgraded(name, sites, parameterized_roots.get(name, []), profile, achieved)
        roots.extend(check_created(name, sites, parameterized_roots.get(name, []), profile))
        if roots:
            ids = [root["id"] for root in roots]
            w.require(len(ids) == len(set(ids)), f"duplicate helper root: {name}")
            output[name] = roots
    return dict(sorted(output.items()))
