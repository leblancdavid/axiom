from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Program:
    """Parsed AIR semantic entities; validation precedes code generation."""

    document: dict[str, Any]

    def entities(self, group: str) -> list[dict[str, Any]]:
        return self.document[group]
