# Axiom research log

## Phase 2 baseline and priority experiment (2026-10-01)

Baseline: `experiments/task_manager-v0.1.json` is the original Phase 1 model.
`experiments/task_manager-v0.2-before-priority.json` retains its application
behavior but expresses it in v0.2 for an application-only semantic comparison.
Both baseline and final models validate. The final model is
`air/task_manager.json`.

### Observation: finding the impact of a field addition

**Conventional Approach:** Search for task constructors, readers, persistence,
interfaces and tests, then inspect likely matches.

**Axiom Approach:** `inspect field_priority` finds its type, the creating
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

**Axiom Approach:** A typed enum, `input_default` assignment and
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

**Axiom Approach:** `migration_task_priority` declares a schema transition,
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

**Axiom Approach:** The generated header directs edits back to Axiom. The
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
