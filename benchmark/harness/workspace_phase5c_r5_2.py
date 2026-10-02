"""Versioned B16 checkpoints over the pinned, independent R5.2 B15 states."""

import argparse
import json
from pathlib import Path
import sys

import capability_profile_r5_2 as relative
import regression_phase5c_r5_2 as oracle
import workspace as w
import workspace_phase5e as legacy


RESULTS = w.ROOT / "benchmark/results/phase5c"
PREDECESSORS = {
    "conventional": "b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3",
    "axiom": "c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0",
}
TARGETS = {
    "conventional": "272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8",
    "axiom": "0c61e3be245c0b0e2870ed872c71ea62a6423b59c90575ac720e41f608040f98",
}
PROTOCOL = "PHASE5C-R5-STATE-RELATIVE/1"
PINS = {
    "amendment_sha256": (RESULTS / "PROTOCOL_AMENDMENT_R5_2_STATE_RELATIVE.md",
                         "ecdf7b72e79a0756c628a998e6ed7654b02c26e4de20191317edc64ca237d828"),
    "composer_sha256": (Path(relative.__file__), oracle.COMPOSER_SHA256),
    "oracle_sha256": (Path(oracle.__file__),
                      "ef0aa0b99b7c9f398d5096bb4c90268e48b7f0116427df1bab7bf5e1b4f7a2c2"),
    "legacy_oracle_sha256": (Path(oracle.r5.__file__), oracle.R5_1_SHA256),
    "b16_requirement_sha256": (w.REQUIREMENTS / "B16.md", oracle.REQUIREMENT_SHA256),
    "b16_case_sha256": (w.CASES / "B16.py", oracle.CASE_SHA256),
    "b16_fragment_sha256": (relative.FRAGMENTS / "B16.json", oracle.FRAGMENT_SHA256),
    "b16_replacements_sha256": (oracle.r5.CASE, oracle.r5.CASE_SHA256),
}


def pins():
    for name, (path, expected) in PINS.items():
        w.require(w.file_hash(path) == expected, f"R5.2 frozen pin mismatch: {name}")
    return {name: expected for name, (_, expected) in PINS.items()}


def predecessor(track):
    w.require(track in PREDECESSORS, "unknown B16 track")
    label = "lykoi" if track == "axiom" else track
    path = RESULTS / f"checkpoint-{label}-B15-r4.json"
    w.require(w.file_hash(path) == PREDECESSORS[track], "B15 predecessor hash mismatch")
    prior = json.loads(path.read_text(encoding="utf-8"))
    legacy.validate_record(prior)
    w.require(prior["track"] == track and prior["attempted"][-1]["request"] == "B15" and
              "B16" not in prior["achieved"], "invalid B15 predecessor")
    return prior


def record(track, attempted, files):
    prior = predecessor(track)
    frozen = pins()
    w.require(isinstance(files, dict) and
              all(isinstance(path, str) and isinstance(value, str) and len(value) == 64
                  for path, value in files.items()), "invalid implementation inventory")
    if track == "conventional":
        w.require("benchmark/conventional/task_manager.py" in files and
                  not any(p.startswith(("air/", "generated/", "src/", "tests/")) for p in files),
                  "cross-track implementation contamination")
    else:
        w.require("generated/task_manager.py" in files and
                  not any(p.startswith("benchmark/conventional/") for p in files),
                  "cross-track implementation contamination")
    w.validate_attempts(track, attempted)
    w.require(attempted[:-1] == prior["attempted"] and len(attempted) == 16 and
              attempted[-1]["request"] == "B16", "B16 attempts must extend pinned B15")
    achieved = [a["request"] for a in attempted if a["outcome"] == "SUCCESS"]
    identity = relative.identity(achieved)
    if attempted[-1]["outcome"] == "SUCCESS":
        w.require(identity["expectation_sha256"] == TARGETS[track], "frozen B16 target mismatch")
    else:
        w.require(files == prior["files"], "non-success B16 changed implementation state")
        w.require(identity["expectation_sha256"] == prior["expectation_sha256"],
                  "non-success B16 changed achieved semantics")
    return {"format": 4, "protocol_version": PROTOCOL, "track": track,
            "attempted": attempted, "achieved": achieved, **identity, "files": files,
            "previous_checkpoint_sha256": PREDECESSORS[track],
            "baseline_manifest_sha256": prior["baseline_manifest_sha256"],
            "requirement_hashes": prior["requirement_hashes"],
            "attempt_fragment_hashes": {**prior["attempt_fragment_hashes"],
                                        "B16": frozen["b16_fragment_sha256"]},
            "attempt_case_hashes": {**prior["attempt_case_hashes"],
                                    "B16": frozen["b16_case_sha256"]},
            "case_hashes": {**prior["case_hashes"], **({"B16": frozen["b16_case_sha256"]}
                                              if "B16" in achieved else {})},
            "applicable_oracle_sha256": (frozen["oracle_sha256"] if "B16" in achieved
                                         else frozen["legacy_oracle_sha256"]),
            "harness_sha256": w.file_hash(Path(__file__)), **frozen}


