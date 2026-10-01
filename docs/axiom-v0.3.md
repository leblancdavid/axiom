# Lykoi v0.3: lifecycle and semantic safety

The v0.2 model and validator remain available for historical documents. The
v0.3 serialization adds `state_machines`, `transitions`, explicit `requires`
authority on behaviors and migrations, and structured invariant predicates.
All references use stable IDs; JSON and Python are not the meaning of these
constraints. The closed-world validator is normative beyond JSON Schema.

## Lifecycle

`ax:machine:task_lifecycle` binds the status field to the `TaskStatus` enum.
Creation must initialize it to `pending`. `ax:transition:task_complete` names
the sole allowed `pending → completed` transition, its `fn_complete` trigger,
source-state guard and state-write effect. An update assigning a lifecycle
field without a matching `performs` reference is invalid Lykoi. Changing the
assignment, guard, target, or trigger inconsistently is rejected before code
generation. The runtime checks the source again before applying a transition.
An ID-bearing transition scenario supplies a valid source record and lookup;
the integration suite executes the transition and checks its target and that
repeating it fails without changing persisted state.
No `completed → pending` transition exists. Deletion is collection removal,
not a Task.status transition. Guards are currently required; transition
effects are limited to state writes. This is structural validation, not model
checking or a concurrency guarantee.

## Resources and least authority

`cap_store` names the JSON storage resource. `cap_task_read` and
`cap_task_write` represent separate, scoped access to it. The clock and ID
provider capabilities are independently granted. `requires` declares the
exact authority a behavior or migration needs; `effects` describes what it
does. The validator checks both, including excess grants. `fn_list_overdue`
has read and clock authority, never write authority. This is a semantic
permission model enforced during validation; the current Python backend is
not an OS sandbox against modified generated code or independent processes.

## Invariants and evidence

Structured predicates support `NOT_EMPTY`, `IN`, and `LIFECYCLE_STATE`, with
field IDs and, where needed, a machine ID. The existing unique-field and
record-validation invariants still apply. A `query_exclusion` invariant
declares that `list_overdue_tasks` cannot return completed tasks: the
validator checks its field-equality filter excludes `completed`. Completed
records may still have historical past due dates. Unknown predicate forms
are rejected; no Python expression is canonical Lykoi.

`python -m air_compiler.cli safety MODEL` reports validated model counts, each
invariant's evidence and the invariants relevant to each mutating behavior.
`STRUCTURALLY_GUARANTEED`
currently applies to closed-world query exclusion; stored-state constraints
are `RUNTIME_ENFORCED` by load and pre-write checks. `SCENARIO_VERIFIED` is
reserved for a runner that supplies execution evidence, and `UNVERIFIED` for
declared constraints without enforcement. Neither an empty violation count nor
passing scenarios is a formal proof or an accuracy score.

Impact paths retain their conservative reachability. `semantic_classification`
adds transition, contract, capability, direct, or general dependency reasons;
it does not discard reachable entities. Plans validate the entire candidate
before generation, and their transformation group list includes machines and
transitions. Historical Phase 3 experiment baselines remain pinned to their
original model and should not be reapplied to v0.3.
