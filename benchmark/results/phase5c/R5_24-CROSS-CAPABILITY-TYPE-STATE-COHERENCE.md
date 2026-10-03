# R5.24 — Cross-capability type and state coherence (prospective, 2026-10-03)

**Decision:** `R5_24_SEMANTIC_EXTENSION_REVIEW_REQUIRED`. The class is not
validated. This phase inspected the general type/state pipeline, built an
explicit capability inventory, and established a target-independent
chronological-order interpretation on publications. It **stopped** at the
optional-field presence/refinement semantic gate. No #31 was created. The
historical R5.23 locked component digests and first-failure evidence are
preserved. This is not a complete R5.24 implementation or a benchmark retry.

## 1. Gap taxonomy

R5.23's 13/13 executable slices and twelve-branch program did not compose into
a complete typed program. The newly observed junctions were typed instant ∩
ordering, optional/nullable field ∩ predicates, raw/bound/typed input,
pre-state ∩ post-state shape, and a separately deferred transport binding.
The original frozen result remains 7 BLOCKED, 0 RUN. See
[R5.23](R5_23-B02-COMPREHENSIVE-INTEGRATION-RETRY.md); no case was rerun here.

## 2. Capability/type matrix

[The machine-readable matrix](R5_24-type-matrix.json) inventories 18 bounded
relation families and records accepted/produced/element types, optional and
refinement rules, state and outcome shapes, generation and verifier support.
It describes the **current locked generator**, except where explicitly marked
"separate interpreting prototype". Its dimensions are shape annotations, not
an executable proof of coverage. Key constraints: equality requires identical
declared types; `before` requires two `instant`s; ordering's locked key domain
is required string/integer; defaults require an optional field and a unique
string identity; insertion requires the exact record shape; `post_equals`
targets a same-shaped record state. There is no general membership/presence
predicate implemented by the bounded compiler. The R5.24 inventory test checks
the matrix's required columns and a crucial unsupported junction.

## 3. Type closure

Statuses below concern the **locked generative program**, not host-language
coercions. "Producer" includes typed input/state and literals; these sources
are distinct from relations.

| T | Producing relations / sources | Consuming relations | Junction classification |
| --- | --- | --- | --- |
| string | literal, input, external ID, trim, fallback, field projection | equality, trim, normalization, order key, identity | SEMANTICALLY_VALID_AND_SUPPORTED when required |
| integer | literal, input, cardinality, projection | equality, order key, post_equals | SEMANTICALLY_VALID_AND_SUPPORTED when required |
| boolean | predicates, literal, input | and/not, equality, typed outcome | SEMANTICALLY_VALID_AND_SUPPORTED |
| instant | typed clock, input, literal, projection, fallback | before, equality; chronological order in R5.24 interpreter | SEMANTICALLY_VALID_BUT_UNSUPPORTED for **generated ordering** |
| nullable<T> | literal/null, input, record projection | fallback default of matching nullable type, exact equality | SEMANTICALLY_VALID_BUT_UNSUPPORTED for refined `before`; null as instant is SEMANTICALLY_INVALID |
| optional<T> | omission in input/record, field projection | fallback, default_missing (storage) | SEMANTICALLY_VALID_BUT_UNSUPPORTED for presence-conditioned `before`/equality |
| sequence<T> | selection, ordering, state projection | select, order, cardinality, sole | SEMANTICALLY_VALID_AND_SUPPORTED for checked subsets; UNKNOWN for arbitrary nested compositions |
| record<F> | record expression, sole, projection, state | exact-frame, outcomes, projection | SEMANTICALLY_VALID_AND_SUPPORTED for exact shape; implicit optional→required widening SEMANTICALLY_INVALID |
| state<S_pre>→state<S_post> | state relations | migration contract | SEMANTICALLY_VALID_BUT_UNSUPPORTED when shapes differ |

The type checker already rejects crucial incompatible junctions *before*
emission (`typed` invokes `_compile` for guards and values). This is local
type checking, **not** a complete closure pass: optional refinements and
cross-shape transitions have no admissible plan. Unknown combinations must
stay UNKNOWN rather than being classified from Python's operators.

## 4. `instant` ordering

