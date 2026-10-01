"""Capability-aware entry point for the unchanged Phase 5B external cases."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

import capability_profile as capabilities
import regression as original
import workspace as w


def active_supersessions(profile, achieved):
    return {name: item for name, item in profile["superseded_cases"].items()
            if item["origin"] == "baseline" or item["origin"] in achieved}


def mark_superseded(suite, superseded):
    found = set()

    def visit(tests):
        for test in tests:
            if isinstance(test, unittest.TestSuite):
                visit(test)
            elif test.id() in superseded:
                replacement = superseded[test.id()]
                method = getattr(type(test), test._testMethodName)
                setattr(type(test), test._testMethodName,
                        unittest.skip("superseded by " + replacement["replacement"] + ": " +
                                      replacement["reason"])(method))
                found.add(test.id())

    visit(suite)
    w.require(found == set(superseded), "supersession names an absent frozen test method")


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
    if not args.app.is_file():
        parser.error("application absent")
    import workspace_phase5e as checkpoints

    if w.file_hash(args.checkpoint) != args.expected_hash:
        parser.error("checkpoint hash mismatch")
    record = json.loads(args.checkpoint.read_text(encoding="utf-8"))
    checkpoints.validate_record(record)
    identity = capabilities.identity(achieved)
    if (record["achieved"] != achieved or record["expectation_sha256"] != args.expectation_hash or
            identity["expectation_sha256"] != args.expectation_hash):
        parser.error("composed regression expectation hash mismatch")
    expected_app = ("generated/task_manager.py" if record["track"] == "axiom"
                    else "benchmark/conventional/task_manager.py")
    if w.file_hash(args.app) != record["files"][expected_app]:
        parser.error("application does not match checkpoint")
    original.APP = args.app.resolve()
    original.ACHIEVED = set(achieved)
    original.PROFILE = identity["expectation"]
    baseline_check = original.check_task

    def check_task(test, task):
        baseline_check(test, task)
        for field, kind in original.PROFILE["field_types"].items():
            test.assertIs(type(task[field]), capabilities.TYPES[kind], field)

    original.check_task = check_task
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(original.Regression)
    for request in achieved:
        if int(request[1:]) <= 2:
            continue
        path = w.CASES / f"{request}.py"
        if not path.is_file():
            parser.error(f"frozen external case missing: {request}")
        spec = importlib.util.spec_from_file_location(f"regression_{request}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(module.cases(original.APP, original.PROFILE, frozenset(achieved)))
    superseded = original.PROFILE["superseded_cases"]
    active = active_supersessions(original.PROFILE, achieved)
    try:
        mark_superseded(suite, active)
    except w.ProtocolError as exc:
        parser.error(str(exc))
    result = unittest.TextTestRunner(verbosity=2, resultclass=original.CountedResult).run(suite)
    print(json.dumps({"passed": result.successes, "failure_events": len(result.failures) + len(result.errors),
                      "skipped": len(result.skipped), "case_methods": result.testsRun,
                      "achieved": achieved, "expectation_sha256": args.expectation_hash,
                      "superseded_cases": active}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
