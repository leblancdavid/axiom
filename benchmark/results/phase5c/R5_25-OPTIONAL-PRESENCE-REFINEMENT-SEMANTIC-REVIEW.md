# R5.25 — Optional presence and refinement semantic review (prospective, 2026-10-03)

**Decision:** `EXISTING_TYPE_SYSTEM_GENERALIZATION`. The optional record type
already defines the truth of a membership test; a *scoped elimination rule* for
that type is missing. The separate R5.25 prototype makes that rule explicit
and type-checks/generates a non-task selection. It does not alter the R5.23
compiler, runtime or verifier and does not establish integration into them.

## 1. Exact question and 2. Current optional semantics

Can a relation requiring `T` consume `record.field : optional<T>` only when
the field is present, without coercion or a serialization-order dependency?
The prospective typed definitions in `typed_lowering_r5_12._type` (lines
15–36), `generative_runtime_r5_13.valid` (95–115), and
`generative_r5_13.shape_valid` define optional **record membership**: an
optional key may be missing; if present its value must satisfy `T`. A nullable
key is required and may hold null; `optional<nullable<T>>` permits both
omission and present null. Thus `ABSENT`, `PRESENT(null)` and
`PRESENT(value)` are distinct **only where both wrappers are declared**;
`PRESENT(null)` is invalid for `optional<instant>`. `_type`'s direct
`optional` case checks the *present value*, while the record case decides
whether omission is legal. This is semantic shape evidence, not inference
from Python's `None` or truthiness.

## 3. Optional state versus optional operation input

Both use the same typed record-membership rule. R5.24 independently observed
that an omitted input key and an explicitly supplied fallback value remain
distinct in a bound invocation. `fallback` checks parent membership and
returns a value, not a predicate; afterward its value does not reveal which
case occurred. Persisted state rows have their *own* membership, governed by
the durable row shape and the selection's `item` binding; input binding
metadata cannot refine them. Neither omission nor an empty string/zero is
null. Malformed raw input is outside this typed optional question.

## 4. Existing-composition attempts

| Attempt within existing 30 | Result | Reason |
| --- | --- | --- |
| Typed variables + `equals(field, null)` + `and` | INSUFFICIENT | optional and nullable have distinct types; equality demands matching declared types, and `and` previously checked each operand without narrowing. |
| Finite-domain membership/scope and `select` | INSUFFICIENT | collection membership tests values, not record-key membership; selection binds `item` but cannot change its projected field type. |
| Predicate `not`, `before` and `and` | INSUFFICIENT | Boolean composition cannot manufacture a typed present-value witness; unguarded `before` rejects `optional<instant>`. |
| Preconditions, operation #45 alternatives and postconditions | INSUFFICIENT | a guard can restrict a branch only after it can express presence; a branch tag does not prove a field exists in each row. |
| `default_missing` state relation | WRONG_LAYER | writes a missing field; not a scoped read-only selection condition. |
| Optional-input suppliedness / `fallback` | WRONG_LAYER | the input adapter observes input keys; a fallback invents a value for absence, changing the requested population. |
| Exact frames, equality of whole records, keyed projection | AMBIGUOUS | an exact record witness might imply required keys in a *particular* row, but existing projection refuses optional fields and no universal scoped destructuring/binding rule connects that fact to `before`. |

No currently implemented composition is EXPRESSIVE for this question; this
does **not** mean that optional types lack a defined presence condition.

## 5. Presence's responsibility and 6. refinement model

For a typed record, “field F is present” is a representation proposition
defined by `optional<T>` itself. It can affect application behavior (exact
selection), yet requires no independent domain-specific relation, external
fact or new capability. R5.25 serializes `{"presence":{"ref":["item","due"]}}`
as an *optional-type elimination witness*: it is true iff that key belongs to
the parent record. In a conjunctive scope containing that witness, the **same
stable path** has type `T` for checking dependent consumers. This is a
type-system generalization of existing optional record semantics, not a claim
that existing R5.23 syntax already supports it. The syntax is prospective
typing machinery, not core construct #31. No globally mutable type facts,
sentinel, implicit null exclusion, or application-specific instant rule.

## 7. Scope and 8. conjunction/order independence

Refinements are local to the smallest `and` that directly contains the
presence witness and its nested positive conjuncts. They do not escape that
conjunction, the `select.where` binder, an operation alternative, a
postcondition, or a distinct operation/state. A nested conjunction may use
an enclosing positive fact; a fact in a nested conjunct does not refine a
sibling. Negated presence establishes no present-value fact. The prototype
does not implement negation or implication. Same-path matching prevents a
guard on `item.other` from refining `item.due`. The positive conjunction
denotes a joint constraint; neither `[presence, before]` nor
`[before, presence]` is a procedural program. Validation gathers direct
presence facts over the complete conjunction before checking consumers;
emission evaluates the established presence tests first to avoid reading an
absent field. This scheduling is a checked implementation plan, not an
observable semantic order. Both serialized orders generate equal selection.

## 9. Positive and 10. negative fixtures

