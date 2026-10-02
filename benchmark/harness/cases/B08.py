"""B08 public CLI acceptance for archival and visibility."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Archival(unittest.TestCase):
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

        def test_archive_pending_completed_and_visibility(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                pending = self.call(cwd, "create", "--title", "pending", "--description", "x",
                                    "--priority", "HIGH", "--due-date", "2020-01-01T00:00:00Z")
                completed = self.call(cwd, "create", "--title", "completed", "--description", "x",
                                      "--priority", "HIGH")
                visible = self.call(cwd, "create", "--title", "visible", "--description", "x")
                self.assertEqual([t["archived"] for t in (pending, completed, visible)],
                                 [False, False, False])
                completed = self.call(cwd, "complete", "--id", completed["id"])
                normal = self.call(cwd, "list")
                pending_archive = self.call(cwd, "archive", "--id", pending["id"])
                completed_archive = self.call(cwd, "archive", "--id", completed["id"])
                self.assertEqual(pending_archive, {**pending, "archived": True})
                self.assertEqual(completed_archive, {**completed, "archived": True})
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "archive", "--id", pending["id"], error="invalid_transition")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "list"), [visible])
                self.assertEqual(self.call(cwd, "list-high"), [])
                self.assertEqual(self.call(cwd, "list-overdue"), [])
                self.assertEqual(self.call(cwd, "list-archived"),
                                 [{**task, "archived": True} for task in normal
                                  if task["id"] in (pending["id"], completed["id"])])
                if "B03" in achieved:
                    self.assertEqual(self.call(cwd, "list-tag", "--tag", "unused"), [])
                if "B05" in achieved:
                    self.assertEqual(self.call(cwd, "list-status", "--status", "pending"), [visible])
                    self.assertEqual(self.call(cwd, "list-status", "--status", "completed"), [])
                if "B06" in achieved:
                    self.assertEqual(self.call(cwd, "list-category", "--category", ""), [visible])
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

        def test_explicit_migration_defaults_unarchived(self):
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
                self.assertIs(migrated["archived"], False)
                self.assertEqual(self.call(cwd, "list"), [migrated])
                self.assertEqual(self.call(cwd, "list-archived"), [])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])

    return unittest.defaultTestLoader.loadTestsFromTestCase(Archival)
