"""Phase 5E capability-state checkpoints; never rewrites Phase 5D records."""

import argparse
import json
from pathlib import Path
import sys

import capability_profile as capabilities
import workspace as w


ORACLE = Path(__file__).with_name("regression_phase5e.py")
COMPOSER = Path(__file__).with_name("capability_profile.py")
PHASE5D = w.ROOT / "benchmark/results/phase5d"
BRIDGE = {
    "axiom": ("checkpoint-lykoi-B03.json", "0648016ced11120e57668fb5c9bf824694a450e2463f0ffb68934d962a59a107",
              "snapshot-lykoi-B03.tar", "b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7"),
    "conventional": ("checkpoint-conventional-B03.json", "cf46300fb7fd904a6f42629a049e85bf4af64a7283d42729dd19875156b65999",
                     "snapshot-conventional-B03.tar", "1945902e524fc6e3b30d76230ea4c4c1b96a232dc0b60724ea82c2cdd9bf171c"),
}


def metadata(attempted):
    achieved = [item["request"] for item in attempted if item["outcome"] == "SUCCESS"]
    return achieved, capabilities.identity(achieved)


def record(track, attempted, files, predecessor_hash):
    w.validate_attempts(track, attempted)
    achieved, identity = metadata(attempted)
    return {"format": 3, "track": track, "attempted": attempted,
            "achieved": achieved, **identity, "files": files,
            "attempt_fragment_hashes": capabilities.fragment_hashes([item["request"] for item in attempted]),
            "attempt_case_hashes": {item["request"]: w.file_hash(w.CASES / f"{item['request']}.py")
                                    for item in attempted if int(item["request"][1:]) > 2},
            "previous_checkpoint_sha256": predecessor_hash,
            "baseline_manifest_sha256": w.file_hash(w.MANIFEST),
            "harness_sha256": w.file_hash(Path(__file__)),
            "legacy_harness_sha256": w.file_hash(Path(w.__file__)),
            "oracle_sha256": w.file_hash(ORACLE),
            "legacy_oracle_sha256": w.file_hash(w.ORACLE),
            "composer_sha256": w.file_hash(COMPOSER),
            "requirement_hashes": w.load_manifest()["requirements"],
            "case_hashes": {name: w.file_hash(w.CASES / f"{name}.py") for name in achieved
                            if int(name[1:]) > 2}}


def bridge(track):
    """Pure metadata bridge; original clean B03 archive remains byte-identical."""
    name, expected, snapshot, snapshot_hash = BRIDGE[track]
    source = PHASE5D / name
    w.require(w.file_hash(source) == expected and w.file_hash(PHASE5D / snapshot) == snapshot_hash,
              "pinned Phase 5D continuation mismatch")
    prior = json.loads(source.read_text(encoding="utf-8"))
    w.require(prior["format"] == 2 and prior["track"] == track and
              prior["harness_sha256"] == w.file_hash(Path(w.__file__)) and
              prior["oracle_sha256"] == w.file_hash(w.ORACLE) and
              prior["attempted"][-1]["request"] == "B03" and
              prior["achieved"] == [a["request"] for a in prior["attempted"] if a["outcome"] == "SUCCESS"],
              "invalid Phase 5D bridge source")
    return record(track, prior["attempted"], prior["files"], expected)


def checkpoint(workspace, track, attempted, previous, previous_hash):
    w.require(w.file_hash(previous) == previous_hash, "pinned predecessor mismatch")
    prior = json.loads(previous.read_text(encoding="utf-8"))
    validate_record(prior)
    w.require(prior["track"] == track and attempted[:-1] == prior["attempted"] and
              len(attempted) == len(prior["attempted"]) + 1, "attempt history not an exact extension")
    files = w.workspace_files(workspace)
    if attempted[-1]["outcome"] in ("AXIOM_CAPABILITY_GAP", "BLOCKED_BY_GAP"):
        w.require(files == prior["files"], "gap or block changed implementation state")
    w.check_generated(workspace, track)
    return record(track, attempted, files, previous_hash)


