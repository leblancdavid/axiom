# Lykoi research log

## R5.22 known general lowering-coverage completion (prospective, 2026-10-03)

**Observation:** The known lowering-coverage backlog left by R5.21 was closed on
independent non-task domains (sensor readings and a publication archive), with no
B02 retry, generation, grounding or acceptance. Seven previously not-generative
relations/compositions are now constructively lowered through the existing general
channel and grounded: `external` values via a typed capability boundary (fresh
identity, UTC instant) that records the actual supplied value and enforces its
declared type, rejecting unknown/mismatched/missing-provider uses; omitted-input
`fallback`, kept distinct from the keyed state `default_missing`; the existing
#27 `before` promoted from validating-only to generative over the typed `instant`
form (before/equal/after); matched-row and post-transition **projection**
(`sole`/`project` plus a `post` value slot) realizing the #45 post/outcome channel;
keyed **remove** and envelope-collection-qualified **replace_field** through the
relation-set conjunction (state-shape independent, framing preserved); and an
integrated AST + generic metadata-derived **CLI binding** (`run_cli`). Two composed
end-to-end operations ran, grounded and conformed under real and controlled providers,
changed behavior under semantic-only mutation with zero lowerer edits, and failed
faithfully grounded lowering faults for external, fallback, replacement and removal.
`git diff --check` exit 0 (LF→CRLF notices only); harness 224/224; application/compiler
31/31. Four R5.21 frontier rejection expectations (`external`, `fallback`, `before`,
`sole`) were retired at their checkpoint by the R5.19/R5.20 lifecycle precedent to
type-level observations; the historical R5.21 result document is unchanged. See the
[R5.22 result](../benchmark/results/phase5c/R5_22-KNOWN-GENERAL-LOWERING-COVERAGE-COMPLETION.md).
Result: `R5_22_KNOWN_LOWERING_COVERAGE_COMPLETE`.

**Limit:** This closes the *lowering-coverage* set only. It is not a B02 candidate,
acceptance, grounding or conformance result, and does not establish that a complete
B02 operation serializes. Interface/transport obligations (error envelope/exit codes,
missing-file→`[]`, one shared store, the full multi-operation command AST,
`invalid_state` corruption mapping) and the `BENCHMARK_UNDERSPECIFIED` precedence/
malformed-tag items remain distinct from the backlog and unadvanced. No new core
construct (#31); the typed `instant`, `sole`/`project` and capability boundary are
lowering/typing/binding machinery over existing constructs, and no capability revealed
a semantic deficiency. Candidate core remains 30; Phase 5C paused, B17 unexposed,
R5.2.2 historical authority, format unfrozen, universal correctness unestablished.

## R5.21 third frozen B02 generalization retry (prospective, 2026-10-03)

**Observation:** With the R5.20 suite already current (no newly obsolete
expectations; pre-lock harness 183/183, application/compiler 31/31), the locked
R5.20 architecture resolved its own benchmark debut: the exact R5.19 B02
ordered-`list` serialization now types, renders, **executes, grounds and
conforms** end-to-end — tie-decided `(created_at,id)` order judged by the
relation (exact multiset plus nondecreasing keys) over durable bytes that stay
byte-identical — while the legacy alternative returns `migration_required`
without a write. Executed B02-shaped slices also transferred R5.13 exact-HIGH
selection ∘ ordering and read-only preservation, R5.15 blank-tag guard and
`stable_unique(map(trim))` projection, R5.16 durable version transition with
#30 cardinality count, and R5.18 three-default joint composition (upgraded
from render-only). Thirteen grounded slice cases were GROUNDED + CONFORMANT;
no B02-specific lowering branch exists in the locked path.
See the [R5.21 result](../benchmark/results/phase5c/R5_21-B02-THIRD-GENERALIZATION-RETRY.md).
Result: `R5_21_B02_KNOWN_LOWERING_COVERAGE_INCOMPLETE`.

**Limit:** Complete B02 remains at the generative lowering gate. The decisive
create-success composition rejects explicitly: fresh-ID/UTC-clock value
generation (`unsupported relation: external`) and omitted-input fallback
defaults (`unsupported relation: fallback`); the integrated multi-operation
AST rejects at the same point. Frontier probes additionally recorded strict
time comparison (`before`, #27 — represented/validated only in the R5.4 typed
instant channel), matched-row/post-state outcome projection (#45 post slots
exist in the R5.12 validating checker but the generative channel binds only to
input/pre), the removal transition, and a newly observed state-shape boundary:
keyed `replace_field` lowers over plain sequences but rejects `state relation`
over the versioned envelope. None was repaired; probes were observation only.
Core 30 / historical raw 46, no #31; 0 complete B02 operations, 0 candidate,
0 frozen acceptance methods; grounding/conformance claims stay slice-level and
universal implementation correctness is not established. The serial
one-capability retry pattern is concluded: the recorded next step is a
lowering-coverage completion phase over the known set (comparisons, removal,
outcome projection, input fallback, envelope/mixed transitions, external-value
binder, integrated AST/CLI binding) before any further B02 retry. Phase 5C does
not advance to B03, B17 remains unexposed/unclassified, R5.2.2 historical
authority, semantic-first format unfrozen. Post-lock verification: R5.21
focused 14 OK, full harness 197 OK, application/compiler 31 OK, locked
components re-hashed unchanged; Git LF→CRLF notices are line-ending warnings
reported separately from failures.

## R5.20 general typed ordering lowering (prospective, 2026-10-02)

**Observation:** The existing #43 typed ordering relation is no longer
validating-only. `benchmark/semantic/generative_r5_13.py` now builds a
target-independent ordering plan (required string/integer keys, key sequence
semantic, no direction) and emits executable ordering for media-asset and
device-inventory contracts: 1/2/3/4-key ascending orders, selection∘ordering,
typed record outcomes crossing the public boundary, and read-only listings
whose durable bytes stay untouched while storage order is not rewritten.
Semantic-only key mutations changed generated order without compiler edits;
serialization-order changes left digests/artifacts identical while key-list
permutation changed them; single-key reversal and dropped-secondary lowering
faults grounded faithfully yet failed the relation-based conformance check
(exact multiset + nondecreasing keys), which accepts either tied permutation.
See the [R5.20 result](../benchmark/results/phase5c/R5_20-GENERAL-TYPED-ORDERING-LOWERING.md).
Result: `R5_20_ORDERING_LOWERING_VALIDATED`.

