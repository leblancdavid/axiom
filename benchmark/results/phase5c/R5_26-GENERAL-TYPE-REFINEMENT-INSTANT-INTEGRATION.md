# R5.26 — General type refinement and instant integration (prospective, 2026-10-03)

**Decision:** `R5_26_REFINEMENT_INSTANT_INTEGRATION_PARTIAL`.
Both type capabilities and their joint selection/order composition work in a
versioned, general *read-only* #45 operation profile, but this profile does not
extend the full R5.23 generator's writing transitions, expression coverage or
whole-program assembly. It is not complete integration into the general
checker/generator/verifier across all previously supported operations.

## 1–5. Integration, representation, scope, order and dependency planning

`benchmark/semantic/type_integration_r5_26.py` accepts contract version
`R5.26`, consumes the same `id/input/state/branches` semantic AST shape as the
prospective general generator, and generates operations on its existing runtime.
The locked R5.23 generator, interpreter, runtime and evidence remain byte-for-byte
intact. The observer from `generative_evidence_r5_13.observe` independently
captures the subprocess, public output, event and durable bytes; R5.26 owns its
own challenge/verifier, bound to its own semantic source and provenance hashes.
`present(ref(path))` is an optional-type elimination witness, not construct #31:
the key must be a declared `optional<T>` field; only that exact tuple of binding
and field names is available as `T` inside its smallest positive conjunction.
The checker gathers direct witnesses before checking every conjunct, regardless
of serialization order, and the lowerer schedules presence checks before
consumers. Nested conjunction witnesses do not license sibling predicates;
selection's `item` scope is reset for every row. There is no global narrowing.

## 6–10. Rejection, genericity, exact selection and durable preservation

`test_type_integration_r5_26.py` rejects unguarded optional instant use,
same-typed wrong-field and wrong-record witnesses, use outside a nested
conjunction, post-state reference from a pre-state selection, present on a
required field, and optional keys used for ordering without prior selection.
The same checker/lowerer/verifier works for optional string and integer equality
without specialized branches. For the publication archive, the read-only
operation generated from its AST selects `early-b, early-a` out of absent,
before, after and equal rows for either conjunction serialization; the equal
instant is excluded by strict `before`. Independent durable file bytes are
identical before and after the public call; the event reports no attempted write.

## 11–15. Instant ordering, ties and composition

The R5.26 type capability admits required `instant` keys to the R5.20-style
target-neutral lexicographic plan, together with string and integer secondary
keys. The lowerer compares parsed UTC instants (not lexicographic timestamp
strings); the independent verifier checks exact multiset and nondecreasing
declared key tuples. Equal-key permutations conform, even if Python happens
to return stable order. A selected `optional<instant>` population may order by
that field only when the selection predicate proves its presence on `item`.
The generated `present + before(cutoff) + exact select + order` path executes
and conforms; raw optional-key order rejects instead of defining absent-key
behavior. These are read-only collection operations, not a whole-program
transition integration.

## 16–19. Mutations, grounding, faults and checker/verifier agreement

Changing only the input cutoff yields three matches at `LATE` and none at
`EARLY`; semantic-only optional-field mutations on string/integer collections
change the exact selected population. Key sequences `instant`, `instant +
string`, and `instant + integer` yield the corresponding distinct sorted
tuples without checker/lowerer/verifier edits. Normal optional selection,
instant order, and combined optional-instant ordering pass provenance,
independent public/event/file grounding and semantic conformance. Disposable
fault A includes an absent row: provenance and grounding pass; exact semantic
selection fails. Fault B reverses instant order: grounding passes, ordering
conformance fails. Fault C uses a different optional field's witness and is
rejected before generation. Direct verifier checks accept a declared-key tie
permutation and refuse the corresponding unsafe contract at the checker.
The verifier interprets membership, `before`, exact selection and rank/multiset
constraints from the contract; it does not compare results to the generated
sorting algorithm. These are finite witnesses, not universal correctness.

## 20–24. Matrix, blockers, accounting and next phase

`R5_24-type-matrix.json` retains its historical locked-generator entries and
adds `r5_26_integration`: `instant -> order` and scoped
`optional<T> + present -> relation(T)` are supported **in the R5.26 read-only
profile**; unselected optional keys and nullable instant comparisons are
invalid. Writing transitions and nested ordered outcomes in this profile are
explicitly unsupported. The R5.23 instant-order and optional-refinement
blockers are **RESOLVED_INDEPENDENTLY for read-only programs**, but remain
**PARTIALLY_RESOLVED for full general whole-program integration**. No claim of
complete B02 readiness follows. R5.27 should integrate the type/refinement
analysis and semantic ordering verifier into a separately versioned full
operation pipeline, preserving historical hashes, then challenge writing and
mixed-branch operations in fresh non-task domains before revisiting any frozen
request. Separately study input suppliedness/well-formedness and typed malformed
outcomes; separately study `S_pre -> S_post` cross-shape migration; frozen
transport binding remains outstanding. Neither class was implemented here.

Candidate core semantics remain **30**, no #31: type-system elimination,
ordering capability closure, target lowering and semantic verification are
separate system changes. No B02 retry, complete generation, frozen acceptance,
grounding or conformance was run; Phase 5C stays paused, B03 untouched, B17
unexposed and unclassified, semantic-first format globally unfrozen and R5.2.2
historically authoritative. Universal implementation correctness is not claimed.

Verification: full benchmark harness 259/259 (including architecture,
grounding, R5.10–R5.25 and six R5.26 focused tests); application/compiler
31/31; model validation ok; safety zero violations and invalid transitions;
focused R5.26 6/6; machine-readable matrix parses; `git diff --check` clean.
The initial full run exposed an attempted edit to pinned R5.23 evidence;
restoration and the final full rerun passed the pinned hash test. Git LF→CRLF
notices are separate warnings, not failures.

**Phase gate:** `R5_26_REFINEMENT_INSTANT_INTEGRATION_PARTIAL`
