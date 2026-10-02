# Agent guidance for Lykoi

The project is **Lykoi**, not Axiom. Historical `axiom` and `air` paths and
identifiers remain for compatibility and reproducible research records.

## Start here

Read `docs/project-overview.md` for the research question, long-term direction
and current boundary, then `docs/agent-workflow.md` for the repository map,
change procedures, verification and benchmark rules. Read the applicable
versioned language spec or benchmark protocol *before* editing those areas.
Check `git status` first: existing changes may be another person's work.

Lykoi seeks a small, general, composable semantic vocabulary for AI-authored
software, not a task-manager DSL or an implementation tuned to benchmark tests.
The model is canonical; generated Python is disposable. Do not edit
`generated/` directly. The benchmark compares observable functional behavior,
not source-code similarity. External acceptance tests verify requirements;
they do not define new language semantics.

For frozen benchmark work, preserve frozen language/compiler/runtime/schema,
requirements, oracles, checkpoint evidence and historical classifications.
Record genuine capability gaps instead of adding case-specific primitives;
distinguish gaps from implementation failures and downstream dependency blocks.
Use independently versioned prospective work for protocol or language proposals.
The current R5.3 acceptance reconstruction is unfrozen; do not treat it as an
authorization to expose B17 or change the authoritative R5.2.2 boundary.

## Keep documentation current

As you discover a new paradigm, concept, capability gap, design tradeoff or
empirical learning while working on Lykoi, document it in the same change.
Explain what was learned, the evidence or motivating example, the current
boundary, and what it implies for future work. Distinguish implemented behavior
from proposals and unverified hypotheses; do not claim proof from validation or
passing tests alone.

- Update `docs/project-overview.md` when the long-term direction, major
  milestones or current research boundary changes.
- Record experimental observations and limitations in `docs/research-log.md`,
  design tradeoffs in `docs/decisions.md`, and language semantics in the
  appropriate versioned document under `docs/`.
- Record benchmark-specific findings and protocol changes alongside their
  evidence under `benchmark/results/`. Preserve frozen requirements, oracle
  inputs and historical records; use prospective records for corrections.
- Update README links and status summaries when their descriptions become
  outdated. Use **Lykoi** in new prose while retaining historical names in
  citations, file paths and pinned identifiers.
