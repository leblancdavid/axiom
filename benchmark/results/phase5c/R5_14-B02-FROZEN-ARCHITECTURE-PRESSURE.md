# R5.14 — B02 frozen-architecture pressure (prospective, 2026-10-02)

**Halt at gate 3: GENERATIVE_LOWERING_CAPABILITY.** This is a controlled
out-of-sample reassessment of the already historically encountered B02, not a
continuation of the historical Phase 5C track. The experimental control is the
unchanged 30 candidate core constructs and the R5.13 generator as found in the
workspace. R5.2.2 is the historical benchmark authority; no old checkpoint,
oracle, requirement, compiler, runtime or generated artifact is amended.

## 1. Authoritative reconstruction

Sources: `benchmark/requirements/B02.md:3-7`, inherited
`benchmark/requirements/B01.md:3-6` and `benchmark/baseline.md:3-43`;
`benchmark/harness/regression.py:60-223` with `profiles/B02.json` and
`capabilities/B02.json` is the frozen B02-stage external profile (B01+B02).
The earlier frozen `pilot_oracle.py:30-94` is corroborating B01+B02 acceptance,
not an additional source of requirements. The B02 profile adds `tags` and a
version-4 envelope/default; it does not prescribe the application algorithm.
No requirement was inferred from the Conventional implementation. Each row
below identifies input; pre-state → outcome/post-state; selection/order;
normalization; persistence/failure; and public observation. `—` means that
dimension adds no rule beyond the cited inherited contract.

| Clause / frozen source | Input, pre-state → outcome and post-state | Selection, order, normalization | Persistence, failure, public observation |
| --- | --- | --- | --- |
| B02:3 create flags | `create` takes zero or more repeated `--tag VALUE`; valid current task state → one new task carrying a `tags` array, other tasks preserved | Preserve flag order before normalization; each VALUE is a string | Success returns the created task and persists it across processes with all inherited task fields. |
| B02:3-4 nonblank | Each supplied VALUE, including one among several; state unchanged on rejected invocation | Trim outer whitespace, require every trimmed string nonblank; zero values satisfy the rule vacuously | A blank-after-trim tag returns `invalid_tag`, adds no task and does not change durable state (inherited failure transport/no-write applies). |
| B02:4-5 normalization | Valid repeated values → created task's `tags` | `stable_unique(map(trim(values)))` with case-sensitive equality; retain the *first* occurrence's position, including duplicates after trimming; no alphabetical sorting or case folding | Returned array and stored array agree; not just acceptance on finite example values. |
| B02:6-7 task field/default | Omitted flags on create, or older valid task(s) before explicit migration → task(s) with `tags: []` | Empty ordered sequence; no selection | Every returned task has `tags` (create, list/filter results, complete and delete); old tasks get empty tags through migration, not implicit rewrite on legacy read. |
| Baseline:3-7,27-32 + B01:3-6 + B02 profile | Separate CLI processes; missing/current/v1/v2/v3 state; explicit `migrate` | Preserve B01 CRITICAL acceptance, exact HIGH-only filter, LOW/NORMAL/HIGH legacy values and NORMAL default; legacy records retain existing fields and gain missing priority/due date/tags | JSON stdout on success/exit 0, named JSON stderr/exit 1 on expected failure; missing `list` is `[]` without file creation. Legacy read is `migration_required` with no write. Migration converts legacy records, reports count, writes current envelope; current/absent migrate returns 0. B02 profile's version is 4, v3 is now legacy. |
| Baseline:9-26,34-38 | `create`, `list`, `list-high`, `list-overdue`, `complete`, `delete`; valid/current or invalid state | Each task has exactly inherited fields plus `tags`; unique nonempty IDs, UTC `Z` creation time, normal `(created_at,id)` list order, exact HIGH and pending/dated/strictly-past overdue selection; complete/delete preserve or return the appropriate entire task | Title/due validation, lifecycle transitions, missing IDs, corruption/invalid shape, no-write on failure and durable reads remain obligations. B02 does not replace them. |

