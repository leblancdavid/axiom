"""Finite witnesses and malformed-rule checks for the unfrozen state prototype."""

import json
from pathlib import Path
import unittest

from benchmark.semantic import state_relations
from benchmark.semantic.format import FormatError


FIXTURES = Path(__file__).resolve().parents[1] / "semantic" / "state-relation-fixtures.json"


class StateRelations(unittest.TestCase):
    def test_witnesses(self):
        document = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual(document["status"], "prototype")
        for entry in document["rules"]:
            with self.subTest(entry=entry["id"]):
                self.assertEqual(state_relations.run_witnesses(entry["rule"]),
                                 {case["id"]: case["holds"] for case in entry["rule"]["cases"]})

    def test_malformed_key_and_default_rejected(self):
        document = json.loads(FIXTURES.read_text(encoding="utf-8"))
        ordering, migration = (entry["rule"] for entry in document["rules"])
        ordering["relation"]["keys"] = ["unknown"]
        migration["relation"]["value"] = False
        for rule in (ordering, migration):
            with self.subTest(kind=rule["relation"]["kind"]), self.assertRaises(FormatError):
                state_relations.validate(rule)
