# B17 pre-amendment affected-method audit and proposed mapping

**Status: audit only.** No B17 acceptance, capability fragment, prediction or
implementation is frozen or activated by this document. Inputs are the two
authoritative B16 checkpoints and the frozen B01–B16 cases, B11/R4 repairs,
B16/R5 replacements and R5.2 suite selection. This inventory concerns the
**currently applicable** methods, not every method loaded as an explicit skip.

Interpretation fixed for the proposal: `migrate` writes task records and is a
mutating task command under `requirements/B17.md` line 5. It therefore needs an
existing `--actor`, including when it returns `migrated: 0`; read-only `list`,
`list-*`, and `list-users` do not. `create-user` changes users, not tasks, and
does not acquire a task actor. Failed task mutation calls retain their prior
error/no-write assertions when supplied an authorized actor. The new
actor-required/no-write behavior for omission is additional B17 coverage, not
a reason to discard earlier validation or transition checks.

## Notation and replacement rule

IDs in the tables are complete unittest IDs, using these exact prefixes:

- `R.` = `regression.Regression.`
- `Cnn.` = `regression_Bnn.cases.<locals>.` (the class follows the dot)
- `R4.` = `regression_B11_R4.cases.<locals>.`
- `R5.` = `regression_B16_R5.cases.<locals>.`

For each affected ID `X`, propose precisely one B17 replacement `X ->
B17-replacement(X)` (a separately pinned, one-to-one method ID), only when
`B17` is achieved **and** `X` is the active method in the prior achieved-state
composition. Replacement reruns the original assertions, adapting only task
mutation calls with `--actor system` (the B16 ADMIN, or an authorized actor
provided by the B17 user semantics) and updating only exact user-object
equality to retain the original `id` and require the corresponding `role`.
Do not rewrite user-object results in non-user assertions or change task result
shapes. For each `migrate`, retain migration count, schema, storage and atomicity
checks. The implementation of this mapping must pin every original source hash,
assert one loaded original and one replacement per entry, and fail closed on
any unmatched original; this document is not itself a skip list.

For exact proposed IDs in the tables, expand `X` using the prefixes above,
then define `B17-replacement(X)` as the literal unittest ID
`regression_B17_R6.cases.<locals>.Replacement.test_` followed by the **full**
expanded original ID with each `.` replaced by `__` and the substring
`<locals>` replaced by `locals`. Replacement IDs thus differ for original,
R4, R5 and B16 methods even where their short method names overlap. These
are proposed IDs only; no `regression_B17_R6` module exists while halted.

**A** = actorless task mutation success/error expectation, including migration.
**B** = ID-only user-result equality. **C** = assertions to preserve (in
addition to the original CLI return-code/stderr and read-only/no-write checks).

### Conventional: achieved B01–B16; 33 applicable, 28 prior explicit skips

All 33 currently applicable methods have an A expectation once migration is
included. Only the four entries explicitly marked B also have a B expectation.
The mapping below is exhaustive; `R5` denotes the *already applicable* R5
replacement, not the original method it replaced.

