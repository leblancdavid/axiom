# Phase 5C R4 — halt at the prospective B16 boundary

**Status: HALTED BEFORE B16 FREEZE.** Both tracks have independently restored,
classified checkpoints through B15, recorded in `RESUME-R4-B15-PROGRESS.md`.
B16–B20 have no prospective freeze, prediction, implementation, classification,
checkpoint or final Phase 5C score. The B11 R4 repair and B01–B15 evidence are
untouched.

## Uncovered historical-case conflict

The frozen `benchmark/requirements/B16.md` lines 6–8 make an existing
`--owner USER_ID` **mandatory on task creation**, with omitted or unknown owners
failing `invalid_owner`. However, already achieved and applicable frozen
external methods create tasks without `--owner` and require success. Examples:

* `regression.Regression.test_baseline_lifecycle_filters_failures` (and other
  baseline methods) creates tasks without `--owner`. The B11 fragment
  supersedes this one baseline method on Conventional, but not all baseline
  methods with successful ownerless creation.
* `regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations`
  uses ownerless creation; it remains active on Lykoi, where B11 was blocked.
  Its R4 B11 replacement
  `regression_B11_R4.cases.<locals>.Source.test_verbatim_default_and_mutations_after_b11`
  likewise creates ownerless tasks and remains active on Conventional.
* `regression_B11.cases.<locals>.DeletionRule.test_lifecycle_priority_and_completed_delete_rule`
  and `test_pending_deletion_with_and_without_archive` require ownerless
  creation; B11 is achieved on Conventional.
* `regression_B10.cases.<locals>.Owner.test_trim_reject_and_exact_owner_listing`
  requires ownerless creation to default to the empty owner. B10 is achieved
  on Conventional; B16 replaces this behavior with required, existing users.
* `regression_B14.cases.<locals>.Dependencies.test_order_cycles_and_no_write_failures`
  starts by creating ownerless tasks; B14 is achieved on Conventional.

The R4 runner skips only exact methods prospectively named by achieved
fragments or the narrow B11 R4 overlay. There is no frozen B16 capability
fragment or replacement acceptance case yet. Simply running a compliant B16
implementation against the current accumulated oracle must fail these old
assertions; silently weakening or skipping them, special-casing ownerless
creation, or scoring that failure as an implementation regression would repeat
the B11 acceptance-composition defect. The B16 migration/user rules also need
replacement coverage for all impacted prior behavior. Before B16 exposure,
conduct a symmetric prospective protocol review, enumerate **all** affected
historical methods and their retained assertions, version explicit
supersessions and replacement cases, freeze their hashes, and rerun preflights
and accumulated tests on both B15 states. Halt on any further conflict.

This halt is a methodology boundary, not a B16 result on either track. Do not
begin B17–B20 or Phase 6 from these B15 states until the B16 composition is
explicitly repaired and authorized.
