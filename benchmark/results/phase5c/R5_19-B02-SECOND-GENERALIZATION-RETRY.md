# R5.19 — Second frozen B02 generalization retry (prospective, 2026-10-02)

## Pre-lock suite and historical test lifecycle

The R5.17 result `R5_17_B02_LOWERING_STILL_INCOMPLETE` remains the correct
classification of its locked lowerer and its result artifact is unchanged.
`benchmark/harness/test_b02_retry_r5_17.py` previously asserted that the
*current* lowerer rejects the R5.17 migration slice. R5.18 intentionally
superseded this limitation. The executable assertion now checks that this
historical contract slice types on the current lowerer; this does not rewrite
the historical observation or claim full B02 generation. Only test lifecycle/
expectation changed; no compiler semantics changed to restore the suite.

Before the following lock: full benchmark harness **164 run, 164 passed, 0
failed**; application/compiler suite **31 run, 31 passed**; focused R5.10–R5.18
pattern **31 run, 31 passed**; `git diff --check` exited 0. Git separately
warned of prospective LF→CRLF conversion of the changed historical test; this
is not a check failure.

## Experimental lock — recorded before R5.19 B02 processing

HEAD `c9b9e1a8b9b2c0befb4fdf9b02f734794e919fdd`; identities below are
working-copy Git blob hashes (`git hash-object`), including the pre-lock test
lifecycle edit. This lock freezes the semantic inventory, general lowering and
planner, runtime, binding, provenance, grounding and conformance machinery for
this retry. No repair of these components is authorized during R5.19.

| Component / path | Locked Git blob |
| --- | --- |
| Candidate 30 inventory `R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md` | `d6dc362ee73bfcc26b2b7a8792e1864cd59db8cf` |
| Semantic prototype `benchmark/semantic/prototype.json` | `b9df7de07e268cc6b535be95134f37b16eaff4a8` |
| Semantic relations `benchmark/semantic/invariants.py`, `invariant-fixtures.json` | `1b2fd5e90e627f78c8236d11229a8b3130e6919c`, `15e0086ffa219a3d7ad7ef74acf1122b06afc2c3` |
| Typed checker `benchmark/semantic/typed_lowering_r5_12.py` | `cc09b11d29491d4686404e63db1a571bb6983b58` |
| General lowerer AND canonical relation planner `benchmark/semantic/generative_r5_13.py` | `48e076558070c5bfd5383e19b57e83f2ce41bd24` |
| Generic runtime `benchmark/semantic/generative_runtime_r5_13.py` | `6e03bc8d0a3d57dbaea680aa2b6c4d65a4757dc0` |
| Binding metadata `benchmark/semantic/binding.py` | `32ef8908b294945a6b52e94f693315a6edb86af1` |
| Provenance / independent observation / grounding / semantic case verifier `benchmark/semantic/generative_evidence_r5_13.py` | `914f8c8bf74235338cdb2000fd43a896c3245c15` |
| Grounding framework `benchmark/semantic/grounding_r5_7.py` | `d69847ced09c3d254b0586a66ae3a4fc237d1dca` |
| Conformance framework `benchmark/semantic/conformance.py` | `39501dde66412585e5b5c7b5f25cdc75395d387c` |
| Historical migration-slice test (after lifecycle edit) | `8cf94a08d24e2b21bd19cf78eb63ea8334232a76` |
| Frozen `B02.md`, `B01.md`, `baseline.md` | `d12654997f15a2774ff3b4914ec56dab87f85440`, `07391ea8a41ec79b49f20ca5258fe8b46e5d4a8c`, `8025876f8444591bc7c1ee0ac50f120164374c90` |
| Frozen `regression.py`, `profiles/B02.json`, `capabilities/B02.json` | `8bfa6ba450c59cfc23d34c7560b80fb4c5b1076b`, `b01e779ff75db1d31dca1ba2f242b592a5fc7183`, `313d8fdac17ca13877146464e9097278b89a5989` |

R5.2.2 remains historical benchmark authority. The R5.19 experiment starts
after this lock; no B02-specific compiler, runtime or verifier modification is
permitted.

## Frozen reconstruction and unchanged semantic contract