The established `instant` accepts UTC ISO `Z` text parsed by
`capability_boundary_r5_22.parse_instant`; typed `before` compares the parsed
UTC datetimes, so two valid instants have a total chronological preorder
(equal timestamps tie). Lexicographic ordering of text is not that definition:
`...00Z` and `...00.000Z` are equal chronological instants.
`instant_ordering_r5_24.plan/rank/evaluate` interprets required instant keys
directly through the existing parser, alongside required string/integer
secondary keys. Independent publication probes cover earlier/later/equal,
single and multi-key, semantic-only key changes, a wrong-order
counterexample, and rejection of optional/nullable keys. This **does not**
generate or ground an instant-ordered program: the R5.23-locked `typed` still
rejects `non-orderable key`. A direct edit of its pinned modules was tested
and rolled back because it invalidated R5.23's digest and first-failure tests.
No chronological-order semantic mismatch was found; the generative integration
remains open pending a separately versioned lowerer/verification path.

## 5. Optional/nullable model

`_type` / runtime `valid`: a missing optional record key is allowed; a
present optional key must match the inner type. A nullable key is required
unless also wrapped in `optional`; its value may be `null`. A missing key,
present `null`, and present well-typed instant are distinct values/states.
An omitted optional input is absent from the input record; `fallback` tests
**membership** in the parent record, never truthiness, and preserves a
present null if the declared base is nullable. Malformed raw text is not a
typed instant, even if it is a string in a raw transport channel.

## 6. Guard refinement / #31 gate

Attempted compositions of the existing relations:

- `and(not(equals(optional_field, null)), before(optional_field, cutoff))`:
  rejects at static equality and `before` typing; conjunction cannot narrow.
- `fallback(optional_field, sentinel)` followed by `before`: changes the
  meaning of absence to an instant, and conflates a present sentinel with
  omission. It is not a guard on *the original present value*.
- `default_missing` distinguishes absent storage fields but is a **state
  transition**, not a predicate over a scoped `item` in `select`.
- branch alternatives can guard on a value once present, but cannot first
  express membership of an optional record field as a Boolean predicate.

**Missing application-semantic information:** whether an optional field is
present, and whether a nullable present field is non-null, as a constraint
that licenses later relations to consume a refined `T` *only on that path*.
This matters for publication release dates, sensor check timestamps and
shipment arrival times independently of any task schema. The binding layer
can record *raw input* presence, but cannot decide semantic presence of an
optional **state row** field; runtime truthiness would be incorrect (empty
string, zero, null, and absence have different meanings). It is not justified
to invent a new #31 here. Review whether a type-directed generalization of
existing optional semantics/#45 can express presence constraints without a
new semantic concept; if not, review a candidate semantic relation explicitly.
This gate halts the optional/refinement capability, not the historical 30 count.

## 7. Optional/refinement synthetic tests

No generated optional-instant predicate case is claimed. Existing typing
rejects it; accordingly absent, before/equal/after-cutoff and optional
category comparisons are **unexecuted**, not passing. No implicit fallback
or truthiness implementation was introduced.

## 8. Input suppliedness

An input record with omitted `edition` and one with explicitly supplied
`edition: "standard"` are independently captured as different input objects
in the generated publication probe. Both can yield the same `fallback`
payload. Thus the binding boundary already preserves presence for optional
record fields; fallback's result alone is insufficient to recover it.
Application behavior depending on suppliedness needs a semantic guard after
binding, which is the unresolved presence/refinement question.

## 9. Input well-formedness and invalid-input boundary

Raw presence/value → parser/binder → typed record **or binding failure** →
semantic operation is the current conceptual separation. In the independent
publication probe, omission and valid supplied values execute, ground and
conform; a supplied integer for the optional string is rejected before
execution, with unchanged durable bytes and **no semantic outcome**. There
is no generic typed public parse-error result, public-error serializer or
provenance-challenged binding-failure trace. A well-formed but disallowed
category can be represented by equality/finite alternatives only once typed;
its distinct semantic failure branch was not built here. Do not call the
malformed-input rejection a grounded typed-error operation.

## 10. State-shape limitation

