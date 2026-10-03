# R5.32 — Input binding and typed failure boundary

Prospective independent non-task study, 2026-10-03, based on R5.31 commit
`ad63d5a` (`R5_31_SINGLE_SEMANTIC_AUTHORITY_VALIDATED`). The architecture is
**validated for the bounded synthetic public profile**: raw data either binds to
checked typed input or fails before semantic invocation. Application rejection
remains an operation outcome. Candidate core semantics remain **30**, no #31.

Implementation: `benchmark/semantic/{input_binding_r5_32,public_adapter_r5_32,
public_binding_r5_32,binding_study_r5_32}.py`; tests:
`benchmark/harness/test_input_binding_r5_32.py`. Versioned interface rules:
`docs/input-binding-r5.32.md`. Machine evidence:
`R5_32-binding-evidence.json`, generated from actual subprocess/file observations.

## 1. Current input pipeline

Before R5.32, current_pipeline.observe serialized an already-typed input object
to generated operation argv. The runtime decoded JSON, checked concrete input
and pre-state shapes, invoked the generated operation, checked result/post-state,
wrote durable state when requested, then emitted execution evidence. Malformed
typed input raised a process exception, with no structured public binding result.
The older standalone run_cli used argparse conversions but was not the current
multi-operation application's raw public binding path.

| Responsibility | Existing location | Classification |
| --- | --- | --- |
| operation/argv and JSON payload carrier | current_pipeline.observe / run_application | TRANSPORT |
| argument presence | JSON record key membership, runtime.valid required fields | BINDING / RUNTIME |
| raw strings/data, JSON parsing | runtime.run; older argparse run_cli | TRANSPORT / BINDING |
| integer CLI conversion | older argparse `type=int` | BINDING |
| enum decoding | no enum shape in current profile; finite equals compositions are predicates | UNKNOWN as decoder; SEMANTIC_CONTRACT as predicate |
| instant decoding/validation | runtime.is_instant/valid; before/instant_key helpers | BINDING / RUNTIME |
| optional omission | valid(record), optional-preserving checked record emission | TYPE_SYSTEM / RUNTIME |
| fallback | authoritative analyze; generated fallback and independent interpret | SEMANTIC_CONTRACT |
| static type validation | checked_plan -> typed/analyze -> seal | TYPE_SYSTEM |
| actual concrete value validation | runtime.valid, verifier concrete checks | RUNTIME |
| application validity/branch choice | generated guards; independent semantic interpreter | SEMANTIC_CONTRACT |

Now: public JSON invocation → checked metadata-driven binding → typed success or
structured binding failure → generated semantic invocation when bound → public
result. Independent binding grounding/conformance precedes semantic verification.

## 2. Input-state taxonomy

| State | Meaning | Owner |
| --- | --- | --- |
| OMITTED | public key absent; optional key remains absent in semantic input | binding/compiler concept; semantic optional membership can observe it |
| SUPPLIED_RAW | key present, data not yet decoded | transport/binding concept |
| BINDING_FAILED | no admissible target value or interface/domain match; no complete typed input | binding concept |
| BOUND_TYPED | concrete valid value of the authoritative slot type, decode domain satisfied | binding/type-system boundary |
| SEMANTICALLY_INVALID_TYPED | bound input rejected by operation predicates against input/state | application-semantic concept; contextual, not an invalid type instance |

The last state is not a persisted binder status. It follows actual semantic branch
evaluation. Omission is not null; malformed syntax is not semantic invalidity.
No states become new core constructs.

## 3. Suppliedness model

Preserve public key membership per checked slot as `supplied: bool`. Successful
semantic input retains absent optional keys and present decoded keys. The
configure operation's existing `present(input.preferred)` selects `supplied`
versus `omitted` tags before either branch evaluates fallback. Binding evidence
independently preserves the distinction. No extra application input flag or
new suppliedness relation is introduced.

## 4. Fallback interaction

The binder never installs a fallback. Generated existing semantics supply
`quiet` only when preferred is absent. Supplied `quiet` wins as supplied data;
supplied `bright` wins as bright. Optional seen has no fallback and stays absent
on omission, including in the persisted nested record. A malformed supplied seen
does not cause omission/fallback. Fallback is value selection, not validation.

## 5. Raw parsing boundary

