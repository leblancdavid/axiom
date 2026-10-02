"""Case-scoped evaluation, deliberately incapable of claiming universal proof."""

from benchmark.semantic import binding, contracts, observation
from benchmark.semantic.format import require


def evaluate(contract, mapping, record):
    binding.validate(contract, mapping)
    observation.validate(record)
    require(record["boundary"] == mapping["boundary"], "wrong observed boundary")
    values = binding.project(contract, mapping, record)
    return {"contract": contract["operation"], "invocation": record["invocation"],
            "conforms": contracts.evaluate(contract, values),
            "evidence": "observed_execution", "proof_status": "not_established"}
