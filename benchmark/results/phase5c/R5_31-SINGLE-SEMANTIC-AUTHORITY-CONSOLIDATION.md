# R5.31 — Single semantic authority consolidation

Prospective non-task, same-shape compiler refactoring, 2026-10-03. The gate is
**validated for the supported current-pipeline subset**. Semantic/type meaning
is established by `unified_types_r5_27.checked_plan`; generation and independent
behavioral verification consume its source-bound checked facts. Candidate core
semantics remain **30**, with no #31 and no new semantic capability.

## 1. Complete authority audit

The source is the semantic application dictionary, with operation dictionaries
as its semantic AST. There is no target-code parser between source and checking.
`current_pipeline.checked` validates application identity/shared-state binding;
each operation enters `checked_plan -> typed -> analyze/_analyze`. Analysis
records facts as it validates, then the constructive relation planner consumes
those facts before the plan is sealed. Generation, runtime binding, observation,
grounding and conformance follow. Challenge-time reconstruction uses this same
authoritative analyzer on the independently supplied originating source, not a
second type system or generated target.

| Fact / component | Source data | Already available before R5.31? | Disagreement risk / R5.31 classification |
| --- | --- | --- | --- |
| Application identity/state, `current_pipeline.checked` | semantic application declarations | operation analyzer did not own application-map binding | AUTHORITATIVE structural application binding; no expression inference |
| Declared shapes, `typed`, shared `general.shape_valid` | input/state/payload declarations | yes | AUTHORITATIVE declaration validation; shape helper is not an alternate expression typer |
| Reference/field type, `declared/_field` within analysis | slot declaration and field path | yes | AUTHORITATIVE; field helper only resolves under this analyzer on the current path |
| Expression operand/result types, `analyze/_analyze` | AST, checked slot environment | previously partial | AUTHORITATIVE; all supported kinds now use recursive authoritative analysis |
| Older expressions, former `analyze -> _compile` | raw AST and slots | analyzer delegated rather than recording closure | DUPLICATED_SEMANTIC_DERIVATION removed from current analysis; literals/trim/map/stable_unique/nonblank/for_each now checked here |
| Refinement, `witness/conjunction` | declared optional path, positive conjunction | yes | AUTHORITATIVE; records producer/scope dependencies and declared/effective reference types |
| Ordering, `ordering_plan` within analysis | checked source type, key sequence, scoped selection witnesses | yes | AUTHORITATIVE; preserves string/integer/instant, lexicographic keys and unconstrained ties |
| Former `checked_plan.visit` | same AST after `typed` | yes but not materialized | DUPLICATED_SEMANTIC_DERIVATION removed; fact collection occurs inside analysis, with context-keyed memoization |
| Branch payload/tag typing, `typed` | typed value, declared payload and unique tags | yes | AUTHORITATIVE; result retained in `outcomes` |
| State relation collection, identity, field, operand compatibility, `typed` | state declarations and input/pre expressions | yes, incompletely retained | AUTHORITATIVE; complete source/target/operand bindings retained |
| `_relational` semantic type comparisons and field lookup | formerly raw state and separately compiled expressions | yes in `typed` | DUPLICATED_SEMANTIC_DERIVATION removed on checked path; uses `plan.bindings`, never `resolve/_compile` for that path |
| `_relational` identical/conflicting default comparison | already typed relation bindings and semantic literal/expression values | conjunction facts were established here only | AUTHORITATIVE conjunction fact established during checked-plan construction, retained once; not re-evaluated during generation |
| `_relational` overlapping transforms/unresolved equivalence | checked relation targets, kinds and values | no constructive plan earlier | TARGET_SPECIFIC_CONSTRAINT: bounded constructive support; valid unsupported combinations reject explicitly |
| `generated_unit/expression` | checked plan plus source operation/value structure | partly | DOWNSTREAM_ASSERTION: source identity, fact seal, closure, typed-node membership/kind; no expression inference |
| Legacy emitter `typed/ordering_plan/render` without plan | raw contract and slots | competing legacy typing | HISTORICAL_ONLY; unreachable from `current_pipeline.generate` |
| Scoped ordering source restriction | checked slots and source binding metadata | not a semantic validity question | TARGET_SPECIFIC_CONSTRAINT; remains a bounded emitter limitation |
| Target sort/instant/record emission | checked key types, projections, optional-reference facts | yes | TARGET_SPECIFIC_CONSTRAINT / representation selection, not type discovery |
| `refined_runtime.valid`, input/pre/post/outcome boundary | concrete invocation and checked generated shape metadata | static shapes already known | RUNTIME_VALIDATION; checks actual values, does not infer state shape from durable examples |
| Runtime capability boundary | concrete provider result and now emitted `capability_shapes` | authoritative signatures previously available | RUNTIME_VALIDATION; current operations no longer select types from the runtime's legacy fallback table |
| Observation/provenance, `observe/challenge` | subprocess output, independent file bytes, source/artifact/runtime hashes | n/a | DOWNSTREAM_ASSERTION / evidence integrity; no AST typing |
| `_type/validate_logged` at grounding/conformance | observed data, checked shapes / registered external signature | yes statically; actual values unknown | RUNTIME_VALIDATION; concrete value checking remains necessary |
| Former `interpret(select)` and `_compile` evaluation fallback | raw AST/slots during verification | yes | DUPLICATED_SEMANTIC_DERIVATION removed; element type comes from `operand_type`, older kinds evaluate values directly |
| `conforms/_ordered_relation_holds/interpret` | source semantic requirements, checked facts, independent observations | shared static interpretation | VERIFIER_SEMANTIC_EVALUATION; independent expected behavior and verdict, never generated-code interpretation |
| Verifier no-plan paths for older contracts | historical AST and legacy typer | n/a to current | HISTORICAL_ONLY; R5.27 source without explicit plan reconstructs the same checked plan |

