# R5.28 — Refined plan consumption integration (prospective, 2026-10-03)

**Decision: `R5_28_REFINED_PIPELINE_INTEGRATION_PARTIAL`.** A source-bound checked
plan now reaches a prospective general-emitter fork and an independent semantic
verifier for read and write *operations*. It has **not** become the pinned general
generator/verifier, and no single generated multi-command program was established.
The R5.23 hash-locked files were restored after the full harness exposed this
boundary. Do not reinterpret this fork as general-pipeline resolution.

## 1. Downstream assumption audit

| Site | Classification | Current seam |
| --- | --- | --- |
| `generative_r5_13.typed`, `_relational`, `ordering_plan` | MUST_CONSUME_UNIFIED_ANALYSIS / LEGACY_DUPLICATION | `_compile` rechecks guards, relation operands and required string/integer ordering; historical hash lock prevents editing in place. |
| `generative_r5_13.expression`, `render` | TARGET_SPECIFIC_EMISSION / LEGACY_DUPLICATION | Python emission dispatches by expression kind; order independently replans keys, and conjunction has source order. |
| `generative_runtime_r5_13` | RUNTIME_ONLY | File/CLI boundary checks shapes, writes and logs capabilities; it has no refinement scope. Instant comparison uses UTC datetime, not string order. |
| `generative_evidence_r5_13.challenge` | RUNTIME_ONLY | Manifest, internal trace, public subprocess output and independent durable bytes are challenged; no semantic typing belongs in grounding. |
| `generative_evidence_r5_13.conforms`, `_ordered_relation_holds` | VERIFIER_ONLY / LEGACY_DUPLICATION | `_compile` evaluates semantics and legacy ordering planner rechecks types; old verifier has no present/refined interpretation. |
| `type_integration_r5_26` | HISTORICAL_PROTOTYPE | Separate read-only analyzer/emitter/verifier; not a full operation pipeline. |
| `unified_types_r5_27.analyze` fallback to `_compile` | LEGACY_DUPLICATION | Unrefined expression forms still delegate to historical checker; refinement is confined to the unified analyzer. |

## 2–5. Plan, identity, scope and dependencies

`unified_types_r5_27.checked_plan` first validates the complete contract, then
records source digest, source-object identity, conjunction witnesses as
`(binding-path, producer-node-id)` pairs, checked order key/element types and
checked relation operand types. This is metadata over the same semantic AST,
not a second semantics document. The plan rejects a changed source digest and
unknown operand identity. An `item` witness is checked inside its selection;
the analyzer rejects its use in another selection, nested conjunct, branch or
transition. The witness/consumer edge permits reordering positive conjunctions
for safe short-circuiting, without assigning an order to the semantic relation
set. No key-name-only matching establishes a witness; the producer has an AST
identity and the checker establishes its binding. The prospective emitter uses
the plan's witnesses/order/operand types; it does not re-plan refined types.
Object IDs are process-local and are not serialized; the source digest pins
content. This is a bounded plan, not a persistent cross-process semantic-ID
protocol. The verifier interprets semantic source with the checked scope/key
facts and does not inspect generated Python. Legacy expression forms still
delegate to the old interpreter.

## 6–10. Generated operation observations

The independently named `refined_generator_r5_28`, `refined_runtime_r5_28`
and `refined_evidence_r5_28` are prospective forks of the general, non-task
emitter/runtime/evidence path. They avoid modifying R5.23's hash-pinned
components. `unified_types_r5_27.generate` enters this path with a checked
plan; **it is a side path**, so the architectural gate remains partial.
The archive fixture runs optional-instant selection with presence and strict
`before` in both serialized conjunction orders; an additional exact-code
selection returns only `go`. Both exclude the absent row. Broad ordering
produces `a, go, z`: two equal instants are decided by the secondary code key.
The read is a typed record collection and preserves durable bytes. A
cardinality-one guarded keyed replacement changes only the
selected `go` row's label; a separate keyed removal removes only that row.
Both write shapes are grounded and conformant on the fixture. The guard proves
the selected population for the tested state; the transition itself remains
the existing keyed relation, not a new predicate-transition primitive. These
are separate generated operations, **not** a shared generated program.

## 11–13. Verifier agreement and external regression

