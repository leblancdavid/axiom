"""Phase 5B workspace builder and fail-closed preflight. No application imports."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "benchmark/results/pilot/baseline-snapshot.tar"
ARCHIVE_SHA256 = "71bd1692adb5b34de2e99fca40da657b20b2e838e9816bdb0d801cbdca44eb13"
MANIFEST = ROOT / "benchmark/results/phase5b/baseline-manifest.json"
ORACLE = ROOT / "benchmark/harness/regression.py"
PILOT_ORACLE = ROOT / "benchmark/harness/pilot_oracle.py"
BASELINE_ORACLE = ROOT / "benchmark/harness/test_baseline.py"
REQUIREMENTS = ROOT / "benchmark/requirements"
PROFILES = ROOT / "benchmark/harness/profiles"
CASES = ROOT / "benchmark/harness/cases"
EXPECTED_REQUIREMENTS = {
    "B01": "b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d",
    "B02": "8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b",
}
FROZEN_PROFILES = {
    "baseline": "56890855fc2161c06693657e11534349c4ebfef71316e866ebcd3f1cbc6dd808",
    "B01": "56890855fc2161c06693657e11534349c4ebfef71316e866ebcd3f1cbc6dd808",
    "B02": "46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f",
}


class ProtocolError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def encoded(data):
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True).encode() + b"\n"


def require(ok, reason):
    if not ok:
        raise ProtocolError(reason)


def archive_files():
    require(file_hash(ARCHIVE) == ARCHIVE_SHA256, "baseline archive hash mismatch")
    with tarfile.open(ARCHIVE) as archive:
        seen = set()
        result = {}
        for member in archive:
            path = Path(member.name)
            require(member.isfile() and not path.is_absolute() and ".." not in path.parts
                    and len(path.parts) >= 1 and member.name not in seen,
                    f"unsafe or duplicate archive member: {member.name}")
            seen.add(member.name)
            result[member.name] = archive.extractfile(member).read()
        return result


def track_paths(files, track):
    require(track in ("axiom", "conventional"), "unknown track")
    if track == "conventional":
        paths = ["benchmark/conventional/task_manager.py"]
    else:
        paths = [p for p in files if p.startswith(("air/", "docs/", "experiments/", "generated/",
                                                 "schema/", "src/", "tests/"))]
    require(all(p in files for p in paths), "archive missing selected file")
    if track == "axiom":
        require("experiments/task_manager-v0.2-before-priority.json" in paths,
                "historical compiler fixture absent")
    return sorted(paths)


def make_manifest():
    files = archive_files()
    return {"format": 1, "archive_sha256": ARCHIVE_SHA256,
            "files": {p: digest(data) for p, data in sorted(files.items())},
            "tracks": {t: track_paths(files, t) for t in ("conventional", "axiom")},
            "requirements": {f"B{i:02}": file_hash(REQUIREMENTS / f"B{i:02}.md")
                             for i in range(1, 21)}}


def load_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(data == make_manifest(), "frozen archive/requirements manifest mismatch")
    for name, expected in EXPECTED_REQUIREMENTS.items():
        require(data["requirements"][name] == expected, f"{name} frozen hash mismatch")
    for name, expected in FROZEN_PROFILES.items():
        require(file_hash(PROFILES / f"{name}.json") == expected, f"{name} frozen profile mismatch")
    return data


def workspace_files(workspace):
    result = {}
    for path in workspace.rglob("*"):
        if path.is_symlink():
            raise ProtocolError(f"workspace symlink: {path}")
        if path.is_file():
            rel = path.relative_to(workspace).as_posix()
            result[rel] = file_hash(path)
    return result


def build(track, destination):
    manifest = load_manifest()
    require(not destination.exists(), "destination already exists")
    require(destination.parent.is_dir(), "destination parent missing")
    files = archive_files()
    destination.mkdir()
    try:
        for name in manifest["tracks"][track]:
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(files[name])
        expected = {p: manifest["files"][p] for p in manifest["tracks"][track]}
        require(workspace_files(destination) == expected, "built workspace differs from baseline projection")
        check_generated(destination, track)
    except Exception:
        shutil.rmtree(destination)
        raise
    return expected


def snapshot(workspace, output):
    """Write a byte-for-byte restorable, deterministic snapshot of one step."""
    require(not output.exists() and output.parent.is_dir(), "snapshot destination invalid")
    files = workspace_files(workspace)
    with tarfile.open(output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name in sorted(files):
            content = (workspace / name).read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(content))
    return file_hash(output)


def restore(track, destination, record, snapshot_path, expected_snapshot_hash):
    require(file_hash(snapshot_path) == expected_snapshot_hash, "step snapshot hash mismatch")
    require(record["track"] == track, "step snapshot track mismatch")
    require(not destination.exists() and destination.parent.is_dir(), "restore destination invalid")
    files = {}
    with tarfile.open(snapshot_path) as archive:
        for member in archive:
            path = Path(member.name)
            require(member.isfile() and not path.is_absolute() and ".." not in path.parts
                    and member.name not in files, f"unsafe step snapshot member {member.name}")
            files[member.name] = archive.extractfile(member).read()
    require({p: digest(blob) for p, blob in files.items()} == record["files"], "step snapshot files differ from checkpoint")
    destination.mkdir()
    try:
        for name, blob in files.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        require(workspace_files(destination) == record["files"], "restored workspace hash mismatch")
        check_generated(destination, track)
    except Exception:
        shutil.rmtree(destination)
        raise


def check_generated(workspace, track):
    if track != "axiom":
        return
    artifact = workspace / "generated/task_manager.py"
    manifest = json.loads((workspace / "generated/task_manager.manifest.json").read_text(encoding="utf-8"))
    require(manifest["artifacts"][0]["sha256"] == file_hash(artifact), "stale generated manifest")
    code = ("import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1])/'src')); "
            "from air_compiler.generator import generate; from air_compiler.parser import load; "
            "print(generate(load(Path(sys.argv[1])/'air/task_manager.json')), end='')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, "-c", code, str(workspace.resolve())],
                            capture_output=True, env=env)
    require(result.returncode == 0 and result.stdout.replace(b"\r\n", b"\n") == artifact.read_bytes(),
            f"generated artifact does not match model/compiler: {result.stderr.decode(errors='replace')}")


def checkpoint(workspace, track, attempted):
    manifest = load_manifest()
    require(track in manifest["tracks"], "unknown track")
    ids = [item["request"] for item in attempted]
    require(ids == [f"B{i:02}" for i in range(1, len(ids) + 1)], "nonsequential attempts")
    require(all(item["outcome"] in ("SUCCESS", "AXIOM_CAPABILITY_GAP", "IMPLEMENTATION_FAILURE",
                                     "REGRESSION", "BLOCKED_BY_GAP") for item in attempted), "invalid outcome")
    require(not any(item["outcome"] == "AXIOM_CAPABILITY_GAP" for item in attempted)
            or track == "axiom", "gap on non-Axiom track")
    gaps = set()
    for item in attempted:
        if item["outcome"] == "BLOCKED_BY_GAP":
            require(isinstance(item.get("depends_on"), list) and item["depends_on"]
                    and all(dep in gaps for dep in item["depends_on"]),
                    "blocked request must identify existing gap dependencies")
        if item["outcome"] == "AXIOM_CAPABILITY_GAP":
            require(isinstance(item.get("evidence"), str) and item["evidence"].strip(),
                    "capability gap requires evidence reference")
            gaps.add(item["request"])
    achieved = [item["request"] for item in attempted if item["outcome"] == "SUCCESS"]
    profile = achieved[-1] if achieved else "baseline"
    return {"format": 1, "track": track, "attempted": attempted,
            "achieved": achieved, "profile": profile,
            "profile_sha256": file_hash(PROFILES / f"{profile}.json"),
            "case_hashes": {name: file_hash(CASES / f"{name}.py") for name in achieved if int(name[1:]) > 2},
            "baseline_manifest_sha256": file_hash(MANIFEST),
            "harness_sha256": file_hash(Path(__file__)),
            "oracle_sha256": file_hash(ORACLE),
            "requirement_hashes": manifest["requirements"],
            "files": workspace_files(workspace)}


def preflight(workspace, track, request, record, case_hash=None, profile_hash=None):
    manifest = load_manifest()
    require(record["format"] == 1 and record["track"] == track, "track/checkpoint mismatch")
    require(record["baseline_manifest_sha256"] == file_hash(MANIFEST), "starting baseline identifier mismatch")
    require(record["harness_sha256"] == file_hash(Path(__file__)), "workspace harness version mismatch")
    require(record["oracle_sha256"] == file_hash(ORACLE), "regression oracle version mismatch")
    require(record["requirement_hashes"] == manifest["requirements"], "requirement set mismatch")
    require(request == f"B{len(record['attempted']) + 1:02}" and request in manifest["requirements"],
            "incorrect next request")
    require(file_hash(REQUIREMENTS / f"{request}.md") == record["requirement_hashes"][request],
            "request content hash mismatch")
    require(record["achieved"] == [a["request"] for a in record["attempted"] if a["outcome"] == "SUCCESS"],
            "accumulated state inconsistent")
    profile = record["achieved"][-1] if record["achieved"] else "baseline"
    require(record["profile"] == profile and
            record["profile_sha256"] == file_hash(PROFILES / f"{profile}.json"),
            "regression profile/version mismatch")
    require(record["case_hashes"] ==
            {name: file_hash(CASES / f"{name}.py") for name in record["achieved"] if int(name[1:]) > 2},
            "accumulated case fixture hash mismatch")
    if int(request[1:]) > 2:
        require(case_hash is not None and file_hash(CASES / f"{request}.py") == case_hash,
                "new request case fixture missing or unfrozen")
        require(profile_hash is not None and file_hash(PROFILES / f"{request}.json") == profile_hash,
                "new request schema profile missing or unfrozen")
    require(all(a["request"] == f"B{i:02}" for i, a in enumerate(record["attempted"], 1)),
            "attempt history inconsistent")
    require(checkpoint(workspace, track, record["attempted"])["attempted"] == record["attempted"],
            "attempt status/dependency semantics invalid")
    require(workspace.is_dir() and workspace_files(workspace) == record["files"],
            "workspace missing, modified or has unexpected files")
    require("experiments/task_manager-v0.2-before-priority.json" in record["files"] if track == "axiom"
            else "benchmark/conventional/task_manager.py" in record["files"], "required fixture/source absent")
    require(not any(p.startswith("benchmark/conventional/") for p in record["files"]) if track == "axiom"
            else not any(p.startswith(("air/", "generated/", "src/", "tests/")) for p in record["files"]),
            "cross-track contamination")
    if not record["attempted"]:
        require(record["files"] == {p: manifest["files"][p] for p in manifest["tracks"][track]},
                "incorrect baseline starting state")
    check_generated(workspace, track)
    return {"result": "PASS", "track": track, "request": request,
            "checkpoint_sha256": digest(encoded(record)), "files": len(record["files"]),
            "oracle_sha256": record["oracle_sha256"],
            "requirement_sha256": record["requirement_hashes"][request]}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("manifest")
    for action in ("build", "checkpoint", "preflight", "restore", "snapshot"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--workspace", type=Path, required=True)
        cmd.add_argument("--track", choices=("conventional", "axiom"), required=True)
        if action == "checkpoint":
            cmd.add_argument("--attempted", default="", help="comma-separated B01:SUCCESS,B02:AXIOM_CAPABILITY_GAP")
            cmd.add_argument("--attempts-file", type=Path, help="JSON list for gaps (evidence) and blocked dependencies")
            cmd.add_argument("--output", type=Path, required=True)
        if action == "preflight":
            cmd.add_argument("--request", required=True)
            cmd.add_argument("--checkpoint", type=Path, required=True)
            cmd.add_argument("--expected-hash", required=True, help="previously frozen checkpoint SHA-256")
            cmd.add_argument("--case-hash", help="frozen new request case SHA-256 (B03 onwards)")
            cmd.add_argument("--profile-hash", help="frozen new request profile SHA-256 (B03 onwards)")
        if action == "restore":
            cmd.add_argument("--checkpoint", type=Path, required=True)
            cmd.add_argument("--expected-hash", required=True)
            cmd.add_argument("--snapshot", type=Path, required=True)
            cmd.add_argument("--snapshot-hash", required=True)
        if action == "snapshot":
            cmd.add_argument("--checkpoint", type=Path, required=True)
            cmd.add_argument("--expected-hash", required=True)
            cmd.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "manifest":
            require(not MANIFEST.exists(), "manifest already frozen")
            MANIFEST.parent.mkdir(parents=True, exist_ok=True)
            MANIFEST.write_bytes(encoded(make_manifest()))
            print(file_hash(MANIFEST))
        elif args.action == "build":
            print(json.dumps({"files": len(build(args.track, args.workspace))}))
        elif args.action == "checkpoint":
            require(not (args.attempts_file and args.attempted), "use one attempt source")
            attempts = (json.loads(args.attempts_file.read_text(encoding="utf-8")) if args.attempts_file
                        else [dict(zip(("request", "outcome"), item.split(":")))
                              for item in args.attempted.split(",") if item])
            data = checkpoint(args.workspace, args.track, attempts)
            require(args.output.parent.is_dir() and not args.output.exists(), "checkpoint destination invalid")
            args.output.write_bytes(encoded(data))
            print(file_hash(args.output))
        elif args.action == "restore":
            require(file_hash(args.checkpoint) == args.expected_hash, "pinned checkpoint hash mismatch")
            restore(args.track, args.workspace, json.loads(args.checkpoint.read_text(encoding="utf-8")),
                    args.snapshot, args.snapshot_hash)
            print(json.dumps({"result": "PASS", "files": len(workspace_files(args.workspace))}))
        elif args.action == "snapshot":
            require(file_hash(args.checkpoint) == args.expected_hash, "pinned checkpoint hash mismatch")
            record = json.loads(args.checkpoint.read_text(encoding="utf-8"))
            require(record["track"] == args.track and workspace_files(args.workspace) == record["files"],
                    "workspace differs from pinned checkpoint")
            check_generated(args.workspace, args.track)
            print(snapshot(args.workspace, args.output))
        else:
            require(file_hash(args.checkpoint) == args.expected_hash, "pinned checkpoint hash mismatch")
            record = json.loads(args.checkpoint.read_text(encoding="utf-8"))
            print(json.dumps(preflight(args.workspace, args.track, args.request, record,
                                       args.case_hash, args.profile_hash), sort_keys=True))
    except (ProtocolError, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
        print(json.dumps({"result": "ABORT", "classification": "INFRASTRUCTURE_PROTOCOL_FAILURE",
                          "reason": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
