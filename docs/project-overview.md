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

The [R5.28 refined-plan consumption checkpoint](../benchmark/results/phase5c/R5_28-REFINED-PLAN-CONSUMPTION-INTEGRATION.md)
adds a source-bound checked plan consumed by a prospective non-task generator
and independent verifier fork. Refined chronological reads and guarded replace/
remove writes each execute, ground and conform; all four disposable faults
ground but fail conformance. Historical R5.23 hash-locked components remain
intact. This is **partial** (`R5_28_REFINED_PIPELINE_INTEGRATION_PARTIAL`):
there is no single generated five-command durable program, read-after-write
closure or independently verified command-to-command continuity, and the actual
pinned general compiler/verifier still does not consume the plan. R5.29 should
version a coherent multi-operation general pipeline before revisiting either
R5.23 type-blocker classification. Core 30, no #31; B02 not retried, Phase 5C
paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical authority,
semantic-first format unfrozen and universal correctness unestablished.

The [R5.27 unified typed pipeline checkpoint](../benchmark/results/phase5c/R5_27-UNIFIED-TYPED-PIPELINE-INTEGRATION.md)
adds a prospective, shared operand analyzer for read and write contracts:
scoped optional presence, order-independent conjunctions, instant keys and
typed state-transition operands. It does **not** yet lower or verify refined
writes, generate a multi-command program or ground R5.27 executions. Gate
`R5_27_UNIFIED_TYPED_PIPELINE_PARTIAL`; R5.23's two type blockers are not yet
resolved in the general pipeline. Finish the independent generated/grounded
integration before the separate suppliedness/well-formedness study. Core 30,
no #31; no B02 retry, Phase 5C paused, B03 untouched, B17 unexposed and
unclassified, R5.2.2 historical authority and format globally unfrozen.

The [R5.26 general type integration study](../benchmark/results/phase5c/R5_26-GENERAL-TYPE-REFINEMENT-INSTANT-INTEGRATION.md)
generates, grounds and semantically checks read-only non-task operations with
scoped `optional<T>` elimination and chronological `instant` ordering, including
`present + before + select + order`. Both independently demonstrated R5.23
type blockers are resolved in this separately versioned profile, **not yet in
the full general operation pipeline**. The gate is
`R5_26_REFINEMENT_INSTANT_INTEGRATION_PARTIAL`: R5.27 should carry this analysis
through writing/mixed-branch operations on new domains, without altering pinned
history. Input validity/typed malformed outcomes, cross-shape migration and
frozen transport binding remain separate. Core 30, no #31, no B02 retry; Phase
5C paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical
authority, format globally unfrozen, universal correctness unestablished.

The [R5.25 optional-presence/refinement review](../benchmark/results/phase5c/R5_25-OPTIONAL-PRESENCE-REFINEMENT-SEMANTIC-REVIEW.md)
chooses `EXISTING_TYPE_SYSTEM_GENERALIZATION`: optional state-row presence is
already defined by typed record membership; a scoped type-elimination witness
lets an existing predicate consume the present value without adding a new core
relation. A separate publication-domain generator checks both conjunction
orders and four absent/before/after/equal witnesses, with a grounded but
nonconforming absent-row fault. This resolves the semantic architecture in a
narrow prototype, **not** the pinned general compiler's integration; the R5.23
optional blocker is partially resolved. Core stays 30; R5.26 should integrate
scoped refinement into a separately versioned general checker, generator and
verifier on independent domains. No B02 retry or frozen acceptance, Phase 5C
remains paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historically
authoritative, semantic-first format globally unfrozen, universal correctness
unestablished.

