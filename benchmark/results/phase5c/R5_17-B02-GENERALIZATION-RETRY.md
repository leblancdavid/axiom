# R5.17 — Frozen B02 generalization retry (prospective, 2026-10-02)

## Experimental lock (recorded before B02 contract attempt)

Workspace HEAD `111c671fd86d60c5367c98f7348d9fc55631b2fa`; dirty R5.16
work is deliberately included in the locked working-copy identities below.
Identifiers are Git blob hashes of the **working-copy bytes** (`git hash-object`,
not HEAD versions). Python `3.14.3`, repository-root imports, no external
dependencies; generator `generate(contract, directory)` uses default
`fault=False`. No model, general lowerer, generic runtime, grounding or
conformance repair is authorized once the attempt begins.

| Locked component | Working-copy Git blob |
| --- | --- |
| Prospective semantic inventory/relation meaning: `benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md` | `d6dc362ee73bfcc26b2b7a8792e1864cd59db8cf` |
| B02 decomposition: `benchmark/results/phase5c/R5_14-B02-FROZEN-ARCHITECTURE-PRESSURE.md` | `b2f7b72bac1ddb827c6498e5a7049bc60ab2cf4e` |
| Existing typed relation checker: `benchmark/semantic/typed_lowering_r5_12.py` | `cc09b11d29491d4686404e63db1a571bb6983b58` |
| General generator: `benchmark/semantic/generative_r5_13.py` | `54eed62bec745222a8a4946a8b3584310a1d87c5` |
| Generic runtime: `benchmark/semantic/generative_runtime_r5_13.py` | `6e03bc8d0a3d57dbaea680aa2b6c4d65a4757dc0` |
| Independent observer/grounding/conformance: `benchmark/semantic/generative_evidence_r5_13.py` | `102599f35c15b16aa88671be2a097fa92a303248` |
| General invariant interpreter/fixtures: `benchmark/semantic/invariants.py`, `benchmark/semantic/invariant-fixtures.json` | `1b2fd5e90e627f78c8236d11229a8b3130e6919c`, `15e0086ffa219a3d7ad7ef74acf1122b06afc2c3` |
| Frozen B02, inherited B01, baseline | `d12654997f15a2774ff3b4914ec56dab87f85440`, `07391ea8a41ec79b49f20ca5258fe8b46e5d4a8c`, `8025876f8444591bc7c1ee0ac50f120164374c90` |
| Frozen B02 external configuration: `profiles/B02.json`, `capabilities/B02.json`, `regression.py` | `b01e779ff75db1d31dca1ba2f242b592a5fc7183`, `313d8fdac17ca13877146464e9097278b89a5989`, `8bfa6ba450c59cfc23d34c7560b80fb4c5b1076b` |

Relevant configuration: `typed(contract)` checks the five-key `id/version/input/state/branches`
contract; `state` is one typed sequence-of-records or typed record; input is a
typed record; `branches` have checked Boolean guards and a final otherwise;
`_compile` checks typed expressions; `render` emits Python; `generate` records
contract/artifact/runtime SHA-256 lineage. Runtime reads an existing typed JSON
state file and prints a `{kind,value}` outcome; observer invokes a subprocess
against that file. Frozen B02 config specifies schema version **4**, task
fields including `tags`, and migration defaults `priority: NORMAL`,
`due_date: null`, `tags: []`. No B02-specific CLI binding is configured in this
generator. The R5.16 lowerer/verifier changes and test/artifact were already
uncommitted at lock time; they are not R5.17 modifications.

## Frozen reconstruction and unchanged semantic representation

Authority: `benchmark/requirements/B02.md`, inherited `B01.md` and
`benchmark/baseline.md`, with frozen `benchmark/harness/regression.py` and
`profiles/B02.json` / `capabilities/B02.json` as applicable external
acceptance. R5.2.2 remains historical benchmark authority. R5.14's clause
table (lines 24–41) was rechecked: repeated `--tag` values, trim each value,
reject any blank-after-trim value (`invalid_tag`, no write), retain first
occurrence of each case-sensitive trimmed string in flag order, return `tags`
on every complete task, empty tags on omission/old records, and preserve
inherited B01 priority, lifecycle, queries, sorting, failures, exact field
shapes and explicit migrations. Legacy v1/v2/v3 → v4 fills missing priority,
due date and tags as applicable while retaining already-present fields and
reporting the legacy-record population; current/absent migrate returns zero.
This is **not** just the two B02-named regression methods.