No current downstream component answers a semantic typing question using a
competing expression typer. Multiple functions participate in the one analysis;
this does not mean one authority per function. Target constraints and independent
concrete-value/behavior checking are separate from static semantic typing.

## 2. Complete checked-plan contract

`CheckedPlan` is an in-process, source-bound compiler contract, not a new
serialized semantic language or portable IR. Node/relation identities are Python
object identities **within the originating contract**; the operation's semantic
`id`, source object and canonical digest bind their namespace. They are not
cross-process stable IDs. Consumers cannot substitute a structurally equal copy
of an expression. The source reference is retained for semantic operation/value
structure, diagnostics, provenance and independent interpretation.

| Checked field | Established meaning / consumer entitlement |
| --- | --- |
| `contract`, `digest` | originating operation identity and exact source binding |
| `facts[node]` | node kind, declared type, effective type, checked reference/field path, refinement `(scope, producer)` dependencies and collection element type when applicable |
| `operands[node]` | effective/result type of **every** analyzed expression, including guard, literal, nested normalization, projection, payload and relation operand |
| `scopes[conjunction]` | exact optional path → presence producer dependencies; positive conjunction scheduling without rediscovering guards |
| `orders[node]` | checked source node/result sequence type, element type, ordered keys with scoped field identity, declared/effective type and presence scope/producer, lexicographic comparison, unconstrained ties, no represented direction |
| `bindings[relation]` | pre-source/post-target slot paths, collection/slot type, checked record fields, identity name/type, affected field name/type, operand-name → checked node identity |
| `relations[branch]` | checked constructive conjunction; original source relation identities retained, including default deduplication |
| `projections[node]` | checked field identity/type sequence of a record projection; source/result types are in `operands` |
| `optional_record_fields` | checked optional reference identities eligible for absent-key-preserving construction; not a fallback rule |
| `capabilities` | referenced external capability → authoritative semantic result type |
| `slots` | checked input, pre and post declarations; same-shape pre/post equality in this profile |
| `outcomes` | unique checked outcome tag → checked payload/result type; scalar, record and post/project results |
| `seal` | internal fact-integrity checksum; compiler consistency machinery, not a semantic construct or security proof |

Field identity is scoped: a reference node's checked path is resolved in its
analysis environment; `item` refers to the element of that checked selection.
Ordering field names resolve against the retained checked element; projection
field names resolve against the already checked row. Relation identity/field
bindings include their collection and pre/post namespace. Names alone are not
universal field IDs. No downstream consumer reconstructs these shapes.

## 3. Checked-plan invariants

Construction records each expression while validating it. Cache keys include
node, declared environment and refinement paths; conflicting context-dependent
reuse fails closed rather than inventing a second node interpretation.

Machine checks in `assert_current`, `operand_type` and `assert_invariants` cover:

- exact source digest and checked fact seal;
- expression-fact/operand-key closure and effective-type equality;
- each refined operand's recorded scope/producer membership;
- orderable checked key types and the emitter's supported comparison/tie contract;
- ordering source/field bindings and optional-key presence dependencies;
- pre/post state binding namespaces and checked relation operand membership;
- emitter membership and source-node kind agreement;
- stale source, alien source/expressions and mutated internal fact maps.

