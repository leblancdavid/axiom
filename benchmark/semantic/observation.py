"""Concrete invocation facts; an observer's fidelity is an external obligation."""

from benchmark.semantic.format import require


FACTS = frozenset(("input", "pre", "outcome", "post"))


def validate(record):
    require(isinstance(record, dict) and set(record) ==
            {"source", "boundary", "invocation", "sequence", "facts"} and
            record["source"] == "execution" and
            isinstance(record["boundary"], str) and record["boundary"] and
            isinstance(record["invocation"], str) and record["invocation"] and
            type(record["sequence"]) is int and record["sequence"] >= 0 and
            isinstance(record["facts"], dict) and set(record["facts"]) == FACTS,
            "incomplete execution observation")
    return record


def validate_trace(records):
    require(isinstance(records, list) and records, "empty trace")
    for index, record in enumerate(records):
        validate(record)
        require(record["sequence"] == index and
                (index == 0 or (record["boundary"] == records[index - 1]["boundary"] and
                                record["facts"]["pre"] == records[index - 1]["facts"]["post"])),
                "discontinuous trace")
    return records
