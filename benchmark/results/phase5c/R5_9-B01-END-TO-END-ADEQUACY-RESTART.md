# R5.9 — B01 end-to-end adequacy restart (prospective, 2026-10-02)

**Decision boundary:** R5.2.2 remains the authoritative corrected post-B16
benchmark state. This is a fresh review of the *complete* frozen B01 request
(`benchmark/requirements/B01.md:3-6`) together with the inherited frozen
`benchmark/baseline.md:3-38`, the original `benchmark/harness/regression.py`
(`:86-196`), profile `profiles/B01.json`, and the R5.2.2 corrected
intermediate-state carrier (`PROTOCOL_AMENDMENT_R5_2_2_B01_PRECONDITION.md`).
The Conventional implementation is not a semantic authority. No historical
artifact, compiler, generated file, frozen oracle or acceptance profile was edited.
R5.3 reconstruction remains unfinished; the selected acceptance cases do not
replace a complete assertion-level bridge.

## 1. Frozen contract reconstructed, clause by clause

Notation: `S` is the *actual* durable pre-state, `S'` its after-state, `I`
the call input (including argument presence), `O` the public success/error
outcome, `T(S)` the complete task population, and `R` a successful task result.
`sort` is ascending `(created_at, id)` (baseline:9-11); `filter_HIGH` is an
exact, source-relative selection independent of status. The following table
separates **explicit** text from proposed relational interpretations. A state
view must include storage absence, version and every field that matters; merely
checking a selected sequence cannot establish durability or no-write.

| Explicit frozen obligation / source | Input, pre-state, outcome and post-state | Collection/order/persistence/failure; interpretation limits |
| --- | --- | --- |
| B01:3 `CRITICAL` added “above HIGH” | Create priority domain admits CRITICAL distinctly from HIGH. | No public ranking/comparator or priority-sort is specified; ordinal meaning remains ambiguous. |
| B01:3-4 create CRITICAL persists and returns it | `I.priority=CRITICAL`, valid create and `S`; success `R.priority=CRITICAL`; `S'` contains the returned record. | Baseline create shape/unique nonempty ID/pending/current UTC time/verbatim description/due date apply; existing records must survive (baseline new-task behavior, interpreted as a framed insertion). Another process's list must include it. |
| B01:4 `list` includes it | Input `list`, `S`; result is *all* records including CRITICAL and completed ones, sorted by `(created_at,id)`; `S'=S`. | Exactness excludes missing/extraneous records. Read must not create absent storage (baseline:7). |
| B01:4-5 `list-high` still exactly HIGH | Input `list-high`, `S`; outcome `filter_HIGH(sort(T(S)))`; `S'=S`. | Includes completed HIGH, excludes CRITICAL (completed or pending); exactness, completeness and normal source order. R5.2.2 restores the observation with pending NORMAL and HIGH plus completed CRITICAL; see original regression:168-176. |
| B01:5 existing LOW/NORMAL/HIGH survive migration | Input explicit `migrate`, legacy `S`; successful `S'` keeps each present priority and task identity. | Other pre-existing fields also survive under baseline additive migration; neither replacement nor reordering of unrelated records is authorized by the data relation. Normal *list* order remains separately constrained. |
| B01:6 missing priority defaults NORMAL | Omitted priority on create yields NORMAL; missing field on legacy migration yields NORMAL. | Omission differs from explicit priority; do not overwrite existing LOW/NORMAL/HIGH. Baseline v1 also adds `due_date:null`, v2 adds `due_date:null`. |
| Inherited baseline:13-17 create and invalid input | Valid title, optional due date and priority; success returns exact seven-field record with fresh ID, pending status, creation time and requested/default values. | Blank title `invalid_title`, malformed/non-UTC due date `invalid_due_date`; failures do not change stored bytes. Baseline invalid enum/read state is `invalid_state` on read; precise CLI error for a syntactically invalid priority argument is **not specified** here. |
| Inherited baseline:18-26 completion and read/list behavior | `complete(id)` on pending target: return target with status completed; `S'` changes that status and preserves other fields/records. | Missing ID `task_not_found`, already completed `invalid_transition`, stored bytes unchanged. Completed tasks remain visible in list and completed HIGH in list-high. Delete returns its removed record (including priority), missing ID fails unchanged; overdue filtering remains the inherited baseline behavior. |
| Inherited baseline:27-32 migration | Explicit v1 unversioned or v2 input to v3, success `{"migrated":N}`; preserve old fields/IDs, fill missing priority (v1) and due date (v1/v2). | `N` is the migrated record count as exercised by frozen `upgraded` helper; current/absent storage returns 0; new writes use v3 envelope. Legacy reads fail `migration_required` unchanged. Current-version migration idempotent. Mechanism/byte layout beyond the declared envelope is not specified. |
| Inherited baseline:34-38 failure/state integrity | Malformed JSON, invalid shape, duplicate/blank IDs and titles, invalid enums/timestamps fail `invalid_state` on read. | All failed operations preserve **persisted bytes**, stronger than decoded-state equality; storage absence is observable. Error exit=1 JSON stderr; success exit=0 JSON stdout (baseline:3-7). |