Reference, field, collection, projection and outcome compatibility is validated
by authoritative analysis and retained in the sealed plan. Assertions do not
re-run inference. The seal detects accidental mutation of nested maps; it is
not a defense against an adversary rewriting compiler code and resealing facts.

## 4. Generator refactor

`generated_unit` consumes checked input/pre/post/outcome shapes, relation
bindings and capability signatures. `expression` requires a checked operand for
each real source node and asserts its kind. Recursive trim/map/stable_unique/
nonblank/for_each/sole/project emission retains the same plan (previously some
recursive calls dropped it). Optional parent-path addressing emits target access
from the checked path instead of constructing a synthetic untyped AST node.
Projection fields and external result types come from checked facts. Default
planning retains original relation identities so emitters can consume bindings.
There is no current generator call to legacy `_compile`, emitter `typed` or
emitter `ordering_plan`.

## 5. Target-constraint boundary

Target representation remains legitimate: instant key conversion, dictionary
construction, scoped-source emitter limits, exact singleton runtime checks,
fresh/unique identity runtime checks and constructive overlap restrictions.
The backend can reject a checked combination it cannot construct. It cannot
choose another semantic type to make the combination lowerable. The Python
backend's stable tie choice does not redefine unconstrained semantic ties.

## 6. Ordering authority

`unified_types_r5_27.ordering_plan` is the only current ordering semantic
authority. The emitter reads its key sequence/types; no field inspection,
orderability inference or tie reinterpretation occurs downstream. The verifier
uses the checked element and keys to evaluate exact observed multisets and
nondecreasing chronological/lexicographic ranks. It does not require Python's
stable permutation of fully tied rows. Instant meaning is unchanged.

## 7. Refinement authority

The plan records declared `optional<instant>`, effective `instant`, checked
field path and conjunction producer/scope. Presence scheduling consumes recorded
dependencies in both emitter and interpreter. Refinement does not eliminate
nullable, escape selection scope or become branch-wide suppliedness. Persisted
absent/present optional fields retain R5.30's existing record membership meaning.

## 8. Relation compatibility boundary

`typed` establishes collection, identity, field and expression type compatibility;
`_relational(..., plan)` consumes those bindings during plan construction.
Its checked path bypasses all legacy `resolve`, `_compile` and raw-field type
comparisons. Canonical equivalent defaults are deduplicated; conflicting literals
reject there once. Unsupported non-default overlaps and unresolved equivalence
remain constructive lowering limits. Emission does not re-plan the conjunction.
The independent verifier checks the semantic relations against the observations,
including the joint defaults, rather than trusting the generator's intermediate
post-state construction.

## 9. Outcome authority

Every payload expression has a checked operand/result type; `outcomes` carries
the authoritative tag/type map to generated runtime metadata and conformance.
Integers/counts, strings, record constructors and projected post records retain
their checked types. Python literal values/code never determine payload type.
Observed payloads still undergo concrete type validation.

## 10. State-slot authority

`slots` and `bindings` carry pre/post shapes and resolved target/source paths.
Generated application dispatch uses the checked unit state shape, not a durable
example or a separately inferred application shape. The runtime and verifier
validate actual pre/post values against these declarations. The inventory's
version update/default/count migration remains same-shape; cross-shape state
evolution is outside this result.

## 11. Projection authority

`sole` receives its checked sequence element/result type; `project` receives
checked row/result types and field identities/types; `post` is a checked slot
reference. Neither projection emitter reconstructs a record schema. Required
singleton cardinality remains a concrete runtime/behavioral condition.

## 12. External capability authority

Analysis establishes `fresh_unique_id -> string` and `utc_clock -> instant`.
`GeneratedUnit.capability_shapes` now carries referenced signatures through
application dispatch into `Capabilities`. The provider supplies concrete values
and validates them against **those shapes**. The runtime's old signature table
is a historical default for standalone no-plan calls, not current type authority.
A test changes that fallback table to declare an integer clock: a checked current
clock remains an instant, while an integer provider value fails validation.

## 13. Legacy typer lifecycle

