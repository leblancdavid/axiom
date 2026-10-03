# R5.34 — Checked Transport Binding

Prospective independent study, 2026-10-03; previous gate
`R5_33_CROSS_SHAPE_EVOLUTION_VALIDATED`. Implemented evidence, bounded to a
scalar CLI profile, not frozen benchmark transfer.

**Decision:** generic checked transport is validated across independent generated
applications, including shared-store cross-shape lifecycles. Exact frozen transport
and malformed-input operation-outcome mapping remain partial. Recommend independent
generic boundary completion as R5.35, not a B02 retry.

## 1. Public invocation audit

Classifications combine responsibility and currency; they are not exclusive.

| Invocation path | Classification | Transport/application knowledge |
| --- | --- | --- |
| generated-unit exec/direct calls in lowerer/runtime tests | TEST_ONLY; CURRENT when plan based | tests supply typed inputs/pre-state and application expectations; no public transport |
| current_pipeline.observe -> operation.py internal protocol | TEST_ONLY, BINDING, CURRENT | semantic operation/state/trace/invocation/payload/generation; domain values belong to fixtures |
| current_pipeline OPERATIONS -> refined_runtime.run_application | BINDING, CURRENT | checked dispatch/codecs/generated applicability; no public grammar |
| refined_runtime_r5_28.run_cli | GENERIC_TRANSPORT, BINDING, CURRENT auxiliary path | derives flags but argparse converts integers, bypasses R5.32 structured failures and materializes omitted booleans as false |
| generative_runtime_r5_13.run_cli | GENERIC_TRANSPORT, BINDING, HISTORICAL_ONLY locked reproduction | same early decode/presence mixing; single-operation public adapter |
| R5.32 public_adapter/public_binding | GENERIC_TRANSPORT, BINDING, CURRENT predecessor | raw JSON object and checked aliases/domains; semantic key is public operation; all semantic outcomes use one envelope/exit 0 |
| v0.3 runtime_template.main / canonical generated CLI | GENERIC_TRANSPORT, BINDING, APPLICATION_SPECIFIC supported model, CURRENT canonical track | SPEC-driven flags/migration distinction; same module implements bounded behavior/migration/defaults, without physical transport separation |
| historical b01_target/checkpoint CLI adapters | APPLICATION_SPECIFIC, HISTORICAL_ONLY | separately authored task command/storage/behavior knowledge; not current semantic authority |
| conventional/checkpoint CLI and external oracle helpers | APPLICATION_SPECIFIC, HISTORICAL_ONLY benchmark tracks; TEST_ONLY oracle | domain command/field/error knowledge in external observation, not transport compilation |

Current internal dispatch is not a complete public CLI. Historical/canonical paths
are preserved. No B02 transport fixtures were read as implementation templates.

## 2. Transport responsibility boundary

Transport selects public routes, identifies supplied raw arguments, preserves
missing keys, calls binding, invokes generated execution, encodes outcomes/failures
and publishes status. Binding converts supplied raw values to typed inputs.
Semantics defines operation meaning. Transport excludes state transitions,
predicates, fallback, normalization, migration and application validation.
Adapter durable reads are byte observations, not state interpretation; normal
transport never writes application state.

## 3. Checked transport profile

`checked_transport_r5_34.py` derives/validates machine descriptors against
pipeline.checked. Profiles map public operation to semantic key/contract digest;
public argument to slot/scalar decoder/raw representation/finite domain; checked
outcome tag to exact payload type/JSON encoding/public classification. Requiredness
and pre/post/applicability facts derive from sealed plans. Versioned rules:
`docs/checked-transport-r5.34.md`. Failure classification is public policy, never
a second branch-selection specification. No human-friendly syntax is prescribed.

## 4. Profile validation

Consumes sealed CheckedPlan slots/outcomes/digest/applicability, with invariant
checks. Nine negative categories reject: unknown semantic operation, duplicate
public operation, unknown slot, missing required mapping, incompatible decoder,
duplicate argument/slot binding, incompatible encoding, wrong output shape and
foreign outcome tag. Raw representation and finite-domain policy are also checked
through R5.32 metadata validation. A poisoned alternate analyzer confirms no
downstream retyping. Validation precedes normal artifact generation/execution.

## 5. Suppliedness preservation

