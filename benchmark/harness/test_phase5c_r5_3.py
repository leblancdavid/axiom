"""Frozen-input fixtures for prospective acceptance supersession composition."""

import copy
import ast
import inspect
import json
from pathlib import Path
import textwrap
import unittest

import acceptance_state_r5_3 as relative
import acceptance_inventory_r5_3 as inventory
import capability_profile_r5_2 as schema
import regression_phase5c_r5 as r5
import regression as original
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

    def test_real_frozen_inventory_and_method_disposition_reconstruction(self):
        for achieved, digest, method_count, assertion_count in (
            ([f"B{i:02}" for i in range(1, 17)],
             "6706171247d40a725142ded41cf357fd1d7e5bf30f34875153cc2746c661652a",
             61, 405),
            (["B01", "B04"],
             "07a5e464e994369fbc000b52bbe4cd037c292a4ff736b3b943db793e17472d0c",
             9, 52),
        ):
            with self.subTest(achieved=achieved):
                methods, _, observed = inventory.collect(achieved)
                inventory.validate_sources(methods)
                self.assertEqual(len(methods), method_count)
                self.assertEqual(sum(len(row["assertions"]) for row in methods.values()),
                                 assertion_count)
                self.assertEqual(w.digest(w.encoded({"achieved": achieved, "methods": methods})),
                                 digest)
                actual = {name: item["state"] for name, item in observed.items()}
                self.assertEqual(inventory.reconstruct(methods, achieved)["dispositions"],
                                 actual)

    def test_real_inventory_duplicate_missing_and_source_drift_fail_closed(self):
        methods, _, _ = inventory.collect(["B01", "B04"])
        altered = copy.deepcopy(methods)
        name = next(iter(altered))
        altered[name]["assertions"].append(copy.deepcopy(altered[name]["assertions"][0]))
        with self.assertRaises(w.ProtocolError):
            inventory.validate_sources(altered)
        altered = copy.deepcopy(methods)
        altered[name]["source_sha256"] = "0" * 64
        with self.assertRaises(w.ProtocolError):
            inventory.validate_sources(altered)
        altered = copy.deepcopy(methods)
        altered.pop("regression.Regression.test_b02_tags_and_failure")
        with self.assertRaises(w.ProtocolError):
            inventory.reconstruct(altered, ["B01", "B04"])

    def test_helper_expansion_is_invocation_and_profile_dependent(self):
        # The real runner installs a closure over the current profile, and
        # repeated suite construction nests closures rather than replacing one.
        baseline = original.check_task
        try:
            inventory.collect(["B01", "B04"])
            first = original.check_task
            self.assertIs(first.__closure__[0].cell_contents, baseline)
            inventory.collect([f"B{i:02}" for i in range(1, 17)])
            second = original.check_task
            self.assertIs(second.__closure__[0].cell_contents, first)
            self.assertEqual(len(schema.compose(["B01", "B04"])["field_types"]), 1)
            self.assertEqual(len(schema.compose([f"B{i:02}" for i in range(1, 17)])["field_types"]), 7)
        finally:
            original.check_task = baseline

    def test_b11_replacement_does_not_preserve_all_unrelated_baseline_assertions(self):
        def body(function):
            return ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]

        baseline = body(original.Regression.test_baseline_lifecycle_filters_failures)
        b11 = r5.load_module("regression_B11", w.CASES / "B11.py")
        suite = b11.cases(w.ROOT / "benchmark/conventional/task_manager.py", {}, frozenset())
        replacement = next(inventory.instances(suite))
        new = body(getattr(type(replacement), replacement._testMethodName))
        old_calls = [node for node in ast.walk(baseline) if isinstance(node, ast.Call)]
        new_calls = [node for node in ast.walk(new) if isinstance(node, ast.Call)]
        self.assertTrue(any(isinstance(node.func, ast.Name) and node.func.id == "check_task"
                            for node in old_calls))
        self.assertFalse(any(isinstance(node.func, ast.Name) and node.func.id == "check_task"
                             for node in new_calls))
        # A concrete lost expectation, independent of the helper's field checks.
        self.assertIn("len({r['id'] for r in (normal, high, low)})",
                      ast.unparse(baseline))
        self.assertNotIn("len({r['id'] for r in (normal, high, low)})",
                         ast.unparse(new))


if __name__ == "__main__":
    unittest.main()
