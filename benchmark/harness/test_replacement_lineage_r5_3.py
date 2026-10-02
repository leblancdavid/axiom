"""Prospective R4/R5 site-level lineage checks against frozen source bodies."""

import copy
import unittest

import replacement_lineage_r5_3 as lineage
import workspace as w


class ReplacementLineage(unittest.TestCase):
    def test_rewritten_sites_and_owner_replays_are_exhaustively_accounted(self):
        full = [f"B{i:02}" for i in range(1, 17)]
        early = ["B01", "B04"]
        for achieved, count in ((full, 26), (early, 1), (full, 26)):
            with self.subTest(achieved=achieved):
                first = lineage.collect(achieved)
                self.assertEqual(first, lineage.collect(achieved))
                self.assertEqual(len(first["replacements"]), count)
                self.assertFalse(first["full_prior_assertion_equivalence_proven"])
                for old, entry in first["replacements"].items():
                    if old in lineage.R4_MAP:
                        self.assertEqual(len(entry["preserved"]),
                                         len(lineage.R4_MAP[old]["preserved"]))
                    if entry.get("mechanism") == "rewritten_B10":
                        self.assertEqual(set(entry["source"]),
                                         set(entry["preserved"]) | set(entry["changed"]))

    def test_unmapped_assertion_fails_closed(self):
        original = lineage.R4_MAP
        try:
            altered = copy.deepcopy(original)
            altered[next(iter(altered))]["preserved"].pop(33)
            lineage.R4_MAP = altered
            with self.assertRaises(w.ProtocolError):
                lineage.collect([f"B{i:02}" for i in range(1, 17)])
        finally:
            lineage.R4_MAP = original


if __name__ == "__main__":
    unittest.main()