Frozen authority is `benchmark/requirements/B02.md`, inherited `B01.md` and
`benchmark/baseline.md`, plus `benchmark/harness/regression.py` with the frozen
`profiles/B02.json` and `capabilities/B02.json`; no input or historical R5.2.2
checkpoint changed. Direct comparison with R5.14's clause table and R5.17's
relation set confirms the **same candidate-level expressibility**, not an
integrated accepted B02 AST: ordered repeated flags, per-value trimmed-nonblank
guard, case-sensitive first-occurrence stable uniqueness, omitted `[]`, typed
task-valued outcomes, fresh full-record insertion and preservation, all
versioned legacy defaults and #30 migration count, and inherited filtered/
ordered reads, lifecycle mutations, invalid-state/error and no-write behavior.
No unexpected `CORE_SEMANTIC_GAP` appeared; ambiguous invalid-input precedence
and malformed stored-tag details remain benchmark-underspecified as in R5.14.
Core candidate inventory remains **30**, historical raw entries **46**, no #31.

The **complete intended semantic relation set** is the one specified in
R5.17: `create` branches on title/priority/due validity and every trimmed tag
being nonblank, returns `invalid_tag` with unchanged bytes on blank input, or
builds a full typed task with `tags = stable_unique(map(trim(input.tags)))`,
unique fresh ID, UTC creation time, inherited field defaults and an exact
framed insertion into current v4 records. `list` returns the full population
ordered `(created_at,id)`; `list-high` selects exactly HIGH; `list-overdue`
selects pending dated rows strictly before the clock, then orders. `complete`
updates one pending task while retaining tags; `delete` removes and returns one
entire task; failure alternatives preserve state. `migrate` v1/v2/v3 → v4
retains present fields, defaults *each missing* priority to NORMAL, due_date to
null, tags to `[]` on the **same uniquely keyed legacy population**, relates
result `{migrated: cardinality(pre.records)}` and sets version 4; current or
absent migration returns zero. Legacy reads signal `migration_required` with
no write. JSON CLI transport, exact field shapes, durable file, failure exit,
clock and fresh-ID binding remain inherited obligations. This semantic target
is not reduced to the emitter's accepted subset.

## Locked retry, lowering gate and mandatory halt

The R5.19 focused test uses the **unchanged R5.17 migration-slice serialization**
(three typed defaults on the same `records` collection, post-version 4, typed
pre-population cardinality). `typed(slice)` now succeeds and `render(slice)`
emits all three fields through the R5.18 canonical plan. Thus the exact R5.17
`UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations` rejection
has been removed without any B02-specific compiler modification. This is
**slice generation only**: the historical probe has a v1-only guard and
otherwise-current branch, lacks v2/v3/absent behavior and every create/read/
mutate/CLI obligation, and must not be represented as a B02 candidate.

The next faithful frozen obligation sampled is a *read-only* full-B02-row
`list` on version 4 with `order(pre.records, keys=[created_at,id])` and a
legacy `migration_required` no-write alternative. The locked typed checker
accepts this relation and its typed sequence-of-record outcome. The same
general `render` path then raises exactly
`UNSUPPORTED_LOWERING_CAPABILITY: order` at `generative_r5_13.expression`.
R5.12's `_compile` interprets this typed relation for supplied tuples, but the
R5.13–R5.18 generator does not emit its behavior. This is a **valid semantic
relation with unsupported generation**, not `CONFLICTING_RELATIONS`,
`INVALID_SEMANTIC_COMPOSITION` or a surprise `LOWERING_ERROR`. The lowering
gate is **VALID_SEMANTICS_UNSUPPORTED_LOWERING**. The integrated frozen B02
contract is not serializable/generatable by the current bounded generator;
passing the migration slice cannot stand in for feeding a full integrated AST.
No later B02 operation was attempted after this decisive gate. Mixed collection
transforms (notably frame plus default on one collection) remain explicitly
unsupported; they were not reached as a new observed B02 rejection and were
not broadened. **HALT: no post-lock repair.**

## Authority, candidate, acceptance, grounding and conformance

Inspection of the locked lowerer, canonical planner, generic runtime and case
verifier shows generic field/path dispatch and no B02/task-specific branches or
frozen fixture constants in that path. The slice's migration fields and count
originate in its typed contract, but this does **not** pass the source-authority
gate for complete B02: there is no generated ordered list and no complete B02
behavior to audit. No manually authored normalization, insertion, migration,
task result or task-specific binding was substituted. The R5.11 handwritten
B01 target and historical Conventional application are not candidates.

