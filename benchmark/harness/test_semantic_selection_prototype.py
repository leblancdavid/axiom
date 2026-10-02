"""Finite witnesses and negative checks for the unfrozen ordered selection relation."""

import copy
import json
from pathlib import Path
import unittest

from benchmark.semantic import selection
from benchmark.semantic.format import FormatError


FIXTURE = Path(__file__).resolve().parents[1] / "semantic" / "selection-fixtures.json"


class SelectionFormat(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_linked_witnesses_and_counterexamples(self):
        results = selection.run_witnesses(self.doc)
        self.assertEqual(len(results), 13)
        for rule in self.doc["rules"]:
            for case in rule["cases"]:
                self.assertEqual(results[(rule["id"], case["id"])], case["holds"])
        from benchmark.semantic import invariants
        invariant_path = FIXTURE.with_name("invariant-fixtures.json")
        invariant_ids = {r["id"] for r in invariants.validate(
            json.loads(invariant_path.read_text(encoding="utf-8")))["invariants"]}
        self.assertTrue(set(self.doc["rules"][1]["depends_on"]) <= invariant_ids)

    def test_new_finite_collections_are_not_enumerated_in_rule(self):
        rule = self.doc["rules"][0]
        task = lambda id, priority: {"id": id, "priority": priority}
        source = [task("a", "HIGH"), task("b", "LOW"), task("c", "HIGH")]
        self.assertTrue(selection.evaluate(rule, {"tasks": source,
                                                   "result": [source[0], source[2]]}))
        self.assertFalse(selection.evaluate(rule, {"tasks": source,
                                                    "result": [source[0]]}))
        self.assertFalse(selection.evaluate(rule, {"tasks": source,
                                                    "result": [source[2], source[0]]}))

    def test_rejects_untyped_predicates_and_unsafe_vocabulary(self):
        for predicate in ({"field": {"of": {"var": "task"}, "name": "missing"}},
                          {"contains": {"element": {"literal": "HIGH"},
                                        "collection": {"var": "tasks"}}},
                          {"lambda": "eval(x)"}):
            with self.subTest(predicate=predicate):
                doc = copy.deepcopy(self.doc)
                doc["rules"][0]["selection"]["predicate"] = predicate
                with self.assertRaises(FormatError):
                    selection.validate(doc)

    def test_rejects_invalid_result_and_witness_types(self):
        doc = copy.deepcopy(self.doc)
        doc["rules"][0]["selection"]["result"] = {"literal": "a"}
        with self.assertRaises(FormatError):
            selection.validate(doc)
        doc = copy.deepcopy(self.doc)
        doc["rules"][0]["cases"][0]["bindings"]["result"] = ["HIGH"]
        with self.assertRaises(FormatError):
            selection.validate(doc)


if __name__ == "__main__":
    unittest.main()
