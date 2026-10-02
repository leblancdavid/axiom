# R5.4 selection prototype and adequacy restart — prospective halt

**Status: STOP at B01.** R5.2.2 is authoritative; the semantic-first schema
and this prototype are UNFROZEN. B17 remains UNEXPOSED and UNCLASSIFIED.
This record follows the [invariant restart halt](R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md),
not a freeze, bridge, checkpoint revalidation or CLI acceptance result.

`benchmark/semantic/selection.py` adds one typed relation over arbitrary finite
ordered sequences of strings or declared records. Each rule distinguishes
`source`, `bind`, a closed typed `predicate`, `result`, `ordering`, and
`exactness`. `exact` requires positional sequence equality to **every**
qualifying source occurrence; `sound_only` requires an ordered subsequence of
qualifying occurrences and may omit matches. Equal-valued duplicates retain
their multiplicity. `source_relative` is the only implemented ordering mode.
Field access, typed equality, case-sensitive string membership, conjunction
and negation are composable expressions; no named task predicate, Python,
lambda, arbitrary function or free-form evaluation is admitted. The finite
interpreter is a fixture witness, not a prescribed algorithm: Lykoi and
Conventional may use loops, SQL, indexes, or any equivalent realization.

`selection-fixtures.json` states B01 exact HIGH and B03 exact membership by
the *same* construct. HIGH is a literal, not a selection opcode. The B03 rule
names `B02.ordered_normalization` as its stable dependency; the prototype
validator admits that ID and the focused test checks its existence in the
separate invariant fixture. Cross-document checked composition with all
active prior clauses is **not implemented**. B03's query input is used
verbatim; matching is case-sensitive. Empty, no match, one, multiple, all,
wrong order, omitted match and extra item, plus an unrelated conjunctive
predicate and sound-only counterexample are finite witnesses. They do not
prove the universal rule.

## Frozen-text restart from B01 (stop at first new general gap)

| Frozen clause | Classification and primitives | Adequacy |
| --- | --- | --- |
| B01:3–4 accepted CRITICAL priority, returned/persisted on create and list, above HIGH | Concrete scenario plus typed field/equality and ordering relation | Scenarios can witness domain, create and list; a general priority ordering relation is not typed here. |
| B01:4–5 list-high exactly HIGH across arbitrary tasks | Declarative selection/query composed from finite collection, record field, typed equality, exactness and source-relative order; concrete scenario witnesses | The selection rule expresses soundness **and** completeness for any *given ordered source*. The baseline `(created_at,id)` normal sort is not itself a typed universal order constraint; `sorted` in the scenario format checks finite observations only. It must be bound explicitly before this is a complete B01 query specification. |
| B01:5–6 old LOW/NORMAL/HIGH values preserved through migration, omitted priority defaults NORMAL | Transition constraint plus concrete scenarios, field projection/equality | **FIRST UNSOLVED GENERAL GAP after selection:** no general entity-field frame/preservation and default/migration transition relation for arbitrary old tasks. Finite seeds cannot state this universal property. STOP. |

The restarted adequacy gate therefore **does not pass B01**. B02–B16 are not
classified as passed or freshly screened beyond this stop. The prior
[inventory](R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md) remains a
screening guide, not a substitute for restarting their clauses after resolving
B01. Do not automatically add field-frame, sorting, conditional transition or
other operators merely to advance the table.

## Vocabulary checks at the stop

- B02's ordered first-occurrence normalization remains more precise as
  `stable_unique(map(trim(input)))` under a universal valid-input
  transition. Selection only takes a subset; it cannot transform strings or
  choose just the *first* equal transformed occurrence without extra position
  semantics. Keep B02's separate typed mechanism pending a justified unification.
- B14 remains a graph relation/transition invariant: accepted `add_edge`
  preserves `acyclic`; when proposed addition is cyclic, negation and unchanged
  graph constrain rejection. `acyclic` embodies reachability without adding
  recursion syntax. Its self-reference code and other clauses remain separate.
- Typed UTC clock/strict `before` exists in scenario observations, **not** in
  the selection predicate validator. Inclusive temporal comparison and graph
  reachability inside selection are unsupported; neither is justified by the
  newly stopped B01 screen. Membership is case-sensitive for strings; a
  general typed record/graph lookup across the two prototypes is not claimed.
- See the [42-entry ledger](R5_4-SELECTION-VOCABULARY-LEDGER.md) for reuse,
  single-purpose concepts, control-flow pressure and alternative formalisms.
  No unrestricted computation has been introduced, but duplication between
  validators is a warning against treating this as a finished small language.

Next decision is whether a *small general* state-field preservation/default
relation and an explicit normal-order binding can express B01 without growing
an unrestricted programming language. Continue the clause screen only after
that question is adjudicated. No bounded bridge, B17 freeze/cases/exposure,
checkpoint revalidation, B18–B20, or phase-completion claim follows.
