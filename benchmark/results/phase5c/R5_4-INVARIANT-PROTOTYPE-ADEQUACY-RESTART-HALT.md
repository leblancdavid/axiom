# R5.4 invariant prototype and restarted adequacy screen — prospective halt

**Status: STOP at B01's format gap.** R5.2.2 remains authoritative. The
semantic-first schema is UNFROZEN; B17 is UNEXPOSED and UNCLASSIFIED. This
record does not replace the controlled-clock
[restart halt](R5_4-SEMANTIC-ADEQUACY-RESTART-HALT.md) or certify a B01–B16
bridge, application acceptance, or a future verification strategy.

## Declarative extension and bounded evidence

`benchmark/semantic/invariants.py` validates a separate prospective invariant
document. `scope` universally ranges over **all finite valid instances** of a
typed domain (string sequences or directed graphs); `bindings` name typed
inputs, outputs and observations; optional `precondition` restricts applicable
transitions; `transition.before/after` identifies the state pair; `property`
describes the required postcondition. `origin`, `when`, `depends_on`, `replaces`
and stable `id` identify provenance and checked semantic relationships. Each
`witnesses` link resolves to a scenario ID and a derived case ID with typed
bindings. There are no executable strings in the records. The existing
`format.py` scenario documents and `compile_plan` have **not** been replaced
or silently augmented; linking invariant cases to actual CLI acceptance is a
later bridge task.

| Primitive | Frozen reason and meaning |
| --- | --- |
| `finite_sequence`, `sequence[string]`, `for_each` | B02's arbitrary number of flags and each tag's nonblank validation; empty sequences satisfy `for_each` vacuously. |
| `trim`, `nonblank`, `map(trim)` | B02 trim each VALUE and reject whitespace-only VALUE; the collection mapping is not specific to tags. |
| `stable_unique(case_sensitive_string)` | B02 retain first transformed occurrence, preserving relative order under explicit case-sensitive equality. |
| `equals`, `and`, `not`, typed literal/variable | Compare pre/post collections or graphs and combine bounded conditions for B02/B14. These are closed typed forms, not a free expression evaluator. |
| `finite_directed_graph`, `graph[string]`, `add_edge`, `acyclic` | B14's arbitrary-size directed dependency relation, proposed edge, and cycle validity. Reachability is embodied by acyclicity; no task-specific predicate or graph traversal algorithm appears in the records. |
| transition scope / precondition | B02 input→output normalization and B14 valid before→accepted/rejected after transitions. |

The fixture has `B02.ordered_normalization`: for every finite valid input
sequence, output equals `stable_unique(map(trim(input)),
case_sensitive_string)`. It has `B14.accepted_edge_acyclic` and
`B14.cycle_rejection`: from an acyclic graph an accepted addition yields the
edge-extended acyclic graph; an addition that would cycle is rejected and does
not change the relation. B14's **separate self-reference error code** remains
a scenario requirement, not inferred from the cycle rule. Endpoint existence,
duplicate IDs, error envelopes, unrelated persisted fields and CLI wiring are
not certified by these graph rules. The evaluator rejects edges outside the
declared node set. The fixture graph represents directed ID relations, not
task objects.
Graph equality ignores node/edge enumeration order. No separate pairwise
quantifier, existential quantifier, reachability syntax or higher-order
function was added: first-occurrence comparison is covered by stable unique,
and arbitrary paths by acyclicity. A later frozen clause may justify a new
construct, but this prototype does not infer one from examples.

`invariant-fixtures.json` links invariant ID → scenario ID → derived case ID:
B02 empty, singleton, distinct, repeated duplicates/trim, and mixed-case order;
B14 no edges, simple edge, chain, branching, direct self-cycle, indirect cycle
and longer cycle. The local interpreter checks twelve linked cases and can
challenge the rules on new inputs. These are **semantic fixture cases**, not
subprocess acceptance of Conventional or Lykoi; even passing CLI witnesses
would not prove the universal rule. A later compiler/runtime may establish a
structural guarantee independently of these finite dynamic witnesses. Neither
strategy changes the requirement's declarative meaning.

## Fresh frozen-text screen, in order

Read `benchmark/requirements/B01.md` through `B16.md` from the beginning.
`S` = concrete scenario is needed, `I` = general invariant is needed,
`BOTH` = both; classifications concern frozen meaning, **not** claims that
records or active R5.2.2 carriers are complete. A scenario can witness a rule,
but cannot define it by enumeration. Rows after the first blocking gap are
screening findings only, not passed gates.

