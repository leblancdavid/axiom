# R5.4 semantic-format adequacy restart — prospective halt

**Status: STOP at the format gate.** This is a review of frozen requirement
meaning, not reconstruction of Python assertions. No semantic schema is frozen;
no B01–B16 clause bridge, B17 acceptance, composer, checkpoint revalidation or
B17-ready protocol is certified here. R5.2.2 remains the authoritative
corrected executable boundary. B17 remains UNEXPOSED and unclassified.

## Gate 1: controlled application clock

The disposable semantic probe now binds a single explicit UTC instant to its
semantic references and to each Python subprocess before application loading,
using `benchmark/semantic/clock_adapter.py`. `datetime.now(timezone.utc)` in
the application and the acceptance observations see that same instant. Missing,
late, non-UTC or mismatched bindings fail closed; naive local clock reads fail
closed. This adapter changes neither application nor the frozen oracle. The
focused fixture `ClockVocabulary.test_b12_entity_due_instants_and_query_plan_share_app_clock`
uses the pinned Conventional post-B16 executable: past/equal/future due dates,
strict `before`, urgent query exclusion at equality, application `created_at`
equality, two repeated runs and missing/mismatched binding rejection. This is
an execution-side witness, not an R5.2.2 revalidation or proof of an arbitrary
application's time-source discipline.

## Gate 2: requirement-text screening across B01–B16

The table inventories frozen-text *dimensions* from
`benchmark/requirements/B01.md` through `B16.md`. Each row gives proposed
stable clause roots (not yet assigned or verified bridge IDs), preconditions,
action, observation phase and expectation, and dependency/lineage. `S` means
seed/precondition, `A` invocation, `R` response/error, `P` persisted state,
`Q` query and `N` no-write comparison. `+` means an addition, `→` a change of
an earlier rule, and `dep` a semantic prerequisite. These labels are review
notes, **not** validated semantic records or activation edges.

