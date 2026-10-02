"""Frozen-input fixtures for prospective acceptance supersession composition."""

import copy
import json
from pathlib import Path
import unittest

import acceptance_state_r5_3 as relative
import capability_profile_r5_2 as schema
import regression_phase5c_r5 as r5
import workspace as w


RESULTS = w.ROOT / "benchmark/results/phase5c"


def assertion(root, carrier, *dimensions):
    return {"dimensions": list(dimensions), "chain": [root.split("#")[0], carrier]
            if root.split("#")[0] != carrier else [carrier]}


def state(*entries, edges=None):
    return {"methods": {name: {"status": status, "assertions": checks}
                        for name, status, checks in entries},
            "supersessions": edges or {}}


def change(dimensions, **replacements):
    return {"name": "B17", "dimensions": list(dimensions), "replacements": replacements}


class AcceptanceTransition(unittest.TestCase):
    def test_a_active_both(self):
        prior = state(("M", "active", {"M#mutation": assertion("M#mutation", "M", "actor")}))
        rule = change(["actor"], M="N")
        self.assertEqual(relative.compose(prior, rule), relative.compose(copy.deepcopy(prior), rule))
        self.assertEqual(relative.compose(prior, rule)["supersessions"]["M"]["replacement"], "N")

    def test_b_differing_prior_disposition_and_h_shared_semantics(self):
        early = state(("M", "active", {"M#mutation": assertion("M#mutation", "M", "actor")}))
        late = state(("M", "superseded", {"M#mutation": assertion("M#mutation", "M", "actor")}),
                     ("R", "active", {"M#mutation": assertion("M#mutation", "R", "actor")}),
                     edges={"M": {"replacement": "R", "amendment": "B11"}})
        rule = change(["actor"], M="B17_M", R="B17_R")
        a, b = relative.compose(early, rule), relative.compose(late, rule)
        self.assertEqual(a["methods"]["B17_M"]["assertions"]["M#mutation"]["dimensions"],
                         b["methods"]["B17_R"]["assertions"]["M#mutation"]["dimensions"])
        self.assertEqual(a["methods"]["B17_M"]["assertions"]["M#mutation"]["chain"],
                         ["M", "B17_M"])
        self.assertEqual(b["methods"]["B17_R"]["assertions"]["M#mutation"]["chain"],
                         ["M", "R", "B17_R"])
        self.assertEqual(b["supersessions"]["M"]["amendment"], "B11")

    def test_c_replacement_to_replacement_and_l_provenance(self):
        prior = state(("M", "superseded", {"M#mutation": assertion("M#mutation", "M", "actor")}),
                      ("R", "active", {"M#mutation": assertion("M#mutation", "R", "actor")}),
                      edges={"M": {"replacement": "R", "amendment": "B11"}})
        result = relative.compose(prior, change(["actor"], M="unused", R="T"))
        self.assertEqual(result["methods"]["T"]["assertions"]["M#mutation"]["chain"],
                         ["M", "R", "T"])
        self.assertEqual(result["supersessions"]["R"],
                         {"replacement": "T", "amendment": "B17"})

    def test_d_removed_behavior_is_not_recreated(self):
        prior = state(("M", "superseded", {"M#old": assertion("M#old", "M", "actor")}),
                      ("R", "active", {"M#other": assertion("M#other", "R", "other")}),
                      edges={"M": {"replacement": "R", "amendment": "B11"}})
        self.assertEqual(relative.compose(prior, change(["actor"], M="X", R="Y")), prior)

    def test_e_unaffected_assertion_carried_and_f_independent_dimensions(self):
        prior = state(("M", "active", {
            "M#task": assertion("M#task", "M", "actor"),
            "M#user": assertion("M#user", "M", "role"),
            "M#ordering": assertion("M#ordering", "M", "ordering")}))
        actor = relative.compose(prior, change(["actor"], M="A"))
        self.assertEqual(actor["methods"]["A"]["assertions"]["M#ordering"]["dimensions"],
                         ["ordering"])
        both = relative.compose(prior, change(["actor", "role"], M="AR"))
        self.assertEqual(set(both["methods"]["AR"]["assertions"]), set(prior["methods"]["M"]["assertions"]))
        self.assertEqual(both["methods"]["AR"]["assertions"]["M#user"]["chain"], ["M", "AR"])

    def test_g_track_label_never_enters_composition(self):
        prior = state(("M", "active", {"M#task": assertion("M#task", "M", "actor")}))
        results = []
        for label in ("conventional", "lykoi", "arbitrary"):
            record = {"track": label, "acceptance": copy.deepcopy(prior)}
            results.append(relative.compose(record["acceptance"], change(["actor"], M="R")))
        self.assertEqual(results, [results[0]] * 3)

    def test_i_b11_j_b16_and_k_r5_2_prior_activation(self):
        records = [json.loads((RESULTS / f"checkpoint-{label}-B16-r5_2.json").read_text(encoding="utf-8"))
                   for label in ("conventional", "lykoi")]
        replacements = r5.load_module("regression_B16_R5", r5.CASE)
        before = []
        for record in records:
            achieved = record["achieved"]
            profile = schema.compose(achieved)
            self.assertEqual(w.digest(w.encoded(profile)), record["expectation_sha256"])
            selection = r5.select_supersessions(profile, achieved, replacements)
            before.append(selection)
            self.assertEqual(sum(v["replacement"] == "B16-R5" for v in selection.values()),
                             24 if "B16" in achieved else 0)
            self.assertEqual(sum(v["replacement"] == "B11" for v in selection.values()),
                             4 if "B11" in achieved else 0)
            self.assertEqual(schema.compose(achieved), profile)
        self.assertEqual(len(before), 2)

    def test_missing_active_replacement_and_collision_fail_closed(self):
        prior = state(("M", "active", {"M#task": assertion("M#task", "M", "actor")}))
        for rule in (change(["actor"]), change(["actor"], M="M")):
            with self.assertRaises(w.ProtocolError):
                relative.compose(prior, rule)
        self.assertEqual(prior["methods"]["M"]["status"], "active")


if __name__ == "__main__":
    unittest.main()