Raw membership preserves omitted preferred/seen as supplied=false/OMITTED;
explicit valid values are supplied=true. Omitted keys remain absent in semantic
input and optional persisted fields. Catalogue fallback comes from semantic
source. Another real CLI test distinguishes omitted boolean from supplied JSON
false. Fault B falsely marks omitted preferred supplied and fails both transport
and input binding conformance.

## 6. Raw binding

`--units 7` remains text until unchanged R5.32 integer decoding; timestamp text
goes unchanged to the instant binder. No operation-specific timestamp parser.
Generic JSON wire parsing produces raw data, not semantic values; false enters
R5.32 as raw Boolean. Supported input bases are string/integer/instant/boolean.
Collection/nullable slots and repeated flag accumulation are outside this profile.
Finite domains are explicit interface policy, not inferred semantic guard values.

## 7. Public outcome taxonomy

| Status | Exit | Distinction |
| --- | --- | --- |
| SUCCESS | 0 | typed declared public-success outcome |
| SEMANTIC_FAILURE | 1 | typed declared public-failure outcome |
| BINDING_FAILURE | 2 | structured binding failure, operation not invoked |
| INVOCATION_FAILURE | 3 | runtime rejection, no typed outcome/event |
| TRANSPORT_FAILURE | 4 | routing/grammar or profile integrity failure |

Normal statuses emit one JSON stdout envelope, empty public stderr; integrity
failure uses stderr before trace/state access. Generated stderr/exit is captured
separately. Applicability rejection is not fabricated as a declared semantic
failure. Binding failure remains separate internally and publicly.

## 8. Output encoding

Generic encoding validates checked branch shape before serializing unchanged
payload. Actual calls cover record create, record-collection list, string mutation,
integer removal/migration count and structured record failure, with nested/optional
data preserved. Wrong payload shapes reject in focused tests. No domain serializer.
Current public envelope/streams/exits are bounded, not arbitrarily configurable.
Faults D/E fail output conformance while semantic conformance passes.

## 9. Generic CLI adapter

`transport_runtime_r5_34.py`: public argv -> checked route -> supplied raw map ->
unchanged R5.32 bind -> generated operation.py -> checked result encoder.
Launch paths/state/trace/invocation are infrastructure, separate from public
flag/value inputs. Unknown flags reach binding; malformed/duplicate pairs reject
in transport. One metadata-driven algorithm handles all operations; no per-command
Python functions. Generation delegates to current_pipeline and seals artifacts.

## 10. Application A

New independent mineral catalogue: create/list/replace/remove, create publicly
named register. Rows have code, label, medium, quantity and optional seen instant.
Seven/mineral are semantic acceptance conditions; gas is a valid raw-domain value
but semantically rejected. Typed record insertion, label fallback and replacement/
removal frames are semantic relations. Fifteen actual calls share one file.
Final state has only M-1, label=new.

## 11. Application B

Existing independent R5.33 specimen sources expose legacy read/insertion,
migration and current insertion/read. Both envelope row-shape upgrade and legacy
array-root promotion use the same adapter/binder/encoder, different checked
source/profile metadata and no transport algorithm edits.

## 12. Binding-failure results

Actual CLI omitted optional and explicit preferred/valid instant inputs bind.
Malformed instant, invalid finite-domain medium, malformed integer, missing
required inputs and unknown argument fail binding: **5/5 negative binding calls**
have no semantic event and unchanged bytes. Domain mutation adds another boundary
failure. Raw omission/explicit membership is retained in transport/binding evidence.

## 13. Semantic-failure results

`register --code M-3 --medium gas --units 7` binds; gas is in the public domain.
Generated semantics returns rejected with typed reason=rule_not_satisfied, public
SEMANTIC_FAILURE/exit 1. All applicable layers pass, no state change. Fault D
forces SUCCESS while semantics still conforms; public output conformance fails.

## 14. Cross-shape lifecycle

Each B application executes legacy -> legacy_insert -> migrate -> current_insert
-> current on one durable file. **10/10 calls** ground/conform; **8/8 adjacent
byte links** match. Migration counts four specimens; current insert adds a fifth.
Revision becomes 2, present medium/provenance survive and absent medium defaults
through generated relations. Root promotion changes actual JSON array to object.

## 15. Operation availability

Checked pre/post shapes and precondition-presence are metadata; transport does
not inspect revision or duplicate predicates. Two current calls before migration
and three legacy calls after migration reject per witness: **10/10 unavailable
calls** invoke the generated boundary, preserve bytes, return INVOCATION_FAILURE/3
and have no typed event/verdict. Shape/version rules remain generated semantics.

