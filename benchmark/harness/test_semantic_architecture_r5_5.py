"""Responsibility boundaries for the unfrozen R5.5 operation prototype."""

import copy
import json
from pathlib import Path
import unittest

from benchmark.semantic import binding, conformance, contracts, observation, operation_contract
from benchmark.semantic.format import FormatError


FIXTURE = Path(__file__).resolve().parents[1] / "semantic" / "operation-contract-fixtures.json"


class ArchitectureSeparation(unittest.TestCase):
    def setUp(self):
        self.legacy = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.contract = operation_contract.abstract_contract(self.legacy)
        self.mapping = {"operation": self.contract["operation"], "boundary": "adapter:one",
                        "slots": {"input.rows": "input", "pre.records": "pre",
                                  "result": "outcome", "post.records": "post"}}

    def record(self, case, sequence=0):
        values = operation_contract.values(case)
        return {"source": "execution", "boundary": "adapter:one",
                "invocation": case["id"], "sequence": sequence,
                "facts": {fact: values[slot] for slot, fact in self.mapping["slots"].items()}}

    def test_contract_is_independent_and_rejects_location_and_evidence(self):
        contracts.validate(self.contract)
        for extra in ("boundary", "cases", "python_function", "proof_status"):
            invalid = {**self.contract, extra: "not semantic"}
            with self.subTest(extra=extra), self.assertRaises(FormatError):
                contracts.validate(invalid)

    def test_binding_references_contract_without_checks(self):
        binding.validate(self.contract, self.mapping)
        for change in ({"checks": self.contract["checks"]},
                       {"operation": "other"}):
            with self.assertRaises(FormatError):
                binding.validate(self.contract, {**self.mapping, **change})

    def test_fixtures_remain_supplied_tuples_not_execution_traces(self):
        self.assertEqual(operation_contract.run_witnesses(self.legacy),
                         {case["id"]: case["holds"] for case in self.legacy["cases"]})
        with self.assertRaises(FormatError):
            observation.validate(self.legacy["cases"][0])

    def test_observation_cannot_specify_requirements_or_claim_proof(self):
        record = self.record(self.legacy["cases"][0])
        observation.validate(record)
        for extra in ("checks", "holds", "proof_status"):
            with self.subTest(extra=extra), self.assertRaises(FormatError):
                observation.validate({**record, extra: True})

    def test_conformance_is_case_scoped_even_for_passing_execution(self):
        for case in self.legacy["cases"]:
            record = self.record(case)
            result = conformance.evaluate(self.contract, self.mapping, record)
            self.assertEqual(result["conforms"], case["holds"])
            self.assertEqual(result["proof_status"], "not_established")
            self.assertEqual(result["evidence"], "observed_execution")
        wrong = self.record(self.legacy["cases"][0])
        wrong["boundary"] = "other"
        with self.assertRaises(FormatError):
            conformance.evaluate(self.contract, self.mapping, wrong)

    def test_failure_does_not_change_contract_and_trace_requires_continuity(self):
        original = copy.deepcopy(self.contract)
        first = self.record(self.legacy["cases"][0])
        second = self.record(self.legacy["cases"][2], 1)
        with self.assertRaises(FormatError):
            observation.validate_trace([first, second])
        second["facts"]["pre"] = first["facts"]["post"]
        observation.validate_trace([first, second])
        self.assertFalse(conformance.evaluate(self.contract, self.mapping, second)["conforms"])
        self.assertEqual(self.contract, original)


if __name__ == "__main__":
    unittest.main()
