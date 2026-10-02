# R5.4 B17 partial-dependency adjudication — prospective Phase 5C rule

**Decision, not an executed B17 result or acceptance freeze.** This resolves
the question raised in
`R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION-HALT.md`. R5.2.2 remains the
authoritative corrected post-B16 executable boundary. B17 is unexposed and
unachieved on both tracks; neither checkpoint, application, frozen requirement,
nor historical classification changes here.

## Unit of measurement

Phase 5C continues to classify **complete benchmark requests** through B20.
Its existing request outcomes (`SUCCESS`, `AXIOM_CAPABILITY_GAP`,
`BLOCKED_BY_GAP`, and the other protocol outcomes) are not clause outcomes.
Where a track lacks B16 and completing B17 as a whole requires B16's missing
persistent users/ownership, its B17 request outcome is
`BLOCKED_BY_GAP -> B16`. This is a conditional classification rule, **not** a
new recorded B17 attempt or a finding that every B17 clause depends on B16.
Satisfying missing-actor rejection alone cannot make the request `SUCCESS`.

The Conventional track has the authoritative B01–B16 continuation, including
B16. Evaluate the *entire* frozen B17 request there against that state under
the normal protocol. This dependency rule neither weakens its acceptance nor
preclassifies its outcome.

## Clause dependencies and request completion

The frozen-text assessment in the halt record is retained. A prospective
semantic inventory should carry **stable clause IDs** and checked prerequisite
semantic roots, rather than flattening the whole request to one opaque B16
edge. The following is a dependency sketch, **not** a completed clause
inventory, active-root registry, or acceptance case list:

| B17 clause dimension | Prerequisite | Reason |
| --- | --- | --- |
| Missing actor rejection (`actor_required`) before a task mutation, with no write | None from B16 | Absence of `--actor` can be rejected without looking up users or owners. |
| Unknown actor (`unknown_actor`) | B16 persistent user registry | "Existing user" needs authoritative membership. |
| Roles on users, including `system` ADMIN and role-bearing user results | B16 persistent users and built-in `system` | B17 extends the B16 user objects and commands. |
| USER-own/ADMIN-any create and mutations, including authorized migration and permission failures | B16 users and task ownership | Role and owner relationships are needed to decide permission. |
| Existing task reading/listing without actor | None from B16 for the read exemption itself | User listing still presupposes the B16 user registry. |

Before format freeze, assign independently reviewed IDs to each required B17
clause and exact IDs to its B16 prerequisite roots. Check unknown targets and
derive the request edge `B17 completion -> B16` from the **required** clauses
that need those roots. Completion requires *all* required B17 clauses, not only
the independent ones. This derived edge does not add B16 semantics to a track
that lacks them. Do not use track identity to derive applicability. The
existing checked `depends_on` and state-relative `replaces` prototype remains
prospective; unknown dependency or replacement targets fail closed.

The prospective representation has two distinct levels (illustrative names;
the B16 roots and full B17 clause IDs still require inventory and review):

```text
request B17:
  required_clauses: [B17.MISSING_ACTOR_REJECTION, B17.UNKNOWN_ACTOR, ...]
clause B17.MISSING_ACTOR_REJECTION:
  depends_on: []
clause B17.UNKNOWN_ACTOR:
  depends_on: [<checked B16 persistent-user semantic root>]
```

The `required_clauses` list determines request completion; clause prerequisites
explain *why* that completion depends on B16. An observation ID, a carrier
method ID or an unchecked prose label is not a prerequisite semantic root.

## Separate diagnostic observations

An independently observable clause of a blocked request **may** be probed in
disposable/restored state without B16 activation. Record its result in a
separate diagnostic register, using only `OBSERVED_SUPPORTED`,
`OBSERVED_UNSUPPORTED`, or `NOT_OBSERVED_DEPENDENCY` (for a clause that cannot
be exercised without a missing prerequisite). These are *observations about
expressibility of a clause in the frozen track*, not benchmark outcomes. An
untested clause must not be called supported or unsupported. A diagnostic
record must include:

- frozen clause semantic ID, exact prerequisite IDs, track and pinned starting
  checkpoint/achieved-request set;
- diagnostic setup and independent expected observation; actual observation,
  diagnostic result and evidence/provenance;
- restored/disposable-state evidence and explicit confirmation that the
  authoritative continuation and request-level classification were unchanged.

Use the [separate diagnostic record template](../../semantic/diagnostic-template.md)
for any eventual probe; it is not an acceptance carrier or achieved checkpoint.

For example, `B17.MISSING_ACTOR_REJECTION = OBSERVED_SUPPORTED` beside
`B17: BLOCKED_BY_GAP -> B16` would say only that the frozen track already
rejects a missing actor under the recorded setup. It does **not** establish
B17 achievement. No such observed result is asserted by this decision.

Diagnostic clause IDs never enter the achieved-request set. No
`{B01,B04,B17.partial}` or `{B01,B04,B17.MISSING_ACTOR}` continuation exists.
Diagnostics do not activate B17 `adds` or `replaces`, dependent semantics,
acceptance composition, B18 dependencies, or a normal achieved-B17 checkpoint.
Only complete request achievement can activate B17 under Phase 5C. Preserve
diagnostics for post-B20 analysis of truly missing, dependency-blocked, and
independently supported semantics inside blocked requests. A future
semantic-first benchmark could deliberately choose clause-level measurements
from its outset; this decision does not prescribe that future unit.

## Remaining pre-exposure gates

1. Encode checked clause-level prerequisite metadata and request-completion
   aggregation, preserving request-level classification; represent diagnostic
   observations separately from classifications and achieved histories.
2. Retain the typed UTC-clock/strict-before and checked stable-ID dependency
   and state-relative replacement prototypes. Define and validate an explicit
   application clock adapter binding the executable to the **same** controlled
   instant as the semantic plan. Fail closed when the adapter is absent or
   mismatched; never substitute an independent wall-clock read.
3. Restart semantic-format adequacy across frozen B01–B16 clauses. If it
   succeeds, complete the bounded clause-to-carrier bridge against unchanged
   R5.2.2 and independently check affected-carrier retention.
4. Reconcile the B17 draft against the active semantic state, derive cases,
   independently restore/revalidate both B16 checkpoints, and establish a
   separately reviewed B17-ready boundary **before** exposure.

These gates have not passed. The R5.3 unfinished evidence stays preserved;
this adjudication does not authorize B18–B20 or `PHASE_5C_COMPLETE`.
