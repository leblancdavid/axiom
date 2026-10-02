# B11/R4 historical assertion-preservation audit — decision stop

Status: **audit only**. R5.3 is unfrozen and B17 unexposed. No frozen oracle,
classification, checkpoint or implementation is amended here. The unit of
comparison is a behavioral assertion with its setup and observation point,
not the count of Python `assert*` calls. In the table below `B` means
`benchmark/harness/regression.py:87-120`, `D` means the frozen
`benchmark/harness/cases/B11.py:24-72`; the B11 request is
`benchmark/requirements/B11.md:1-5`, the declaration is
`benchmark/harness/capabilities/B11.json`, and the contemporary intent is
`B11-FREEZE-R3.md:11-21` and `PROTOCOL_AMENDMENT_R4.md:32-59`.

## Baseline lifecycle → B11 disposition (complete method)

The frozen B11 declaration supersedes the *whole* baseline method upon B11
achievement, explicitly claiming the remaining lifecycle, filtering, failures
and no-write behavior. Its only intended baseline behavioral change is
completed **unarchived** deletion: success becomes `delete_requires_archive`
without writes, with success after archive. B11 also adds CRITICAL priority
and pending/archived deletion observations. R4 does not edit this replacement;
it adds B04/B07 replacement methods. `call` and `self.call` additionally
require success exit 0, empty stderr and JSON stdout, or failure exit 1,
empty stdout and exact JSON error; these apply to every call below, including
unassigned calls. Both helper implementations enforce those same outcomes.

| Baseline source | Semantic assertion, including setup | B11 carrier / disposition |
| --- | --- | --- |
| B:90-91 | Initial `list` succeeds with no tasks and does not create storage | D:27-28 **explicitly preserved** |
| B:92-93 | Blank-title create fails `invalid_title`, without creating storage | D:29-31 **explicitly preserved** |
| B:94-98 | Creates normal (no priority/due date), HIGH (past due), LOW (future due), all successfully; later observations use returned records | D:32-38 creates same three categories plus CRITICAL; **preserved** for successful creation and past/future filter setup. B11 changes normal description input from `details` to `x`; no direct assertion on that value, but the original distinct-description round-trip stimulus is no longer exercised (**scenario narrowing**, not an additional independently asserted description rule). |
| B:99 | Three created IDs are pairwise distinct | No equivalent B11 assertion; list equality and final set equality do not require pairwise uniqueness. **CONFIRMED_PRESERVATION_OMISSION** |
| B:100-101; helper B:60-69 | Every one of the three newly created records satisfies `check_task` | No invocation on created records in D; **CONFIRMED_PRESERVATION_OMISSION**. Expanded requirements below. |
| B:100-102 | Each of the three newly created records has `status == pending` before mutation | D:81 checks one *different* archived pending task; not equivalent to the three unarchived creation outputs. **CONFIRMED_PRESERVATION_OMISSION** |
| B:103 | Normal/HIGH/LOW priorities are NORMAL/HIGH/LOW | D:39-40 also checks CRITICAL; **explicitly preserved** |
| B:104 | Omitted due date on normal creation is `None` | No equivalent default-on-create assertion in D; **CONFIRMED_PRESERVATION_OMISSION** |
| B:105 | `list` contains exactly the returned new records in `(created_at,id)` order | D:41-43 checks all four records in the same order; **explicitly preserved** (four rather than three is intentional B11/B01 composition) |
| B:106 | `list-high` returns HIGH and excludes ordinary/LOW | D:44 checks HIGH only, including exclusion of CRITICAL; **explicitly preserved** |
| B:107 | Only past-due pending HIGH appears in `list-overdue` | D:45; **explicitly preserved** |
| B:108-111 | Invalid due-date create and missing-ID complete return exact errors and leave stored bytes unchanged | D:46-50; **explicitly preserved** |
| B:112-113 | Completing HIGH returns the same record except `status == completed` | D:51-54; **explicitly preserved**, also checks CRITICAL completion |
| B:114 | Completed HIGH disappears from overdue listing | D:55 after completing HIGH and CRITICAL; **explicitly preserved** (CRITICAL had no due date) |
| B:115-117 | Re-completing HIGH fails `invalid_transition` with no storage change | D:56-60 includes this error, plus two failed unarchived deletes, with a single before/after byte comparison; **explicitly preserved**, with broader failure sequence |
| B:118 | Delete completed, unarchived HIGH succeeds and returns completed record | **INTENTIONALLY_SUPERSEDED** by D:58-59 (reject/no write), D:62-67 (archive then successful delete, preserving archived record) |
| B:119 | A second delete of HIGH fails `task_not_found` | D:68; **explicitly preserved** |
| B:120 | Final `list` contains just normal and LOW IDs | D:71-72; **explicitly preserved** after both HIGH and CRITICAL are removed; D:69-70 adds empty `list-high`/`list-overdue` |

No additional independent baseline lifecycle *assertion* is missing after
expanding the helpers and comparing every observation above. The changed
description input is a lost differential test stimulus and should be retained
if restoring the original scenario, but the baseline method never asserted
the returned description equals `details` (it compared returned records to
later list output); it is not silently promoted to a fifth baseline invariant.

