# R5.33 — Cross-Shape State Evolution Review

Prospective independent review, 2026-10-03. Audit recorded before any compiler
changes. Entry point: `benchmark.semantic.current_pipeline`.

## 1. Same-shape assumption audit

| Location | Assumption | Classification |
| --- | --- | --- |
| R5.4 operation-contract halt, lines 77–83 | before/after of one compatible state type | SEMANTIC (historical provisional restriction) |
| contracts.py validate/_term_type/validate_values | one record schema for all four slots | HISTORICAL_ONLY |
| operation_contract.py; state_relations.py | one schema for before/after fixtures | HISTORICAL_ONLY |
| typed_lowering_r5_12.lower | both slots use contract.state | HISTORICAL_ONLY |
| generative_r5_13.py and its runtime/evidence | one state declaration | HISTORICAL_ONLY (pinned reproduction) |
| unified_types_r5_27.typed | closed AST has one state; outcome post slot repeats it | TYPE_SYSTEM |
| unified_types_r5_27.typed state relations | one collection, field and identity type serves both sides | TYPE_SYSTEM |
| unified_types_r5_27.checked_plan | slots.pre == slots.post; one state passed to relation planner | CHECKED_PLAN |
| refined_generator_r5_28._relational | one collection path/type and implicit unchanged outside frame | LOWERING |
| refined_generator_r5_28.generated_unit | post starts as pre; same collection path on both sides; GeneratedUnit.state_shape | LOWERING |
| refined_generator_r5_28 legacy typed/render | duplicate state slots and shallow updates | HISTORICAL_ONLY on current checked path |
| current_pipeline.checked | every operation equals application's single state | TYPE_SYSTEM |
| current_pipeline.generate | first unit's state shape passed to entire dispatcher | LOWERING |
| refined_runtime_r5_28.run/_invoke/run_cli | read and commit validate with one state shape | PERSISTENCE / RUNTIME |
| refined_runtime_r5_28.run_application | all operations share state codec | RUNTIME |
| refined_evidence_r5_28.conforms | concrete types from same slots; matching collection paths; equal root keys/frame | VERIFIER |
| current_pipeline.observe/challenge | captures raw distinct bytes/values without same-shape coercion | EVIDENCE: no equality-of-types assumption |
| binding.py/observation.py/conformance.py | historical four sequence slots inherit single contract schema | HISTORICAL_ONLY |
| public_binding_r5_32/input_binding_r5_32 | input metadata only; delegates actual state boundary to current runtime | RUNTIME dependency, no independent state authority |

## 2. #45 operation-contract analysis

The historical proposal explicitly said one compatible state type; it was not
already a checked four-independent-type implementation. R5.5 separates #45 into
a typed relation on input, pre, outcome and post, without requiring whole-state
equality. Equality itself requires equal **operand** types, not equal state-root
types. Generalizing the two slot declarations leaves that semantic relation and
its universal invocation scope intact. Classify the slot gap as existing
operation-contract/type-system generalization, not a new application relation.

## 3. Existing evolution/state construct audit

* #21 transition binds before/after; #22 restricts applicability. Historical
  finite-domain validators collapse both domains; no transformation is implied.
* #44 keyed default explicitly defines target keyed row = old row plus absent
  field default, preserving identity set and every existing field. This equation
  is meaningful with different source/target row declarations if both values are
  independently typed. It does not permit arbitrary renaming/removal.
* Equality #6 compares same-typed projections across differently typed roots.
  Field/record construction can define target metadata/version without equating
  source and target roots. Existing post_equals is a bounded constructive form.
* #30 cardinality consumes the exact selected source population, not field edits.
* Exact insertion/removal/replacement frames preserve all other row fields;
  general heterogeneous per-row reconstruction is not implied by these frames.
* Selection/order preserve element type. map is specifically pointwise trim of
  strings; for_each is specifically strings. Neither is an arbitrary record map.
* sole/project/record build individual projected/constructed values, not arbitrary
  heterogeneous populations. Such stronger transformations remain unsupported.
* Evolution/link #37–42 refers to research requirement lineage/achieved history.
  It neither supplies application versions nor constructs durable values.

## 4. Existing-composition attempts

Independent domain: mineral specimen register. StateA contains accession:string,
designation:string and optional provenance:string/medium:string rows; StateB makes
medium required (a separate negative/positive fixture also omits medium entirely
from the source schema). An envelope target additionally contains revision:integer,
specimens:sequence<StateB.Record>, metadata:record<collection:string>.

