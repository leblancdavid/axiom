"""Finite executable-case expansion and effective B16 owner witness."""

import unittest

import capability_profile_r5_2 as profiles
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


def transitioned_observation_fixture(self, cwd):
    ordinary = self.create(cwd, "--title", "ordinary", "--description", "x")
    selected = self.create(cwd, "--title", "selected", "--description", "x",
                           "--priority", "HIGH")
    changed = self.create(cwd, "--title", "changed", "--description", "x",
                          "--priority", "CRITICAL")
    self.assertEqual(self.call(cwd, "list-high"), [selected])
    self.assertEqual(self.call(cwd, "complete", "--id", changed["id"])["status"], "completed")
    self.assertEqual(self.call(cwd, "list-high"), [selected])


def distinct_ids_fixture(self, cwd):
    alpha = self.create(cwd, "--title", "alpha", "--description", "x")
    beta = self.create(cwd, "--title", "beta", "--description", "x")
    gamma = self.create(cwd, "--title", "gamma", "--description", "x")
    self.assertEqual(len({row["id"] for row in (alpha, beta, gamma)}), 3)


def returned_and_persisted_fixture(self, cwd):
    normal = self.create(cwd, "--title", "normal", "--description", "x")
    high = self.create(cwd, "--title", "high", "--description", "x", "--priority", "HIGH")
    critical = self.create(cwd, "--title", "critical", "--description", "x", "--priority", "CRITICAL")
    self.assertEqual([normal["priority"], high["priority"], critical["priority"]],
                     ["NORMAL", "HIGH", "CRITICAL"])
    self.assertEqual(self.call(cwd, "list-high"), [high])


def comprehended_return_fixture(self, cwd):
    first = self.create(cwd, "--title", "first", "--owner", "Alex")
    second = self.create(cwd, "--title", "second", "--owner", "system")
    self.assertEqual([task["owner"] for task in (first, second)], ["Alex", "system"])


def file_state_fixture(self, cwd):
    self.assertFalse((cwd / "tasks.json").exists())
    before = (cwd / "tasks.json").read_bytes()
    self.call(cwd, "list", error="migration_required")
    self.assertEqual((cwd / "tasks.json").read_bytes(), before)


