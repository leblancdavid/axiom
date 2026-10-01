import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "generated" / "task_manager.py"


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)

    def run_app(self, *args, error=None):
        result = subprocess.run([sys.executable, str(APP), *args], cwd=self.cwd, capture_output=True, text=True)
        if error is not None:
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stderr), {"error": error})
            return None
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_lifecycle_and_persistence(self):
        self.assertEqual(self.run_app("list"), [])
        task = self.run_app("create", "--title", "First", "--description", "Details")
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["description"], "Details")
        self.assertTrue(task["created_at"].endswith("Z"))
        self.assertEqual(self.run_app("list"), [task])
        completed = self.run_app("complete", "--id", task["id"])
        self.assertEqual(completed["status"], "completed")
        self.run_app("complete", "--id", task["id"], error="invalid_transition")
        self.assertEqual(self.run_app("delete", "--id", task["id"]), completed)
        self.assertEqual(self.run_app("list"), [])
        self.run_app("delete", "--id", task["id"], error="task_not_found")

    def test_failures_leave_state_intact(self):
        self.run_app("create", "--title", "  ", "--description", "x", error="invalid_title")
        self.assertFalse((self.cwd / "tasks.json").exists())
        task = self.run_app("create", "--title", "Valid", "--description", "x")
        before = (self.cwd / "tasks.json").read_bytes()
        self.run_app("complete", "--id", "missing", error="task_not_found")
        self.assertEqual((self.cwd / "tasks.json").read_bytes(), before)
        (self.cwd / "tasks.json").write_text("{broken", encoding="utf-8")
        self.run_app("list", error="invalid_state")
        self.run_app("complete", "--id", task["id"], error="invalid_state")

    def test_invariants_on_load(self):
        task = self.run_app("create", "--title", "Valid", "--description", "x")
        (self.cwd / "tasks.json").write_text(json.dumps([task, task]), encoding="utf-8")
        self.run_app("list", error="invalid_state")
        task["id"] = ""
        (self.cwd / "tasks.json").write_text(json.dumps([task]), encoding="utf-8")
        self.run_app("list", error="invalid_state")


if __name__ == "__main__":
    unittest.main()
