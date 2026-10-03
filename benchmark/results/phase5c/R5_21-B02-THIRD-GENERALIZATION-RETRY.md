# R5.21 — Third frozen B02 generalization retry (prospective, 2026-10-03)

Third and last planned locked retry under the serial pattern *retry B02 →
discover one unsupported lowering capability → implement it independently →
retry again*. R5.2.2 remains historical benchmark authority. No locked compiler,
runtime, verifier, frozen requirement, profile, oracle or historical artifact was
modified; probes are observation only. Phase 5C does not advance to B03; B17
remains unexposed and unclassified; the semantic-first format remains globally
unfrozen.

## 1. Pre-lock suite lifecycle adjustments

A full audit of current-lowerer expectations found none newly obsolete. The only
two executable expectations that independent compiler work had superseded were
already retired at their checkpoints by the established lifecycle precedent:
the R5.17 overlapping-default rejection expectation (updated at R5.19) and the
R5.19 `order` rejection expectation (updated at R5.20). Every remaining
`UnsupportedLowering` assertion in the suite still describes actual locked
behavior (R5.12 default_missing validating rejection, R5.13/R5.15/R5.16/R5.18
bounded-transition gates, R5.20 direction/scoped-source rejections); all pass
unchanged. No historical result artifact or conclusion was rewritten.
Adjustments required before this lock: none.

## 2. Green pre-lock verification

Full benchmark harness **183 run, 183 passed, 0 failed**; application/compiler
suite **31 passed**; `validate` ok; `safety` zero capability violations and
zero invalid transitions; focused R5.10–R5.19 pattern **32 passed**; R5.20
focused **18 passed**; R5.17 and R5.19 retry files **1 passed** each;
`git diff --check` exited 0. Git separately warned of LF→CRLF conversion on
working-copy files — line-ending warnings, reported separately, not failures.

## 3. Experimental lock

HEAD `c9b9e1a8b9b2c0befb4fdf9b02f734794e919fdd`; identities are working-copy Git
blob hashes (`git hash-object`). The general lowerer, canonical relation
planner and ordering planner live in one module; the locked evidence module
carries the grounding challenge and the semantic case verifier.

| Component / path | Locked Git blob |
| --- | --- |
| Canonical application model `air/task_manager.json` | `2c9a51cc2993462bfcadb34d09b469d081135d75` |
| 30-candidate inventory `R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md` | `d6dc362ee73bfcc26b2b7a8792e1864cd59db8cf` |
| Vocabulary ledger `R5_4-SELECTION-VOCABULARY-LEDGER.md` | `662d37683b7840be10840e23eb914aa44cf5d87e` |
| Semantic prototype `benchmark/semantic/prototype.json` | `b9df7de07e268cc6b535be95134f37b16eaff4a8` |
| Semantic relations `invariants.py`, `invariant-fixtures.json` | `1b2fd5e90e627f78c8236d11229a8b3130e6919c`, `15e0086ffa219a3d7ad7ef74acf1122b06afc2c3` |
| Validating checker `typed_lowering_r5_12.py` | `cc09b11d29491d4686404e63db1a571bb6983b58` |
| General lowerer + relation planner (`typed`/`_relational`/`render`) + ordering planner (`ordering_plan`) `generative_r5_13.py` | `42cb8eacc843dcc9773c2f47258673c0624d363f` |
| Generic runtime `generative_runtime_r5_13.py` | `6e03bc8d0a3d57dbaea680aa2b6c4d65a4757dc0` |
| Binding metadata `binding.py` (with `contracts.py` `20299697281ac743b66599367673e3e625fd7fc2`) | `32ef8908b294945a6b52e94f693315a6edb86af1` |
| Provenance / independent observation / grounding challenge / semantic case verifier `generative_evidence_r5_13.py` | `efc072e3ae27e74439f2a374e61e7ec88f54b478` |
| Grounding framework `grounding_r5_7.py` | `d69847ced09c3d254b0586a66ae3a4fc237d1dca` |
| Conformance framework `conformance.py` | `39501dde66412585e5b5c7b5f25cdc75395d387c` |
| Historical retry tests (lifecycle state at lock) `test_b02_retry_r5_17.py`, `test_b02_retry_r5_19.py`, `test_ordering_lowering_r5_20.py` | `8cf94a08d24e2b21bd19cf78eb63ea8334232a76`, `c9acf77a0808acb4ebc0382ee69709a0326fb0d0`, `209a1bd3e554a012610172711b4d9f596209e0e8` |
| Frozen `B02.md`, `B01.md`, `baseline.md` | `d12654997f15a2774ff3b4914ec56dab87f85440`, `07391ea8a41ec79b49f20ca5258fe8b46e5d4a8c`, `8025876f8444591bc7c1ee0ac50f120164374c90` |
| Frozen `regression.py`, `profiles/B02.json`, `capabilities/B02.json` | `8bfa6ba450c59cfc23d34c7560b80fb4c5b1076b`, `b01e779ff75db1d31dca1ba2f242b592a5fc7183`, `313d8fdac17ca13877146464e9097278b89a5989` |

