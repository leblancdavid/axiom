"""Lykoi protocol amendment: observer-safe execution and pinned checkpoint bridge."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

import workspace as w


RESULTS = w.ROOT / "benchmark/results"
PINS = {
    "axiom": {
        "prior": ("phase5b/checkpoint-axiom-B02.json", "31dd8302529cdfabd0609ca7b3dddd64ca48764f1ae0255dfcb79d91a400ba90"),
        "source": ("phase5c/checkpoint-axiom-B03.json", "c81c5187ac14aee7052a07b370e1678d75e7fc0ac8eac1490ba052f80c8beb80"),
        "snapshot": ("phase5b/snapshot-axiom-B02.tar", "b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7"),
        "caches": (),
    },
    "conventional": {
        "prior": ("phase5b/checkpoint-conventional-B02.json", "a57c38e0681a0fce5e43b09cdf32ea3a348217b6f5ab6ae03e918b3482fc5e7a"),
        "source": ("phase5c/checkpoint-conventional-B03.json", "727950c4e89b295333ab819eb23e76937b05775d5557e4d287f4fd0041686d19"),
        "snapshot": ("phase5c/snapshot-conventional-B03.tar", "58e7f75af2a4b57327a2ca0cce3f91ddb778a824a97b3b5765ffc5119e3f8f82"),
        "caches": ("benchmark/conventional/__pycache__/task_manager.cpython-314.pyc",
                   "benchmark/conventional/__pycache__/test_task_manager.cpython-314.pyc"),
    },
}


def pinned(pair):
    path, expected = pair
    source = RESULTS / path
    w.require(w.file_hash(source) == expected, f"historical evidence hash mismatch: {path}")
    return source, expected


def bridge(track, destination, checkpoint_path, snapshot_path):
    """Verify old bytes exactly; omit only the two proven Conventional caches."""
    config = PINS[track]
    prior_path, prior_hash = pinned(config["prior"])
    source_path, _ = pinned(config["source"])
    archive_path, _ = pinned(config["snapshot"])
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    w.require(prior["track"] == track and source["track"] == track and
              [(a["request"], a["outcome"]) for a in source["attempted"][:-1]] ==
              [(a["request"], a["outcome"]) for a in prior["attempted"]] and
              source["attempted"][-1]["request"] == "B03", "invalid B03 provenance")
    # The halted Lykoi coordinator shortened the B02 evidence citation in its
    # attempt file. Preserve the pinned predecessor's full citation instead.
    attempts = [*prior["attempted"], source["attempted"][-1]]
    w.require(not destination.exists() and destination.parent.is_dir(), "bridge workspace destination invalid")
    w.require(not checkpoint_path.exists() and checkpoint_path.parent.is_dir() and
              not snapshot_path.exists() and snapshot_path.parent.is_dir(), "bridge evidence destination invalid")
    blobs = {}
    with tarfile.open(archive_path) as archive:
        for member in archive:
            name = member.name
            path = Path(name)
            w.require(member.isfile() and not path.is_absolute() and ".." not in path.parts and
                      name not in blobs, f"invalid historical archive member: {name}")
            blobs[name] = archive.extractfile(member).read()
    w.require({name: w.digest(blob) for name, blob in blobs.items()} == source["files"]
              if track == "conventional" else
              {name: w.digest(blob) for name, blob in blobs.items()} == prior["files"],
              "historical snapshot does not match its checkpoint")
    caches = set(config["caches"])
    w.require(caches <= blobs.keys(), "expected historical caches missing")
    for name in caches:
        stem = Path(name).name.split(".cpython-314.pyc")[0]
        source_name = f"benchmark/conventional/{stem}.py"
        w.require(source_name in blobs and blobs[name][:4] == importlib.util.MAGIC_NUMBER,
                  f"unverified historical bytecode: {name}")
    clean = {name: blob for name, blob in blobs.items() if name not in caches}
    if track == "axiom":
        w.require({name: w.digest(blob) for name, blob in clean.items()} == prior["files"],
                  "blocked Lykoi state differs from the last valid checkpoint")
        incidental = source["files"].keys() - prior["files"].keys()
        w.require(len(incidental) == 8 and
                  all(name.startswith("src/air_compiler/__pycache__/") and
                      name.endswith(".cpython-314.pyc") and
                      f"src/air_compiler/{Path(name).name.removesuffix('.cpython-314.pyc')}.py" in prior["files"]
                      for name in incidental) and
                  {name: hash_ for name, hash_ in source["files"].items() if name not in incidental} == prior["files"],
                  "quarantined B03 contains an unclassified implementation change")
        attempts_path = RESULTS / "phase5c/B03-axiom-attempts.json"
        w.require(json.loads(attempts_path.read_text(encoding="utf-8")) == source["attempted"],
                  "recorded B03 dependency attempt differs from quarantined evidence")
    else:
        w.require({name: w.digest(blob) for name, blob in clean.items()} ==
                  {name: hash_ for name, hash_ in source["files"].items() if name not in caches},
                  "Conventional implementation differs from historical B03")
    destination.mkdir()
    try:
        for name, blob in clean.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
        w.require(w.workspace_files(destination) == {n: w.digest(b) for n, b in clean.items()},
                  "bridged workspace differs from verified implementation state")
        record = w.checkpoint(destination, track, attempts, prior, prior_hash)
        checkpoint_path.write_bytes(w.encoded(record))
        snapshot_hash = w.snapshot(destination, snapshot_path)
        return {"track": "Lykoi" if track == "axiom" else "Conventional",
                "previous_checkpoint_sha256": prior_hash, "source_checkpoint_sha256": w.file_hash(source_path),
                "implementation_files": len(record["files"]), "historical_caches_removed": sorted(caches),
                "checkpoint_sha256": w.file_hash(checkpoint_path), "snapshot_sha256": snapshot_hash}
    except BaseException:
        # Keep any produced evidence/workspace for diagnosis; never alter source evidence.
        raise


def run(workspace, command, read_only):
    w.require(workspace.is_dir(), "missing benchmark workspace")
    before = w.workspace_files(workspace)
    w.require(command and command[0] != "--", "missing command")
    with tempfile.TemporaryDirectory(prefix="lykoi-observer-", dir=workspace.parent) as outside:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TEMP": outside,
               "TMP": outside, "TMPDIR": outside, "PYTHONPYCACHEPREFIX": outside}
        if (workspace / "src").is_dir():
            env["PYTHONPATH"] = str((workspace / "src").resolve())
        result = subprocess.run(command, cwd=workspace, env=env)
    after = w.workspace_files(workspace)
    if read_only:
        w.require(after == before, "observation changed benchmark implementation bytes")
    return result.returncode


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    bridge_cmd = sub.add_parser("bridge")
    bridge_cmd.add_argument("--track", choices=PINS, required=True)
    bridge_cmd.add_argument("--workspace", type=Path, required=True)
    bridge_cmd.add_argument("--checkpoint", type=Path, required=True)
    bridge_cmd.add_argument("--snapshot", type=Path, required=True)
    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("--workspace", type=Path, required=True)
    run_cmd.add_argument("--read-only", action="store_true")
    run_cmd.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.action == "bridge":
            print(json.dumps(bridge(args.track, args.workspace, args.checkpoint, args.snapshot), sort_keys=True))
            return 0
        command = args.command[1:] if args.command and args.command[0] == "--" else args.command
        return run(args.workspace, command, args.read_only)
    except (w.ProtocolError, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
        print(json.dumps({"result": "ABORT", "classification": "INFRASTRUCTURE_PROTOCOL_FAILURE",
                          "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
