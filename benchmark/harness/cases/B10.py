"""B10 public CLI acceptance for an optional task owner."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Owner(unittest.TestCase):
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

        def test_trim_reject_and_exact_owner_listing(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                for bad in ("", " \t "):
                    self.call(cwd, "create", "--title", "bad", "--description", "x",
                              "--owner", bad, error="invalid_owner")
                self.assertFalse((cwd / "tasks.json").exists())
                first = self.call(cwd, "create", "--title", "first", "--description", "x",
                                  "--owner", "  Alex  ")
                second = self.call(cwd, "create", "--title", "second", "--description", "x",
                                   "--owner", "Alex")
                other = self.call(cwd, "create", "--title", "other", "--description", "x",
                                  "--owner", "alex")
                unowned = self.call(cwd, "create", "--title", "unowned", "--description", "x")
                self.assertEqual([t["owner"] for t in (first, second, other, unowned)],
                                 ["Alex", "Alex", "alex", ""])
                completed = self.call(cwd, "complete", "--id", first["id"])
                self.assertEqual(completed["owner"], "Alex")
                normal = self.call(cwd, "list")
                before = (cwd / "tasks.json").read_bytes()
                for owner in ("Alex", "alex", "", " Alex ", "missing"):
                    self.assertEqual(self.call(cwd, "list-owner", "--owner", owner),
                                     [task for task in normal if task["owner"] == owner])
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "delete", "--id", second["id"])["owner"], "Alex")

        def test_migration_defaults_unowned(self):
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
                self.assertEqual(migrated["owner"], "")
                self.assertEqual(self.call(cwd, "list"), [migrated])
                self.assertEqual(self.call(cwd, "list-owner", "--owner", ""), [migrated])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])

    return unittest.defaultTestLoader.loadTestsFromTestCase(Owner)
