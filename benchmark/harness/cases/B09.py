"""B09 external CLI acceptance for the inclusive due-date window."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class DueWindow(unittest.TestCase):
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

        def test_inclusive_window_pending_nonarchived_and_normal_order(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                start = "2020-01-01T00:00:00Z"
                middle = "2020-01-02T00:00:00Z"
                end = "2020-01-03T00:00:00Z"
                first = self.call(cwd, "create", "--title", "start", "--description", "x",
                                  "--priority", "HIGH", "--due-date", start)
                self.call(cwd, "create", "--title", "undated", "--description", "x")
                mid = self.call(cwd, "create", "--title", "middle", "--description", "x",
                                "--priority", "CRITICAL", "--due-date", middle)
                last = self.call(cwd, "create", "--title", "end", "--description", "x",
                                 "--due-date", end)
                done = self.call(cwd, "create", "--title", "done", "--description", "x",
                                 "--due-date", middle)
                hidden = self.call(cwd, "create", "--title", "hidden", "--description", "x",
                                   "--due-date", middle)
                self.call(cwd, "complete", "--id", done["id"])
                self.call(cwd, "archive", "--id", hidden["id"])
                ordered = self.call(cwd, "list")
                before = (cwd / "tasks.json").read_bytes()
                expected = [t for t in ordered if t["id"] in (first["id"], mid["id"], last["id"])]
                self.assertEqual(self.call(cwd, "list-due", "--start", start, "--end", end), expected)
                self.assertEqual(self.call(cwd, "list-due", "--start", middle, "--end", middle),
                                 [mid])
                self.assertEqual(self.call(cwd, "list-due", "--start", end, "--end", end),
                                 [last])
                self.assertEqual(self.call(cwd, "list-due", "--start", "2019-01-01T00:00:00Z",
                                           "--end", "2019-12-31T00:00:00Z"), [])
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

        def test_invalid_ranges_and_timestamps_do_not_write(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                good = "2020-01-01T00:00:00Z"
                later = "2020-01-02T00:00:00Z"
                self.call(cwd, "list-due", "--start", later, "--end", good,
                          error="invalid_window")
                for bad in ("yesterday", "2020-01-01T00:00:00+00:00",
                            "2020-01-01T01:00:00+01:00"):
                    self.call(cwd, "list-due", "--start", bad, "--end", later,
                              error="invalid_due_date")
                    self.call(cwd, "list-due", "--start", good, "--end", bad,
                              error="invalid_due_date")
                self.assertFalse((cwd / "tasks.json").exists())
                self.call(cwd, "create", "--title", "one", "--description", "x")
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "list-due", "--start", later, "--end", good,
                          error="invalid_window")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(DueWindow)
