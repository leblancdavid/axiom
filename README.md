# Lykoi

Lykoi is an AI-native semantic representation for software. This experimental
software-development system is designed around AI authorship: an AI maintains a
semantic model of a software system, validates its relationships and contracts,
and generates disposable implementation artifacts. The model, not Python, is
the source of truth. Python is the first backend, not the definition of Lykoi.

Lykoi (pronounced “lie-KOY”) is named after the Lykoi cat breed. Its central
question is: what should software look like when AI, rather than humans, is the
primary programmer? Human intent leads to an AI-authored Lykoi semantic model,
then validation, lowering and generation, and finally an executable system.

For the work to date, current research boundary and long-term goal, see
[`docs/project-overview.md`](docs/project-overview.md). The project is **Lykoi,
not Axiom**; historical `axiom` names are retained only for compatibility and
reproducible research records.

Contributors and AI agents should start with [`AGENTS.md`](AGENTS.md) and the
[agent workflow](docs/agent-workflow.md) before changing the model, compiler or
benchmark.

The task application lives in [`air/task_manager.json`](air/task_manager.json)
(the `air/` path and `air_compiler` import path are retained for compatibility).
The current v0.3 model is documented in [`docs/axiom-v0.3.md`](docs/axiom-v0.3.md),
its JSON envelope in [`schema/axiom-v0.3.schema.json`](schema/axiom-v0.3.schema.json),
and the experiment in [`docs/research-log.md`](docs/research-log.md).
The historical v0.1 semantics are preserved in [`docs/air-v0.1.md`](docs/air-v0.1.md).
Existing `air/`, `air_compiler`, `axiom_version`, and schema paths remain stable
compatibility interfaces for saved models and research artifacts.

Phase 5's comparative-maintenance setup, conventional Python baseline,
external behavioral oracle, twenty sequential requests and execution records
are in [`benchmark/`](benchmark/README.md). The benchmark is in progress:
post-B16 histories have been revalidated against the corrected oracle, while
R5.3 acceptance reconstruction remains unfrozen and B17 is unexposed.

Python 3.10+; no third-party dependencies. In PowerShell from the repository root:

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli generate air/task_manager.json generated/task_manager.py
python -m air_compiler.cli inspect air/task_manager.json field_priority
python -m air_compiler.cli diff experiments/task_manager-v0.2-before-priority.json air/task_manager.json
python -m air_compiler.cli impact air/task_manager.json field_due_date --manifest generated/task_manager.manifest.json
python -m air_compiler.cli safety air/task_manager.json
python -m air_compiler.cli plan experiments/phase3-due-dates.plan.json
python -m unittest discover -s tests -v
```

The Phase 3 experiment plan is pinned to the **pre-change** model. After it has
been applied, its baseline hash deliberately prevents reapplication; consult
`experiments/phase3-prechange-impact.json` and
`experiments/phase3-impact-comparison.json` for the saved predictions and
outcome. On a matching baseline, `python -m air_compiler.cli apply PLAN` stages
the model and generated artifact, verifies them and rolls back on failure.

Run the application from a separate working directory: it stores `tasks.json`
in that directory. The generated artifact offers `create --title T --description
D [--priority LOW|NORMAL|HIGH] [--due-date UTC_TIMESTAMP]`, `list`, `list-high`,
`list-overdue`, `complete --id ID`,
`delete --id ID`, and `migrate`. Omitted priority defaults to `NORMAL`. An old
task file must be upgraded with `migrate` before other commands will read it;
this is an explicit, atomic schema migration. Overdue means pending with a
non-null due date strictly before the current UTC time.

**Never edit files under `generated/` directly.** Change the Lykoi model,
validate, regenerate, and verify the behavior. `generated/task_manager.manifest.json`
records provenance and the artifact hash. Changing Lykoi's semantic vocabulary
requires a compiler/backend change, a documented capability gap, and tests.

**Intent may be probabilistic. Program semantics should not be.**

**If the system knows an operation is invalid, it should be impossible for an AI-generated change to silently introduce it. Behaviors should possess the minimum authority necessary to perform their declared semantics.**
