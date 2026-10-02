"""Prospective, implementation-independent state-relative composition fixtures."""

import copy
import json
from pathlib import Path
import unittest

import capability_profile as legacy
import capability_profile_r5_2 as relative
import regression_phase5c_r5_1 as acceptance
import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5c"
RULE = {"schema_increment": 1, "requires": [], "add_fields": {},
        "ensure_fields": {"owner": {"type": "str", "default": "system", "from": [""]}}}


class StateRelativeComposition(unittest.TestCase):
    def states(self):
        records = [json.loads((RESULTS / f"checkpoint-{track}-B15-r4.json").read_text(encoding="utf-8"))
                   for track in ("conventional", "lykoi")]
        for record in records:
            self.assertEqual(legacy.identity(record["achieved"])["expectation_sha256"],
                             record["expectation_sha256"])
        return records

    def test_existing_and_absent_are_one_target_without_unrelated_changes(self):
        conventional, lykoi = self.states()
        for record, present in ((conventional, True), (lykoi, False)):
            with self.subTest(present=present):
                prior = copy.deepcopy(record["expectation"])
                target = relative.apply_fragment(prior, "B16", RULE)
                self.assertEqual(prior, record["expectation"])
                self.assertEqual(target["fields"].count("owner"), 1)
                self.assertEqual(target["migration_defaults"]["owner"], "system")
                self.assertEqual(target["field_types"]["owner"], "str")
                self.assertEqual(target["fields"][:-1] if not present else target["fields"],
                                 prior["fields"])
                for field in prior["fields"]:
                    if field != "owner":
                        self.assertEqual(target["migration_defaults"].get(field),
                                         prior["migration_defaults"].get(field))
                self.assertEqual(target["schema_version"], prior["schema_version"] + 1)
                self.assertEqual(target["superseded_cases"], prior["superseded_cases"])
                self.assertEqual(target["achieved"], [*prior["achieved"], "B16"])

    def test_track_label_has_no_effect_and_realizations_differ(self):
        conventional, lykoi = self.states()
        a, b = (record["expectation"] for record in (conventional, lykoi))
        for label in ("conventional", "lykoi", "another-track"):
            with self.subTest(label=label):
                state = {"track": label, "expectation": copy.deepcopy(a)}
                self.assertEqual(relative.apply_fragment(state["expectation"], "B16", RULE),
                                 relative.apply_fragment(a, "B16", RULE))
        self.assertNotIn("owner", b["fields"])
        self.assertIn("owner", a["fields"])
        self.assertEqual(relative.apply_fragment(a, "B16", RULE)["migration_defaults"]["owner"],
                         relative.apply_fragment(b, "B16", RULE)["migration_defaults"]["owner"])
        self.assertEqual(len(relative.apply_fragment(a, "B16", RULE)["fields"]), len(a["fields"]))
        self.assertEqual(len(relative.apply_fragment(b, "B16", RULE)["fields"]), len(b["fields"]) + 1)

    def test_requirement_is_not_achievement_or_implementation(self):
        _, lykoi = self.states()
        self.assertNotIn("B16", lykoi["achieved"])
        self.assertNotIn("owner", lykoi["expectation"]["fields"])
        hypothetical = relative.apply_fragment(lykoi["expectation"], "B16", RULE)
        self.assertIn("owner", hypothetical["fields"])
        self.assertNotIn("owner", lykoi["expectation"]["fields"])
        self.assertNotIn("B16", lykoi["achieved"])
        self.assertEqual(lykoi["files"], self.states()[1]["files"])

    def test_incompatible_prior_is_rejected_without_mutation(self):
        conventional, _ = self.states()
        prior = conventional["expectation"]
        bad = copy.deepcopy(prior)
        bad["migration_defaults"]["owner"] = "unrecognized"
        with self.assertRaises(w.ProtocolError):
            relative.apply_fragment(bad, "B16", RULE)
        self.assertEqual(bad["migration_defaults"]["owner"], "unrecognized")
        for invalid in ({**RULE, "ensure_fields": {"owner": {"type": "int", "default": 2, "from": [0]}}},
                        {**RULE, "add_fields": {"owner": {"type": "str", "default": ""}}}):
            with self.assertRaises(w.ProtocolError):
                relative.apply_fragment(prior, "B16", invalid)

    def test_legacy_b11_and_r5_1_acceptance_unchanged(self):
        replacements = acceptance.load_module("regression_B16_R5", acceptance.CASE)
        for record in self.states():
            achieved = record["achieved"]
            self.assertEqual(relative.compose(achieved), legacy.compose(achieved))
            self.assertEqual(relative.identity(achieved), legacy.identity(achieved))
            active = acceptance.select_supersessions(record["expectation"], achieved, replacements)
            self.assertEqual(len(active), 4 if record["track"] == "conventional" else 0)
            self.assertFalse(any(item["replacement"] == "B16-R5" for item in active.values()))
            next_active = acceptance.select_supersessions(record["expectation"],
                                                          [*achieved, "B16"], replacements)
            self.assertEqual(sum(item["replacement"] == "B16-R5"
                                 for item in next_active.values()),
                             24 if record["track"] == "conventional" else 5)


if __name__ == "__main__":
    unittest.main()
