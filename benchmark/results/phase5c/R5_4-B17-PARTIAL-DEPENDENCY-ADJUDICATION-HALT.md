# R5.4 B17 dependency analysis — partial-dependency classification halt

**Prospective analysis, NOT a classification or freeze.** R5.2.2 remains the
authoritative corrected historical executable boundary. B17 is UNEXPOSED and
UNFROZEN; no implementation or historical result is changed. This record
continues `R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md` under the subsequent
authorization for typed time and checked semantic relationships.

## Frozen requirement evidence, independent of the draft and implementations

`benchmark/requirements/B16.md:3-11` introduces persistent users identified
by case-sensitive IDs, the built-in `system` user, `create-user`/`list-users`,
required valid task owners and migration/owner validation. In contrast,
`benchmark/requirements/B17.md:3-10` defines roles **on users**, `--actor` as
an **existing user**, permissions in terms of the actor's role and the task's
owner, and rejection before mutation. B17 does not itself specify creation,
storage, or migration of a user registry or a replacement owner model.

| B17 dimension | Dependency assessment | Frozen-text reasoning |
| --- | --- | --- |
| Missing `--actor` on mutating task commands | INDEPENDENT_OF_B16 (as an observable rejection) | The flag's absence and `actor_required` error can be observed before any user lookup; no-write on that rejection needs only task state (`B17.md:5,8-10`). This does **not** implement the rest of actor authorization. |
| Unknown `--actor` | DEPENDS_ON_B16 | "An existing user" and `unknown_actor` require an authoritative user collection, introduced by `B16.md:3-6` (`B17.md:5,7-8`). |
| Role-bearing user results and default USER/system ADMIN | DEPENDS_ON_B16 | User objects, `create-user`, `list-users` and built-in `system` are B16 semantics that B17 extends (`B16.md:3-6`, `B17.md:3-5`). |
| USER-own/ADMIN-any creation and mutation | DEPENDS_ON_B16 | Requires both role-bearing existing users and valid task ownership; B16 introduces both (`B16.md:3-11`, `B17.md:5-7`). |
| Rejection/no-write | PARTIALLY_DEPENDENT | Missing-actor/no-write is independently observable. Unknown-actor and permission-denied/no-write require user/owner relationships (`B17.md:7-10`). |
| Migration | PARTIALLY_DEPENDENT | `migrate` is a mutating task command under B17's "all" clause; omitting actor can be rejected without B16. Authorized migration and owner/user validation require B16's persistent user/ownership model (`B16.md:8-11`, `B17.md:5-10`). |
| Unrestricted reading/listing | INDEPENDENT_OF_B16 for existing task reads | The explicit read exception does not require user lookup (`B17.md:9`). User listing itself presupposes B16. |

**Answer to the two dependency questions:** Yes, there are independently
observable B17 requirements on `{B01,B04}` (notably missing-actor rejection
and unrestricted task reads). But satisfying B17 **as a whole** requires B16's
persistent user/ownership semantics: the B17 text provides no independent
definition of its existing users and owners. B17 is therefore
**PARTIALLY_DEPENDENT**, not uniformly independent or uniformly dependent.
These are semantic assessments, not achieved-state predictions or a capability
classification. No hypothetical `{B01,B04,B17}` target is authorized here.

## Protocol question requiring adjudication

`benchmark/README.md:64-68` and
`benchmark/results/phase5b/FROZEN.md:115-120` provide a request-level
`BLOCKED_BY_GAP` outcome when a later request needs a named missing
prerequisite. Historical B12 was classified `BLOCKED_BY_GAP` on B08 in
`RESUME-R4-B12-PROGRESS.md:7-14` even though some query exclusions can be
described without archival; its B12 acceptance was marked **inapplicable**.
Those rules and that precedent do not specify whether/how to classify or
independently observe the *non-dependent B17 dimensions* while B17 as a whole
is blocked, nor how to report such observations without treating them as a
partial success or modifying the frozen request. An automatic
`BLOCKED_BY_GAP -> B16` with no treatment of those observations, or an
automatic partial B17 activation, would each invent a rule at this boundary.

**STOP before Part 7 B17 draft changes or B17 composition.** Adjudicate the
request-level versus clause-level observation/classification rule prospectively
and independently before updating the draft or deriving cases. The old draft's
guards and unchecked `prior` strings are not dependency evidence and remain
unfrozen. Retain R5.3 diagnostics without restarting exhaustive reconstruction.

## Independently prepared format mechanics (not a schema freeze)

`benchmark/semantic/format.py` prototype v2 adds a declared `utc_now` binding,
typed UTC instants/projections, integral-second offsets and typed strict
`before` observations. A clock is sampled once per named step by an injected
fixture clock; parsing a semantic file does not read time. The disposable
subprocess probe refuses clock-dependent CLI invocations because it cannot
inject the same instant into the application's clock. The selected v1 B17
draft is not promoted. `benchmark/semantic/relationships.py` separately
validates exact requirement IDs, dependency targets/cycles, prior semantic
roots and state-relative active replacements on synthetic fixtures. This is
not yet integrated with a bounded B01–B16 clause inventory, verified carriers
or B17 records. These mechanics alone do not resolve the old adequacy halt or
authorize a format/protocol freeze.