def validate_record(current):
    w.require(current.get("format") == 3 and current.get("track") in BRIDGE,
              "invalid Phase 5E checkpoint format or track")
    track = current["track"]
    w.validate_attempts(track, current["attempted"])
    w.require(current["attempted"] and current["achieved"] ==
              [a["request"] for a in current["attempted"] if a["outcome"] == "SUCCESS"],
              "achieved capabilities do not match attempt history")
    expected = record(track, current["attempted"], current["files"],
                      current["previous_checkpoint_sha256"])
    w.require(current == expected, "checkpoint capability/protocol identity mismatch")
    if len(current["attempted"]) == 3:
        w.require(current == bridge(track), "unrecognized Phase 5E bridge checkpoint")
    return expected


def preflight(workspace, track, request, current, case_hash, fragment_hash):
    validate_record(current)
    w.require(track == current["track"] and request == f"B{len(current['attempted']) + 1:02}" and
              request in current["requirement_hashes"], "wrong next request/track")
    w.require(w.file_hash(w.REQUIREMENTS / f"{request}.md") == current["requirement_hashes"][request],
              "prospective requirement hash mismatch")
    w.require(case_hash == w.file_hash(w.CASES / f"{request}.py") and
              fragment_hash == w.file_hash(capabilities.FRAGMENTS / f"{request}.json"),
              "prospective case/capability not frozen")
    w.require(w.workspace_files(workspace) == current["files"], "workspace inventory mismatch")
    w.require("experiments/task_manager-v0.2-before-priority.json" in current["files"] if track == "axiom"
              else "benchmark/conventional/task_manager.py" in current["files"], "required fixture absent")
    w.require(not any(p.startswith("benchmark/conventional/") for p in current["files"]) if track == "axiom"
              else not any(p.startswith(("air/", "generated/", "src/", "tests/")) for p in current["files"]),
              "cross-track contamination")
    w.check_generated(workspace, track)
    return {"result": "PASS", "track": track, "request": request,
            "checkpoint_sha256": w.digest(w.encoded(current)),
            "expectation_sha256": current["expectation_sha256"],
            "files": len(current["files"])}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    bridge_cmd = sub.add_parser("bridge")
    bridge_cmd.add_argument("--track", choices=BRIDGE, required=True)
    bridge_cmd.add_argument("--output", type=Path, required=True)
    for action in ("checkpoint", "preflight", "restore", "snapshot"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--track", choices=BRIDGE, required=True)
        cmd.add_argument("--workspace", type=Path, required=True)
        cmd.add_argument("--checkpoint", type=Path, required=True)
        cmd.add_argument("--expected-hash", required=True)
        if action == "checkpoint":
            cmd.add_argument("--attempts-file", type=Path, required=True)
            cmd.add_argument("--output", type=Path, required=True)
        if action == "preflight":
            cmd.add_argument("--request", required=True)
            cmd.add_argument("--case-hash", required=True)
            cmd.add_argument("--fragment-hash", required=True)
        if action == "restore":
            cmd.add_argument("--snapshot", type=Path, required=True)
            cmd.add_argument("--snapshot-hash", required=True)
        if action == "snapshot":
            cmd.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "bridge":
            w.require(not args.output.exists() and args.output.parent.is_dir(), "bridge output exists or parent absent")
            args.output.write_bytes(w.encoded(bridge(args.track)))
            print(w.file_hash(args.output))
            return 0
        w.require(w.file_hash(args.checkpoint) == args.expected_hash, "checkpoint hash mismatch")
        current = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        validate_record(current)
        w.require(current["track"] == args.track, "track mismatch")
        if args.action == "restore":
            w.restore(args.track, args.workspace, current, args.snapshot, args.snapshot_hash)
            print(json.dumps({"result": "PASS", "files": len(current["files"])}))
        elif args.action == "preflight":
            print(json.dumps(preflight(args.workspace, args.track, args.request, current,
                                       args.case_hash, args.fragment_hash), sort_keys=True))
        elif args.action == "checkpoint":
            attempts = json.loads(args.attempts_file.read_text(encoding="utf-8"))
            result = checkpoint(args.workspace, args.track, attempts, args.checkpoint, args.expected_hash)
            w.require(not args.output.exists() and args.output.parent.is_dir(), "checkpoint output invalid")
            args.output.write_bytes(w.encoded(result))
            print(w.file_hash(args.output))
        elif args.action == "snapshot":
            w.require(w.workspace_files(args.workspace) == current["files"], "workspace differs from checkpoint")
            w.check_generated(args.workspace, args.track)
            print(w.snapshot(args.workspace, args.output))
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
        print(json.dumps({"result": "ABORT", "classification": "INFRASTRUCTURE_PROTOCOL_FAILURE",
                          "reason": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
