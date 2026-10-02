"""R5: conditional B16 acceptance composition over the pinned R4 oracle."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

import capability_profile as capabilities
import regression as original
import regression_phase5c_r4 as r4
import regression_phase5e as prior
import workspace as w
import workspace_phase5e as checkpoints


CASE = Path(__file__).with_name("cases") / "B16_R5_replacements.py"
CASE_SHA256 = "9310e8f19557c8e9dfee4a1c4527524ec38c5de238d5b11d3ef9f5e08aa72d74"
R4_SHA256 = "61830ce905deff3565180b3767e933f50e5c17bfef25ca4bcac41f9c4a706cb9"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_supersessions(profile, achieved, replacements):
    active = r4.select_supersessions(profile, achieved)
    if "B16" in achieved:
        for name, (origin, _, _) in replacements.METHODS.items():
            if (origin == "baseline" or origin in achieved) and name not in active:
                active[name] = {
                    "origin": origin, "replacement": "B16-R5",
                    "replacement_method": replacements.replacement_id(name),
                    "reason": "B16 requires an existing owner on creation or migrates empty owner to system; "
                              "R5 retains all unrelated frozen assertions",
                }
    return active


def explain(suite, achieved, active, replacements):
    """Exact disposition of every loaded frozen and replacement method."""
    result = {}

    def visit(tests):
        for test in tests:
            if isinstance(test, unittest.TestSuite):
                visit(test)
            else:
                name = test.id()
                w.require(name not in result, f"duplicate oracle method: {name}")
                if name in active:
                    item = active[name]
                    result[name] = {"state": "superseded", **item}
                elif name in {item["replacement_method"] for item in active.values()
                              if "replacement_method" in item}:
                    result[name] = {"state": "replacement", "amendment": "B16-R5"}
                elif name.startswith("regression_B11_R4."):
                    result[name] = {"state": "replacement", "amendment": "B11-R4"}
                elif name in profile_skips(achieved):
                    result[name] = {"state": "skipped", "rule": "capability prerequisite not achieved"}
                elif name in replacements.METHODS:
                    result[name] = {"state": "active", "B16": "not achieved"}
                else:
                    result[name] = {"state": "active"}

    visit(suite)
    return result


def profile_skips(achieved):
    return {f"regression.Regression.test_{name}" for name, required in (
        ("b01_priority_and_regression", "B01"),
        ("b01_historical_priorities", "B01"),
        ("b02_tags_and_failure", "B02"),
        ("b02_explicit_migration", "B02")) if required not in achieved}


def build_suite(app, profile, achieved, replacements, *, mark_skips=True):
    original.APP = app.resolve()
    original.ACHIEVED = set(achieved)
    original.PROFILE = profile
    baseline_check = original.check_task

    def check_task(test, task):
        baseline_check(test, task)
        for field, kind in profile["field_types"].items():
            test.assertIs(type(task[field]), capabilities.TYPES[kind], field)

    original.check_task = check_task
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(original.Regression)
    for request in achieved:
        if int(request[1:]) <= 2:
            continue
        path = w.CASES / f"{request}.py"
        w.require(path.is_file(), f"frozen external case missing: {request}")
        module = load_module(f"regression_{request}", path)
        suite.addTests(module.cases(app, profile, frozenset(achieved)))
    active = select_supersessions(profile, achieved, replacements)
    if "B11" in achieved:
        repair = load_module("regression_B11_R4", r4.REPAIR_CASE)
        suite.addTests(repair.cases(app, profile, frozenset(achieved)))
    if "B16" in achieved:
        selected = {name for name in active if name in replacements.METHODS
                    and active[name]["replacement"] == "B16-R5"}
        suite.addTests(replacements.cases(suite, selected, app, profile))
        expected = {active[name]["replacement_method"] for name in selected}
        w.require(len(expected) == len(selected), "duplicate B16 replacement method")
    dispositions = explain(suite, achieved, active, replacements)
    if mark_skips:
        prior.mark_superseded(suite, active)
    return suite, active, dispositions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--achieved", default="")
    parser.add_argument("--expectation-hash", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--expected-hash", required=True)
    args = parser.parse_args()
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    achieved = list(filter(None, args.achieved.split(",")))
    try:
        w.require(args.app.is_file(), "application absent")
        w.require(w.file_hash(Path(r4.__file__)) == R4_SHA256, "R4 oracle changed")
        w.require(w.file_hash(r4.REPAIR_CASE) == r4.REPAIR_CASE_SHA256, "R4 repair changed")
        w.require(w.file_hash(CASE) == CASE_SHA256, "R5 replacement hash mismatch")
        for request, expected in r4.FROZEN.items():
            w.require(w.file_hash(w.CASES / f"{request}.py") == expected,
                      f"R4 frozen case changed: {request}")
        w.require(w.file_hash(capabilities.FRAGMENTS / "B11.json") == r4.B11_FRAGMENT_SHA256,
                  "R4 B11 fragment changed")
        w.require(w.file_hash(args.checkpoint) == args.expected_hash, "checkpoint hash mismatch")
        record = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        checkpoints.validate_record(record)
        identity = capabilities.identity(achieved)
        w.require(record["achieved"] == achieved and
                  record["expectation_sha256"] == args.expectation_hash and
                  identity["expectation_sha256"] == args.expectation_hash,
                  "composed regression expectation hash mismatch")
        expected_app = ("generated/task_manager.py" if record["track"] == "axiom"
                        else "benchmark/conventional/task_manager.py")
        w.require(w.file_hash(args.app) == record["files"][expected_app],
                  "application does not match checkpoint")
        replacements = load_module("regression_B16_R5", CASE)
        suite, active, dispositions = build_suite(args.app, identity["expectation"],
                                                   achieved, replacements)
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    result = unittest.TextTestRunner(verbosity=2, resultclass=original.CountedResult).run(suite)
    print(json.dumps({"passed": result.successes,
                      "failure_events": len(result.failures) + len(result.errors),
                      "skipped": len(result.skipped), "case_methods": result.testsRun,
                      "achieved": achieved, "expectation_sha256": args.expectation_hash,
                      "superseded_cases": active, "dispositions": dispositions,
                      "repair_case_sha256": w.file_hash(r4.REPAIR_CASE),
                      "b16_replacements_sha256": w.file_hash(CASE)}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
