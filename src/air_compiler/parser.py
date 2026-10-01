import json
from pathlib import Path

from .model import Program


class AirError(ValueError):
    pass


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AirError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse(text: str) -> Program:
    try:
        document = json.loads(text, object_pairs_hook=_unique_pairs)
    except json.JSONDecodeError as exc:
        raise AirError(f"invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise AirError("AIR root must be an object")
    for key in ("air_version", "application", "types", "capabilities", "state", "invariants", "behaviors", "commands"):
        if key not in document:
            raise AirError(f"missing required AIR field: {key}")
    return Program(document)


def load(path: str | Path) -> Program:
    return parse(Path(path).read_text(encoding="utf-8"))