Interpretation boundaries: a “new ID” entails freshness against the current
population, not a prescribed UUID algorithm. “Current” creation time requires
a clock binding to evaluate precisely; the frozen oracle checks UTC shape, not
an exact instant. The frozen request does not state that migration should
reclassify HIGH or rank CRITICAL numerically. The ordinary list has exactly
the inherited timestamp/ID order, **not** a priority order. The post-B16
carrier adapts later achieved features; it does not redefine the B01-only
schema or its v3 migration target.

## 2. CRITICAL adjudication

Five independent propositions: (1) accepted finite priority domain membership;
(2) CRITICAL round-trips through create/storage/list; (3) exact-HIGH query
excludes CRITICAL; (4) independently observable CRITICAL > HIGH ordinal
comparison; (5) normal list order. Frozen text and corrected carrier support
(1)-(3); baseline supplies `(created_at,id)` for (5). No comparator, rank
result, priority-sorted view or rank-dependent command establishes (4).
**PRIORITY_ORDINAL_UNDERSPECIFIED**. “Above HIGH” cannot license a new
comparator or priority sort; the ambiguity is `BENCHMARK_UNDERSPECIFICATION`,
not evidence that a semantic construct is missing.

## 3. Existing-construct composition: abstract obligations, not executable B01 contracts

Candidate numbers refer to the historical 45-entry ledger, not 45 implemented
integrated language operations. Put each rule inside #45 over the *same* typed
`(I,S,O,S')`; use #22/#23 for applicable states and finite populations, #1-8
for typed records, projection, presence, equality and Boolean alternatives.
`P => Q` is #8(`#7(P,#8(Q))`) complemented as in R5.8. Assign distinct typed
success and error tags; no command-specific semantic operator is proposed.