| Frozen clause (source lines) | Class | General meaning / concrete observable distinction; current format finding |
| --- | --- | --- |
| B01:3–6 priority domain and ordering | BOTH | Finite accepted priority values and `CRITICAL` above `HIGH`; ordering relation still untyped. Create/list and migration/default are concrete witnesses of general field rules. |
| B01:4–6 exact `list-high`, preservation and default | BOTH | **FIRST NEW BLOCKER:** exact HIGH selection and preservation across arbitrary old tasks require general selection/transition rules; default NORMAL and old LOW/NORMAL/HIGH examples are scenarios. |
| B02:3–5 zero or more tags; each trimmed nonblank | BOTH | Arbitrary finite sequence and universal validation expressed in typed B02 precondition; `invalid_tag` and no-write require concrete error witness **and** a rejection rule not yet encoded. |
| B02:4–7 case-sensitive first-occurrence order, returned field, omission/migration | BOTH | Compositionally expressed for valid inputs by `B02.ordered_normalization`; omission/migration/return on every task still need general field and migration rules plus scenarios. |
| B03:3–4 exact case-sensitive tag membership, completed inclusion, normal order | BOTH | Independent selection gap: cannot state general filter/membership over arbitrary task collections or preserve selected order in the present invariant vocabulary. Concrete list outputs alone cannot state it. |
| B03:5–7 blank error, absent tag, no-write, case example | BOTH | Negative input/query and no-write across all states are general constraints; absent/`work` vs `Work` are scenario witnesses. |
| B04:3–6 supplied source verbatim through create/list/mutation, omitted/migrated empty | BOTH | Arbitrary supplied string and preservation across mutations require field/transition projection not present; whitespace, default and migration are scenario witnesses. |
| B05:3–5 status selection, order, empty and read-only | BOTH | General filtered selection/order/no-write missing; pending/completed/empty scenarios witness it. |
| B06:3–7 category trim/default/error, exact filter and full list | BOTH | General conditional normalization, blank rejection and selection missing; empty/whitespace/migration and case-sensitive results are scenarios. |
| B07:3–6 ordered notes default, append trimmed nonblank, reject without change | BOTH | General append/validation and preservation of order for arbitrary repetitions missing; zero/repeated/blank are witnesses. |
| B08:3–8 archived status independence, terminal transition, visibility across named lists | BOTH | General field/transition and filter invariants missing; pending/completed and repeated-archive matrix are concrete witnesses. |
| B09:3–7 inclusive UTC window and pending/unarchived selection/order | BOTH | Typed time exists for strict `before`, but inclusive bound and general conjunction/filter rules are missing; equal/reversed/invalid boundaries, undated and no-write have scenarios. |
| B10:3–7 supplied owner trim/nonblank/default and exact case-sensitive filter | BOTH | General normalization and selection missing; error, omitted/migration/empty filter have witnesses; B16 later replaces optional ownership semantics. |
| B11:3–5 completed-unarchived delete rejection/no-write vs other deletes | BOTH | General conditional transition rule missing; pending/archived/completed matrix witnesses it. |
| B12:3–6 strict UTC urgent qualification and continuing all-priority overdue | BOTH | Controlled clock witnesses strict equality boundary, but general time/filter/order rule missing; priority/status/archive/no-write scenarios are needed. |
| B13:3–6 archived mutation prohibition, no reopen, retained delete/visibility | BOTH | General transition/allowed-operation constraint missing; error, no-write and retained behaviors need witnesses. No finite call proves absent operation. |
| B14:3–7 ordered ID dependencies, self/missing/duplicate/cycle validation | BOTH | Arbitrary-size cycle and accepted-edge relation are expressible by B14 fixture rules; ordered append, self-specific error, missing/duplicate and failed writes need separate general rules plus scenarios. |
| B14:8–9 archived reference identity and referenced-delete rejection | BOTH | Arbitrary referential integrity / delete prohibition is general; archival/deletion scenarios witness it. |
| B15:3–6 every dependency complete, archived-complete counts, failure no-write | BOTH | Universal relation lookup/transition predicate missing; pending/complete/archived, dependency preservation and prior transition precedence have scenarios. |
| B16:3–6 built-in system and arbitrary unique nonblank case-sensitive user IDs; sorted list | BOTH | General ID uniqueness/lookup/sorted-selection missing; duplicate/blank/system and ordered return scenarios witness it. |
| B16:7–11 existing required owner, migration mapping/unknown rejection and retry, prior owner filter | BOTH | General cross-entity membership/migration/atomicity missing; missing/unknown owner, old unowned, unknown migrated owner/retry and filter witnesses needed. |

The first new fundamental gap is already B01's universal exact-HIGH selection
over arbitrary task collections, not the number of available examples; B03
adds general tag membership to the same family. The inventory also exposes field projection,
conditional transitions, inclusive time, relationship lookup, query ordering
and negative/no-write properties requiring careful separate treatment. No
further primitives are added merely to finish the table. This is a **halted
adequacy review**, not a finding that all B01–B16 clauses are faithfully
represented. In particular the new B02/B14 records cover only their stated
subrules; the remaining clauses need verified IDs, conditions, executable
links and active replacement edges before the format gate can succeed.

Next research step: decide whether one small typed selection/relationship
projection construct can express B01, B03, B05, B08, B09, B12, B15 and B16 without
turning the requirement format into a second programming language. Review
the other gaps against frozen text before versioning. Do not advance bounded
bridge, B17 freeze/exposure/acceptance, checkpoint revalidation or B17-ready
status from this prototype.
