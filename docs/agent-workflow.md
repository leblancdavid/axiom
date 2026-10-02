# Working on Lykoi: agent guide

This guide is project governance for agents working in the repository. Start
with [the project overview](project-overview.md); it describes the research
goal and the current boundary. `AGENTS.md` is the short entry point. For an
experiment, its frozen protocol and evidence govern that experiment; this guide
does not retroactively amend them or authorize a new run.

## Orient before editing

1. Read `AGENTS.md`, `README.md` and `docs/project-overview.md`. Check
   `git status` and inspect relevant local changes before editing; do not
   overwrite another person's in-progress work.
2. Identify the task's scope: application model, language/compiler, research
   documentation, benchmark preparation, frozen track execution, or prospective
   protocol work. Do not carry a change from one scope into another implicitly.
3. Read the governing sources for that scope. Use `docs/axiom-v0.3.md` and
   `schema/axiom-v0.3.schema.json` for current model semantics; earlier versioned
   docs are historical. Use `benchmark/README.md`, the applicable frozen
   requirement, and the relevant `benchmark/results/` protocol and checkpoint
   for benchmark work. An overview cannot replace a versioned freeze record.
4. State whether a claim is implemented behavior, an observation, a design
   proposal or an unverified hypothesis. Keep evidence and denominators with
   empirical claims. Passing validation or tests does not prove generality,
   safety, semantic equivalence or a comparative advantage.

## Repository map and normal development

| Location | Role |
| --- | --- |
| `air/task_manager.json` | Canonical Lykoi task-manager model; `air` is a compatibility path. |
| `schema/`, `src/air_compiler/` | Serialized shapes, validator, semantic tooling and current Python backend. Changing semantic vocabulary requires general semantics, validation, backend work, documentation and relevant tests. |
| `generated/` | Disposable generated implementation and manifest. Regenerate from the model; never hand-edit. |
| `tests/` | Language/compiler and application tests. |
| `docs/` and `experiments/` | Versioned semantics, decisions, research observations and pinned earlier experiments. Do not reapply a stale hash-pinned plan to a newer model. |
| `benchmark/requirements/`, `benchmark/harness/`, `benchmark/results/` | Frozen requests, external oracle/tooling, and versioned protocols, checkpoints and evidence. Do not treat the root model as a benchmark track's live workspace. |

From the repository root, for **ordinary non-frozen** model/compiler work with
Python 3.10+ (PowerShell):

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli safety air/task_manager.json
python -m unittest discover -s tests -v
python -m unittest discover -s benchmark/harness -v
```

Use `inspect`, `diff` and `impact` to trace semantic IDs before editing. If the
model is intentionally changed, regenerate normally and verify the generated
artifact and manifest; use a temporary copy when checking a proposed change
that should not modify the repository. Run checks relevant to the change, and
record what actually ran. The commands above are development checks, **not**
the checkpoint restore, external-suite and freeze gates of a benchmark
amendment. Do not run `apply` on an old experiment plan: its pinned baseline is
expected to reject reapplication.

## Language design and research discipline

The research question is whether a small general-purpose semantic vocabulary
can compose complex software reliably. Prefer typed, explicit, reusable
primitives and their composition to a new operation for each application
feature. Before proposing an extension, identify the precise expressiveness
gap, examples beyond the triggering requirement, interactions with existing
semantics, validator/runtime obligations, migration/compatibility costs, and a
way to challenge generality with unseen problems. Do not imitate a host
language's syntax simply to make authoring familiar. A bounded current
implementation does not establish that the eventual language is general.

Move correctness into language semantics, constraints, compiler/runtime
guarantees and validated external-capability adapters where feasible. Keep the
core semantic model separate from integration details such as storage, clocks,
IDs and other external services. Additional adapters are a direction to
investigate, not a claim that today's backend enforces isolation or provides
formal proof. Tests are essential for the language, compiler/runtime,
adapters, intent interpretation and independent evaluation; they are not the
semantic target for generated application behavior.

## Benchmark firewall

Phase 5C compares Conventional source maintenance with a **frozen** Lykoi
capability set on cumulative B01–B20 requests. Observable satisfaction of the
frozen requirement is the criterion, not identical code, names, algorithms or
representation. Derive implementation from the requirement and permitted
context; independently verify with external acceptance tests. Do not use
hidden oracle details to drive implementation unless the governing protocol
explicitly allows them. Do not rewrite a requirement, test, frozen tool,
checkpoint or old classification to improve an outcome.

During a frozen track run, do not extend Lykoi's compiler, schema or runtime to
pass a newly encountered request. Record an evidenced capability gap when the
frozen semantic vocabulary cannot express it (historical records call this
`AXIOM_CAPABILITY_GAP`; newer conventions may say `LYKOI_CAPABILITY_GAP`).
Distinguish this from a failed implementation within the existing vocabulary.
Use `BLOCKED_BY_GAP` only when the later request actually depends on the
missing prerequisite; an earlier gap alone does not block every later task.
Preserve the achieved history and report applicable external checks, skips and
regressions separately. Protocol defects are not language capability defects.
Benchmark agents must follow the frozen track instructions and isolation
rules; this repository-wide context is not permission to disclose the other
track's solution or hidden acceptance details inside an isolated run.

The authoritative corrected post-B16 acceptance boundary is R5.2.2. R5.3 is
prospective assertion-level reconstruction, not a frozen equivalence proof;
B17 remains unexposed. Follow the current boundary in
`docs/project-overview.md` and the versioned records under
`benchmark/results/phase5c/` before touching this area. Preserve frozen
inputs and historical results. Record corrections as prospective, separately
versioned evidence, with provenance and independent checks before any claimed
freeze. Governance edits do not advance the benchmark.

## After a benchmark and keeping this guide current

Once a frozen suite actually completes, collect gaps, group them by semantic
cause, propose the smallest abstractions that address multiple gaps, evolve a
new version separately, rerun the original suite under a controlled protocol
and evaluate on new unseen domains. B01–B20 can remain a stable diagnostic
suite, but repeated success on the same task manager cannot establish
generality. Structured semantic requirements from which executable acceptance
can be derived are a *future proposal*, not today's oracle; avoid having to
reverse-engineer requirements from Python test bodies again.

Update `AGENTS.md` when entry-point rules change, this guide when work
procedures change, and `docs/project-overview.md` when direction, milestones or
current boundary changes. Put observations and limitations in
`docs/research-log.md`, design tradeoffs in `docs/decisions.md`, and language
semantics in the relevant versioned doc. Benchmark-specific findings belong
beside their evidence under `benchmark/results/`, without editing frozen
history. Check README links and status claims in the same change. A future
agent should be able to tell *what is known, what is proposed, and what remains
unverified* from these documents without assuming passing tests imply proof.
