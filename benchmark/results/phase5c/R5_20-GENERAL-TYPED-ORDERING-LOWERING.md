# R5.20 — General typed ordering lowering (prospective, 2026-10-02)

## Scope and authority

R5.20 implements generative lowering for the **existing** typed ordering
semantics on independent non-task domains, as recommended by
[R5.19](R5_19-B02-SECOND-GENERALIZATION-RETRY.md)
(`R5_19_B02_NEXT_LOWERING_GAP`). B02 is **not** used as an implementation
fixture and is **not** retried: no B02 generation to disk, execution, frozen
acceptance, grounding or conformance occurred in this experiment. R5.2.2
remains historical benchmark authority; Phase 5C remains paused; B17 remains
unexposed and unclassified; the semantic-first format remains globally
unfrozen. This record is prospective compiler evidence, not a freeze.

Changed components (working-copy Git blob identities for reference):
`benchmark/semantic/generative_r5_13.py` `42cb8eacc843dcc9773c2f47258673c0624d363f`,
`benchmark/semantic/generative_evidence_r5_13.py` `efc072e3ae27e74439f2a374e61e7ec88f54b478`,
new `benchmark/harness/test_ordering_lowering_r5_20.py` `209a1bd3e554a012610172711b4d9f596209e0e8`,
lifecycle-updated `benchmark/harness/test_b02_retry_r5_19.py` `c9acf77a0808acb4ebc0382ee69709a0326fb0d0`.
The shared validating checker
(`benchmark/semantic/typed_lowering_r5_12.py`) and the generic runtime
(`generative_runtime_r5_13.py`) are **unchanged**; HEAD is
unchanged (`c9b9e1a8b9b2c0befb4fdf9b02f734794e919fdd`).

## 1. Existing ordering semantic reconstruction

The candidate core construct is **#43 `lexicographic_order`**, inventoried in
the [selection vocabulary ledger](R5_4-SELECTION-VOCABULARY-LEDGER.md):
`Seq<Record> × ordered typed field keys × Seq<Record> -> Bool`; exact record
multiset plus ascending key order. In the unfrozen #45 contract vocabulary it
is the `{'order': {'source': <expr>, 'keys': [<field>, …]}}` expression node,
**validating-only** since R5.12 (`typed_lowering_r5_12._compile` interprets it
for supplied tuples); the R5.13–R5.18 generator rejected it, which is exactly
the gate R5.19 hit (`benchmark/harness/test_typed_lowering_r5_12.py` exercises
`order` under validating lowering only).

Property reconstruction from the existing code and records only:

| Property | Represented? | Where |
| --- | --- | --- |
| Source collection | yes | `source` expression yielding `sequence` |
| Result collection | yes | result type = source type (same element type) |
| Ordered element type | yes | keys resolve through `sequence/record` fields |
| Key field/reference | yes | flat required field names |
| Multiple lexicographic keys | yes | `keys` list; sequence is semantic |
| Ascending/descending direction | **no** | only ascending exists; no per-key direction |
| Source-relative ordering | not in #43 | #12 `source_relative` is a selection property |
| Exactness | yes | exact multiset; permutation, no loss/creation |
| Tie behavior | **not declared** | see §8; interpreters disagree |
| Stability | **no** | not a represented requirement |
| Null/missing-value behavior | excluded | optional/nullable fields are not orderable |
| Type constraints | yes | key field shape exactly `string` or `integer` |

Related but distinct representations, deliberately **not** lowered here: the
v0.3 model's `order_by` behavior field (current task-manager backend track,
not the #45 contract vocabulary), `state_relations.lexicographic_order`
(R5.4 witness relation), #35 `sorted` (finite-scenario observation operator),
and #12 `source_relative` (selection occurrence order). No semantics were
invented for unrepresented properties.

## 2. Supported generative subset

`generative_r5_13.ordering_plan(node, slots)` defines the R5.20 subset:

- **SUPPORTED KEY TYPES**: required `string` and `integer` fields of the
  sequence's record element type (identical to the locked validating
  interpreter; booleans, optional, nullable, sequence and record fields are
  not orderable).
- **SUPPORTED DIRECTIONS**: none representable; ascending implicit. Any
  `direction`-shaped addition rejects as `invalid ordering`.