| Machinery | Retained role | Current authority? |
| --- | --- | --- |
| `typed_lowering_r5_12._compile` | HISTORICAL_TEST_SUPPORT, HISTORICAL_COMPILER_REPRODUCTION | No |
| `generative_r5_13.typed/ordering_plan/generate` | historical pinned reproduction and explicit legacy-subset bridge | No |
| `refined_generator_r5_28.typed/ordering_plan`, no-plan render | historical standalone test compatibility | No |
| verifier no-plan older-version `_compile` paths | historical test/reproduction support | No |
| `_field`, `_type`, `_path`, canonical/hash and shape-validation helpers | SHARED_NON_AUTHORITATIVE_HELPER under the designated analyzer, or concrete runtime validation | No alternate expression authority |
| `unified_types_r5_27.typed/analyze/checked_plan` | CURRENT_PIPELINE authoritative analysis | Yes, one path |

Nothing needed for pinned reproduction was deleted. The current-path legacy
delegation and downstream fallback inference were retirable call sites, removed
here; historical machinery remains outside the current authority count.

## 14. Verifier authority boundary

`interpret` evaluates all supported kinds directly from semantic requirements
and independently observed values. It no longer calls `_compile` or `analyze`;
selection element types, orders, projection fields, scopes, payload types and
state field bindings come from the checked plan. Shared type meaning is distinct
from a shared behavioral verdict: expected selection/normalization/removal/
replacement/default relations are evaluated independently of generated Python.
Actual output and state are challenged against independently captured endpoints.
Faults A–E demonstrate that a faithfully reported generator error is not accepted
because it used the same type analysis.

## 15. Internal consistency tests

`test_semantic_authority_r5_31.py` includes changed orders, operands, outcomes,
state bindings, projections, scopes and slots. Each causes an explicit compiler
internal-consistency failure before emission and interpretation. Alien copied
expressions and stale source also reject. The downstream reanalysis trap poisons
`analyze`, alternate emitter typing and alternate ordering **after** checking;
archive units still generate and the independent verifier still evaluates actual
read/write calls. No alternate typing interpretation is selected.

## 16. Semantic mutation propagation

Only source changes, with unchanged compiler/runtime/verifier:

| Mutation | Checked-plan change | Independently grounded conformant behavior |
| --- | --- | --- |
| instant-primary order → code-only order | `orders.keys`, source digest | B/A → A/B |
| post projection code+label → code | `projections`, result operand and `outcomes.ok` | two-field → code-only record |
| stable_unique(map(trim)) → map(trim) | expression closure and source digest | a/b → a/b/a |
| fallback default first → second | source-bound checked literal and digest; semantic type remains string | omitted value changes; explicit value remains explicit |
| cutoff / replacement value / removal target | checked source/operands/relation bindings | R5.29 source-only regressions still change query/post-state/removed row |

Source-only value mutations need not change the semantic **type**. They change
the originating checked source identity and downstream behavior while retaining
the checked type. No downstream special-case edits were made for mutations.

## 17. Current capability regression matrix

| Capability | Current-entry witness rerun | Result |
| --- | --- | --- |
| selection | archive refined queries | grounded/conformant |
| normalization | inventory; R5.31 normalization mutation | grounded/conformant |
| string ordering | inventory secondary code; R5.31 primary code mutation | grounded/conformant |
| integer ordering | inventory primary rank | grounded/conformant |
| instant ordering | archive created/code | grounded/conformant |
| optional refinement | persisted absent/present archive reads | grounded/conformant |
| before | archive cutoff predicates/mutation | grounded/conformant |
| fallback | archive labels; R5.31 default/explicit mutations | grounded/conformant |
| external | archive fresh ID/clock insertion | grounded/conformant |
| default_missing | inventory label/flag | grounded/conformant |
| cardinality | archive removal and inventory migration | grounded/conformant |
| insertion | archive create | grounded/conformant |
| remove | archive chain/target mutation | grounded/conformant |
| replace_field | archive chain/value mutation | grounded/conformant |
| projection | archive post result and R5.31 field mutation | grounded/conformant |
| record-valued outcomes | archive create/project | grounded/conformant |
| overlapping defaults | inventory two defaults over same rows | grounded/conformant |
| same-shape migration | inventory version/default/count | grounded/conformant |

These are bounded regression witnesses, not all inputs or per-capability
exhaustive fault coverage. The matrix preserves that distinction.

## 18. Five-operation application regression

The structurally assembled archive generates through `current_pipeline` and
runs the established eight-call sequence: create A, create B, query A, order B/A,
replace A, read new A, remove A, read empty. All eight calls ground and conform;
each post byte sequence equals the next pre bytes. Read-after-write closure and
optional refinement after persistence are re-established. Omitted `seen` remains
absent; supplied `seen` remains present and is the only qualifying refined row.