| Frozen source | Clauses / preconditions → action → observation and expectation | Relationship and format finding |
| --- | --- | --- |
| B01:3–6 | Priority domain CRITICAL above HIGH; create with CRITICAL → R/P/Q returns and persists it; list-high includes exactly HIGH; old priorities through migration → P unchanged; omitted priority → R NORMAL. | + priority value; → prior priority domain/list-high; finite domain is witnessable but ordering *above* has no typed priority ordering relation. |
| B02:3–7 | Zero or more tags, arbitrary string input → create → R/P trimmed, case-sensitive first-occurrence deduplicated ordered array on all tasks; omitted/migrated → R/P `[]`; blank input → error `invalid_tag`, N no new task. | + repeated input / task field; dep create/migration. **Blocking gap:** no typed trim, nonblank, stable unique, case-sensitive sequence transformation or quantified input rule. Finite examples cannot encode the unbounded `zero or more` and `each VALUE` meaning. |
| B03:3–7 | Existing tagged tasks incl. completed → list-tag input → Q exact case-sensitive membership in normal order, missing tag `[]`, blank error, N unchanged storage. | dep B02 tags; + query. No general membership/filter or order semantics, only concrete result equality. |
| B04:3–6 | Optional source including whitespace → create/list/mutate/migrate → R/P verbatim value, omitted/old `""`, later mutations preserve. | + field, dep prior task lifecycle; `create_at` preexists. Arbitrary verbatim preservation needs a field invariant. |
| B05:3–5 | Pending/completed tasks → list-status both values → Q precisely matching ordered tasks, empty `[]`, N. | + query, dep existing status/order; only finite example equality. |
| B06:3–7 | Category absent/empty/nonempty/whitespace → create/migrate → R/P default, trim or invalid_category; exact case-sensitive list-category incl. `""` → Q; list unchanged. | + field/query, dep migration and existing list; general string normalization/filter unavailable. |
| B07:3–6 | New/migrated task → notes `[]`; append-note with arbitrary trimmed nonblank text, repeated in order → R/P appended; blank → error and N. | + ordered notes/mutation, dep task identity; no general append/trim invariant. |
| B08:3–8 | Pending/completed with archived false → archive → R/P true, repeat error; archived independently of status → all named ordinary lists exclude, list-archived includes, status unchanged. | + lifecycle/visibility; → old list selection. Scenario matrix witnessable, universal visibility rule unavailable. |
| B09:3–7 | UTC bounds incl. equal/reversed/invalid, dated/undated, archived/status → list-due → Q inclusive interval ordered or named error, N. | dep B08 archived and prior due/status; + window query. Typed `before` is strict only; inclusive range has no typed general predicate. |
| B10:3–7 | Owner omitted/supplied blank/nonblank/old record → create/migrate → R/P `""`, trim or invalid_owner; list-owner incl. empty → Q exact case-sensitive match. | + owner/filter; later B16 → optional-owner validity/default. |
| B11:3–5 | Completed unarchived/archived, pending any archive status → delete → error + N or R/P removed and returned. | → earlier delete rule, dep B08 archived; cases witnessable. |
| B12:3–6 | Pending nonarchived, due before/equal/after bound UTC and priority HIGH/CRITICAL/other → list-urgent/list-overdue → Q strict boundary, ordered results, N. | + urgent query, dep B01/B08/due; typed time and bound application clock now support boundary witnesses; general conjunction/selection rule not encoded. |
| B13:3–6 | Archived task → complete/append-note → error + N; archived deletion follows B11; archived remains visible until delete; no unarchive/reopen action. | → transition, dep B08/B11/B07; absence of an operation cannot be proven from finite examples. |
| B14:3–9 | New/migrated → ordered dependency IDs `[]`; add-dependency self/missing/duplicate/cycle/valid → R/P appended or named error + N both tasks; archive reference remains ID; delete referenced task → error + N. | + graph relationship, → delete, dep stable task IDs; arbitrary directed cycles/reachability cannot be represented by finite scenario equality. |
| B15:3–6 | Dependency pending vs. all complete incl. archived complete → complete → error + N or succeeds; dependency array unchanged, prior archived/transition rules retained. | → completion, dep B14/B13/B08; universal `any`/`every` graph predicate missing. |
| B16:3–11 | Built-in system + arbitrary unique nonblank case-sensitive user IDs → create-user/list-users → R/P IDs ordered or duplicate/blank error; create requires existing owner, unknown/missing error; migrate unowned to system, unknown nonempty owner error + N, create user/retry succeeds; prior owner filter retained. | + persistent users, → B10 optional owner/migration, dep task ownership. No quantified identity/membership invariant or general migration mapping. |

The earliest decisive gap is B02: `format.py` accepts only literal/previous-result
expressions, finite ordered CLI actions, `equals`, `distinct` and typed strict
`before`. For any finite plan exercising tags `x` and `X` and a finite number
of duplicates, an implementation that treats a *new* nonblank value incorrectly
or fails on one additional repetition still passes the plan. No semantic
record can state `for each tag, trim then retain the first case-sensitive
occurrence, for any number of arguments` in this vocabulary. An opaque Python
predicate or a benchmark-specific `tags_correct` primitive would hide the
requirement rather than represent it. B14's unbounded graph-cycle requirement
is another independent challenge. Adding examples is useful for acceptance
but does not close the semantic-format gate.

This table is **not** the required per-clause semantic encoding: the missing
primitive prevents that certification. In particular, the proposed roots lack
verified preconditions, exact replacement edges and achieved-history guards.
The next research step is a small domain-general rule vocabulary for sequences,
strings, quantified entity relations and graph reachability with independent
validation and executable semantics, then restart full clause-by-clause
adequacy review. Do not version/pin the schema, build the bridge, finalize B17,
or claim any later gate passed until this gap is resolved and reviewed.
