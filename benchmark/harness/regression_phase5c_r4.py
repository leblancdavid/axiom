"""Versioned B11 oracle repair. Phase 5E runner and frozen cases stay unchanged."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

import capability_profile as capabilities
import regression as original
import regression_phase5e as prior
import workspace as w
import workspace_phase5e as checkpoints


REPLACEMENTS = {
    "regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations": {
        "origin": "B04", "replacement": "B11",
        "reason": "B11 requires archive before deleting a completed task; R4 replacement preserves B04 source assertions"},
    "regression_B07.cases.<locals>.Notes.test_append_order_trim_and_failed_append": {
        "origin": "B07", "replacement": "B11",
        "reason": "B11 requires archive before deleting a completed task; R4 replacement preserves B07 note assertions"},
}
REPAIR_CASE = Path(__file__).with_name("cases") / "B11_R4_replacements.py"
REPAIR_CASE_SHA256 = "8a8bfad8451e747e31429f1bd87055689d3115ef851861ec48810fbe4678ca60"
FROZEN = {
    "B04": "85be09e650943ac296fea889577d21657a31a6e9993e32603e9604e2b7b89c03",
    "B07": "d02a0d9ea314a4fcf65eb12ad2ec4ae41cf18cec6a5a7d6aa69e26114b576c5d",
    "B11": "721fc2fb1c4d9f7d51978721799fd26be12a3186d481667fff5b0060be64201a",
}
B11_FRAGMENT_SHA256 = "5dcf7ee0f046515bfdd198feede631c5b767fb17d5e77302d79b662f7e335f7c"


def select_supersessions(profile, achieved):
    active = prior.active_supersessions(profile, achieved)
    if "B11" in achieved:
        for test_id, item in REPLACEMENTS.items():
            if item["origin"] in achieved:
                w.require(test_id not in active, "R4 supersession conflicts with frozen fragment")
                active[test_id] = item
    return active


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
    if w.file_hash(args.checkpoint) != args.expected_hash:
        parser.error("checkpoint hash mismatch")
    try:
        w.require(w.file_hash(REPAIR_CASE) == REPAIR_CASE_SHA256,
                  "R4 replacement case hash mismatch")
        for request, expected_hash in FROZEN.items():
            w.require(w.file_hash(w.CASES / f"{request}.py") == expected_hash,
                      f"R4 frozen case changed: {request}")
        w.require(w.file_hash(capabilities.FRAGMENTS / "B11.json") == B11_FRAGMENT_SHA256,
                  "R4 B11 fragment changed")
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
            w.require(path.is_file(), f"frozen external case missing: {request}")
            spec = importlib.util.spec_from_file_location(f"regression_{request}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            suite.addTests(module.cases(original.APP, original.PROFILE, frozenset(achieved)))
        active = select_supersessions(original.PROFILE, achieved)
        if "B11" in achieved:
            w.require(REPAIR_CASE.is_file(), "R4 replacement case absent")
            spec = importlib.util.spec_from_file_location("regression_B11_R4", REPAIR_CASE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            suite.addTests(module.cases(original.APP, original.PROFILE, frozenset(achieved)))
        prior.mark_superseded(suite, active)
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    result = unittest.TextTestRunner(verbosity=2, resultclass=original.CountedResult).run(suite)
    print(json.dumps({"passed": result.successes,
                      "failure_events": len(result.failures) + len(result.errors),
                      "skipped": len(result.skipped), "case_methods": result.testsRun,
                      "achieved": achieved, "expectation_sha256": args.expectation_hash,
                      "superseded_cases": active,
                      "repair_case_sha256": w.file_hash(REPAIR_CASE)}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
