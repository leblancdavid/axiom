"""Read-only independent B16 restores against frozen R5.2 plus additive repair."""

import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import acceptance_inventory_r5_3 as prior_inventory
import assertion_preservation_r5_2_1 as repair
import capability_profile_r5_2 as profiles
import regression as original
import regression_phase5c_r5_1 as parent
import revalidate_b16_r5_3 as prior_restore
import workspace as w
import workspace_phase5c_r5_2 as checkpoints


def run(label):
    w.require(label in prior_restore.SNAPSHOTS and prior_restore.TEMP.is_dir(),
              "unknown authoritative B16 checkpoint")
    track = "axiom" if label == "lykoi" else "conventional"
    checkpoint_hash, archive_hash = prior_restore.SNAPSHOTS[label]
    checkpoint = prior_inventory.RESULTS / f"checkpoint-{label}-B16-r5_2.json"
    archive = prior_inventory.RESULTS / f"snapshot-{label}-B16-r5_2.tar"
    w.require(w.file_hash(checkpoint) == checkpoint_hash and
              w.file_hash(archive) == archive_hash, "B16 checkpoint/snapshot hash drift")
    record = json.loads(checkpoint.read_text(encoding="utf-8"))
    checkpoints.validate_record(record)
    w.require(record["track"] == track, "wrong checkpoint identity")
    with tempfile.TemporaryDirectory(prefix=f"r5-2-1-{label}-", dir=prior_restore.TEMP) as folder:
        workspace = Path(folder) / "fresh-restore"
        w.restore(track, workspace, record, archive, archive_hash)
        w.require(w.workspace_files(workspace) == record["files"], "restored inventory changed")
        app = workspace / ("generated/task_manager.py" if track == "axiom" else
                           "benchmark/conventional/task_manager.py")
        profile = profiles.identity(record["achieved"])
        w.require(profile["expectation_sha256"] == record["expectation_sha256"],
                  "restored profile drift")
        methods, _, observed = prior_inventory.collect(record["achieved"])
        prior_inventory.validate_sources(methods)
        reconstructed = prior_inventory.reconstruct(methods, record["achieved"])
        w.require(reconstructed["dispositions"] ==
                  {name: row["state"] for name, row in observed.items()},
                  "parent method inventory mismatch")
        with prior_inventory.isolated_construction():
            replacements = parent.load_module("regression_B16_R5", parent.CASE)
            suite, _, disposition, restored = repair.build_suite(
                app, profile["expectation"], record["achieved"], replacements)
            expected = 0 if label == "lykoi" else 5
            w.require(len(restored) == expected and
                      set(restored) == (set() if not expected else set(repair.ORIGINS)),
                      "restoration inventory differs from composed state")
            stream = io.StringIO()
            result = unittest.TextTestRunner(stream=stream, verbosity=2,
                                             resultclass=original.CountedResult).run(suite)
            external = {"passed": result.successes, "skipped": len(result.skipped),
                        "case_methods": result.testsRun,
                        "failure_events": len(result.failures) + len(result.errors)}
            failures = [{"method": str(test), "traceback": detail}
                        for test, detail in result.failures + result.errors]
        internal_dir = workspace / ("tests" if track == "axiom" else "benchmark/conventional")
        internal = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                                   str(internal_dir), "-p", "test_*.py"], cwd=workspace,
                                  capture_output=True, text=True,
                                  env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        w.require(w.workspace_files(workspace) == record["files"],
                  "validation modified checkpoint files")
        return {"checkpoint_sha256": checkpoint_hash, "snapshot_sha256": archive_hash,
                "achieved": record["achieved"], "expectation_sha256": record["expectation_sha256"],
                "file_count": len(record["files"]), "parent_inventory_sha256": w.digest(w.encoded(
                    {"achieved": record["achieved"], "methods": methods})),
                "repair_inventory_sha256": w.digest(w.encoded(restored)), "restored": restored,
                "external": external, "external_failures": failures,
                "internal_passed": internal.returncode == 0 and
                f"Ran {33 if track == 'axiom' else 39} tests" in internal.stderr,
                "internal_output": internal.stdout + internal.stderr}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", choices=prior_restore.SNAPSHOTS, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.checkpoint)
    if args.output:
        w.require(args.output.parent.is_dir(), "output parent absent")
        args.output.write_bytes(w.encoded(result))
    print(json.dumps({k: v for k, v in result.items() if k not in ("internal_output", "restored")},
                     sort_keys=True))
    return 0 if result["external"]["failure_events"] == 0 and result["internal_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