| Frozen obligation | Classification | Unchanged candidate relations (R5.14 comparison) |
| --- | --- | --- |
| Repeated input, all-elements validity, ordered case-sensitive normalized tags, omitted `[]` | EXPRESSIBLE_EXISTING | #3/#4/#6, #13–17, #21–23/#45; `stable_unique(map(trim(values)))`, guarded `for_each(nonblank)`, and typed empty sequence. Same as R5.14. |
| Full fresh task inserted exactly once, returned as typed task with tags, untouched other tasks | EXPRESSIBLE_EXISTING | #1–6, #10–12/#43 exact full-record frame, #21–23/#45 typed result. R5.16's `exact_frame` is an internal encoding of this conjunction. Same assessment, now independently lowered on specimens only. |
| Explicit versioned legacy migration, preserve existing fields, default three different missing fields on the same rows, integer population result | EXPRESSIBLE_EXISTING | #21–23/#44/#30/#45, with durable version binding and field-specific typed defaults. R5.16 only lowered **one** default per collection; no semantic #31 is implied by needing three. |
| Inherited filtered/ordered reads, complete/delete, validation and typed failures, durable no-write | EXPRESSIBLE_EXISTING | #10–12, #25/#27/#43/#44/#45 with operation and state relations; abstract representation is not a generated executable or a verified binding. Same as R5.14. |
| Precedence of independently invalid create inputs, exhaustive malformed persisted-tag taxonomy | BENCHMARK_UNDERSPECIFIED | No new rule inferred; specified invalid-state and byte preservation still apply. |

No frozen clause was reclassified `CORE_SEMANTIC_GAP`. This is candidate-level
expressibility across the existing prospective inventory, **not** one accepted
integrated B02 AST. The 30 candidate constructs have not changed.

The complete intended #45 B02 relation set, stated independently of the
emitter, is: `create(input,pre,outcome,post)` branches on all tag values
nonblank after trim and inherited title/due/priority validity; success
constructs a full task with `tags = stable_unique(map(trim(input.tags)))`
(or `[]`), fresh nonempty ID, UTC creation instant and inherited defaults,
relates it to a typed task result and an exact-frame insertion into the
current v4 records, while preserving unrelated rows. Invalid branches have
typed error classifications and unchanged durable bytes. `list` selects all
records and orders `(created_at,id)`; `list-high` selects exactly HIGH then
orders; `list-overdue` selects pending, dated and strictly earlier than the
clock then orders. `complete` updates exactly one pending record while retaining
all its fields including tags; `delete` removes exactly one target and returns
that full record; failure branches preserve state. `migrate` on each legacy
v1/v2/v3 population relates the same uniquely keyed pre-rows to post-rows
with **all applicable missing** priority/due_date/tags fields defaulted,
every present field retained, post schema version 4 and
`{migrated: cardinality(pre.records)}`; current/absent migration has zero
count and unchanged/appropriate durable state. Reads of legacy state yield
`migration_required` without write. The baseline error/shape/clock/ID and
subprocess transport obligations also remain in the contract/binding, not in
test glue. This relation set is the semantic target, not a claim that
`generative_r5_13.py` accepts its full serialization.

## Unchanged-lowering attempt and mandatory halt

`benchmark/harness/test_b02_retry_r5_17.py` serializes the decisive B02
*migration slice*: a v1 typed envelope, keyed task records, the three
missing-field defaults on **one** `records` projection, the post-version
equality and #30 typed pre-population count. The test invokes the unchanged
`generative_r5_13.typed` entry point used by `render`/`generate`. The v2/v3,
absent-state, create/read/mutate and external CLI alternatives are specified
above but **not** falsely represented by this partial test serialization:
its fallback `current` is only a gate probe, not an adequate B02 migration
contract. It cannot become a candidate. In particular, one optional-field
default on v1 passes its relation shape, but the second default on the same
collection meets `_relational`'s explicit conflict check at lines 150–153:

`UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations`

The focused R5.17 test passes by checking this exact rejection. **Result:
`VALID_SEMANTICS_UNSUPPORTED_LOWERING`** (bounded checker classification),
not `INVALID_SEMANTIC_COMPOSITION`: independent missing-field defaults on
different fields commute at the abstract keyed-record level and B02 requires
them together. Nor is this a `LOWERING_ERROR` exception or `GENERATED`.
The unchanged generator has no `order` emission (`_compile` validates `order`,
`expression` raises unsupported), and its relation list has no deletion or
general multi-field lifecycle transformation. These are additional inspected
coverage limits, **not** further B02 attempts or observed B02 failures.
Type/binding support for baseline clock, IDs, CLI failures, missing file and
legacy envelope variations remains unverified at this gate. Splitting defaults
across invocations, hard-coding migration in an adapter, or silently dropping
inherited obligations would violate the frozen requirement. Integration
**halts immediately**; no compiler or semantic repair was made.

