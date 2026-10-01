"""External CLI oracle: no imports from either task application."""

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
TRACKS = {
    "conventional": ROOT / "benchmark" / "conventional" / "task_manager.py",
    "axiom": ROOT / "generated" / "task_manager.py",
}
FIELDS = {"id", "title", "description", "status", "priority", "created_at", "due_date"}


def invoke(app, cwd, *args):
    result = subprocess.run([sys.executable, str(app), *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode not in (0, 1):
        raise AssertionError(f"{app}: unexpected exit {result.returncode}: {result.stderr}")
    if result.returncode == 0:
        if result.stderr:
            raise AssertionError(f"unexpected stderr: {result.stderr}")
        return json.loads(result.stdout), None
    if result.stdout:
        raise AssertionError(f"unexpected stdout: {result.stdout}")
    return None, json.loads(result.stderr)["error"]


def stamp(value):
    assert isinstance(value, str) and value.endswith("Z"), value
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.utcoffset().total_seconds() == 0


class BaselineOracle(unittest.TestCase):
    def test_lifecycle_filters_and_failures(self):
        traces = {}
        for name, app in TRACKS.items():
            with self.subTest(track=name), tempfile.TemporaryDirectory() as directory:
                cwd = Path(directory)
                def call(*args, error=None):
                    value, failure = invoke(app, cwd, *args)
                    self.assertEqual(failure, error)
                    return value

                self.assertEqual(call("list"), [])
                self.assertFalse((cwd / "tasks.json").exists())
                self.assertIsNone(call("create", "--title", "  ", "--description", "x", error="invalid_title"))
                self.assertFalse((cwd / "tasks.json").exists())
                normal = call("create", "--title", "normal", "--description", "details")
                high = call("create", "--title", "high", "--description", "x", "--priority", "HIGH",
                            "--due-date", "2020-01-01T00:00:00Z")
                low = call("create", "--title", "low", "--description", "x", "--priority", "LOW",
                           "--due-date", "2999-01-01T00:00:00Z")
                ids = {r["id"] for r in (normal, high, low)}
                self.assertEqual(len(ids), 3)
                for task in (normal, high, low):
                    self.assertEqual(set(task), FIELDS)
                    self.assertEqual(task["status"], "pending")
                    stamp(task["created_at"])
                self.assertEqual(normal["priority"], "NORMAL")
                self.assertIsNone(normal["due_date"])
                self.assertEqual([r["id"] for r in call("list")],
                                 [r["id"] for r in sorted((normal, high, low), key=lambda r: (r["created_at"], r["id"]))])
                self.assertEqual(call("list-high"), [high])
                self.assertEqual(call("list-overdue"), [high])
                before = (cwd / "tasks.json").read_bytes()
                call("create", "--title", "bad", "--description", "x", "--due-date", "yesterday",
                     error="invalid_due_date")
                call("complete", "--id", "missing", error="task_not_found")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                done = call("complete", "--id", high["id"])
                self.assertEqual(done, {**high, "status": "completed"})
                self.assertEqual(call("list-overdue"), [])
                before = (cwd / "tasks.json").read_bytes()
                call("complete", "--id", high["id"], error="invalid_transition")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(call("delete", "--id", high["id"]), done)
                call("delete", "--id", high["id"], error="task_not_found")
                self.assertEqual({r["id"] for r in call("list")}, {normal["id"], low["id"]})
                traces[name] = (normal["priority"], high["priority"], low["priority"],
                                len(call("list")), len(call("list-high")), len(call("list-overdue")))
        self.assertEqual(traces["conventional"], traces["axiom"])

    def test_migration_and_corruption(self):
        for name, app in TRACKS.items():
            with self.subTest(track=name), tempfile.TemporaryDirectory() as directory:
                cwd = Path(directory)
                path = cwd / "tasks.json"
                old = {"id": "legacy", "title": "Old", "description": "x", "status": "pending",
                       "created_at": "2026-01-01T00:00:00Z"}
                path.write_text(json.dumps([old]), encoding="utf-8")
                unchanged = path.read_bytes()
                self.assertEqual(invoke(app, cwd, "list"), (None, "migration_required"))
                self.assertEqual(path.read_bytes(), unchanged)
                self.assertEqual(invoke(app, cwd, "migrate"), ({"migrated": 1}, None))
                self.assertEqual(invoke(app, cwd, "list"), ([{**old, "priority": "NORMAL", "due_date": None}], None))
                self.assertEqual(invoke(app, cwd, "migrate"), ({"migrated": 0}, None))
                version_two = {**old, "priority": "HIGH"}
                path.write_text(json.dumps({"schema_version": 2, "records": [version_two]}), encoding="utf-8")
                self.assertEqual(invoke(app, cwd, "list"), (None, "migration_required"))
                self.assertEqual(invoke(app, cwd, "migrate"), ({"migrated": 1}, None))
                self.assertEqual(invoke(app, cwd, "list"), ([{**version_two, "due_date": None}], None))
                record = {**version_two, "due_date": None}
                for rows in ([record, record], [{**record, "id": ""}]):
                    path.write_text(json.dumps({"schema_version": 3, "records": rows}), encoding="utf-8")
                    self.assertEqual(invoke(app, cwd, "list"), (None, "invalid_state"))
                path.write_text("{broken", encoding="utf-8")
                self.assertEqual(invoke(app, cwd, "list"), (None, "invalid_state"))

    def test_overdue_boundary_fixture(self):
        # No implementation hooks or clock injection: the fixed instants straddle
        # any normal benchmark run, while equal-time semantics are specified below.
        for name, app in TRACKS.items():
            with self.subTest(track=name), tempfile.TemporaryDirectory() as directory:
                cwd = Path(directory)
                def row(identifier, due, status="pending"):
                    return {"id": identifier, "title": identifier, "description": "x", "status": status,
                            "priority": "NORMAL", "created_at": "2026-01-01T00:00:00Z", "due_date": due}
                rows = [row("past", "2020-01-01T00:00:00Z"), row("future", "2999-01-01T00:00:00Z"),
                        row("none", None), row("done", "2020-01-01T00:00:00Z", "completed")]
                (cwd / "tasks.json").write_text(json.dumps({"schema_version": 3, "records": rows}), encoding="utf-8")
                self.assertEqual(invoke(app, cwd, "list-overdue"), ([rows[0]], None))


if __name__ == "__main__":
    unittest.main()
