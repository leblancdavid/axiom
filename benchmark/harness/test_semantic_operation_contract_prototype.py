"""Synthetic operation tuples challenge the unfrozen contract binding."""

import json
from pathlib import Path
import unittest

from benchmark.semantic import operation_contract
from benchmark.semantic.format import FormatError


FIXTURES = Path(__file__).resolve().parents[1] / "semantic" / "operation-contract-fixtures.json"


class OperationContracts(unittest.TestCase):
    def test_typed_tuples(self):
        document = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual(operation_contract.run_witnesses(document),
                         {case["id"]: case["holds"] for case in document["cases"]})

    def test_unbound_slot_and_mistyped_state_rejected(self):
        document = json.loads(FIXTURES.read_text(encoding="utf-8"))
        document["checks"][0]["left"] = "unbound.rows"
        with self.assertRaises(FormatError):
            operation_contract.validate(document)
        document["checks"][0]["left"] = "input.rows"
        document["cases"][0]["post"]["records"][0]["flag"] = "false"
        with self.assertRaises(FormatError):
            operation_contract.validate(document)
