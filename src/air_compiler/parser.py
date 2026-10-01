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
        raise AirError("Lykoi root must be an object")
    if "axiom_version" not in document and "air_version" not in document:
        raise AirError("missing required Lykoi version")
    if "axiom_version" in document and "errors" not in document:
        raise AirError("missing required Lykoi field: errors")
    for key in ("application", "types", "capabilities", "state", "invariants", "behaviors", "commands"):
        if key not in document:
            raise AirError(f"missing required Lykoi field: {key}")
    if document.get("axiom_version") == "0.3":
        for key in ("state_machines", "transitions"):
            if key not in document:
                raise AirError(f"missing required Lykoi field: {key}")
    return Program(document)


def load(path: str | Path) -> Program:
    return parse(Path(path).read_text(encoding="utf-8"))