| Obligation | Existing composition | Decision |
| --- | --- | --- |
| applicability | #22 with typed equals on declared revision | expressible; boundary must enforce before invocation |
| row mapping | #44 source rows to target rows, default medium | expressible add-field mapping; current AST cannot bind different sides |
| identity | #44 exact unique identity sets | expressible |
| existing fields and unrelated optional data | #44 full row preservation | expressible |
| new field | typed literal default in #44 | expressible even when absent from source schema |
| rename/remove field | not permitted by #44 equation; project can change a single row only | unsupported stronger record-population relation; not necessary for this add-field witness |
| version | equality on target revision and typed literal | expressible |
| outcome/count | #30 over pre population, typed integer outcome | expressible |
| frame | #44 row frame plus explicit equalities for preserved root projections | expressible; new root must have complete target coverage |
| envelope | #44 pre root collection -> post.specimens; target field equalities for revision/metadata | expressible as conjunction; no manual wrapping needed |

## 5. Semantic decision gate

**EXISTING_OPERATION_CONTRACT_GENERALIZATION**. Distinct slot declarations,
side-qualified collection bindings, complete target coverage and enforced
applicability are required. Existing #44 plus equalities describes the bounded
row addition and envelope promotion without inventing a record-map primitive.
This decision does not claim arbitrary schema evolution. No #31 is authorized.

## 6. Pre/post state typing

Implemented R5.33 contract profile: `state: {pre: StateA, post: StateB}` and an
existing Boolean `requires` precondition. Authoritative `typed` checks both
shapes without widening. Outcome expressions bind post to StateB. `preserve`
cannot inhabit a different post type. A same-shape R5.33 operation uses equal
slots and ordinary existing relations. R5.27 source remains the same-shape
shorthand. Versioned rules: `docs/state-evolution-r5.33.md`.

## 7. Cross-state relation typing

Existing #44 has explicit source/target projection paths on their respective
slots. Checked bindings retain source_type, target_type, source_fields, target
fields, identity, source_field/target_field identities and typed operands. An
empty path is its side's root; one field is a checked collection projection.
Equalities resolve target fields against post, not pre. Unknown fields, wrong
types, removed source fields, unmapped target fields, conflicting source/identity
groups, overlapping and incomplete target construction reject before generation.
There is no field-name-only lookup across untyped durable dictionaries.

## 8. Independent versioned domain

`benchmark/semantic/evolution_study_r5_33.py` declares a mineral specimen register
with accession/designation, optional provenance/medium and required V2 medium.
One fixture upgrades envelope rows; another promotes the legacy root collection
to a revision-2 envelope. These are non-task schemas. Optional provenance is
unrelated scientific information and must survive. A present medium=`rock`
must survive while absent medium becomes `mineral`.

## 9. Row-shape migration

The row witness reads a revision-1 envelope whose specimen medium is optional,
then commits a revision-2 envelope whose medium is required. The independently
observed pre-migration insertion adds M-4, so migration reports **4 specimens**,
not three field changes. Required/default, unchanged accession/designation and
optional provenance, exact identity population and version all conform. A
separate focused witness generates a field absent from the V1 schema entirely.
Empty populations and two compatible defaults with optional-to-required
provenance tightening also execute and conform.

## 10. Envelope promotion

The root witness reads `sequence<RecordV1>` and commits a typed record containing
revision=2, specimens=`sequence<RecordV2>` and typed metadata. The same five-
operation generated program reads/inserts legacy rows and reads/inserts V2
envelopes. The root changes from JSON array to object; neither codec pretends
these roots have one type. Both row and root cases have actual durable evidence.

## 11. Source-authority audit

Every application operation is generated by current_pipeline. Target construction
initializes an empty target of the checked root kind and fills only its checked
relations. #44 binds pre root/specimens to post.specimens; post_equals constructs
revision and nested metadata from typed source expressions. Full target coverage
is checked. The generator/runtime/verifier contain no specimen field names or
domain branches. The study module supplies source, seeds, observations and
disposable faults; it never performs the normal migration algorithm. The
Python dictionary/list operations implement checked relations, not hidden
application policy. Semantic-only mutation demonstrates source authority.

## 12. Version applicability

Checked `requires` is the existing semantic #22 precondition, generated as an
applicability predicate. It executes after concrete input/pre validation and
before operation execution. Envelope V1 declares revision=1 applicability;
current operations declare revision=2. Already-current and unknown revision=99
legacy-shaped states reject without reinterpretation/write. Collection V1 uses
the declared legacy root type as applicability; a V2 envelope is not a V1 array.
Unknown incompatible shapes reject concrete binding. State version names in
application metadata register shapes, not application predicates.

