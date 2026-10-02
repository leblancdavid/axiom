"""Independent prototype checks; these do not promote a new acceptance oracle."""

import copy
from pathlib import Path
import unittest

from benchmark.semantic import format as semantic
from benchmark.semantic import probe
import acceptance_repaired_r5_3 as frozen_bridge


PROTOTYPE = Path(__file__).resolve().parents[1] / "semantic" / "prototype.json"
B17_DRAFT = PROTOTYPE.with_name("b17-draft.json")


class SemanticPrototype(unittest.TestCase):
    def setUp(self):
        self.document = semantic.load(PROTOTYPE)

    def test_both_histories_select_distinct_b01_carriers(self):
        early = semantic.compile_plan(self.document, ["B01", "B04"])
        full = semantic.compile_plan(self.document, [f"B{i:02}" for i in range(1, 17)])
        self.assertEqual([(p["semantic_id"], p["variant"]) for p in early],
                         [("B01.high_after_critical", "early_original")])
        self.assertEqual(len(full), 5)
        corrected = full[0]["steps"]
        self.assertEqual([s["invoke"]["command"] for s in corrected if "invoke" in s][:3],
                         ["create", "create", "create"])
        self.assertIn("B01.full_exact_intermediate_state",
                      [s["observe"]["id"] for s in corrected if "observe" in s])

    def test_fails_closed_on_overlapping_variants(self):
        bad = copy.deepcopy(self.document)
        bad["scenarios"][0]["variants"][1]["when"]["requires"] = ["B01", "B16"]
        with self.assertRaisesRegex(semantic.FormatError, "overlapping variants"):
            semantic.validate(bad)

    def test_fails_closed_on_unbound_reference(self):
        bad = copy.deepcopy(self.document)
        bad["scenarios"][0]["variants"][0]["steps"][0]["invoke"]["args"].append(
            {"ref": "not_created.id"})
        with self.assertRaisesRegex(semantic.FormatError, "unbound"):
            semantic.validate(bad)

    def test_fails_closed_on_non_string_cli_literal(self):
        bad = copy.deepcopy(self.document)
        bad["scenarios"][0]["variants"][0]["steps"][0]["invoke"]["args"][0] = (
            {"literal": 5})
        with self.assertRaisesRegex(semantic.FormatError, "CLI literal"):
            semantic.validate(bad)

    def test_fails_closed_on_missing_observation_and_duplicate_id(self):
        bad = copy.deepcopy(self.document)
        bad["scenarios"][0]["variants"][1]["steps"] = [
            s for s in bad["scenarios"][0]["variants"][1]["steps"] if "observe" not in s]
        with self.assertRaisesRegex(semantic.FormatError, "no observation"):
            semantic.validate(bad)
        bad = copy.deepcopy(self.document)
        bad["scenarios"][0]["variants"][1]["steps"][3]["observe"]["id"] = (
            bad["scenarios"][0]["variants"][0]["steps"][3]["observe"]["id"])
        with self.assertRaisesRegex(semantic.FormatError, "duplicate observation ID"):
            semantic.validate(bad)

    def test_pinned_post_b16_snapshots_run_selected_prototype_witnesses(self):
        self.assertEqual(len(probe.probe(self.document, "conventional")), 5)
        self.assertEqual(probe.probe(self.document, "lykoi"),
                         [("B01.high_after_critical", "early_original")])

    def test_historical_carriers_exist_in_corrected_parent(self):
        for achieved in ([f"B{i:02}" for i in range(1, 17)], ["B01", "B04"]):
            parent = frozen_bridge.collect(achieved)
            available = set(parent["parent_methods"]) | set(parent["repair_carrier_ids"])
            for scenario in self.document["scenarios"]:
                for variant in scenario["variants"]:
                    if set(variant["when"]["requires"]) <= set(achieved) and not (
                            set(variant["when"]["forbids"]) & set(achieved)):
                        self.assertIn(variant["carrier"], available)

    def test_b17_draft_is_conditional_and_not_retroactive(self):
        draft = semantic.load(B17_DRAFT)
        self.assertEqual(semantic.compile_plan(draft, ["B01", "B04"]), [])
        self.assertEqual(semantic.compile_plan(draft, [f"B{i:02}" for i in range(1, 17)]), [])
        target = semantic.compile_plan(draft, [f"B{i:02}" for i in range(1, 18)])
        self.assertEqual({p["semantic_id"] for p in target},
                         {"B17.user_roles", "B17.task_actor_and_permissions",
                          "B17.admin_cross_owner", "B17.migration_requires_actor",
                          "B17.mutation_command_actor_matrix"})


if __name__ == "__main__":
    unittest.main()