## 16. Grounding

Reproduce `R5_34-transport-evidence.json`:

```powershell
python -m benchmark.semantic.transport_study_r5_34 benchmark/results/phase5c/R5_34-transport-evidence.json
```

Evidence retains sources/specifications/manifests, actual command/argv, stdout,
stderr/exit, exact pre/post bytes/digests, raw map/suppliedness/binding, separate
generated response and semantic events. **46 observations**: A 15, B lifecycle
10, availability 10, faults 6, mutations 5. External observation wraps processes;
independent argv reconstruction and R5.32 decode oracle challenge binding, then
current semantic verification challenges durable endpoints. Self-report alone
cannot establish grounding. Snapshots do not prove no transient writes, concurrent
isolation, atomicity or malicious-runtime fidelity.

## 17. Layered conformance

Separate TRANSPORT_BINDING_CONFORMANT, INPUT_BINDING_CONFORMANT,
SEMANTIC_EXECUTION_CONFORMANT and TRANSPORT_OUTPUT_CONFORMANT, plus profile
integrity/transport grounding. Null means not applicable/evaluable, not success.
**25/25 normal A+B calls** pass applicable layers; **18/18** have grounded typed
semantic execution. A has 5 binding failures and 2 transport route/grammar failures.
Availability calls have no semantic verdict. Five mutations pass applicable
layers (four semantic executions, one binding failure).

## 18. Six-fault matrix

Only disposable copied adapters/profiles change and are resealed with real bytes;
authoritative source/expected profile stays unchanged.

| Fault | Injection | Exposed layer |
| --- | --- | --- |
| A wrong routing | public list selects remove | transport/input/output fail; missing code prevents execution |
| B false suppliedness | omitted preferred reported supplied | transport/input fail; semantic/output still pass |
| C wrong decoder | units integer descriptor changed to instant | normal checked validation rejects category; disposable re-sealed profile produces binding failure and independent profile authority fails |
| D failure as success | encoder forces SUCCESS | semantic passes, transport output fails |
| E result field omitted | encoder removes label | semantic passes, transport output fails |
| F transport mutation | read-only list appends forbidden record outside semantics | independent durable observation contradicts semantic event; semantic grounding/conformance and transport binding fail while output matches |

All six are exposed; C earns no verdict beyond failed authority. F's transport
event matches snapshots, but its semantic event does not. This is independent
architectural rejection through evidence, not OS sandbox enforcement.

## 19. Source-authority audit

Production transport contains metadata checks, routing, raw extraction, binder
calls, generated invocation, shape encoding and evidence/integrity. No catalogue/
specimen fields, insertion/filter/order/replacement/removal/migration/default
algorithms. State is read as bytes for digests only. Semantic fixtures/seeding
and disposable faults live in study machinery, not normal adapters. Durable
application writer remains generated semantic runtime.

## 20. Metadata-driven second application

A supplies public aliases/domains/failure statuses; B derives descriptors for
different operations/outcomes/pre/post shapes. One adapter handles both; adding
B requires source/profile only. Same current generation/runtime protocol.

## 21. Semantic/profile mutation

Five witnesses share identical adapter digest:

| Mutation | Actual change |
| --- | --- |
| register -> enrol public name | renamed route invokes same checked create |
| remove preferred optional mapping | omission stays absent, required mappings complete |
| semantic fallback -> curated | generated durable/result label changes |
| semantic create record result -> code scalar | checked encoding follows new result shape |
| narrow raw medium domain | gas fails binding rather than semantics |

All applicable layers pass. Optional omission policy never computes a default.
Swapped public names matching other slot names also validate. R5.32 existing
semantic type-mutation regressions pass, without altering binding semantics.

## 22. Profile integrity

Application ID/source digest, unit digests and generation identity bind profile
to semantic revision. Runtime checks semantic/runtime hashes, manifest identity
and profile/adapter/binder seal before binding/state access. Regenerate a semantic
default with old profile retained: actual CLI blocks exit 4/stderr, no traces,
unchanged state. Independent challenge recomputes profile from CheckedPlans, so
resealed incompatible fault C fails authority. Digests detect stale/corrupt
revisions, not hostile-writer authentication. Process-local plan IDs are not
treated as stable persisted identity.