Unavailable invocations return nonzero with the existing diagnostic boundary;
they have no semantic event/verdict. This is not the deferred mapping of binding
failures to operation-declared outcomes. Normal semantic outcomes are typed.

## 13. Persistence boundary

Each generated operation descriptor contains its own pre and post shapes.
Runtime reads JSON and checks pre with PreState; after execution it validates
PostState and outcome before serialization. The same durable file is used
throughout. A concrete V2 envelope fails the V1 codec; the focused wrong-codec
check rejects it before committing. Reading pre and committing post do not
share a loose shape or mutate a deserialized pre object in place.

## 14. Atomicity limitations

Generated computation, identity checks and complete post validation precede
durable writing. Normal computation/type/applicability failures do not initiate
that write. Persistence still uses direct write_text: an interrupted/failed
write can truncate or leave partial durable bytes, and concurrent callers are
not locked. No atomic replace, transaction, fsync, crash recovery or atomic
event-plus-state commit is established. An event/output failure after commit
may leave changed state without grounded execution evidence. The observations
distinguish durable pre bytes, execution event and durable post bytes for
completed calls; they do not prove all intermediate effects or atomicity.

## 15. Outcome/cardinality

Migration's integer outcome is existing #30 cardinality over the entire declared
pre specimen population. The lifecycle includes four records (one already has
equivalent medium); all four belong to the migrated population, so count=4.
Standalone mutation/fault witnesses have three rows and count=3. No implementation
counts modified fields. Empty and multiple-default checks count population once.

## 16. Grounding

Machine record: `R5_33-evolution-evidence.json`, generated by:

```powershell
python -m benchmark.semantic.evolution_study_r5_33 --output benchmark/results/phase5c/R5_33-evolution-evidence.json
```

It retains source/manifest, external actual public operation/input/invocation/
stdout/stderr/exit, exact durable pre/post bytes and hashes, actual execution
events, and provenance/grounding/semantic verdicts. Both seven-call lifecycles
have **14/14 grounded conformant invocations**, with 12/12 adjacent byte-digest
links. Six post-migration unavailable invocations retain unchanged bytes and
have no semantic event. Two source mutations ground/conform. All five faults
ground and fail semantics. Provenance is integrity relative to source/runtime/
artifact hashes, not hostile-runtime attestation or universal proof.

## 17. Verifier integration

current_pipeline.challenge grounds actual event/public/durable endpoints, then
passes the originating contract's CheckedPlan to the existing independent
verifier. It checks input, PreState and PostState separately, applicability,
branch/tag/payload/count and target equalities. Independent keyed #44 evaluation
checks exact identities and each target row against preserved source fields plus
the declared defaults. It never invokes generated code or discards type
distinctions. Partial migration fails required target typing even when a faulty
generated runtime descriptor admits it. Behavioral evaluation remains distinct
from shared static authority.

## 18. Same-shape regression

Full current-pipeline R5.29/R5.30/R5.31/R5.32 suites pass: insertion, replacement,
removal, same-shape migration and read-only operations, including old grounded
faults/source mutations. R5.33 also generates version-specific same-shape
insertion/read operations in its cross-version applications. Equal pre/post
types reuse the ordinary relation planner. Historical locked components and
fixtures remain unchanged and their integrity tests pass.

## 19. Multi-command lifecycle

For each shape witness, one generated five-operation application performs:

`legacy read -> legacy insertion -> legacy read -> migrate -> current read ->
current insertion -> current read`.

All seven calls use one generated operation.py/runtime and durable state.json;
no unrelated application is launched after migration. Migration transforms four
specimens; post-version insertion adds a fifth. Each adjacent durable digest
matches; read-only calls preserve bytes. Both pre/post command generations derive
from that application's semantic source and checked state metadata.

## 20. Version-specific operation availability

Per-operation checked pre/post descriptors and generated #22 predicates replace
the previous application-wide first-unit codec on the current dispatch path.
Current operations reject V1 before execution; legacy read/insertion/migration
reject V2. No operation-name/domain/version-number branches exist in runtime.
Metadata selects the operation descriptor; source predicates determine revision
applicability. Historical four-element descriptors keep their same-shape fallback.

## 21. Semantic mutation

Two source-only regeneration witnesses, no compiler/runtime/verifier changes:

| Mutation | Actual durable effect | Verdict |
| --- | --- | --- |
| default mineral -> crystal | formerly absent medium becomes crystal; present rock preserved | grounded/conformant |
| metadata collection mineral-register -> curated-register | V2 metadata changes; row mapping remains intact | grounded/conformant |

