# R5.27 — Unified typed pipeline integration (prospective, 2026-10-03)

**Decision:** `R5_27_UNIFIED_TYPED_PIPELINE_PARTIAL`. This checkpoint introduces
one target-independent R5.27 operand analyzer for reading and writing contracts,
and passes a legacy-compatible insertion through the existing general generator
and verifier. **Refined reads/writes and instant ordering do not yet pass through
that generator/verifier.** Do not promote R5.26's read-only evidence to
read/write evidence.

## 1. Pipeline comparison

| Axis | R5.23 general read/write | R5.26 read-only integration | R5.27 checkpoint |
| --- | --- | --- | --- |
| Semantic AST | versioned `id/input/state/branches`, typed expression nodes, branch transitions | same envelope, `present` expression | same envelope, version `R5.27` |
| Type environment | `input`, `pre`; `post` only for outcome; transient `item` in selection | `input`, `pre`, transient `item`; no writing `post` | `input`, `pre`, `post`, transient `item` in one analyzer |
| Optional | record key may be absent; fallback/default; no scoped elimination | exact-path presence witness unwraps optional in a positive conjunction | same witness, also checks transition operands |
| Refinement | none | direct selection predicate or smallest positive conjunction, never global | same, reset per selection; guard does not authorize separate expressions |
| Relation planning | checked conjunction of framed insertion, defaults, replacement, removal, post equality | only read-only selection/order | operand typing added, relation-set overlap/uniqueness planning **pending** |
| Ordering | required string/integer keys; Python tuple emitter; multiset/tie verifier | instant included with UTC parse; optional key only after selection | typed plan accepts instant and locally selected optional instant; emitter pending |
| State slots | same declared pre/post state shape; record/sequence projections | sequence only, preserve only | same-shape record/sequence typed; no cross-shape extension |
| Outcomes | tagged exact typed payload, post projection, external values | tagged read-only payload | tagged exact typed payload checked; no R5.27 lowering |
| Runtime | generic file/subprocess boundary with event and external log | same runtime | unchanged; no new runtime path |
| Evidence/verifier | manifest digest, public/event/durable challenge; relational post-state checks | separate manifest/challenge and independent selection/order verifier | one legacy-compatible insertion uses the historical verifier; no unified refined verifier |

Duplicated rules remain in R5.23 `_compile`, ordering planner, R5.26
`analyze`/`ordering_plan` and both evidence verifiers. Incompatible assumptions:
R5.23's key ordering excludes instant, R5.26's checker rejects transitions,
and R5.23's expression emitter does not know `present`. Historical locked files
are unchanged; this is a prospective consolidation boundary, not a retroactive
revision of the R5.23 lock.

## 2–5. Unified type design and its checked boundary

`benchmark/semantic/unified_types_r5_27.py` exposes `analyze(expression, slots,
refinements)`, `conjunction`, `ordering_plan` and `typed(contract)`. Slot shapes
cover input, pre, post and per-selection item; expressions cover typed literals,
records, external capability types, collection element types, fallback, outcomes
and relation operands. `present(ref(binding, field))` witnesses only a declared
`optional<T>` field. `and` gathers direct witnesses as a relation set before
checking all conjuncts; no left-to-right typing dependency. The witness is not
exported to a sibling, a different row, an independent operation guard, or a
different field. Nullable is not eliminated. `before` requires two `instant`
operands. The same ordered-key plan admits required string/integer/instant keys
and optional keys proved present by the direct selected population. This is
checker-level closure, **not** yet general emitter/verifier closure. Other
previously checked non-refinement expressions still delegate to the historical
validating expression checker; consolidation of those paths is outstanding.
`generate_legacy_subset` first checks the R5.27 contract, then uses the pinned
general generator only when its own checker accepts it. It rejects refined
selection/order rather than silently routing to the R5.26 side path.

## 6–15. Composition and whole-program status

The independent archive-domain R5.27 static fixtures exercise both serialization
orders of `present(seen) AND before(seen, cutoff)`, optional instant ordering,
typed external instant in an insertion record, and the same guarded selection
in read, remove and replace-field contracts. For the writing guard the selection
also compares the record's required key with input key; a cardinality-one guard
controls the existing keyed transition. Checker rejection includes wrong-field
witness, leaked nested witness, unselected optional ordering key, presence on a
required key, and wrong replacement type. These are typed contracts, **not**
generated operations or proof that a match is unique in every state.

