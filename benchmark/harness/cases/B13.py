"""B13: archival is terminal for completion and note append, not deletion."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class ArchivedMutations(unittest.TestCase):
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

        def test_archived_pending_and_completed_mutations_are_rejected(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                pending = self.call(cwd, "create", "--title", "pending", "--description", "x")
                completed = self.call(cwd, "create", "--title", "completed", "--description", "x")
                completed = self.call(cwd, "complete", "--id", completed["id"])
                pending = self.call(cwd, "archive", "--id", pending["id"])
                completed = self.call(cwd, "archive", "--id", completed["id"])
                before = (cwd / "tasks.json").read_bytes()
                for task in (pending, completed):
                    self.call(cwd, "complete", "--id", task["id"], error="invalid_transition")
                    self.call(cwd, "append-note", "--id", task["id"], "--text", "new",
                              error="invalid_transition")
                    self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "list-archived"),
                                 sorted((pending, completed), key=lambda t: (t["created_at"], t["id"])))
                self.assertEqual(self.call(cwd, "delete", "--id", pending["id"]), pending)
                self.assertEqual(self.call(cwd, "delete", "--id", completed["id"]), completed)
                self.assertEqual(self.call(cwd, "list-archived"), [])

        def test_unarchived_operations_remain_valid(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                task = self.call(cwd, "create", "--title", "active", "--description", "x")
                task = self.call(cwd, "append-note", "--id", task["id"], "--text", "  note  ")
                self.assertEqual(task["notes"], ["note"])
                completed = self.call(cwd, "complete", "--id", task["id"])
                self.assertEqual(completed["status"], "completed")
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "delete", "--id", task["id"], error="delete_requires_archive")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(ArchivedMutations)
