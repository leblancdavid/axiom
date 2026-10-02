"""Invocation-specific frozen helper fixtures across both achieved histories."""

import collections
import unittest

import capability_profile_r5_2 as profiles
import helper_invocations_r5_3 as helpers
import semantic_channels_r5_3 as channels


class HelperInvocations(unittest.TestCase):
    def test_migration_calls_and_row_iterations_are_distinct(self):
        for achieved, expected_baseline in (([f"B{i:02}" for i in range(1, 17)],
                                             "test_baseline_migration_corruption_with_owner"),
                                            (["B01", "B04"], "test_baseline_migration_corruption")):
            evidence = channels.collect(achieved)
            roots = evidence["helper_invocation_roots"]
            migration = {name: group for name, group in roots.items()
                         if any(root["helper"] == "benchmark/harness/regression.py:71-83"
                                for root in group)}
            self.assertEqual(len(migration), 3 if "B02" in achieved else 2)
            self.assertTrue(any(name.endswith(expected_baseline) for name in migration))
            for name, group in migration.items():
                invocations = collections.defaultdict(list)
                for root in group:
                    invocations[root["invocation"]].append(root)
                    self.assertEqual(root["method"], name)
                    self.assertEqual(root["provenance"][-1], root["assertion"])
                self.assertEqual(len(invocations), 2)
                for invocation in invocations.values():
                    precondition = invocation[0]["precondition"]
                    self.assertTrue(precondition["input_payload"])
                    self.assertEqual(len([r for r in invocation if r["case"] == "migrate"]), 1)
                    self.assertEqual(len([r for r in invocation if r["case"] == "sorted-rows"]), 1)
                    self.assertEqual(len([r for r in invocation if r["case"].endswith(":id-type")]),
                                     len(precondition["expected_rows"]))
            b01 = next(group for name, group in migration.items()
                       if name.endswith("test_b01_historical_priorities"))
            self.assertEqual({len(root["precondition"]["expected_rows"]) for root in b01}, {3})
            self.assertEqual({root["precondition"]["input_payload"]["schema_version"]
                              for root in b01}, {2, 3})
            ids = [root["id"] for group in roots.values() for root in group]
            self.assertEqual(len(ids), len(set(ids)))

    def test_created_tasks_have_independent_profile_field_checks(self):
        full = channels.collect([f"B{i:02}" for i in range(1, 17)])
        name, group = next((name, group) for name, group in full["helper_invocation_roots"].items()
                           if name.endswith("test_baseline_create_assertions_restored"))
        self.assertEqual(len(group), 3 * (7 + 7))
        self.assertEqual([root["precondition"]["created_task"]["title"]
                          for root in group if root["case"] == "fields"],
                         ["normal", "high", "low"])
        fields = profiles.compose(full["achieved"])["field_types"]
        for title in ("normal", "high", "low"):
            checks = [root for root in group if root["precondition"]["created_task"]["title"] == title]
            self.assertEqual({root["case"] for root in checks if root["case"].startswith("field:")},
                             {f"field:{field}" for field in fields})

    def test_unknown_helper_caller_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unreconstructed upgraded caller"):
            helpers._migration_cases("unknown", {"line": 3, "expression": "upgraded(...)"},
                                     [], {"migration_defaults": {} })


if __name__ == "__main__":
    unittest.main()