The prospective verifier chooses a branch and evaluates semantic expressions
against independently read pre/post bytes, input and logged external values.
An ordered result requires the exact selected multiset and chronologically
nondecreasing typed keys (ties unconstrained). Transition framing is evaluated
from source relations, not from emitted transition code. An unguarded optional
`before` fails both checker and verifier validation; changed-source plan reuse
fails. The required-instant archive insertion still passes generation,
subprocess observation, public result, external log and durable row equality.

## 14–16. Persistence closure, program, continuity, mutations

**Not established:** insertion and later refinement/order over the *same*
written optional-instant row; one five-command generated program; or an
independently checked post(N) = pre(N+1) sequence. The insertion fixture uses
a required-instant row, while the read/write fixture declares an optional
instant row; exact constructor typing does not widen required to optional.
Implemented semantic-only mutations (regenerate without component edits):
refinement target `seen`→`other` together with its ordering key, cutoff to
the equality boundary, replacement value, and matched remove predicate/target.
The checked plan rejects mutations made *after* planning.

## 17–20. Grounding, four faults and circularity

The new focused test exercises subprocess events, independently captured public
JSON, independent before/after durable file bytes, manifest hashes and the
capability log. Each of four disposable faulty artifact variants updates its
own manifest to maintain integrity; semantic contracts are unchanged:

| Fault | Observed discrepancy | Grounded | Conformant |
| --- | --- | --- | --- |
| A absent optional matches | selected population includes absent row | yes | no |
| B instant ordering | secondary key dropped on tied instants | yes | no |
| C wrong write field | selected row changes `code` instead of `label` | yes | no |
| D external/persistence mismatch | public uses provider instant; persisted row has another | yes | no |

The semantic verifier shares the *type interpretation* but neither executes
the emitted Python as its expectation nor consumes its generated transition
plan. The observer challenges claims against public and durable surfaces. This
does not establish universal correctness or all adversarial observer cases.

## 21–25. Lifecycle, matrix, blockers and gate

`unified_types_r5_27` plan machinery and R5.28 fork are **prospective**;
R5.23 remains the CURRENT_GENERAL_PIPELINE at its historical lock, R5.25/26
are HISTORICAL_PROTOTYPE / COMPATIBILITY_FIXTURE, and R5.23/R5.26 duplicate
type interpretation is RETIRABLE_DUPLICATION only after an independently
versioned replacement has met the whole-program gate. Nothing is deleted.
`R5_24-type-matrix.json` adds separate R5.28 read/write, whole-program,
grounding and fault dimensions without changing historical rows.

R5.23 instant ordering and optional guard refinement remain **PARTIALLY_RESOLVED**,
not `RESOLVED_IN_GENERAL_PIPELINE`: the pinned compiler still does not consume
the plan, and the fork has no multi-command generated program. The remaining
independent classes are suppliedness/well-formedness, typed malformed outcomes,
cross-shape state evolution and frozen transport binding. No B02 retry was
undertaken. Candidate core semantics remain **30**, no #31; checked-plan and
prospective emission/verification are system machinery. The semantic-first
format remains globally unfrozen.

## 26. Exact R5.29 recommendation

Version a single general multi-operation compiler interface that accepts this
checked plan without modifying the R5.23 locked snapshot; support one durable
state shape for external insertion, refined/ordered reads and both refined
writes, then establish post/pre continuity and replay four faults in that ONE
generated program. Remove the R5.28 fork only after that independent evidence,
and only then reassess the two R5.23 type blockers. Do not work on unrelated
semantic capabilities at this gate.

**Verification at checkpoint:** full benchmark harness 269/269 (including
architecture/grounding/semantic, relevant R5.10–R5.27 and R5.28 focused
6/6); application/compiler 31/31; validation OK; safety 0 capability
violations / 0 invalid transitions; machine-readable matrix parses and
`git diff --check` exits 0.
An initial full benchmark harness run reported 268 tests with three historical
R5.23 hash-lock failures caused by in-place edits; those files were restored
and integration moved to the prospective fork. The subsequent full harness
passed 269/269 including the historical lock test. Git LF→CRLF notices are separate
from test failures. No frozen B02 acceptance, grounding or conformance was run
as an R5.28 experiment; pre-existing historical harness diagnostics are not a
new B02 retry. Phase 5C paused, B03 untouched, B17 unexposed/unclassified,
R5.2.2 historical benchmark authority, universal correctness unclaimed.

**Phase gate: `R5_28_REFINED_PIPELINE_INTEGRATION_PARTIAL`**
