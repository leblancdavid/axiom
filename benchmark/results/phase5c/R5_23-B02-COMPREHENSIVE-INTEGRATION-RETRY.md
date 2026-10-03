# R5.23 — Comprehensive frozen B02 integration retry (prospective, 2026-10-03)

First comprehensive B02 retry performed **after** the entire known B02
lowering-coverage backlog received independent generative evidence (R5.22,
`R5_22_KNOWN_LOWERING_COVERAGE_COMPLETE`). One separately locked attempt
against the unchanged current compiler; no repair after lock. R5.2.2 remains
historical benchmark authority. Phase 5C does not advance to B03; B17 remains
unexposed and unclassified; the semantic-first format remains globally
unfrozen; universal implementation correctness is not claimed. Candidate core
semantic constructs remain **30**; no #31 was added and no existing semantic
definition was changed.

**Headline result.** The locked general lowering pipeline now executes B02's
create-success (external identity + clock + fallback + framed insertion),
lifecycle replacement and removal over the versioned envelope, N-way keyed
migration defaults with cardinality-derived count, migration-required legacy
reads, and the ordered read on string-typed rows — each grounded and
semantically conformant on B02-shaped data, and a twelve-branch multi-command
B02-shaped document serializes, renders and runs as **one** program. But the
**complete** B02 command document fails whole-program serialization at the
typed-validation stage, and the failure is a previously unidentified class:
**type integration between independently validated capabilities**. The
semantically correct `instant` creation timestamp is not an admissible
ordering key (`non-orderable key`), while the string-typed column that does
order cannot receive the `instant`-typed clock (`outcome payload type
mismatch`). The same independence pattern repeats: `before` binds only plain
instant operands, so overdue cannot null-guard a `nullable`/`optional`
due date; guard predicates cannot compare an *optional* record field with a
required-typed literal; one contract admits one state shape, so version-
dependent row typing (v2/v3 legacy ∩ v4 current) and the v1 bare-list →
envelope promotion are unlowerable; and input-domain validity (`provided`,
"well-formed instant") has no relation node, so `invalid_due_date`/
`invalid_state` cannot become typed failure branches. The frozen
error-envelope/positional-CLI/missing-file transport was separately confirmed
absent — as R5.22 explicitly deferred. Generation gate:
**KNOWN_CAPABILITY_FAILED_TO_COMPOSE via PREVIOUSLY_UNKNOWN_LOWERING_CAPABILITY**;
application execution HALTED before candidate creation, per protocol.

## 1. Pre-lock repository checkpoint

R5.22 had in fact been committed before this retry began (the task brief's
"reported as not committed" was stale): HEAD
`3438122610efb850b481352bf5b18a34c2ecc813` ("r5.22", author David Leblanc,
2026-10-03 05:55:29 -0700) contains the full R5.22 source/test/documentation
change set (`git show --stat`: 12 files, +1527/−82, including
`capability_boundary_r5_22.py`, `test_lowering_coverage_r5_22.py` and the
R5.22 result artifact). `git status` at R5.23 start: **working tree clean**,
`main` in sync with `origin/main`. Because the exact compiler state to be
tested was already a clean committed checkpoint, no new commit was required or
created; recording the existing commit plus component hashes satisfies the
checkpoint requirement honestly.

## 2. Verification baseline (pre-lock, all green)

- Full benchmark harness: **224 run, 224 passed, 0 failed** (104.3 s).
- Application/compiler suite (`tests/`): **31 passed**.
- `python -m air_compiler.cli validate air/task_manager.json`: `Lykoi validate: ok`.
- `python -m air_compiler.cli safety air/task_manager.json`: 0 capability
  violations, 0 invalid transitions (6 invariants, 1 state machine, 1
  protected resource; evidence RUNTIME_ENFORCED 5, STRUCTURALLY_GUARANTEED 1).
- Focused R5.5–R5.22 suites, all OK: R5.10 4, R5.11 4, R5.12 3, R5.13 5,
  R5.15 6, R5.16 4, R5.18 4, R5.20 18, R5.17 1, R5.19 1, R5.21 14, R5.22 27,
  R5.7 grounding 10, R5.5 architecture 6, R5.8 3.
- `git diff --check`: exit 0.
- Python 3.14.3; no third-party dependencies.

**Pre-lock lifecycle updates:** none. Nothing in the current suite was newly
obsolete by R5.22 work (R5.22 itself retired the four frontier-rejection
expectations under the established precedent); no historical artifact or
conclusion was rewritten.

## 3. Experimental lock

Identities are working-copy Git blob hashes (`git hash-object`) at the clean
HEAD; sha256 values are additionally pinned in the R5.23 suite's
`LOCK_DIGESTS` and re-verified post-experiment (§23).