## 19. Inventory application regression

The unchanged R5.30 inventory compiles through the same entry. Normalize,
ordered read and migrate all ground and conform. Trim/deduplicate yields a/b;
integer rank then string code orders A/B; overlapping defaults supply untitled
and false; durable version becomes 2 and count is 2. No alternate generator
or inventory-specific compiler behavior is selected.

## 20. Fault matrix regression

| Fault | Observed semantic violation | Grounding | Conformance |
| --- | --- | --- | --- |
| A | absent optional row incorrectly admitted | pass | fail |
| B | chronological primary order reversed | pass | fail |
| C | replacement writes wrong field | pass | fail |
| D | persisted timestamp differs from recorded clock | pass | fail |
| E | read operation itself overwrites unrelated row | pass | fail |

E is the R5.30 operation-caused fault, not merely the older between-call
continuity discrepancy. Disposable artifact manifests are updated so the faults
challenge behavior after grounding, not stale provenance. Valid application
generation and source semantics remain unchanged.

## 21. Duplicate-authority negative test

The archive's refined instant-ordered expression is accepted by authoritative
analysis but rejected by historical `_compile` (`present` unsupported or instant
key non-orderable). This is a real historical disagreement risk: retyping during
downstream interpretation could reject a checked valid operation. The new test
first exhibits the historical rejection, then poisons legacy typing in checker,
emitter and verifier and runs the current operation. One checked interpretation
produces B/A, independently grounds and conforms. The old interpreter is kept
for historical reproduction, never selected by current compilation.

## 22. Raw-AST access audit

| Current/downstream access | Classification | Boundary |
| --- | --- | --- |
| application names/id, operation map/order, source canonical hashes in current entry | REQUIRED_NON_SEMANTIC_METADATA | dispatch, symbols and provenance; no expression types |
| emitter expression operator, literal value, child structure, branch order/tag and relation kind | REQUIRED_NON_SEMANTIC_METADATA | lowering an already checked node/value structure; every real expression requires its checked operand |
| emitter reference/fallback/presence addressing | REQUIRED_NON_SEMANTIC_METADATA | checked path/key membership machinery; no optional type or presence-witness discovery |
| emitter source-slot membership for scoped sort limitation | REQUIRED_NON_SEMANTIC_METADATA | constructive target constraint, not key type/orderability |
| source digest/alien-plan error messages | DIAGNOSTIC_ONLY | internal consistency and source attribution |
| verifier guards, predicates, literal values, relation/branch structure | LEGITIMATE_VERIFIER_SEMANTIC_INPUT | independently evaluates semantic behavior; static types/field bindings come from plan |
| former verifier `analyze(select)` / `_compile`, planner raw field typing, lost recursive plans | DUPLICATED_SEMANTIC_AUTHORITY | removed from current path |
| no-plan legacy emitter/verifier raw-type access | historical, outside current audit denominator | preserved for reproduction, not current authority |

The goal is zero downstream **competing semantic/type derivation**, not zero
AST structure or semantic requirement access. Backend construction and independent
verification necessarily consume operation structure and values.

## 23. Current entry-point invariant

New supported applications call `benchmark.semantic.current_pipeline.generate`,
then `observe/challenge`. Both archive and inventory use this entry. There is
no feature-based alternate checker/generator selection. Checking and independent
challenge-time analysis both use `unified_types_r5_27.checked_plan`; all downstream
static typing comes from its facts. The separate v0.3 task backend and historical
prototype APIs are not current authorities for this prospective subset.

## 24. Architecture gate

| Current-pipeline semantic authority | Count | Owner |
| --- | --- | --- |
| Semantic typing | **ONE** | authoritative typed analysis → complete CheckedPlan |
| Ordering semantics | **ONE** | authoritative ordering analysis → `orders` |
| Optional/refinement | **ONE** | authoritative scoped analysis → `facts/scopes` |
| Outcome typing | **ONE** | authoritative value/tag checking → `outcomes` |
| State-slot typing | **ONE** | authoritative state checking → `slots/bindings` |

This gate follows the call-path audit and negative authority tests. Test count
alone is not the decision criterion. Independent behavioral evaluation and
concrete runtime validation are not competing static type authorities.

## 25. Updated capability matrix

