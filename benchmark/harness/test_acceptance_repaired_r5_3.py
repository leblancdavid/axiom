"""R5.3 bridge fixtures: frozen repaired roots are imported, not duplicated."""

import unittest

import acceptance_repaired_r5_3 as bridge
import assertion_preservation_r5_2_1 as repair
import workspace as w


class RepairedLineage(unittest.TestCase):
    def test_frozen_transition_matches_executable_carriers(self):
        for achieved, expected in ((["B01", "B04"], 0),
                                   ([f"B{i:02}" for i in range(1, 17)], 5)):
            with self.subTest(achieved=achieved):
                first = bridge.collect(achieved)
                self.assertEqual(first, bridge.collect(achieved))
                self.assertEqual(len(first["restored_roots"]), expected)
                self.assertEqual(len(first["repair_carrier_ids"]), 0 if not expected else 2)
                self.assertEqual(first["repair_inventory_sha256"], bridge.EXPECTED[tuple(achieved)])
                self.assertFalse(first["full_prior_assertion_equivalence_proven"])
                for key, row in first["restored_roots"].items():
                    self.assertEqual(row["original_carrier"], repair.ORIGINS[key][0])
                    self.assertEqual(row["chain"][0], repair.ORIGINS[key][0])

    def test_source_drift_fails_closed(self):
        expected = bridge.REPAIR_SHA256
        try:
            bridge.REPAIR_SHA256 = "0" * 64
            with self.assertRaises(w.ProtocolError):
                bridge.collect(["B01", "B04"])
        finally:
            bridge.REPAIR_SHA256 = expected
