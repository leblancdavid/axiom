"""Deterministic fixtures for the additive historical preservation transition."""

import copy
import json
import unittest

import acceptance_inventory_r5_3 as previous_inventory
import assertion_preservation_r5_2_1 as repair
import capability_profile_r5_2 as profiles
import regression_phase5c_r5_1 as parent
import workspace as w


class Preservation(unittest.TestCase):
    def composed(self, achieved):
        with previous_inventory.isolated_construction():
            replacements = parent.load_module("regression_B16_R5", parent.CASE)
            suite, active, dispositions = parent.build_suite(
                w.ROOT / "benchmark/conventional/task_manager.py", profiles.compose(achieved),
                achieved, replacements, mark_skips=False)
            return dispositions

    def test_original_active_and_b11_superseded_are_history_relative(self):
        early = ["B01", "B04"]
        late = [f"B{i:02}" for i in range(1, 17)]
        for achieved, expected in ((early, 0), (late, 5)):
            with self.subTest(achieved=achieved):
                dispositions = self.composed(achieved)
                self.assertEqual(len(repair.inventory(dispositions, profiles.compose(achieved))), expected)
                self.assertEqual(len(repair.selection(dispositions)), 0 if not expected else 2)
                # A changed label is not an input to the state-relative selector.
                for label in ("lykoi", "conventional", "unrelated"):
                    record = {"track": label, "dispositions": copy.deepcopy(dispositions)}
                    self.assertEqual(repair.selection(record["dispositions"]),
                                     repair.selection(dispositions))

    def test_provenance_and_original_scenarios(self):
        achieved = [f"B{i:02}" for i in range(1, 17)]
        profile = profiles.compose(achieved)
        selected = repair.inventory(self.composed(achieved), profile)
        self.assertEqual(set(selected), set(repair.ORIGINS))
        for root, item in selected.items():
            self.assertEqual(item["original_carrier"], repair.ORIGINS[root][0])
            self.assertEqual(item["original_source"], repair.ORIGINS[root][1])
            self.assertEqual(item["audit"], repair.AUDIT)
            self.assertEqual(item["chain"][0], item["original_carrier"])
            self.assertEqual(item["chain"][1], "B11:omitted")
        # Frozen roots and frozen B11 body are independently pinned by R5.1.
        self.assertEqual(w.file_hash(parent.CASE), parent.CASE_SHA256)
        self.assertEqual(w.file_hash(w.CASES / "B11.py"), parent.r4.FROZEN["B11"])
        self.assertEqual(selected["baseline.check_task"]["field_types"], profile["field_types"])
        self.assertEqual(w.digest(w.encoded(selected)), w.digest(w.encoded(
            repair.inventory(self.composed(achieved), profile))))

    def test_repeated_construction_and_r5_layers(self):
        small, large = ["B01", "B04"], [f"B{i:02}" for i in range(1, 17)]
        first = self.composed(small)
        self.composed(large)
        self.assertEqual(first, self.composed(small))
        previous = previous_inventory.collect(large)
        self.composed(small)
        self.assertEqual(previous, previous_inventory.collect(large))
        for achieved in (small, large):
            states = self.composed(achieved)
            for original in repair.CARRIERS:
                self.assertEqual(states[original]["state"],
                                 "superseded" if achieved == large else "active")
            self.assertEqual(repair.selection(states), repair.selection(copy.deepcopy(states)))

    def test_unexpected_supersession_fails_closed(self):
        dispositions = self.composed(["B01", "B04"])
        dispositions[repair.BASELINE]["state"] = "superseded"
        dispositions[repair.BASELINE]["replacement"] = "unknown"
        with self.assertRaises(w.ProtocolError):
            repair.selection(dispositions)

    def test_skipped_origin_and_verbatim_r5_replay_do_not_duplicate(self):
        dispositions = self.composed(["B01", "B04"])
        dispositions[repair.PRIORITY] = {"state": "skipped"}
        dispositions[repair.BASELINE] = {"state": "superseded", "replacement": "B16-R5"}
        self.assertEqual(repair.selection(dispositions), [])


if __name__ == "__main__":
    unittest.main()