### Exact helper scope at the B11 boundary

`regression.check_task` (`regression.py:60-69`) checked, **on each of the
three create results**: exact keys equal to the achieved schema profile's
`fields`; `id` is a string and nonblank after stripping; `created_at` is a
string ending in `Z`, parseable as ISO 8601 after replacing `Z` with `+00:00`,
with UTC offset zero; and, if B02 is achieved, `tags` is a list. This last
condition applies on the Conventional B11 history but not to a history without
B02. The profile-dependent runner wrapper (`regression_phase5c_r4.py:82-89`,
`regression_phase5c_r5_1.py:87-94`) adds exact `type` equality for **each**
profile `field_types` entry on each invocation (seven entries on B01–B16).
Those checks are one invocation's expansion, not seven independent helper
calls or independently imposed requirements from nested construction. Other
methods' `upgraded` helper checks these shapes on *migrated rows*; the overdue
fixture checks the probe's key set only (`regression.py:156-159`). Neither
observes all the same create results under the lifecycle setup.

The B11 request changes deletion eligibility only; its requirement, case,
fragment and freeze give no intent to waive identity uniqueness, create-result
shape/type/time validity, pending initial state or null default due date.
They are valid unrelated baseline requirements. B11 `test_pending_deletion...`
checks an archived task stays pending (`B11.py:74-84`), but that is not
the initial-status assertion on normal/HIGH/LOW create results. Migration
defaults of `due_date: null` test migration, not a new create default.
Other active acceptance methods do exercise adjacent creation, ordering,
storage validation, migration and filtering; none restores the missing
**same preconditions and observations** as a semantic assertion group.

## Other B11/R4 replacement compositions

The frozen fragment also supersedes `regression.Regression.test_b01_priority_and_regression`
(`regression.py:163-178`). B11 checks NORMAL/HIGH/CRITICAL/LOW creation
priority (`B11.py:39-40`), initial list and `list-high` (`41-44`), and
completion of CRITICAL with its full returned record/status (`52-54`). Its
post-deletion empty overdue and high lists (`69-70`) cover the end state;
completion/deletion of CRITICAL now obeys archive-before-delete. **Additional
CONFIRMED_PRESERVATION_OMISSION, B01 provenance:** B01:176 checks
`list-high == [high]` **after CRITICAL is completed but while HIGH remains
pending**. D:44 checks this only while CRITICAL is still pending; D:51-55
completes HIGH before CRITICAL, and D:69 checks after both are deleted. No
other active B11/R4 or subsequent B12–B16 method asserts the same
post-CRITICAL-completion/HIGH-pending `list-high` state. The B01:173
`list-high == [high]` before completion *is* preserved by D:44. B01:178
`list-overdue == []` after deleting the non-due CRITICAL task is an
observation at a different point; since no task in that B01 scenario has a
due date, the same empty overdue behavior is exercised in D:70, while
the difference in intermediate HIGH-selection is recorded separately above.
The B01 completed-unarchived CRITICAL delete success at B01:177 is
**INTENTIONALLY_SUPERSEDED** by the B11 rule. B01's list equality/ordering,
priority defaults and completion of CRITICAL have carriers in D:39-54.

R4 additionally replaces exactly B04's
`SourceLabel.test_verbatim_default_and_mutations` and B07's
`Notes.test_append_order_trim_and_failed_append` (`regression_phase5c_r4.py:18-25`).
Comparing `cases/B04.py:25-44` with `cases/B11_R4_replacements.py:30-54`:
verbatim/omitted/empty source values, ID→source map of `list`, HIGH-filter
source, completed return and subsequent list round-trip all remain asserted.
Only success of completed-unarchived deletion changes to error/no-write,
then archive and successful delete preserving source. Comparing
`cases/B07.py:24-45` with `B11_R4_replacements.py:57-83`:
both initial empty notes, trim/append order, list round-trips, blank append
error/no-write, unaffected second record, completed notes and successful
deletion's notes all remain asserted; B11 rejection/no-write and archive are
added. The frozen B04 and B07 *migration* methods are never superseded by R4
(`PROTOCOL_AMENDMENT_R4.md:49`). The same `self.call` success/error envelope
persists. **No further unrelated asserted behavior loss found in these two
R4 replacement bodies**. The fifth omission above belongs to B11's B01
supersession, not the B04/B07 R4 repair.

## Propagation and affected histories