The original abstract `contracts.py` hardcodes `schema.record` for both
`pre.records` and `post.records`. The bounded typed #45 checker (`lower`)
uses `contract['state']` for both slots and both `_type` checks. The
generator `typed` constructs `slots={'input', 'pre'}` and
`value_slots={'input','pre','post'}` with the *same* state; `_relational`
resolves each collection against that one shape, and `post_equals` requires
that same record. `render` initializes `post = pre`, updates that shape, and
passes one state shape to runtime `run` / `run_cli`, whose `_invoke` validates
post against it. The durability boundary writes that post unchanged; no
pre/post version-binding pair is declared. `generative_evidence_r5_13.conforms`
also `_type`s both pre and post against that one shape, and its collection
frame logic compares fields of that shape. R5.16/R5.18 migrations default
missing fields *within* a permissive row and update an envelope version;
they do not change the declared state shape. This is an architectural
assumption across type checking, planning, runtime and verification.

## 11. Pre/post typing and 12–14. Migration composition

Conceptually `operation<I,S_pre,O,S_post>` is a plausible generalization of
#45, **not** a new construct. It requires two checked slots, typed branch
applicability, an exact mapping of preserved identity/untouched fields across
different shapes, a destination construction plan, and matching runtime and
independent verifier shape checks. Merely accepting a second schema label
would weaken the contract. No cross-shape transition was implemented:
independent V1 row→V2 row, bare collection→versioned envelope, default/count/
projection composition, durable readback, and faults involving partial
promotions remain **UNSUPPORTED/UNTESTED**. The same-shape legacy defaults
from R5.16/R5.18 do not establish this stronger claim.

## 15. Cross-capability planner

Minimum justified future ordering: validate typed slots and relation domains;
establish path-sensitive optional presence; analyze raw/bound/typed inputs;
check `S_pre→S_post` correspondence and frame; then plan relations and emit.
Current `typed` is an early *local* type gate; the R5.24 interpreter is not
integrated into that gate. A whole-program coherence pass is warranted only
once its missing constraint meaning and state mapping are specified. No
general theorem prover was built.

## 16–19. Whole-program, mutation, grounding and faults

No **one generated program** combines these capabilities; therefore the
whole-program pressure test is NOT EXECUTED. Publication key-list mutations
change the independent chronological interpreter's result; this is not a
generated-program mutation claim. Publication input fallback executions
produce independently observed public stdout, durable bytes, internal event
and provenance/integrity challenge (three grounded/conformant valid cases).
The malformed supplied value yields a process failure before the internal
event; it is not a grounded error outcome. A deliberately reversed instant
order is an interpreting counterexample, **not** a generated grounded fault.
The six requested cross-capability grounding/conformance faults (wrong
instant order, absent-value `before`, lost suppliedness, malformed-as-typed,
V2 label/V1 row, correct rows/wrong envelope) are not all faithfully observable
yet; they remain untested. R5.23's earlier faults are separate evidence.

## 20. Layer ownership

| Junction | Owner(s) | Current boundary |
| --- | --- | --- |
| instant ∩ order | TYPE_SYSTEM, LOWERING, VERIFICATION | chronological semantics defined; prototype only |
| optional/nullable ∩ guard | CORE_SEMANTICS, TYPE_SYSTEM, LOWERING | presence/refinement review required |
| omitted vs supplied | BINDING, CORE_SEMANTICS where behavior differs | input record preserves omission; no presence guard |
| malformed raw value | TRANSPORT, BINDING; typed error mapping in operation contract if required | no typed parse-failure boundary |
| semantically disallowed typed input | CORE_SEMANTICS, TYPE_SYSTEM | typed finite alternatives possible; untested here |
| pre/post durable shapes | STATE_SCHEMA, TYPE_SYSTEM, LOWERING, RUNTIME, VERIFICATION | single state shape across all five |
| frozen public interface | TRANSPORT, BINDING | separately deferred |

## 21. Construct gate and 22. Generic transport

Candidate core **30**, new core **0**. Presence is the exact unresolved
semantic information (§6), not a justification to add #31 without review.
Generic binding needs operation selection, raw field presence and value,
parse result/failure, typed input or checked error mapping, and separate
public outcome/error serialization; persistence initialization and durable
schema discrimination need explicit binding. The existing named-flag CLI
does not establish those interfaces for arbitrary public commands. No
frozen transport was implemented.

## 23. Revised coverage methodology

Apply the same four status definitions **separately to each row**: SYNTHETICALLY
VALIDATED = independently generated/executed/grounded/conformant with
adversarial and semantic-only mutations; BENCHMARK TRANSFER DEMONSTRATED =
the same capability composed in a locked benchmark-shaped whole program with
appropriate acceptance/grounding, without silently changing the freeze;
UNKNOWN = no decisive faithful test; UNSUPPORTED = a checked rejection or
demonstrated incompatible plan. A static inventory or interpreter alone does
not satisfy SYNTHETICALLY VALIDATED.