Every identifier matches the R5.19 lock except the R5.20 ordering changes to
`generative_r5_13.py`/`generative_evidence_r5_13.py` and the two recorded
test-lifecycle files; all were re-hashed unchanged after the retry. Post-lock
addition: new probe file `benchmark/harness/test_b02_retry_r5_21.py`
(`e505750b07b30ec5b13e143a51f0f7f2880a4242`); no locked component changed.

## 4. Semantic adequacy confirmation

Direct comparison against R5.14's clause table, R5.17's relation set and
R5.19's frozen reconstruction confirms the unchanged candidate vocabulary still
represents every frozen B02 obligation: repeated-flag input and per-value
trimmed-nonblank guard (#3/#4/#13/#14/#17/#22), case-sensitive first-occurrence
normalization with `[]` omission (#15/#16/#6), typed task-valued outcomes and
alternatives (#45), fresh full-record insertion and preservation (#21–23),
versioned legacy defaults (#44) with cardinality-derived migrated count (#30),
inherited exact HIGH selection (#10–12), typed `(created_at, id)` ordering
(#43), lifecycle transitions, strict-past time selection (#25/#27 represented
and validated in the R5.4 format/scenario channel) and no-write failure
behavior. No `CORE_SEMANTIC_GAP` appeared; ambiguous invalid-input precedence
and malformed stored-tag taxonomy remain `BENCHMARK_UNDERSPECIFIED` exactly as
in R5.14. Fresh-ID and creation-clock **generation** remain inherited
binding/adapter obligations (R5.14 §2), not a 31st core construct.
Candidate core count remains **30**; historical raw inventory 46; no #31.

## 5. B02 contract

The complete intended semantic relation set is unchanged from R5.17/R5.19:
`create` branches on validity of title/priority/due and every trimmed tag,
returns `invalid_tag` with unchanged bytes on blank input, or builds the full
typed task (`tags = stable_unique(map(trim(input.tags)))`, fresh ID, UTC
creation time, omitted-field defaults) and inserts it through an exact frame;
`list` returns the population ordered `(created_at,id)`; `list-high` selects
exactly HIGH then orders; `list-overdue` selects pending dated rows strictly
before the clock; `complete`/`delete` preserve or return the entire task;
`migrate` applies each missing-field default to the same uniquely keyed legacy
population, sets version 4 and reports `{migrated: cardinality(pre.records)}`;
legacy reads signal `migration_required` with no write; JSON CLI transport,
exact field shapes, durable file, failure exit, clock and fresh-ID binding
remain inherited obligations. The contract was **not** reduced to fit current
compiler coverage: faithful B02-shaped slices plus one integrated multi-branch
serialization (with explicit placeholders for the external/fallback relations)
were fed to the locked lowerer in `test_b02_retry_r5_21.py`.

## 6. R5.19 ordering-blocker retry (recorded before proceeding)

The exact R5.17/R5.19 ordered-`list` serialization (full B02 legacy-row shape,
`order(pre.records, keys=[created_at,id])`, `migration_required` no-write
alternative) now types **and** renders through the locked lowerer
(`sorted(pre['records'], key=lambda …)` emitted from the contract's key list —
no task names in the lowerer). Beyond rendering, it was generated, executed as
a real subprocess over a disposable B02-shaped durable population whose storage
order differs from semantic order and whose two HIGH rows tie on `created_at`
(id decides), independently grounded and semantically conformant; the legacy
alternative returns `migration_required` with byte-identical storage.
**R5.19 `UNSUPPORTED_LOWERING_CAPABILITY: order` is RESOLVED without any
B02-specific compiler modification.**

## 7. Capability-transfer matrix

Classification uses only actual B02 lowering in this retry.

| Capability ← independent origin | Actual R5.21 B02 result |
| --- | --- |
| Ordered normalization ← R5.15 | **TRANSFERRED_IN_B02**: blank-tag guard (`for_each`/`nonblank`/`trim`, three blank-input shapes incl. `''`) and `stable_unique(map(trim))` projection of the frozen sample values executed, grounded and conformed on B02-shaped contracts. Full create embedding not reached (§8 gate). |
| Typed record-valued outcomes ← R5.15 | **TRANSFERRED_IN_B02**: record outcomes `{tags: …}` and `{migrated: n}` executed; full 8-field task outcome NOT_REACHED at the gate. |
| Keyed missing-field default ← R5.15 | **TRANSFERRED_IN_B02**: executed on B02 legacy rows (present fields preserved, absent filled). |
| Framed insertion ← R5.16 | **NOT_REACHED**: upstream create-success gate (§8); synthetic-only (R5.16). |
| Durable version transition ← R5.16 | **TRANSFERRED_IN_B02**: executed `schema_version` 1→4 durable write, grounded. |
| Cardinality-derived migrated count ← R5.16/#30 | **TRANSFERRED_IN_B02**: `{migrated: 2}` executed and conformed against `cardinality(pre.records)`. |
| Overlapping compatible defaults ← R5.18 | **TRANSFERRED_IN_B02**: three same-collection defaults executed jointly (upgrades R5.19's typed-and-rendered-only transfer). |
| Typed lexicographic ordering ← R5.20 | **TRANSFERRED_IN_B02**: §6; also composed under exact selection in `list-high`. |
| Exact selection ← R5.13 | **TRANSFERRED_IN_B02**: exact-HIGH selection (CRITICAL excluded by equality) ordered and executed. |
| Durable read-only preserve ← R5.13 | **TRANSFERRED_IN_B02**: ordered views returned with byte-identical storage and `attempted_write: false`. |
| Keyed lifecycle replacement ← R5.13 | Slice: **TRANSFERRED_IN_B02** on plain-sequence B02-shaped state; **STILL_UNSUPPORTED** over the versioned envelope (§8, newly observed). |

## 8. Complete lowering result — gate and decisive composition

The complete lowering attempt ends **VALID_SEMANTICS_UNSUPPORTED_LOWERING**.
The decisive next failure is the faithful **create-success composition**: the
constructed task outcome requires value generation with no checked generative
interpretation — `{'external': …}` (fresh unique ID; UTC creation instant),
rejected `UNSUPPORTED_LOWERING… unsupported relation: external`, and the
omitted-input fallback `{'fallback': …}` (priority→NORMAL, due→null), rejected
`unsupported relation: fallback`. The integrated multi-branch B02 document
rejects at exactly this point, so the full contract still cannot be serialized.
Frontier observation (no repair) additionally records: strict time comparison
`before` (#27) rejected — represented and validated only in the R5.4 typed
instant/clock channel (`format.py:229-235`), never generative; matched-row /
post-state outcome projection rejected — the four-slot #45 validating checker
(`typed_lowering_r5_12.lower`) has `post`/`outcome` slots but the generative
channel binds outcomes to `input`/`pre` only; `remove` (delete) transition
rejected `state relation`; keyed `replace_field` over the versioned envelope
record state rejected `state relation` (transition support is state-shape
dependent: plain sequences only); mixed frame+default on one collection
remains explicitly unsupported and was not reached. **HALT: no post-lock
repair; nothing beyond observation was performed.**

## 9. Full B02 lowering-coverage matrix (known contract)

| B02 relation/composition | Classification |
| --- | --- |
| Ordered `list` read + legacy `migration_required` no-write | GENERATIVE_CONFIRMED_IN_B02 (executed slice) |
| `list-high` exact selection ∘ ordering | GENERATIVE_CONFIRMED_IN_B02 (executed slice) |
| Blank-tag guard + `invalid_tag` outcome + byte preservation | GENERATIVE_CONFIRMED_IN_B02 (executed slice) |
| `stable_unique(map(trim))` tag normalization | GENERATIVE_CONFIRMED_IN_B02 (executed projection; full embedding blocked by §8) |
| N-way keyed defaults + version equality + cardinality count (migrate) | GENERATIVE_CONFIRMED_IN_B02 (executed slice; v1-shape only, R5.17 limits retained) |
| Keyed lifecycle status replacement | GENERATIVE_CONFIRMED_IN_B02 on plain-sequence state; envelope shape UNSUPPORTED |
| Exact full-record insertion in create | GENERATIVE_CONFIRMED_SYNTHETIC_ONLY (R5.16); NOT_REACHED in B02 |
| Full task-valued create/complete/delete outcomes | UNSUPPORTED (external/fallback gate) |
| Fresh-ID and UTC-clock value generation | UNSUPPORTED generatively; inherited binding/adapter obligation |
| Omitted-input default fallback | UNSUPPORTED (no #44 expression interpretation for inputs) |
| Strict-past comparison (#27 `before`) and due-date instant parsing (#25) | VALIDATING_ONLY (R5.4 format/scenario channel); UNSUPPORTED generatively |
| Matched-row/post-state outcome projection (#45 post/outcome slots) | VALIDATING_ONLY (R5.12 four-slot checker); UNSUPPORTED generatively |
| Row removal transition (delete) | UNSUPPORTED (abstract #21–23 only; no grammar) |
| `invalid_state` on corrupt stored data (enums, duplicate IDs, malformed JSON) | UNKNOWN (runtime shape check partial; failure mapping never reached) |
| CLI argument transport, error envelope/exit codes, missing-file→`[]`, one shared store across commands, integrated multi-operation AST | NOT_REACHED (interface/binding layer) |
| Failure-branch precedence and stored malformed-tag taxonomy | NOT_REACHED; `BENCHMARK_UNDERSPECIFIED` as in R5.14 |

## 10. Source-authority audit

Gate not passed for complete B02 (generation did not succeed; Part 7 is
conditional on it). What is established: the locked lowerer/planner/runtime/
verifier contain generic dispatch and no B02/task-specific branches — the R5.20
automated contamination audit (`test_lowerer_contains_no_task_b02_or_
benchmark_vocabulary`) re-passed on the locked blob inside the green suite; all
slice behavior, including `(created_at, id)` ordering data, arrives through
contract keys/slots/shapes; no manually authored normalization, ordering,
insertion, migration, record outcome or frozen fixture constant was substituted
in any lowering path.

## 11. Distinct R5.21 candidate

Not authorized and not created (generation gate not GENERATED). Semantic
identity, generated B02 operation identities, candidate provenance and artifact
integrity: **N/A**. Disposable slice executables in temporary directories are
not candidates.

## 12. Frozen acceptance

Not run. Passed **N/A**, failed **N/A**, skipped **N/A**. The frozen oracle,
profile and requirements were used read-only and re-hashed unchanged.

## 13. Grounding

Candidate-level grounding: **N/A**. Slice-level grounding evidence exists for
the executed probes (ordered list and legacy alternative, blank-tag guard,
tags projection, list-high and legacy alternative, complete transition and
non-match, migration and current alternative): every case ran the generated
program as a subprocess, passed the provenance digest challenge, matched
internal events against independently captured public stdout and durable
file readback, and reported `provenance_valid: true, grounded: true` with
correct `attempted_write` byte obligations.

## 14. Semantic conformance

Evaluated against the same contracts that drove generation. All thirteen
grounded slice cases: **GROUNDED + CONFORMANT** — including the tie-decided
`(created_at,id)` permutation judged by the relation (exact multiset plus
nondecreasing keys), joint-default post-state equality, and cardinality
outcome. **GROUNDED + NON_CONFORMANT: 0 observed. GROUNDING_FAILED: 0.**
No universal correctness follows from slice-level conformance.

## 15. Ordering-specific transfer result

R5.20 ordering transfer = **DEMONSTRATED**: the B02 ordered-`list` contract
types and renders without lowerer modification, and further executes, grounds
and conforms end-to-end on B02-shaped data (§6, §7, §14).

## 16. Historical progression (no history rewritten)

- R5.14: broad B02 lowering insufficiency (multiple existing relations
  generative-unsupported).
- R5.17: overlapping collection relations blocked.
- R5.18: independent N-way default composition validated.
- R5.19: N-way defaults transferred (typed+rendered); `order` became the next
  blocker.
- R5.20: independent typed ordering lowering validated on non-task domains.
- R5.21: ordering transferred **and executed** in B02 shape; overlapping
  defaults, durable version transition, #30 count, selection, normalization
  and record outcomes transferred at executed-slice level; the next blocker is
  the create-success external/fallback composition plus several known
  interface/projection/removal/comparison boundaries.

## 17. Compiler maturity assessment

**Semantic-model maturity:** B02 continues to fit the 30-construct model for a
fifth consecutive confirmation; every observed blocker is a lowering or binding
coverage limit, not a representation gap. **Compiler-coverage maturity:** of
the enumerated B02 relation classes (§9), 6 classes are generatively confirmed
in B02-shaped execution, 1 partially (state-shape dependent), 1 synthetic-only,
2 validating-only-plus-unsupported, 5–6 unsupported and 3–4 never reached at
interface level. Remaining failures are **missing implementation coverage and
integration scope**, not architectural contradictions: the locked
contract→plan→generate→ground→conform path handled every relation class it has
been given, unchanged, and rejected everything else explicitly and safely —
no silent fallback, no invented direction or tie semantics, no #31.

## 18. Construct accounting

Candidate core constructs remain **30**; historical raw inventory 46; no #31
added. The frontier placeholder nodes (`external`, `fallback`, `sole`,
`before`, `remove`) are rejected probes referencing existing candidate
constructs or inherited obligations — never accepted, never lowered, never
counted. Demonstrated benchmark transfer updated **only** for capabilities
actually reached in B02: ordering (R5.20 origin) plus execution-level upgrade
of R5.15 normalization/defaults/record outcomes, R5.16 durable version +
#30 count, R5.18 N-way defaults, and R5.13 selection/preserve/read-only —
7 of the 8 tracked capabilities now execute, ground and conform on B02-shaped
slices; framed insertion remains NOT_REACHED. Still 0 complete B02 operations,
0 grounded calls against a candidate, 0 frozen acceptance methods.

## 19. Universal correctness

UNIVERSAL_IMPLEMENTATION_CORRECTNESS_ESTABLISHED = **NO**. Slice conformance,
grounded probes and prior validating evidence do not establish universal
correctness of the B02 behavior or of the vocabulary.

## 20. Exact next recommendation

Do not run a fourth serial one-capability B02 retry. Execute a **lowering
coverage completion phase** on independent non-task domains, closing the
**known** §9 set as a bundle rather than one discovery per cycle:
(1) strict comparison / typed instant predicates; (2) removal transition;
(3) matched-row/post-state outcome projection; (4) omitted-input fallback
defaults; (5) transition support independent of state shape (envelope
collections) and mixed collection transforms; (6) an external-value binder
(clock/ID adapter boundary keeping core semantics separate); (7) the
integrated multi-operation AST with CLI/state binding. Then reassess B02 once
against the closed set. R5.14/R5.17/R5.18/R5.19/R5.20 records stand unchanged;
Phase 5C does not advance to B03; B17 remains unexposed and unclassified; the
semantic-first format remains globally unfrozen; R5.2.2 remains historical
benchmark authority.

## Verification record

Pre-lock (§2). Post-lock focused retry
`python -m unittest discover -s benchmark/harness -p
test_b02_retry_r5_21.py -v`: **14 run, 14 passed** (10 executable B02-shaped
slice probes incl. alternatives; 4 frontier/gate probes). Full harness post-lock
**197 run, 197 passed, 0 failed** (183 pre-lock + 14 new); application/compiler
**31 passed**. All locked components re-hashed unchanged (§3). `git diff
--check` exit 0; the new file produced no whitespace diagnostics
(`--no-index --check` output empty); Git separately emitted LF→CRLF
line-ending warnings, reported separately from failures. No repair of any locked
component occurred after §3.

    R5_21_B02_KNOWN_LOWERING_COVERAGE_INCOMPLETE