One external UTC-instant framed insertion with a required instant column was
generated through that bridge, observed by subprocess output, event, external
log and independent durable readback, and passed the **historical** R5.23
grounding/conformance challenge. The same instant appeared in event, public
outcome and durable row. This does not prove a unified R5.27 verifier or
optional refinement over that written row.

Exact selection, normalization, string/integer ordering, fallback, external,
keyed default, cardinality, framed insertion, remove, replace-field, projection,
tagged outcome, overlapping defaults and same-shape migration remain historical
R5.23 generative capabilities tested by the existing harness. R5.27 has not
regenerated this list under its checker. No refined write transition, durable
replace/remove composition, order over *written*
records, optional refinement over *written* records, or multi-command program
has been generated in R5.27. Sequential durable-state continuity and
semantic-only whole-program mutation consequently have **no R5.27 result**.
An optional field in the declared row shape does not by itself license a record
constructor to insert a required value without matching the exact optional
record shape; the test's external insertion uses a required instant shape.

## 16–20. Grounding, faults, coherence, runtime and lifecycle

There is **one** legacy-compatible R5.27-checker-fronted grounded execution and
**zero** R5.27 semantic fault
challenges. Faults A (ignored presence), B (wrong instant order), C (wrong field
replaced) and D (different persisted external instant) remain untested in a
unified generated program. R5.26 already challenged A and B in its own read-only
profile; that evidence is not transferred. The checker and verifier therefore
do **not** yet share a unified interpretation of transitions/refinements; the
R5.26 and R5.23 verifiers remain separate. The unchanged generic runtime has
no archive/task/B02 field or operation branch; semantics are presently emitted
by the older separate lowerers. R5.26 remains a historical read-only prototype
and compatibility fixture, **not** the authoritative full general pipeline;
R5.23 remains the only historical generative general read/write profile, while
the R5.27 analyzer is prospective and incomplete. Do not retire either emitter.

## 21–25. Matrix, blockers, accounting and next gate

The new `r5_27_general_pipeline` dimension in `R5_24-type-matrix.json` records
separately semantic support, general checker, generator, verifier, whole-program,
grounding and faults; historical matrix entries are retained. R5.23 instant
ordering and optional refinement are **PARTIALLY_RESOLVED**: the R5.26 read-only
generated results and R5.27 shared typed-operand results do not establish
`RESOLVED_IN_GENERAL_PIPELINE`. Input suppliedness/well-formedness and typed
malformed outcomes, cross-shape migration, and frozen transport binding remain
distinct blockers. R5.28 should **first** finish this same R5.27 integration
gate: connect the shared analyzer to relation planning, generative lowering and
an independent semantic verifier, then generate and ground one non-task
multi-command durable program with refined writes, external instant insertion,
ordered/refined reads of written records, continuity and all four grounded
nonconforming faults. Only after that evidence should suppliedness and
well-formedness be considered as separate R5.28 semantic work. No new semantic
capability is authorized by this checkpoint.

Candidate core semantics remain **30**; no #31. One prospective analyzer and
four focused tests (three static, one executed legacy bridge) are type-analysis/test machinery, outside core
construct accounting. No B02 retry, complete B02 generation, frozen B02
acceptance/grounding/conformance; Phase 5C paused, B03 untouched, B17 unexposed
and unclassified, semantic-first format globally unfrozen, R5.2.2 historical
benchmark authority. Universal correctness is not claimed.

**Verification:** full benchmark harness 263/263 (including architecture,
grounding, semantic, R5.10–R5.26 focused suites and four R5.27 tests);
application/compiler suite 31/31; model validation ok; safety 0 capability
violations, 0 invalid transitions; R5.27 focused 4/4; type matrix parses;
`git diff --check` exit 0. Git printed LF→CRLF working-copy notices for four
tracked documentation/matrix files; these are notices, not check failures.

**Phase gate:** `R5_27_UNIFIED_TYPED_PIPELINE_PARTIAL`
