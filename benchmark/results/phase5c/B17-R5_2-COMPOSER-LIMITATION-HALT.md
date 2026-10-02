# Phase 5C — B17 composer limitation, pre-amendment halt

**Status: STOP at Step 6.** The affected-method audit is
`B17-AFFECTED-METHOD-AUDIT.md`. Neither the B17 oracle nor its fragment,
request case, target, prediction, implementation, result or checkpoint has
been produced. Both post-B16 continuation states remain authoritative;
B18–B20 are unprocessed. No earlier frozen evidence has been changed.

## Independently identifiable collision

The frozen R5.2 state-relative composer
`benchmark/harness/capability_profile_r5_2.py:67–79` permits a
`supersedes_cases` contribution only if the test ID is **not already** in
`prior["superseded_cases"]`. Its predecessor, `capability_profile.py:69–82`,
has the same restriction. There is no state-relative operation for "supersede
this still-active method if present; otherwise preserve its existing
supersession." This is an intentional conflict guard, not a permission to
delete a prior disposition.

For example, B17 must replace
`regression.Regression.test_baseline_lifecycle_filters_failures` in the
post-B16 Lykoi history `{B01,B04}` to retain its lifecycle assertions while
adding the required task actor. That history has no earlier supersession of
the method. In the Conventional post-B16 history B01–B16, B11's **frozen**
fragment already supersedes the same ID; the still-active lifecycle test is
instead the B16/R5 `DeletionLifecycle` replacement. A **single** B17 fragment
listing the baseline method works for the former profile and is rejected for
the latter as `invalid or conflicting case supersession: B17:...`. Omitting
the ID leaves the Lykoi historical success expectation active if that track
achieves B17. The same obstruction applies to
`regression.Regression.test_b01_priority_and_regression` (already
superseded by B11 only on the Conventional history). B11/R4 and B16/R5
also select different active methods from the same frozen semantic request;
neither an unconditional skip nor a track-specific fragment is authorized.

The R5.2 `ensure_fields` operation supports state-relative **task-field**
presence/defaults, not state-relative **acceptance supersession** of a method
whose prior disposition differs. Its `supersedes_cases` validation cannot
express this B17 mapping. Quietly changing the composer, treating a conflicting
entry as a no-op, or making the replacement runner override the composed
supersession would extend its protocol under cover of this authorization.
The user specifically requires stopping and documenting this limitation
separately, so no such change has been made.

The B17 requirement's persisted user/role authorization may also establish a
semantic dependency on B16's user registry for the Lykoi history. That
dependency must be evaluated under the existing prerequisite/classification
rules before B17 classification; numerical ordering alone does not decide it.
It does not remove the general composition limitation: a proposed B17
amendment must describe conditional activation for either achieved-state
profile without testing track names or assuming a future result.

## Evidence and next boundary

The audit enumerates 33 currently applicable Conventional methods and seven
currently applicable Lykoi methods, with the existing 28 Conventional
supersession skips and two Lykoi B02 prerequisite skips kept separate. The
repository harness discovery completed **29/29** (`python -m unittest
discover -s benchmark/harness -p 'test_*.py'`); the underlying baseline
fixture suites also passed. This confirms existing behavior, not a B17
amendment, independent B16 checkpoint restoration, or post-amendment
revalidation. The blocker requires a separately authorized, prospectively
specified state-relative **acceptance-composition** extension with fixtures
and freeze before any B17 artifact or exposure. Until then B17 is unprocessed;
do not claim Phase 5C complete or start Phase 6.
