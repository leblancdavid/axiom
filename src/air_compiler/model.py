from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Program:
    """Parsed Lykoi document; validation precedes semantic indexing or generation."""

    document: dict[str, Any]

    def entities(self, group: str) -> list[dict[str, Any]]:
        return self.document[group]

    @property
    def version(self) -> str:
        return self.document.get("axiom_version", self.document.get("air_version", ""))