| Dimension | R5.24 status | What evidence would close it |
| --- | --- | --- |
| RELATION COVERAGE | historical synthetic coverage; instant-order junction UNSUPPORTED | generated typed relation on independent domain |
| TYPE-CLOSURE COVERAGE | UNSUPPORTED (instant→order in locked generator) | typed producers/consumers share exact domain in generated program |
| RELATION-COMPOSITION COVERAGE | UNKNOWN for new junctions | conjunction with shared fields and independent verifier |
| OPTIONAL/REFINEMENT COVERAGE | UNSUPPORTED | absent/null/present guard, strict comparison and negative faults |
| INPUT/BINDING COVERAGE | PARTIAL synthetic observation; typed-error UNKNOWN | raw/present/parsed/disallowed alternatives with grounded error mapping |
| STATE-SHAPE COVERAGE | UNSUPPORTED | pre/post different typed durable shapes + frame challenges |
| WHOLE-PROGRAM COVERAGE | UNKNOWN | one generated non-task program exercises all supported junctions |
| GROUNDING COVERAGE | PARTIAL (fallback only) | challenged traces/public/durable and integrity for all new junctions |

For each dimension, use SYNTHETICALLY VALIDATED only after the listed witness;
BENCHMARK TRANSFER DEMONSTRATED only after separately authorized locked transfer;
UNKNOWN when not exercised; UNSUPPORTED on explicit valid-but-unlowerable
rejection. No dimension is upgraded by a relation-level test elsewhere.

## 24. Conceptual B02 readiness (no retry)

| R5.23 blocker | Assessment |
| --- | --- |
| instant ordering | PARTIALLY_RESOLVED: chronology interpreted; generator/verifier still reject |
| optional/nullable guards | UNRESOLVED: semantic-extension review gate |
| suppliedness/well-formedness | PARTIALLY_RESOLVED: presence preserved in input; typed error bridge absent |
| version-dependent rows | UNRESOLVED |
| envelope promotion | UNRESOLVED |
| public transport | REQUIRES_TRANSPORT_WORK |

Another comprehensive retry is **not justified** by these results.

## 25. Construct and system accounting

| Layer | R5.24 additions / status |
| --- | --- |
| candidate core semantics | 30 total; +0; #31 undecided |
| type system | +1 separate checked instant-order plan/interpreter; no locked compiler changes |
| lowering/planning | +0 integrated; prototype plan above is not generative |
| binding | +0; observed existing optional-input record |
| transport | +0 |
| runtime | +0 |
| provenance/observation | +0; reused existing challenge |
| verification | +0 integrated; interpreting wrong-order counterexample only |
| evidence/tests | +1 matrix JSON, +1 focused test module (6 tests), +1 result record |

## 26. Verification and exact next recommendation

Application/compiler suite: **31 passed**. Model validation: **ok**. Safety:
0 capability violations and 0 invalid transitions. Focused new suite: **6
passed**. Full benchmark harness was run during the initial direct-lowering
trial (249 tests; seven failures: four R5.23 historical digest subtests and
three superseded first-failure assertions); those edits were rolled back.
After restoring the locked modules the final full harness passed **249/249**,
including R5.23 lock integrity, R5.10–R5.23 focused tests, architecture,
grounding and semantic-prototype suites. Final `git diff --check` exited 0.
Git LF→CRLF notices were line-ending warnings, not test failures. The seven
trial failures are reported separately from this final green state.

**Next:** focused review of presence/null refinement using the existing
optional type and #45 first, with explicit cross-domain semantics and a
decision on whether any genuinely new relation is needed. After that review,
implement and test a *separately versioned* coherence compiler/runtime/
verifier path, including exact pre/post shape correspondence, without
altering historical R5.23 pinned modules or freezing the format. Only then
attempt one generated multi-command non-task pressure test and fault matrix.
No B02 retry or frozen acceptance ran here. Phase 5C paused; B03 untouched;
B17 unexposed/unclassified; format globally unfrozen; R5.2.2 historical
authority; universal correctness not established.

    R5_24_SEMANTIC_EXTENSION_REVIEW_REQUIRED