- **SUPPORTED COLLECTION TYPES**: `sequence` of `record` reached from the
  `input`/`pre` contract slots, including sequences produced by already
  generative expressions (e.g. exact `select`).
- **UNSUPPORTED ORDERING SEMANTICS**: per-key direction; ordering a
  quantifier-local (scoped) binding — `UNSUPPORTED_LOWERING_CAPABILITY: order
  (scoped source)`; non-record or non-sequence sources; empty key lists;
  tie-breaking beyond the declared keys; stability as a requirement. Repeated
  keys are tolerated as redundant projections because the validating
  interpreter tolerates them; emission behaves identically and is not
  redefined.

Safe rejection is used everywhere the semantics authorize no behavior.

## 3. Target-independent ordering plan

Flow: semantic order relation → validate collection element type (`_compile`
of `source` must yield `sequence`) → validate each key reference and type via
`_field` → canonical plan `{'element': <record shape>, 'keys':
[(field, type), …]}` with the **key sequence preserved** → backend emission.
The plan holds no Python constructs; the Python backend (`expression`/`render`)
is the sole consumer so far and emits one `sorted(..., key=lambda …)` per plan.
Nothing in the plan encodes Python sorting behavior as meaning: the relation's
checkable content (§8) is evaluated independently of the emitted call. A second
backend could consume the same plan in principle; that portability is a design
claim, not a demonstrated second backend.

## 4. Synthetic non-task domains

Two independent domains satisfy the requirement:

- **media assets**: `asset_id`, `title` (string), `year`, `shelf` (integer);
  read-only ordered listing over a durable typed population.
- **device inventory**: `serial`, `model`, `site` (string), `installed`,
  `warranty` (integer); ordered listings, selection+ordering and guarded
  compositions.

Field identities appear **only** inside contract data. The lowerer contains no
domain vocabulary (§18 audit).

## 5. Single-key results

Ordering media by `title`: already-sorted, reversed and arbitrary permuted
inputs all execute to `Apple, Mango, Zephyr` through real subprocess calls;
empty and one-element populations return unchanged permutations; the
inapplicable-request branch (`unavailable`) grounds with untouched bytes.
Ordering by integer `year` with duplicate values (2001 twice) yields a
grounded, conformant nondecreasing permutation. Observed order is derived from
the semantic relation (typed keys from `pre`), not hand-written: the fixture's
independent expectation is the sorted key sequence itself.

## 6. Multi-key (lexicographic) results

- Two keys `(site, serial)`: the three Widgets tie on `site`; `serial` decides
  (`S1, S2, S9, S5`). Grounded and conformant.
- Three keys `(site, installed, serial)`: `(north, 90)` tie decided by the
  third key (`S2, S9, S1, S5` on the tie-modified population).
- Four-key plan `(site, installed, warranty, serial)` executes and conforms.
  The same planner/emitter path handles 1/2/3/4 keys; nothing branches on the
  key count (`ordering_plan` returns N pairs; emission projects all N).

## 7. Direction results and limitations

Direction is **not represented** by the current semantic model, so none was
implemented. A contract adding `direction` rejects as `invalid ordering` before
generation; the plan carries no `direction`; normal artifacts contain no
`reverse`. Mixing ascending and descending keys is therefore out of the
expressible vocabulary — a documented language limitation for later semantic
review, not a lowering defect.

## 8. Tie/stability analysis

The relation's checkable content is: result is a **multiset permutation** of
the source with **nondecreasing key tuples**. Fully tied elements are therefore
**unconstrained** by the declared semantics. Two pre-existing interpreters
disagree beyond that: the locked validating lowering computes a *stable*
Python `sorted` (a deterministic tie choice), while the separate R5.4
`state_relations.lexicographic_order` witness requires *strict* adjacency,
which makes tied-key populations unsatisfiable there. R5.20 documents this
divergence; it repairs neither and invents no tie rule.

Consequently the grounded conformance path (`conforms` →
`_ordered_relation_holds`) judges an ordering-valued outcome by the relation,
so it **does not reject** either tied permutation merely because Python chose
one. Both permutations of a tied population ground and conform. Backend
determinism is separately *observed* (stable output across runs) but is not
asserted as semantics. Implementation determinism ≠ semantic requirement.

## 9. Type-safety results

