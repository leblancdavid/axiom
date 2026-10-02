# R5.4 bounded bridge — semantic-format adequacy halt (prospective)

**Status: STOP at Part 1, before semantic-format schema/content freeze.** This
review does not change R5.2.2, the preserved R5.3 diagnostics, any frozen
requirement, either implementation, or either post-B16 checkpoint. B17 is
UNEXPOSED and UNFROZEN. This is an expressiveness finding, not a claim that a
historical executable carrier is wrong.

## Evidence and boundary

`benchmark/semantic/format.py` currently validates the
`LYKOI-BENCHMARK-SEMANTIC-PROTOTYPE/1` vocabulary. A plan has ordered `seed`,
`invoke`, `snapshot`, and `observe` steps. Expressions are JSON literals,
references into prior results/snapshots, lists, or rows sorted by named fields;
observations are equality or pairwise distinctness. The CLI command list and
storage filename are adapter choices. The selected B01, B11, B14 and B16
witnesses demonstrate some of these operations, but are not a clause inventory.

| Required dimension | Prototype assessment |
| --- | --- |
| Stable scenario/observation ID and originating request | Present; `origin.note` is prose, not a verified clause/source-span link. |
| Achieved-history applicability | `when.requires/forbids` present; variant overlap checked. |
| Initial state, entities/relationships and actions | Literal storage seed and ordered CLI calls with bound values; ordinary data relationships can be expressed via IDs and references. |
| Observation phase, result, error, persisted effect and no-write | Ordered result/error calls and byte snapshots/equality present; no-write needs explicitly paired snapshots. |
| Ordering, identity, dependency graph and atomicity | Lists, explicit sort, distinct IDs, dependency operations and before/after byte equality can witness concrete examples; these do not establish a universal graph invariant. |
| Time relationships | **Missing:** no typed UTC instant, clock read, offset, or time comparison. Only literal timestamps or values returned by the application can be passed to an action. |
| `adds`, `replaces`, `depends_on` | `lineage` permits `adds`, `retains`, `replaces` with unchecked string `prior`; there is **no** `depends_on`, checked target, or compositional active semantic state. `retains` in the example is not an explicit replacement edge. |
| Provenance and active carrier references | Free-form note and optional single carrier string; the selected test checks existence, not clause-to-carrier coverage, applicability of each referenced carrier, source pin, or retention of unaffected clauses in the same method. |

**Concrete missing semantic concept:** B12's frozen
`benchmark/requirements/B12.md:3-6` says urgent tasks are due *strictly before
current UTC time*. Its historical carrier
`benchmark/harness/cases/B12.py:55-67` constructs a due date from the UTC clock
plus two days and observes both `list-urgent` and `list-overdue`, with a
before/after storage comparison. The R5 replacement's corresponding active
method is identified in `B17-AFFECTED-METHOD-AUDIT.md` as
`regression_B16_R5.cases.<locals>.UrgentBoundary.test_strict_current_time_and_empty_query_never_write_with_owner`.
No expression in the current schema can supply an instant relative to the
execution clock. A fixed far-future/past literal witnesses some inclusion or
exclusion examples but does not encode the frozen time relationship or the
carrier's original precondition. Substituting opaque Python fixture logic or
declaring fixed dates equivalent would violate the clause-first bridge.

The independent composer gate also cannot pass with this schema: B11 changes
completed-unarchived deletion while retaining pending/archived deletion and
unrelated lifecycle behavior; `lineage.prior` strings are not validated against
an active semantic target. B17 draft's `prior` values such as
`B16.system_user` are **observation IDs**, not separately inventoried active
requirement IDs, and the draft requires both B16 and B17 in every variant.
For hypothetical achieved `{B01,B04,B17}` it consequently selects no B17
scenario. Whether B17 depends on a persistent user registry from B16 is an
unresolved semantic dependency for that history, not permission to inject B16,
invent an early-history user model, or branch on a track name. See the frozen
`benchmark/requirements/B17.md:3-10` and the prior affected-method audit.

## Next adjudication before resuming the bridge

Define and independently review a *general* typed UTC-now/relative-instant
expression and its observation-time semantics (including how to avoid flaky
boundary cases); specify checked requirement-level `adds`, `replaces` and
`depends_on` edges and exact achieved-history applicability, distinct from
scenario observations and executable method IDs. Decide the B17/B16 dependency
for the early history from frozen requirements. Then version/pin the format,
enumerate frozen B01–B16 clauses, validate their active R5.2.2 carriers and
affected-method retention, derive B17 cases, and perform fresh independent
checkpoint validation **before** any protocol or B17-ready freeze. If another
frozen clause exposes an expressiveness gap, stop there and record it. No
bounded-bridge completeness, derived-case, full-suite revalidation, or B17-ready
claim is made by this review.
