"""Composition-only R5 fixtures; never modify real B15 track workspaces."""

import json
from pathlib import Path
import unittest

import regression_phase5c_r5 as r5
import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5c"


class R5Composition(unittest.TestCase):
    def setUp(self):
        self.replacements = r5.load_module("regression_B16_R5", r5.CASE)

    def state(self, track):
        record = json.loads((RESULTS / f"checkpoint-{track}-B15-r4.json").read_text(encoding="utf-8"))
        achieved = record["achieved"]
        app = (Path("generated/task_manager.py") if track == "lykoi"
               else Path("benchmark/conventional/task_manager.py"))
        suite, active, dispositions = r5.build_suite(app, record["expectation"],
                                                     achieved, self.replacements, mark_skips=False)
        return record, suite, active, dispositions

    def test_real_B15_states_have_exact_R4_composition(self):
        for track, cases, existing, affected in (("conventional", 34, 4, 24),
                                                   ("lykoi", 9, 0, 5)):
            with self.subTest(track=track):
                record, suite, active, disposition = self.state(track)
                self.assertNotIn("B16", record["achieved"])
                self.assertEqual(suite.countTestCases(), cases)
                self.assertEqual(len(active), existing)
                self.assertTrue(all(active[name]["replacement"] != "B16-R5"
                                    for name in active))
                self.assertEqual(len([name for name in self.replacements.METHODS
                                      if name in disposition and disposition[name]["state"] in
                                      ("active", "replacement")]), affected)

    def test_hypothetical_B16_achievement_is_track_local_and_replaced(self):
        for track, count, prior in (("conventional", 24, 4), ("lykoi", 5, 0)):
            with self.subTest(track=track):
                record, suite, previous, _ = self.state(track)
                synthetic = [*record["achieved"], "B16"]
                active = r5.select_supersessions(record["expectation"], synthetic, self.replacements)
                selected = {name for name in active.keys() & self.replacements.METHODS.keys()
                            if active[name]["replacement"] == "B16-R5"}
                self.assertEqual(len(selected), count)
                self.assertEqual(len(active), prior + count)
                replacements = self.replacements.cases(suite, selected,
                                                        Path("fixture/task_manager.py"),
                                                        record["expectation"])
                self.assertEqual(replacements.countTestCases(), count)
                ids = set()
                for test in replacements:
                    self.assertNotIn(test.id(), ids)
                    ids.add(test.id())
                self.assertEqual(ids, {self.replacements.replacement_id(name)
                                       for name in selected})
                if track == "conventional":
                    self.assertNotIn("regression.Regression.test_baseline_lifecycle_filters_failures",
                                     selected)
                    self.assertIn("regression_B11_R4.cases.<locals>.Source."
                                  "test_verbatim_default_and_mutations_after_b11", selected)
                else:
                    self.assertIn("regression.Regression.test_baseline_lifecycle_filters_failures",
                                  selected)
                    self.assertNotIn("regression_B11_R4.cases.<locals>.Source."
                                     "test_verbatim_default_and_mutations_after_b11", selected)

    def test_mapping_is_exact_and_b10_is_only_migration_exception(self):
        methods = self.replacements.METHODS
        self.assertEqual(len(methods), 27)
        self.assertEqual({name for name in methods if name.endswith("test_migration_defaults_unowned")},
                         {"regression_B10.cases.<locals>.Owner.test_migration_defaults_unowned"})
        self.assertEqual(len(self.replacements.SPECIAL), 2)
        self.assertTrue(self.replacements.SPECIAL <= methods.keys())


if __name__ == "__main__":
    unittest.main()
