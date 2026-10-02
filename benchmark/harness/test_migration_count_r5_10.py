"""Synthetic count/selection/transition tuples; no B01 executable is invoked."""

import unittest

from benchmark.semantic import cardinality, selection, state_relations
from benchmark.semantic.format import FormatError


ELEMENT = {"id": "string", "priority": "string"}
COUNT = {"element": ELEMENT, "optional": ["priority"],
         "fields": {"migrated": "integer"}}
DEFAULT = {"schema": ELEMENT, "relation": {"kind": "default_missing",
           "identity": "id", "field": "priority", "value": "NORMAL"}}
SELECT = {"id": "legacy_population", "origin": "B01", "depends_on": [],
          "records": {"Task": ELEMENT},
          "bindings": {"rows": "sequence[Task]", "candidates": "sequence[Task]",
                       "legacy": "boolean"},
          "selection": {"source": {"var": "rows"}, "bind": "task",
                        "predicate": {"var": "legacy"},
                        "result": {"var": "candidates"},
                        "ordering": "source_relative", "exactness": "exact"},
          "cases": [{"id": "type_probe", "bindings": {
              "rows": [], "candidates": [], "legacy": True}, "holds": True}]}


def migration_tuple(pre, candidates, post, outcome, *, legacy=True):
    """One synthetic #45 tuple: pre, selected population, post, typed result."""
    selected = selection.evaluate(SELECT, {"rows": pre, "candidates": candidates,
                                           "legacy": legacy})
    transition = (state_relations.evaluate(DEFAULT, {"before": pre, "after": post})
                  if legacy else pre == post)
    return (selected and transition and outcome["kind"] == "success" and
            cardinality.evaluate(COUNT, candidates, outcome["value"], "migrated"))


class MigrationCountR510(unittest.TestCase):
    def test_typed_general_relation(self):
        self.assertTrue(cardinality.evaluate(
            {"element": "string", "optional": [],
             "fields": {"size": "integer", "label": "string"}},
            ["a", "a"], {"size": 2, "label": "repeated"}, "size"))
        self.assertFalse(cardinality.evaluate(COUNT, [], {"migrated": -1}, "migrated"))
        for bad in (True, 1.0, "1"):
            with self.subTest(bad=bad), self.assertRaises(FormatError):
                cardinality.evaluate(COUNT, [], {"migrated": bad}, "migrated")
        with self.assertRaises(FormatError):
            cardinality.validate({**COUNT, "optional": [[]]})

    def test_arbitrary_legacy_population(self):
        selection.validate({"status": "prototype", "rules": [SELECT]})
        for n in (0, 1, 4, 17):
            with self.subTest(n=n):
                pre = [{"id": str(i)} if i % 2 == 0 else
                       {"id": str(i), "priority": "HIGH"} for i in range(n)]
                post = [{**row, "priority": row.get("priority", "NORMAL")}
                        for row in pre]
                outcome = {"kind": "success", "value": {"migrated": n}}
                self.assertTrue(migration_tuple(pre, pre, post, outcome))
                self.assertFalse(migration_tuple(
                    pre, pre, post, {"kind": "success", "value": {"migrated": n + 1}}))
                if n:
                    self.assertFalse(migration_tuple(pre, pre[:-1], post, outcome))

    def test_non_candidates_and_current_version(self):
        # Priority already present does not remove a v2 row from the migrated set.
        pre = [{"id": "low", "priority": "LOW"},
               {"id": "high", "priority": "HIGH"}]
        self.assertTrue(migration_tuple(pre, pre, pre,
                        {"kind": "success", "value": {"migrated": 2}}))
        self.assertTrue(migration_tuple(pre, [], pre,
                        {"kind": "success", "value": {"migrated": 0}}, legacy=False))
        self.assertFalse(migration_tuple(pre, [], pre,
                         {"kind": "success", "value": {"migrated": 2}}, legacy=False))
        self.assertFalse(migration_tuple(pre, pre, pre,
                         {"kind": "error", "value": {"migrated": 2}}))

    def test_general_filtered_population_excludes_non_candidates(self):
        # Unrelated selection pressure: candidate predicate varies per record.
        rows = [{"id": "a", "eligible": True},
                {"id": "b", "eligible": False},
                {"id": "c", "eligible": True}]
        selected = [rows[0], rows[2]]
        rule = {**SELECT, "records": {"Item": {"id": "string", "eligible": "boolean"}},
                "bindings": {"rows": "sequence[Item]", "candidates": "sequence[Item]"},
                "selection": {**SELECT["selection"],
                              "predicate": {"field": {"of": {"var": "task"},
                                                      "name": "eligible"}}},
                "cases": [{"id": "type_probe", "bindings": {
                    "rows": [], "candidates": []}, "holds": True}]}
        selection.validate({"status": "prototype", "rules": [rule]})
        self.assertTrue(selection.evaluate(rule, {"rows": rows, "candidates": selected}))
        relation = {"element": rule["records"]["Item"], "optional": [],
                    "fields": {"size": "integer"}}
        self.assertTrue(cardinality.evaluate(relation, selected, {"size": 2}, "size"))
        self.assertFalse(cardinality.evaluate(relation, selected, {"size": 3}, "size"))


if __name__ == "__main__":
    unittest.main()