| Operation | Attempted universal relational decomposition | Integration boundary |
| --- | --- | --- |
| Create | Domain `{LOW,NORMAL,HIGH,CRITICAL}`; success task has requested/default priority, exact input title/description/due date, pending status, fresh nonblank ID and clock-bound UTC creation. Select old records from `S'` by `id != R.id` (#10-12), compare their canonical ordered view to `T(S)` (#43, #6); select `id == R.id` from `S'` and equate exactly to singleton `[R]`. Reject new ID already present in `T(S)` by exact empty selection. This relates returned and persisted *full record*, not just priority. Error alternatives require unchanged state/bytes where specified. | #45 implementation cannot type CLI input records with optional args, nullable due date, or singleton task outcome; no checked B01 public/storage lowering. |
| Normal list | `O.value = #43(T(S), created_at:instant, id:string)` with exact multiset, full field equality, unique keys; `S'=S`. Includes completed tasks. | #43 evaluator exists separately but not in #45's typed predicate checker; `tasks.json` has no checked state projection. |
| list-high | Let `L=#43(T(S))`; #10/11/12 require `O.value=exact_select(L, r.priority==HIGH)` and `S'=S`. Includes completed HIGH, no CRITICAL, omissions or extras. | Selection witness evaluator is separate from #45 and cannot attach this to actual B01 calls yet. |
| Complete | For pending target `k=I.id`, select exactly one before target and one after target. Require return equals post target, its status completed; project and equate each *other* field of pre/after target (#2/#6). Exact selection on `id != k` from both states and comparison of canonical full-record collections (#43/#6) frames unrelated records. Missing/already completed imply typed errors plus `S'=S`; byte-level unchanged is a separate observable effect constraint. | #45 does not implement these selection/projection relations over the same tuple or typed record-valued result; failure tag model can express conditions only when predicates are integrated. |
| Migration | For v1/v2 `S`, compose #44 keyed `default_missing(priority,NORMAL)` where absent, then #44 `default_missing(due_date,null)` where absent; compare complete keyed after collection; preserve identities and every present field. Constrain version transition in checked evolution/state metadata, success outcome and repeated migration=0; legacy read error with unchanged bytes. | #44 currently supports one optional field, typed string/bool/instant default (not null), and no version or numeric count; v1/v2 intermediary is a relational witness, not an observed extra operation. |

The insertion/frame decomposition uses selection's *exact* mode to prohibit
extra identities and #43's full-record multiset equality to avoid imposing
storage order. For an empty pre-state the outside-target selection is empty;
for arbitrary finite pre-states the same equations apply. Its `R.id`-dependent
predicate, singleton result and cross-typed projections have not been accepted
by one integrated validator; this is a **composition hypothesis**, not a
demonstrated universal contract. No `insert` primitive is justified yet.
Completion uses the same technique twice: target-field projection/equality
and outside-target full-record framing. Equality of the target status alone
would miss priority or due-date changes; equality of the result alone would
miss changes to unrelated records. No `complete_task` construct is justified.

Alternatives considered: #44 alone cannot add an identity (its identity sets
must agree), nor change an existing target status. #6 alone on entire `S/S'`
forbids legitimate mutations. #10 without exactness admits omitted/extra
records; #43 alone does not identify the one permitted change. Finite witness
steps #28-36 do not universally constrain calls. Composed #10-12/#43 plus
typed projections and #45 avoid those particular failures *in the abstract*;
neither the existing separate evaluators nor #45 currently check the whole
expression. A future integrated checker must verify totality, typing and
predicate applicability instead of treating these prose equations as code.

## 4. Migration outcome/version and construct #30 gate

Transformation, actual persisted v3 state, result `{"migrated":N}`, failure
classification and no-byte-change, legacy fixture compatibility and version
mapping are separate obligations. The v1/v2/v3 labels and JSON envelopes are
evolution/link and implementation-binding metadata; the record-preservation
and count relation are application semantics. Neither Python migration function
names nor its algorithm belong in core semantics.

**STOP before construct #30.** Exact frozen clause: `benchmark/baseline.md:27-32`
requires `migrate` return `{"migrated": N}`, with 0 for current/absent state;
`regression.py:71-83,122-135,185-196` exercises counts. For arbitrary valid
legacy populations, the current implemented candidate relations do not state
that the **numeric outcome equals the cardinality of the migrated collection**.
Attempted compositions: #44 maps every old identity exactly once but never
relates its size to a scalar result; #10-12 can select the migrated population
but cannot project its length into an outcome; #23 universal finite scope
constrains each element, not numeric cardinality; #6 can equate collections or
typed scalars only when a count term is already available; #26 accepts an
integer seconds offset, not a generic collection-to-integer relation; #45
currently admits a uniform sequence payload rather than numeric outcome
records. Equating the result to a fixture literal works only at one population
size. Count/cardinality would plausibly apply outside B01 to pagination,
batch operations and deletions, but its relation to an observed JSON numeric
payload also needs outcome typing/adapter lowering. **Primary classification:
CORE_SEMANTIC_EXPRESSIVENESS (provisional)**. Focused review must determine
whether count is already derivable in a consistently typed composition before
adding any construct. The nullable due-date/default and heterogeneous outcome
payload are additional **DOMAIN_SEMANTICS** and **COMPILER_LOWERING** questions,
not permissions to create primitives in this restart.

## 5. Actual B01 boundary, provenance and observation

`benchmark/semantic/b01_restart.py` declares a closed command/argument map for
create, list, list-high, complete and migrate, validates presence and names,
pins `generated/task_manager.py` extracted from the historical Lykoi B01 tar
against `checkpoint-axiom-B01.json:files`, and runs it from a disposable
directory. It captures the actual subprocess argv, complete exit/stdout/stderr,
and independently reads `tasks.json` raw bytes and decoded envelope before and
after each invocation. `test_b01_restart.py` runs the actual original frozen
B01 acceptance methods on that pinned app, checks a real selected B01 root
call sequence, failure endpoints and one v1 migration. This is checked
**public adapter metadata plus artifact integrity and independent endpoint
observation**, not a semantic contract or a compiler-owned B01 operation event.
The stable semantic operation names in the prospective table map to public
CLI tokens; the SHA identifies the deployed snapshot artifact, not a per-
operation generation or contract digest. The snapshot's single artifact
manifest has no operation-specific boundary attribution, and the v0.3
executable emits no R5.7-style internal operation/persistence invocation
record. Fabricating one from public output or the same readback would merely
self-assert grounding. Consequently R5.7's internal-versus-independent
challenge **cannot pass for B01** without further checked lowering/target
instrumentation. No synthetic vial evidence was re-labeled as application
execution. File endpoint equality alone cannot exclude intermediate writes or
undeclared effects; isolated single-file runs are the observed scope.

| Actual selected execution | Independent evidence | R5.7 grounding / #45 conformance |
| --- | --- | --- |
| B01 root: default, HIGH, CRITICAL creates; list-high, list, complete CRITICAL, list-high | Seven subprocess calls; public root check true; each call had separately reopened durable file; artifact hash matched pinned snapshot. | **GROUNDING FAILURE / not evaluated**: no internal B01 event. External root success is not a #45 verdict. |
| Already-completed `complete` error | Exit 1 and `invalid_transition` JSON stderr; before/after raw byte hashes equal. | **GROUNDING FAILURE / not evaluated** for the same missing event. |
| v1 unversioned one-record explicit migration | Public `{"migrated":1}`, independently read v3 envelope, preserved identity/fields and NORMAL/null defaults. | **GROUNDING FAILURE / not evaluated**; one count does not establish the arbitrary-count rule. |
| Original frozen B01 regression on pinned B01 Lykoi snapshot | Five passes, zero failure events; later request cases skipped under the B01 profile. | Frozen acceptance evidence, **not** grounded #45 evidence or universal correctness. |

These executions are neither `GROUNDED + SEMANTICALLY CONFORMANT` nor
`GROUNDED + SEMANTICALLY NON-CONFORMANT`: both statuses require a challenged
actual B01 event and an integrated B01 contract evaluator. If an observation
is unreliable it must fail grounding; if a faithful observation later shows a
behavioral bug it must reach semantic verification and fail there. R5.7/R5.8
synthetic fault tests demonstrate that separation for their own operation,
not for B01.

## 6. Layer-by-layer unresolved obligations and statuses

Each row has **one primary** blocker category; secondary dependencies are
described in the text above, not counted as an alternative primary category.

| Remaining obligation | Primary blocker |
| --- | --- |
| General numeric migration count tied to arbitrary before-state population | CORE_SEMANTIC_EXPRESSIVENESS |
| Typed null/omitted due date and full B01 enum/input-state validity across v1/v2/v3 | DOMAIN_SEMANTICS |
| Integrate #10/#43/#44 and field/singleton projections in one #45 contract checker | CONFORMANCE_VERIFICATION |
| Typed record success and numeric migration outcome in #45 checked signatures | COMPILER_LOWERING |
| Actual CLI argument/return/error and durable state view mapping beyond the closed command/flag table | INTERFACE_BINDING |
| Per-operation B01 boundary generation and emitted internal invocation facts | COMPILER_LOWERING |
| Independent challenge of a B01 internal event with public and raw durable endpoints | EXECUTION_OBSERVATION |
| Proof of complete durable effect coverage, byte-identical failure endpoint and intermediate-write behavior | DURABLE_STATE_GROUNDING |
| B01-specific contract digest, operation/persistence IDs and artifact-to-operation association | PROVENANCE |
| Versioned v1/v2/v3 state-view mapping and explicit migration outcome/version relation | EVOLUTION/MIGRATION_METADATA |
| Observable priority rank beyond domain/round-trip/exact HIGH | BENCHMARK_UNDERSPECIFICATION |
| All-input/all-reachable-state implementation correctness | UNKNOWN |

**Semantic adequacy:** NOT ESTABLISHED; the migration count is a concrete
provisional core gap, and the full typed composition has not been integrated.
**Grounding adequacy:** NO for R5.7's B01 same-invocation challenged evidence;
independent public/durable endpoints and pinned artifact exist, but internal
attribution does not. **Observed conformance:** NOT EVALUATED under #45 for
B01; selected frozen acceptance/public observations pass on the pinned B01
snapshot. **Universal implementation correctness:** NOT ESTABLISHED. A
contract's universal scope, even if later achieved, cannot prove that all
executions obey it from these finite cases. The result is not a claim about
Conventional structural similarity, generated-code readability, names or
control-flow style; only observable relations and checked machine identity
matter.

## 7. Construct accounting, next action and verification

Historical numbered inventory remains **45 raw**, categorized: core/domain
13 (#1-8,#13-14,#25-27), collection 11 (#9-12,#15-20,#43), state 4
(#21-23,#44), abstract operation 1 (#45) = **29 candidate core**; observation
3 (#24,#30-31), verification 2 (#32,#36), evidence/testing 5 (#28-29,#33-35),
evolution/link 5 (#37-40,#42), administration 1 (#41) = **16 non-core**.
R5.7's separate 12 unnumbered machinery responsibilities remain; this restart
adds **two unnumbered responsibilities**: B01 public command/argument adapter
metadata (binding) and checkpoint-pinned application snapshot extraction
(provenance). Raw numbered count is still 45, candidate core 29; expanded
responsibility inventory is **59 = 45 + 12 + 2**. Test cases and this research
record are evidence/administration, not constructs. No #30 was added.

**Recommendation:** Focused review of numeric outcome/cardinality and typed
full-schema integration against the *entire* B01 baseline; test the proposed
exact-selection insertion/completion frame on arbitrary populations without
introducing a task-specific primitive. Separately design checked B01 CLI and
storage-state lowering with per-operation provenance/internal events, then
challenge them independently and only then run the case verifier. Do not infer
an ordinal comparator from ambiguous language. Keep R5.2.2 authoritative,
Phase 5C paused, B17 unexposed/unclassified and the format UNFROZEN.

Verification (repository root, Python standard library): complete benchmark
harness **133 tests OK**, application/compiler **31 OK**, focused architecture
**6 OK**, grounding **10 OK**, R5.8 semantics **3 OK**; focused R5.9 adapter
**5 OK**, including the original frozen B01 regression against the pinned B01
snapshot (**5 passing methods, 2 B02 skips, zero failures**). The harness
also exercises the other semantic relation prototypes. `git diff --check`
exited 0, with no whitespace diagnostics for tracked changes; three new files
were separately checked via `git diff --no-index --check -- NUL <file>` with no
whitespace diagnostics (the new-file difference itself returns exit 1).
Git separately warned about future LF-to-CRLF working-copy conversion for the
three tracked docs and the three new files; these are not test or whitespace
failures. All counts are development evidence, not adequacy/proof metrics.

R5_9_B01_MULTIPLE_GAPS