## 23. Current-pipeline integration

Transport generation delegates to current_pipeline.generate; execution invokes
its operation.py, verification delegates to current_pipeline.challenge. No
transport compiler or alternate semantic analyzer. R5.32 binder/metadata validator
are unchanged; R5.33 semantics/current pipeline/frozen locks unchanged.

## 24. Future transport boundary

HTTP/RPC/GUI adapters need wire routing and raw membership extraction, checked
binding/invocation and public encoding/status translation, plus independent
wire observations/faults. They must not implement state/predicates/defaults.
CLI tokens/process observation are concrete adapters; checked descriptors and
binding/invocation shapes are common machinery. No network/server implemented.

## 25. Frozen B02 descriptive comparison

Done **after independent implementation/tests**, using only descriptive
requirements/B02.md and inherited baseline.md. No fixture template/candidate/
frozen acceptance; no transport implementation edits follow the comparison.

| Frozen requirement | Classification | Reason |
| --- | --- | --- |
| subprocess operation and named scalar flag/value pairs | SUPPORTED_BY_GENERIC_TRANSPORT | actual independent CLI lifecycle |
| exact public operation/flag names | REQUIRES_PROFILE_CONFIGURATION | metadata aliases |
| omitted/supplied optional scalar flags | SUPPORTED_BY_GENERIC_TRANSPORT | R5.32 membership preserved |
| UTC instant and scalar raw binding | SUPPORTED_BY_GENERIC_TRANSPORT | explicit/malformed cases exercised |
| zero-or-more repeated --tag into collection | UNSUPPORTED_GENERIC_TRANSPORT_CAPABILITY | repeats reject, R5.32 has no collection-slot decoder |
| trim/nonblank/case-sensitive ordered deduplication | BENCHMARK_SPECIFIC | application semantics, not transport |
| tags field and omitted/migrated [] defaults | BENCHMARK_SPECIFIC | semantic outcome/state/defaults |
| JSON scalar/record/list representation | SUPPORTED_BY_GENERIC_TRANSPORT | checked generic encoder |
| exact bare stdout result without wrapper | UNSUPPORTED_GENERIC_TRANSPORT_CAPABILITY | current status/outcome envelope is fixed |
| failure stderr {error: CODE}, exit 1, empty stdout | UNSUPPORTED_GENERIC_TRANSPORT_CAPABILITY | typed failure stdout/1, binding failure stdout/2; no configurable stream/envelope policy |
| invalid_tag/invalid_due_date public category names | REQUIRES_PROFILE_CONFIGURATION | naming is policy, exact envelope/exit projection still unsupported |
| shared durable store across processes | SUPPORTED_BY_GENERIC_TRANSPORT | both lifecycles use same file |
| implicit cwd tasks.json | REQUIRES_PROFILE_CONFIGURATION | launch/file selection convention; prototype uses explicit infrastructure path |
| missing store -> [] without creating; migrate missing -> count 0 | UNSUPPORTED_GENERIC_TRANSPORT_CAPABILITY | no checked absent-store/persistence initialization policy; transport must not invent state defaults |
| malformed JSON/state -> frozen invalid_state public failure | UNSUPPORTED_GENERIC_TRANSPORT_CAPABILITY | runtime rejection is generic INVOCATION_FAILURE, no configurable persistence taxonomy |
| version-dependent operation availability/migration routing | SUPPORTED_BY_GENERIC_TRANSPORT | generated shapes/applicability govern |
| IDs/status/priority/overdue/no-new-task rule | BENCHMARK_SPECIFIC | source relations/capabilities |
| exact complete inherited frozen integration | UNKNOWN | intentionally unexecuted |

These are future generic capability questions, not permission to repair task
behavior in R5.34. Frozen B02 itself has not passed.

## 26. #31 decision

No missing frozen-independent application-semantic concept found. Routing,
decoder selection and encoding are interface/binding/runtime machinery. No #31
or semantic-extension review gate. Unsupported collection/persistence/public
policy needs independent generic review, not task-specific behavior.

## 27. Capability matrix

R5_24-type-matrix.json retains prior profiles and adds r5_34_checked_transport:
transport_profile, operation_routing, suppliedness_preservation, raw_binding,
output_encoding, layered_conformance, profile_integrity and
cross_shape_lifecycle_transport. Eight supported bounded dimensions with evidence/
limits; focused/full validation checks coverage, core count and current entry.