**Limit:** Direction and tie stability are not represented by the current
model and were not invented: `direction` contracts and quantifier-local
ordering reject explicitly. Pre-existing interpreters diverge on ties (stable
sorted vs strict-adjacent witness), recorded as an existing ambiguity rather
than repaired. Verifier/emitter share type logic, so common-mode faults remain
possible. Core 30, no #31; historical raw 46. B02 was **not** retried — the
R5.19 historical test's current-lowerer assertion was updated by lifecycle
precedent only, and ordering benchmark transfer stays NO / NOT YET TESTED.
Phase 5C paused, B17 unexposed/unclassified, R5.2.2 historical authority,
semantic-first format unfrozen, universal implementation correctness not
established. Verification: R5.20 focused 18 OK, full harness 183 OK,
application/compiler 31 OK, validate/safety OK, R5.10–R5.19 focused 32 OK,
`git diff --check` exit 0 with separate Git LF→CRLF line-ending warnings.

## R5.19 second frozen B02 generalization retry (prospective, 2026-10-02)

**Observation:** The R5.17 historical test's obsolete current-compiler
rejection expectation was replaced with a current typed-slice assertion; its
historical result remains untouched. Pre-lock benchmark harness 164/164,
application/compiler 31/31, focused R5.10–R5.18 pattern 31/31 and tracked
diff check passed. Locked source hashes and frozen-authority pins are in the
[R5.19 result](../benchmark/results/phase5c/R5_19-B02-SECOND-GENERALIZATION-RETRY.md).
The exact R5.17 B02-shaped migration slice now types and renders all three
defaults through the independent R5.18 plan. This is observed compiler
transfer, not an executable complete B02 operation. A typed read-only B02
normal-list contract then rejects `render` with
`UNSUPPORTED_LOWERING_CAPABILITY: order`: the earlier overlap blocker has
cleared, but full B02 remains at the general lowering gate.

**Limit:** The R5.17 migration slice omits other legacy versions and all task
commands. No complete R5.19 B02 candidate, frozen acceptance, B02 grounding or
case conformance exists; counts are N/A. No post-lock repair. Core 30 / raw 46,
no #31; Phase 5C does not advance to B03, B17 remains unexposed/unclassified,
R5.2.2 historical authority, semantic-first format unfrozen and universal
implementation correctness not established. Study ordered-result generation on
independent non-task domains in a separate experiment. Git LF→CRLF notices
are reported separately from check failures.

## R5.18 overlapping relation lowering (prospective, 2026-10-02)

**Observation:** The previous one-owner-per-collection check blocked N
compatible relations before generation. A typed canonical plan and joint
verifier now compose 1/2/3 independent defaults on instrument records; reverse
relation ordering is behaviorally equivalent, duplicates are redundant and
incompatible literals reject. A durable old→new transition counts records,
not defaulted fields; the injected wrong second default is grounded but fails
conformance. See the [R5.18 record](../benchmark/results/phase5c/R5_18-OVERLAPPING-RELATION-COMPOSITION-LOWERING.md).

**Limit:** Frame/default overlap, post-state-dependent or unresolved same-field
expressions and normalization/write interactions are still unsupported; no
arbitrary relation solver or general optimizer follows. Final full harness:
164 tests, 163 pass and one preserved historical R5.17 assertion fails because
it expects rejection from the old lowerer. Application/compiler 31 OK, R5.16
focused 4 OK, R5.18 focused 4 OK. `git diff --check` clean, separate LF→CRLF
warnings. Core 30 / historical raw 46, no frozen retry, Phase 5C paused,
B17 unexposed/unclassified, R5.2.2 historical authority, format unfrozen;
universal correctness not established.

## R5.17 frozen B02 generalization retry (prospective, 2026-10-02)

**Observation:** The unchanged 30-candidate vocabulary still abstractly
represents frozen B02 including inherited B01/baseline obligations. A contract
slice combining B02's missing priority, nullable due date and empty ordered
tags defaults on the same keyed legacy collection, post-version 4 and a typed
population count reaches the unchanged R5.16 `typed` checker and rejects the
second default as `UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection
relations`. The focused rejection test and 160-test harness pass; this is a
**lowering halt**, not a passing B02 integration. See the
[R5.17 record](../benchmark/results/phase5c/R5_17-B02-GENERALIZATION-RETRY.md).

**Limit:** R5.15/R5.16 generated normalization, record outcomes, exact
insertion and *single-default* durable migration on unrelated domains, but no
B02 operation was generated or grounded. Frozen B02 acceptance and conformance
are N/A, not zero-pass observations. Task ordering/lifecycle/CLI binding remain
untested or unsupported in this path. No repair, new construct or B03 advance;
core 30 / historical raw 46, R5.2.2 historical authority, B17 unexposed and
unclassified, semantic-first format unfrozen. Application/compiler 31 OK;
R5.10–R5.17 focused 101 OK; whitespace checks clean with separate Git
LF→CRLF warnings. Universal correctness not established.

## R5.16 independent framed insertion and durable transition (prospective, 2026-10-02)

**Observation:** The checked exact-selection/full-record frame now generates a
fresh-key specimen registration over empty and populated durable collections.
A separate archive contract reads actual persisted V1/V2/unsupported versions,
defaults only missing fields in a uniquely keyed population, reports #30's
0/1/2 candidate cardinalities and persists V2. Independent public/file/event
grounding and semantic verification distinguish four insertion and six migration
fault variants; mutation of semantic field mapping/default changes generated
durable behavior. Trim and record-valued results compose without new lowering
branches. See the [R5.16 result](../benchmark/results/phase5c/R5_16-FRAMED-INSERTION-DURABLE-MIGRATION-LOWERING.md).

