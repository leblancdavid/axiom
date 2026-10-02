"""B05 external status-filter behavior on isolated CLI storage."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class StatusListing(unittest.TestCase):
        def call(self, cwd, *args):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result)
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_both_statuses_and_no_write(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.assertEqual(self.call(cwd, "list-status", "--status", "pending"), [])
                self.assertEqual(self.call(cwd, "list-status", "--status", "completed"), [])
                self.assertFalse((cwd / "tasks.json").exists())
                first = self.call(cwd, "create", "--title", "first", "--description", "x")
                second = self.call(cwd, "create", "--title", "second", "--description", "x")
                third = self.call(cwd, "create", "--title", "third", "--description", "x")
                done = self.call(cwd, "complete", "--id", second["id"])
                normal = self.call(cwd, "list")
                before = (cwd / "tasks.json").read_bytes()
                self.assertEqual(self.call(cwd, "list-status", "--status", "pending"),
                                 [task for task in normal if task["status"] == "pending"])
                self.assertEqual(self.call(cwd, "list-status", "--status", "completed"), [done])
                self.assertEqual({task["id"] for task in normal}, {first["id"], second["id"], third["id"]})
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.call(cwd, "complete", "--id", first["id"])
                self.call(cwd, "complete", "--id", third["id"])
                before = (cwd / "tasks.json").read_bytes()
                self.assertEqual(self.call(cwd, "list-status", "--status", "pending"), [])
                self.assertEqual(self.call(cwd, "list-status", "--status", "completed"), self.call(cwd, "list"))
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(StatusListing)
