# R5.30 — Current pipeline hardening and structured assembly (prospective)

**Decision: `R5_30_CURRENT_PIPELINE_HARDENING_PARTIAL`.** This is an
independent non-task same-shape development checkpoint, not a benchmark retry.
The new development entry remains `benchmark.semantic.current_pipeline`.

## Type and ordering authority audit (parts 1–6)

| Location / question | Classification | R5.30 disposition |
| --- | --- | --- |
| `unified_types_r5_27.typed/analyze`: expression shapes, scoped presence, instant operands, branch payload, relation operand/field types | authoritative semantic typing | source-bound checked plan retains operand types, witness dependencies and orders; relation conjunctions are now also planned once by `checked_plan` |
| `unified_types_r5_27.checked_plan.visit`: re-calls `analyze` on selection source/relations after `typed` | SEMANTIC_REDERIVATION | remains; source-bound facts are incomplete for arbitrary expression nodes |
| `typed_lowering_r5_12._compile` reached by `analyze` for older expression kinds | LEGACY_DUPLICATION | remains as the historical expression checker; not a feature-based compiler fallback |
| `refined_generator_r5_28.typed` / `ordering_plan` / legacy `render` branch | LEGACY_DUPLICATION | still callable by historical standalone users; current entry's checked-plan branch does not invoke these checks |
| `_relational`: operand type, field identity/type, collection shape and relation overlap | SEMANTIC_REDERIVATION + TARGET_CONSTRAINT | current path calls once from checked-plan construction; emitter reads `plan.relations` instead of replanning. Operand shapes come from `plan.operand_type`; overlap/framing remain checked planner constraints. The checker also checks some field/operand types independently, so *whole-path* duplication remains. |
| `generated_unit`: source-bound plan and relation lookup | SAFETY_ASSERTION | stale/alien plans reject, unsupported transitions reject explicitly |
| `refined_evidence_r5_28.conforms`: `_type` of independently observed input/pre/post/payload | VERIFIER_REQUIREMENT | retained: actual observed data still needs checking, even after static typing |
| `refined_evidence_r5_28.conforms`: contract interpretation and state relation equality | VERIFIER_REQUIREMENT | independent expected behavior, not target-source inference; current challenge supplies a checked plan, but separately reconstructs it at challenge time |
| `refined_evidence_r5_28` legacy path without plan | LEGACY_DUPLICATION | historical standalone compatibility only |

Authoritative checked facts presently include source digest/identity, guard
dependencies by source-node identity, typed relation operands, ordered element
and ordered `(key, effective type)` sequence, checked relation conjunctions,
and optional record-field references. Declared input/state and branch payload
types remain in the validated semantic source, while typed results of **all**
expression nodes, field bindings and outcome payloads are not yet materialized
as independent checked-plan facts. The emitter still uses the source AST to
choose operations; this is a remaining semantic-authority seam, not a second
application entry point. A stale plan fails before generation.

Ordering is established by `unified_types_r5_27.ordering_plan`, including
presence-refined keys, string/integer/instant types and source key sequence.
The generator uses only `plan.orders[id(expr)]` for the current entry; instant
keys are converted at the target boundary. The verifier reads the same plan
but evaluates an independently observed multiset and nondecreasing
lexicographic keys, allowing permutations of fully tied rows. Direction is not
defined and is not inferred from Python sorting. The legacy generator's
`ordering_plan` still duplicates key orderability on the standalone path;
`interpret(select)` also re-analyzes a source to obtain its item type. This
prevents claiming fully unified ordering/type authority end to end.

## Assembly, determinism, provenance (parts 7–11)

R5.29 called `emitter.render` for each contract, cut from `def execute(` to
`if __name__`, renamed the function via string replacement and concatenated
the resulting Python text before adding a dispatch table. The cut discarded
each fragment's imports, entry binding, type and source identity; it assumed
exact spelling and placement of two rendered-source sentinels and a function
name. Rendered Python was being treated as compiler IR.

The current checked path calls `generated_unit(contract, plan, symbol)`.
Its minimal immutable `GeneratedUnit` holds semantic operation identity,
checked contract digest, declaration lines, input/state and outcome binding
shapes and required import names. `current_pipeline.generate` constructs all
units before rendering one application artifact and dispatcher. No rendered
operation file is parsed, sliced or recomposed. Declaration lines are still
target-specific strings, rather than a target-neutral statement IR; this is
minimal structured assembly, not a general optimizing compiler IR. Existing
operation order is insertion order in the semantic application map, with
index-based symbols. For identical semantic source and runtime the artifact,
manifest, operation order and per-unit digests are byte-identical across two
independent generation directories. Runtime invocation UUIDs, external IDs
and clock readings are intentionally nondeterministic. The manifest binds
application digest, operation-name → source digest, artifact and runtime hashes
to a generation digest. Observed runtime events bind generation, invocation and
operation name; the independent challenge verifies source/unit and bytes before
conformance. Reordering operations changes index-based generated function
names; unrelated unit *source digests* stay stable, but generated symbol
identities are not stable under reordering.

## Capability inventory and current-path regressions (parts 12–14, 19–25)

The versioned machine-readable current-path assessment is
[`R5_24-type-matrix.json`](R5_24-type-matrix.json), key
`r5_30_current_pipeline`. Historical-only and prospective-only classifications
in the earlier keys are preserved. On the present evidence:

| Current-pipeline demonstrated | Witness |
| --- | --- |
| exact selection, guarded optional refinement, before, instant ordering, external insertion, fallback expression, cardinality, removal, replace_field, projection, record-valued outcomes | publication application, R5.29 eight-call chain, A–D; R5.30 structurally regenerated chain |
| normalization (`map`/`stable_unique`), integer/string lexicographic ordering, overlapping keyed defaults, same-shape durable version update/count | new inventory-domain `test_current_entry_normalization_order_and_same_shape_defaults`, three grounded conformant operations |
| optional absent and present persisted records | new archive omitted-input round-trip test |
| unintended durable write on preserve/read branch | new operation-caused E test, grounded true/conformant false |

Legacy `refined_generator_r5_28.render` still serves standalone historical
test fixtures; `current_pipeline` has no feature dispatch to pinned generators.
Unknown state relations and unsupported transitions reject in checking or
generation. There is **one designated current non-task application entry**,
but that alone does not close the duplicated semantic authority inside its
shared analyzer and emitter. The v0.3 `air_compiler` is a separate versioned
task-manager backend, not another current entry for this prospective subset.

The publication application uses `create`, `query`, `ordered`, `replace`,
`remove` on one durable file. The unchanged R5.29 eight-call test now
compiles through the structured-unit path: create A, create B, refined query
A, ordered query B/A, guarded replace A, query new A, remove A, query empty.
Each independently observed post byte sequence equals the following call's
pre bytes; eight operations ground and conform. The R5.29 semantic-only
cutoff, ordering-key, replacement-value and removal-target mutations also
regenerate through this path with no runtime/verifier edits. Optional query
field and projection mutations were not independently run here. New supported
applications invoke `current_pipeline.generate(model, directory)` then
`observe`/`challenge` without selecting an internal versioned compiler;
the inventory-domain test is an executable example. A–D again ground true
and conform false in the full harness.

## Optional input construction and fault E (parts 15–18, 20–22)

Typed optional record fields permit absence, not null. `fallback(optional<T>,
T)` yields `T` on omission, so a record field built from a fallback becomes
**present**. A direct optional field reference inside a typed record should
instead copy the field only when it exists. R5.29 always emitted the dictionary
lookup, raising on omitted input. The checked source now marks direct optional
record references; generated construction and independent semantic
interpretation both conditionally include the field by parent-record
membership. They do not apply fallback to `seen`. The optional `preferred`
input continues to provide a fallback for required `label`.

The new archive test constructs A with omitted `seen`, B with explicitly
supplied `seen`, persists both, then reads via guarded `present(seen) AND
before(seen, cutoff)`: A remains absent and excluded, B remains present and
refines to `instant`. It grounds and conforms on both writes and the read,
with read-only bytes unchanged. This covers absence versus presence; it does
not extend input suppliedness to malformed-input typed outcomes.

Fault E modifies only the disposable generated `query` function, changing
its `post = pre; write = False` into a write that changes B's label while
returning the correct public A query result. The test updates the disposable
artifact manifest, independently reads pre and post bytes around **the same
call**, and challenges the execution event. Result: provenance valid, grounded
true, conformant false; B's changed durable label is independently visible.
The next call starts with the corrupted post bytes, differing from the valid
pre-chain state, but the failing conformance of the faulty read is the direct
detector. A–D remain distinct executable faults, not continuity-only checks.

## Gate, blockers, accounting and R5.31 (parts 26–29)

R5.23 optional refinement and instant ordering are demonstrated through the
current checked application entry; classify their *supported same-shape
subset* as `RESOLVED_IN_CURRENT_PIPELINE`. Do not extrapolate to frozen
whole-program B02 or unsupported representations. Separate unresolved
classes: suppliedness/well-formedness, malformed-input typed outcomes,
cross-shape state evolution and frozen transport binding. Further architectural
blockers: redundant checker/plan analysis and legacy expression/type/order
inference, incomplete explicit expression/payload fact closure, target-specific
declaration strings and insufficient capability-by-capability fault/mutation
coverage. Consequently the requested fully authoritative compiler gate is
**partial**, despite one entry and structured assembly.

Candidate core semantics remain **30**; no #31. Generated units, provenance
and optional-field emission are compiler machinery applying existing typed
record membership. No B02 retry, complete B02 generation, new frozen B02
acceptance, B02 grounding/conformance or benchmark advancement was conducted
as R5.30 work. The full historical harness includes pre-existing B02
diagnostic fixtures and nested historical tests, which are not a new retry.
Phase 5C remains paused, B03 untouched, B17 unexposed/unclassified, format
globally unfrozen, R5.2.2 historical authority, universal correctness unclaimed.

**Exact R5.31 recommendation:** finish expression-level authoritative fact
closure in `unified_types_r5_27` and make current emitter/semantic verifier
consume the source-bound facts, retire the current-path dependence on legacy
type and order inference, then challenge independent semantic mutations and
faults for every matrix row before reconsidering the architecture gate. Keep
the same current entry, no new semantic capability and the benchmark firewall.

Verification at this checkpoint: full harness 278/278 (includes R5.10–R5.29,
architecture/grounding/semantic and four new R5.30 tests), application/compiler
31/31; model validation OK; safety 0 capability violations, 0 invalid
transitions; matrix JSON valid; `git diff --check` passed. LF→CRLF notices,
if any, are separate from test failures.
