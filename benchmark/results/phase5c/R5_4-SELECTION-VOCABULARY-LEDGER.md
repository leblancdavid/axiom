# R5.4 proposed vocabulary ledger — unfrozen, 2026-10-02

Inventory of **implemented prototype constructs**, not a language freeze. Signatures
are schematic; `T` is a checked type, `Seq<T>` a finite ordered sequence, `G`
a finite directed graph. `Bxx` identifies the earliest frozen requirement
motivating the concept, not a proof of full clause coverage. `—` means
benchmark machinery or a baseline observation rather than a new Bxx clause.
Executable means interpreted by prototype fixtures/probe; metadata is never
application semantics. The two independent expression validators are not yet
one integrated typed schema.

| # | Primitive | Signature / meaning | First | Reused | Kind | Executable | Benchmark-only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | record schema | `name -> {field:T}` typed entity shape | B01 | B03 | data | yes | no |
| 2 | field | `record<T>.field -> T` projection | B01 | B03 | query | yes | no |
| 3 | finite sequence | `Seq<T>` ordered finite collection | B01 | B02,B03 | data | yes | no |
| 4 | var | `name:T -> T` bound value | B01 | B02,B03,B14 | data | yes | no |
| 5 | literal | typed string/bool constant | B01 | B02,B03,B14 | data | yes | no |
| 6 | equals | `T × T -> Bool`, type-matched equality | B01 | B02,B03,B14 | relation | yes | no |
| 7 | and | `Bool+ -> Bool` conjunction | B02 | B14; B01 fixture | relation | yes | no |
| 8 | not | `Bool -> Bool` complement | B14 | B01 fixture | relation | yes | no |
| 9 | contains | `Seq<T> × T -> Bool`, case-sensitive string equality | B03 | none yet | relation | yes | no |
| 10 | selection | `Seq<T> × (bound T -> Bool) × Seq<T>` relates source, predicate, result | B01 | B03 | query | yes | no |
| 11 | exactness | `exact | sound_only`; exact includes all qualifying occurrences | B01 | B03 | query | yes | no |
| 12 | source_relative | preserve source occurrence order in selected result | B01 | B03 | query | yes | no |
| 13 | trim | `String -> String`, strip outer whitespace | B02 | none in typed rules yet | relation | yes | no |
| 14 | nonblank | `String -> Bool` after explicit trim | B02 | none yet | invariant | yes | no |
| 15 | map(trim) | `Seq<String> -> Seq<String>` pointwise trim | B02 | none yet | relation | yes | no |
| 16 | stable_unique | `Seq<String> -> Seq<String>`, first case-sensitive occurrence | B02 | none yet | relation | yes | no |
| 17 | for_each | `Seq<String> × (String -> Bool) -> Bool`, universal check | B02 | none yet | invariant | yes | no |
| 18 | directed graph | finite nodes and ordered-pair edge set | B14 | none yet | data | yes | no |
| 19 | add_edge | `G × node × node -> G`, set addition | B14 | none yet | transition | yes | no |
| 20 | acyclic | `G -> Bool`, no node reaches itself | B14 | none yet | invariant | yes | no |
| 21 | transition | typed before/after pair | B02 | B14 | transition | yes | no |
| 22 | precondition | `Bool` restricts applicable transitions | B02 | B14 | transition | yes | no |
| 23 | finite domain scope | universal rule over finite sequence/graph instances | B02 | B14 | invariant | yes | no |
| 24 | clock | `utc_now -> Instant`, one controlled observation | B12 | none yet | observation | yes | yes |
| 25 | instant | parse UTC literal/result projection to typed instant | B09 | B12 | observation | yes | yes |
| 26 | offset | `Instant × integer seconds -> Instant` | B12 | none yet | observation | yes | yes |
| 27 | before | `Instant × Instant -> Bool`, strict time comparison | B09 | B12 | relation | yes | yes |
| 28 | scenario | ordered finite witness case | B01 | B02–B16 | observation | yes | yes |
| 29 | seed | write fixed JSON fixture state | B01 | B02–B16 | observation | yes | yes |
| 30 | invoke | observe public CLI call/result or error | B01 | B02–B16 | observation | yes | yes |
| 31 | snapshot | observe `tasks.json` bytes/absence | B01 | B02–B16 | observation | yes | yes |
| 32 | observe | compare bound values by relation | B01 | B02–B16 | observation | yes | yes |
| 33 | ref | scenario result/field/index reference | B01 | B02–B16 | observation | yes | yes |
| 34 | list | construct finite observation list | B01 | B02–B16 | observation | yes | yes |
| 35 | sorted | sort observed rows by declared fields | B01 | B16 | observation | yes | yes |
| 36 | distinct | compare observed values for inequality | B01 | later witnesses | observation | yes | yes |
| 37 | adds | introduce scenario assertion/root | B01 | B02–B16 | benchmark evolution metadata | no | yes |
| 38 | retains | scenario lineage retains prior meaning | B01 | B02–B16 | benchmark evolution metadata | no | yes |
| 39 | replaces | checked root replacement (scenario lineage still unchecked) | B11 | later clauses | benchmark evolution metadata | no | yes |
| 40 | depends_on | checked active semantic-ID prerequisite in relationship composer | B03 | later clauses | benchmark evolution metadata | no | yes |
| 41 | when | requires/forbids achieved history | B01 | B02–B16 | benchmark evolution metadata | no | yes |
| 42 | carrier | names historical acceptance method for later verification | — | B01–B16 | benchmark evolution metadata | no | yes |
| 43 | lexicographic_order | `Seq<Record> × ordered typed field keys × Seq<Record> -> Bool`; exact multiset and strict ascending key order | B01 | none yet | query relation | yes | no |
| 44 | default_missing | keyed finite before/after collections; preserve present fields, fill absent field, preserve identity set | B01 | none yet | transition relation | yes | no |

