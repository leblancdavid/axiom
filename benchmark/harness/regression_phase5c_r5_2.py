"""Prospective B16 oracle over a pinned B15 predecessor, without checkpoint promotion."""

import argparse
import json
from pathlib import Path
import sys
import unittest

import capability_profile as legacy
import capability_profile_r5_2 as relative
import regression as original
import regression_phase5c_r5_1 as r5
import regression_phase5c_r4 as r4
import workspace as w
import workspace_phase5e as checkpoints


R5_1_SHA256 = "419a5feb9c09643adfa7c48ac9cf5123e255451571ff91345103cd7aa83e28c0"
COMPOSER_SHA256 = "eb5172eab4287cad80a67e47820e8039a0ac678252a36ed40adf735c4f048f97"
FRAGMENT_SHA256 = "2e50f5ff3fc35ae3adfbed5c263b192f887b5d476da8af943262c87421e5411d"
CASE_SHA256 = "b4e3bf5eaa3286d3f9569a0f48a3a8974fbc0d4defaf97f8f64958d64b24f49b"
REQUIREMENT_SHA256 = "cf9ede733a5b305677dc954a50a9146d9766a7943e0a2f70099b9db4c4fdc1be"
CASE = w.CASES / "B16.py"


def prospective(predecessor, achieved, app, *, mark_skips=True):
    w.require(w.file_hash(Path(r5.__file__)) == R5_1_SHA256 and
              w.file_hash(Path(relative.__file__)) == COMPOSER_SHA256 and
              w.file_hash(legacy.FRAGMENTS / "B16.json") == FRAGMENT_SHA256 and
              w.file_hash(CASE) == CASE_SHA256 and
              w.file_hash(w.REQUIREMENTS / "B16.md") == REQUIREMENT_SHA256 and
              w.file_hash(r5.CASE) == r5.CASE_SHA256 and
              w.file_hash(Path(r4.__file__)) == r5.R4_SHA256,
              "prospective B16 protocol artifact hash mismatch")
    checkpoints.validate_record(predecessor)
    w.require(achieved == [*predecessor["achieved"], "B16"] and app.is_file(),
              "B16 must be a prospective extension of a valid B15 predecessor")
    w.require(legacy.identity(predecessor["achieved"])["expectation_sha256"] ==
              predecessor["expectation_sha256"], "B15 achieved profile changed")
    target = relative.identity(achieved)
    replacements = r5.load_module("regression_B16_R5", r5.CASE)
    suite, active, disposition = r5.build_suite(app, target["expectation"], achieved,
                                                replacements, mark_skips=mark_skips)
    w.require(sum(name.startswith("regression_B16.") for name in disposition) == 3,
              "missing or duplicate B16 acceptance methods")
    return suite, target, active, disposition


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--prior-checkpoint", type=Path, required=True)
    parser.add_argument("--prior-hash", required=True)
    parser.add_argument("--achieved", required=True)
    parser.add_argument("--expectation-hash", required=True)
    args = parser.parse_args()
    try:
        w.require(w.file_hash(args.prior_checkpoint) == args.prior_hash,
                  "B15 predecessor hash mismatch")
        prior = json.loads(args.prior_checkpoint.read_text(encoding="utf-8"))
        suite, target, active, disposition = prospective(
            prior, list(filter(None, args.achieved.split(","))), args.app)
        w.require(target["expectation_sha256"] == args.expectation_hash,
                  "prospective target hash mismatch")
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    result = unittest.TextTestRunner(verbosity=2, resultclass=original.CountedResult).run(suite)
    print(json.dumps({"passed": result.successes,
                      "failure_events": len(result.failures) + len(result.errors),
                      "skipped": len(result.skipped), "case_methods": result.testsRun,
                      "achieved": target["expectation"]["achieved"],
                      "expectation_sha256": target["expectation_sha256"],
                      "superseded_cases": active, "dispositions": disposition}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