The [R5.24 cross-capability coherence review](../benchmark/results/phase5c/R5_24-CROSS-CAPABILITY-TYPE-STATE-COHERENCE.md)
has **halted at semantic-extension review**, not validated whole-program
coherence. An independent publication-domain interpreter confirms that the
existing typed UTC `instant` admits chronological ordering, but the R5.23-
locked generator still rejects instant keys. An independent generated input
probe preserves omitted versus explicitly supplied values and grounds the
valid cases; malformed input stops before a typed semantic outcome. Existing
construct compositions cannot yet express presence-conditioned refinement of
an optional state-row field; pre/post durable shapes also remain coupled to
one declaration. Historical compiler/runtime/verifier locks remain intact;
the full harness passes 249 tests and the application/compiler suite passes
31. Review whether existing optional semantics and #45 can express the
missing guard before any #31 decision, then develop a separately versioned
coherence pipeline and independent cross-shape/whole-program witnesses.
No B02 retry or candidate was produced. Candidate core remains 30, R5.2.2
historical authority, Phase 5C paused, B03 untouched, B17 unexposed and
unclassified, the semantic-first format globally unfrozen and universal
implementation correctness unestablished.

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
The [R5.6 grounding and trust model](../benchmark/results/phase5c/R5_6-GROUNDING-TRUST-MODEL.md)
recommends compiler-owned operation/persistence boundaries and specific
provenance, challenged by independent public-call and durable-state observation.
This is a ready-to-prototype architecture, **not** an implemented grounded
contract verifier: current records can still self-assert their origin and the
single-artifact manifest cannot attribute an operation. No new semantic
construct or B01 capability was added (45 historical raw, 29 candidate core).
B01 remains inadequate and halted; R5.2.2 authoritative, Phase 5C paused,
B17 unexposed and unclassified, and the semantic-first format unfrozen.
The [R5.7 synthetic grounding implementation](../benchmark/results/phase5c/R5_7-GROUNDING-PROTOTYPE.md)
now generates an isolated operation and per-operation provenance, executes real
subprocess calls, challenges internal records with independently captured public
output and durable file readback, and only then invokes the R5.5 case verifier.
Fault injection distinguishes wrong behavior from false reports and stale
artifacts. It remains **partial**: the 29-candidate contract vocabulary cannot
express conditional typed error classification/no-write obligations; an explicit
adapter policy checks the selected failure case, not semantic conformance alone.
No B01 repair, benchmark activation or format freeze follows. R5.2.2 remains
authoritative, B01 halted/inadequate, Phase 5C paused and B17 unexposed and
unclassified.
The [R5.8 conditional-outcome review](../benchmark/results/phase5c/R5_8-CONDITIONAL-OUTCOME-EXPRESSIVENESS.md)
generalizes the prospective #45 contract to compose typed outcome tags, Boolean
predicates and before/after state relations. The synthetic R5.7 failure now
passes or fails case-scoped semantic conformance after grounding, without the
adapter failure policy. The candidate core count remains 29. This resolves
that narrow semantic gap, not general variant-dependent payload typing or
no-attempted-write proof; B01 remains inadequate and halted, Phase 5C paused,
B17 unexposed and unclassified, R5.2.2 authoritative, format unfrozen.
The [R5.9 B01 end-to-end restart](../benchmark/results/phase5c/R5_9-B01-END-TO-END-ADEQUACY-RESTART.md)
reconstructs the complete frozen B01 contract with its inherited baseline.
Exact selection and ordering suggest a relational insertion/completion frame,
but arbitrary migration count lacks an established typed collection-to-numeric
outcome relation. A checkpoint-pinned B01 executable passes the selected frozen
cases and independent public/durable observations; it does not emit the internal
per-operation event needed to challenge B01 grounding or reach #45 semantic
conformance. This is a **multiple-gap halt** under the 29-candidate ceiling,
not a new construct, universal adequacy or correctness finding. R5.2.2 stays
authoritative, Phase 5C paused, B17 unexposed/unclassified and the format
unfrozen.
The [R5.10 focused migration-count review](../benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md)
adds one general prospective finite-collection cardinality relation (#30):
exact legacy candidate selection can now relate its population to a typed
numeric outcome for arbitrary supplied finite populations. The synthetic
prototype does not integrate a B01 #45 checker or ground B01 execution.
Prospective accounting is 46 raw categorized constructs / 30 candidate core;
the historical 45-entry inventory is retained. B01 remains inadequate and
halted, its R5.7 grounding failed/unestablished, R5.2.2 authoritative, Phase
5C paused, B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.11 B01 instrumented integration](../benchmark/results/phase5c/R5_11-B01-INSTRUMENTED-INTEGRATION.md)
builds a distinct, prospectively generated B01 executable with per-operation
provenance and runtime events. The new executable passes the original frozen
B01 profile (5 passes, 2 B02 skips); actual create, list, list-high, complete
and migration calls have independently challenged public and durable endpoints
and case-scoped conformance. A faithfully reported wrong migration count fails
semantics after grounding, while a false post-state report fails grounding
before semantic evaluation. The 30-candidate abstract vocabulary is adequate
for the observable B01 contract without a #31; the B01-specific checker is not
a general typed #45 compiler, and universal implementation correctness remains
unestablished. The historical executable is unchanged and its old acceptance
is not retroactively grounded. R5.2.2 remains authoritative, Phase 5C paused,
B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.12 POC health gate](../benchmark/results/phase5c/R5_12-POC-HEALTH-GENERAL-LOWERING-GATE.md)
finds that R5.11's B01 implementation and most of its checker were separately
authored Python, while the semantic label index only affected digests. A small
typed, target-neutral **validating** #45 lowerer now checks read-only B01
list/list-high cases and a structurally different synthetic filter/order/count
contract; mutation changes checked outcomes without lowerer edits. No B01
algorithm is generated from that source, and a valid keyed-default combination
remains unsupported. The 30-core candidate and grounding direction remain
plausible, but lowering is **not general enough to scale**: the next step is
bounded generative operation lowering challenged on a non-task domain, before
any further frozen-request execution. R5.2.2 remains authoritative, Phase 5C
paused, B17 unexposed/unclassified, and the semantic-first format unfrozen.
The [R5.13 non-task generative prototype](../benchmark/results/phase5c/R5_13-SEMANTIC-DRIVEN-GENERATIVE-LOWERING.md)
now emits stateful executable predicates, tagged outcomes and bounded keyed
transitions from typed semantic contracts. Value and structural mutations plus
a novel combination change real subprocess/file behavior without lowerer
edits; independent grounding and contract conformance distinguish an injected
lowering fault. This validates a **constrained** generative slice, not B01
generation, arbitrary synthesis or scaling readiness. Keep 30 candidate core
constructs / 46 raw entries, format unfrozen, Phase 5C paused, R5.2.2
historically authoritative and B17 unexposed/unclassified. At the R5.13
checkpoint, B02 had not been resumed.
The [R5.14 controlled B02 pressure test](../benchmark/results/phase5c/R5_14-B02-FROZEN-ARCHITECTURE-PRESSURE.md)
now reconstructs frozen B02 and inherited obligations without adapting that
architecture. Existing candidate relations express ordered tag normalization,
blank rejection and abstract migration/defaults, but R5.13's general generator
cannot emit those compositions or complete task operations. It halts at the
generative-lowering gate: no B02 candidate, acceptance, grounding or conformance
result follows. The old frozen v0.3 B02 capability gap remains historical; this
is a new prospective compiler-boundary finding, not a retroactive repair.
Next: test general lowering of the missing existing relations on independent
non-task examples before any B02 retry. Keep 30 candidates / 46 raw entries,
 format unfrozen, Phase 5C paused after this B02-only pressure test, R5.2.2
 historically authoritative and B17 unexposed/unclassified.