**Distinct R5.19 B02 candidate:** not authorized/created; semantic identity,
generated B02 operation identities, candidate provenance and artifact integrity
data **N/A**. The in-memory migration-slice `render` bytes are not a complete
candidate or an instrumented acceptance target. **Frozen applicable B02
acceptance:** not run; passed **N/A**, failed **N/A**, skipped **N/A**. No B02
internal execution event, independent public-call/durable observation, or
provenance challenge exists for an R5.19 candidate; representative normalization,
record outcome, insertion, defaults and migration cases are **not reached**.
`GROUNDED + CONFORMANT`, `GROUNDED + NON_CONFORMANT`, `GROUNDING_FAILED` are
**N/A**. No acceptance failure or grounding-boundary failure is classified;
the exact failure layer is **general generative lowering of typed order**.

## Blocker transfer and general-capability matrix

R5.17 locked the one-owner-per-collection checker and stopped on its second
default. R5.18 independently developed an N-way compatible-default plan on
instrument inventories (with joint verification). At this separately locked
R5.19 retry, the *same* R5.17 B02 migration slice passes typed checking and
renders all defaults without B02-specific compiler work. **The overlap
capability transfers to a B02 migration slice**, while the *whole frozen B02*
still stops at ordered list lowering. Do not infer acceptance or broader
operation transfer from this targeted compiler observation.

| General capability / independent origin | Actual R5.19 B02 transfer |
| --- | --- |
| Ordered normalization ← R5.15 | Available in generic emitter; no full B02 create generated; **not demonstrated for B02**. |
| Record-valued outcomes ← R5.15 | Migration slice's `{migrated: cardinality(...)}` renders; **slice only**, not a task-valued B02 result. |
| Bounded keyed default ← R5.15 | Three typed defaults render on B02 legacy-row shape; **slice only**. |
| Framed insertion ← R5.16 | Not reached in a complete B02 create; **not demonstrated for B02**. |
| Durable version transition ← R5.16 | Slice renders `post_equals(schema_version,4)`; no B02 durable execution; **slice only**. |
| Cardinality-derived migration outcome ← R5.16 / #30 | Slice renders cardinality of pre-records; no B02 execution; **slice only**. |
| N-way compatible defaults ← R5.18 | **Yes, B02 migration slice types and renders**; not full v1/v2/v3 migration. |
| Ordered task-list generation ← existing candidate #43, validating R5.12 | **No**; locked generator rejects `order`. |

Demonstrated reuse update: one B02-shaped migration **lowering slice** now
demonstrates transfer of the independently developed compatible-default plan;
**0 complete B02 operations**, **0 grounded B02 calls**, **0 frozen B02
acceptance methods** against an R5.19 candidate. Do not count the slice as a
frozen-request executable achievement. R5.14 remains semantics-valid/lowering-
insufficient; R5.17 remains semantics-valid/overlap-blocked under its lock;
R5.18 remains independently validated relation composition. None of their
historical artifacts or conclusions is amended.

## Decision and next recommendation

Post-lock focused `python -m unittest discover -s benchmark/harness -p
test_b02_retry_r5_19.py -v`: **1 run, 1 passed**, exercising both overlap
transfer and the exact `order` rejection. No frozen B02 acceptance was run
because generation was not authorized. Final `git diff --check` and
`git diff --no-index --check -- NUL` on each new R5.19 file exited 0;
working-copy Git LF→CRLF notices on edited/new files were line-ending
warnings, not whitespace or test failures. Rechecked locked general lowerer,
runtime, typed checker, binding, observer/verifier and prototype hashes against
the pre-attempt identities: unchanged.

Exact next recommendation: preserve this locked failed retry, then study
**generic ordered sequence-of-record outcome generation** on independent
non-task domains in a separately versioned compiler experiment, with semantic
mutations, source-authority audit and independent observation; investigate
remaining lifecycle/CLI binding and mixed-transform limits independently
before any separately authorized frozen B02 retry. No R5.19 compiler repair
or B03 activation follows. Phase 5C does not automatically advance to B03;
B17 remains unexposed and unclassified, the semantic-first format remains
globally unfrozen, and R5.2.2 remains historical benchmark authority.

UNIVERSAL_IMPLEMENTATION_CORRECTNESS_ESTABLISHED = NO

R5_19_B02_NEXT_LOWERING_GAP