| Component / path | Locked Git blob |
| --- | --- |
| Commit | `3438122610efb850b481352bf5b18a34c2ecc813` |
| Canonical application model `air/task_manager.json` | `2c9a51cc2993462bfcadb34d09b469d081135d75` (unchanged since R5.21) |
| 30-candidate inventory `R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md` | `d6dc362ee73bfcc26b2b7a8792e1864cd59db8cf` |
| Vocabulary ledger `R5_4-SELECTION-VOCABULARY-LEDGER.md` | `662d37683b7840be10840e23eb914aa44cf5d87e` |
| Semantic prototype `benchmark/semantic/prototype.json` | `b9df7de07e268cc6b535be95134f37b16eaff4a8` |
| Semantic relations `invariants.py` | `1b2fd5e90e627f78c8236d11229a8b3130e6919c` |
| Validating checker `typed_lowering_r5_12.py` | `96b12e34a91ee4839e2e322aad0f81579530a812` |
| General lowerer + relation planner + ordering planner `generative_r5_13.py` | `8e2364da17cfe3a66f5ffd5262a7710955596a65` |
| Generic runtime `generative_runtime_r5_13.py` | `51319880d44d36917b4017fed53f583e3d46390c` |
| Capability boundary `capability_boundary_r5_22.py` | `47140dea536238e6b43cce67bf8e7601fd831616` |
| Binding metadata `binding.py` / contracts `contracts.py` | `32ef8908b294945a6b52e94f693315a6edb86af1` / `20299697281ac743b66599367673e3e625fd7fc2` |
| Cardinality `cardinality.py` | `c4d38f0c1c9d31f5cb3e165f5c8ce2d29e66e6e6` |
| Provenance/grounding challenge/semantic case verifier `generative_evidence_r5_13.py` | `0a19f6d95008044120ada8dc0b809c43ce6bb2bd` |
| Grounding framework `grounding_r5_7.py` / conformance `conformance.py` | `d69847ced09c3d254b0586a66ae3a4fc237d1dca` / `39501dde66412585e5b5c7b5f25cdc75395d387c` |
| Format/scenario channel `format.py` | `ba4190fca6b1903206e228a83a13fdc6826b9e97` |
| Frozen `B02.md`, `B01.md`, `baseline.md` | `d12654997f15a2774ff3b4914ec56dab87f85440`, `07391ea8a41ec79b49f20ca5258fe8b46e5d4a8c`, `8025876f8444591bc7c1ee0ac50f120164374c90` |
| Frozen `regression.py`, `profiles/B02.json`, `capabilities/B02.json` | `8bfa6ba450c59cfc23d34c7560b80fb4c5b1076b`, `b01e779ff75db1d31dca1ba2f242b592a5fc7183`, `313d8fdac17ca13877146464e9097278b89a5989` |
| Prior retry/coverage tests `test_b02_retry_r5_17.py`, `test_b02_retry_r5_19.py`, `test_b02_retry_r5_21.py`, `test_lowering_coverage_r5_22.py`, `test_ordering_lowering_r5_20.py`, `test_relation_composition_r5_18.py` | `8cf94a08d24e2b21bd19cf78eb63ea8334232a76`, `c9acf77a0808acb4ebc0382ee69709a0326fb0d0`, `bd2fd46f2ff6ebe2ba428eb856b804bf0923db42`, `2a92ce8f9a9e0ccdb1d7cdaa6e325c80e1a31bac`, `209a1bd3e554a012610172711b4d9f596209e0e8`, `da1e9f83955d370ce98f5eec05fc06707544b432` |

Post-lock addition: the R5.23 evidence file
`benchmark/harness/test_b02_integration_r5_23.py` (this retry's test/evidence
collection; assembly, observation and grounding only — it implements no
application behavior and changes no expected semantics). **No locked component
changed** (§23 integrity re-check).

## 4. B02 semantic adequacy confirmation (Part 1)

Reconstructed directly against R5.14 §2, R5.17's relation set, R5.19's frozen
reconstruction and R5.21 §4/§5. Every frozen B02 obligation, including the
inherited baseline/B01 accumulation exercised by the frozen
`regression.py` + `profiles/B02.json` + `capabilities/B02.json` configuration,
re-classifies as before:

| Obligation | Classification | Existing candidate semantics |
| --- | --- | --- |
| Repeated `--tag` flags; trim; every trimmed value nonblank; `invalid_tag` with no new task and unchanged bytes | EXPRESSIBLE_EXISTING | #3/#4/#6, #13/#14/#17, #21–23 guards, #45 typed alternatives |
| Case-sensitive first-occurrence deduplication `stable_unique(map(trim(values)))`; `tags` array on every returned task; `[]` on omission/migration | EXPRESSIBLE_EXISTING | #15/#16, #21–23, #44/#45, fallback obligation |
| Fresh full task inserted exactly once, all inherited fields, unrelated rows preserved | EXPRESSIBLE_EXISTING | #1–6, #21–23 exact frame, #45 record outcome |
| Fresh ID and UTC creation instant; omitted-input defaults (`NORMAL`, `null`, `[]`) | EXPRESSIBLE_EXISTING | #24/#25 clock/instant + fresh-identity as inherited binding obligations; fallback |
| `(created_at,id)` ordering; exact HIGH selection (CRITICAL excluded); strict-past dated pending overdue selection | EXPRESSIBLE_EXISTING | #43, #10–12, #25/#27 |
| `complete` pending→completed preserving every field incl. tags, full return; `delete` removing exactly one target, full return; failure branches with durable no-write | EXPRESSIBLE_EXISTING | #21–23, #44/#45 keyed transitions, #7/#8 |
| Explicit v1/v2/v3→v4 migration: keyed defaults only for *missing* fields, present fields retained, version set, `{migrated: cardinality(legacy)}`; current/absent migrate 0; legacy reads `migration_required` without write | EXPRESSIBLE_EXISTING | #44 N-way, #30, #21–23 versioned applicability, #45 |
| JSON transport, exact field shapes, error envelope/exit codes, missing-file→`[]`, one shared store, clock/ID binding | EXPRESSIBLE_EXISTING (contract/binding layer) | inherited binding/adapter obligations (R5.14 §2; semantic/README "benchmark-boundary mechanics") |
| Precedence among independently invalid create inputs; whitespace taxonomy beyond trimming; malformed persisted-tag taxonomy | BENCHMARK_UNDERSPECIFIED | unchanged from R5.14/R5.17/R5.19/R5.21 |