## Source authority, candidate, acceptance, grounding and conformance

The R5.17 test contains contract data plus a lowerer-rejection assertion, not
an application algorithm, task CLI, fixture-specific generator or target code.
The locked generator, runtime and verifier were inspected: there is no B02
operation-name/tag/version branch; `tag` in its contract is an outcome kind.
R5.15 normalization/record outcomes and R5.16 insertion/single-default durable
transition are generated on **other domains**. No B02 algorithm is generated,
so B02 source authority is **not established**, rather than passed. No distinct
R5.17 B02 candidate, generated operation identity, candidate provenance or
artifact integrity exists; the experimental identities in the lock are source
hashes only.

Frozen B02 acceptance against an R5.17 generated candidate: **not run**;
passed **N/A**, failed **N/A**, skipped **N/A** (no candidate). No R5.17 B02
internal event, independent public or durable observation, provenance
challenge or semantic verification exists. Ordered normalization, creation,
record-valued results and migration/default grounding cases are all **not
attempted under the halt rule**; GROUNDED + CONFORMANT, GROUNDED +
NON_CONFORMANT and GROUNDING_FAILED counts are **N/A**, not zero observed
results. Historical checkpoint replays nested in the development harness are
not acceptance of this candidate.

## R5.14 comparison, independent transfer and overfitting

R5.14: candidate semantics sufficient, R5.13 lowering failed already on
normalization and also lacked insertion/default/version/typed outcomes. R5.17:
same semantic assessment, independently expanded **general** lowering can now
emit #13–17 ordered normalization and #45 record outcomes (R5.15 media/device),
and #10–12 exact insertion plus a single #44 default with checked version/#30
count (R5.16 specimen/archive). Those are **available isolated or synthetic
composed capabilities**, not successfully transferred B02 operations. A B02
multi-default migration still rejects before generation; task list ordering,
delete and complete are not demonstrated by these studies. Cross-request B02
executable reuse remains **0 generated B02 operations, 0 grounded B02 calls**;
the R5.15/R5.16 evidence supports *potential* transfer by relation type,
not actual transfer to the frozen request. No B02-specific branch was introduced
and no task-specific glue implemented behavior; this limits evidence of
benchmark fitting, but the rejected composition prevents evidence against
overfitting from frozen B02 behavior. The compiler's one-collection-change
restriction and missing CLI binding are concrete remaining generality limits.
No numeric overfitting score is assigned.

## Separate generalization conclusions and next recommendation

- **Semantic transfer:** yes at the unchanged 30-candidate abstract-vocabulary
  level; integrated B02 AST/type validation is not demonstrated.
- **Compiler transfer:** partial general capabilities from unrelated domains
  exist; **no complete B02 behavior generated** by the unchanged lowerer.
- **Source authority:** no generated B02 behavior to attribute.
- **Acceptance:** not reached for an R5.17 B02 candidate.
- **Grounding:** no actual B02 execution to challenge.
- **Conformance:** not evaluated on B02 executions.
- **Universal correctness:** not established.

Candidate core **30**, historical raw inventory **46**, no #31 and no new
demonstrated cross-request executable reuse. Phase 5C does not automatically
advance to B03; B17 is unexposed and unclassified, the semantic-first format
globally unfrozen and R5.2.2 remains historical authority. Exact next
recommendation: preserve this clean failed retry, then in a **separate**
prospective compiler study investigate multi-field keyed defaults over one
collection, ordered query lowering and inherited lifecycle/CLI bindings on
independent non-task domains with source mutations and independent grounding;
only after independent evidence consider another explicitly authorized B02
retry. Do not repair this R5.17 attempt.

## Verification

From repository root: benchmark harness `python -m unittest discover -s
benchmark/harness -v` **160 OK** (including architecture R5.5, grounding R5.7,
semantic-prototype tests, R5.10–R5.16 focused tests and the R5.17 gate test);
application/compiler `$env:PYTHONPATH='src'; python -m unittest discover -s
tests -v` **31 OK**; focused R5.10–R5.17 file-pattern suite **101 OK**;
focused R5.17 **1 OK**. These checks include historical frozen-case replays
on saved checkpoint states; **none** is frozen acceptance against a generated
R5.17 B02 candidate. `git diff --check` and untracked-file whitespace checks
exited 0; Git separately warned about LF→CRLF conversion on working-copy
files, not test/whitespace failures.

R5_17_B02_LOWERING_STILL_INCOMPLETE