| Active original method -> B17 replacement | Dimension | Preserved assertions (C) |
| --- | --- | --- |
| `R.test_b01_historical_priorities` -> `B17-replacement(R.test_b01_historical_priorities)` | A: migrate | old priorities, schema-2/3 migration, order, defaults |
| `R.test_b02_explicit_migration` -> `B17-replacement(R.test_b02_explicit_migration)` | A: migrate | tags default, historical payloads and migration counts |
| `C04.SourceLabel.test_explicit_migration_of_prior_storage` -> `B17-replacement(C04.SourceLabel.test_explicit_migration_of_prior_storage)` | A: migrate | source default, schema, idempotent second migration, no-write |
| `C06.Categories.test_migration_defaults_category` -> `B17-replacement(C06.Categories.test_migration_defaults_category)` | A: migrate | category default, schema and no-write |
| `C07.Notes.test_explicit_migration_initializes_notes` -> `B17-replacement(C07.Notes.test_explicit_migration_initializes_notes)` | A: migrate, append-note | notes initialization, trimmed append, migrated identity/schema |
| `C08.Archival.test_explicit_migration_defaults_unarchived` -> `B17-replacement(C08.Archival.test_explicit_migration_defaults_unarchived)` | A: migrate | false archival default, empty archive listing, schema |
| `R5.BaselineMigration.test_baseline_migration_corruption_with_owner` -> `B17-replacement(R5.BaselineMigration.test_baseline_migration_corruption_with_owner)` | A: migrate, create | legacy v1/v2 fields/defaults, invalid duplicate/id/corrupt state |
| `R5.BaselineOverdue.test_baseline_overdue_fixture_with_owner` -> `B17-replacement(R5.BaselineOverdue.test_baseline_overdue_fixture_with_owner)` | A: create | current schema, overdue filtering, task fields |
| `R5.Tags.test_b02_tags_and_failure_with_owner` -> `B17-replacement(R5.Tags.test_b02_tags_and_failure_with_owner)` | A: create, complete | tag trim/dedup/order, priority, ID set, invalid tag/no-write |
| `R5.TagExact.test_exact_case_sensitive_tag_with_completed_tasks_with_owner` -> `B17-replacement(R5.TagExact.test_exact_case_sensitive_tag_with_completed_tasks_with_owner)` | A: create, complete | exact tag case, completed inclusion, read no-write |
| `R5.TagBlank.test_blank_queries_leave_storage_unchanged_with_owner` -> `B17-replacement(R5.TagBlank.test_blank_queries_leave_storage_unchanged_with_owner)` | A: create | invalid blank tag query and storage immutability |
| `R5.Status.test_both_statuses_and_no_write_with_owner` -> `B17-replacement(R5.Status.test_both_statuses_and_no_write_with_owner)` | A: create, complete | pending/completed filtering, IDs, no-write reads |
| `R5.Categories.test_create_filter_and_failed_create_with_owner` -> `B17-replacement(R5.Categories.test_create_filter_and_failed_create_with_owner)` | A: create, complete, delete | category trim/case/default, failure/no-write, list/delete result |
| `R5.Archival.test_archive_pending_completed_and_visibility_with_owner` -> `B17-replacement(R5.Archival.test_archive_pending_completed_and_visibility_with_owner)` | A: create, complete, archive | archive transitions, result equality, visibility and no-write |
| `R5.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order_with_owner` -> `B17-replacement(R5.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order_with_owner)` | A: create, complete, archive | inclusive bounds, filtering, order and no-write |
| `R5.DueInvalid.test_invalid_ranges_and_timestamps_do_not_write_with_owner` -> `B17-replacement(R5.DueInvalid.test_invalid_ranges_and_timestamps_do_not_write_with_owner)` | A: create | invalid timestamps/window and storage immutability |
| `R5.Owner.test_registered_trim_reject_and_exact_owner_listing` -> `B17-replacement(R5.Owner.test_registered_trim_reject_and_exact_owner_listing)` | A: create, complete, delete; B: two create-user returns | registered owner validation/trim/case/default system, owner list, IDs, no-write; IDs Alex/alex retained and roles USER asserted |
| `R5.OwnerMigration.test_migration_defaults_system` -> `B17-replacement(R5.OwnerMigration.test_migration_defaults_system)` | A: migrate | migrated owner system, list-owner, schema and no-write |
| `R5.DeletionLifecycle.test_lifecycle_priority_and_completed_delete_rule_with_owner` -> `B17-replacement(R5.DeletionLifecycle.test_lifecycle_priority_and_completed_delete_rule_with_owner)` | A: create, complete, archive, delete | priorities, task IDs, filtering, failure precedence with actor, archive-before-delete, no-write |
| `R5.DeletionPending.test_pending_deletion_with_and_without_archive_with_owner` -> `B17-replacement(R5.DeletionPending.test_pending_deletion_with_and_without_archive_with_owner)` | A: create, delete, archive | pending deletion and archived deletion, empty lists |
| `R5.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue_with_owner` -> `B17-replacement(R5.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue_with_owner)` | A: create, complete, archive | urgent priority/due exclusions, ordering, overdue IDs, no-write |
| `R5.UrgentBoundary.test_strict_current_time_and_empty_query_never_write_with_owner` -> `B17-replacement(R5.UrgentBoundary.test_strict_current_time_and_empty_query_never_write_with_owner)` | A: create | future boundary, empty query and no-write |
| `R5.Archived.test_archived_pending_and_completed_mutations_are_rejected_with_owner` -> `B17-replacement(R5.Archived.test_archived_pending_and_completed_mutations_are_rejected_with_owner)` | A: create, complete, archive, append-note, delete | terminal transition, errors/no-write, archived ordering, delete results |
| `R5.Active.test_unarchived_operations_remain_valid_with_owner` -> `B17-replacement(R5.Active.test_unarchived_operations_remain_valid_with_owner)` | A: create, append-note, complete, delete | trimmed notes, completion, completed-delete rejection/no-write |
| `R5.DependencyCycles.test_order_cycles_and_no_write_failures_with_owner` -> `B17-replacement(R5.DependencyCycles.test_order_cycles_and_no_write_failures_with_owner)` | A: create, add-dependency, delete | dependency order, cycle/errors/no-write, referential integrity |
| `R5.DependencyMigration.test_archived_reference_and_explicit_migration_with_owner` -> `B17-replacement(R5.DependencyMigration.test_archived_reference_and_explicit_migration_with_owner)` | A: create, archive, add-dependency, delete, migrate | archived references, integrity/errors, schema-9 dependency migration and IDs |
| `R5.CompletionGate.test_pending_dependencies_reject_without_writes_then_succeed_with_owner` -> `B17-replacement(R5.CompletionGate.test_pending_dependencies_reject_without_writes_then_succeed_with_owner)` | A: create, add-dependency, complete, archive | dependency gate/no-write, final status and ordered dependency IDs |
| `R5.CompletionArchived.test_archived_parent_still_obeys_terminal_transition_with_owner` -> `B17-replacement(R5.CompletionArchived.test_archived_parent_still_obeys_terminal_transition_with_owner)` | A: create, add-dependency, archive, complete | archived parent terminal error/no-write |
| `R5.Source.test_verbatim_default_and_mutations_after_b11_with_owner` -> `B17-replacement(R5.Source.test_verbatim_default_and_mutations_after_b11_with_owner)` | A: create, complete, archive, delete | verbatim/default source, persistence, IDs, B11 archive-before-delete and no-write |
| `R5.Notes.test_append_order_trim_and_failed_append_after_b11_with_owner` -> `B17-replacement(R5.Notes.test_append_order_trim_and_failed_append_after_b11_with_owner)` | A: create, append-note, complete, archive, delete | note order/trim, persistence, invalid note/no-write, B11 archive-before-delete |
| `C16.RequiredOwnership.test_users_required_owner_and_existing_filter` -> `B17-replacement(C16.RequiredOwnership.test_users_required_owner_and_existing_filter)` | A: create; B: list-users + two create-user returns + list-users | user ID/case/uniqueness/invalid user, valid owner, invalid owner/no-write, task ID/fields/list/order, conditional owner filtering; system ADMIN, Alex/alex USER |
| `C16.RequiredOwnership.test_unowned_migration_defaults_to_system` -> `B17-replacement(C16.RequiredOwnership.test_unowned_migration_defaults_to_system)` | A: migrate; B: list-users | historical owner system, count/schema/no-write, system ID and ADMIN role |
| `C16.RequiredOwnership.test_unresolved_nonempty_owner_migration_is_atomic_and_retryable` -> `B17-replacement(C16.RequiredOwnership.test_unresolved_nonempty_owner_migration_is_atomic_and_retryable)` | A: create, migrate; B: create-user return | unresolved-owner atomic failure, retry after registration, preserved task ID/owner; missing-user ID and USER role |