No `UNEXPECTED_SEMANTIC_GAP` at the representation level; no construct #31.
Count remains **30** (raw historical inventory 46). What R5.23 newly exposes
is *not* a representable/unrepresentable question: the failing items below are
lowering/type-integration capabilities over existing semantics (the typed
instant #25 exists; it is not orderable; the before #27 exists; it is not
null-safe; the guard #45 exists; it cannot test optional-field membership).
Per protocol this does not block assembly — assembly was attempted (§5–§6) and
the classification stands.

## 5. Complete B02 semantic source (Part 2)

A single authoritative command document (`b02.application` / `r5.23`) assembled
from existing constructs only, keyed on `input.request`, with the
legacy-permissive envelope state required by the migration obligation
(row `LEGACY_ROW`: required id/title/description/status, **instant**
`created_at`, **optional** priority / due-date(`optional nullable instant`) /
tags(`optional sequence string`); state `{schema_version: integer, records:
sequence<LEGACY_ROW>}`; shared input record with optional per-command fields),
covering **all** frozen obligations — 15 branches:

1. `migration_required` — sv≠4 ∧ request∈{list,list-high,list-overdue} (or-encoded
   via #8 `not(and(not…))`), preserve;
2. `listed` — sv=4, `order(pre.records, [created_at, id])` (#43), preserve;
3. `listed_high` — exact HIGH selection (#10–12) ∘ ordering;
4. `listed_overdue` — pending ∧ due≠null ∧ `before(item.due_date, external
   utc_clock)` (#25/#27) ∘ ordering;
5–7. `invalid_title` / `invalid_tag` / `invalid_priority` (#13/#14/#17 guards;
   priority membership expressed by `fallback(priority,'NORMAL')` equality-chain
   conjunction — a genuine compositional success: the supplied-vs-omitted
   distinction folds into the default being a valid member);
8. `created` — full typed task record (#1–6): `external` fresh ID +
   `external` UTC clock, `fallback` defaults (NORMAL/null/[]),
   `stable_unique(map(trim(tags)))`, exact-frame insertion (#21–23);
9. `completed` — keyed envelope `replace_field` (relation set) with
   sv=4 ∧ exactly-one-pending cardinality guard, outcome `sole` over `post`
   (#45 post/projection);
10–11. `invalid_transition` / `task_not_found` (cardinality-1 vs 0 select guards);
12. `deleted` — keyed `remove` relation, outcome `sole` over `pre`;
13–14. `migrated` — three N-way keyed defaults + `post_equals` version 4 over
    the same legacy population, `{migrated: cardinality(pre.records)}` (#30);
    `current` — zero-count preserve at sv=4;
15. `invalid_request` — the single unconditional final branch.

This is the authoritative behavioral source for the attempted candidate; no
B02 behavior was authored anywhere else.

## 6. Whole-program lowering result (Parts 3–4)

Fed through the locked pipeline (`typed` → relation planning → `render` →
`generate`):

- **Decisive whole-program failure:** `typed(complete-document)` raises
  `ValueError: non-orderable key` at branch 2 (`listed`). The ordering
  planner accepts only `string`/`integer` keys
  (`generative_r5_13.ORDER_KEY_TYPES`); the faithful B02 row types
  `created_at` as **`instant`** because the creation value is the `instant`-typed
  clock capability. Down-typing the column to `string` reopens the other side
  of the same junction: `external('utc_clock')` compiles to `instant` and the
  create outcome/row then rejects with `outcome payload type mismatch`
  (asserted both directions in `test_clock_and_ordering_type_domains_are_disjoint`).
  The two independently validated capabilities (R5.20 ordering, R5.22
  external/clock) meet at one field type and neither interpretation is
  admissible for the other — the first-failure classification is therefore
  **PREVIOUSLY_UNKNOWN_LOWERING_CAPABILITY** (typed-instant ordering-key
  integration), not a re-manifestation of any R5.22 backlog row.

- **Branch isolation matrix** (each branch + final otherwise, legacy-permissive
  state; recorded by `test_branch_matrix_records_which_compositions_reach_serialization`):

| Branch | Serialization outcome (exact diagnostic) |
| --- | --- |
| migration_required | **SERIALIZES + RENDERS** |
| listed | `non-orderable key` |
| listed_high | `equality type mismatch` (optional `item.priority` vs required string literal) |
| listed_overdue | `equality type mismatch` (optional due-date vs null test) |
| invalid_title / invalid_tag / invalid_priority | **SERIALIZES + RENDERS** |
| created | `outcome payload type mismatch`; with current-typed outcome instead: `framed record type mismatch` (all-present constructed record vs optional-permissive row) |
| completed / invalid_transition / task_not_found / deleted | **SERIALIZES + RENDERS** |
| migrated / current | **SERIALIZES + RENDERS** |
| (invalid_due_date, invalid_state) | no admissible guard node exists: `unsupported relation: is_valid_instant` / `unsupported relation: provided` |

- **Additional decisive compositions** (each asserted in the suite):
  `before` over a *required-nullable* instant (`due_date: {nullable:'instant'}`)
  rejects `before requires two typed instants` — the overdue obligation is
  unlowerable in both row typings; keyed defaults over an all-required current
  row reject `invalid default field or type` — one contract's single state
  shape cannot be version-dependent; a v1 bare-list state *does* type and
  render the three-default transition but `post_equals` rejects
  `invalid post equality` — a sequence state cannot record the version, and
  no one state declaration spans bare-list→envelope promotion.

- **Maximal composable integrated program:** a twelve-branch document over the
  all-required current row (create guards + created + un-ordered list +
  exact-HIGH list-high + completed + invalid_transition + task_not_found +
  deleted + migrate-current + migration_required + invalid_request) **types,
  renders and executes as one multi-command program** through the locked
  pipeline (`test_maximal_integrated_document_types_and_renders`; transport
  probes drive this same generated program). This upgrades R5.21's per-slice
  transfers to a genuine multi-operation composition, while the omitted
  obligations (ordered reads on faithful types, overdue, legacy migrate,
  due-date/state validity) remain the recorded gate failures.

- **Generation gate:** `KNOWN_CAPABILITY_FAILED_TO_COMPOSE` in the sense that
  every failed junction involves capabilities with independent evidence, but
  the operative classification is **PREVIOUSLY_UNKNOWN_LOWERING_CAPABILITY**:
  no complete candidate was generated; **application execution HALTED**; no
  repair attempted. AST integration *within the serializable subset* succeeded
  (multi-operation single program); the frozen CLI/clock/ID **binding
  integration** additionally fails (§15 transport), matching R5.22's explicitly
  deferred interface items.

## 7. Source-authority audit (Part 5)

Conditional on a complete candidate: **not applicable — none was generated.**
For what was generated, the audit path semantic source → general lowering →
generated behavior holds: the R5.22 contamination audit
(`test_changed_modules_contain_no_task_b02_or_benchmark_vocabulary`,
`test_lowerer_contains_no_task_b02_or_benchmark_vocabulary`) re-passed inside
the green 243-test harness against unchanged locked blobs (§23); every B02
name, field, version constant and fixture value in this experiment arrives
only through contract data; the lowerer/planner/runtime contain no task branch;
no B02 behavior was authored in any adapter (the transport tests exercise only
rejections, and the missing transport is itself the finding).

## 8. Candidate identity (Part 6)

**NOT CREATED** — generation gate not passed, so no R5.23 instrumented B02
candidate exists: source semantic identity = §5 document digest set (per-contract
sha256 recorded in each disposable `provenance.json`); compiler checkpoint = §3;
generated-artifact/operation identities, provenance and integrity: **N/A** for a
candidate. Disposable slice programs in temporary directories are not
candidates (R5.21 §11 precedent). Historical candidates/checkpoints untouched.

## 9. Complete frozen B02 acceptance matrix (Parts 7–8)

The applicable frozen profile is `regression.py` with `--achieved B01,B02`
(profile `B02.json`): seven accumulated case methods. **None executed:**
application execution halted at the generation gate; no complete candidate
existed to run; the frozen oracle, profile, capability file and requirements
were used read-only and re-hashed unchanged (§3, §23).

| Frozen case | Outcome | Reason |
| --- | --- | --- |
| test_baseline_lifecycle_filters_failures | BLOCKED | no generated candidate (halting at §6) |
| test_baseline_migration_corruption | BLOCKED | ditto; `invalid_state` branch additionally unlowerable (§6) |
| test_baseline_overdue_fixture | BLOCKED | ditto; overdue composition rejected (§6) |
| test_b01_priority_and_regression | BLOCKED | no candidate |
| test_b01_historical_priorities | BLOCKED | no candidate; v1/v2/v3 multi-shape storage unlowerable in one contract (§6) |
| test_b02_tags_and_failure | BLOCKED | no candidate; ordered/complete/delete slices individually grounded (§10) |
| test_b02_explicit_migration | BLOCKED | no candidate; v3∩v1 single-document typing (§6) |

PASSED 0, FAILED 0, SKIPPED 0, BLOCKED 7 — **not** zero-pass evidence; these
are protocol-mandated non-executions. Test isolation (Part 8): the frozen
harness's per-method fresh-temporary-directory isolation was preserved by
construction (nothing ran); slice probes are case-scoped in temp directories,
one failure never contaminating another (all 13 slice runs in this suite are
independent and each fully grounds, §10).

## 10. Grounding matrix (Part 9)

Every executed B02-shaped invocation ran the generated program as a real
subprocess behind the provenance digest challenge; internal event matched
independently captured stdout and durable file readback; `attempted_write`
obligations checked against bytes:

| # | Operation (contract, branch) | Externals | Grounded | Notes |
| --- | --- | --- | --- | --- |
| 1 | create-success, controlled provider (`gen-7`/CLOCK) | recorded | **YES** | full 8-field record incl. normalized tags |
| 2 | create-success, **real** provider | recorded, `validate_logged` true | **YES** | returned == persisted == logged |
| 3 | blank-tag `invalid_tag` | none used | **YES** | bytes identical, `attempted_write false` |
| 4 | blank-title `invalid_title` | none | **YES** | ditto |
| 5 | `invalid_priority` (`BANANA`) | none | **YES** | ditto |
| 6 | `completed` (envelope replace_field + post `sole`) | none | **YES** | only target row changed |
| 7 | `deleted` (keyed remove + pre `sole`) | none | **YES** | target absent, unrelated rows preserved |
| 8 | `migrated` (3 N-way defaults + version + #30 count) | none | **YES** | v1 envelope → v4, `{migrated: 2}` |
| 9–11 | `migration_required` reads for list / list-high / list-overdue | none | **YES** | sv=1, byte-preserved, no write |
| 12 | ordered `list` (string-typed row, ties decided by id) | none | **YES** | storage order ≠ semantic order |
| 13 | exact-HIGH `list-high` ordered (string-typed row) | none | **YES** | CRITICAL excluded by equality |

Not executable at all (typed-failure before any run): faithful-typed ordered
`list`/`list-high`, `listed_overdue`, `invalid_due_date`, `invalid_state`,
v1-bare→v4 promotion.

## 11. Semantic conformance matrix (Part 10)

Evaluated against the same §5/§6 contracts that drove generation (independent
interpreter, not emitted Python): all 13 grounded runs above are
**GROUNDED + CONFORMANT**, including under the real provider (conformance
judges the *relation* — typed, fresh, returned==persisted==logged — never a
predetermined literal). GROUNDED + NON_CONFORMANT: 0. GROUNDING_FAILED: 0.
NOT_EXECUTABLE: the five faithful-typed obligations listed in §10. No frozen
acceptance outcome was substituted for conformance (none exists).

## 12. Acceptance-vs-conformance comparison (Part 11)

| Case | Frozen acceptance | Grounding | Conformance |
| --- | --- | --- | --- |
| any complete-B02 behavior | BLOCKED (no candidate) | slice-level YES (13) | slice-level CONFORMANT (13) |

No PASS-with-nonconformance or FAIL-with-conformance discrepancy can arise,
because acceptance never ran. The structural discrepancy this retry exposes
is different and explicitly classified: **slice-level success coexists with
whole-program failure** — 13/13 grounded-conformant B02-shaped slice executions
alongside a generation gate that rejects the complete document. Slice
conformance is therefore not acceptance evidence and not whole-program
composition evidence; no repair was attempted for either side.

## 13. Known-capability transfer matrix (Part 12)

Columns: independent evidence origin → reached in the **complete** program? →
generated (in the serializable/maximal program)? → executed → grounded →
conformed. "Reached in complete program" = the obligation serializes inside
the §5 whole-document.

| Capability ← origin | Complete program | Generated | Executed | Grounded | Conformed |
| --- | --- | --- | --- | --- | --- |
| Selection / read-only preserve ← R5.13 | yes | yes | yes | yes | yes |
| Ordered normalization ← R5.15 | yes | yes | yes | yes | yes |
| Record-valued outcome (#45) ← R5.15 | yes | yes | yes | yes | yes |
| Keyed missing-field default ← R5.15 | yes | yes | yes | yes | yes |
| Framed insertion ← R5.16 | **blocked** (complete doc) via row typing; yes over current-row doc | yes | **yes (R5.23 first)** | yes | yes |
| Durable version transition ← R5.16 | yes (envelope v→4) | yes | yes | yes | yes |
| Cardinality #30 ← R5.10/R5.16 | yes | yes | yes | yes | yes |
| Overlapping N-way defaults ← R5.18 | yes | yes | yes | yes | yes |
| Typed ordering #43 ← R5.20/R5.21 | **blocked** (instant key) | yes (string-typed) | yes | yes | yes |
| External ID/clock ← R5.22 | **blocked** jointly with ordering | yes | yes | yes | yes |
| Omitted-input fallback ← R5.22 | yes | yes | yes | yes | yes |
| `before` ← R5.22 | **blocked** (nullable operand) | yes (plain instant, R5.22) | no (B02 form) | no | no |
| `sole`/`project`/`post` projection ← R5.22 | yes (`sole` over post/pre) | yes | yes | yes | yes |
| Keyed `remove` ← R5.22 | yes | yes | yes | yes | yes |
| Envelope `replace_field` ← R5.22 | yes | yes | yes | yes | yes |
| Integrated AST ← R5.22 (single-op) | **partial** — 12-branch multi-command program runs; complete doc fails | yes (subset) | yes (subset) | yes | yes |
| CLI/public binding ← R5.22 `run_cli` | **no** — frozen argv form rejected; error envelope absent | no (frozen transport) | n/a | n/a | n/a |

**10 of 17 known capabilities transferred through the whole program executed,
grounded and conformant** (plus framed-insertion and ordering at
string-typed-subset level only); 4 fail only through *joint* composition
(ordering∩instant, external∩ordering, before∩nullable, AST-complete-vs-subset);
1 (`before`) has never executed in any B02 form; the CLI binding capability is
confirmed absent for the frozen transport.

## 14. Whole-program composition analysis (Part 13)

The failures are **composition-class**, not piece-class: every failing junction
involves two capabilities each already validated independently.

| Category (Part 13 vocabulary) | Observed junction |
| --- | --- |
| **Type-integration conflict** (relation-dependency conflict via shared field domain) | `instant` clock value ∩ `ORDER_KEY_TYPES=('string','integer')` for the same `created_at` field; constructed all-present record ∩ optional-permissive row in `exact_frame`/outcome typing |
| **Guard-predicate typing conflict** | optional/nullable record fields vs required-typed literals in `equals`; no optional-unwrap in predicate position (`fallback` binds only slot refs, not quantifier-bound `item` fields) |
| **State-frame conflict** | one state shape per contract vs version-dependent row requirements (v2/v3 vs v4) and bare-list→envelope promotion; `post_equals` impossible on sequence state |
| **Lowering-grammar expressiveness gap** | no `provided`/domain-membership predicate → `invalid_due_date` and read-time `invalid_state` cannot become typed failure branches |
| **Binding/transport gap (previously known, deferred by R5.22)** | positional command argv; repeated `--tag` vs per-field flags; `tasks.json` in cwd; missing-file→`[]`; exit-1 `{"error":CODE}` envelope; shared store across invocations |
| Runtime sequencing / outcome composition / persistence boundary | **no conflicts observed** where pieces serialized: the 12-branch program plans, renders and sequences correctly |

Why independent R5.22 evidence did not cover these: each R5.22 fixture chose
*permissive operand typings for its one relation* (string timestamps for
ordering, required `instant` fields for `before`, all-required rows for framed
insertion, optional-*input* refs for fallback) and closed its matrix row per
relation. No R5.22 case combined two evidence-grade type domains on one field,
no case put an optional/nullable **record** field into a guard, no case spanned
two storage shapes in one contract, and the "Integrated AST / CLI binding" row
was closed on **single-operation** evidence while the complete multi-operation
document was simultaneously excluded from the backlog as "B02 assembly" — the
exclusion carried the composition pressure but was never itself an open
backlog item. (§19 classification of the methodology blind spot.)

## 15. External/fresh-value analysis (Part 14)

Executed twice on B02-shaped create: controlled (`gen-7`/`2026-07-01T00:00:00Z`)
and real provider (uuid4 hex; wall-clock Z instant). In both: values are
typed (`validate_logged` re-checks the capability domain), **recorded**
(internal event `externals`), and **consistent** — the returned record's
`id`/`created_at` equal the persisted row's, which equal the logged supplied
values; the exact-frame freshness guard enforces absence-from-pre
structurally (R5.22) and the omitted `priority`/`due_date`/`tags` inputs took
their `fallback` defaults on the same invocation. Conformance judged the
relation (typed, fresh, returned==persisted==logged), never a predetermined
literal. No new external gap appeared; the *interaction* of externals with
ordering is §14's type-integration conflict.

## 16. Migration analysis (Part 15)

Integrated envelope migration (v1-shaped sv=1 records → v4) executed as one
program run: durable pre-version observed (sv=1, fields missing), overlapping
keyed defaults applied jointly to the same population (present `priority:
HIGH` and `due_date: null` preserved; `tags []` and missing `priority`/`due`
filled), post-version 4 written durably, migrated population independently
read back, `{migrated: 2}` derived via #30 `cardinality(pre.records)` and
grounded/conformant. Count semantics match the authoritative reading used in
R5.10/R5.16/R5.17/R5.21 (population of the applicable legacy set). The
migration_required no-write alternative executed grounded+conformant.
**Not** integrated: v2/v3 (require the *same* contract to also read current
all-required rows — §14 state-frame conflict) and v1 bare-list promotion
(transition serializes over a sequence state but the version cannot be
recorded and the shape cannot change).

## 17. Read-only analysis (Part 16)

Ordered `list` and exact-HIGH ordered `list-high` executed over a disposable
B02-shaped durable population whose storage order differs from semantic order
with a `created_at` tie decided by `id`: returned collections satisfy the
selection/order relations (conformance by exact multiset + nondecreasing keys,
per the R5.20 relation-not-stable interpretation), durable bytes identical,
`attempted_write false` grounded. Unordered `list`/`list-high` executed
*inside the maximal integrated program* (subset) also byte-preserving. No
sorted view was persisted anywhere. The faithful-typed ordered read itself is
blocked at generation (§6), so its read-only purity was established only on
string-typed rows — recorded honestly.

## 18. Mutation/framing analysis (Part 17)

`completed`: keyed envelope `replace_field` changed exactly the target row's
`status`, the full updated record (incl. `tags ['work','Work']`) returned via
`sole` over `post`, the two unrelated rows byte-equal in post, no extra
record. `deleted`: keyed `remove` dropped exactly the matched target (returned
whole, from `pre`), unrelated rows preserved. `created`: exact frame appended
exactly the constructed record; unrelated population preserved. Grounded and
conformant in all cases; R5.22's injection faults for replacement/removal
faithfully grounded-but-nonconformant remain the negative controls.

## 19. Failure/no-write analysis (Part 18)

`invalid_tag`, `invalid_title`, `invalid_priority` and `migration_required`
executed: typed failure outcome **and** durable state after failure both
grounded — byte-identical readback with `attempted_write false` (semantic
unchanged state observed physically: no attempted write, not merely an
unchanged value). The frozen *transport* half of failure behavior (exit 1 +
`{"error":CODE}` envelope) does not exist in the locked runtime and is
classified with binding, not semantics (§14 transport row). Branch precedence
among simultaneously invalid inputs remains `BENCHMARK_UNDERSPECIFIED`
(R5.14), untouched.

## 20. Unknown-gap classification (Part 19)

Capabilities newly exposed beyond the R5.22 known backlog:

1. **UNKNOWN_LOWERING_CAPABILITY** — typed-instant ordering-key integration
   (instant ∩ orderable domain). Decisive for the complete document.
2. **UNKNOWN_LOWERING_CAPABILITY** — null-safe/optional-aware guard predicates
   (`equals`/`before` over optional or nullable record fields; no optional-
   unwrap in predicate position). Blocks faithful `list-overdue` and
   legacy-row `list-high`.
3. **UNKNOWN_LOWERING_CAPABILITY** — input-domain validity/suppliedness
   relations (`invalid_due_date` well-formedness branch; `invalid_state`
   read-corruption mapping as a typed branch).
4. **WHOLE_PROGRAM_INTEGRATION_GAP** — version-dependent state shapes: one
   contract cannot span v1 bare-list vs v2/v3/v4 envelopes or required-
   current ∩ optional-legacy row typing; storage-shape promotion unexpressed.
5. **BINDING_GAP (previously known, explicitly deferred by R5.22 §19, now
   confirmed decisive for acceptance compatibility)** — frozen CLI argv form,
   repeated flags, shared `tasks.json` store, missing-file→`[]`, error
   envelope/exit codes.

Why R5.22's coverage analysis missed 1–4: its backlog was a list of
*relation kinds*, each validated on its own with fixture types chosen to suit
that relation; the matrix then marked the "Integrated AST / CLI binding" row
closed from a single-operation probe while simultaneously (and, in hindsight,
inconsistently) classifying the multi-operation command document as assembly
work "out of the backlog". Inter-capability **type domains** (instant vs
orderable keys; optional/nullable vs required terms; required-record vs
permissive-row frames; one-shape-per-contract) were never a row anyone could
close, so "no known required relation remains validating-only/unsupported"
was true per relation yet false per program. Lesson for the compiler-coverage
methodology: coverage must be enumerated over *pairs/compositions sharing a
representation domain* (fields, types, storage shape, contract cardinality),
not over relation kinds alone. No `BENCHMARK_REQUIREMENT_PREVIOUSLY_MISSED`
finding: every blocked obligation was already in R5.14/R5.17's reconstruction.
No `GROUNDING_GAP`: all 13 executable cases grounded.

## 21. B02 generalization assessment (Part 21)

- **Semantic adequacy:** YES at representation level for the third consecutive
  retry plus this comprehensive pass — the 30 candidate constructs still
  represent every observable B02 obligation; no #31. The discovered blockers
  sit below representation, in lowering/type-integration/binding layers.
- **Generative completeness:** NO. The locked compiler did not generate the
  complete B02 candidate. It did generate an executable twelve-branch
  multi-command B02-shaped program — first true multi-operation whole-program
  generation in the series — missing four obligation classes.
- **Source authority:** for everything generated: YES (behavior derives only
  from contracts; locked modules re-hashed unchanged; contamination audits
  pass). No complete candidate existed, so no candidate-level authority claim.
- **Frozen acceptance:** NOT RUN; 0 passed, 0 failed, 0 skipped, 7 blocked
  (§9). Honest non-execution, not evidence of failure or success.
- **Grounding:** 13 B02-shaped executions trustworthy (provenance-challenged,
  public + durable endpoints, `attempted_write` byte-obligations).
- **Semantic conformance:** 13/13 grounded executions conformant against the
  generating contracts; 0 non-conformant; faithful-typed blocked obligations
  NOT_EXECUTABLE.
- **Independent-capability transfer:** 10/17 known capabilities fully
  transferred (executed+grounded+conformant in B02 form, several now inside a
  multi-operation program); 2 transferred only under unfaithful typings
  (ordering, framed insertion at string/current-row subsets); 3 blocked by
  inter-capability composition; 1 (`before`) never executed in B02 form; CLI
  binding absent for the frozen transport.
- **Whole-program composition:** NO. Pieces composed wherever they did not
  share a domain; every failure is at a shared representation domain (one
  field's type, one contract's state shape, one program's transport).
- **Universal correctness:** NO — 13 slice cases plus one subset program
  establish none.

## 22. Construct accounting (Part 23)

Candidate core semantic constructs remain **30**; historical raw categorized
inventory 46; **no construct #31**. The newly observed blockers reference
existing semantics (#24/#25 clock/instant, #27 before, #43 order, #44 defaults,
#45 branches, #30 cardinality) and existing deferred obligations — they are
lowerer/planner/binding limitations, and nothing was added, changed or
counted. Compiler/lowering accounting: locked modules unchanged this phase.
Testing accounting: +1 file, 19 evidence tests. **Demonstrated cross-request
(B02) transfer updated only where whole-program evidence exists:** first
multi-operation integrated B02-shaped program executed (subset); first
executed B02-shaped create with real and controlled external providers;
framed insertion upgraded from synthetic-only/slice to executed inside an
integrated program; ordering remains transferred only for string-typed rows.
No claim that any complete B02 operation has been generated, accepted or
grounded.

## 23. Verification record

Pre-lock: §2 (224 harness, 31 tests, validate/safety, focused suites, `git
diff --check` 0, clean checkpoint `34381226`).

Post-lock: new focused suite `python -m unittest discover -s benchmark/harness
-p test_b02_integration_r5_23.py -v`: **19 run, 19 passed** (assembly/gate
diagnostics, branch matrix, grounding/conformance slices, transport
observations, lock-integrity). Full harness: **243 run, 243 passed, 0 failed**
(224 prior + 19 new). Application/compiler suite unchanged: 31 passed.
`LockIntegrity` re-verified all twelve locked sha256 component digests —
including every lowering/planner/runtime/boundary/verifier module and every
frozen authority file — byte-identical after the experiment; **no repair
occurred after lock**. `git diff --check` exit 0; the new file produced no
whitespace diagnostics (`--no-index --check` output empty).

**Line-ending notices (reported separately, not failures):** Git emitted its
standard LF→CRLF working-copy conversion warning for the new untracked test
file. Working tree at completion: HEAD unchanged (`34381226`), additions only
(this artifact, the evidence suite, and the three documentation updates).

## 24. Decision and exact next recommendation (Part 22)

**R5_23_PREVIOUSLY_UNKNOWN_LOWERING_GAP.** The comprehensive retry confirms
strongly that (a) the 30-construct semantic model is representation-adequate
for frozen B02, (b) per-relation lowering coverage is genuinely closed, and
(c) the remaining distance to a complete generated B02 is dominated by
**inter-capability type integration**, versioned-storage single-contract
composition, input-validity guard relations, and the previously and
explicitly deferred frozen-transport binding layer — classes the R5.22
per-relation backlog methodology could not express as rows.

Do **not** run another isolated one-capability discovery retry, and do not
advance Phase 5C to B03. The next work should be a **focused whole-program
integration phase plus compiler-coverage methodology revision** (suggested
R5.24): on independent non-task domains, generalize (1) ordering-key and
comparison operand domains over typed instants; (2) optional/nullable-aware
predicate typing; (3) input suppliedness/domain-validity relations as typed
failure guards; (4) version-dependent state handling (multiple storage shapes
and row typings across one program's applicability rules); and (5) the
interface/transport binding contract (positional commands, repeated flags,
shared store, missing-file semantics, error envelope/exit codes) as a checked
binding layer, then one final comprehensive B02 retry. R5.2.2 remains
historical authority; Phase 5C does not advance to B03; B17 remains
unexposed and unclassified; the semantic-first format remains globally
unfrozen; universal implementation correctness is not claimed; the candidate
core count remains 30 with no #31; no repair occurred after the §3 lock.

    R5_23_PREVIOUSLY_UNKNOWN_LOWERING_GAP
