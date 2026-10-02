# B16 prospective acceptance-composition audit (proposal, NOT a freeze)

This audit compares `RESUME-R4-B16-HALT.md`, the frozen B01–B15 cases,
`B11_R4_replacements.py`, and the two B15 checkpoint achieved sets. It does
not change the B01–B15 oracle, authorize skipping a method, or expose B16 to
either track. The proposed disposition below becomes applicable only **after
B16 is achieved** on a track. Before that, its B15 accumulated oracle must
remain exactly as pinned in R4.

## Exact proposed method-level dispositions

Every row below requires a separately named, explicitly pinned B16 replacement
method reproducing the unaffected assertions. `regression_Bxx` denotes the
module loaded by the R4 oracle from frozen `cases/Bxx.py`. C = Conventional;
L = Lykoi. A method is selected only if its origin is achieved, it is not
already superseded by an earlier applicable amendment, **and B16 is achieved**.
An unsuccessful or blocked B16 cannot supersede anything.

| Frozen method ID | Track at B15 | Obsolete assertion / required retained coverage |
| --- | --- | --- |
| `regression.Regression.test_baseline_migration_corruption` | C, L | Successful ownerless fixture creation; retain version-1/2 migration, duplicate/blank-ID corruption and no-write behavior. |
| `regression.Regression.test_baseline_overdue_fixture` | C, L | Successful ownerless schema probe; retain due-date selection and schema/field checks. |
| `regression.Regression.test_b02_tags_and_failure` | C | Successful ownerless plain/tagged creation; retain tag ordering/deduplication, priority selection, invalid-tag rejection, persistence and completion. |
| `regression_B03.cases.<locals>.TagListing.test_exact_case_sensitive_tag_with_completed_tasks` | C | Successful ownerless fixture creation; retain exact, case-sensitive tag selection, completed-task inclusion and no-write. |
| `regression_B03.cases.<locals>.TagListing.test_blank_queries_leave_storage_unchanged` | C | Successful ownerless fixture creation; retain all blank-tag errors and no-write both before and after fixture creation. |
| `regression_B05.cases.<locals>.StatusListing.test_both_statuses_and_no_write` | C | Successful ownerless fixture creation; retain empty/ordered pending/completed filtering and no-write. |
| `regression_B06.cases.<locals>.Categories.test_create_filter_and_failed_create` | C | Successful ownerless fixture creation, including invalid-category probe; retain trim/default/category filter/case-sensitivity, completion, deletion and no-write on invalid category. |
| `regression_B08.cases.<locals>.Archival.test_archive_pending_completed_and_visibility` | C | Successful ownerless fixture creation; retain pending/completed archival, list visibility, optional achieved filter checks, transitions and no-write. |
| `regression_B09.cases.<locals>.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order` | C | Successful ownerless fixture creation; retain inclusive bounds, pending/visible exclusion, ordering and no-write. |
| `regression_B09.cases.<locals>.DueWindow.test_invalid_ranges_and_timestamps_do_not_write` | C | Successful ownerless fixture creation; retain invalid ranges/timestamps and no-write before and after creation. |
| `regression_B10.cases.<locals>.Owner.test_trim_reject_and_exact_owner_listing` | C | Successful creation with unregistered Alex/alex and without owner, plus default `owner == ""`; register Alex and alex first, supply a registered owner for the former unowned task, retain trim, blank rejection, case-sensitive exact filters, read-only queries, completion and deletion; empty-owner filter remains valid and returns no matches. |
| `regression_B10.cases.<locals>.Owner.test_migration_defaults_unowned` | C | Explicit expectation that migrated unowned task has `owner == ""` and matches empty-owner filter; retain explicit migration/no-write/schema checks, assert migrated owner `system` and exact `system` filter, and empty filter returns no matches. |
| `regression_B11.cases.<locals>.DeletionRule.test_lifecycle_priority_and_completed_delete_rule` | C | Successful ownerless creation; retain invalid title/due-date errors with a valid owner, lifecycle, priority, overdue, complete/archive/delete rule, IDs, lists and no-write. |
| `regression_B11.cases.<locals>.DeletionRule.test_pending_deletion_with_and_without_archive` | C | Successful ownerless creation; retain pending deletion with/without archive and empty lists. |
| `regression_B12.cases.<locals>.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue` | C | Successful ownerless creation; retain priority/time exclusions, ordering, earlier overdue selection and no-write. |
| `regression_B12.cases.<locals>.Urgent.test_strict_current_time_and_empty_query_never_write` | C | Successful ownerless creation; retain empty query, near-future strictness and no-write. |
| `regression_B13.cases.<locals>.ArchivedMutations.test_archived_pending_and_completed_mutations_are_rejected` | C | Successful ownerless creation; retain archival terminal errors/no-write, archived list and permitted deletion. |
| `regression_B13.cases.<locals>.ArchivedMutations.test_unarchived_operations_remain_valid` | C | Successful ownerless creation; retain note trimming, completion and unarchived completed deletion rejection/no-write. |
| `regression_B14.cases.<locals>.Dependencies.test_order_cycles_and_no_write_failures` | C | Successful ownerless creation; retain ordered IDs, duplicate/self/cycle/missing failures, dependency deletion integrity, list round-trip and no-write. |
| `regression_B14.cases.<locals>.Dependencies.test_archived_reference_and_explicit_migration` | C | Successful ownerless creation; retain archived dependency references, deletion rule, explicit old-schema migration and no-write. |
| `regression_B15.cases.<locals>.CompletionDependencies.test_pending_dependencies_reject_without_writes_then_succeed` | C | Successful ownerless creation; retain completion gate, archived completed prerequisites, dependency order, repeat-complete rejection and no-write. |
| `regression_B15.cases.<locals>.CompletionDependencies.test_archived_parent_still_obeys_terminal_transition` | C | Successful ownerless creation; retain archived parent terminal transition/no-write. |
| `regression_B11_R4.cases.<locals>.Source.test_verbatim_default_and_mutations_after_b11` | C | Successful ownerless creation; retain verbatim/empty/omitted source, list/list-high, completion, no-write completed-delete rejection, archival and deletion preservation. |
| `regression_B11_R4.cases.<locals>.Notes.test_append_order_trim_and_failed_append_after_b11` | C | Successful ownerless creation; retain empty/ordered/trimmed notes, failed append/no-write, separate task, completion, B11 deletion rule and preservation. |
| `regression.Regression.test_baseline_lifecycle_filters_failures` | L only at B15 | Successful ownerless creation; B11 has already superseded this on C. If B16 succeeds independently on L, retain lifecycle/validation/IDs/filter/order/no-write assertions and L's still-applicable pre-B11 completed deletion behavior. |
| `regression.Regression.test_b01_priority_and_regression` | L only at B15 | Successful ownerless creation; B11 has already superseded this on C. If B16 succeeds independently on L, retain B01 priority/filter/completion/deletion behavior. |
| `regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations` | L only at B15 | Successful ownerless creation; R4 B11 has already superseded this on C. If B16 succeeds independently on L, retain verbatim/empty/omitted source, list/list-high, completion and deletion under L's applicable B11 state. |