def validate_record(current):
    w.require(current.get("format") == 4 and current.get("protocol_version") == PROTOCOL and
              current.get("track") in PREDECESSORS, "invalid R5.2 checkpoint version/track")
    expected = record(current["track"], current["attempted"], current["files"])
    w.require(current == expected, "R5.2 checkpoint inventory or identity mismatch")
    return expected


def checkpoint(workspace, track, attempted):
    prior = predecessor(track)
    files = w.workspace_files(workspace)
    w.require(set(files).isdisjoint({"checkpoint.json", "snapshot.tar"}),
              "evidence stored inside implementation workspace")
    w.check_generated(workspace, track)
    result = record(track, attempted, files)
    w.require(result["track"] == prior["track"], "cross-track predecessor")
    if track == "conventional":
        w.require("benchmark/conventional/task_manager.py" in files and
                  not any(p.startswith(("air/", "generated/", "src/", "tests/")) for p in files),
                  "cross-track implementation contamination")
    else:
        w.require("generated/task_manager.py" in files and
                  not any(p.startswith("benchmark/conventional/") for p in files),
                  "cross-track implementation contamination")
    return result


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("checkpoint", "snapshot", "restore"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--track", choices=PREDECESSORS, required=True)
        cmd.add_argument("--workspace", type=Path, required=True)
        cmd.add_argument("--checkpoint", type=Path, required=True)
        if action == "checkpoint":
            cmd.add_argument("--attempts-file", type=Path, required=True)
        else:
            cmd.add_argument("--expected-hash", required=True)
            cmd.add_argument("--snapshot", type=Path, required=True)
            if action == "restore":
                cmd.add_argument("--snapshot-hash", required=True)
    args = parser.parse_args()
    try:
        if args.action == "checkpoint":
            w.require(not args.checkpoint.exists() and args.checkpoint.parent.is_dir(),
                      "checkpoint output exists or parent absent")
            attempts = json.loads(args.attempts_file.read_text(encoding="utf-8"))
            args.checkpoint.write_bytes(w.encoded(checkpoint(args.workspace, args.track, attempts)))
            print(w.file_hash(args.checkpoint))
        else:
            w.require(w.file_hash(args.checkpoint) == args.expected_hash,
                      "R5.2 checkpoint hash mismatch")
            current = json.loads(args.checkpoint.read_text(encoding="utf-8"))
            validate_record(current)
            w.require(current["track"] == args.track, "R5.2 track mismatch")
            if args.action == "snapshot":
                w.require(w.workspace_files(args.workspace) == current["files"],
                          "snapshot inventory mismatch")
                w.check_generated(args.workspace, args.track)
                print(w.snapshot(args.workspace, args.snapshot))
            else:
                w.restore(args.track, args.workspace, current, args.snapshot, args.snapshot_hash)
                print(json.dumps({"result": "PASS", "files": len(current["files"]),
                                  "expectation_sha256": current["expectation_sha256"]}))
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
        print(json.dumps({"result": "ABORT", "classification": "INFRASTRUCTURE_PROTOCOL_FAILURE",
                          "reason": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