## 22. Fault matrix

Faults alter disposable generated artifacts and reseal their artifact provenance.
Runtime/source/verifier semantics remain canonical. All execute real public calls
with independently observed durable results.

| Fault | Actual effect | Grounding | Semantic conformance |
| --- | --- | --- | --- |
| A | wrong medium default/new field | pass | fail |
| B | first accession replaced with wrong identity | pass | fail |
| C | transformed rows, wrong durable revision=1 | pass | fail |
| D | correct rows, wrong envelope metadata.collection | pass | fail |
| E | M-3 remains without medium; only part of required population transformed | pass | fail |

Fault E also corrupts the disposable **generated post codec descriptor** to
optional medium so that partial rows can actually reach durability. The semantic
source/CheckedPlan and independent verifier still require V2 medium. This is a
declared target-boundary fault, not weakening the normal compiler or pretending
an otherwise rejected partial execution was grounded. Fault D violates metadata
within a typed root; incompatible root forms additionally fail concrete typing.

## 23. Type-confusion negatives

Focused checks reject: V1 root projected as V2 field; V2-only field read from a
V1 selection; wrong source/target projection/field type; missing target mapping;
cross-type preserve; pre codec substituted for post; inconsistent identities in
two defaults; V2 operations on V1; revision 2/99 on revision-1 migration. Plan
source/fact mutation fails closed. The focused concrete wrong-codec invocation
fails post validation before persistence. These are type/binding negatives, not
grounded operation-declared errors.

## 24. CheckedPlan authority

Independent slots, input/outcome facts, cross-state source/target field/collection
bindings, capabilities, applicability node identity and checked evolution branch
IDs flow through the existing authoritative analyzer. All are sealed. Generator
and verifier consume the recorded evolution mode, rather than infer state types
again. A poisoned analyze after checking still permits target unit emission and
independent conformance. No competing migration-specific checker is introduced.
Application version registration is checked metadata; version predicates remain
ordinary analyzed semantic facts. Field identities are source-bound scoped paths
and node IDs, not globally nominal schema IDs; plans remain in-process.

## 25. Current-pipeline invariant

The only new generated application path is `benchmark.semantic.current_pipeline`.
Existing analyzer/emitter/runtime/evidence modules are its components. R5.33
standalone historical render rejects explicitly and directs application assembly
through the current entry. `evolution_study_r5_33` is fixtures/evidence and
`verify_evolution_r5_33` is verification administration; neither is a compiler.
No cross_shape_pipeline, migration pipeline or prospective compiler fork exists.

## 26. Construct #31 review decision

No #31 review is required for the demonstrated keyed-default/root-equality
composition. #45 generalization suffices together with existing #44/#22/#6/#30
and typed field/record construction. Evolution metadata cannot supply behavior.
Arbitrary row renaming/removal or heterogeneous per-row reconstruction remains
unsupported; this review does not classify all such requests as semantically
adequate. A future requirement for that stronger relation needs its own exact
composition review, not an automatic migration primitive or hidden compiler map.

## 27. Layer ownership

