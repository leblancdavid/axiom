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

R5.2.2 is the frozen corrected acceptance boundary after B16. Exhaustive R5.3
Python-test reconstruction has stopped as a prerequisite for later requests;
its [latest worksheet](../benchmark/results/phase5c/R5_3-BULK-RECONCILIATION-WORKSHEET-PROGRESS.md)
and unresolved coverage remain preserved, not certified equivalent. The
[bounded-bridge decision](../benchmark/results/phase5c/R5_4-BOUNDED-BRIDGE-DECISION.md)
authorizes a prospective semantic-requirement prototype and targeted
historical-carrier preservation against R5.2.2. It is not a new oracle freeze.
B17 has not been exposed; B17–B20 are not completed.

Selected B01/B11/B14/B16 scenarios now have
[prototype witnesses](../benchmark/results/phase5c/R5_4-SEMANTIC-PROTOTYPE-PROGRESS.md)
on pinned post-B16 snapshots; this does not cover all frozen clauses. The
[format adequacy review](../benchmark/results/phase5c/R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md)
stopped before schema freeze. Experimental typed UTC-clock and checked
requirement-relationship fixtures now address those vocabulary gaps, but the
[B17 frozen-text dependency review](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION-HALT.md)
finds independently observable missing-actor behavior alongside B16-dependent
role/owner authorization. The
[prospective adjudication](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md)
keeps Phase 5C request-level: a track missing B16 is blocked on B17 as a whole,
while independently observable clauses may have **separate diagnostic evidence**
without partial achievement. Next: checked clause dependencies and separate
diagnostics, controlled application-clock binding, B01–B16 format adequacy,
the bounded bridge and independently verified B16 checkpoints before any
B17-ready freeze or exposure.
The [adequacy restart](../benchmark/results/phase5c/R5_4-SEMANTIC-ADEQUACY-RESTART-HALT.md)
now exercises a controlled UTC subprocess clock on a disposable post-B16
application but **halts at the format gate**: finite scenario observations do
not express B02's general ordered deduplication of arbitrary repeated tags
(nor B14's arbitrary dependency cycles). No semantic schema, clause bridge or
B17-ready protocol has been frozen. The later gates remain pending.
The [invariant prototype restart](../benchmark/results/phase5c/R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md)
now expresses B02 ordered normalization and B14 cycle rules in a separate,
unfrozen typed collection/graph vocabulary with linked finite semantic
fixtures. A fresh B01–B16 frozen-text screen stops at B01: general exact-HIGH
selection across arbitrary tasks is not yet expressible (B03 adds membership
selection). The adequacy
gate remains halted; no CLI acceptance bridge or later B17 gate has advanced.
The [selection restart](../benchmark/results/phase5c/R5_4-SELECTION-ADEQUACY-RESTART-HALT.md)
now states exact ordered selection for B01/B03 using the same general typed
relation, with [explicit vocabulary counts](../benchmark/results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md).
The fresh screen still halts at B01: normal-order binding and arbitrary
old-task field preservation/default on migration remain unexpressed. This
prototype is unfrozen and does not advance the bridge or B17.
The [B01 order/transition restart](../benchmark/results/phase5c/R5_4-B01-ORDER-TRANSITION-ADEQUACY-HALT.md)
now prototypes typed ascending normal order and keyed migration/default
preservation. B01 remains inadequate: rules over supplied collections are not
yet bound universally to create/list/migrate commands and persistent state;
the meaning of priority rank also needs adjudication. The adequacy gate stays
at B01 and the semantic format remains unfrozen.
The [operation-contract investigation](../benchmark/results/phase5c/R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md)
finds one plausible generic binder over invocation, pre-state, result and
post-state, reused by existing relations. Its synthetic typed-tuple witnesses
are not universally bound to public calls/storage; B01 remains inadequate,
and priority “above HIGH” has no established observable rank comparison.
The unfrozen ledger counts 45 provisional constructs. No later adequacy gate
has advanced.
The [architectural checkpoint](../benchmark/results/phase5c/R5_4-SEMANTIC-ARCHITECTURE-CHECKPOINT.md)
pauses the B01 repair loop: abstract operation contracts appear reusable, but
the proposed #45 binder conflates the contract with interface mapping, actual
execution observation and conformance/proof. The 45-entry prototype inventory
contains 29 candidate core semantic constructs after separating finite evidence
and benchmark administration; this is not a language freeze or an adequacy
result. A checked static interface/state binding plus independent observed
traces is the next *design hypothesis*, not an implemented capability. B01
remains inadequate and halted, R5.2.2 authoritative, the format unfrozen,
Phase 5C paused, and B17 unexposed and unclassified.
The [R5.5 architecture revision](../benchmark/results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md)
now physically separates the provisional #45 abstract relation, checked slot
metadata, execution-record shape and case-scoped verifier. Historical synthetic
fixtures remain synthetic; no actual-call/storage binding or observer fidelity
has been established. The inventory remains 45 raw and 29 candidate core
constructs with observation, verification, evidence and lineage accounted for
separately. R5.5 is **partial**, not an adequacy restart: B01 stays halted and
inadequate, R5.2.2 authoritative, format unfrozen, Phase 5C paused and B17
unexposed and unclassified.
Longer term, complete the ordered benchmark with
honest accounting for capability gaps, dependency
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
manager cannot demonstrate it. The prospective B17–B20 protocol will explore
first-class structured semantic requirements with acceptance derived from
them, rather than inferring semantics from Python tests. This is a research
direction, not an established benchmark or language capability. Passing
validation or a safety report alone is never a behavioral proof. See the
[agent workflow](agent-workflow.md)
for the practical change and evidence rules.