Acceptance specifically samples empty and duplicate/mixed-case tags, `invalid_tag`
with byte-identical file, completion preservation, v3 and unversioned migration,
and B01/baseline regressions. It does **not** prove the universal sequence rule.
The frozen text does not specify precedence when multiple independent create
inputs are invalid, precise whitespace taxonomy beyond trimming, or how to
classify every imaginable malformed *stored* tag array (for example repeated
already-persisted values). Those are `BENCHMARK_UNDERSPECIFIED` edges, not
permission to drop the specified valid-input and failure obligations. The
baseline's invalid record shape and exact public field set still apply.

## 2. Semantic expressibility gate — PASS at candidate-vocabulary level

This is a clause-level encoding assessment, **not** a claim that one integrated
typed B02 document is currently accepted by one validator. The 30 candidates
are an unfrozen inventory spread across prototypes. `#45` means a conditional
typed operation tuple (input, before, tagged result, after), not a new CLI
primitive. The input/state/output interface needs a checked binding later.

| Clause | Classification | Existing semantic composition |
| --- | --- | --- |
| Repeated flags and per-value validity | EXPRESSIBLE_EXISTING | #3 finite ordered string sequence, #4 bound item, #13 trim, #14 nonblank, #17 for_each, #22 guard and #23 finite scope; an invalid input selects the `invalid_tag` outcome under #45. |
| Trimmed case-sensitive first-occurrence array, including zero elements | EXPRESSIBLE_EXISTING | #15 map(trim) then #16 stable_unique with string equality #6; #21-23 relate supplied input to task's output field for arbitrary finite valid inputs. `B02.ordered_normalization` in `benchmark/semantic/invariant-fixtures.json` is an existing finite-witness-linked universal rule prototype, not a generated program. |
| Failure and no new task/no write | EXPRESSIBLE_EXISTING | #7/#8 Boolean guard, #21-23 unchanged before/after state, #45 typed `invalid_tag` alternative; durable byte preservation is a binding/observation obligation, not a new core operator. |
| New record, empty omission default, field retained by mutations/read results | EXPRESSIBLE_EXISTING | #1-6 task field/sequence/equality, #21-23 same-invocation before/after framing, #44 missing-field default where applicable and #45 result alternatives; reuse B01 insertion/preservation framing for arbitrary state rows, not a tags-specific update primitive. |
| Legacy conversion v1/v2/v3 and result count | EXPRESSIBLE_EXISTING | #44 keyed default/preservation applied to missing fields; #21-23 versioned applicability/transition, #10-12 exact legacy population and core #30 cardinality to migrated integer result via #45. Multiple fields/nullable due date require composition/type integration, not an identified #31. |
| Inherited selection, ordering, lifecycle, error and task envelope | EXPRESSIBLE_EXISTING | #10-12 selection, #25/#27 time, #43 typed order, #21-23 state relation, #44 defaults, #45 tagged operation relation, core #30 numeric migration outcome; B01 abstract expressibility was assessed in R5.11, not B01 generative lowering. |
| Unspecified invalid-input precedence / unspecified corrupted-tag details | BENCHMARK_UNDERSPECIFIED | No additional semantic clause is imposed by the frozen sources. |

No precise frozen B02 clause is classified `CORE_SEMANTIC_GAP`; #31 is not
introduced. In particular a finite fixture alone could not express arbitrary
tag repetitions, but #13-17 already provide the general rule. This gate
assesses *meaning*, not completeness of current prototype validation, type
integration, implementation or B02 acceptance.

## 3. Lowering support gate — HALT