The generic decoder exercises string, ASCII decimal integer, existing UTC-Z
instant and explicit finite domains of checked scalar values. Boolean is also
supported. String values are not trimmed or screened for application validity.
Integer bool/float/null, whitespace, Unicode digits and malformed text reject.
Instant parsing uses the existing valid instant domain unchanged. Domain checking
is explicit binding policy after scalar decoding, not inferred application logic.
All-or-failure results suppress partial input as `input: null`.

## 6. Binding failure representation

Closed categories: malformed_payload, unknown_operation, unknown_argument,
missing_required, malformed_scalar, outside_domain. Failure fields are public
argument identity, checked semantic slot identity, expected base type and category.
Raw data is unnecessary in persistent diagnostics. The public code comes from
complete category mapping metadata. Domain expectation is recoverable from the
source-checked binding descriptor. Whole-boundary failures use null identities.
Slot identity is scoped by operation and originating generation, not a universal
field name. Synthetic external evidence intentionally includes its raw fixtures.

## 7. Outcome-mapping comparison

| Model | Architectural consequence | Decision |
| --- | --- | --- |
| A: binder directly returns public error | preserves separation; public classification can be hardwired | valid baseline, but mapping needs explicit ownership |
| B: binding failure becomes declared semantic operation outcome | implies an additional failure-aware operation input/entry or fabricated execution; current scalar signature cannot consume malformed instant | not chosen; do not inject invalid typed values or pretend #45 executed |
| C: binding contract maps category to public/semantic outcome | explicit interface policy can map to public result before invocation; semantic mapping would require a legitimate typed failure-aware contract | chosen **public mapping** variant |

C is implemented as a structured binding-failure public envelope with checked
category-to-code metadata. The generated operation's declared outcomes stay
semantic. It is not an implementation of C's possible semantic-outcome variant.
This bounded public boundary closes the architecture question without adding #31.

## 8. Semantic-invalidity distinction

Existing predicates/preconditions suffice: integer 8 binds, then fails equality
to allowed quota 7; LATE binds as instant, then fails strict before(LATE); calibrate
belongs to the public finite domain but is forbidden by the current rule; a second
acquire is rejected because durable mode is no longer idle. Each produces
`rule_rejected` with preserve-state through existing operation semantics.

## 9. Synthetic domain

An observatory console, not task-manager field renaming. Shared record state:
label:string, at:instant, mode:string, quota:integer, last:record of optional
note:string/seen:instant. Four generated operations: configure (optional/fallback
and presence), schedule (typed instant), mode (finite public domain plus state
rule), quota (integer plus semantic constraint). Existing post_equals relations
provide same-shape stateful writes. No providers, application-specific parsers or
hand-authored operation implementations are used.

## 10. Omitted-input results

Configure `{}` records both slots OMITTED, semantic input `{}`, public semantic
outcome `omitted/quiet`, durable label quiet and durable last `{}`. Seen is absent
without fallback. Schedule `{}` instead yields missing_required binding failure,
no semantic trace and unchanged durable state. Both independently ground and
conform at their appropriate layers.

## 11. Explicit fallback-equivalent result

Configure preferred=quiet records BOUND_TYPED/supplied=true, invokes with
`{"preferred":"quiet"}`, returns `supplied/quiet`, persists label quiet and
last.note quiet. The final label equals omission's label; public tag, suppliedness,
typed record membership and durable nested note distinguish the paths.

## 12. Malformed instant result

Schedule when=not-a-date returns category malformed_scalar, expected instant,
code input.malformed_scalar, exit 2 and empty stderr. No invalid instant or
semantic input is produced, no semantic trace exists, state bytes remain equal.
Independent binding conformance passes; semantic conformance is null, not true.

## 13. Invalid finite-domain result

Mode setting=broken yields outside_domain against the explicit idle/acquire/
calibrate decode domain. Setting=calibrate binds as string/domain member, invokes
the operation and returns semantic rule_rejected/mode_forbidden. This distinction
is intentional even though the current profile has no nominal enum shape.

## 14. Additional scalar malformed result

Quota units=7x fails integer binding before invocation. Boolean, null, float,
whitespace, empty string, underscore-separated and Unicode-digit raw values also
fail in focused edge checks. Configure preferred=5 fails string binding. Quota
units=7 binds as integer 7 and durably updates quota to 7.

## 15. Typed semantic-invalidity result