**Limit:** These are bounded one-frame/one-default collection transitions on
checked typed records, not arbitrary mixed relation synthesis, full CLI
binding, an acceptance result or universal implementation correctness.
Overlapping transforms reject; generated append is one valid storage-order
witness, not insertion ordering semantics. Result:
`R5_16_LOWERING_GAPS_CLOSED` for the two targeted capabilities only. Core 30,
historical raw 46, no B02 retry; Phase 5C paused, B17 unexposed/unclassified,
R5.2.2 historical authority and semantic-first format unfrozen. Harness 159
OK, application/compiler 31 OK, focused final R5.16 4 OK; tracked diff check
passed with separate Git line-ending warnings.

## R5.15 independent general lowering (prospective, 2026-10-02)

**Observation:** On independent media, device and library operations,
semantic-source mutations to ordered normalization, typed record field mapping
and keyed missing-field default alter real generated subprocess results or
durable state without compiler edits. A library operation composes all three;
a novel nested normalization/cardinality/device-state combination generates
without further edits. Internal events agree with public and durable observers;
a disposable wrong device replacement grounds but fails semantic conformance.
See the [R5.15 result](../benchmark/results/phase5c/R5_15-GENERAL-LOWERING-COVERAGE-EXPANSION.md).

**Limit:** Insertion remains unintegrated/unsupported; library edition is input
applicability, not a checked persisted version change. Bounded one-field
defaults do not establish full migration or all #44 compositions. The shared
typed AST/verifier still admits common-mode errors. Result:
`R5_15_GENERAL_LOWERING_PARTIAL`. Candidate core remains 30; historical raw
numbered inventory 46 with new unnumbered compiler/runtime/test machinery.
No generated B02 candidate or R5.15 B02 acceptance was run; historical v0.3
B02 gap unchanged. Phase 5C paused, B17 unexposed/unclassified, R5.2.2
historically authoritative, semantic-first format unfrozen. Verification:
harness 155 OK, application/compiler 31 OK, validate/safety OK, diff check OK;
Git line-ending warnings separate from failures.

## R5.14 controlled B02 architecture pressure (prospective, 2026-10-02)

**Observation:** The frozen B02 repeated-tag, trim/nonblank, case-sensitive
first-occurrence and empty/migrated-default obligations can be expressed using
the existing prospective 30-candidate vocabulary. The R5.13 generator's
supported non-task slice does not emit map(trim), stable_unique, for_each or
keyed missing defaults; it also cannot build B02 insertion/versioned migration
and task-valued results. Halted at `GENERATIVE_LOWERING_CAPABILITY` before
candidate creation. See the [R5.14 record](../benchmark/results/phase5c/R5_14-B02-FROZEN-ARCHITECTURE-PRESSURE.md).

**Limit:** This is conceptual candidate-semantic expressibility across separate
prototypes, not a single integrated validated B02 model. No generated B02
acceptance, grounding or semantic-conformance result exists; demonstrated B02
executable reuse remains zero. The historical frozen v0.3 B02 language gap
remains unchanged. The result suggests better semantic coverage than compiler
coverage, not universal correctness or an architecture contradiction. Keep
30 core / 46 raw, semantic-first format unfrozen, Phase 5C paused after B02,
R5.2.2 historically authoritative, B17 unexposed/unclassified.
Verification: harness 149 OK (including architecture, grounding, prototypes
and R5.10–R5.13), application/compiler 31 OK; model validate and safety OK;
`git diff --check` passed. Four LF→CRLF warnings were separate from failures.

## R5.13 non-task generative lowering (prospective, 2026-10-02)

**Observation:** Typed container contracts A–C generate disposable stateful
Python behavior: changing a selection literal or the referenced state field
changes real subprocess results and persisted bytes without compiler edits.
A fourth composition replaces a different field under a negated guard. The
external observer challenges events with independently captured stdout and
reopened state; an injected replacement-code fault remains grounded but fails
semantic conformance. Valid unsupported #44 relations reject explicitly,
type mismatches reject before execution, and repeated builds are byte-identical.
See the [R5.13 result](../benchmark/results/phase5c/R5_13-SEMANTIC-DRIVEN-GENERATIVE-LOWERING.md).

**Limit:** This is a constrained non-task state shape and string-result slice,
not B01 generation, arbitrary synthesis or universal correctness. The compiler
and verifier share typed AST infrastructure and can share bugs; endpoint
grounding cannot detect every intermediate effect. Representation verbosity and
AI-authoring cost are unmeasured. The recommended next experiment challenges
independent non-task state shapes and richer typed binding before any scaling.
At the R5.13 checkpoint Phase 5C was paused and B02 not yet resumed; B17
unexposed/unclassified, format unfrozen,
R5.2.2 historically authoritative, 30 candidate core / 46 raw unchanged.
Verification: benchmark harness 149 OK, application/compiler 31 OK; focused
architecture 6, grounding 10, semantic prototypes 33, R5.10 4, R5.11 4,
R5.12 3, R5.13 5 OK. `git diff --check` passed; four tracked LF→CRLF warnings
were separate from failures.

## R5.12 POC health review (prospective, 2026-10-02)

**Observation:** R5.11 template generation substitutes metadata rather than
lowering semantic operation behavior. B01 command rules appear in both target
Python and its case checker; the operation label index supplies hashes, not
an authoritative typed contract. A small general typed validating lowerer now
handles the two B01 read-only success checks and a synthetic non-task typed
filter/order/cardinality contract. Mutating the latter's predicate reverses
which grounded-*shape* tuple conforms without modifying lowering code; a novel
valid keyed-default relation is explicitly unsupported. See the
[R5.12 gate](../benchmark/results/phase5c/R5_12-POC-HEALTH-GENERAL-LOWERING-GATE.md).