Source audit: `benchmark/semantic/generative_r5_13.py:3-5,41-85,88-135`
supports record input, sequence-of-record pre-state, refs, literals, equality,
and/not, selection/cardinality, ordered string-payload branches, preservation
or keyed field replacement. `typed_lowering_r5_12.py:35-95,104-152` compiles
some **validating** read constraints; `invariants.py:23-52,184-200` interprets
B02 normalization on supplied tuples. `generative_runtime_r5_13.py:21-36`
reads an existing JSON state sequence and emits a tagged result, not a task CLI.

| Required behavior | Classification | Exact support boundary |
| --- | --- | --- |
| Typed record/sequence fields, equality/and/not, selection/cardinality, string-tagged branch, preserve/no-write or keyed replacement in R5.13's state shape | GENERATIVELY_SUPPORTED | These isolated constructs are emitted from semantic data on the non-task R5.13 contracts; this is not a complete B02 command. |
| Ordered map(trim), stable_unique, universal nonblank on arbitrary repeated inputs | VALID_BUT_UNSUPPORTED_LOWERING | #13-17 have supplied-tuple interpreters, but neither `expression` nor `typed` in the general generator emits them. R5.12 also has no corresponding expression nodes. This is a required B02 success/failure path, not a fixture-only edge. |
| Keyed `default_missing` and composition over versions/multiple optional task fields | VALID_BUT_UNSUPPORTED_LOWERING | #44 exists as a semantic relation and R5.13 explicitly rejects it in guard/transition. Its record checker requires exact fields and cannot express nullable due date in the generated subset. |
| Create insertion with normalized array field; migration of legacy envelopes; complete/delete and ordered task-array outcomes | VALID_BUT_UNSUPPORTED_LOWERING | R5.13 only replaces a scalar field in existing equal-key rows or preserves the sequence; its result payload is string, not a task, ordered list or integer count. No general append/remove, multi-field transition, versioned storage or varied payload generation is demonstrated. |
| Normal-list/exact-HIGH read-only supplied tuple checks | VALIDATING_ONLY | R5.12 checks selected B01 cases via typed relations; it does not generate list/list-high executable behavior or B02 task results. |
| Concrete B02 CLI argument/state/outcome binding and full negative-path durability | UNKNOWN | Not exercised once required lowering fails; absence of checked CLI binding is a separate potential non-semantic issue, not the reason to invent new semantic syntax. |

The second row alone stops the generative attempt. The third and fourth are
additional independently identified compiler breadth gaps; no new lowering is
implemented and no existing semantics are silently ignored. These are not
`CORE_SEMANTIC_GAP` findings. Type-system integration (nullable and
heterogeneous result shapes) is also necessary but does not supersede the
decisive unsupported semantic-to-behavior lowering.

## 4–9. Source authority, candidate, acceptance, grounding, conformance, halt

**Source-authority gate:** not passed/reached for B02. The R5.13 non-task
source-authoritative path exists, but cannot generate the required operations.
R5.11's B01 template and B01-specific verifier are separately authored Python
behavior (R5.12 audit); neither is a valid B02 workaround. A metadata digest or
handwritten target would not establish B02 semantic-source authority.

**Candidate generation:** not authorized; no instrumented B02 candidate built.
**Frozen B02 acceptance:** not executed against a generated candidate; pass,
fail and skip counts are **not applicable**, not zero-pass evidence or invented
skips. **Grounding and semantic conformance:** not executed for B02; there are
no B02 cases to label GROUNDED + CONFORMANT, GROUNDED + NON_CONFORMANT or
GROUNDING_FAILED. Existing R5.13 cases are not B02 evidence.

**Halt record:** stage = lowering gate; layer =
`GENERATIVE_LOWERING_CAPABILITY` (with separate unverified `TYPE_SYSTEM` and
`BINDING` integration pressure). Trigger = valid #15/#16/#17 composition for
arbitrary repeated flags is not emitted by `generative_r5_13.expression`; #44
and new-record/versioned operations are also unsupported. No patch-on-failure
or B02-specific branch was made. This is a capability finding, not a failed
application implementation and not an architecture contradiction.