The [R5.15 independent lowering study](../benchmark/results/phase5c/R5_15-GENERAL-LOWERING-COVERAGE-EXPANSION.md)
now generates ordered normalization, typed record outcomes and a bounded keyed
missing-field default on media, device and library domains. Semantic-only
mutations change generated behavior; three new capabilities compose in one
synthetic operation, with grounded executions and a fault that grounds but fails
conformance. Framed insertion remains an abstract, unintegrated relation; a
full checked versioned migration is also not generated. The result is
**partial**, not B02 readiness: no B02 candidate was generated or retried.
Keep 30 candidate core / 46 historical raw entries, Phase 5C paused, B17
unexposed/unclassified, R5.2.2 historically authoritative and the
semantic-first format globally unfrozen. Next: integrate exact insertion
framing and checked durable version transitions on further non-task domains.
The [R5.16 independent transition study](../benchmark/results/phase5c/R5_16-FRAMED-INSERTION-DURABLE-MIGRATION-LOWERING.md)
now constructively lowers an exact full-record insertion frame and a checked
durable V1→V2 default/version/count transition on specimen and archive data.
Independent public/file grounding, semantic-only mutations, composition and
faithfully grounded nonconforming faults close these **bounded general-lowering**
gaps, not all relation shapes or interface binding. Candidate core remains 30;
no B02 candidate or retry followed. Phase 5C remains paused, R5.2.2 historical
authority, B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.17 frozen B02 retry](../benchmark/results/phase5c/R5_17-B02-GENERALIZATION-RETRY.md)
locks the R5.16 working-copy architecture and reconfirms B02 expressibility
with 30 candidate core constructs, but stops at unchanged general lowering:
three missing-field defaults on the same legacy task population encounter the
explicit overlapping-collection rejection. No B02 candidate was generated;
frozen acceptance, grounding and conformance were not reached. This is a
compiler-composition gap, not a new semantic construct or a retroactive change
to the historical v0.3 B02 gap. Next study the unresolved general composition
on independent non-task domains in a separate experiment before any further
frozen retry. Phase 5C does not proceed to B03; B17 remains unexposed and
 unclassified, R5.2.2 historical authority and semantic-first format unfrozen.