**Limit:** Synthetic tuples are not observed execution; target implementation
does not regenerate from changed typed contracts. No universal correctness or
per-program productivity comparison follows. Recommendation: generative
bounded #45 lowering and independent non-task challenge before scaling. R5.2.2
remains authoritative; Phase 5C paused; B17 unexposed/unclassified; 30 core
unchanged; semantic-first format unfrozen.

## R5.11 B01 instrumented integration (prospective, 2026-10-02)

**Observation:** A separately generated B01-only CLI passes the unmodified
frozen B01 profile (5 passes, 2 B02 skips). Generated internal events on real
subprocess calls match independent public output and reopened persisted state;
the observed create, normal list, exact-HIGH list, completion and migration
cases are grounded and conformant. A three-record v2 migration preserves all
three existing priorities and reports 3 via #30 cardinality. A disposable
wrong-count variant is grounded/nonconformant, while a false post-state report
fails grounding before conformance. See the [R5.11 record](../benchmark/results/phase5c/R5_11-B01-INSTRUMENTED-INTEGRATION.md).

**Limit:** Abstract 30-candidate expressiveness and grounded finite cases do
not prove universal implementation correctness or a generally checked typed
#45 lowering. File endpoint checks do not expose every intermediate write.
The historical executable is unchanged; R5.2.2 remains authoritative,
Phase 5C paused, B17 unexposed and the semantic-first format unfrozen.

## R5.10 migration count expressiveness (prospective, 2026-10-02)

