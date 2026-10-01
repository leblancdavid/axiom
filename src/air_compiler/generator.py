"""Deterministic Python backend; never edits an existing generated file by hand."""

import json
from pathlib import Path

from .model import Program
from .validator import validate


HEADER = "# THIS FILE IS GENERATED.\n# DO NOT MODIFY DIRECTLY.\n# MODIFY THE AIR REPRESENTATION INSTEAD.\n"
MARKER = "SPEC = {}  # AIR_SPEC_INSERTION_POINT"


def generate(program: Program) -> str:
    validate(program)
    template = Path(__file__).with_name("runtime_template.py").read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        raise RuntimeError("Python backend template is missing its AIR insertion point")
    canonical = json.dumps(program.document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return HEADER + template.replace(MARKER, f"SPEC = json.loads({canonical!r})")


def write(program: Program, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate(program), encoding="utf-8", newline="\n")
