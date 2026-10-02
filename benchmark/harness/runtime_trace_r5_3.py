"""Prospective observation of the frozen external oracle; never an acceptance oracle.

The only patches are process-local wrappers, installed after suite construction.
The restored application runs in a separate process and is never instrumented.
"""

import argparse
import ast
from contextlib import contextmanager
import datetime
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import acceptance_inventory_r5_3 as inventory
import assertion_preservation_r5_2_2 as frozen
import capability_profile_r5_2 as profiles
import regression as original
import regression_phase5c_r5_1 as runner
import revalidate_b16_r5_3 as restores
import workspace as w
import workspace_phase5c_r5_2 as checkpoints


UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
ISO = re.compile(r"\b\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\b")
HELPERS = {"call", "create", "check_task", "check_created", "upgraded", "owner_call", "_call"}


def source(frame):
    try:
        path = Path(frame.f_code.co_filename).resolve().relative_to(w.ROOT).as_posix()
    except ValueError:
        return None
    if not path.startswith("benchmark/harness/") or path == "benchmark/harness/runtime_trace_r5_3.py":
        return None
    return f"{path}:{frame.f_lineno}"


class Recorder:
    def __init__(self, workspace=None):
        self.raw = []
        self.method = None
        self.serial = 0
        self.invocations = {}
        self.contexts = {}
        self.places = {}
        self.workspace = workspace

    def emit(self, kind, frame, **fields):
        self.raw.append({"kind": kind, "method": self.method, "source": source(frame), **fields})

    def sites(self, frame):
        path = frame.f_code.co_filename
        if path not in self.places:
            try:
                tree = ast.parse(Path(path).read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                return {}
            sites = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.Assert, ast.For, ast.Raise)):
                    sites.setdefault(node.lineno, []).append({
                        "kind": type(node).__name__, "expression": ast.unparse(
                            node.test if isinstance(node, (ast.If, ast.Assert)) else
                            node.iter if isinstance(node, ast.For) else node)})
            self.places[path] = sites
        return self.places[path]

    def trace(self, frame, event, arg):
        if self.method is None or source(frame) is None:
            return None
        if event == "call" and frame.f_code.co_name in HELPERS:
            self.serial += 1
            self.invocations[id(frame)] = self.serial
            self.emit("helper_enter", frame, invocation=self.serial,
                      helper=frame.f_code.co_name,
                      caller=source(frame.f_back),
                      arguments={k: v for k, v in frame.f_locals.items() if k not in ("self", "test")})
        elif event == "return" and id(frame) in self.invocations:
            self.emit("helper_return", frame, invocation=self.invocations.pop(id(frame)), observed=arg)
        elif event == "line":
            for site in self.sites(frame).get(frame.f_lineno, ()):
                self.emit("source_path", frame, site=site,
                          bindings={k: v for k, v in frame.f_locals.items()
                                    if k in ("version", "payload", "expected", "count", "task", "field", "kind", "rows")})
        return self.trace

    def normalize(self):
        # Discover generated values in first-observation order, not in sorted-key
        # order. An alias is reused everywhere, including later commands and lists.
        ids, dates, folders = {}, {}, {}
        relative_dates = {}
        for event in self.raw:
            if (event["kind"] == "helper_enter" and event.get("caller") ==
                    "benchmark/harness/cases/B12.py:61" and event["helper"] in ("call", "_call")):
                command = event["arguments"].get("args", ())
                if (command[:1] == ("create",) and "--due-date" in command and
                        "--title" in command and command[command.index("--title") + 1] == "later"):
                    relative_dates[command[command.index("--due-date") + 1]] = "<B12:now+2days>"
            if event["kind"] == "cli":
                folder = str(event["cwd"])
                folders.setdefault(folder, f"<cwd:{len(folders) + 1}>")
            def discover(value, generated=False):
                if isinstance(value, dict):
                    for key, item in value.items():
                        if generated and key == "created_at" and isinstance(item, str) and ISO.fullmatch(item):
                            dates.setdefault(item, f"<created_at:{len(dates) + 1}>")
                        if generated and key == "id" and isinstance(item, str) and UUID.fullmatch(item):
                            ids.setdefault(item, f"<id:{len(ids) + 1}>")
                        discover(item, generated)
                elif isinstance(value, (list, tuple)):
                    for item in value:
                        discover(item, generated)
            if event["kind"] == "cli" and event["command"][:1] == ["create"] and event["returncode"] == 0:
                discover(event["observed"], True)

        def convert(value):
            if isinstance(value, (bytes, bytearray)):
                try:
                    return {"storage_json": convert(json.loads(value))}
                except (ValueError, UnicodeError):
                    return {"bytes_sha256": w.digest(bytes(value))}
            if isinstance(value, (Path, os.PathLike)):
                return convert(str(value))
            if isinstance(value, str):
                if self.workspace is not None:
                    value = value.replace(str(self.workspace), "<restore>")
                for folder, token in sorted(folders.items(), key=lambda pair: -len(pair[0])):
                    value = value.replace(folder, token)
                for date, token in dates.items():
                    value = value.replace(date, token)
                for date, token in relative_dates.items():
                    value = value.replace(date, token)
                return UUID.sub(lambda match: ids.get(match.group(), match.group()), value)
            if isinstance(value, dict):
                return {convert(str(k)): convert(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [convert(v) for v in value]
            if isinstance(value, (set, frozenset)):
                return sorted((convert(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
            if isinstance(value, (bool, int, float)) or value is None:
                return value
            if isinstance(value, datetime.datetime):
                return convert(value.isoformat())
            if isinstance(value, subprocess.CompletedProcess):
                return {"returncode": value.returncode, "stdout": convert(value.stdout),
                        "stderr": convert(value.stderr)}
            # Only incidental Python identity/type representation is discarded.
            if isinstance(value, type):
                return f"<type:{value.__module__}.{value.__qualname__}>"
            return f"<runtime:{type(value).__module__}.{type(value).__qualname__}>"

        return convert(self.raw)


@contextmanager
def observe(recorder):
    old_run = unittest.TestCase.run
    old_subprocess = subprocess.run
    originals = {name: getattr(unittest.TestCase, name) for name in dir(unittest.TestCase)
                 if name.startswith("assert") and callable(getattr(unittest.TestCase, name))}

    def run(test, result=None):
        previous = recorder.method
        recorder.method = test.id()
        try:
            return old_run(test, result)
        finally:
            recorder.method = previous

    def cli(*args, **kwargs):
        caller = inspect.currentframe().f_back
        if recorder.method is None or source(caller) is None:
            return old_subprocess(*args, **kwargs)
        result = old_subprocess(*args, **kwargs)
        command = args[0] if args else kwargs.get("args")
        try:
            output = json.loads(result.stdout) if result.stdout else None
        except (ValueError, TypeError):
            output = result.stdout
        try:
            error = json.loads(result.stderr) if result.stderr else None
        except (ValueError, TypeError):
            error = result.stderr
        recorder.emit("cli", caller, command=list(command[2:]), cwd=kwargs.get("cwd"),
                      returncode=result.returncode, observed=output, error=error)
        return result

    def asserted(name, original_method):
        def wrapper(test, *args, **kwargs):
            caller = inspect.currentframe().f_back
            try:
                return original_method(test, *args, **kwargs)
            finally:
                if recorder.method is not None and source(caller) is not None:
                    recorder.emit("assertion", caller, assertion=name, arguments=args,
                                  keywords=kwargs, passed=sys.exc_info()[0] is None)
        return wrapper

    with patch.object(unittest.TestCase, "run", run), patch.object(subprocess, "run", cli):
        with contextmanager_patches(originals, asserted):
            previous = sys.gettrace()
            sys.settrace(recorder.trace)
            try:
                yield
            finally:
                sys.settrace(previous)


@contextmanager
def contextmanager_patches(originals, factory):
    from contextlib import ExitStack
    with ExitStack() as stack:
        for name, method in originals.items():
            stack.enter_context(patch.object(unittest.TestCase, name, factory(name, method)))
        yield


def execute(label):
    w.require(label in restores.SNAPSHOTS and restores.TEMP.is_dir(), "unknown checkpoint")
    w.require(w.file_hash(Path(runner.r4.__file__)) == runner.R4_SHA256 and
              w.file_hash(runner.r4.REPAIR_CASE) == runner.r4.REPAIR_CASE_SHA256 and
              w.file_hash(runner.CASE) == runner.CASE_SHA256,
              "frozen runner carrier drift")
    for request, expected_hash in runner.r4.FROZEN.items():
        w.require(w.file_hash(w.CASES / f"{request}.py") == expected_hash,
                  f"frozen case drift: {request}")
    checkpoint_hash, snapshot_hash = restores.SNAPSHOTS[label]
    checkpoint = inventory.RESULTS / f"checkpoint-{label}-B16-r5_2.json"
    snapshot = inventory.RESULTS / f"snapshot-{label}-B16-r5_2.tar"
    w.require(w.file_hash(checkpoint) == checkpoint_hash and w.file_hash(snapshot) == snapshot_hash,
              "frozen checkpoint drift")
    record = json.loads(checkpoint.read_text(encoding="utf-8"))
    checkpoints.validate_record(record)
    track = record["track"]
    w.require(track == ("axiom" if label == "lykoi" else "conventional"), "checkpoint identity")
    with tempfile.TemporaryDirectory(prefix="r5-3-trace-", dir=restores.TEMP) as folder:
        workspace = Path(folder) / "restore"
        w.restore(track, workspace, record, snapshot, snapshot_hash)
        app = workspace / ("generated/task_manager.py" if track == "axiom" else
                           "benchmark/conventional/task_manager.py")
        profile = profiles.identity(record["achieved"])
        w.require(profile["expectation_sha256"] == record["expectation_sha256"], "profile drift")
        with inventory.isolated_construction():
            replacements = runner.load_module("regression_B16_R5", runner.CASE)
            original_methods = {name: getattr(original.Regression, name) for name in
                                dir(original.Regression) if name.startswith("test_")}
            try:
                suite, active, dispositions, _ = frozen.build_suite(
                    app, profile["expectation"], record["achieved"], replacements,
                    mark_skips=False)
                runner.prior.mark_superseded(suite, active)
                recorder = Recorder(workspace)
                import io
                with observe(recorder):
                    stream = io.StringIO()
                    result = unittest.TextTestRunner(stream=stream, verbosity=0,
                                                     resultclass=original.CountedResult).run(suite)
            finally:
                for name, method in original_methods.items():
                    setattr(original.Regression, name, method)
            expected = (35, 28) if "B16" in record["achieved"] else (7, 2)
            w.require(result.wasSuccessful() and (result.successes, len(result.skipped)) == expected,
                      f"external suite failed: {stream.getvalue()}")
        w.require(w.workspace_files(workspace) == record["files"], "trace altered restored files")
        events = recorder.normalize()
        return {"achieved": record["achieved"], "checkpoint_sha256": checkpoint_hash,
                "events_sha256": w.digest(w.encoded(events)), "events": events,
                "passed": result.successes, "skipped": len(result.skipped),
                "dispositions": {key: val["state"] for key, val in sorted(dispositions.items())}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", choices=restores.SNAPSHOTS, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = execute(args.checkpoint)
    if args.output:
        w.require(args.output.parent.is_dir(), "output parent missing")
        args.output.write_bytes(w.encoded(result))
    print(json.dumps({"achieved": result["achieved"], "events": len(result["events"]),
                      "events_sha256": result["events_sha256"], "passed": result["passed"],
                      "skipped": result["skipped"]}, sort_keys=True))


if __name__ == "__main__":
    main()
