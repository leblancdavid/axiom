"""Checked, target-neutral slot locations; never a behavior specification."""

from benchmark.semantic.format import require
from benchmark.semantic import contracts


FACTS = frozenset(("input", "pre", "outcome", "post"))


def validate(contract, binding):
    contracts.validate(contract)
    require(isinstance(binding, dict) and set(binding) ==
            {"operation", "boundary", "slots"} and
            binding["operation"] == contract["operation"] and
            isinstance(binding["boundary"], str) and binding["boundary"] and
            isinstance(binding["slots"], dict) and
            set(binding["slots"]) == contracts.SLOTS and
            set(binding["slots"].values()) == FACTS,
            "invalid operation binding")
    return binding


def project(contract, binding, record):
    validate(contract, binding)
    return contracts.validate_values(contract, {
        slot: record["facts"][fact] for slot, fact in binding["slots"].items()
    })
