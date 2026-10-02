# Lykoi research log

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
