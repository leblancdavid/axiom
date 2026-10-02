# R5.4 B01 operation-contract investigation — prospective halt

**STOP at B01.** R5.2.2 remains authoritative. This record and its synthetic
prototype are UNFROZEN. No Phase 5C run, later-clause adequacy restart, B17
exposure/classification, acceptance replacement or semantic schema freeze is
implied. Sources: frozen `benchmark/requirements/B01.md:3-6`, inherited
`benchmark/baseline.md:3-38`, original `benchmark/harness/regression.py:163-196`
and the R5.2.2 corrected B01 intermediate-state precondition. Observable
equivalence is the target; implementation structure is irrelevant.

## First: local sufficiency versus missing observation binding

Let `I` be a **valid invocation including omitted versus supplied arguments**,
`S` the actual persistent pre-state (including version and records), `R` the
actual public result, and `S'` the actual post-state of the **same invocation**.
`O` is a referenced operation value, not a new language operator per command.
For queries, `S' = S`; for errors, the result must carry an error outcome and
storage must remain unchanged. The task schema, identity, optional fields,
validity conditions and effect boundaries must be typed; `S` cannot merely be
an arbitrary list detached from persisted storage. Here are the variables
needed at each site, *before* proposing new vocabulary:

| Frozen observation | Locally reusable relation | Universally bound variables still needed |
| --- | --- | --- |
| Create input: supplied CRITICAL or omitted priority | typed literal/field equality, baseline input default | every valid `I.priority` (presence and value), `O=create`, `S`; reject invalid inputs separately |
| Create return: priority CRITICAL or NORMAL on omission, full returned task | field/equals | `I`, fresh `R.id`, `R.priority`, other fields, and same invocation's `S,S'` |
| Persisted create record | keyed record equality and field/equals; #44 only handles missing-field updates, **not insertion** | `S.records`, `S'.records`, `R.id` and record keyed by `R.id`; exactly one fresh ID, all old records preserved |
| Ordinary `list` result | #43 exact lexicographic order on a supplied collection | list `O,I,S,R,S'`; `S.records` as complete source and `R` as exact ordered result; `S'=S` |
| `list-high` result (including after completion) | #10–12 exact source-relative HIGH selection, composed with #43 | list-high `O,I,S,R,S'`, ordered source derived from **that** `S`; `S'=S` |
| State before `complete` | typed precondition/field equality | completed target `I.id`, task in `S.records`, unrelated records and actual pre-state of same invocation |
| State after `complete` | transition plus field equality; no general keyed update/frame relation yet | `R`, `S'.records`, target `I.id`, status and priority; exact preservation of all other fields/records |
| Explicit migration before-state | #44 accepts arbitrary supplied collections with optional priority | explicit `O=migrate`, actual legacy version and `S.records`; `I`, not a conveniently constructed before-list |
| Explicit migration after-state | #44 preserves keyed present fields and defaults absent priority | actual `S'.records`, `R.migrated`, version transition, all present fields, count and no other changes |

The remaining inherited baseline obligations still participate in a **complete**
B01 assessment: all accepted priority values and invalid-enum rejection;
nonblank title, verbatim description, new ID, pending status, UTC creation
time and optional due date; exact task shape; default create priority;
`list` includes completed records; `list-high` includes completed HIGH;
complete/delete retain task fields and return the appropriate record; legacy
read fails `migration_required` without write; explicit migration from both
old versions fills only missing fields, reports its actual count, is idempotent
on current/absent storage, and produces the current version; failed operations
do not mutate storage. The existing scenarios witness some instances, and
the baseline model/relations constrain some values, but none is universally
connected to actual invocation/state observations by this prototype. In
particular, a byte-level no-write guarantee is stronger than decoded record
equality. These are not silently certified by the table's local relations.

The **minimal observation spine** is `(O, I, S, outcome, S')`, where successful
`outcome` contains `R`; `O` may be fixed by the contract and thus omitted from
an individual tuple. `(input, pre-state, result, post-state)` is sufficient as
a *binding shape for one successful call*, not a complete B01 semantics: it
needs an operation reference, validity/error partition, persistent-state
projection, quantification, typed record/field relations and sequential
composition (`S'` of one call is `S` of the next). To enforce no-write failure,
the state representation may additionally have to distinguish exact stored
bytes from equal decoded records. A controlled clock/fresh ID belongs to the
environment of an invocation, not to a B01-specific binder.

## Candidate and scope

Propose **one generic operation-contract binder**: for each reachable valid
typed state `S` and each applicable typed invocation `I` of referenced `O`,
bind its actual outcome `R` and resulting state `S'`, and require a conjunction
of existing typed relations on projections of `(I,S,R,S')`. Quantification is
universal over invocations/states, *not* over arbitrary imagined outcomes: an
actual operation must produce an outcome, and every produced outcome must obey
the relation. A parameterized binder/relational inclusion can express this
without unrestricted first-order logic or arbitrary executable predicates.
The binding domain must define valid states and arguments; errors need a
disjoint applicable domain and typed error result. A state view must identify
the public storage observation, not a caller-supplied sample. For sequential
calls, use the same binder repeatedly with `S_next = S'`; this is composition,
not a `list-high` or migration-specific binding construct.