| Machinery | Ownership |
| --- | --- |
| existing four-slot relation, keyed default/equalities/precondition/cardinality | CORE SEMANTICS (existing meaning; #45 signature generalization) |
| separate root/element/field typing, complete construction and no widening | TYPE SYSTEM |
| source/target facts, applicability/evolution IDs and seal | CHECKED PLAN |
| version shape registration | checked application/binding metadata; not historical EVOLUTION METADATA |
| historical #37–42 links | EVOLUTION METADATA; preserved, not an application implementation |
| target initialization/checked projection population | LOWERING |
| per-operation pre/post codec validation and durable serialization | PERSISTENCE |
| generic applicability/operation dispatch | RUNTIME |
| independently typed keyed equations and target equality checks | VERIFICATION |
| specimen fixtures, public/file/event challenge, mutation/fault records | EVIDENCE |
| full-discovery restriction runner | verification administration |

## 28. Capability matrix

`R5_24-type-matrix.json` preserves prior profiles and adds
`r5_33_state_evolution`: pre_state_type, post_state_type, cross_shape_generation,
cross_shape_persistence, cross_shape_grounding, cross_shape_verification and
version_specific_operation_binding. All seven are supported **within the
documented bounded relation/profile** and have independent witnesses. The
focused/full suite validates dimension coverage, core count and current entry.

## 29. R5.23 blocker reassessment

**Cross-shape state evolution: RESOLVED_INDEPENDENTLY** for explicitly typed
keyed default/add-field and root-envelope transitions with whole lifecycle and
independent verification. This does not claim arbitrary migration, frozen
request transfer or implementation correctness beyond the observed scope.
Frozen transport remains **UNRESOLVED**, separately. Suppliedness/well-formedness
retains R5.32's independent resolution; malformed-input outcome mapping remains
**PARTIALLY_RESOLVED** and was not investigated here. B02 was not retried.

## 30. Remaining blockers and verification

Frozen transport and operation-declared mapping of pre-invocation failures remain
separate. Constructive limits: one-level root collection projections, no arbitrary
row rename/remove/map, no nominal version sum type, no deep record-path evolution.
Registered shapes are structural; overlapping schemas require explicit source
applicability. Persistence limitations are in section 14. Optional field absence
is distinct from nullable data and remains typed.

Environment: Windows, **Python 3.14.3**, executable reported by `py -0p`:
`C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe`.
The prior R5.32 temporary Python 3.12 executable is unavailable here; this is
an environment observation, not a test failure. Tests run directly in this
workspace; no LF mirror was necessary, and historical hash checks pass.

| Check | Actual result |
| --- | --- |
| full discovery `python -m benchmark.semantic.verify_evolution_r5_33` | 308 discovered, 307 pass, 1 explicit restriction skip; no failures/errors; final code run 66.302 s |
| architecture/grounding/semantic/binding and relevant R5.10–R5.32 suites | included and pass in full discovery |
| R5.33 focused evolution suite | 10/10 pass, final focused run 2.154 s; also included in full discovery |
| application/compiler discovery | 31/31 pass |
| model validation with PYTHONPATH=src | OK |
| safety | 0 capability violations, 0 invalid transitions |
| capability matrix | passes in focused/full suites |
| git diff --check | pass; Git LF→CRLF notices reported separately |

The full runner excludes exactly
`test_phase5e.CapabilityProfileTests.test_read_only_validation_of_both_continuation_states`,
which would internally execute frozen B02 acceptance. Its historical source is
unchanged. Historical diagnostic regression tests retain their pinned meanings;
their execution is not a new B02 retry or frozen acceptance. Initial lifecycle
fixture edits exposed two real framed-record type mismatches after adding insert
commands; the semantic fixtures were corrected to update their associated literal
types/values, then focused/full checks passed. A subsequent registration-order
refactor produced one real R5.29 diagnostic regression (`selection needs sequence`
instead of the required unregistered-state binding rejection); the early signature
registration check was restored, retaining authoritative checked facts downstream.
The affected R5.29 suite passes 5/5 and the final full discovery passes. These
were actual fixture/regression errors, not Python or line-ending failures.
LF→CRLF notices are not diff-check failures.

## 31. Construct/system accounting

30 candidate core semantic constructs; no #31. Historical 46-entry raw categorized
inventory remains unchanged. This is a versioned #45 slot/type generalization and
checked relation/lowering/persistence/verifier integration, not a new core
migration primitive. R5.31 single authority and R5.32 binding/semantic distinction
remain intact. No canonical task model, generated application, frozen requirement,
oracle, historical runtime/schema/hash lock or old evidence was edited.

B02 is not retried; frozen B02 acceptance is not run; frozen B02 transport is not
implemented; Phase 5C remains paused; B03 remains untouched; B17 remains unexposed
and unclassified; semantic-first format remains globally unfrozen; R5.2.2 remains
historical benchmark authority; universal implementation correctness is not claimed.

## 32. Exact recommendation for R5.34

Begin **Checked Transport Binding Review** independently on a non-task generated
application. Audit public invocation grammar, input suppliedness/decode, operation
availability, public result/error/exit mapping, missing-store policy, shared-store
selection and provenance against checked metadata. Keep transport policy separate
from semantic input validity, state evolution and operation-declared outcomes.
First record a semantic/ownership decision; only then implement justified generic
bindings through current_pipeline and the R5.32 boundary, with actual whole-
lifecycle grounding, source/metadata mutation and faults. Preserve R5.33 typed
pre/post contracts. Do not authorize a B02 retry/acceptance, Phase 5C restart,
B03 advance, B17 exposure or format freeze from this recommendation. Atomic
persistence hardening is a separately scoped future boundary, not established here.

The gate follows explicit composition, checked source authority and actual row/
root durable evidence, whole lifecycle and fault discrimination, not test count.

R5_33_CROSS_SHAPE_EVOLUTION_VALIDATED