**Observation:** Frozen v2 B01 migration counts all three converted records,
not records lacking priority. The existing relations select and preserve an
arbitrary legacy population but cannot equate its extent to the reported
integer. A general typed cardinality relation (#30) plus exact selection and
a synthetic transition accepts supplied populations of size 0, 1, 4, 17 and
rejects wrong counts. A filtered three-row witness counts only its two
candidates. See the [R5.10 record](../benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md).

**Limit:** These are synthetic semantic witnesses, not integrated versioned
B01 contracts or execution. Prospective count is 46 raw / 30 candidate core;
historical inventory stays at 45. The pinned B01 executable still lacks the
R5.7 internal per-operation event. B01 inadequate and halted, Phase 5C paused,
B17 unexposed/unclassified, R5.2.2 authoritative and format unfrozen.

## R5.9 B01 complete-contract restart (prospective, 2026-10-02)

**Observation:** Frozen B01 plus inherited baseline require a numeric migration
count for arbitrary legacy populations. Exact selection, ordering, projection
and equality suggest insertion and completion framing without a new command
primitive, but the currently integrated #45 checker cannot evaluate that
composition. The pinned B01 Lykoi snapshot passed five frozen acceptance
methods, and independent public/file endpoint capture covered seven selected
root calls, a completion failure and v1 migration. The snapshot emits no
per-operation internal event to challenge, so B01 grounding fails and #45
case conformance is not evaluated. See the [R5.9 evidence](../benchmark/results/phase5c/R5_9-B01-END-TO-END-ADEQUACY-RESTART.md).

**Limit:** Numeric count/cardinality is a provisional core expressiveness gap;
full typing, migration metadata and checked B01 interface/provenance are separate
blockers. CRITICAL's independent ordinal behavior is underspecified, not grounds
for priority sorting. No #30 was added (45 historical raw, 29 candidate core).
R5.2.2 remains authoritative; B01 halted, Phase 5C paused, B17 unexposed and
unclassified and the semantic-first format unfrozen.

## R5.8 conditional outcome expressiveness (prospective, 2026-10-02)

**Implemented observation:** A generalized #45 abstract contract composes
typed outcome tags, conjunction/complement and equality/state relations for
the synthetic R5.7 operation. Grounded correct failure and success conform;
an incorrect failure classification or changed durable state reaches semantic
non-conformance without the earlier adapter policy. See the
[R5.8 analysis](../benchmark/results/phase5c/R5_8-CONDITIONAL-OUTCOME-EXPRESSIVENESS.md).

**Limit:** This is one common payload type and one observed state view; it does
not prove variant-specific payload typing, no attempted write, byte-level
equivalence for all stores, or general conformance. The 29 candidate core and
45 historical raw counts do not change. B01 remains inadequate and halted;
R5.2.2 authoritative, Phase 5C paused, B17 unexposed and unclassified,
semantic-first format unfrozen.

## R5.7 case-scoped grounding experiment (prospective, 2026-10-02)

**Implemented observation:** A generated synthetic vial-sealing operation was
called in isolated subprocesses; external argument/output capture and raw
durable-file readback challenged internal invocation events and checked artifact
provenance. Wrong result/state and error-path writes produced grounded
non-conformance; fabricated input/post reports and stale artifacts were rejected
before conformance. The [R5.7 record](../benchmark/results/phase5c/R5_7-GROUNDING-PROTOTYPE.md)
contains the fault matrix, trust boundary, verification and construct ledger.

**Limit:** R5.5 equality/default relations do not express conditional typed
failure classification. An adapter policy handles the selected case without
enlarging the 29 candidate core constructs; this makes the prototype partial,
not a B01 adequacy finding. The 45 historical numbered entries remain unchanged;
12 new non-semantic implementation responsibilities are inventoried separately.
B01 remains inadequate and halted; R5.2.2 authoritative, Phase 5C paused,
B17 unexposed and unclassified, semantic-first format unfrozen.

## R5.6 grounding and trust model (prospective, 2026-10-02)

**Code observation:** The R5.5 record checks a self-reported `source` and an
opaque boundary string, while the current generated manifest pins one artifact
with all model IDs, not a public-entry-to-contract map. The independent scenario
probe can read file bytes around selected subprocess calls but does not create
generic same-invocation contract records. The runtime's one-file `os.replace`
does not imply cross-resource atomicity or crash durability.

**Assessment:** Compiler ownership can normalize operation and persistence
boundaries, attach specific provenance and route declared effects, but compiler
hooks alone risk circular trust. Independent argv/outcome capture and post-call
durable readback can challenge reported facts on scoped cases. This is a
ready-to-prototype recommendation with explicit unknown-effect/concurrency
limits, not an implemented grounding path or universal claim. No prototype or
new construct was needed for this architecture decision; counts remain 45 raw
and 29 candidate core. The [R5.6 record](../benchmark/results/phase5c/R5_6-GROUNDING-TRUST-MODEL.md)
contains the boundary and assurance analysis. B01 remains inadequate and
halted, R5.2.2 authoritative, Phase 5C paused, B17 unexposed and unclassified,
and the semantic-first format unfrozen.

## R5.5 semantic architecture separation (prospective, 2026-10-02)

**Implemented observation:** The historical seven synthetic #45 tuple checks
now delegate to an extracted abstract contract evaluator. Separate validators
reject implementation fields in contracts, behavioral checks in binding,
and requirements or proof labels in concrete records. The case verifier
reports `proof_status: not_established` even when the relation holds; trace
continuity validates equal adjacent state on one declared boundary. Six new
architecture tests exercise these responsibilities, not B01 behavior.

**Limit:** The slot map and execution records are not yet a faithful adapter
to actual public calls or durable state. The selected subprocess scenario
probe is unchanged and not wired to the new verifier. This is an architectural
partial result, not a semantic capability gain, acceptance freeze or proof.
The [R5.5 result](../benchmark/results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md)
contains the 45-entry responsibility accounting and AI-native review. B01
remains inadequate and halted; R5.2.2, the Phase 5C pause and B17 boundary
remain in force.

## R5.4 semantic architecture checkpoint (prospective, 2026-10-02)

**Observation:** The seven #45 synthetic tuples test a supplied relation,
whereas the selected R5.4 CLI scenarios observe real executions; no checked
mapping joins their input/pre/outcome/post slots across all public calls. The
raw 45 prototype entries include ten observation/evidence and six benchmark
administration constructs, leaving 29 provisional candidate core constructs
when #45 is limited to its abstract operation relation. This does not establish
minimality, integration or B01 adequacy.

**Assessment:** The grounding gap mainly spans interface metadata, lowering,
observation and verification; universal implementation correctness requires a
separate proof argument. A typed operation relation is plausible semantic
source, but conflating it with actual-execution binding requires architectural
revision before B01 work continues. The
[checkpoint](../benchmark/results/phase5c/R5_4-SEMANTIC-ARCHITECTURE-CHECKPOINT.md)
records alternatives, finite-evidence limits and exposed-clause reuse. R5.2.2
remains authoritative; B01 is halted and inadequate, the format unfrozen,
Phase 5C paused, and B17 unexposed and unclassified.

## B01 operation-contract adequacy investigation (prospective, 2026-10-02)

**Observation:** Existing relations constrain supplied collections but not
every actual public invocation and persistent before/after state. A single
typed operation binding is a plausible common interface; seven synthetic
fixtures for an arbitrary operation distinguish result/state/source failures
and two correct populations using equality and keyed missing defaults. They
are finite witnesses, not application or universal contract verification.

**Halt:** Public observation grounding and universal state/invocation scope
remain unimplemented; keyed creation/update framing and migration outcome
semantics are also open. “Above HIGH” has no specified observable rank
comparison and does not imply priority-sorted lists. B01 is inadequate; the
prototype ledger now has 45 constructs. See the
[operation-contract halt](../benchmark/results/phase5c/R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md).

## Phase 5C exact-selection restart (prospective, 2026-10-02)

**Prototype observation:** A typed exact selection relation now checks
soundness, completeness, multiplicity and source-relative order for finite
ordered sources; B01 equality and B03 case-sensitive membership compose from
the same construct. Thirteen positive/negative fixture cases and extra
counterexamples exercise it, not universal truth or application acceptance.
The [ledger](../benchmark/results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md)
counts 42 implemented prototype constructs, 28 reused across frozen clauses.

**Halt:** B01's arbitrary-task priority preservation/default through migration
still lacks a general state-field transition/frame rule; its normal sorted
query order also lacks a typed universal binding. No further clause gate was
passed. Temporal/graph selection predicates and cross-document clause
composition are not implemented. See the
[restart record](../benchmark/results/phase5c/R5_4-SELECTION-ADEQUACY-RESTART-HALT.md).

## Phase 5C invariant vocabulary restart (prospective, 2026-10-02)

**Prototype:** Typed universal transition rules over arbitrary finite string
sequences and directed graphs now compose trim, stable case-sensitive
first-occurrence uniqueness, proposed edge addition and acyclicity. Schema
validation checks types, bindings, relationships and witness links. Twelve
linked semantic cases exercise the collection and graph rules; this is not
application acceptance or universal proof. The separate B14 self-error and
other B02/B14 clauses remain to be represented and bridged.

**Observation/halt:** Re-screening frozen B01–B16 text from B01 found B01's
general exact-HIGH selection cannot be faithfully stated by this bounded
vocabulary; B03's tag-membership selection and normal ordering are independent
instances of the same gap. The
[restart record](../benchmark/results/phase5c/R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md)
classifies clause groups and inventories every primitive and remaining gap.
No schema freeze, R5.2.2 replacement, B17 exposure or B17 classification
follows from these fixtures.

## Phase 5C clock binding and format restart (prospective, 2026-10-02)

**Implementation/witness:** A disposable subprocess adapter binds one explicit
UTC instant before loading the Python application. A focused fixture on the
pinned Conventional post-B16 executable checks strict before/equal/after,
application creation timestamp equality, repeated execution and missing or
mismatched binding rejection. This does not revalidate the frozen suites.

**Observation/halt:** Screening frozen B01–B16 text after the clock fix found
that finite equality/distinctness/time scenarios cannot state B02's rule for
arbitrary numbers of trimmed, ordered, case-sensitive unique tags; B14's
general cycle condition is another challenge. The
[adequacy restart record](../benchmark/results/phase5c/R5_4-SEMANTIC-ADEQUACY-RESTART-HALT.md)
documents the source-level inventory and stops before schema freeze or B17
composition. A general rule vocabulary remains a proposal, not a demonstrated
solution.

## Phase 5C B17 partial-dependency adjudication (prospective, 2026-10-02)

**Decision:** Phase 5C still measures complete requests. If the frozen track
lacks B16, B17 as a whole is `BLOCKED_BY_GAP -> B16`; missing-actor rejection
can be independently observed without becoming partial B17 achievement. Record
such observations with separate diagnostic vocabulary and restored/disposable
state; no B17 replacement or achieved history is activated. Conventional must
meet the full B17 requirement on its B16 continuation. The
[adjudication record](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md)
sets the rule, not a B17 outcome. Clause-ID inventory, clock adapter, bounded
bridge and checkpoint revalidation remain open before B17 exposure.

## Phase 5C typed-clock and B17 dependency review (prospective, 2026-10-02)

**Prototype:** A named `utc_now` binding with typed UTC instants, offsets and
strict-before comparison passes controlled-clock fixture checks for before,
equal and after; checked semantic-root and dependency composition passes
synthetic fail-closed fixtures. The subprocess probe correctly refuses to
claim a clock-dependent application witness without an application clock
adapter. Neither mechanism is a frozen clause-to-carrier bridge.

**Frozen-text assessment (prior halt):** B17's missing-actor rejection and existing task
read exemption can be observed without B16, while roles, existing actors and
owner-based permissions require B16's persistent users/ownership. The
request-level historical blocked-by-gap protocol did not explicitly settle
how to observe independently testable dimensions of a partly dependent but
blocked request. The analysis and original stop are in the
[halt record](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION-HALT.md);
the separate adjudication above resolves that question without exposing B17.

## Phase 5C bounded-bridge format gate (prospective, 2026-10-02)

**Observation:** The Part 1 adequacy review stopped before schema freeze.
The prototype's literal/reference expressions cannot specify a due timestamp
relative to current UTC time, required by the frozen B12 clause and its active
historical boundary carrier. Its unchecked lineage strings also do not express
validated requirement-level dependencies or replacement targets; the B17
draft's B16 guard leaves hypothetical early-history B17 without a scenario.
Details and source locations are in
[`R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md`](../benchmark/results/phase5c/R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md).
These are format/composition gaps, not evidence of a language capability gap
or of an incorrect R5.2.2 oracle. B17 remains unexposed and unfrozen.

## Phase 5C semantic-requirement prototype (prospective, 2026-10-02)

**Observation:** R5.3's saved 233/28 candidate sites are not a certified
assertion-level semantic inventory; its latest worksheet still has 187/21
unexplained candidates. The corrected B01 case shows why precondition fidelity
matters: a HIGH-only witness misses the pending NORMAL task present when the
original `list-high` assertion ran. The R5.2.2 corrected parent remains the
authoritative historical acceptance boundary.

**Prototype result:** A small JSON scenario vocabulary describes ordered
commands, achieved-history guards, storage snapshots, data bindings and
observations. Selected B01/B11/B14/B16 witnesses execute successfully on a
pinned Conventional B16 snapshot (five scenarios); the early B01 variant
executes on a pinned Lykoi {B01,B04} snapshot (one scenario). The prototype
validator also rejects overlapping variants and unbound references. These are
examples and diagnostic checks, not exhaustive requirement coverage, restored
full-suite revalidation, or a new frozen oracle. B17 semantic records have
been drafted but neither derived acceptance nor protocol freeze exists.

**Research implication:** Semantic-first authoring may avoid reconstructing
every Python helper path for new requests, provided targeted historical
carrier retention is independently checked. Whether it actually reduces
effort or errors compared with B11–B16 remains an untested hypothesis; collect
comparable per-request effort and corrections at B17–B20.

## Phase 2 baseline and priority experiment (2026-10-01)

Baseline: `experiments/task_manager-v0.1.json` is the original Phase 1 model.
`experiments/task_manager-v0.2-before-priority.json` retains its application
behavior but expresses it in v0.2 for an application-only semantic comparison.
Both baseline and final models validate. The final model is
`air/task_manager.json`.

### Observation: finding the impact of a field addition

**Conventional Approach:** Search for task constructors, readers, persistence,
interfaces and tests, then inspect likely matches.

**Lykoi Approach:** `inspect field_priority` finds its type, the creating
behavior, filtered reader, migration and owner by semantic IDs. Diffing the
v0.2 baseline against the final model identifies the new `type_priority`,
`field_priority`, `arg_priority`, `fn_list_high`, `cmd_list_high`, `cmd_migrate`, contracts and
`migration_task_priority`. `fn_create` assigns the field and consumes the
new input; `fn_list_high` filters on it; `cmd_create` binds the input. The
`type_task` change reaches `fn_complete` and `fn_delete` through their output
type, and `state_tasks` reaches all four existing behaviors via state
relationships. `fn_list`, `fn_complete` and `fn_delete` also acquire a
`migration_required` failure because their state now has schema version 2.

**Result:** Explicit references made direct impact easier to discover. The
initial v0.1-to-v0.2 diff was noisy because identity was added to contracts
and errors and effect categories changed; a normalized v0.2 baseline is
necessary to isolate the application change. The current impact calculation
reports immediate semantic dependents, not a complete transitive execution
path; some affected entities are conservatively flagged.

**Implication:** Machine-queryable relationships help, but changes to the
*language representation* must be distinguished from changes to application
behavior in research comparisons.

### Observation: default and HIGH-only selection

**Conventional Approach:** Add a field to a Python record, a default in the
constructor, a new CLI flag and a filtered-list code path.

**Lykoi Approach:** A typed enum, `input_default` assignment and
`field_equals` collection predicate represent the requested semantics in the
model. Validation checks enum literals, typed assignments, command bindings,
predicate field references and inferred effect footprints. The generated
Python was never manually edited.

**Result:** Validation and all 17 tests pass. An isolated execution created
a NORMAL task and a HIGH task; `list-high` returned exactly the HIGH task and
`list` returned both. There was a language capability gap: Phase 1 could
neither bind an optional input with a default nor select a subset of a
collection. The smallest reusable extensions were a typed input default and
a typed equality predicate. Both are backend-independent and enable new
validation. They required changes to the validator and Python backend; this
upfront compiler work is more expensive than the corresponding short Python
edit for a single small app.

**Implication:** Explicit semantics may pay off across repeated maintenance
tasks, but this first experiment does not demonstrate a net speed advantage.

### Observation: existing persisted tasks

**Conventional Approach:** Write a migration script or opportunistically
default missing fields during reads; review failures manually.

**Lykoi Approach:** `migration_task_priority` declares a schema transition,
constant field addition and read/write effects. An old file makes ordinary
commands report `migration_required`. `migrate` checks the resulting record
shape and invariants before atomic replacement; repeated invocation is a
no-op.

**Result:** Integration tests show legacy data remains untouched until
migration, then receives NORMAL priority. This surfaced a second capability
gap: the Phase 1 persistence format had no schema version. v0.2 introduces an
explicit versioned envelope and a narrow additive migration. The current
migration model does not support transformations, deletions, multi-state
coordination, or proving old-record invariants independently of the final
schema; those would need new general-purpose semantics before use.

**Implication:** Storage compatibility is part of semantic modification, not
merely a generated-code detail. Explicit migrations make it visible but add
representation and runtime complexity.

### Observation: provenance and reproducibility

**Conventional Approach:** Associate a commit and build output by filename.

**Lykoi Approach:** The generated header directs edits back to Lykoi. The
manifest records model/compiler versions, the artifact hash and semantic
entity IDs. Inspection/diff uses the model rather than the generated source.

**Result:** Regeneration is deterministic and the compiler test compares the
generated file byte-for-byte. The manifest currently associates the one
self-contained artifact with all semantic entities; it cannot attribute a
particular generated line to one behavior. The experiment's generated artifact
SHA-256 is `db19c077abd7b9177e1092ad38edb3479720e1f60bc1e8ac90ece0b37d1f9afd`.

**Implication:** Artifact-level provenance is useful now; finer attribution
requires a more granular lowering pipeline, not a claim of behavioral proof.

## Capability-gap decisions

| Missing concept | Why Phase 1 was insufficient | Smallest reusable addition | Backend-independent? | New validation |
| --- | --- | --- | --- | --- |
| Optional priority input | Only required CLI inputs and unconditional assignments existed. | Typed `input_default` binding; omission selects a literal default. | Yes; CLI flags are only one boundary binding. | Input type matches field, default belongs to enum, optional argument has a default. |
| HIGH-only list | `list` could only return the entire collection. | Typed collection selection with `field_equals` before sorting. | Yes. | Predicate field exists and its literal matches the field type. |
| Existing persisted tasks | Phase 1 had no schema version or migration operation. | Identified additive state migration with declared read/write effects and an explicit command. | Semantic transition yes; the JSON envelope and atomic replacement are backend details. | Version chain, target field and default type, complete effect declaration, final-state invariants. |

## Phase 3: plan-first due-date experiment (2026-10-01)

The original model hash is `f57f6b8661db24fad4de119875454638008f6a24`
(Git blob SHA-1). Before changing `air/task_manager.json`, I wrote
`experiments/phase3-due-dates.plan.json`, validated its typed operations and
saved explained paths in `experiments/phase3-prechange-impact.json`. `plan`
reported direct-dependent omissions for five unchanged postconditions and
`inv_unique_ids`; these were kept as warnings instead of being silently
folded into an edit list. The first `apply` generated and verified a staged
change, but one negative plan-validator test failed: after rejecting removal
of the state, the reporter still tried to index the invalid candidate. Apply
restored the original model and artifacts; fixing the reporter made the
second apply pass all 22 tests; the final suite, including a later stale-plan
regression and provenance check, passes all 24 tests. No generated Python was
read to plan impact.

Actual semantic operations are recorded in `experiments/phase3-actual-diff.json`;
the ID comparison is in `experiments/phase3-impact-comparison.json`:
16 expected-and-changed, 12 expected-but-unchanged, zero unexpectedly
changed. The unchanged IDs include all old list/update/delete behaviors,
their commands, the old migration, the storage and clock capabilities and
the task list type. They are affected *conceptually* via the new record
shape/state version but require no semantic edit. This is evidence of
conservative reachability, not a precision score. It is partly tautological:
the plan specifies concrete transformations, so comparing its predicted
change IDs to its own resulting structural diff cannot establish that the
original human intent was inferred correctly.

1. **Could affected entities be found from relationships alone?** Yes for
   the record, constructors, readers, persisted state, commands, constraints,
   migration, and declared capabilities. `type_task → type_task_list →
   state_tasks → fn_list → cmd_list` is an inspectable pre-change path. The
   manifest points to a single artifact containing all entities and cannot
   locate an affected generated region. Pre-existing Python tests have no
   model relationship; the new fixed-clock scenario is model-owned.
2. **Missing dependencies?** Nullable field shape, composed predicates,
   clock-dependent selection, and executable example expectations were
   missing concepts, not missing edges. A new `field_before_clock` predicate
   adds an explicit dependency on `cap_clock`; its `clock_read` effect is
   inferred and checked. The pre-existing migration command referenced one
   migration, so supporting a second version required treating that binding
   as the latest migration in a chain.
3. **Excess irrelevant results?** Yes. Type/state reachability includes
   commands and postconditions that did not change. Paths are useful for
   inspection, but the current direct/indirect labels describe graph distance,
   not likelihood of needing modification. Missing direct dependents were
   warnings rather than proof of plan incompleteness.
4. **Did planning catch mistakes?** It identified omitted direct dependents
   before application and rejected invalid plans in tests (dangling state
   removal and empty behavioral verification). It did not predict the
   reporter bug: that surfaced during apply verification. Verification strings
   are declared evidence goals, not formally linked to test IDs or proven to
   have been covered by the runner.
5. **Did clock access help?** Yes. The overdue behavior declares `cap_clock`
   and `clock_read`. Removing the effect fails validation. A fixed-clock
   scenario checks past/future/equal/undated/completed records without
   depending on wall-clock timing, and asserts one clock sample per query.
   The public CLI still reads the real system clock through that capability.
6. **Where is Lykoi still structural conventional code?** The backend is a
   Python interpreter for narrowly structured CRUD and filter instructions;
   the plan's append/set operations manipulate JSON arrays and fields. The
   scenario test imports the generated module, and artifact-level provenance
   remains broad. The bounded semantics give deterministic validation, but
   neither the plan nor its contracts express arbitrary temporal logic or
   guarantee that a verification sentence corresponds to an executed test.

The migration from state version 2 to 3 adds `due_date: null` to old records;
version 1 migration chains through the earlier priority migration. Normal
reads reject unmigrated state. Strictly earlier UTC instants qualify as
overdue, and complete or undated tasks do not. These observations were made
from the model and tests, with compiler template work following the plan.

## Phase 4: lifecycle, authority, semantic safety (2026-10-01)

The v0.3 Task model gives its status lifecycle and `pending → completed`
transition stable IDs. `fn_complete` must perform that transition and match
its target and source guard. Mutating status without the transition, changing
the target, and removing the source guard are rejected during validation,
before generating Python. A generated-runtime scenario completes a pending
record, then verifies that repeating the transition fails without altering
the file.

Storage read and write authority are separately identified and granted to
each behavior/migration. Removing required write authority or adding write
authority to the overdue reader fails validation; effects alone do not confer
permission. This is model-level authority, not an OS-level sandbox.

The safety report classifies the stored-record invariants as runtime enforced
and the completed-record exclusion from the overdue query as structurally
guaranteed by its validated equality filter. It does not count passing tests
as formal proof. The model has six declared invariants and one transition;
the verification suite now runs 31 tests. Phase 3's 16/12/0 comparison remains
a conservative reachability observation, not an accuracy or safety score.

## Phase 5C: executable-path observation (2026-10-02)

The prospective R5.3 reconstruction revealed a measurement distinction:
source sites indicate possible assertions, while a runtime trace supplies
concrete invocations, operands and reached paths. Two frozen R5.2.2 achieved
histories produced repeatable normalized external-suite traces, but a same-line
event/root correlation alone cannot demonstrate that the reconstructed root
preserves the CLI input, returned value, later persisted observation and
rejection precondition. Generated IDs and creation times require relational
aliases rather than removal; B12's wall-clock-relative deadline additionally
requires recording its *source-derived* relative-time rule. An initial
in-process rerun also exposed frozen skip-marker mutation of the baseline
test class; restoring those methods after execution made repetition possible
without changing the frozen runner. The evidence and open reconciliation gates
are recorded in [R5.3 runtime-trace progress](../benchmark/results/phase5c/R5_3-RUNTIME-TRACE-VALIDATION-PROGRESS.md).

This supports using static and dynamic evidence together, not treating the
dynamic trace as a new semantic authority. No completeness or equivalence
claim follows while executable paths remain unmapped.
# Prospective B01 semantic-format restart (2026-10-02)

Reading the frozen B01 request against the inherited baseline and corrected
R5.2.2 carrier shows two distinguishable collection relations: ascending
`(created_at, id)` exact result order, and keyed field-preserving migration
with NORMAL applied only when priority is absent. The unfrozen
`benchmark/semantic/state_relations.py` prototypes both and checks finite
positive/negative witnesses. It does not bind those collections to arbitrary
public command traces or persisted states, nor settle the observable meaning
of the priority rank. B01 adequacy remains halted; details and limitations are
in `benchmark/results/phase5c/R5_4-B01-ORDER-TRANSITION-ADEQUACY-HALT.md`.

## R5.23 comprehensive B02 integration-retry observations (prospective, 2026-10-03)

The first comprehensive B02 retry after closing the known lowering-coverage
backlog relation-by-relation reached a new integration first — a twelve-branch
multi-command B02-shaped semantic program typed, rendered and executed as one
generated program, with create-success (typed external identity and clock,
fallback defaults, framed insertion, embedded tag normalization) grounded and
semantically conformant under both controlled and real providers. Thirteen of
thirteen executable B02-shaped operations grounded with byte-level no-write
obligations honored on every failure and read. Yet the *complete* document still
halted at typed validation, and the failures were not of the kind the backlog
could enumerate: independently validated capabilities collided where they share
one representation domain. `instant` creation timestamps (required by the clock
capability) are rejected as ordering keys, while orderable string columns reject
the clock; `before`/`equals` bind neither optional nor nullable record fields, so
faithful overdue selection and legacy-row filters cannot guard; the grammar has
no suppliedness or domain-well-formedness relation, so `invalid_due_date` and
read-time `invalid_state` have no typed failure branch; one contract admits one
state shape, so v2/v3-versus-v4 row typing and bare-list-to-envelope promotion
cannot coexist with current reads. The deferred frozen-transport binding
(positional argv, repeated flags, shared store, missing-file semantics, error
envelope and exit codes) was separately observed absent — as expected, and never
secretly substituted.

The measurement lesson: "no known required relation remains unsupported" held
per relation while being false per program. The "Integrated AST / CLI binding"
coverage row was closed from a single-operation probe while the multi-operation
document was excluded from the backlog as assembly, leaving the composition
pressure uncategorized. Coverage enumeration must track *shared domains*
(field type junctions, optional/nullable operand rules, storage-shape versioning,
contract arity, transport contracts), not relation kinds alone. Slice
grounding/conformance remains non-substitutable for whole-program generation;
no frozen acceptance ran, and no repair occurred after lock. No semantic
construct was added: the candidate core count remains 30 with no #31; every
observed blocker references existing semantics (#24/#25, #27, #43, #44, #45, #30)
at the lowering/type-integration/binding layer. Details and the exact gate are in
`benchmark/results/phase5c/R5_23-B02-COMPREHENSIVE-INTEGRATION-RETRY.md`.
