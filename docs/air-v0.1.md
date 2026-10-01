# AIR v0.1 semantic model

`air/task_manager.json` is the canonical application. JSON is only its serialization.
`air_version` pins the meaning of every supported kind and predicate; unknown kinds
are errors. All significant entities (including record fields and behavior inputs)
have globally unique, stable IDs. References resolve by ID; names are metadata.
CLI command tokens and flags are external interface strings, not entity references.

## Types and state

Built-ins are `prim:string` and `prim:timestamp` (UTC RFC 3339 with `Z`).
User types are `enum`, `record`, and `list`. A state is one typed list backed by
an explicitly referenced `json_file` capability. The file stores the list of
records directly. `missing_file: empty_collection` is the only missing-file
policy in v0.1. Invalid JSON, invalid records, and broken invariants fail with
`invalid_state`; filesystem errors fail with `persistence_failure`.

An invariant is either `unique_field` or `all_records_valid`; the latter allows
`nonblank` and `timestamp_utc` field rules. Invariants are checked on load and
before persistence. No operation may persist invalid state.

## Behavior semantics

The only kinds are `create`, `list`, `update`, `delete`. Every behavior names
its state, typed inputs/output, dependency IDs, state reads/writes, effects,
ordered conditions, assignments, guarantees, and possible failure codes.
Declared footprints must **exactly** equal inferred footprints, not merely
contain them. Every kind reads state. Create/update/delete write it. Storage
implies `file_read` and, for writers, `file_write`. Capability assignments
imply `clock_read` or `random_id` and a capability dependency.

Create evaluates assignments for every record field, rejects duplicate IDs,
appends and persists. List returns a copy sorted ascending by `order_by`.
Update and delete look up a record via `lookup`, evaluate conditions in order,
then update fields or remove the record, respectively, and persist. Delete
returns the removed record. Update leaves unassigned fields unchanged.
`record_exists` must precede any `record_field_equals` condition. Conditions
can also use `nonblank_input`. A failed condition raises its declared code
before mutation. A failed write leaves the old JSON file intact (atomic replace).
Guarantees are checked against the resulting in-memory state before returning;
an internal guarantee violation fails rather than silently succeeding.

Assignment sources are a typed input, a typed literal, or `utc_clock` /
`uuid_v4` capability. A clock yields a UTC timestamp; UUID yields a string.
`result_field_equals`, `result_in_state`, `result_id_absent_from_state`, and
`result_equals_state_sorted` are the supported guarantee predicates. Where a
literal assignment disagrees with a literal guarantee, validation rejects the
program. Guarantees are not free-form natural language.

`id_collision` is an explicit create failure: UUID uniqueness is checked, not
assumed. Each behavior must declare `invalid_state` and `persistence_failure`;
writers additionally declare any condition failures, and create declares
`id_collision`. Successful CLI commands print JSON; errors print JSON containing
`error` on stderr with a nonzero exit code. The data path is relative to the
process working directory, making isolated executions possible.

## Pipeline and validation boundary

`parser` checks the JSON envelope, `model` retains the parsed semantic entities,
`validator` checks references, types, relationships, footprints, condition and
contract consistency; `generator` emits a self-contained Python program from
a fixed runtime template and a canonically serialized validated model.
Validation errors include an entity ID or JSON path. Generator output is
byte-for-byte identical for identical AIR input. Neither timestamps nor input
file locations appear in generated code. The generator refuses invalid AIR.

This limited operation algebra is intentional: adding due-date filters later
should force an explicit, versioned semantic extension rather than unvalidated
Python snippets or a premature general-purpose expression language.
