"""Pinned-history checks for the conservative bulk reconciliation worksheet."""

import json
import unittest

import bulk_reconcile_r5_3 as bulk
import semantic_channels_r5_3 as channels
import workspace as w


class BulkReconciliation(unittest.TestCase):
    def test_saved_histories_keep_unverified_paths_open(self):
        results = w.ROOT / "benchmark/results/phase5c"
        for label, achieved, expected in (("full", [f"B{i:02}" for i in range(1, 17)], 233),
                                          ("early", ["B01", "B04"], 28)):
            with self.subTest(history=label):
                baseline = json.loads((results / f"R5_3-{label}-runtime-reconciliation.json").read_text())
                trace = json.loads((results / f"R5_3-{label}-runtime-trace.json").read_text())
                source = channels.collect(achieved)["direct_assertion_roots"]
                sheet = bulk.reconcile(baseline, trace, source)
                self.assertEqual(sheet["baseline_candidates"], expected)
                self.assertEqual(sum(sheet["candidate_counts"].values()), expected)
                self.assertTrue(sheet["unmapped_semantic_runtime_events"])
                self.assertEqual(sheet["rejection_path_completeness"], "NOT ESTABLISHED")
                self.assertEqual(sheet["assertion_level_semantic_diff"], "BLOCKED")
                for identity, indices in sheet["canonical_root_to_events"].items():
                    self.assertEqual(len(indices), 1)
                    self.assertIn(identity, sheet["runtime_event_to_roots"][str(indices[0])])
                sites = {row["source"]: row for row in sheet["source_candidates"]}
                self.assertEqual(sites["benchmark/harness/cases/B04.py:59"]["disposition"],
                                 "SEMANTIC_ROOT")
                self.assertEqual(sites["benchmark/harness/cases/B04.py:67"]["disposition"],
                                 "SEMANTIC_ROOT")


if __name__ == "__main__":
    unittest.main()
