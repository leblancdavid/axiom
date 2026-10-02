# Lykoi: project overview and direction

**The project is named Lykoi, not Axiom.** `axiom` appears in historical
filenames, serialized version keys, benchmark track IDs and pinned research
records; `air/` and `air_compiler` remain compatibility paths. Those names do
not rename the project. Historical evidence retains its original spelling so
that saved models, hashes and checkpoints remain reproducible.

## Long-term goal

Lykoi is an experiment in AI-native programming-language design. Its central
research question is: **what is the smallest general-purpose semantic
vocabulary from which an AI can reliably compose complex software?** The
proposed direction is to distill programming into general, composable,
unambiguous, machine-friendly concepts rather than imitate human-oriented
syntax, assemble code-generation templates, or add a benchmark-specific
primitive for each new feature. This is a research hypothesis, not an
established minimum or a claim that the current vocabulary is general-purpose.

The intended architecture is human intent → AI interpretation → Lykoi semantic
representation → validated, compiler-controlled transformation → executable
implementation/runtime → observable behavior. The semantic model, rather
than a generated Python file, is the source of truth. Python is the first
backend, not the definition of the language.

The goal is to make changes easier to reason about and safer to maintain:
identify affected behavior by stable semantic relationships, reject known
invalid states and unauthorized effects before generation, make migrations
explicit, and connect generated artifacts and verification evidence to their
model. Longer term, correctness should move into language semantics,
constraints, compiler/runtime guarantees and validated infrastructure
adapters, so more properties hold by construction rather than by repeatedly
repairing generated application code. Tests remain important for Lykoi's
semantics, compiler/runtime, adapters, intent interpretation and independent
evaluation; they are not a target to fit. This is a research direction, not
a claim of general correctness or that Lykoi already outperforms conventional
programming. The current language supports a bounded task-management domain;
broader operations, stronger verification, more precise provenance and other
backends require further language and compiler work. Core semantics and
external resources such as storage, time and IDs should remain distinguishable.

## Work completed

- **Semantic foundation (v0.1–v0.3).** A task-manager model now represents
  types, states, behaviors, commands, capabilities, contracts, invariants,
  migrations, lifecycle transitions and scoped authority. The closed-world
  validator checks cross-references and effect/authority consistency. The
  Python backend generates the task CLI; its generated file is not hand-edited.
  See [v0.2](axiom-v0.2.md) and [v0.3](axiom-v0.3.md) for the language boundary.
- **Maintenance tools and experiments.** `inspect`, `diff` and `impact` expose
  semantic relationships; `plan` and `apply` support hash-pinned, validated
  changes with staged verification and rollback on failure. Priority, explicit
  storage migration and due-date experiments exposed missing language concepts
  and tested reusable extensions. Generated manifests record artifact-level
  provenance. Phase 4 added lifecycle checks, least-authority declarations and
  safety evidence labels. The observations and limitations are in the
  [research log](research-log.md).
- **Comparative benchmark.** Phase 5 established a frozen conventional Python
  baseline, an external behavioral oracle and twenty ordered maintenance
  requests. A pilot and subsequent checkpointed execution tested the two
  tracks; Lykoi has a documented B02 language capability gap. The protocol
  was repaired prospectively to address workspace observer effects, divergent
  achieved feature sets and acceptance-case supersession. The two authoritative
  post-B16 histories are Conventional B01–B16 and Lykoi {B01,B04}; their
  corrected acceptance suites were independently revalidated. These are
  observed benchmark states, **not** a completed twenty-request comparison or
  evidence of a winner. See the [benchmark protocol](../benchmark/README.md)
  and [post-B16 corrected boundary](../benchmark/results/phase5c/R5_2_2-POST-B16-CORRECTED-CONTINUATION.md).

## Current boundary and next steps

The B01–B20 sequence is intended as a cumulative diagnostic: early requests
probe local data/query operations (B01–B05); middle requests increasingly
stress cross-cutting state and relationships (B06–B10), then behavioral rules,
invariants, dependencies and transitions (B11–B15); later requests probe
architectural/stateful concepts such as persistent entities, identity,
ownership, actors, roles, history, recurrence, projects and permissions
(B16–B20). This is a research framing for the frozen requests, not a new
requirement, implementation claim or acceptance criterion.

R5.2.2 is the frozen corrected acceptance boundary after B16. R5.3 is
reconstructing assertion-level semantic roots and replacement lineage across
the two achieved histories. Its inventories are still incomplete: active
conditional, helper, CLI and persistence paths need exhaustive mapping and an
independent semantic comparison. The [latest progress record](../benchmark/results/phase5c/R5_3-RETURNED-FIELD-RESTART-PROGRESS.md)
reports unresolved coverage, so no zero-unexplained-difference certificate or
R5.3 freeze has been established. B17 has not been exposed; B17–B20 are not
completed. R5.3 reconstruction work is prospective, not part of the frozen
boundary.

The immediate research task is to finish the R5.3 coverage and equivalence
gate, revalidate both B16 checkpoints against the finished oracle, and only
then freeze a prospective protocol for later requests. Longer term, complete
the ordered benchmark with honest accounting for capability gaps, dependency
blocks, regressions and measurement limits. The benchmark tests functional
equivalence against frozen requirements, not similarity to Conventional's
source. Its external acceptance tests independently verify behavior; they
must not become the design target for Lykoi's semantic vocabulary. A capability
gap in a frozen run is evidence to preserve, not an invitation to extend that
version mid-run.

After a completed frozen suite, cluster gaps by underlying semantics, propose
small abstractions that address multiple cases, freeze an evolved language
version and compare it under a controlled rerun. Challenge any apparent
generalization on *new, unseen domains*: indefinitely extending the one task
manager cannot demonstrate it. Future benchmarks should explore first-class
structured semantic requirements with acceptance derived from them, rather
than having to infer semantics from Python tests. These are future plans, not
completed benchmark or language capabilities. Passing validation or a safety
report alone is never a behavioral proof. See the [agent workflow](agent-workflow.md)
for the practical change and evidence rules.
