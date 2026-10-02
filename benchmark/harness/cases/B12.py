"""B12: urgent overdue selection, strict UTC boundary, and no-write reads."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Urgent(unittest.TestCase):
        def call(self, cwd, *args):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result)
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_urgent_overdue_exclusions_order_and_prior_overdue(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                past = "2020-01-01T00:00:00Z"
                future = "2999-01-01T00:00:00Z"

                def create(title, priority="NORMAL", due=None):
                    args = ["create", "--title", title, "--description", "x",
                            "--priority", priority]
                    if due:
                        args.extend(("--due-date", due))
                    return self.call(cwd, *args)

                high = create("high", "HIGH", past)
                low = create("low", "LOW", past)
                critical = create("critical", "CRITICAL", past)
                normal = create("normal", "NORMAL", past)
                no_date = create("no date", "CRITICAL")
                not_yet = create("future", "HIGH", future)
                done = create("completed", "CRITICAL", past)
                hidden = create("archived", "HIGH", past)
                self.call(cwd, "complete", "--id", done["id"])
                self.call(cwd, "archive", "--id", hidden["id"])
                expected = [task for task in self.call(cwd, "list")
                            if task["id"] in (high["id"], critical["id"])]
                before = (cwd / "tasks.json").read_bytes()
                self.assertEqual(self.call(cwd, "list-urgent"), expected)
                overdue = self.call(cwd, "list-overdue")
                self.assertEqual({task["id"] for task in overdue},
                                 {high["id"], low["id"], critical["id"], normal["id"]})
                self.assertNotIn(no_date, overdue)
                self.assertNotIn(not_yet, overdue)
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

        def test_strict_current_time_and_empty_query_never_write(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.assertEqual(self.call(cwd, "list-urgent"), [])
                self.assertFalse((cwd / "tasks.json").exists())
                near_future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat().replace("+00:00", "Z")
                future = self.call(cwd, "create", "--title", "later", "--description", "x",
                                   "--priority", "CRITICAL", "--due-date", near_future)
                before = (cwd / "tasks.json").read_bytes()
                self.assertEqual(self.call(cwd, "list-urgent"), [])
                self.assertEqual(self.call(cwd, "list-overdue"), [])
                self.assertEqual(self.call(cwd, "list"), [future])
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)

    return unittest.defaultTestLoader.loadTestsFromTestCase(Urgent)
