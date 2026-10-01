# Lykoi research log

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
