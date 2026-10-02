"""Additive R5.2.1 acceptance carriers for the B11 preservation audit.

Selection consumes composed R5.2 method dispositions, never a track label.
The original frozen sources remain the assertion roots; this module supplies
only observations missing from the B11 replacement body.
"""

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import capability_profile as capabilities
import regression_phase5c_r5_1 as parent
import workspace as w


VERSION = "PHASE5C-R5.2.1-ASSERTION-PRESERVATION/1"
PARENT = "PHASE5C-R5-STATE-RELATIVE/1"
AUDIT = "benchmark/results/phase5c/B11-R4-HISTORICAL-ASSERTION-PRESERVATION-AUDIT.md"
BASELINE = "regression.Regression.test_baseline_lifecycle_filters_failures"
PRIORITY = "regression.Regression.test_b01_priority_and_regression"
ORIGINS = {
    "baseline.ids": (BASELINE, "regression.py:99", "three-created-task IDs distinct"),
    "baseline.check_task": (BASELINE, "regression.py:100-101; regression.py:60-69", "each created task passes applicable check_task"),
    "baseline.pending": (BASELINE, "regression.py:100-102", "each created task initially pending"),
    "baseline.due_date": (BASELINE, "regression.py:104", "normal create defaults due_date to null"),
    "B01.high_after_critical": (PRIORITY, "regression.py:168-176", "pending HIGH remains in list-high after CRITICAL completes"),
}
CARRIERS = {
    BASELINE: "test_baseline_create_assertions_restored",
    PRIORITY: "test_b01_intermediate_high_restored",
}


def selection(dispositions):
    """Fail closed unless the original is live or superseded specifically by B11."""
    selected = []
    for origin, method in CARRIERS.items():
        w.require(origin in dispositions, f"missing frozen origin: {origin}")
        row = dispositions[origin]
        if row["state"] in ("active", "skipped"):
            continue
        # R5 replays this exact original body with the owner argument adapted;
        # its assertions are still present. B11 takes precedence when achieved.
        if row["state"] == "superseded" and row["replacement"] == "B16-R5":
            continue
        w.require(row["state"] == "superseded" and row["replacement"] == "B11" and
                  row["origin"] == ("baseline" if origin == BASELINE else "B01"),
                  f"unexpected disposition for preservation origin: {origin}")
        selected.append(method)
    return selected


def inventory(dispositions, profile):
    selected = selection(dispositions)
    result = {}
    for key, (origin, source, behavior) in ORIGINS.items():
        if CARRIERS[origin] not in selected:
            continue
        result[key] = {"original_carrier": origin, "original_source": source,
                       "requirement": behavior, "lost_at": "B11 supersession",
                       "restored_at": VERSION,
                       "chain": [origin, "B11:omitted", f"{__name__}.{CARRIERS[origin]}"],
                       "audit": AUDIT,
                       "field_types": profile["field_types"] if key == "baseline.check_task" else None}
    return dict(sorted(result.items()))


def cases(app, profile, achieved, dispositions):
    selected = selection(dispositions)
    app = Path(app).resolve()
    achieved = frozenset(achieved)

    class Preservation(unittest.TestCase):
        def call(self, cwd, *args):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result)
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def create(self, cwd, *args):
            # R5's owner adapter supplies exactly this existing owner when B16
            # is active; no owner is injected for an earlier schema.
            owner = (("--owner", "system") if profile["migration_defaults"].get("owner") == "system"
                     else ())
            return self.call(cwd, "create", *args, *owner)

        def check_created(self, task):
            # One profile-dependent expansion of the original check_task per
            # create result, not the mutable runner-global wrapper chain.
            self.assertEqual(set(task), set(profile["fields"]))
            self.assertIsInstance(task["id"], str)
            self.assertTrue(task["id"].strip())
            self.assertIsInstance(task["created_at"], str)
            self.assertTrue(task["created_at"].endswith("Z"))
            self.assertEqual(datetime.fromisoformat(task["created_at"].replace(
                "Z", "+00:00")).utcoffset().total_seconds(), 0)
            if "B02" in achieved:
                self.assertIsInstance(task["tags"], list)
            for field, kind in profile["field_types"].items():
                self.assertIs(type(task[field]), capabilities.TYPES[kind], field)

        def test_baseline_create_assertions_restored(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                normal = self.create(cwd, "--title", "normal", "--description", "details")
                high = self.create(cwd, "--title", "high", "--description", "x",
                                   "--priority", "HIGH", "--due-date", "2020-01-01T00:00:00Z")
                low = self.create(cwd, "--title", "low", "--description", "x",
                                  "--priority", "LOW", "--due-date", "2999-01-01T00:00:00Z")
                self.assertEqual(len({r["id"] for r in (normal, high, low)}), 3)
                for task in (normal, high, low):
                    self.check_created(task)
                    self.assertEqual(task["status"], "pending")
                self.assertIsNone(normal["due_date"])

        def test_b01_intermediate_high_restored(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                high = self.create(cwd, "--title", "High", "--description", "x",
                                   "--priority", "HIGH")
                critical = self.create(cwd, "--title", "Critical", "--description", "x",
                                       "--priority", "CRITICAL")
                self.call(cwd, "complete", "--id", critical["id"])
                self.assertEqual(self.call(cwd, "list-high"), [high])

    suite = unittest.TestSuite()
    for method in selected:
        suite.addTest(Preservation(method))
    return suite


def build_suite(app, profile, achieved, replacements, *, mark_skips=True):
    """Compose over the unchanged frozen parent, adding selected methods."""
    suite, active, dispositions = parent.build_suite(
        app, profile, achieved, replacements, mark_skips=mark_skips)
    repair = cases(app, profile, achieved, dispositions)
    suite.addTests(repair)
    return suite, active, dispositions, inventory(dispositions, profile)