class ParameterizedRoots(unittest.TestCase):
    def test_filesystem_checks_are_separate_persisted_state_roots(self):
        result = roots.expand(file_state_fixture, "fixture", "fixture.py", "active")
        absent, unchanged = result["direct_assertions"]
        self.assertEqual((absent["operation"], absent["expected_result"], absent["phase"]),
                         ("file-existence", False, "persisted_state"))
        self.assertEqual((unchanged["operation"], unchanged["expected_result"]),
                         ("file-bytes-equality", "$before (captured file bytes)"))
        self.assertEqual(unchanged["snapshot"]["source"],
                         f"fixture.py:{file_state_fixture.__code__.co_firstlineno + 2}")
        self.assertEqual(unchanged["prior_steps"][-1]["expression"],
                         "self.call(cwd, 'list', error='migration_required')")
        self.assertNotEqual(absent["id"], unchanged["id"])

    def test_real_file_state_carriers_have_distinct_roots(self):
        inventory = channels.collect(["B01", "B04"])
        regression = next(rows for name, rows in inventory["direct_assertion_roots"].items()
                          if name.endswith("test_baseline_lifecycle_filters_failures"))
        self.assertTrue(any(row["assertion"].endswith("regression.py:91") and
                            row["expected_result"] is False for row in regression))
        migration = next(rows for name, rows in inventory["direct_assertion_roots"].items()
                         if name.endswith("SourceLabel.test_explicit_migration_of_prior_storage"))
        self.assertTrue(any(row["assertion"].endswith("B04.py:59") and
                            row["snapshot"]["source"].endswith("B04.py:57") for row in migration))
        self.assertTrue(any(row["assertion"].endswith("B04.py:67") and
                            row["snapshot"]["source"].endswith("B04.py:65") for row in migration))
        self.assertTrue(any(row["assertion"].endswith("B04.py:63") and
                            row["operation"] == "persisted-json-field-equality" and
                            row["field"] == "schema_version" and
                            row["expected_result"] == profiles.compose(["B01", "B04"])[
                                "schema_version"] for row in migration))

    def test_comprehended_returned_fields_are_separate(self):
        expanded = roots.expand(comprehended_return_fixture, "fixture", "fixture.py", "active")
        self.assertEqual([(row["binding"], row["field"], row["expected_result"])
                          for row in expanded["direct_assertions"]],
                         [("first", "owner", "Alex"), ("second", "owner", "system")])

    def test_returned_values_are_independent_of_requested_and_persisted_values(self):
        def build():
            return roots.expand(returned_and_persisted_fixture, "fixture", "fixture.py",
                                "restoration", lineage={"frozen": "R5.2.2"})

        first = build()
        self.assertEqual(first, build())
        self.assertEqual(w.digest(w.encoded(first)), w.digest(w.encoded(build())))
        returned = first["direct_assertions"]
        self.assertEqual([(r["binding"], r["field"], r["expected_result"]) for r in returned],
                         [("normal", "priority", "NORMAL"), ("high", "priority", "HIGH"),
                          ("critical", "priority", "CRITICAL")])
        self.assertEqual(len({r["id"] for r in returned}), 3)
        self.assertEqual(returned[0]["creation_input"]["requested_fields"].get("--priority"), None)
        self.assertEqual(returned[1]["creation_input"]["requested_fields"]["--priority"], "HIGH")
        self.assertEqual(returned[2]["creation_input"]["requested_fields"]["--priority"], "CRITICAL")
        self.assertTrue(all(r["operation"] == "returned-field-equality" and
                            r["observed_value"] == f"${r['binding']}.priority" and
                            r["creation_input"]["returned_binding"] == r["binding"] and
                            r["lineage"] == {"frozen": "R5.2.2"} and
                            len(r["prior_steps"]) == 3 for r in returned))
        persisted = first["observations"][0]
        self.assertEqual(persisted["operation"], "list-high")
        self.assertNotIn(persisted["id"], {r["id"] for r in returned})
        self.assertEqual(persisted["expected_result"], [persisted["entities"]["high"]])

    def test_input_alone_creates_no_returned_field_root(self):
        def input_only(self, cwd):
            high = self.create(cwd, "--title", "high", "--priority", "HIGH")
            self.assertEqual(self.call(cwd, "list-high"), [high])

        result = roots.expand(input_only, "fixture", "fixture.py", "restoration")
        self.assertEqual(result["direct_assertions"], [])
        self.assertEqual(len(result["observations"]), 1)

    def test_real_corrected_carrier_returned_priority_roots(self):
        inventory = channels.collect([f"B{i:02}" for i in range(1, 17)])
        name = next(name for name in inventory["direct_assertion_roots"] if name.endswith(
            "test_b01_intermediate_high_exact_precondition"))
        rows = [r for r in inventory["direct_assertion_roots"][name]
                if r["operation"] == "returned-field-equality"]
        self.assertEqual([(r["binding"], r["expected_result"]) for r in rows],
                         [("default", "NORMAL"), ("high", "HIGH"), ("critical", "CRITICAL")])
        self.assertTrue(all(r["assertion"].endswith(":75") and
                            r["lineage"]["restoration"][0]["frozen_root"] ==
                            "B01.high_after_critical" for r in rows))

    def test_early_source_return_and_later_persisted_source_are_distinct(self):
        inventory = channels.collect(["B01", "B04"])
        name = next(name for name in inventory["direct_assertion_roots"] if name.endswith(
            "SourceLabel.test_verbatim_default_and_mutations"))
        returned = [row for row in inventory["direct_assertion_roots"][name]
                    if row["operation"] == "returned-field-equality"]
        self.assertEqual([(row["binding"], row["expected_result"]) for row in returned],
                         [("labelled", "  API\tfeed  "), ("omitted", ""), ("empty", ""),
                          ("completed", "  API\tfeed  ")])
        self.assertEqual(returned[0]["creation_input"]["requested_fields"]["--source"],
                         "  API\tfeed  ")
        self.assertEqual(returned[-1]["creation_input"]["returned_binding"], "labelled")
        persisted = [row for row in inventory["direct_observation_roots"][name]
                     if row["operation"] == "list"]
        self.assertTrue(persisted)
        self.assertFalse({row["id"] for row in returned} & {row["id"] for row in persisted})

    def test_distinct_ids_from_previous_create_results(self):
        def build():
            return roots.expand(distinct_ids_fixture, "fixture", "fixture.py", "restoration")

        first = build()
        self.assertEqual(first, build())
        self.assertEqual(len(first["direct_assertions"]), 1)
        root = first["direct_assertions"][0]
        self.assertEqual(root["operation"], "distinct-field-count")
        self.assertEqual(root["inputs"], {"field": "id", "bindings": ["alpha", "beta", "gamma"],
                                          "values": ["$alpha.id", "$beta.id", "$gamma.id"]})
        self.assertEqual(root["expected_count"], 3)
        self.assertEqual(len(root["prior_steps"]), 3)
        self.assertEqual(root["id"], build()["direct_assertions"][0]["id"])

    def test_direct_observation_joins_transition_assertion_and_lineage(self):
        lineage = {"restoration": [{"frozen_root": "fixture.original",
                                    "chain": ["original", "lost", "incomplete", "corrected"],
                                    "precondition": {"at_list_high": {
                                        "NORMAL": "pending", "HIGH": "pending",
                                        "CRITICAL": "completed"}}}]}

        def build():
            return roots.expand(transitioned_observation_fixture, "fixture", "fixture.py",
                                "restoration", lineage=lineage, achieved=("B16",))

        first = build()
        self.assertEqual(first, build())
        self.assertEqual(w.digest(w.encoded(first)), w.digest(w.encoded(build())))
        before, transition, after = first["observations"]
        self.assertEqual(len({row["id"] for row in first["observations"]}), 3)
        self.assertNotEqual(before["id"], after["id"])
        self.assertEqual(before["lineage"]["restoration"], [])
        self.assertEqual(after["lineage"], lineage)
        self.assertEqual(after["operation"], "list-high")
        self.assertEqual(after["arguments"], ["list-high"])
        self.assertEqual(after["expected_result"], [after["entities"]["selected"]])
        self.assertEqual(after["expected_result_shape"], "exact list of task rows")
        self.assertEqual(after["entities"]["ordinary"]["status"], "pending")
        self.assertEqual(after["entities"]["selected"]["status"], "pending")
        self.assertEqual(after["entities"]["changed"]["status"], "completed")
        self.assertEqual(before["entities"]["changed"]["status"], "pending")
        self.assertEqual(after["prior_steps"][-1]["source"], transition["assertion"])
        self.assertEqual(after["call"], after["assertion"])

    def test_corrected_carrier_post_completion_has_canonical_invocation(self):
        full = channels.collect([f"B{i:02}" for i in range(1, 17)])
        name = next(name for name in full["direct_observation_roots"] if name.endswith(
            "test_b01_intermediate_high_exact_precondition"))
        observations = full["direct_observation_roots"][name]
        earlier, later = (row for row in observations if row["operation"] == "list-high")
        self.assertEqual(earlier["lineage"]["restoration"], [])
        self.assertEqual(later["lineage"]["restoration"][0]["frozen_root"],
                         "B01.high_after_critical")
        self.assertEqual(later["entities"]["critical"]["status"], "completed")
        self.assertEqual(later["expected_result"], [later["entities"]["high"]])
        self.assertIn("complete", later["prior_steps"][-1]["expression"])

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
