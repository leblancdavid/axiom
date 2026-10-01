"""B03 external CLI acceptance: exact tag selection without storage mutation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class TagListing(unittest.TestCase):
        def call(self, cwd, *args, error=None):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            if error is not None:
                self.assertEqual(result.returncode, 1, result)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr), {"error": error})
                return None
            self.assertEqual(result.returncode, 0, result)
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_exact_case_sensitive_tag_with_completed_tasks(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                first = self.call(cwd, "create", "--title", "first", "--description", "x",
                                  "--tag", "work")
                other_case = self.call(cwd, "create", "--title", "other", "--description", "x",
                                       "--tag", "Work")
                untagged = self.call(cwd, "create", "--title", "untagged", "--description", "x")
                completed = self.call(cwd, "create", "--title", "completed", "--description", "x",
                                      "--tag", "work", "--tag", "home")
                completed = self.call(cwd, "complete", "--id", completed["id"])
                before = (cwd / "tasks.json").read_bytes()
                normal = self.call(cwd, "list")
                self.assertEqual(self.call(cwd, "list-tag", "--tag", "work"),
                                 [task for task in normal if task["id"] in {first["id"], completed["id"]}])
                self.assertEqual(self.call(cwd, "list-tag", "--tag", "Work"), [other_case])
                self.assertEqual(self.call(cwd, "list-tag", "--tag", " work "), [])
                self.assertEqual(self.call(cwd, "list-tag", "--tag", "absent"), [])
                self.assertNotIn(untagged, self.call(cwd, "list-tag", "--tag", "work"))
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

        def test_blank_queries_leave_storage_unchanged(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                for value in ("", "   "):
                    self.call(cwd, "list-tag", "--tag", value, error="invalid_tag")
                    self.assertFalse((cwd / "tasks.json").exists())
                self.call(cwd, "create", "--title", "task", "--description", "x", "--tag", "a")
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "list-tag", "--tag", " \t ", error="invalid_tag")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(TagListing)
