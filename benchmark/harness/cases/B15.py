"""B15: completion requires every dependency completed, including archived ones."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class CompletionDependencies(unittest.TestCase):
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

        def test_pending_dependencies_reject_without_writes_then_succeed(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                root = self.call(cwd, "create", "--title", "root", "--description", "x")
                first = self.call(cwd, "create", "--title", "first", "--description", "x")
                second = self.call(cwd, "create", "--title", "second", "--description", "x")
                root = self.call(cwd, "add-dependency", "--id", root["id"],
                                 "--depends-on", first["id"])
                root = self.call(cwd, "add-dependency", "--id", root["id"],
                                 "--depends-on", second["id"])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "complete", "--id", root["id"], error="incomplete_dependencies")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.call(cwd, "complete", "--id", first["id"])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "complete", "--id", root["id"], error="incomplete_dependencies")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.call(cwd, "complete", "--id", second["id"])
                archived = self.call(cwd, "archive", "--id", second["id"])
                self.assertEqual(archived["status"], "completed")
                finished = self.call(cwd, "complete", "--id", root["id"])
                self.assertEqual(finished["status"], "completed")
                self.assertEqual(finished["dependencies"], [first["id"], second["id"]])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "complete", "--id", root["id"], error="invalid_transition")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

        def test_archived_parent_still_obeys_terminal_transition(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                prerequisite = self.call(cwd, "create", "--title", "prerequisite", "--description", "x")
                parent = self.call(cwd, "create", "--title", "parent", "--description", "x")
                self.call(cwd, "add-dependency", "--id", parent["id"],
                          "--depends-on", prerequisite["id"])
                self.call(cwd, "archive", "--id", parent["id"])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "complete", "--id", parent["id"], error="invalid_transition")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(CompletionDependencies)