All rejected by explicit lowering/type diagnostics during `typed()`
verification, before any artifact exists: key absent from the element type
(`invalid typed field reference`), non-string key (`invalid ordering key`),
empty key list (`invalid ordering`), extra `direction` (`invalid ordering`),
ordering a non-sequence (`ordering needs a sequence`), ordering a
sequence-of-strings (`invalid typed field reference` at key resolution),
sequence-valued key field (`non-orderable key`), and result element-type
mismatch (`outcome payload type mismatch`). Ordering a quantifier-local source
rejects at emission with `UNSUPPORTED_LOWERING_CAPABILITY: order (scoped
source)`. No case relies on Python runtime errors, and no rejection falls back
to source order.

## 10. Semantic-only mutation results

Changing only contracts — primary key `title`→`year`, narrowing devices to
`(site)`, widening to `(site, serial, installed)`, swapping key order — and
regenerating changes the observed executable order accordingly
(`a2,a3,a1` by title; nondecreasing years with free ties; `S1,S2,S9,S5` vs
site-only groups). No lowerer, runtime or evidence file was edited in these
steps; the same session runs old and new mutations side by side.

## 11. Serialization independence

A contract rebuilt with swapped dictionary key order inside the order node and
envelope serializes to **identical canonical bytes, identical contract digest
and identical generated artifact** (`canonical` sorts object keys). The
`keys` **list** order is semantic and is never canonicalized: `(year,title)`
vs `(title,year)` produce different digests, different bytes and — on the
crossed population — different observed orders (`a4,a2,a3,a1` vs
`a2,a4,a3,a1`). Key-sequence rotation also changes the emitted projection.
Reordered record multiplicity comparison inside conformance uses canonical
per-row bytes, so field serialization order cannot masquerade as meaning.

## 12. Selection + ordering composition

`order(select(pre, item.model == 'Widget'), (site, serial))` compiles,
executes and conforms with **no selection+ordering-specific domain code**: the
Gadget record is excluded, the remaining records are reordered by the
secondary key, and the source-relative property of #12 is not required for
correctness after sorting. All three existing expression classes compose
through unchanged emission paths.

## 13. Typed record composition

Ordered collections cross the operation outcome/public boundary as JSON arrays
of full records with native field types (`str`/`int`), validated by the
generic runtime against the declared `value_type`. Nothing was flattened to
display strings.

## 14. Durable state / read-only behavior

The listing branches use the existing `preserve` transition. For an
intentionally unsorted stored population, generated execution returns the
ordered view while `state.json` **before and after bytes are equal** and the
event records `attempted_write: false`; the stored order is provably not
rewritten. Semantics require no persistence reordering, so none is generated.

## 15. Grounding results

Every executed case runs the generated program as a subprocess and is
challenged by `observe`/`challenge`: internal event (input/pre/post/outcome/
write), independently captured public stdout, independent durable-file
readback, and provenance digest challenge (contract/artifact/runtime/
generation). Test-side expectations compute the ordering independently; the
independently observed returned order matches the actual generated public
result in all grounded cases.

## 16. Conformance and fault results

Two disposable lowering faults (emitter-only, semantics untouched):

- single-key **reversal** fault: faithfully executes, grounds (`provenance_valid
  True`, `grounded True`), returns `Zephyr, Mango, Apple`, and fails semantic
  conformance (violates nondecreasing keys).
- multi-key **dropped-secondary** fault on `(site, serial)`: executes, grounds,
  keeps `site` nondecreasing but returns `S9` before `S2` inside the tie —
  conformance fails. A silently dropped secondary key cannot pass the
  relation.

Expected semantics were not modified to obtain these failures.

## 17. Novel composition

A new combination absent from the first ordering fixture composes without any
lowerer modification: a `cardinality(select(...)) == 3` guard **and**
`order(select(pre, not Gadget), (site, installed, serial))` producing a typed
record-collection outcome; it grounds and conforms (`S2, S1, S9`).

## 18. B02 contamination audit

Automated source audit (`test_lowerer_contains_no_task_b02_or_benchmark_
vocabulary`) scans the general ordering machinery for quoted task/B02 field
literals (`'created_at'`, `'priority'`, `'due_date'`, `'tags'`, `'status'`,
`'NORMAL'`, `'HIGH'`, `B02`, `tasks.json`, `schema_version`, `insert_task`) and
for the two fixture domains' field names; none occur in
`generative_r5_13.py` or `generative_evidence_r5_13.py`. Manual review confirms
no `(created_at, id)` hard-coding, no B02 command or benchmark paths, no
expected-ordering constants and no task record assumptions: ordering data
arrives only through contract keys, slots and shapes. The R5.19 historical
probe's updated assertion is test lifecycle (see below), not fixture use.