Units=8 binds as integer 8 with no binding failures, invokes generated quota,
returns rule_rejected/quota_forbidden and preserves durable bytes. Schedule LATE
and mode's domain-valid/state-invalid values likewise invoke and fail semantics.
Parsing is not allowed to inspect state or quota policy.

## 16. CheckedPlan integration

No extension to the sealed plan was necessary: R5.31 already includes
`slots.input`, authoritative optional wrappers and base shape facts. Public
metadata asserts the plan's source/seal/invariants and consumes those declarations.
No analysis of guards/defaults or alternate expression typer is added. A trap
poisoning analyze after checking still permits metadata generation; mutation of
the sealed input declaration fails closed. Actual scalar validation is a runtime
value check against checked expectations, not another semantic type authority.

## 17. Binding metadata

Each operation maps public argument → `{slot,type,optional,domain}`. Aliases
setting→value and units→amount demonstrate public names need not equal semantic
names. User policy cannot supply or override a semantic type. Unknown operations/
slots, duplicate aliases, unknown metadata keys, untyped/duplicate domain values
and incomplete failure-code maps reject before public generation. Supported
scalar descriptors are generated from sealed plans; unsupported shapes reject.

## 18. Generic public adapter

The synthetic JSON-object CLI identifies operation, preserves key presence,
binds according to generated descriptors, emits binding evidence, invokes the
single generated operation.py only on complete success and wraps its observable
outcome. Administrative state/trace/invocation/generation arguments are explicit.
Current runtime validates the concrete typed input again. The adapter contains
no observatory field names, operation cases or domain parsing. Public mapping
changes through metadata without semantic outcome changes.

## 19. Evidence model

Binding event: operation, invocation, semantic generation, slot suppliedness/
state, binding result, semantic_invoked, public result, pre/post durable digests.
Semantic event: unchanged current-pipeline actual invocation/input/pre/post/
outcome/attempted-write/external evidence. Fresh invocation-specific trace paths
prevent a previous success trace from being mistaken for failed binding execution.
Study evidence retains external observation and both actual events; failed cases
have semantic_event=null. No attempted-write claim is invented for an uninvoked
operation. Artifact provenance is separate for public files and semantic artifacts.

## 20. Grounding results

The 18-call shared-store sequence independently captures public stdout/stderr/
exit, exact invocation payload, before/after bytes and actual trace files. All
18 bind-ground and bind-conform. Ten actual semantic invocations independently
semantic-ground and semantic-conform; eight binding failures have no semantic
verdict. Successive post/pre digests match for all 17 adjacent pairs. Three
source-mutated calls also ground/conform at both layers. This is finite evidence,
not exhaustive input or transport coverage.

## 21. No-state-change results

Eight normal binding failures preserve observed durable bytes and decoded state.
Four typed semantic rejections preserve bytes under semantic contracts. Fault C
changes at from LATE to EARLY during a forbidden invocation: independently read
durable state exposes it. The binding obligation checks **no semantic state
change**. Byte equality does not prove zero physical writes; binding evidence
files are written by design. Hidden transient/same-byte writes are not attested.

## 22. Fault matrix

All faults modify only disposable copied files; their public artifact hashes are
re-sealed so verdicts concern behavior/evidence rather than stale provenance.

| Fault | Injection | Independently observed effect | Binding grounding / conformance |
| --- | --- | --- | --- |
| A | decoder substitutes a valid instant for malformed raw text | semantic invocation and timestamp change despite raw not-a-date | pass / fail: raw-to-typed correspondence |
| B | explicit quiet slot evidence is rewritten as omitted | actual generated operation still reports supplied/quiet and persists note | pass / fail: suppliedness evidence mismatch |
| C | failed binding invokes generated schedule with invented valid input | actual semantic trace and durable LATE→EARLY mutation | pass / fail: no-invocation/no-state-transition obligation |
| D | bound integer 8 is relabeled malformed_scalar | public binding_failure, no semantic invocation where rule_rejected required | pass / fail: binding/semantic layer mismatch |

Semantic conformance is deliberately not promoted after binding failure. Fault A
could be locally valid for the invented typed value, which is why raw binding
conformance must precede semantics. Fault C's actual trace is retained, never
silently erased to make the adapter's expected failure look uninvoked.

## 23. Binding versus semantic verification