The B16 retry test's first `create-user known` result is not asserted against
an ID-only shape; retain the call and its success without inventing a
superseded assertion. Likewise, B16's invalid `create-user` errors remain
unchanged. B17's new role/permission errors need their own prospective cases.

### Lykoi: achieved {B01, B04}; seven applicable, two existing B02 skips

Lykoi has **no B16 or R5 methods** applicable. These seven originals require
actor adaptation only if B17 is achieved; none asserts user-result shape.

| Active original method -> B17 replacement | Dimension | Preserved assertions (C) |
| --- | --- | --- |
| `R.test_baseline_lifecycle_filters_failures` -> `B17-replacement(R.test_baseline_lifecycle_filters_failures)` | A: create, complete, delete | task IDs/fields, priorities/dates/status, list/filter/order, errors/no-write; see B11 condition below |
| `R.test_baseline_migration_corruption` -> `B17-replacement(R.test_baseline_migration_corruption)` | A: migrate, create | historical defaults and corruption rejection |
| `R.test_baseline_overdue_fixture` -> `B17-replacement(R.test_baseline_overdue_fixture)` | A: create | fixture schema/fields and overdue selection |
| `R.test_b01_priority_and_regression` -> `B17-replacement(R.test_b01_priority_and_regression)` | A: create, complete, delete | priorities, high/overdue selections, completed result and deletion (only if B11 not achieved) |
| `R.test_b01_historical_priorities` -> `B17-replacement(R.test_b01_historical_priorities)` | A: migrate | historical priority/default/schema/ordering |
| `C04.SourceLabel.test_verbatim_default_and_mutations` -> `B17-replacement(C04.SourceLabel.test_verbatim_default_and_mutations)` | A: create, complete, delete | source verbatim/default/persistence, IDs and deletion (only if B11 not achieved) |
| `C04.SourceLabel.test_explicit_migration_of_prior_storage` -> `B17-replacement(C04.SourceLabel.test_explicit_migration_of_prior_storage)` | A: migrate | migration source/default/count/schema/no-write |

