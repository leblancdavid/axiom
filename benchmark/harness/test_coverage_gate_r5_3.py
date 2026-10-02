"""Branch-qualified prospective coverage remains fail-closed."""

import unittest

import coverage_gate_r5_3 as coverage


class CoverageBranches(unittest.TestCase):
    def test_historical_schema_else_is_unreachable_in_both_histories(self):
        for history in ([f"B{i:02}" for i in range(1, 17)], ["B01", "B04"]):
            with self.subTest(history=history):
                result = coverage.collect(history)
                row = next(row for row in result["direct_assertions"]
                           if row["method"].endswith("test_b01_historical_priorities")
                           and row["source"].endswith(":191"))
                self.assertEqual(row["disposition"], "unreachable")
                self.assertEqual(row["branch"][-1]["condition"],
                                 "PROFILE['schema_version'] > 3")
                self.assertFalse(row["branch"][-1]["reachable"])
                self.assertNotIn(row, result["unmapped_source_channels"])
                self.assertEqual(result["assertion_level_semantic_diff"],
                                 "BLOCKED until concrete path completeness")


if __name__ == "__main__":
    unittest.main()
