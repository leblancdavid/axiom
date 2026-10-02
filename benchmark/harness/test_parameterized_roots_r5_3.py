"""Finite executable-case expansion and effective B16 owner witness."""

import unittest

import parameterized_roots_r5_3 as roots
import semantic_channels_r5_3 as channels
import workspace as w


def six_case_fixture(self, cwd):
    first = self.call(cwd, "create", "--title", "first", "--description", "x", "--owner", "  A  ")
    second = self.call(cwd, "create", "--title", "second", "--description", "x", "--owner", "A")
    third = self.call(cwd, "create", "--title", "third", "--description", "x", "--owner", "a")
    fourth = self.call(cwd, "create", "--title", "fourth", "--description", "x", "--owner", "system")
    self.call(cwd, "complete", "--id", first["id"])
    normal = self.call(cwd, "list")
    before = (cwd / "tasks.json").read_bytes()
    for value in ("A", "a", "", " A ", "absent", "system"):
        self.assertEqual(self.call(cwd, "list-owner", "--owner", value),
                         [task for task in normal if task["owner"] == value])
    self.assertEqual((cwd / "tasks.json").read_bytes(), before)


class ParameterizedRoots(unittest.TestCase):
    def test_six_cases_are_source_derived_repeatable_and_track_independent(self):
        def build():
            return roots.expand(six_case_fixture, "fixture", "fixture.py", "replacement",
                                lineage={"original": "source"}, achieved=("B16",))

        first = build()
        self.assertEqual(first, build())
        self.assertEqual(w.digest(w.encoded(first)), w.digest(w.encoded(build())))
        self.assertEqual(first["unresolved"], [])
        calls = [row for row in first["roots"] if row["kind"] == "call" and
                 row["arguments"] and row["arguments"][0] == "list-owner"]
        self.assertEqual([row["arguments"][-1] for row in calls],
                         ["A", "a", "", " A ", "absent", "system"])
        self.assertEqual([[task["binding"] for task in row["expected_result"]] for row in calls],
                         [["first", "second"], ["third"], [], [], [], ["fourth"]])
        self.assertEqual(calls[0]["expected_result"][0]["status"], "completed")
        self.assertEqual(len({row["id"] for row in calls}), 6)
        self.assertEqual(len({row["site"] for row in calls}), 1)
        self.assertTrue(all(row["expected_persistent_state"] and row["prior_steps"] and
                            row["lineage"] == {"original": "source"} and
                            row["cli_outcome"]["exit"] == 0 for row in calls))
        self.assertNotIn("track", roots.expand.__code__.co_varnames)

    def test_frozen_carrier_and_other_loops(self):
        full = channels.collect([f"B{i:02}" for i in range(1, 17)])
        self.assertFalse(full["unresolved_parameterized_loops"])
        self.assertEqual({row["source"] for group in full["helper_parameterized_sites"].values()
                          for row in group},
                         {"benchmark/harness/regression.py:80",
                          "benchmark/harness/assertion_preservation_r5_2_1.py:105"})
        effective = full["parameterized_roots"]
        owner = next(rows for name, rows in effective.items() if name.endswith(
            "Owner.test_registered_trim_reject_and_exact_owner_listing"))
        owner_calls = [row for row in owner if row["site"].endswith(":113") and row["kind"] == "call"]
        self.assertEqual(len(owner_calls), 6)
        self.assertEqual([row["arguments"][-1] for row in owner_calls],
                         ["Alex", "alex", "", " Alex ", "missing", "system"])
        self.assertEqual([[task["binding"] for task in row["expected_result"]] for row in owner_calls],
                         [["first", "second"], ["other"], [], [], [], ["formerly_unowned"]])
        self.assertEqual(owner_calls[0]["original_assertion"],
                         "benchmark/harness/cases/B10.py:45")
        self.assertTrue(all(row["expected_persistent_state"] and row["state"] == "replacement"
                            for row in owner_calls))
        for suffix, site, count in (("Categories.test_create_filter_and_failed_create_with_owner", ":46", 5),
                                     ("DueInvalid.test_invalid_ranges_and_timestamps_do_not_write_with_owner", ":64", 3),
                                     ("DependencyCycles.test_order_cycles_and_no_write_failures_with_owner", ":43", 6),
                                     ("Archived.test_archived_pending_and_completed_mutations_are_rejected_with_owner", ":34", 2)):
            matched = next(rows for name, rows in effective.items() if name.endswith(suffix))
            self.assertEqual(sum(row["kind"] == "call" and row["site"].endswith(site)
                                 for row in matched), count, suffix)
        early = channels.collect(["B01", "B04"])
        self.assertFalse(early["unresolved_parameterized_loops"])
        self.assertFalse(any(name.startswith("regression_B16_R5.")
                             for name in early["parameterized_roots"]))


if __name__ == "__main__":
    unittest.main()