The [R5.18 independent relation-composition study](../benchmark/results/phase5c/R5_18-OVERLAPPING-RELATION-COMPOSITION-LOWERING.md)
now plans N compatible keyed defaults over one typed collection, deduplicates
equivalent relations, rejects conflicting literals and unsupported structural
overlaps, and checks their joint post-state in an instrument inventory. Durable
version/count outcomes and a grounded but nonconformant lowering fault exercise
the conjunction. At the R5.18 checkpoint, the R5.17 executable assertion still
expected the old lowerer to reject; R5.18 is not a new frozen retry. Core 30;
Phase 5C paused, B17 unexposed/unclassified, R5.2.2 historical authority,
format unfrozen. Next:
a separately locked retry, not a retroactive R5.17 result.
The [R5.19 second locked B02 retry](../benchmark/results/phase5c/R5_19-B02-SECOND-GENERALIZATION-RETRY.md)
first restored current-suite consistency by updating the executable R5.17
assertion to reflect current compiler behavior, preserving its historical
result. The full harness then passed 164/164 before lock. The unchanged
R5.17 three-default migration slice now types and renders through R5.18's
planner, demonstrating **bounded B02-shaped transfer without task-specific
compiler changes**. But a typed B02 ordered `list` hits the next unchanged
generator limit, `UNSUPPORTED_LOWERING_CAPABILITY: order`. This is another
lowering halt, not a B02 candidate or acceptance/grounding result. Core 30,
no #31, no B03 advance, B17 unexposed/unclassified, R5.2.2 historical
authority, format unfrozen and universal correctness unestablished. Next:
independent non-task generative ordered-outcome study before any further retry.
The [R5.20 general ordering lowering](../benchmark/results/phase5c/R5_20-GENERAL-TYPED-ORDERING-LOWERING.md)
now generatively lowers the existing #43 typed ordering relation on media and
device domains: one-, two-, three- and four-key ascending plans over typed
record collections, composed with exact selection and typed record-valued
outcomes, read-only over durable bytes, grounded and fault-tested; ties remain
semantically unconstrained and direction remains unrepresented (both reject
explicitly). No B02 retry occurred, no #31 follows and benchmark transfer
remains untested; result `R5_20_ORDERING_LOWERING_VALIDATED`. Next: a
separately locked third B02 retry, with direction semantics and scoped
ordering reserved for independent semantic/lowering study.
The [R5.21 third locked B02 retry](../benchmark/results/phase5c/R5_21-B02-THIRD-GENERALIZATION-RETRY.md)
restored suite consistency (no newly obsolete expectations; pre-lock harness
183/183), locked the R5.20 architecture and confirmed the unchanged 30-construct
model again represents frozen B02. R5.20 ordering **transferred**: the exact
R5.19 `order` blocker is resolved and the B02-shaped ordered `list`, together
with executed-slice transfers of R5.13 selection/read-only, R5.15
normalization/defaults/record outcomes, R5.16 durable version transition and
#30 count, and R5.18 N-way defaults, now generate, execute, ground and conform
as disposable slices without task-specific compiler changes. Complete B02 still
stops at the generative lowering gate: create-success needs fresh-ID/UTC-clock
value generation and omitted-input fallback defaults (both rejected explicitly),
and known boundaries remain for strict time comparison, matched-row/post-state
outcome projection, removal transitions and envelope-shaped lifecycle
replacement; the integrated multi-operation AST and CLI/clock/ID binding remain
unreached. This is the last planned one-capability retry cycle: result
`R5_21_B02_KNOWN_LOWERING_COVERAGE_INCOMPLETE` recommends a lowering-coverage
completion phase closing the known set independently before any further B02
retry. Core 30, no #31, no candidate/acceptance/grounding result for a complete
B02, Phase 5C does not advance to B03, B17 unexposed/unclassified, R5.2.2
historical authority, format unfrozen, universal correctness unestablished.
The [R5.22 known lowering-coverage completion](../benchmark/results/phase5c/R5_22-KNOWN-GENERAL-LOWERING-COVERAGE-COMPLETION.md)
replaces the serial B02 discovery loop and closes the **known** R5.21 backlog on
independent non-task domains (sensor readings, publication archive) with **no B02
retry**: `external` values through a typed capability boundary, omitted-input
`fallback` distinct from keyed `default_missing`, `before` (#27) promoted from
validating-only to generative over the typed `instant` form, matched-row/post-state
**projection**, keyed **remove** and envelope **replace_field** through the
relation-set conjunction, and a generic metadata-derived **CLI binding** — each
generated, executed, grounded, semantically conformant, and fault-tested; two
composed operations re-derived from semantics-only mutation with zero lowerer edits.
Four R5.21 frontier rejection expectations were retired by the lifecycle precedent.
Result `R5_22_KNOWN_LOWERING_COVERAGE_COMPLETE` for the lowering-coverage backlog:
no known required relation remains validating-only/unsupported/unknown. This does not
assert a complete B02 serializes or advance acceptance/interface/transport layers.
Core remains 30 with no #31 (the typed instant, `sole`/`project` and boundary are
lowering/typing/binding machinery, not new semantics), Phase 5C paused, B17
unexposed/unclassified, R5.2.2 historical authority, format unfrozen, universal
correctness unestablished. A separately locked comprehensive B02 retry
against the closed lowerer followed.
The [R5.23 comprehensive locked B02 integration retry](../benchmark/results/phase5c/R5_23-B02-COMPREHENSIVE-INTEGRATION-RETRY.md)
reconfirmed the 30-construct model's representation adequacy and reached new
integration firsts: B02-shaped create-success with typed external identity/clock
and fallback inputs executed, grounded and conformed under controlled and real
providers; a twelve-branch multi-command B02-shaped program typed, rendered and
ran as one generated program through the locked pipeline; envelope lifecycle
replacement, keyed removal, N-way migration defaults with the #30 count,
migration-required no-write reads and string-typed ordered reads all re-grounded
conformant (13/13 executable slice cases). Complete whole-program generation
still halted at typed validation, now for a newly identified class: independently
validated capabilities collide on **shared representation domains**. A
semantically typed `instant` creation timestamp is not an admissible ordering key
(`non-orderable key`), while the orderable string column refuses the
`instant`-typed clock (`outcome payload type mismatch`); `before`/`equals` cannot
bind optional or nullable record fields (faithful `list-overdue`, legacy-row
`list-high`); no relation expresses input suppliedness or domain well-formedness,
so `invalid_due_date`/`invalid_state` cannot become typed failure branches; and
one contract admits one state shape, so version-dependent rows (v2/v3 ∩ v4) and
bare-list→envelope promotion are unlowerable. The deliberately deferred
frozen-transport binding (positional argv, error envelope/exit codes,
missing-file→`[]`, shared store) was separately confirmed absent as the known
secondary blocker. Frozen acceptance never ran (7 cases blocked, no candidate);
no repair and no #31; the R5.22 per-relation backlog methodology was true per
relation yet false per program. Result
`R5_23_PREVIOUSLY_UNKNOWN_LOWERING_GAP` directs the next step not to another
isolated one-capability retry but to a focused whole-program integration phase
(inter-capability type integration, versioned-storage handling, input-validity
relations and checked transport binding on independent domains) plus revision of
coverage enumeration from relation kinds to shared-domain compositions, before a
final B02 retry. Keep core 30, Phase 5C paused, B17 unexposed/unclassified,
R5.2.2 historical authority, format unfrozen and universal correctness
unestablished. Longer term, complete the ordered benchmark with
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
