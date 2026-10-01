# Axiom v0.2 semantic model

## Authority and boundary

The Axiom document is canonical; JSON is a serialization, and the Python
backend is an implementation artifact. `schema/axiom-v0.2.schema.json`
specifies the serialized shapes. `validator.validate` provides the normative
cross-entity, type, operation, effect and contract checks which JSON Schema
cannot express. Unknown semantic kinds/fields are rejected. Older v0.1
documents remain valid input for inspection/diff, but generation of v0.2
applications uses `axiom_version: "0.2"`.

An entity ID is a stable, globally unique string, independent of its display
name. Existing Phase 1 IDs are retained. New IDs may use `ax:<kind>:<opaque>`;
no spelling or prefix conveys operational meaning. Built-in type references
are `prim:string` and `prim:timestamp`; they are reserved IDs. External CLI
tokens, flags, enum values and error codes are boundary values, not identity.

## Entities

| Entity | Meaning and references |
| --- | --- |
| Application | Identity of the application. |
| Type | `enum` with allowed values, `record` of ID-bearing typed fields, or `list` of a record type. |
| Capability | `json_file` storage with explicit missing-file policy, `utc_clock`, or `uuid_v4`. These are declared environmental access points. |
| State | Typed collection, storage capability, key field, schema version and invariant IDs. |
| Invariant | Unique field or rules applied to every stored record; checked on load and before writes. |
| Error | Stable ID with an external error code. Behaviors and preconditions refer to its ID. |
| Behavior | Typed inputs/output, operation, dependency IDs, reads/writes, declared effects, preconditions, assignments, postconditions and errors. |
| Contract | ID-bearing precondition (`conditions`) or postcondition (`guarantees`) owned by a behavior; invariants are state-owned contracts. |
| Command | External token and flags mapped to a behavior's input IDs, or the explicit `migrate` command mapped to a migration ID. |
| Migration | Version-to-version, constant field additions to one state, with explicit effects; applied by the generated `migrate` operation. |

Relationships are indexed in `semantics.index`, including `owns`, `type`,
`depends_on`, `reads`, `writes`, `assigns`, `filters_by`, `constrained_by`,
`exposes`, `may_fail_with`, and `migrates`. `inspect` returns both incoming and
outgoing edges. A dependency is not inferred by searching generated Python.

## Effects, contracts and operation algebra

The effect set is extensible; v0.2 recognizes `state_read`, `state_write`,
`file_read`, `file_write`, `clock_read`, and `random_id`. Pure computation has
no effects. File effects arise from the current `json_file` capability, not
from the abstract meaning of state access. The validator checks declared
footprints and effects against those implied by the operation and assignments;
an undeclared or unused effect is an error. Migrations likewise declare their
read/write effects.

The supported operations remain `create`, `list`, `update`, and `delete` on
one record collection. Assignments use typed literal, input, input with a
default, or capability. `list` can select records via a typed `field_equals`
predicate before sorting; this is a semantic query, not injected Python.
Optional CLI inputs must be bound to a defaulted assignment. Conditions are
ordered preconditions with a referenced failure ID; postconditions check
result fields or membership, absence or sorted results at runtime. A
`result_field_equals_assignment` postcondition checks a field against its
input/default assignment. The validator rejects known contradictions but does
not prove arbitrary properties. State invariants run before returning a
result or persisting a mutation.

State schema version 1 uses the historical JSON list. Version 2 uses an
envelope `{ "schema_version": 2, "records": [...] }`. A legacy list is never
silently rewritten during normal behavior: normal commands return
`migration_required`; `migrate` applies model-declared defaults and validates
the resulting state before atomic replacement. No arbitrary migration scripts
are allowed. The current migration operation supports one state and additive
constant fields; more complex migration is a language capability gap.

## Tools and provenance

`axiom inspect MODEL ENTITY_ID` (currently invoked through
`python -m air_compiler.cli`) reports entity structure, references,
dependencies and effects. `axiom diff BEFORE AFTER` compares validated
entities by ID, attributes and relationship edges; affected entities include
direct changes and immediate dependents, with explicit causes. It does not
prove behavioral equivalence or compute a transitive execution trace.

Generation is deterministic for the same model, compiler version and backend
configuration. The generated header identifies Axiom as its producer. The
adjacent manifest records compiler version, model version, artifact name,
SHA-256 and associated semantic entity IDs. Names of generated artifacts
are implementation configuration, not semantic identities.
