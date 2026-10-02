# R5.11 — B01 instrumented integration (prospective, 2026-10-02)

**Authority:** R5.2.2 remains the historical post-B16 benchmark boundary.
Sources: frozen `benchmark/requirements/B01.md`, `benchmark/baseline.md`,
`benchmark/harness/regression.py` with `profiles/B01.json`, and the corrected
R5.2.2 B01 intermediate-state carrier. This is a new B01-only candidate; the
checkpoint-pinned executable, its checkpoint, frozen oracle and `generated/`
were not edited. The prospective semantic format remains unfrozen.

## 1. Assembled semantic contract and completeness gate (before generation)

Let `(I,S,O,S')` be a single #45 operation contract; `S` includes absence,
version and complete finite task population, and `O` has a typed success or
error variant. Equality below means complete typed record equality, not just
field presence. The contract is universal over applicable valid inputs and
states; the cases measured below are finite instances, not its definition.

| Frozen obligation | Classification | Composed requirement |
| --- | --- | --- |
| CRITICAL accepted, stored and returned distinctly; exact HIGH excludes it | REPRESENTED | Finite domain membership, field equality, #10–12 exact predicate selection; no rank comparison. |
| “Above HIGH” as numeric ordering | BENCHMARK_UNDERSPECIFIED | No public ordinal comparator, priority sort or rank-dependent result in the frozen contract. Do not impose an ordinal rule. |
| Create and defaults | REPRESENTED | Valid nonblank title, verbatim description, optional UTC due date/null, input priority or NORMAL; fresh unique nonblank ID, pending, UTC current creation instant. Success `R` equals the *entire* persisted row selected in `S'` by `R.id`; exact selection of all other IDs in `S'` equals the old population, with exactly one extra identity. #10–12, #43 and typed equality express insertion and framing without an insertion primitive. |
| Normal list | REPRESENTED | Successful result equals the complete population sorted ascending `(created_at,id)` (#43), including completed and CRITICAL; `S'=S`, including absent-storage read. |
| list-high | REPRESENTED | Result equals *all and only* rows whose priority equals HIGH, including completed HIGH, in the same ordering; `S'=S`. CRITICAL and all other values excluded. |
| Complete | REPRESENTED | Exactly one keyed pending target changes only status to completed; result equals that complete post-target, all other target fields and all unrelated rows unchanged. Missing ID: `task_not_found`; completed target: `invalid_transition`; both preserve stored bytes. Conditional typed #45 outcome plus keyed exact selection/frame. |
| Delete and overdue inherited baseline | REPRESENTED | Delete returns the exact removed target and preserves all other rows; missing ID fails unchanged. Overdue returns exact pending, dated rows strictly before current UTC instant, sorted normally and without write. Clock evaluation needs an observed clock binding to check a close boundary. |
| Migration, defaults, and count | REPRESENTED | Valid unversioned v1 or version-2 envelope selects *all* pre-state rows as legacy conversion candidates. #44 preserves each identity and every present field, defaults v1 priority to NORMAL and v1/v2 missing due date to null, writes version-3 envelope. #30 requires `cardinality(candidates,O.migrated)`. Already-prioritized v2 rows still count. Current/absent selects the empty population, yields numeric zero, leaves state unchanged; legacy read fails `migration_required` without write. |
| Invalid inputs/state and failed-operation byte preservation | REPRESENTED | Typed validity conditions and #45 error alternatives distinguish `invalid_title`, `invalid_due_date`, `invalid_state`, `migration_required` and target errors; failure preserves raw durable endpoint. The exact CLI diagnostic for syntactically invalid priority is BENCHMARK_UNDERSPECIFIED. |
| JSON CLI, stable operation mapping, persistence and artifact integrity | NON_SEMANTIC_GAP before implementation | Interface/encoding, compiler lowering, instrumentation, observation and provenance work, not #31 semantics. |

The relational create and completion frames quantify over every keyed identity,
including empty and arbitrarily large finite populations. Migration's candidate
predicate depends on the *envelope version*, not missing priority. No
`CORE_SEMANTIC_GAP` was found in the abstract 30-candidate composition, so
generation proceeded without #31. This gate is an expressiveness judgment;
it does **not** assert that the earlier restricted `contracts.py` validator can
parse the entire B01 contract. Nullable due dates, integer outcomes, versioned
input and record-valued outputs require typed lowering. The R5.11 case checker
implements these rules in a separate prospective adapter, not a frozen general
semantic schema or a universal validator.

## 2. Candidate, provenance and execution paths

`benchmark/semantic/b01_integration_r5_11.py:build` deterministically renders
`b01_target_r5_11.py` into the distinct
`benchmark/results/phase5c/r5_11_candidate/task_manager.py` and
`provenance.json`. The template implements B01-only v3 CLI behavior; it is
not copied over the historical executable. The manifest links each semantic
operation (`create`, `list`, `list-high`, `list-overdue`, `complete`, `delete`,
`migrate`) to `unit_<operation>`, `store_tasks`, an operation contract-clause
digest, aggregate contract digest, template digest, generation ID and artifact
SHA-256. The checker recomputes these values and hashes the deployed artifact
before trusting any event. This is drift detection, not a signed build or proof
that translation is correct.

The candidate owns the operation entry and `commit` persistence boundary. Each
actual subprocess call with instrumentation enabled writes its own sidecar
event: operation/boundary/persistence/generation/invocation IDs, parsed concrete
input, decoded pre-state, typed success/error outcome, decoded post-state and
attempted-write report. It reads the file again after the operation rather than
claiming the write buffer as durable post-state. Normal CLI stdout/stderr and
exit codes do not depend on the event. The independent runner chooses argv and
invocation ID, reads `tasks.json` bytes/decoded state before launch, captures
real stdout/stderr/exit, and reopens the file after termination **before**
reading the event. The challenge compares all IDs, argv/input, public result or
error, pre/post values, and raw unchanged endpoints for reported no-write;
conformance is invoked only for `GROUNDED` events. Raw hashes expose byte
changes that decoded equality could miss. Event construction is in the
generated candidate; tests do not synthesize execution records.

The evaluator composes the selection/order/frame/default relations over the
challenged tuple and invokes the actual prospective `cardinality.evaluate` on
the selected legacy IDs and typed `migrated` integer. This B01-specific lowering
is independently checked against public/durable endpoints, but is not yet a
general-purpose declarative #45 compiler. In particular the checker assumes
valid applicable source states in the selected success cases. These are
integration limits, not extra semantic constructs.

## 3. Grounding and semantic results (selected observed cases)

`benchmark/harness/test_b01_integration_r5_11.py` generates disposable fresh
builds and invokes real processes. The persisted candidate uses the same
deterministic build. Every listed positive verdict had matching provenance,
internal evidence, independently captured public output and independently
reopened durable endpoints.

| Actual operation/state | Grounding | Case-scoped conformance |
| --- | --- | --- |
| Absent-storage list; NORMAL-default, HIGH and CRITICAL creates, with returned row matching persisted row and all prior rows preserved | GROUNDED | CONFORMANT |
| Normal list after creates and a completion, complete sorted collection, no write | GROUNDED | CONFORMANT |
| list-high with NORMAL, HIGH and CRITICAL (also after HIGH completed and CRITICAL completed), exact HIGH only, no write | GROUNDED | CONFORMANT |
| Complete HIGH/CRITICAL, preserving other rows and target fields; already-completed and missing-target errors, unchanged file | GROUNDED | CONFORMANT |
| Delete CRITICAL and preserve remaining rows | GROUNDED | CONFORMANT |
| Absent-storage migration (0); v2 three already-prioritized HIGH/LOW/NORMAL records (3), repeated v3 (0), unversioned v1 default (1) | GROUNDED | CONFORMANT |

For v2, three already-present priorities are preserved, due dates defaulted,
and the numeric count is **3**: #30 relates the entire selected legacy
population to the integer outcome. Counting missing priorities would yield
zero and fail. The version-3 post-state was independently reopened. An empty
legacy envelope and controlled exact-time overdue invocation were not included
in grounded positive cases; the contract is not a universal execution proof.

**Fault isolation:** A disposable `wrong_count` generated variant actually
converts one v2 row but publicly returns 2. Its internal outcome and durable
report agree with independently observed reality: **GROUNDED + NON_CONFORMANT**.
A separate `false_post` variant converts that same row but reports pre-state
as its post-state: **GROUNDING_FAILED**, conformance **not evaluated**. Editing
the deployed disposable artifact after manifest generation invalidates
provenance and similarly prevents trusted conformance. The primary candidate
does not contain either fault.

## 4. Frozen acceptance and historical comparison

The **original unmodified** frozen B01-profile regression against the new
candidate: **7 methods, 5 passed, 2 B02 skips, 0 failure events**. It covers
the inherited lifecycle, overdue fixture, migration/corruption and B01
priority/migration methods. R5.9 recorded the same **5 passes/2 skips** on
the separately checkpoint-pinned historical B01 executable. The two agree at
these frozen observable acceptance endpoints; no identity of source, algorithm,
trace format or internal representation is claimed. The historical executable
still has no R5.7 B01 internal event and its original acceptance result is
**not** retroactively grounded. The corrected R5.2.2 carrier remains the
authoritative historical post-B16 acceptance state, not this new B01-only run.

## 5. Accounting, adequacy and limits

Prospective vocabulary: **30 candidate core / 46 categorized raw entries**;
historical numbered inventory remains 45. R5.11 adds **zero** numbered core
constructs. Its template compiler, B01 binding, sidecar event, artifact
provenance, independent captures, challenge, adapter evaluator and fault
variants are unnumbered implementation/verification machinery, not #31.

**B01 semantic adequacy: YES at the abstract relational expressiveness gate.**
The 30 candidates can constrain arbitrary valid B01 populations and inputs,
subject to the genuinely unobservable priority comparator/CLI diagnostic and
explicit clock binding. This does not certify the restricted prototype schema
as a complete generic compiler or establish implementation correctness.

**B01 grounding adequacy: YES for the observed operation/file boundary.**
The actual candidate emits challenged per-operation evidence for stateful and
read-only calls; false reports and artifact drift are rejected. This does not
prove coverage of every possible filesystem effect or intermediate write.

**Observed conformance:** all grounded primary-candidate cases above are
CONFORMANT; the grounded disposable wrong-count case is NON_CONFORMANT. The
false-post and drift cases are GROUNDING_FAILED and have no trusted semantic
verdict. Acceptance and conformance are separately recorded.

`UNIVERSAL_IMPLEMENTATION_CORRECTNESS_ESTABLISHED = NO`.

Limits: selected finite cases, no all-input proof; no checked general-purpose
#45 lowering of full versioned/nullable heterogeneous B01 contracts; clock
instant not independently pinned for close-boundary overdue; no independent
intermediate-write trace, fsync guarantee, undeclared-sink audit, concurrency
model or hostile-manifest defense. The candidate is a prospective B01-only
integration, not a new benchmark history, format freeze or B17 exposure.

**Exact next step:** turn this case-specific relational lowering into a checked,
typed, versioned declarative #45 contract evaluator (including optional/null
fields, integer results, error alternatives and controlled clock binding),
then challenge it on new valid states and an independent domain before any
language/benchmark freeze. Keep R5.2.2 authoritative and Phase 5C paused.

Verification: focused R5.11 four tests OK; full benchmark harness 141 tests
OK (before the last added focused assertions, which were subsequently rerun
and passed); application/compiler suite 31 tests OK; frozen B01 profile on the
persisted candidate 5 passed/2 skipped/0 failures; `git diff --check` passed.

R5_11_B01_END_TO_END_VALIDATED
