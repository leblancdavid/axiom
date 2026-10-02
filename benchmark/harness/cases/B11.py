"""B11 deletion rule plus replacement lifecycle and B01 priority coverage."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class DeletionRule(unittest.TestCase):
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

        def test_lifecycle_priority_and_completed_delete_rule(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.assertEqual(self.call(cwd, "list"), [])
                self.assertFalse((cwd / "tasks.json").exists())
                self.call(cwd, "create", "--title", "  ", "--description", "x",
                          error="invalid_title")
                self.assertFalse((cwd / "tasks.json").exists())
                normal = self.call(cwd, "create", "--title", "normal", "--description", "x")
                high = self.call(cwd, "create", "--title", "high", "--description", "x",
                                 "--priority", "HIGH", "--due-date", "2020-01-01T00:00:00Z")
                critical = self.call(cwd, "create", "--title", "critical", "--description", "x",
                                     "--priority", "CRITICAL")
                low = self.call(cwd, "create", "--title", "low", "--description", "x",
                                "--priority", "LOW", "--due-date", "2999-01-01T00:00:00Z")
                self.assertEqual([normal["priority"], high["priority"], critical["priority"], low["priority"]],
                                 ["NORMAL", "HIGH", "CRITICAL", "LOW"])
                self.assertEqual(self.call(cwd, "list"),
                                 sorted((normal, high, critical, low),
                                        key=lambda r: (r["created_at"], r["id"])))
                self.assertEqual(self.call(cwd, "list-high"), [high])
                self.assertEqual(self.call(cwd, "list-overdue"), [high])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "create", "--title", "bad", "--description", "x",
                          "--due-date", "yesterday", error="invalid_due_date")
                self.call(cwd, "complete", "--id", "missing", error="task_not_found")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                completed_high = self.call(cwd, "complete", "--id", high["id"])
                completed_critical = self.call(cwd, "complete", "--id", critical["id"])
                self.assertEqual(completed_high, {**high, "status": "completed"})
                self.assertEqual(completed_critical, {**critical, "status": "completed"})
                self.assertEqual(self.call(cwd, "list-overdue"), [])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "complete", "--id", high["id"], error="invalid_transition")
                self.call(cwd, "delete", "--id", high["id"], error="delete_requires_archive")
                self.call(cwd, "delete", "--id", critical["id"], error="delete_requires_archive")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertIn(completed_high, self.call(cwd, "list"))
                archived_high = self.call(cwd, "archive", "--id", high["id"])
                archived_critical = self.call(cwd, "archive", "--id", critical["id"])
                self.assertEqual(archived_high, {**completed_high, "archived": True})
                self.assertEqual(archived_critical, {**completed_critical, "archived": True})
                self.assertEqual(self.call(cwd, "delete", "--id", high["id"]), archived_high)
                self.assertEqual(self.call(cwd, "delete", "--id", critical["id"]), archived_critical)
                self.call(cwd, "delete", "--id", high["id"], error="task_not_found")
                self.assertEqual(self.call(cwd, "list-high"), [])
                self.assertEqual(self.call(cwd, "list-overdue"), [])
                self.assertEqual({t["id"] for t in self.call(cwd, "list")},
                                 {normal["id"], low["id"]})

        def test_pending_deletion_with_and_without_archive(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                ordinary = self.call(cwd, "create", "--title", "ordinary", "--description", "x")
                archived = self.call(cwd, "create", "--title", "archived", "--description", "x")
                self.assertEqual(self.call(cwd, "delete", "--id", ordinary["id"]), ordinary)
                archived = self.call(cwd, "archive", "--id", archived["id"])
                self.assertEqual(archived["status"], "pending")
                self.assertEqual(self.call(cwd, "delete", "--id", archived["id"]), archived)
                self.assertEqual(self.call(cwd, "list"), [])
                self.assertEqual(self.call(cwd, "list-archived"), [])

    return unittest.defaultTestLoader.loadTestsFromTestCase(DeletionRule)
