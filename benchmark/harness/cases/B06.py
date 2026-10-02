"""B06 public CLI category creation, filtering and migration."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Categories(unittest.TestCase):
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

        def test_create_filter_and_failed_create(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.call(cwd, "create", "--title", "bad", "--description", "x",
                          "--category", " \t ", error="invalid_category")
                self.assertFalse((cwd / "tasks.json").exists())
                a = self.call(cwd, "create", "--title", "a", "--description", "x",
                              "--category", "  Work  ")
                b = self.call(cwd, "create", "--title", "b", "--description", "x",
                              "--category", "Work")
                other = self.call(cwd, "create", "--title", "other", "--description", "x",
                                  "--category", "work")
                omitted = self.call(cwd, "create", "--title", "omitted", "--description", "x")
                explicit = self.call(cwd, "create", "--title", "explicit", "--description", "x",
                                     "--category", "")
                self.assertEqual([t["category"] for t in (a, b, other, omitted, explicit)],
                                 ["Work", "Work", "work", "", ""])
                completed = self.call(cwd, "complete", "--id", a["id"])
                self.assertEqual(completed["category"], "Work")
                normal = self.call(cwd, "list")
                before = (cwd / "tasks.json").read_bytes()
                for value in ("Work", "work", "", " Work ", "absent"):
                    self.assertEqual(self.call(cwd, "list-category", "--category", value),
                                     [task for task in normal if task["category"] == value])
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "delete", "--id", b["id"])["category"], "Work")

        def test_migration_defaults_category(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                prior = {"id": "old", "title": "old", "description": "x", "status": "pending",
                         "priority": "NORMAL", "created_at": "2026-01-01T00:00:00Z", "due_date": None}
                path = cwd / "tasks.json"
                path.write_text(json.dumps({"schema_version": 3, "records": [prior]}), encoding="utf-8")
                before = path.read_bytes()
                self.call(cwd, "list", error="migration_required")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                self.assertEqual(self.call(cwd, "list"), [{**prior, **profile["migration_defaults"]}])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])

    return unittest.defaultTestLoader.loadTestsFromTestCase(Categories)