## 10–13. Historical comparison, reuse, overfitting, accounting

The corrected Phase 5A pilot (`benchmark/results/pilot/REPORT.md:34-60`) and
Phase 5B B02 checkpoint reported `AXIOM_CAPABILITY_GAP`: frozen v0.3 fields and
inputs could not hold repeated string arrays, trim/deduplicate, or default `[]`;
the old model remained B01-only. R5.4's first semantic-format halt likewise
could not state arbitrary ordered normalization. The later *candidate* #3 and
#13-17 universal rules resolve that **prospective expressibility** gap; #44/#45
and core #30 cover abstract migration/outcome relationships. They do not
retroactively alter the frozen v0.3 gap or checkpoint. R5.13 adds executable
lowering for a different, smaller stateful slice; it does **not** resolve B02
normalization, repeated-input handling or full task transitions. Thus the old
historical gap persists in its frozen architecture, while this experimental
architecture reaches a **different layer** (general generative lowering).

Demonstrated reuse for B02 **execution**: none (0 generated B02 operations, 0
grounded B02 calls). Existing cross-domain *semantic* witnesses include B02
ordered-normalization fixtures, synthetic state/default and #45 relations and
R5.13 non-task stateful generation; these are not cross-request executable
reuse. Do not increment demonstrated frozen-request reuse from B01 or count
plausible #43/#44 cross-clause applications as demonstrated B02 lowering.
Expressibility beyond the B01-shaped rules is evidence against a strictly
B01-only semantic vocabulary, but the halt shows semantic coverage currently
outpaces compiler coverage; it neither proves nor refutes general executable
reuse. Forcing B02 through handwritten Python would be a strong overfitting
signal and is disallowed here.

Candidate core count **30** / raw categorized inventory **46**, unchanged.
No #31, no new language version, no semantic-first format freeze. A future
general compiler study may test composition of ordered string transformation,
conditional errors, insertion, typed results and versioned defaults on
independent non-task domains *before* deciding whether to retry B02. This is
compiler work to evaluate, not an R5.14 patch authorization. Phase 5C stops at
B02; B03 is not attempted. B17 stays unexposed/unclassified; universal
implementation correctness is not claimed.

## 14. Exact next recommendation and verification

Keep this halt immutable as the result of the frozen-architecture attempt.
In a separately versioned future experiment, develop and challenge general
generative support for the identified existing relations on non-task examples,
including rejected blank input, ordered normalization, defaulted legacy state,
typed results and independently observed durable state. Reassess B02 only after
independent source-authority and binding checks; do not treat a prospective
compiler extension as part of this run.

Verification from repository root: `python -m unittest discover -s
benchmark/harness -v` **149 OK** (includes R5.5 architecture 6, R5.7
grounding 10, semantic-prototype groups, R5.10 4, R5.11 4, R5.12 3 and
R5.13 5); `$env:PYTHONPATH='src'; python -m unittest discover -s tests -v`
**31 OK**. `python -m air_compiler.cli validate air/task_manager.json`
reported `Lykoi validate: ok`; `python -m air_compiler.cli safety
air/task_manager.json` reported zero capability violations and zero invalid
transitions. No R5.14 integration test or B02 candidate execution was
authorized. `git diff --check` exited 0 with no whitespace errors. The
untracked R5.14 artifact also passed `git diff --no-index --check -- NUL
<artifact>` with no whitespace diagnostics. Git separately emitted LF→CRLF
working-copy warnings on four already-modified tracked files
(`b01_integration_r5_11.py`, `decisions.md`, `project-overview.md`,
`research-log.md`) and the new artifact; warnings are not failures. These
development suites check
the unchanged architecture, **not** a generated B02 candidate. Any B02 skips
printed by nested historical harness tests refer to the historical B01-only
checkpoint, not R5.14 B02 acceptance.

R5_14_B02_SEMANTICS_VALID_LOWERING_GAP
