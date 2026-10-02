"""Disposable independent B16 restore/revalidation for prospective R5.3.

Runs the unchanged B16 oracle beside the candidate inventory reconstruction.
It does not promote the candidate into the historical runner or expose B17.
"""

import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import acceptance_inventory_r5_3 as inventory
import capability_profile_r5_2 as profiles
import regression as original
import regression_phase5c_r5_1 as r5
import workspace as w
import workspace_phase5c_r5_2 as checkpoints


SNAPSHOTS = {
    "conventional": ("c2602584521bcacaaf68ac1394531f835fe9578765a1eb5b31aa943c5f728c8a",
                     "383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e"),
    "lykoi": ("7318a230fb2a89bce5722b02a0899f72122e5bde5679c0fba4d0a896c55edf95",
              "36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5"),
}
TEMP = Path("C:/Users/lblan/AppData/Local/Temp/opencode")


def run(label):
    w.require(label in SNAPSHOTS and TEMP.is_dir(), "unknown snapshot or temporary directory")
    track = "axiom" if label == "lykoi" else "conventional"
    checkpoint_hash, snapshot_hash = SNAPSHOTS[label]
    checkpoint = inventory.RESULTS / f"checkpoint-{label}-B16-r5_2.json"
    snapshot = inventory.RESULTS / f"snapshot-{label}-B16-r5_2.tar"
    w.require(w.file_hash(checkpoint) == checkpoint_hash and
              w.file_hash(snapshot) == snapshot_hash, "authoritative B16 archive/hash drift")
    record = json.loads(checkpoint.read_text(encoding="utf-8"))
    checkpoints.validate_record(record)
    w.require(record["track"] == track, "wrong checkpoint identity")
    with tempfile.TemporaryDirectory(prefix=f"r5-3-verify-{label}-", dir=TEMP) as folder:
        workspace = Path(folder) / "fresh-restore"
        w.restore(track, workspace, record, snapshot, snapshot_hash)
        w.require(w.workspace_files(workspace) == record["files"], "restored inventory changed")
        app = workspace / ("generated/task_manager.py" if track == "axiom" else
                           "benchmark/conventional/task_manager.py")
        profile = profiles.identity(record["achieved"])
        w.require(profile["expectation_sha256"] == record["expectation_sha256"],
                  "restored achieved profile changed")
        methods, _, runner_dispositions = inventory.collect(record["achieved"])
        candidate = inventory.reconstruct(methods, record["achieved"])
        diff = {name: {"candidate": candidate["dispositions"][name],
                       "runner": runner_dispositions[name]["state"]}
                for name in methods if candidate["dispositions"][name] !=
                runner_dispositions[name]["state"]}
        w.require(not diff, "candidate/runner method disposition difference")
        replacements = r5.load_module("regression_B16_R5", r5.CASE)
        suite, superseded, dispositions = r5.build_suite(
            app, profile["expectation"], record["achieved"], replacements)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=0,
                                         resultclass=original.CountedResult).run(suite)
        external = {"passed": result.successes, "skipped": len(result.skipped),
                    "case_methods": result.testsRun,
                    "failure_events": len(result.failures) + len(result.errors)}
        w.require(result.wasSuccessful() and external == (
            {"passed": 33, "skipped": 28, "case_methods": 61, "failure_events": 0}
            if track == "conventional" else
            {"passed": 7, "skipped": 2, "case_methods": 9, "failure_events": 0}),
            f"B16 external revalidation mismatch: {external}\n{stream.getvalue()}")
        w.require(set(dispositions) == set(methods) and
                  len(superseded) == (28 if track == "conventional" else 0),
                  "frozen oracle inventory changed")
        test_dir = workspace / ("tests" if track == "axiom" else "benchmark/conventional")
        internal = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir),
             "-p", "test_*.py"], cwd=workspace, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        count = 33 if track == "axiom" else 39
        w.require(internal.returncode == 0 and f"Ran {count} tests" in internal.stderr,
                  f"B16 internal revalidation mismatch: {internal.stdout}\n{internal.stderr}")
        w.require(w.workspace_files(workspace) == record["files"],
                  "revalidation modified checkpoint files")
        return {"checkpoint_sha256": checkpoint_hash, "snapshot_sha256": snapshot_hash,
                "achieved": record["achieved"], "expectation_sha256": record["expectation_sha256"],
                "file_count": len(record["files"]), "external": external,
                "internal_passed": count, "candidate_method_diff": diff,
                "candidate_assertion_equivalence_proven": False,
                "candidate_inventory_sha256": w.digest(w.encoded(
                    {"achieved": record["achieved"], "methods": methods}))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", choices=SNAPSHOTS, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.checkpoint)
    if args.output:
        w.require(args.output.parent.is_dir(), "output directory missing")
        args.output.write_bytes(w.encoded(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