## 19. Coverage matrix (generative lowering)

| Capability | Represented | Validating lowering | Generative lowering | Grounded | Fault-tested | Benchmark transfer |
| --- | --- | --- | --- | --- | --- | --- |
| Single-key order (string/int) #43 | yes | yes (R5.12) | **yes (R5.20)** | yes | yes | **NO / NOT YET TESTED** |
| N-key lexicographic (N≥1) | yes | yes | **yes** | yes | yes | NO / NOT YET TESTED |
| Direction | no | no | no (rejects) | N/A | rejection-tested | N/A |
| Tie/stability requirement | no | interpreter-only | not required; relation-checked | yes | yes (both perms) | N/A |
| Order ∘ exact selection | yes (#10–12/#43) | yes | **yes** | yes | yes | NO / NOT YET TESTED |
| Order-valued typed records | yes (#45) | yes | **yes** | yes | yes | NO / NOT YET TESTED |
| Durable read-only ordering | yes (preserve) | yes | **yes** | yes | yes (bytes equal) | N/A |
| Ordered normalization (R5.15) | yes | yes | yes | yes | yes | NO / NOT YET TESTED |
| N-way defaults (R5.18), frame (R5.16), migration (R5.16), #30 count | yes | yes | yes | yes | yes | slice-level only |

Benchmark transfer for ordering remains **NO / NOT YET TESTED** because R5.20
must not retry B02. The R5.19 historical test now asserts only that the
*current* lowerer types and renders its locked B02-shaped probe; the R5.19
halt artifact and classification stand unchanged, exactly following the
R5.17/R5.19 test-lifecycle precedent. Rendering bytes in memory is not a
candidate, acceptance, grounding or conformance result.

## 20. Construct accounting

Candidate core semantic count remains **30**; historical raw inventory remains
46. No construct #31: the planner, emitter branch, relational conformance path
and tests are unnumbered compiler/evidence machinery over existing #43, like
R5.15–R5.18 additions.

## 21. Verification record

- R5.20 focused: **18 run, 18 passed**.
- Full benchmark harness: **183 run, 183 passed, 0 failed** (R5.19 recorded
  164 pre-lock; the R5.19 focused test and the 18 new R5.20 tests account for
  the difference).
- Application/compiler suite: **31 passed**; `validate` and `safety`: ok.
- Focused `test_*r5_1[0-9]*` R5.10–R5.19 pattern: **32 passed**.
- R5.12 typed lowering **3**, R5.7 grounding **10**, R5.11 integration **4**,
  R5.8 conditional outcomes **3**, R5.5 architecture **6**, semantic-prototype
  pattern **33**: all passed.
- `git diff --check`: exit 0. Separately reported **line-ending warnings**
  (Git LF→CRLF notices on touched/new files) — warnings, not failures.

## 22. Recommendation for the next step

Preserve this record and the updated working copy, then perform a
**separately locked third B02 retry** against the current architecture. Do not
fold ordering-specific repairs into that retry. Independently and in separate
experiments: direction semantics (requires semantic review, not lowering),
scoped/quantified ordering, mixed collection transforms, and lifecycle/CLI
binding remain open; none blocks the ordering slice studied here.

## Gate

Ordering lowering transfers R5.19's decisive gap: the existing #43 relation now
drives general generated executable ordering over two independent non-task
domains, for one, two, three and four keys, composed with exact selection and
typed record outcomes, read-only over durable state, grounded through
independent public and file observation, with conformance faults that faithfully
execute yet fail semantics, and with no B02-specific lowering anywhere.
Unrepresented properties (direction, tie stability) reject explicitly rather
than silently. No important *represented* ordering form remains validating-only.

UNIVERSAL_IMPLEMENTATION_CORRECTNESS_ESTABLISHED = NO
Candidate core semantics: 30. B02 not retried. Phase 5C paused. B17 unexposed
and unclassified. R5.2.2 historical authority. Format unfrozen.

    R5_20_ORDERING_LOWERING_VALIDATED
