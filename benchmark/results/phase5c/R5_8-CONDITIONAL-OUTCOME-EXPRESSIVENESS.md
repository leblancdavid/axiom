# R5.8 conditional outcome expressiveness — prospective, 2026-10-02

**Boundary:** focused review of the unfrozen R5.5/R5.7 synthetic operation
contract. This does not modify frozen requirements, cases, benchmark histories,
the v0.3 compiler or R5.2.2. R5.7's grounding architecture remains in place.

## 1. Abstract requirement and 2. exact gap

For an invocation with input `I`, pre-state `S`, outcome `O` and post-state
`S'`, let `C(I,S)` be a well-typed predicate and `E` a typed outcome class.
The obligation is `C(I,S) => (O.kind = E and S' = S)`; complementary
conditions may require other outcome classes and post-state relations. An
operation contract constrains each applicable tuple, not an implementation's
choice of branches. `S` here is the declared semantic state view.

| Question | Existing 29 candidates | R5.7 executable contract before R5.8 |
| --- | --- | --- |
| Express `C`? | Yes, for the selected state predicate: #44 `default_missing(S,S)` holds exactly when the optional field is present in every row; #7/#8 compose predicates. Other predicates need their own typed relations. | No predicate expression accepted in #45's flat checks. |
| Express typed `E`? | #1 record, #2 projection, #3 finite collection and #5 literal allow a record with an explicitly finite tag domain; a mere unbounded string is insufficient. | `result` was required to be a record sequence, not a tagged outcome. |
| Express alternatives? | #7 conjunction and #8 complement express implication `not(and(C,not(P)))`, including multiple cases. | Flat checks are an unconditional conjunction only. |
| Express `S'=S`? | Yes, #6 equality of type-matched state values. | Yes, as `equals(pre.records,post.records)`. |
| Associate condition, outcome and post-state for one call? | Possible *conceptually* within #45's four-slot relation using Boolean composition. | No: typed outcome and nested predicates had no integrated checker. |
| Coexistence of success/failure? | Possible as complementary constraints on the same typed tuple. | No: the envelope classification was outside the relation. |

Thus no new logical primitive is needed, but the existing **operation contract
#45 needs generalization** from a flat, uniform-sequence checker to typed
outcome projection and Boolean composition over its four slots. This is a
prototype implementation/generalization, not a claim that all 29 constructs
are integrated or all outcome signatures are supported.

## 3. Existing-composition attempts

1. **Flat equalities plus #44**: `input=pre`, `default_missing(pre,post)`,
   `result=post` accepts an already-complete input with both success and error
   public classifications; the classification is not a slot value. It also
   rejects an otherwise valid typed envelope as the result. Failed at outcome
   typing/association, not at state equality.
2. **#22 precondition `C` on an error-only operation**: it restricts which
   tuples apply, but leaves successful invocations outside this operation's
   contract; two independently named operations do not constrain the same
   public invocation. Failed at total alternative coverage for one operation.
3. **Finite fixtures/finite domain scope #23 or scenario error expectation
   #30 (historical non-core)**: sampled inputs and expected error observations
   cannot impose a general predicate on every applicable operation tuple.
   Finite-domain quantification can scope a rule but does not create the
   missing outcome/condition association; scenario `when` #41 selects benchmark
   histories, not state-dependent operation behavior.
4. **Typed record with a tag and common value, plus #6/#7/#8/#44 under #45**:
   `C := default_missing(S,S)`; `F := (O.kind=error and S'=S)`;
   `T := (O.kind=success and default_missing(S,S'))`.
   Require `not(and(C,not(F)))` and `not(and(not(C),not(T)))` with
   `I=S` and `O.value=S'` as shared constraints. This is exact for the selected
   typed domain, including the empty sequence, and rejects both wrong tags and
   wrong state. Verbosity is immaterial. The 29-concept composition succeeds;
   R5.7's checker needed the #45 generalization to accept it.

## 4. Error-specific versus general-outcome models

| Model | Assessment |
| --- | --- |
| A: error-specific `when/error/unchanged` | Short here, but couples errors to no-change and needs more machinery for recoverable errors, success variants and stateful failures. Reject as a core addition. |
| B: conditional outcome/postcondition cases | General and local; a case table is convenient machine serialization but demands rules for overlap, exhaustiveness and combined constraints. Can be a view over the relation, not a new core construct. |
| C: typed relation on `(I,S,O,S')` | Smallest semantic foundation already represented by #45; compose constraints on its slots. No prescribed order/control flow. Completeness/consistency across conditions remains a contract authoring/validation obligation. |
| D: existing primitives composed differently | Selected solution: #1–8, #21–23, #44 and generalized #45 typed projection/evaluation. No separate branch or error primitive. |

## 5. No-write analysis

