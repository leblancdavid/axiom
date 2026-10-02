# Phase 5C R5 — prospective B16 acceptance-composition amendment

**Version:** `PHASE5C-R5-B16-COMPOSITION/1`. **Status: FROZEN before B16
preflight, prediction, implementation or classification on either track.**
Authority: the B16 conflict in `RESUME-R4-B16-HALT.md` and the independently
verified 27-method union in `B16-ACCEPTANCE-COMPOSITION-AUDIT.md`. The latter
is an audit proposal, not an executable oracle. This amendment is additive to
`PROTOCOL_AMENDMENT_R4.md` and `R4-EXECUTION-PIN.md`. B01–B15 historical
requirements, cases, predictions, classifications, results, checkpoint records,
snapshots and original R4 oracle remain byte-identical and retain their
original meanings. Evaluate functional behavior, not source-code identity.

## Exact semantic scope and activation

B16 requires task creation to name an existing `--owner`; omitted or unknown
owners fail `invalid_owner`. Previously unowned tasks migrate to `system`.
Only the obsolete historical expectations of successful ownerless creation,
unregistered named owners, or migration to an empty owner are displaced. Other
assertions in the same methods remain compulsory. The frozen B16 acceptance
case/fragment will be frozen separately **after** the B16-ready boundary.

For each track independently, activate R5 supersessions **if and only if B16
is in that track's achieved-capability set**. A gap, blocked dependency or
other non-success leaves that track's pre-B16 accumulated oracle in force.
An origin must also be achieved, and a frozen method already superseded by
achieved B11/R4 retains its earlier disposition; R5 replaces the applicable
B11/R4 *replacement* where necessary. No change applies retrospectively.
The R5 runner aborts on absent source methods, duplicate replacement IDs,
hash drift, composition/checkpoint mismatch or an R4 supersession collision.
Every selected frozen method gets an explicit named replacement method and a
reported `superseded_cases` entry with its replacement ID; no implicit skip.

## Exact supersession inventory

The full original-ID → replacement-ID mapping is the 27-entry immutable
`METHODS` table in `cases/B16_R5_replacements.py` (pinned below). The audit
table, pinned below, records each original's request, specific superseded
assertion, and unaffected assertions. These two pinned tables are incorporated
into this amendment as its exact inventory. Abbreviations below expand to the
full IDs in that table; no wildcard or suffix matching is used by the runner.

| Origin/method names | B15 applicability | Disposition when that track achieves B16 |
| --- | --- | --- |
| `regression.Regression.test_baseline_migration_corruption`, `test_baseline_overdue_fixture` | Both | Replay every frozen assertion with a built-in existing `system` owner for the fixture task; migration/defaults, corrupt-state checks, schema and overdue selection retained. |
| `regression.Regression.test_b02_tags_and_failure` | Conventional | Replay tag/default/deduplication/invalid-tag/no-write/completion checks with valid owner. |
| `regression_B03.TagListing.test_exact_case_sensitive_tag_with_completed_tasks`, `test_blank_queries_leave_storage_unchanged` | Conventional | Replay both methods, including exact tag matching and blank-query/no-write, with valid owner. |
| `regression_B05.StatusListing.test_both_statuses_and_no_write` | Conventional | Replay pending/completed filtering, order and no-write with valid owner. |
| `regression_B06.Categories.test_create_filter_and_failed_create` | Conventional | Replay category trim/default, invalid category, filters, completion and deletion with valid owner. |
| `regression_B08.Archival.test_archive_pending_completed_and_visibility` | Conventional | Replay archival, visibility, transitions, filters and no-write with valid owner. |
| `regression_B09.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order`, `test_invalid_ranges_and_timestamps_do_not_write` | Conventional | Replay bounds, filtering, timestamp errors and no-write with valid owner. |
| `regression_B10.Owner.test_trim_reject_and_exact_owner_listing` | Conventional | Register `Alex` and `alex`, retain trim/blank rejection, exact/case-sensitive filter, read-only and deletion; replace ownerless task with explicitly owned `system` task. |
| `regression_B10.Owner.test_migration_defaults_unowned` | Conventional | Preserve explicit migration/no-write/schema checks; assert migrated `system` owner and `system` filter instead of empty owner/filter. |
| `regression_B11.DeletionRule.test_lifecycle_priority_and_completed_delete_rule`, `test_pending_deletion_with_and_without_archive` | Conventional | Replay priority, lifecycle, completed/pending archive/delete and no-write with valid owner. |
| `regression_B12.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue`, `test_strict_current_time_and_empty_query_never_write` | Conventional | Replay urgency/time, exclusions, order and no-write with valid owner. |
| `regression_B13.ArchivedMutations.test_archived_pending_and_completed_mutations_are_rejected`, `test_unarchived_operations_remain_valid` | Conventional | Replay terminal rules, notes, valid mutations/deletion and no-write with valid owner. |
| `regression_B14.Dependencies.test_order_cycles_and_no_write_failures`, `test_archived_reference_and_explicit_migration` | Conventional | Replay ordered dependencies, cycles, missing IDs, deletion integrity and migration with valid owner. |
| `regression_B15.CompletionDependencies.test_pending_dependencies_reject_without_writes_then_succeed`, `test_archived_parent_still_obeys_terminal_transition` | Conventional | Replay completion gate, archived prerequisites, ordering and terminal/no-write rules with valid owner. |
| `regression_B11_R4.Source.test_verbatim_default_and_mutations_after_b11`, `regression_B11_R4.Notes.test_append_order_trim_and_failed_append_after_b11` | Conventional | Replay unchanged source and notes assertions, B11 completed deletion requirements and no-write with valid owner. |
| `regression.Regression.test_baseline_lifecycle_filters_failures`, `test_b01_priority_and_regression`; `regression_B04.SourceLabel.test_verbatim_default_and_mutations` | Lykoi only at B15 | Replay original pre-B11 lifecycle/priority/source/deletion assertions with valid owner **only if Lykoi independently achieves B16 without B11**. Already superseded on Conventional by B11/R4. |

