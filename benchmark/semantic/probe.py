"""Disposable black-box witness for the semantic-format prototype.

Runs only selected *example* scenarios. This is neither the frozen R5.2.2
runner nor a B17 acceptance composer; no benchmark workspace is modified.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone

from benchmark.semantic import format as semantic


SNAPSHOTS = {
    "conventional": ("snapshot-conventional-B16-r5_2.tar",
                     "383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e",
                     "benchmark/conventional/task_manager.py",
                     [f"B{i:02}" for i in range(1, 17)]),
    "lykoi": ("snapshot-lykoi-B16-r5_2.tar",
              "36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5",
              "generated/task_manager.py", ["B01", "B04"]),
}
RESULTS = Path(__file__).resolve().parents[1] / "results" / "phase5c"


def resolve(value, bindings):
    kind, operand = next(iter(value.items()))
    if kind == "literal":
        return operand
    if kind == "instant":
        return semantic.utc_instant(resolve(operand, bindings), "instant")
    if kind == "clock_ref":
        return bindings[operand]
    if kind == "offset":
        return resolve(operand["from"], bindings) + timedelta(seconds=operand["seconds"])
    if kind == "list":
        return [resolve(item, bindings) for item in operand]
    if kind == "sorted":
        rows = resolve(operand["items"], bindings)
        return sorted(rows, key=lambda row: tuple(row[field] for field in operand["by"]))
    parts = operand.split(".")
    result = bindings[parts[0]]
    for part in parts[1:]:
        result = result[int(part)] if isinstance(result, list) else result[part]
    return result


def run_variant(app, scenario, clock=None):
    # This disposable subprocess probe cannot override the application's clock.
    # A semantic clock and a CLI query must never be mistaken for one clock.
    semantic.require(not (any("clock" in step for step in scenario["steps"]) and
                          any("invoke" in step for step in scenario["steps"])),
                     "application clock adapter required for clock-dependent invocation")
    with tempfile.TemporaryDirectory() as folder:
        cwd = Path(folder)
        bindings = {}
        for index, step in enumerate(scenario["steps"]):
            kind, body = next(iter(step.items()))
            context = f"{scenario['semantic_id']}/{scenario['variant']} step {index + 1}"
            if kind == "seed":
                (cwd / body["path"]).write_text(json.dumps(body["value"]), encoding="utf-8")
            elif kind == "clock":
                semantic.require(clock is not None, f"{context}: controlled clock required")
                instant = clock()
                semantic.require(isinstance(instant, datetime) and
                                 instant.tzinfo is not None and
                                 instant.utcoffset() == timedelta(0),
                                 f"{context}: clock must return UTC instant")
                bindings[body["bind"]] = instant.astimezone(timezone.utc)
            elif kind == "snapshot":
                path = cwd / body["path"]
                bindings[body["bind"]] = path.read_bytes() if path.exists() else None
            elif kind == "invoke":
                args = [resolve(arg, bindings) for arg in body["args"]]
                args = [arg.isoformat().replace("+00:00", "Z")
                        if isinstance(arg, datetime) else arg for arg in args]
                semantic.require(all(isinstance(arg, str) for arg in args),
                                 f"{context}: non-string CLI argument")
                result = subprocess.run([sys.executable, str(app), body["command"], *args],
                                        cwd=cwd, capture_output=True, text=True,
                                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                if "error" in body:
                    semantic.require(result.returncode == 1 and result.stdout == "" and
                                     json.loads(result.stderr) == {"error": body["error"]},
                                     f"{context}: wrong error envelope: {result}")
                else:
                    semantic.require(result.returncode == 0 and result.stderr == "",
                                     f"{context}: wrong success envelope: {result}")
                    bindings[body["bind"]] = json.loads(result.stdout)
            else:
                if body["relation"] == "equals":
                    passed = resolve(body["actual"], bindings) == resolve(body["expected"], bindings)
                elif body["relation"] == "distinct":
                    values = [resolve(value, bindings) for value in body["values"]]
                    passed = all(a != b for i, a in enumerate(values) for b in values[i + 1:])
                else:
                    passed = ((resolve(body["actual"], bindings) <
                               resolve(body["expected"], bindings)) == body["result"])
                semantic.require(passed, f"{context}: failed {body['id']}")


def probe(document, track):
    """Run only the selected example scenarios against a pinned B16 snapshot."""
    name, sha256, member, achieved = SNAPSHOTS[track]
    path = RESULTS / name
    semantic.require(hashlib.sha256(path.read_bytes()).hexdigest() == sha256,
                     "B16 snapshot drift")
    plans = semantic.compile_plan(document, achieved)
    with tarfile.open(path) as archive, tempfile.TemporaryDirectory() as folder:
        source = archive.extractfile(member)
        semantic.require(source is not None, "missing snapshot application")
        app = Path(folder) / "app.py"
        app.write_bytes(source.read())
        for plan in plans:
            run_variant(app, plan)
    return [(plan["semantic_id"], plan["variant"]) for plan in plans]