**Count at selection halt.** 42 named constructs: 27 substantive data,
relation, query, invariant, transition and clock constructs (#1–27), 9
finite-witness observation constructs (#28–36), 6 evolution/link constructs
(#37–42). **28 are reused by multiple frozen clauses** (#1–7,
#10–12, #21–23, #25, #27–35, #37–41); **14 have only one frozen
clause, fixture-only reuse, or administrative use** (#8–9, #13–20,
#24, #26, #36, #42). Of the latter, #8 also occurs in a non-frozen
B01 conjunction fixture. The categories are not a score of expressive adequacy.
`sorted` is an observation operator, not yet a typed universal query-order
constraint. Scope, ordering, selection exactness, and `depends_on` are counted
separately because each imposes an independent semantic obligation. The ledger
does not count Python implementation helpers or CLI command names as primitives.

There is no unrestricted loop, recursion, mutation or arbitrary user function
in the records. `for_each`, selection and `map(trim)` are bounded declarative
operators over finite collections; the interpreter's loops implement their
meaning, not an algorithm imposed on either benchmark track. Nevertheless
the 42-entry inventory, two distinct expression validators and one-off
operators show **real language-creep pressure**. It remains defensible as a
declarative requirements prototype, not a general programming language; that
assessment must be revisited at each gap. A small relational logic (selection,
projection, ordering and constraints), finite relational model checker or
existing constraint notation might reduce custom syntax, but would still need
typed time, ordered first-occurrence normalization, transition/CLI observations
and historical lineage. No comparative encoding or size measurement has been
done, so fewer concepts is a hypothesis, not a finding. No technology change
is authorized by this ledger.

## B01 ordering and migration restart (prospective)

Current inventory: **44** named constructs, **29** substantive (#1–27,
#43–44), **9** finite-observation (#28–36), **6** evolution/link (#37–42).
**28** have cross-clause reuse as enumerated above; **16** are single-clause,
fixture-only or administrative (#8–9, #13–20, #24, #26, #36, #42–44).
Reused building blocks for the new rules are records, fields, finite sequences,
typed equality, transition/precondition and finite-domain scope (#1–6,
#21–23); typed instant (#25) now also has a B01 use. `sorted` (#35) remains
an observation operator, not a substitute for #43. B01-only #43–44 are
provisional: keyed field default is plausibly reusable for schema evolution;
lexicographic order for other exact-result queries. Neither reuse claim proves
necessity. The existing `source_relative` selection (#12) composes with #43
when its source is the ordered task sequence; no new selection mode is needed.

Pressure: #43 needs type-safe instant ordering and unique keys for the valid
task domain; #44 currently models a single optional default and requires
fully declared record fields. Neither connects a rule to a public command or
persisted state. A smaller alternative may be a typed finite relational
constraint notation with keyed record equality and an ordered result view;
another is a generic frame condition plus an explicit missing-field default.
No size comparison or adequacy proof has established either as simpler. Avoid
turning these relations into an arbitrary expression evaluator or a special
B01 migration procedure.

## B01 operation-contract investigation (prospective)

**45** provisional named constructs: **30 substantive** (#1–27, #43–45),
**9** finite-observation (#28–36), **6** evolution/link (#37–42). The
demonstrated cross-clause reuse count remains **28**; **17** have only
single-clause, fixture or administrative use. Candidate #45 is a generic typed
operation-tuple contract/binder, not an additional command construct. Its
synthetic checker currently evaluates only supplied tuples, so actual
application binding and universal scope are **proposed, not implemented**.

| # | Primitive | Signature / meaning | First | Reused | Kind | Executable | Benchmark-only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | operation contract (partial tuple prototype) | referenced `O`, typed `(I,S,R,S')` and existing relations; universal actual-operation binding proposed | B01 | B02–B16 plausible, not demonstrated | contract | supplied tuple only | no |

See [the operation-contract halt](R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md)
for the rejected alternatives, source/return/state scope, priority-domain
uncertainty and precise remaining gate. Earlier 42/44 counts above are
historical checkpoint counts, not the current inventory.
