"""R5.2.2: correct the B01 carrier's intermediate-state precondition.

Compose the frozen R5.2.1 suite first, replacing only its B01 method when
the original B01 method was superseded by B11. Selection uses dispositions,
never the name of the implementation being tested.
"""

from pathlib import Path
import tempfile
import unittest

import assertion_preservation_r5_2_1 as prior
import workspace as w


VERSION = "PHASE5C-R5.2.2-B01-PRECONDITION/1"
PARENT = prior.VERSION
ROOT = "B01.high_after_critical"
METHOD = "test_b01_intermediate_high_exact_precondition"
OLD_ID = f"assertion_preservation_r5_2_1.cases.<locals>.Preservation.{prior.CARRIERS[prior.PRIORITY]}"


def selection(dispositions):
    # The parent selector fails closed on unknown supersessions.
    selected = prior.selection(dispositions)
    row = dispositions[prior.PRIORITY]
    return [METHOD] if prior.CARRIERS[prior.PRIORITY] in selected and (
        row["state"] == "superseded" and row["replacement"] == "B11"
        and row["origin"] == "B01") else []


def inventory(dispositions, profile):
    result = prior.inventory(dispositions, profile)
    if selection(dispositions):
        original = result[ROOT]
        result[ROOT] = {**original, "restored_at": VERSION,
                        "incomplete_carrier": OLD_ID,
                        "chain": [prior.PRIORITY, "B11:omitted", OLD_ID,
                                  f"{__name__}.cases.<locals>.Correction.{METHOD}"],
                        "precondition": {"create_order": ["NORMAL", "HIGH", "CRITICAL"],
                                         "at_list_high": {"NORMAL": "pending", "HIGH": "pending",
                                                          "CRITICAL": "completed"}}}
    return dict(sorted(result.items()))


def cases(app, profile, achieved, dispositions):
    selected = selection(dispositions)
    app = Path(app).resolve()

    class Correction(unittest.TestCase):
        def call(self, cwd, *args):
            # Use the same CLI envelope as the frozen parent without mutating it.
            import json
            import subprocess
            import sys
            process = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process)
            self.assertEqual(process.stderr, "")
            return json.loads(process.stdout)

        def create(self, cwd, *args):
            owner = (("--owner", "system") if profile["migration_defaults"].get("owner") == "system"
                     else ())
            return self.call(cwd, "create", *args, *owner)

        def test_b01_intermediate_high_exact_precondition(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                default = self.create(cwd, "--title", "Default", "--description", "x")
                high = self.create(cwd, "--title", "High", "--description", "x",
                                   "--priority", "HIGH")
                critical = self.create(cwd, "--title", "Critical", "--description", "x",
                                       "--priority", "CRITICAL")
                self.assertEqual([default["priority"], high["priority"], critical["priority"]],
                                 ["NORMAL", "HIGH", "CRITICAL"])
                self.assertEqual(self.call(cwd, "list-high"), [high])
                self.assertEqual(self.call(cwd, "list"), sorted(
                    (default, high, critical), key=lambda r: (r["created_at"], r["id"])))
                self.assertEqual(self.call(cwd, "complete", "--id", critical["id"])["status"],
                                 "completed")
                self.assertEqual(self.call(cwd, "list-high"), [high])

    return unittest.TestSuite(Correction(name) for name in selected)


def build_suite(app, profile, achieved, replacements, *, mark_skips=True):
    suite, active, dispositions, old_inventory = prior.build_suite(
        app, profile, achieved, replacements, mark_skips=mark_skips)
    selected = selection(dispositions)
    def instances(items):
        for item in items:
            if isinstance(item, unittest.TestSuite):
                yield from instances(item)
            else:
                yield item

    loaded = list(instances(suite))
    old = [test for test in loaded if test.id() == OLD_ID]
    w.require(len(old) == len(selected), "R5.2.1 B01 carrier composition drift")
    retained = unittest.TestSuite(test for test in loaded if test.id() != OLD_ID)
    retained.addTests(cases(app, profile, achieved, dispositions))
    corrected = inventory(dispositions, profile)
    w.require(set(corrected) == set(old_inventory) and all(
        corrected[key] == old_inventory[key] for key in old_inventory if key != ROOT),
        "unrelated restoration roots changed")
    return retained, active, dispositions, corrected
