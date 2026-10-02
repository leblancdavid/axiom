"""B16 target derivation and prospective oracle inventory, never run on B15 apps."""

import json
from pathlib import Path
import unittest

import capability_profile_r5_2 as relative
import regression_phase5c_r5_2 as prospective
import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5c"


class B16Prospective(unittest.TestCase):
    def test_actual_b15_histories_derive_two_targets_from_one_frozen_fragment(self):
        for track, digest, count in (("conventional", "272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8", 24),
                                     ("lykoi", "0c61e3be245c0b0e2870ed872c71ea62a6423b59c90575ac720e41f608040f98", 5)):
            with self.subTest(track=track):
                record = json.loads((RESULTS / f"checkpoint-{track}-B15-r4.json").read_text(encoding="utf-8"))
                app = (Path("generated/task_manager.py") if track == "lykoi" else
                       Path("benchmark/conventional/task_manager.py"))
                # Build only: these B15 implementations must never execute B16 acceptance.
                suite, target, active, disposition = prospective.prospective(
                    record, [*record["achieved"], "B16"], (w.ROOT / app), mark_skips=False)
                self.assertEqual(target["expectation_sha256"], digest)
                self.assertEqual(target, relative.identity([*record["achieved"], "B16"]))
                self.assertEqual(target["expectation"]["migration_defaults"]["owner"], "system")
                self.assertEqual(sum(item["replacement"] == "B16-R5" for item in active.values()), count)
                self.assertEqual(sum(name.startswith("regression_B16.") for name in disposition), 3)
                self.assertEqual(suite.countTestCases(), len(disposition))
                self.assertNotIn("B16", record["achieved"])
                self.assertEqual(record["expectation"]["migration_defaults"].get("owner"),
                                 "" if track == "conventional" else None)


if __name__ == "__main__":
    unittest.main()