`R5_24-type-matrix.json` retains historical entries and adds
`r5_31_current_pipeline`: 20 supported capability rows with `semantic_authority`
pointing to the unified CheckedPlan architecture, five explicit one-authority
counts and core construct accounting. Historical/prototype evidence is not
relabeled as current authority. JSON parsing and authority-field checks pass.

## 26. R5.23 blocker reassessment

For the supported current same-shape subset:

- optional refinement: `RESOLVED_IN_SINGLE_AUTHORITY_CURRENT_PIPELINE`;
- instant ordering: `RESOLVED_IN_SINGLE_AUTHORITY_CURRENT_PIPELINE`.

Neither statement retries or establishes complete frozen B02 integration.
Historical locked results are preserved.

## 27. Remaining blockers and verification boundary

Independent classes remain suppliedness/well-formedness, malformed-input typed
outcomes, cross-shape state evolution and frozen transport binding. None was
implemented here. Target-string declarations, in-process node identities,
bounded constructive support, nested-order behavioral limitations and incomplete
exhaustive fault coverage remain research/compiler limitations, not duplicate
current type authorities. Universal implementation correctness is not claimed.

Verification (final code, Python **3.12.10**, isolated LF checkout of repository
HEAD plus the actual R5.31 patch and new test file):

| Check | Result |
| --- | --- |
| full `unittest discover -s benchmark/harness -v` | **286/286**, 233.457 s; includes architecture/grounding/semantic, relevant R5.10–R5.30 focused suites and all eight R5.31 tests |
| application/compiler `unittest discover -s tests -v` | **31/31** |
| model `validate air/task_manager.json` | OK |
| model `safety air/task_manager.json` | 0 capability violations, 0 invalid transitions |
| capability-matrix JSON / authority fields | valid, 20 current rows |
| `git diff --check` | passed; line-ending notices reported separately |

Environment investigation: `python` was absent and `py -3` selected Python 3.9,
below the supported minimum. That first full attempt reported 12 failures / 69
errors (285 test methods), including unsupported annotations and CRLF working-tree
hash drift on untouched pinned files; the application/compiler run had one import
error, and validation could not import the compiler. `git ls-files --eol` confirmed
LF index / CRLF working bytes for untouched locked files. No locks were changed.
An official Python 3.12.10 embeddable interpreter and a `core.autocrlf=false`
temporary clone restored the supported runtime and exact pinned LF bytes. The
first supported full run timed out at 240 s; a longer run passed, and the final
run after capability-binding and ordering-key fact closure passed all 286 methods. One new runtime
negative test initially rejected its malformed descriptor in the descriptor
builder; it was corrected to inject directly at the intended runtime boundary.

The requested full historical harness contains existing B02-shaped diagnostic
tests and nested historical Conventional acceptance cases (including B02/B03).
Those executed as unchanged regression machinery. They are **not** a new B02
candidate, current-pipeline B02 generation, grounding, conformance, retry or
frozen B02 acceptance gate. No separate frozen B02 acceptance command was run.
This distinction is necessary to report the full-harness invocation accurately.

LF→CRLF Git notices were emitted for changed working-tree files. They are
not `diff --check` failures. The actual initial pinned-hash failures caused by
existing CRLF checkout bytes are separately recorded above, not dismissed as
mere notices. The LF test mirror did not modify frozen files in this workspace.

## 28. Construct/system accounting

- Candidate core semantic constructs: **30**; no construct #31.
- Historical categorized raw inventory: **46**, unchanged.
- New fields, seals, assertions, capability-shape plumbing and analysis memoization:
  compiler/type/runtime-binding machinery applying existing semantics.
- One current application entry and one current authoritative static type path;
  independent grounding and behavioral verdicts retained.
- Phase 5C remains paused; B03 untouched; B17 unexposed and unclassified.
- Semantic-first format remains globally unfrozen; R5.2.2 remains historical
  benchmark authority; no universal correctness claim.

## 29. Exact recommendation for R5.32

Begin a **bounded independent suppliedness/well-formedness semantic review**:
first audit what the existing 30 constructs can express and distinguish
well-formed-input domain requirements from malformed-input typed outcomes.
Use independent non-task source contracts and preserve this single-authority
pipeline. Produce a versioned design/expressiveness decision before authorizing
any capability implementation. Do not combine the review with cross-shape
migration or frozen transport implementation, do not authorize #31 by default,
and do not retry B02, advance Phase 5C/B03 or expose B17.

R5_31_SINGLE_SEMANTIC_AUTHORITY_VALIDATED
