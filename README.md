# Axiom: AI Intermediate Representation (AIR)

AIR, not Python, is the task manager's source of truth. See
[`air/task_manager.json`](air/task_manager.json) for the complete application,
[`docs/air-v0.1.md`](docs/air-v0.1.md) for its semantics, and
[`docs/decisions.md`](docs/decisions.md) for research tradeoffs.

Requires Python 3.10+; no third-party dependencies. From the repository root:

```sh
PYTHONPATH=src python -m air_compiler.cli validate air/task_manager.json
PYTHONPATH=src python -m air_compiler.cli generate air/task_manager.json generated/task_manager.py
python -m unittest discover -s tests -v
python generated/task_manager.py create --title 'Example' --description 'Try AIR'
python generated/task_manager.py list
python generated/task_manager.py complete --id <id-from-create>
python generated/task_manager.py delete --id <id-from-create>
```

In PowerShell, replace `PYTHONPATH=src` with `$env:PYTHONPATH='src';`.
The CLI stores `tasks.json` in its current working directory; run it from an
isolated directory to keep demonstration data out of the repository.
Successful commands print JSON. Declared failures print `{"error":"code"}`
on stderr and exit 1.

## Repository rule

**Never edit `generated/` application files directly.** Their prominent header
identifies them as generated artifacts. Change AIR, validate, regenerate, then
run the tests. Changes to the representation's semantics belong in the compiler
and require corresponding validation and test updates.

## Modification experiment protocol

For each request, record the changed AIR entity IDs, validate, regenerate,
run both test categories, and report results. Extensions such as priority,
optional due dates, editing rules, and overdue filters are deliberately deferred
until this vertical slice works; they will test where the semantic model needs
an explicit, versioned extension.