Separate verdict fields: provenance_valid, binding_grounded, binding_conformant,
semantic_grounded, semantic_conformant. Grounding checks the public event against
external endpoints; independent concrete decoding checks its required meaning.
The oracle never calls bind/decode (poisoned-call regression confirms separation).
Only a conformant successful binding passes the independently expected typed
record into current_pipeline.challenge. That verifier consumes CheckedPlan facts
and independently evaluates semantic behavior. Shared static type authority does
not imply shared behavioral verdict. Malformed failures do not falsely pass #45.

## 24. Layer-ownership matrix

| Concept | Primary ownership | Other legitimate responsibility |
| --- | --- | --- |
| suppliedness | TRANSPORT captures; BINDING preserves | CORE_SEMANTICS optional membership / OPERATION_CONTRACT present; VERIFICATION challenges |
| raw value | TRANSPORT | BINDING ephemeral decode; VERIFICATION independent external fixture |
| parsing | BINDING | RUNTIME concrete shape guard; VERIFICATION independent decoder |
| binding failure | BINDING | TRANSPORT public delivery; VERIFICATION category/no-invocation checks |
| typed value | TYPE_SYSTEM expected shape | BINDING produces, RUNTIME validates, CORE_SEMANTICS evaluates |
| semantic invalidity | OPERATION_CONTRACT | CORE_SEMANTICS predicates/outcomes; VERIFICATION independent evaluation |
| fallback | CORE_SEMANTICS | OPERATION_CONTRACT chooses expression; RUNTIME executes; VERIFICATION evaluates |
| public error mapping | BINDING interface policy | TRANSPORT envelope/exit; VERIFICATION checks |

## 25. Construct #31 decision

No missing application-semantic concept was demonstrated. Existing optional
membership/present/fallback, typed predicates, branches/outcomes and state
relations express all application behaviors in the study. Raw omission, decode
failure, diagnostics and interface mapping are compiler/binding/runtime concepts.
Do not turn malformed raw text into an instant just to reach #45. Core count 30.

## 26. Current-pipeline integration

Every successful and semantically rejected application call executes operation.py
generated by `benchmark.semantic.current_pipeline.generate`. Wrappers use its
authoritative checked analysis and its independent challenge. No prospective
compiler fork, alternative semantic/type analyzer or typing change is introduced.
Historical modules and pinned evidence are preserved. R5.31 authority tests all
pass in the required harness run.

## 27. Multi-command pressure test

One generated four-command observatory program, one shared durable file, 18
success/error invocations. Configure writes optional nested record membership;
schedule writes a typed instant; mode writes a finite-domain value and then
rejects a state-forbidden repeat; quota writes a decoded integer. Reads of each
subsequent durable pre-state establish byte-to-byte continuity, with rejection
paths mixed into the same chain. This demonstrates composition rather than four
isolated parser probes.

## 28. Semantic mutation results

No binder/compiler changes between source variants:

| Source-only mutation | Binding effect | Generated semantic/durable effect |
| --- | --- | --- |
| configure fallback quiet→bright | omitted input remains absent | omitted/bright, label bright |
| quota declared integer→string, matching state/literal types | 7x now binds as string instead of malformed integer | semantic rule_rejected; typed quota state remains string |
| mode allowed acquire→calibrate using existing equality guard | same finite decode domain, calibrate still binds | ok/calibrate, durable mode calibrate |

These mutate existing semantic declarations/constraints, not interface policy to
pretend a nominal enum exists. Public decode-domain changes can separately be
made through validated metadata. All three actual calls ground and conform.

## 29. Capability matrix

`R5_24-type-matrix.json` adds a separately versioned `r5_32_input_binding` profile
with explicit dimensions raw_input_binding, suppliedness, parse_decode,
binding_failure, typed_invocation, semantic_invalidity_distinction, public_adapter
and binding_grounding. All are supported **within this scalar synthetic profile**
and linked to witnesses/faults. Matrix validation checks dimensions, support and
core count. Frozen transport and cross-shape evolution are explicitly unsupported.
Historical R5.23–R5.31 classifications are preserved as historical observations.

## 30. R5.23 blocker reassessment

| Class | Prospective classification | Exact boundary |
| --- | --- | --- |
| suppliedness / well-formedness | RESOLVED_INDEPENDENTLY | scalar JSON-object binding, checked types, provenance, existing semantic presence |
| malformed-input typed outcomes | PARTIALLY_RESOLVED | structured typed-category public failure mapping validated; malformed input is not a semantic operation value, and a mapping into declared application outcome tags is not implemented |
| cross-shape state evolution | UNRESOLVED | independent R5.33 review |
| frozen B02 transport | UNRESOLVED | synthetic public profile is not frozen transport |