Typed slots minimally include an operation reference/signature, structured
input with presence, state-before and state-after of one compatible state
type, and a success/error result union. Fields/projections and the existing
finite-domain scope (#23), typed variable (#4), equality (#6), transition
(#21), precondition (#22), sequence (#3), schema (#1) and relations (#10–12,
#43–44) can be reused. **The separate prototype validators do not share
these types or bind an actual CLI invocation to storage.** A string `scope`
annotation, a finite `invoke`/`snapshot` scenario, or manually quantified
prose does not implement the binder. The candidate's totality, effect framing,
reachability, adapter soundness and source/result typing still need checked
semantics and lowering before a universal application claim is justified.

Composition test: #43 relates `S.records` to the full `list` result. #10–12
then relate that ordered source to `list-high`'s exact HIGH result (including
completed HIGH, excluding completed CRITICAL). #44 relates actual legacy
`S.records` to `S'.records` for explicit migration, preserving LOW/NORMAL/HIGH
when present and defaulting a missing priority. Typed field/equality relates
`I.priority`, `R.priority` and the same keyed post-record on create; **neither
#44 nor equality states fresh keyed insertion, uniqueness and preservation of
all other records**, or the exact updated-record result and frame for complete.
A small general keyed delta/frame relation might extend #44 rather than
inventing command-specific transitions; this is unimplemented and cannot be
counted as solved by the binder. Likewise, migration result count/version and
read-without-write need relations over the entire state/outcome, not just #44.

## Independent priority-domain adjudication

The frozen B01 text says `CRITICAL` is “above `HIGH`” but exposes **no numeric
rank, priority-comparison command, priority-sorted list, or rank-dependent
behavior**. The inherited normal list order is `(created_at, id)`; `list-high`
uses exact equality. B12 later includes both HIGH and CRITICAL in urgent
selection, without assigning a relative rank. What is observable at B01 is
acceptance, exact round-trip in create/storage/list, exclusion from
`list-high`, and preservation/default for older priorities. A typed finite
ordered priority domain could encode the natural *intended* ordinal
`LOW < NORMAL < HIGH < CRITICAL`, but neither the full ordering of lower
labels nor a comparator's observable result is fixed by this text. A finite
enum already represents membership; an ordered domain is **not established
necessary** for these observables. Whether “above” imposes an independently
testable ordinal invariant remains **uncertain**; do not substitute priority
sorting for normal order, nor silently mark this clause semantically adequate.

## Vocabulary checkpoint and rejected alternatives

The existing ledger contains **44** constructs: 29 substantive, 9 finite
observation, 6 evolution/link; 28 have cross-clause reuse and 16 are
single-clause/fixture-only/administrative. #43–44 are already provisional
B01-origin relations. The synthetic tuple checker below adds **one provisional
concept**, generic operation-contract binding (#45), for a total of **45**:
30 substantive, 9 observation, 6 evolution/link; 28 demonstrated cross-clause
reuse, 17 not demonstrated. Plausible reuse is not counted as demonstrated.
It reuses equality and #44, including typed finite record validation; no
command name is a construct. This is a constrained test of the candidate,
not an integrated universal binder or a new frozen Lykoi language feature.

Rejected: per-command `create_task`/`list_tasks`/`list_high` or migration
binders (benchmark-specific); finite scenario enumeration as universal proof;
`sorted` observation (#35) as an order invariant; priority sorting as a proxy
for “above”; using #44 to model insertion; unrestricted logic/eval/Python
callbacks (unnecessary for the binding spine and too broad); requiring
Conventional and Lykoi to share an algorithm or data layout. A generalized
keyed update/frame is **deferred**, not rejected as unnecessary. If integration
requires several unrelated special-purpose binders, halt and reconsider the
representation rather than accumulating a benchmark DSL.

## Cross-clause reuse pressure only (frozen B02–B16 text)

All of B02–B16 have at least one public operation whose arguments, result,
pre-state and post-state need the same binder; this is **plausibility**, not
adequacy or an implemented encoding. B02/B04/B06/B10 add create input/field
defaults and migration; B03/B05/B09/B12 add exact ordered, nonmutating query
results; B07/B08/B11/B13/B14/B15 add success/failure transitions and no-write
frames; B16 adds users, ownership, failed create/migration and ordered
`list-users`. B02 additionally needs ordered normalization; B09/B12 time;
B14 graph acyclicity; B16 cross-entity identity. Those relations are
independent of binding and remain unimplemented/unchecked where applicable.
No features are added on behalf of those clauses and none is declared adequate.

## Synthetic fixture evidence and stop

`benchmark/semantic/operation-contract-fixtures.json` uses an arbitrary
`upgrade_items` operation, not a B01 command. The typed tuple checker reuses
#6 and #44 on one input/pre/result/post tuple: seven witnesses include two
distinct valid input/state populations, correct result with wrong state,
correct state with wrong result, wrong source, missing transition and unintended
mutation. The negative witnesses are rejected; they are not a proof over all
inputs/states. The result-equals-post constraint is **only this operation's
contract**, not a universal rule for CLI results. The fixtures do not invoke
an application, constrain an implementation over all states, establish a
storage adapter, or cover B01 create/list/complete/migrate. The checked
prototype exposes exactly why sample tuples alone cannot establish the
universal observation binding.

**B01 adequacy: NO.** Next precise gap: implement/check the generic binder's
universal scope and its connection to *actual* public invocations and
persistent pre/post-state, including sequential reads; currently #45 checks
only supplied tuples. Then test whether a generalized keyed insertion/update
frame and outcome relations are needed to finish the create/complete/migration
obligations. Independently resolve the “above HIGH” semantic uncertainty.
Do not proceed to B02 adequacy or a format freeze from these witnesses.
