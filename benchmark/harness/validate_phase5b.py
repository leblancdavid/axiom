"""Replay the recorded pilot implementations in *fresh verified* workspaces.

This validates the protocol; it is not a second agent run or a new implementation
comparison. All pilot inputs are checked against their frozen hashes.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5b"
PILOT = w.ROOT / "benchmark/results/pilot"


def execute(args, cwd=None, env=None):
    run = subprocess.run(args, cwd=cwd, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})},
                         capture_output=True, text=True)
    return {"command": args, "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr}


def checked(log, args, cwd=None, env=None):
    result = execute(args, cwd, env)
    log.append(result)
    w.require(result["exit_code"] == 0, f"failed command: {args}\n{result['stderr']}")
    return result


def case_run(log, workspace, track, achieved):
    app = workspace / ("benchmark/conventional/task_manager.py" if track == "conventional" else "generated/task_manager.py")
    args = [sys.executable, "-B", str(w.ORACLE), "--app", str(app)]
    if achieved:
        args += ["--achieved", ",".join(achieved)]
    result = checked(log, args)
    return json.loads(result["stdout"])


def internal_run(log, workspace, track):
    if track == "axiom":
        return checked(log, [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                       cwd=workspace, env={"PYTHONPATH": str(workspace / "src")})
    if (workspace / "benchmark/conventional/test_task_manager.py").is_file():
        return checked(log, [sys.executable, "-B", "-m", "unittest", "discover", "-s", "benchmark/conventional", "-v"],
                       cwd=workspace)
    return {"note": "No conventional baseline internal suite; external baseline suite is mandatory."}


def save_checkpoint(workspace, track, attempted, name):
    data = w.checkpoint(workspace, track, attempted)
    path = RESULTS / f"checkpoint-{track}-{name}.json"
    if path.exists():
        w.require(path.read_bytes() == w.encoded(data), "existing checkpoint differs from replay")
    else:
        path.write_bytes(w.encoded(data))
    archive = RESULTS / f"snapshot-{track}-{name}.tar"
    if archive.exists():
        with tempfile.TemporaryDirectory(prefix="phase5b-snapshot-check-") as directory:
            fresh = Path(directory) / "candidate.tar"
            w.snapshot(workspace, fresh)
            w.require(w.file_hash(fresh) == w.file_hash(archive), "existing step archive differs from replay")
    else:
        w.snapshot(workspace, archive)
    return {"file": path.relative_to(w.ROOT).as_posix(), "sha256": w.file_hash(path),
            "snapshot": archive.relative_to(w.ROOT).as_posix(), "snapshot_sha256": w.file_hash(archive),
            "data": data}


def gate(log, workspace, track, request, cp):
    args = [sys.executable, "-B", str(w.ROOT / "benchmark/harness/workspace.py"), "preflight",
            "--workspace", str(workspace), "--track", track, "--request", request,
            "--checkpoint", str(w.ROOT / cp["file"]), "--expected-hash", cp["sha256"]]
    return json.loads(checked(log, args)["stdout"])


def check_restore(log, root, track, cp):
    target = root / f"restored-{track}-{len(cp['data']['attempted'])}"
    args = [sys.executable, "-B", str(w.ROOT / "benchmark/harness/workspace.py"), "restore",
            "--workspace", str(target), "--track", track, "--checkpoint", str(w.ROOT / cp["file"]),
            "--expected-hash", cp["sha256"], "--snapshot", str(w.ROOT / cp["snapshot"]),
            "--snapshot-hash", cp["snapshot_sha256"]]
    result = checked(log, args)
    w.require(w.workspace_files(target) == cp["data"]["files"], "restore differs from checkpoint")
    shutil.rmtree(target)
    return json.loads(result["stdout"])


def negative_gate(workspace, track, cp, log):
    checks = {}
    with tempfile.TemporaryDirectory(prefix="phase5b-negative-") as folder:
        tmp = Path(folder)
        if track == "axiom":
            fixture = workspace / "experiments/task_manager-v0.2-before-priority.json"
            artifact = workspace / "generated/task_manager.py"
        else:
            fixture = workspace / "benchmark/conventional/task_manager.py"
            artifact = fixture
        for name, path, action in (("missing_fixture", fixture, "delete"),
                                   ("modified_fixture", fixture, "modify"),
                                   ("stale_generated" if track == "axiom" else "modified_application", artifact, "modify")):
            probe = tmp / name
            shutil.copytree(workspace, probe)
            target = probe / path.relative_to(workspace)
            if action == "delete":
                target.unlink()
            else:
                target.write_bytes(target.read_bytes() + b"\n# tampered\n")
            try:
                w.preflight(probe, track, "B01", cp["data"])
            except w.ProtocolError as exc:
                checks[name] = str(exc)
            else:
                raise w.ProtocolError(f"preflight accepted {name}")
        probe = tmp / "extra"
        shutil.copytree(workspace, probe)
        (probe / "unexpected.txt").write_text("unexpected", encoding="utf-8")
        try:
            w.preflight(probe, track, "B01", cp["data"])
        except w.ProtocolError as exc:
            checks["unexpected_file"] = str(exc)
        else:
            raise w.ProtocolError("preflight accepted unexpected file")
        for name, args in (("wrong_track", ["--track", "axiom" if track == "conventional" else "conventional"]),
                           ("wrong_requirement", ["--request", "B02"]),
                           ("wrong_checkpoint_hash", ["--expected-hash", "0" * 64])):
            params = {"track": track, "request": "B01", "expected-hash": cp["sha256"]}
            params[args[0][2:]] = args[1]
            result = execute([sys.executable, "-B", str(w.ROOT / "benchmark/harness/workspace.py"), "preflight",
                              "--workspace", str(workspace), "--checkpoint", str(w.ROOT / cp["file"]),
                              "--track", params["track"], "--request", params["request"],
                              "--expected-hash", params["expected-hash"]])
            w.require(result["exit_code"] == 2 and "INFRASTRUCTURE_PROTOCOL_FAILURE" in result["stderr"],
                      f"preflight accepted {name}")
            checks[name] = result["stderr"].strip()
            log.append(result)
    return checks


def replay_conventional(workspace):
    source = workspace / "benchmark/conventional/task_manager.py"
    text = source.read_text(encoding="utf-8")
    old = 'PRIORITIES = ("LOW", "NORMAL", "HIGH")'
    w.require(text.count(old) == 1, "conventional B01 source does not match pilot patch")
    source.write_text(text.replace(old, 'PRIORITIES = ("LOW", "NORMAL", "HIGH", "CRITICAL")'), encoding="utf-8", newline="\n")
    # Reconstruct the exact pilot-added B01 test from its preserved transcript.
    transcript = PILOT / "transcripts/conventional-B01-implementation.jsonl"
    for line in transcript.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        state = event.get("part", {}).get("state", {})
        patch = state.get("input", {}).get("patchText", "")
        if "*** Add File: test_task_manager.py" in patch and state.get("status") == "completed":
            section = patch.split("*** Add File: test_task_manager.py\n", 1)[1].split("*** End Patch", 1)[0]
            lines = [item[1:] for item in section.splitlines() if item.startswith("+")]
            (workspace / "benchmark/conventional/test_task_manager.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise w.ProtocolError("pilot B01 conventional test patch missing")


def replay_axiom(workspace, log):
    model = workspace / "air/task_manager.json"
    original = json.loads(model.read_text(encoding="utf-8"))
    prior = json.loads((PILOT / "outputs/axiom/air_task_manager.json").read_text(encoding="utf-8"))
    enum = next(t for t in original["types"] if t["id"] == "type_priority")
    invariant = next(t for t in original["invariants"] if t["id"] == "inv_priority")
    enum["values"].append("CRITICAL")
    invariant["predicate"]["values"].append("CRITICAL")
    w.require(original == prior, "pilot B01 Axiom model contains additional/unexpected edits")
    model.write_bytes((PILOT / "outputs/axiom/air_task_manager.json").read_bytes())
    (workspace / "tests/test_application.py").write_bytes(
        (PILOT / "outputs/axiom/tests_test_application.py").read_bytes())
    checked(log, [sys.executable, "-B", "-m", "air_compiler.cli", "validate", "air/task_manager.json"],
            cwd=workspace, env={"PYTHONPATH": str(workspace / "src")})
    checked(log, [sys.executable, "-B", "-m", "air_compiler.cli", "generate", "air/task_manager.json",
                  "generated/task_manager.py"], cwd=workspace, env={"PYTHONPATH": str(workspace / "src")})
    w.require(w.file_hash(workspace / "generated/task_manager.py") ==
              w.file_hash(PILOT / "outputs/axiom/generated_task_manager.py"), "pilot B01 generated output mismatch")
    w.check_generated(workspace, "axiom")


def replay_conventional_b02(workspace):
    source = workspace / "benchmark/conventional/task_manager.py"
    test = workspace / "benchmark/conventional/test_task_manager.py"
    source.write_bytes((PILOT / "outputs/conventional/task_manager.py").read_bytes())
    test.write_bytes((PILOT / "outputs/conventional/test_task_manager.py").read_bytes())
    w.require(w.file_hash(source) == "e573c719964b197f6a02efde60a9589f465f2e78f7d2efa48d35873f48282106",
              "pilot B02 conventional source mismatch")


def main():
    log = []
    stages = {}
    with tempfile.TemporaryDirectory(prefix="axiom-phase5b-", dir=os.environ.get("TEMP")) as folder:
        root = Path(folder)
        for track in ("conventional", "axiom"):
            workspace = root / track
            w.build(track, workspace)
            cp0 = save_checkpoint(workspace, track, [], "baseline")
            stages[f"{track}-baseline"] = {"checkpoint": {k: v for k, v in cp0.items() if k != "data"},
                                              "restore": check_restore(log, root, track, cp0),
                                              "preflight": gate(log, workspace, track, "B01", cp0),
                                              "oracle": case_run(log, workspace, track, []),
                                              "internal": internal_run(log, workspace, track)}
            stages[f"{track}-baseline"]["negative_preflight"] = negative_gate(workspace, track, cp0, log)
            if track == "conventional":
                replay_conventional(workspace)
            else:
                replay_axiom(workspace, log)
            cp1 = save_checkpoint(workspace, track, [{"request": "B01", "outcome": "SUCCESS"}], "B01")
            stages[f"{track}-B01"] = {"checkpoint": {k: v for k, v in cp1.items() if k != "data"},
                                         "restore": check_restore(log, root, track, cp1),
                                         "preflight_B02": gate(log, workspace, track, "B02", cp1),
                                         "oracle": case_run(log, workspace, track, ["B01"]),
                                         "internal": internal_run(log, workspace, track)}
            if track == "conventional":
                replay_conventional_b02(workspace)
                outcome, achieved = "SUCCESS", ["B01", "B02"]
            else:
                # The permitted frozen model/compiler/runtime cannot represent a
                # repeated string-array flag. Do not modify source or generated code.
                before = w.workspace_files(workspace)
                w.require(before == w.workspace_files(workspace), "gap mutated Axiom workspace")
                outcome, achieved = "AXIOM_CAPABILITY_GAP", ["B01"]
            b02 = {"request": "B02", "outcome": outcome}
            if track == "axiom":
                b02["evidence"] = "benchmark/results/pilot/REPORT.md#four-primary-runs; phase5b/validation.json:axiom-B02.unmet_B02_probe"
            cp2 = save_checkpoint(workspace, track, [{"request": "B01", "outcome": "SUCCESS"}, b02], "B02")
            stages[f"{track}-B02"] = {"checkpoint": {k: v for k, v in cp2.items() if k != "data"},
                                         "restore": check_restore(log, root, track, cp2),
                                         "outcome": outcome, "oracle": case_run(log, workspace, track, achieved),
                                         "internal": internal_run(log, workspace, track)}
            if track == "conventional":
                with tempfile.TemporaryDirectory(prefix="phase5b-regression-") as folder:
                    candidate = Path(folder) / "candidate"
                    shutil.copytree(workspace, candidate)
                    source = candidate / "benchmark/conventional/task_manager.py"
                    contents = source.read_text(encoding="utf-8")
                    original = 'task.priority == "HIGH"'
                    w.require(contents.count(original) == 1, "regression probe cannot identify filter")
                    source.write_text(contents.replace(original, 'task.priority == "CRITICAL"'), encoding="utf-8")
                    probe = execute([sys.executable, "-B", str(w.ORACLE), "--app", str(source),
                                     "--achieved", "B01,B02"])
                    log.append(probe)
                    summary = json.loads(probe["stdout"])
                    w.require(probe["exit_code"] == 1 and summary["failure_events"] > 0,
                              "injected behavioral regression escaped oracle")
                    stages[f"{track}-B02"]["regression_detection_probe"] = summary
            if track == "axiom":
                w.require(cp2["data"]["files"] == cp1["data"]["files"], "B02 gap changed Axiom state")
                probe = execute([sys.executable, "-B", str(w.ORACLE), "--app", str(workspace / "generated/task_manager.py"),
                                 "--achieved", "B01,B02"])
                log.append(probe)
                summary = json.loads(probe["stdout"])
                w.require(probe["exit_code"] == 1 and summary["failure_events"] >= 2,
                          "B02 gap probe did not demonstrate missing B02 behavior")
                stages[f"{track}-B02"]["unmet_B02_probe"] = summary
    evidence = {"format": 1, "method": "replay of recorded Phase 5A artifacts, not independent agent attempts",
                "stages": stages, "commands": log}
    output = RESULTS / "validation.json"
    w.require(not output.exists(), "validation evidence already frozen")
    output.write_bytes(w.encoded(evidence))
    print(json.dumps({"result": "PASS", "evidence_sha256": w.file_hash(output),
                      "stage_oracles": {s: data["oracle"] for s, data in stages.items()}}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"result": "ABORT", "classification": "INFRASTRUCTURE_PROTOCOL_FAILURE",
                          "reason": str(exc)}), file=sys.stderr)
        sys.exit(2)