Existing skipped `R.test_b02_tags_and_failure` and
`R.test_b02_explicit_migration` require B02 and are not B17 supersessions on
this achieved history. If B17 cannot be achieved, all seven originals and
the two B02 skips remain exactly as at B16; the table is prospective only.

## D: already superseded; never double-count or replace an inactive body

Conventional has 28 previous supersession skips. Two are B11 profile
supersessions (`R.test_baseline_lifecycle_filters_failures`,
`R.test_b01_priority_and_regression`); two are B11/R4 supersessions
(`C04.SourceLabel.test_verbatim_default_and_mutations`,
`C07.Notes.test_append_order_trim_and_failed_append`). R5 supersedes the
following 24 originals (including the R4 replacements), which are **not**
additional B17 targets on the Conventional history:

`R.test_baseline_migration_corruption`, `R.test_baseline_overdue_fixture`,
`R.test_b02_tags_and_failure`,
`C03.TagListing.test_exact_case_sensitive_tag_with_completed_tasks`,
`C03.TagListing.test_blank_queries_leave_storage_unchanged`,
`C05.StatusListing.test_both_statuses_and_no_write`,
`C06.Categories.test_create_filter_and_failed_create`,
`C08.Archival.test_archive_pending_completed_and_visibility`,
`C09.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order`,
`C09.DueWindow.test_invalid_ranges_and_timestamps_do_not_write`,
`C10.Owner.test_trim_reject_and_exact_owner_listing`,
`C10.Owner.test_migration_defaults_unowned`,
`C11.DeletionRule.test_lifecycle_priority_and_completed_delete_rule`,
`C11.DeletionRule.test_pending_deletion_with_and_without_archive`,
`C12.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue`,
`C12.Urgent.test_strict_current_time_and_empty_query_never_write`,
`C13.ArchivedMutations.test_archived_pending_and_completed_mutations_are_rejected`,
`C13.ArchivedMutations.test_unarchived_operations_remain_valid`,
`C14.Dependencies.test_order_cycles_and_no_write_failures`,
`C14.Dependencies.test_archived_reference_and_explicit_migration`,
`C15.CompletionDependencies.test_pending_dependencies_reject_without_writes_then_succeed`,
`C15.CompletionDependencies.test_archived_parent_still_obeys_terminal_transition`,
`R4.Source.test_verbatim_default_and_mutations_after_b11`,
`R4.Notes.test_append_order_trim_and_failed_append_after_b11`.

Four further originals (`R.test_baseline_lifecycle_filters_failures`,
`R.test_b01_priority_and_regression`,
`C04.SourceLabel.test_verbatim_default_and_mutations`,
`C07.Notes.test_append_order_trim_and_failed_append`) appear in the R5 map but
are already superseded by B11/R4 and therefore **must not** acquire a second
skip. Their still-valid checks flow through their applicable B11/R4 then R5
replacements above. On Lykoi, B11/R4 and R5 are inactive; its three overlapping
originals remain active as shown in the seven-row table.

## E: unaffected methods

With `migrate` included in B17's mutating-task scope, there are **no**
unaffected currently applicable methods on either post-B16 history. This does
not license a broad skip: the 33 and seven exact replacements above retain
their original unrelated assertions. Previously skipped B02 methods on Lykoi
remain skipped only for their original missing prerequisite. If a frozen B17
rule explicitly excludes `migrate`, the audit and mapping must be revised and
reverified **before** any amendment or B17 exposure; it must not be quietly
assumed during implementation.

## Activation and state-relative selection proposed for implementation

The original method selected for replacement is determined by achieved
history: where B11/B16 is achieved, replace the active B11/R5 replacement;
where not, replace the original. A single request B17 has the same actor and
role semantics in both histories. Before B17 success, no new skip or
replacement runs. Activate independently only on the successful track. Prior
B16 is **not** inserted into a B16-gap history. B17's user/role semantics
presuppose a persisted user registry; determine its formal dependency under
the frozen dependency rules before attempting classification, without treating
the numerical request order as a dependency by itself. Do not let eventual
output, classification or track labels select a replacement.