| State | B11-achieved history | History without B11 |
| --- | --- | --- |
| Before B11 | Baseline lifecycle and B01 method active; all five assertion groups present | Same when B01 achieved |
| B11/R4 | Fragment skips baseline lifecycle and B01; B11 body lacks four baseline groups and B01 intermediate-state group. R4 adds B04/B07 repairs only. | Fragment/R4 skips not selected; baseline and B01 methods remain active |
| R5 | `regression_phase5c_r5.py` selects active B11 lifecycle for owner-adapted R5 replacement; `cases/B16_R5_replacements.py:169-189` replays its exact code object. It cannot regenerate absent checks. B11 supersessions take precedence over attempted baseline/B01 replacements (`regression_phase5c_r5.py:31-41`). | Original baseline/B01 sources still active; B16 owner replay only if B16 achieved without B11 |
| R5.1 | Same selection/body (`regression_phase5c_r5_1.py:31-42,83-116`); no restoration | Same condition |
| R5.2/post-B16 | `regression_phase5c_r5_2.py:25-46` delegates suite construction to R5.1; unchanged omission | Unachieved B16/B11 means original sources remain active |

The post-B16 Conventional checkpoint (`checkpoint-conventional-B16-r5_2.json`)
records achieved B01–B16: **its composed acceptance is affected by all five
coverage losses**. The post-B16 Lykoi checkpoint
(`checkpoint-lykoi-B16-r5_2.json`) records only B01 and B04: B11/B16 did not
activate, so **its composed acceptance retains the original baseline/B01
assertions**, including the four plus the B01 intermediate-state check.
This conclusion depends on achieved history, not track name. Any future
history achieving B11 encounters the loss unless an additive restoration is
approved; any history without B11 retains the original tests.

### Oracle coverage versus implementation behavior

The omission first occurred when B11 superseded the methods; neither the
passing R4 results nor later R5/R5.2 pass counts establish those omitted
properties. Read-only inspection of the current Conventional implementation
(`benchmark/conventional/task_manager.py:157-167`) shows `uuid4` IDs, initial
`pending`, UTC `Z` creation time and `due_date=None` default. This supports
implementation intent but is not a read-only replay of every historical
checkpoint and does not establish all five assertions against every historical
binary/state. The Lykoi post-B16 history retains the executable originals;
its recorded acceptance results cover them at that checkpoint, not B11.
**No historical implementation is reclassified** on an oracle-coverage finding.

## Construction isolation for prospective analysis

The frozen R5.1 `build_suite` captures `original.check_task` and installs a
profile wrapper; a second in-process build captures that wrapper and nests it.
Prospective `acceptance_inventory_r5_3.collect` now enters
`isolated_construction`: reset the helper to the captured original baseline
function before building, then restore `APP`, `ACHIEVED`, `PROFILE` and helper
in `finally`, including on failure. It does not change any pinned runner or
frozen acceptance case. Fixtures in `test_phase5c_r5_3.py` compare first and
repeated inventories across different achieved profiles, check saved global
identity/provenance and the single direct base-helper closure, and execute
the helper on representative records with exactly one field-type check per
profile field. Nested prior-process wrappers are not semantic requirements.

## Prospective remediation proposal — NOT APPLIED

Authorize a **new additive protocol revision**, independently pinned and
reviewed before any further acceptance freeze, that carries original
assertion IDs/provenance (`regression.py:99-104` and B01:176) forward:

1. For histories in which B11 superseded baseline lifecycle, assert on the
   normal/HIGH/LOW create results: three different IDs; each record's exact
   applicable fields, nonblank string ID, valid UTC `Z` timestamp and
   conditional B02 tags-list/type checks; pending initial status for each;
   and `normal["due_date"] is None`. Use the achieved schema profile at the
   tested state, and apply one deterministic profile-field-type layer. Keep
   owner adaptation where B16 is achieved.
2. For histories in which B11 superseded B01, assert `list-high == [high]`
   after completing CRITICAL while HIGH remains pending. The minimal additive
   scenario can create HIGH and CRITICAL in disposable storage with their
   required current owner and applicable defaults; it need not rewrite or
   replace B11's method. Its semantic root remains B01:176.
3. Activate only when the origin is achieved and the original carrier is
   superseded by B11. Where B11 is not achieved, retain original baseline/B01
   methods; do not duplicate their requirements. Continue to supersede the
   obsolete completed-unarchived deletion success assertions; never revive
   them. R5's owner adaptation and R5.2 history-relative schema composition
   still apply; restoration is an additional active carrier, not a rewrite of
   their frozen bodies. The original `details` description may be reused as
   the baseline stimulus, without inventing an extra invariant.
4. Before applying the revision to future scoring, optionally restore each
   historical checkpoint independently into a disposable, read-only-validated
   environment and run the *proposed* additive checks as separately labelled
   retrospective diagnostics. Do not rewrite the checkpoint, frozen result or
   classification. If a historical implementation fails, stop for a separate
   explicit protocol/adjudication decision distinguishing an implementation
   defect from this oracle defect; do not silently backdate a failure or
   weaken the restored checks.

**Decision stop:** the four reported baseline groups are confirmed omissions
and exhaustive for asserted baseline lifecycle groups; one further B01
intermediate-state assertion was lost by B11 composition. No additional
B04/B07 R4 assertion omissions were found. There is adjacent but no
precondition-equivalent active coverage for the five lost groups on a
B11-achieved history. No R5.3 freeze, historical oracle repair, B17
construction/exposure or B17–B20 execution is authorized by this audit.
