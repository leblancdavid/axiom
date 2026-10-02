"""B07 public CLI acceptance for ordered, appendable task notes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Notes(unittest.TestCase):
        def call(self, cwd, *args, error=None):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1 if error else 0, result)
            if error:
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr), {"error": error})
                return None
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_append_order_trim_and_failed_append(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                first = self.call(cwd, "create", "--title", "first", "--description", "x")
                second = self.call(cwd, "create", "--title", "second", "--description", "x")
                self.assertEqual(first["notes"], [])
                self.assertEqual(second["notes"], [])
                first = self.call(cwd, "append-note", "--id", first["id"], "--text", "  first note  ")
                self.assertEqual(first["notes"], ["first note"])
                first = self.call(cwd, "append-note", "--id", first["id"], "--text", "second\t")
                self.assertEqual(first["notes"], ["first note", "second"])
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == first["id"]), first)
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "append-note", "--id", first["id"], "--text", " \t ",
                          error="invalid_note")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == first["id"]), first)
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == second["id"])["notes"], [])
                completed = self.call(cwd, "complete", "--id", first["id"])
                self.assertEqual(completed["notes"], ["first note", "second"])
                self.assertEqual(self.call(cwd, "delete", "--id", first["id"])["notes"],
                                 ["first note", "second"])

        def test_explicit_migration_initializes_notes(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                old = {"id": "old", "title": "old", "description": "x", "status": "pending",
                       "priority": "NORMAL", "created_at": "2026-01-01T00:00:00Z", "due_date": None}
                path = cwd / "tasks.json"
                path.write_text(json.dumps({"schema_version": 3, "records": [old]}), encoding="utf-8")
                before = path.read_bytes()
                self.call(cwd, "list", error="migration_required")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                migrated = {**old, **profile["migration_defaults"]}
                self.assertEqual(migrated["notes"], [])
                self.assertEqual(self.call(cwd, "list"), [migrated])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])
                appended = self.call(cwd, "append-note", "--id", "old", "--text", "  migrated  ")
                self.assertEqual(appended, {**migrated, "notes": ["migrated"]})

    return unittest.defaultTestLoader.loadTestsFromTestCase(Notes)