Thus C has **24** active methods needing B16 replacement (23 successful
ownerless-creation methods plus B10's explicit unowned-migration assertion).
L has **5** active methods needing B16 replacement at its B15 achieved set.
The conditional union comprises **27** exact historical method IDs. L can
only activate the C-only rows if it subsequently achieves their origins; the
R4/B11 replacements and original B04 method must never be active together.

## Assertions that must remain active without method replacement

The original frozen methods already superseded by achieved B11 on C are
`regression.Regression.test_baseline_lifecycle_filters_failures`,
`regression.Regression.test_b01_priority_and_regression`,
`regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations`,
and `regression_B07.cases.<locals>.Notes.test_append_order_trim_and_failed_append`.
Their applicable B11/R4 coverage must survive B16 via the B11 method and
the two R4 replacement-method rows above. On L, original B07 is inapplicable
because B07 was not achieved.

Retain without skipping all active migration-only cases whose expectations
are computed from the composed `migration_defaults` (baseline historical
priorities, B02, B04, B06, B07, B08), B09/B10-independent validations,
and all remaining applicable assertions. Where B10 is achieved, B16
composition must change the `owner` migration default from `""` to `"system"`;
where B10 is not achieved, B16 needs its own explicit owner field contribution
and migration default, without rewriting any old checkpoint meaning.
Do not change the frozen B10 fragment or old checkpoints. Explicitly check
missing/unknown owner failures and unresolved nonempty-owner migration in
the separately frozen B16 acceptance case.

## Required implementation and validation boundary

Pin the hash of each new replacement case, exact map, and new R5 runner;
reject absent IDs/collisions and require a corresponding replacement method
for each selected skip. Preserve the R4 runner and B01–B15 bytes. Freeze all
these additions before predictions or implementation. Independently restore
both B15 snapshots, verify full checkpoint inventories and hashes, and run
the B15 accumulated external/internal and repository harness suites before
the B16 prospective freeze. A B15 implementation cannot be expected to pass
B16-required-owner tests before B16 is implemented; the new oracle must gate
these dispositions on achieved B16 and preserve the B15 result counts.