Names prefixed `regression_Bxx.Class` above denote the exact full IDs
`regression_Bxx.cases.<locals>.Class.method` (and similarly for
`regression_B11_R4`). No B07 method is newly superseded: on Conventional
the original B07 method has already been superseded by R4, whose Notes
replacement appears above; on Lykoi B07 was not achieved. Migration-only
methods whose expected rows use the composed `migration_defaults` remain
active. The separately frozen B16 fragment must express the `system` migration
default for an achieved B16 track, without altering older frozen fragments.

## Mechanism, provenance and frozen bytes

The R5 case module calls each original frozen method body unchanged. For its
23 Conventional methods with obsolete ownerless fixture creation (and the
analogous Lykoi methods), a local per-replacement CLI call adapter supplies
`--owner system` *only* to `create` calls missing an owner. It does not seed
users or storage, change errors, alter non-create commands, modify source
methods, or suppress assertions. The two B10 methods are spelled out because
they must register users/change asserted values. The replacement module
names all 27 original IDs and 27 replacement IDs explicitly. The R5 runner
composes frozen cases, R4's achieved B11 overlay, and conditional R5 cases;
it reports each loaded method's active/superseded/replacement/existing-rule
skip disposition. It retains format-3 checkpoint and composer validation.

SHA-256 values are over raw bytes (lowercase hex):

| Artifact | SHA-256 |
| --- | --- |
| `B16-ACCEPTANCE-COMPOSITION-AUDIT.md` | `7aeed0bea18f69ec4733a6688f7c7b495fce7ec6ff2f65c969a3080005265b20` |
| `benchmark/harness/cases/B16_R5_replacements.py` | `9310e8f19557c8e9dfee4a1c4527524ec38c5de238d5b11d3ef9f5e08aa72d74` |
| `benchmark/harness/regression_phase5c_r5.py` | `26c24272474a4a814d2adf016a174bfc243f93be23f6f7da126635133a6c9444` |
| `benchmark/harness/test_phase5c_r5.py` | `6e01d242a18119253feb58323bfb8c6099b2ecf2dfbedc1f5bf504f473ee8229` |
| R4 runner | `61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9` |
| R4 replacements | `8a8bfad8451e747e31429f1bd87055689d3115ef851861ec48810fbe4678ca60` |
| Conventional B15 checkpoint / snapshot | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` / `8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc` |
| Lykoi B15 checkpoint / snapshot | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` / `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` |

All original B01–B15 requirement/case/fragment hashes remain pinned in the
B15 checkpoints and earlier freezes. Before any B16 exposure, independently
restore the two B15 snapshots, validate their inventories and R4-equivalent
accumulated external/internal suites under R5, and run the repository harness
suite including the hypothetical B16 composition fixtures. Record a B16-ready
boundary only on complete success; stop and record a halt for any drift or
new contradiction. Do not silently repair or re-freeze after seeing a B16
implementation. No B17–B20 exposure before a valid B16 classification.