## 28. R5.23 transport blocker reassessment

**GENERIC_ARCHITECTURE_VALIDATED**: checked public routing drives supplied raw
binding/generated invocation/checked encoding across independent applications,
including row/root cross-shape closure and faults. Exact frozen readiness remains
partial for the concrete uncovered capabilities. Generic architecture validation
does not imply frozen transport passed.

## 29. Full B02 readiness assessment

| Major class | Readiness | Scope |
| --- | --- | --- |
| optional refinement | RESOLVED_INDEPENDENTLY | R5.31 single-authority current pipeline |
| instant ordering | RESOLVED_INDEPENDENTLY | chronological checked current ordering |
| suppliedness/well-formedness | RESOLVED_INDEPENDENTLY | R5.32 scalar boundary |
| malformed-input boundary | PARTIALLY_RESOLVED | structured failure distinct from semantics; operation-declared/public mapping separate |
| cross-shape evolution | RESOLVED_INDEPENDENTLY | bounded R5.33 keyed/root transitions, transported |
| transport binding | PARTIALLY_RESOLVED | architecture validated; collection/public-stream/persistence coverage incomplete |

Not all required classes suffice for comprehensive frozen retry. Do not recommend
B02 retry as R5.35.

## 30. Construct/system accounting and verification

**30 candidate core constructs; no #31.** Historical 46 raw categorized entries
unchanged. Added system machinery: checked profile/challenge, CLI runtime, study
and restriction runner (four Python modules), one test module, versioned interface,
machine evidence/result and updates to capability/research docs. These belong to
binding/runtime/verification/evidence/administration, not core vocabulary. One
semantic authority remains; no canonical task model/generated/frozen oracle/
requirement/runtime/schema/lock edits.

Windows PowerShell, **Python 3.14.3**. No unsupported-Python/environment failures,
no LF mirror; historical hashes pass. Git LF-to-CRLF notices are separate from
actual failures.

| Actual verification | Result |
| --- | --- |
| python -m benchmark.semantic.verify_transport_r5_34 | 319 discovered, 318 pass, 1 restriction skip; 0 errors/failures, 86.944 s |
| architecture/grounding/semantic/binding/evolution and relevant R5.10–R5.33 focused suites | included/passed in full discovery |
| R5.34 focused discovery | 11/11 pass, 5.967 s; also included in full |
| application/compiler discovery with PYTHONPATH=src | 31/31 pass, 2.842 s |
| model validation | OK |
| safety | 0 capability violations, 0 invalid transitions |
| capability matrix | focused/full validation and prior regressions pass |
| machine study | 46 observations, applicable baseline/mutation layers pass, six faults exposed |
| git diff --check | passes; LF-to-CRLF notices separate |

Restriction runner excludes exactly
test_phase5e.CapabilityProfileTests.test_read_only_validation_of_both_continuation_states,
which launches nested frozen B02 acceptance. Exclusion must match once or runner
fails. Historical diagnostic tests remain regressions, not a new B02 retry.

B02 **not retried**, frozen B02 acceptance **not run**, Phase 5C paused, B03
untouched, B17 unexposed/unclassified, semantic-first format globally unfrozen,
R5.2.2 historical benchmark authority; universal correctness unclaimed. Direct
durable writes remain non-transactional/crash-nonatomic; integrity is not sandboxing.

## 31. Exact recommendation for R5.35

Begin **Generic Transport Boundary Completion Review** independently on new
non-task applications. Preserve R5.34 separation; audit/design checked collection/
repeated raw binding, configurable outcome/binding/persistence error envelope/
stream/exit policies and checked absent-store initialization ownership. Resolve
public pre-invocation failure mapping without pretending semantics executed.
Keep defaults/normalization/domain validity/migration/state writes in semantic
source/generated runtime. Use authoritative plans, source/profile-only mutations,
actual durable lifecycles, independent grounding and disposable faults. Reassess
all readiness classes before proposing a separately locked comprehensive retry.
Do not run B02/frozen acceptance as part of the recommended review, resume Phase
5C/advance B03, expose B17, freeze the format or add #31.

The gate follows checked routing/raw binding, independent generated applications,
cross-shape closure and layer-specific fault evidence, not test count or frozen
transport achievement.

R5_34_CHECKED_TRANSPORT_VALIDATED