The second classification preserves the distinction between public boundary
failure and the earlier expectation of an operation-declared malformed-input
outcome. That expectation must not force invalid semantic values or fabricated
operation evidence. The general binding architecture can validate while frozen
application integration remains unestablished. No B02 retry was used to classify.

## 31. Remaining blockers and verification

Cross-shape pre/post evolution and frozen transport remain separate. Nested
public record/sequence/nullable shapes are explicitly unsupported in this bounded
scalar adapter; nominal enum types are absent. JSON duplicate-key policy,
resource bounds, hostile-runtime attestation, physical no-write and general
semantic-outcome mapping from pre-invocation failure are outside the validated
claim. Existing same-shape compiler constructive limits remain.

Supported environment: Windows, official Python **3.12.10** embeddable interpreter
at `C:\Users\lblan\AppData\Local\Temp\opencode\python-r531\python.exe`.
`py` defaults to Python 3.9. The supported interpreter was selected from the
start. Untouched pinned files in the workspace have LF index/CRLF working bytes;
full historical verification therefore used an isolated `core.autocrlf=false`
clone of ad63d5a plus the actual R5.32 tracked patch and new Python files.
No frozen files or hash locks were changed in the workspace.

| Required check | Result |
| --- | --- |
| full harness discovery via `python -m benchmark.semantic.verify_binding_r5_32` | 298 discovered, 297 pass, 1 explicitly skipped; 0 failures/errors; final code 206.510 s (first full run 213.885 s) |
| application/compiler `python -m unittest discover -s tests -v` | 31/31 pass |
| `PYTHONPATH=src` model validate | OK |
| model safety | 0 capability violations, 0 invalid transitions |
| architecture/grounding/semantic and relevant R5.10–R5.31 suites | all run/passed within full harness discovery |
| new R5.32 focused suite | 12/12 pass, final focused run 8.297 s; also included in full discovery |
| capability-matrix validation | passes in new focused/full suites |
| `git diff --check` | pass; LF→CRLF notices are separate |

One excluded historical test,
`test_phase5e.CapabilityProfileTests.test_read_only_validation_of_both_continuation_states`,
would launch frozen B02 acceptance internally. The prospective runner marks it
skipped without editing historical tests. **Frozen B02 acceptance did not run.**
Unchanged historical B02-shaped diagnostic tests run as regression machinery;
they do not generate a new B02 candidate or constitute a new retry. This is full
discovery with a disclosed restriction, not a claim that 298 tests all passed.

Git emitted LF→CRLF conversion notices while exporting the patch. They are not
actual test failures or diff-check failures. The LF mirror protects historical
byte-pinned checks. There were no supported-runtime test failures in R5.32.

## 32. Construct/system accounting

30 candidate core semantic constructs; no #31. Historical 46-entry categorized
raw inventory unchanged. New components are binding metadata/decoding, public
runtime adapter, evidence/verifier integration, non-task fixtures and verification
administration. ONE current authority each for semantic typing, ordering,
optional/refinement, outcome typing and state-slot typing remains intact.

B02 is not retried; frozen B02 acceptance is not run; cross-shape migration is not
implemented; Phase 5C remains paused; B03 remains untouched; B17 remains unexposed
and unclassified; semantic-first format remains globally unfrozen; R5.2.2 remains
historical benchmark authority; universal implementation correctness is not claimed.

## 33. Exact recommendation for R5.33

Begin **Cross-Shape State Evolution and Versioned Durable Boundary** as a bounded
independent non-task semantic/architecture review. Audit whether existing state
relations and operation contracts can bind distinct checked pre/post shapes and
versioned source/target rows while preserving frame/identity/outcome obligations.
First produce an expressiveness and ownership decision; halt before #31 if an
irreducible application-semantic gap is demonstrated. Preserve the R5.31 authority
and R5.32 binding/verifier separation. Only then implement a justified generic
checked transition on a new non-task domain with independent durable grounding,
source-only mutations and faults. Do not combine it with frozen transport, retry
B02, resume Phase 5C, advance B03 or expose B17.

The gate follows coherent layer ownership, actual public/durable evidence and
fault localization, not test count or the unresolved frozen application mapping.

R5_32_INPUT_BINDING_BOUNDARY_VALIDATED