`S'=S` is sufficient for **no semantic state change** in the declared view.
It is also sufficient for **no durable state change** only if that view
faithfully includes all relevant durable state (or a separately checked state
equivalence relation does). It does not imply no attempted write, no temporary
write followed by restoration, byte-identical serialization, or absence of
side effects outside the view. R5.7's selected failure execution leaves the
one observed file unchanged and reports no attempted commit. This R5.8
contract requires the observable post-state to equal the pre-state; the
grounding runner independently reads the file before and after, while the
unchallenged attempted-write bit is not a semantic conformance condition.
The prior adapter byte-hash policy is removed as a source of the obligation.
If byte-identical endpoints become an independent requirement, bytes/absence
must be part of a checked durable state view or an explicit effect contract;
if *no attempted write* is required, an effect/effect-boundary semantics plus
independent observation is needed. An implementation policy or self-reported
bit alone cannot establish it. No `no_write` primitive is justified by this
case. Undeclared resources and intermediate writes remain outside this view.

## 6. Typed outcomes and 7. conditional association

The R5.8 synthetic signature uses an outcome record with a checked finite
`kind` domain `{success,error}` and a `value` of the same typed record sequence
as the state. The challenged *public* classification and result populate
these fields. Literal tags alone do not establish a type: validation rejects
unknown tags and mismatched payload types. Equality and field projection
constrain each tag in relation to input and state. A success with value and a
failure with value are demonstrated; success without value, validation,
not-found and permission errors, and distinct payload types per variant are
**conceptual pressure tests only**. A general finite tagged-record/sum domain
would need variant-dependent payload typing and totality checks; this narrow
checker does not pretend to implement them. A uniform record plus finite tag
already distinguishes multiple classes if its shared payload type suffices.

Formal mechanism: conjunction of type-checked predicates on the *same* tuple,
using `not(and(C,not(P)))` as implication; `P` can itself conjoin tag, value
and post-state constraints. Two such predicates express complementary cases.
No new branch operator, procedural `if`, evaluation order, or external adapter
rule is introduced. The current validator checks well-formed references and
types; it does not prove case disjointness, exhaustiveness for arbitrary
predicates or semantic satisfiability. The two conditions in this fixture are
syntactically complementary (`C`, `not C`), hence jointly cover each typed
invocation by Boolean logic.

## 8. Generality pressure test (conceptual, not benchmark implementations)

| Shape | Relational encoding | Status |
| --- | --- | --- |
| Validation failure, unchanged | `invalid(I,S) => (O.kind=validation_error and S'=S)` | Plausible when `invalid` has a typed predicate; not executed. |
| Not found, unchanged | `not(exists(key,S)) => (O.kind=not_found and S'=S)` | Plausible with typed membership; not executed. |
| Permission failure, unchanged | `not(authorized(I,S)) => (O.kind=permission_error and S'=S)` | Authorization predicate/effect scope not implemented. |
| Success with mutation | `allowed(I,S) => (O.kind=success and transition(S,S'))` | Demonstrated only for the synthetic #44 default transition. |
| Alternate successes | `C1 => tag=created`, `C2 => tag=already_present`, each with own state relation | Multiple finite tags are representable; variant payload typing untested. |
| Condition-dependent transitions | `C1 => P1(S,S')`, `not C1 => P2(S,S')` | Boolean structure demonstrated; other transitions untested. |

None of these formulas requires an error-specific operator. They do require
domain predicates and state relations that the current prototype may lack.

## 9. Cross-clause pressure test (exposed B01–B16 only)

**Plausible reuse from frozen text, not demonstrated reuse or adequacy:** B07
blank-note rejection; B08 repeated-archive failure; B11 completed-unarchived
deletion versus allowed deletion; B14 self/nonexistent/duplicate/cycle failures
and referenced-task deletion; B16 blank/duplicate user, missing/unknown owner
and invalid migration. Each juxtaposes a condition, a classified outcome and
an unchanged or changed state. B14 explicitly requires unchanged tasks on
failure; B16 invalid migration says no data change. Ownership/authorization
predicates for B16 are separate domain work, not provided here. **Demonstrated
reuse in those clauses: none.** R5.8 did not execute or reclassify any B01–B16
case; the only integrated execution is the synthetic operation.

## 10. AI-native representation assessment

