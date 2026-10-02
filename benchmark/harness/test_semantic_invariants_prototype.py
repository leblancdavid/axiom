"""Prospective invariant-format fixtures, not an application acceptance oracle."""

import copy
import json
from pathlib import Path
import unittest

from benchmark.semantic import invariants
from benchmark.semantic.format import FormatError


FIXTURE = Path(__file__).resolve().parents[1] / "semantic" / "invariant-fixtures.json"


class InvariantFormat(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_witnesses_are_linked_and_satisfied(self):
        results = invariants.run_witnesses(self.doc)
        self.assertEqual(len(results), 12)
        self.assertTrue(all(applicable and holds for applicable, holds in results.values()))

    def test_rules_are_not_defined_by_witness_enumeration(self):
        rule = self.doc["invariants"][0]
        self.assertEqual(rule["scope"]["domain"], "finite_sequence")
        self.assertTrue(invariants.evaluate(rule["property"],
                      {"input": ["new", " NEW ", "new", " x ", "NEW"],
                       "output": ["new", "NEW", "x"]}))
        self.assertFalse(invariants.evaluate(rule["property"],
                       {"input": ["new", " NEW ", "new"], "output": ["new"]}))
        graph = self.doc["invariants"][2]
        env = {"before": {"nodes": ["p", "q", "r", "s", "t"],
                          "edges": [["p", "q"], ["q", "r"], ["r", "s"], ["s", "t"]]},
               "after": None, "source": "t", "target": "p", "accepted": False}
        env["after"] = env["before"]
        self.assertTrue(invariants.evaluate(graph["precondition"], env))
        self.assertTrue(invariants.evaluate(graph["property"], env))
        self.assertTrue(invariants.evaluate({"equals": [{"var": "left"},
                                                       {"var": "right"}]},
                      {"left": {"nodes": ["p", "q"], "edges": [["p", "q"]]},
                       "right": {"nodes": ["q", "p"], "edges": [["p", "q"]]}}))

    def test_unknown_types_variables_operations_and_graphs_fail_closed(self):
        mutations = (
            (0, "bindings", "unknown type", lambda r: r["bindings"].update(input="python")),
            (0, "property", "undeclared variable", lambda r: r.update(property={"var": "missing"})),
            (0, "property", "invalid collection operation", lambda r: r.update(
                property={"map": {"sequence": {"var": "input"}, "transform": "eval"}})),
            (0, "property", "invalid comparison", lambda r: r.update(
                property={"stable_unique": {"sequence": {"var": "input"},
                                             "equality": "case_insensitive"}})),
            (2, "property", "invalid graph expression", lambda r: r.update(
                property={"add_edge": {"graph": {"var": "before"}, "from": {"var": "source"}}})),
            (0, "precondition", "malformed quantifier scope", lambda r: r.update(
                precondition={"for_each": {"sequence": {"var": "input"}}})),
        )
        for index, _, message, mutate in mutations:
            with self.subTest(message=message):
                doc = copy.deepcopy(self.doc)
                mutate(doc["invariants"][index])
                with self.assertRaisesRegex(FormatError, message):
                    invariants.validate(doc)

    def test_references_and_witness_bindings_fail_closed(self):
        changes = (
            (lambda d: d["invariants"][0]["depends_on"].append("missing"), "unknown"),
            (lambda d: d["invariants"][0]["witnesses"][0].update(case="missing"), "unknown semantic witness"),
            (lambda d: d["scenarios"][1]["cases"][0]["bindings"]["before"]["edges"].append(["a", "missing"]), "invalid witness bindings"),
            (lambda d: d["invariants"][0]["transition"].update(before="output_missing"), "invalid transition"),
        )
        for change, message in changes:
            with self.subTest(message=message):
                doc = copy.deepcopy(self.doc)
                change(doc)
                with self.assertRaisesRegex(FormatError, message):
                    invariants.validate(doc)

    def test_incorrect_witness_is_not_accepted_as_evidence(self):
        self.doc["scenarios"][0]["cases"][3]["bindings"]["output"] = ["a", "b"]
        outcomes = invariants.run_witnesses(self.doc)
        self.assertEqual(outcomes[("B02.ordered_normalization", "B02.collection",
                                   "B02.repeated")], (True, False))


if __name__ == "__main__":
    unittest.main()