`test_optional_refinement_r5_25.py` runs a generated publication selection
against four typed rows: absent, before, after and equal to the cutoff. Exactly
`early` is selected for **each** serialized order; equal is not before. It
also changes the cutoff and changes the field to `other` using only semantic
source, then regenerates without editing the lowerer. Negative validation
rejects unguarded `before(optional<instant>, instant)`, a presence check on
required `id`, guarding `other` while comparing `due`, and attempting to
reuse a nested guard outside its conjunction. Contradictory present/absent
guards cannot be constructed here: the current bounded predicate syntax has
no absence/negation refinement rule. `optional<nullable<instant>>` with a
presence guard remains nullable and is rejected by `before`, rather than
silently treating present null as an instant.

## 11. Cross-type and 12. broader-refinement pressure

The structural witness accepts optional string (including `""`), integer
(including `0`), record (`{"key":"x"}`), and instant; none relies on
truthiness or timestamp parsing. Its elimination rule is generic
`optional<T> → T`; the fixture directly exercises membership for those
types, while only instant has a generated consuming relation here. Union
membership, successful parsing, tagged payloads, non-null and version
discriminators could share *scoped type facts* in a future type system, but
have different proof premises and no implementation/evidence in R5.25.
Presence alone must not be mistaken for a general proof calculus.

## 13. Representation comparison

| Model | Precision/minimality; validation and scope | Independence/reuse; order and AI risks |
| --- | --- | --- |
| A: ordinary `present` relation with compiler narrowing | precise if tied to record membership; adds a semantic predicate alongside typing | generic but risks counting a representational test twice; implicit far-away narrowing complicates edits |
| B: type-directed presence/refinement witness (chosen) | same truth condition, explicit stable path, smallest checked conjunction; minimal extension of optional elimination | target independent, reusable across T, locally validated; explicit guard costs tokens but edit failures are deterministic |
| C: guarded relation | explicit region and safe evaluation; extra relation wrapper | target independent but may imply procedural `when` order or duplicate conjunction nesting |
| D: implication plus explicit unwrap | can be precise under typed implication; `present ⇒ before` alone permits absent rows, so selection also needs presence | more nodes/bindings and nontrivial proof scope; easy AI omission of the positive selection condition |
| E: existing composition unchanged | no new syntax, but cannot type-check original projection | lacks a checked witness, so neither deterministic narrowing nor safe generation |

## 14. Accounting and 15. cross-clause pressure

Core application semantics remain **30**; +0 core. The new type-directed
presence witness and scoped narrowing change which **already-defined**
optional record states can be related by existing predicates, but introduce
no independently supplied application fact or new domain relation. Type
system/prototype +1; separate generator/checker +1 experimental path; no
historical count rewritten. The R5.23 optional-field blocker is demonstrated
in already-exposed material; R5.24's publications and independent sensor/
shipment examples make reuse plausible, not benchmark-demonstrated. No
additional frozen clause was reclassified and no B02 test was run.

## 16. AI-native assessment and 17. #31 gate

The machine-oriented `presence(ref(path))` has explicit type fact, stable
reference and local editability. Type checking gives deterministic errors
for a changed field/removed guard; validation is insensitive to conjunction
serialization. It costs a wrapper plus a path per guard, but avoids hidden
truthiness/sentinel interpretation. AI edits that move the fact outside its
scope fail early. Model B is preferable to a silent global narrowing or
order-sensitive short circuit. Decision: **`EXISTING_TYPE_SYSTEM_GENERALIZATION`**.

## 18. Prototype, 19. grounding/conformance and 20. blocker

`benchmark/semantic/optional_refinement_r5_25.py` validates typed declarations,
gathers scoped witness paths, checks `before`, generates a small read-only
selection executable and independently evaluates the originating contract.
The publication subprocess output and trace are compared with independently
read durable bytes: trace/pre/result/post agree, attempted_write is false,
and state bytes are unchanged. A disposable edited generated predicate admits
the absent row; its public output matches its trace and its state remains
read-only (**grounding passes**), while the independent contract evaluator
rejects it (**conformance fails**). This is bounded observation, not a general
attestation scheme or a proof of arbitrary code correctness.

The specific R5.23 optional-field blocker is **PARTIALLY_RESOLVED**: optional
state-field refinement is coherent and independently generated/type-checked,
but is not integrated into the pinned general multi-operation pipeline; a
nullable-present value would additionally need non-null refinement. Nothing
here establishes full B02 readiness.

## 21. Updated accounting and 22. exact R5.26 recommendation

Candidate core **30**, new core **0**, #31 **not justified**; historical raw
inventory unchanged. R5.26 should integrate this same scoped optional-type
elimination into a *separately versioned* general type checker, generator and
independent verifier, challenge nested/alternative scope and absent/null
read-only faults on at least two non-task domains, and separately decide
nullable elimination. Preserve R5.23 locks; do not conflate this with instant
ordering, malformed-input outcomes or cross-shape migration.

## Verification and phase boundary

Final verification: full benchmark harness **253/253** (including R5.10–R5.24
focused suites and four new R5.25 tests); application/compiler **31/31**;
R5.25 focused **4/4**; model validation **ok**; safety **0 capability
violations, 0 invalid transitions**; `git diff --check` **exit 0**. Git's
LF→CRLF notices for the three existing documentation files were line-ending
warnings, not failures. No B02 retry,
frozen B02 acceptance, B02-specific behavior, Phase 5C resumption or B03
advance; B17 remains unexposed and unclassified. The semantic-first format
remains globally unfrozen, R5.2.2 remains historical benchmark authority,
and universal implementation correctness is not claimed.

R5_25_OPTIONAL_REFINEMENT_RESOLVED