| Property | Error-only rule | Explicit case table | Typed relational predicates (selected) |
| --- | --- | --- | --- |
| Structural regularity / deterministic generation | Regular but special-purpose | Regular, simple case edits | Regular recursive `and/not/equals/relation` nodes; deterministic validation |
| Explicit typing | Needs separate error/value schema | Naturally per case | Checked slot projections, finite tag and common payload type here |
| Locality / partial modification | Error local; success separate | Branch local; overlap coordination required | Each constraint local to #45; complement conditions reference same slots |
| Stable identity / references | Error IDs possible | Case IDs useful but new reference scheme | Existing operation ID and slot references; no new identity layer |
| Machine validation / ambiguity | Easy locally; unclear coverage | Must validate overlap/coverage | Closed node forms and type checks; logic is declarative, coverage still author responsibility |
| Token overhead | Low for one error; grows with cases | Moderate | Nested Boolean expressions verbose, mechanically manageable |
| Target independence | Yes if abstract | Yes if abstract | Yes; no host exception or branch syntax |

Human readability is not a selection criterion. The relational form avoids
new procedural interpretations and new identity/overlap semantics; its nested
representation costs tokens but is deterministically editable. Comparison is
qualitative, not an AI-authoring benchmark or proof of ease of modification.

## 11. Construct #30 decision and 12. semantic changes

**EXISTING_CONSTRUCT_GENERALIZATION.** Generalize #45's evaluator/contract
shape to accept a finite tagged outcome record and composed typed Boolean
relations over the same four slots. This is integration of existing record,
field, literal, equality, conjunction, complement and state relations, rather
than a new orthogonal construct. The prior flat-sequence `checks` format remains
valid for the historical synthetic fixture. The prospective typed signature is
closed to unsupported nodes, values and outcome tags; `default_missing(pre,pre)`
is permitted as a state predicate. No benchmark compiler/schema/backend is
changed. The two implication constraints replace the R5.7 adapter failure
policy. The semantic responsibility remains within #45 and the types it uses.

## 13. Narrow R5.7 integration result

`grounding_r5_7.contract()` now declares the typed outcome and both conditions.
The challenged public classification/result are combined into the typed outcome
for the existing conformance evaluator; the internal classification/result
must first agree with public observation. The pre/post facts still come from
independent durable readback. No new grounding infrastructure was added.

| Grounded run | Provenance | Challenge | Semantic conformance |
| --- | --- | --- | --- |
| Correct already-complete typed failure, unchanged file | valid | passed | true |
| Error classification with changed durable state | valid | passed | false |
| Incorrect success tag on already-complete input, unchanged state | valid | passed | false |
| Correct success/default transition | valid | passed | true |

Existing false-report and artifact-drift tests still challenge evidence before
semantic evaluation. The results concern these observed calls only, not all
states, actual no-attempted-write guarantees or general compiler correctness.

## 14. Construct accounting and 15. remaining limitations

Historical raw numbered inventory **45**, unchanged: 13 core/domain + 11
collection + 4 state + 1 operation = **29 candidate core**; 3 observation +
2 verification + 5 evidence/testing + 5 evolution/link + 1 administration =
16 non-core. R5.7's separate unnumbered implementation-responsibility inventory
remains 12, so its expanded accounting denominator remains **57**. R5.8 adds
no numbered construct and no separate grounding responsibility; generalized
typing/Boolean evaluation is within existing #45. The new focused tests and
variant are test cases, not semantic primitives or a revision of the historical
ledger. This is neither a minimality proof nor a semantic format freeze.

The checker is still a bounded prototype: one shared payload type for all
tags, fixed four-slot mapping, one observed durable file, no general effect
model, no completeness/overlap solver for arbitrary conditions, no universal
conformance proof, and no demonstration on an unseen domain. Its `value=post`
rule is specific to this synthetic contract, not universal outcome semantics.
Byte-identical no-write and no attempted write are not proved by the semantic
equality alone. R5.2.2 remains authoritative; B01 remains inadequate and
halted, Phase 5C paused, B17 unexposed and unclassified, semantic-first format
unfrozen.

## 16. Exact recommended next step and verification

Challenge the generalized #45 contract on an **unseen, non-benchmark operation**
with two outcome classes requiring *different payload types*, independently
reviewing typing and case exhaustiveness; retain the same separation of
contract, binding, grounding and case-scoped verification. Do not resume B01 or
freeze the format on the basis of this synthetic result.

Verification from the repository root: complete benchmark harness **128 tests
OK**; application/compiler suite **31 tests OK**; focused architecture **6
tests OK**; focused grounding **10 tests OK**; new focused semantic tests **3
tests OK**. `git diff --check` exited 0 with no whitespace diagnostics on
tracked changes. Git separately reported LF-to-CRLF working-copy warnings for
five tracked files; these were not test failures. Each of the six new/untracked
files was separately checked with `git diff --no-index --check -- NUL <file>`:
no whitespace diagnostics (Git exits 1 for the new-file difference itself).
Git separately reported LF-to-CRLF warnings for those files as well. These
checks are development evidence, not proof of universal conformance or
benchmark adequacy.

R5_8_SEMANTIC_GAP_RESOLVED
