# R5.15 — General lowering coverage expansion (prospective, 2026-10-02)

**Decision: partial.** This is compiler research on synthetic media, device and
library data, not a frozen-request execution. R5.14's generative gap is the
starting point; its B02 result and R5.2.2 historical authority are unchanged.
The candidate vocabulary remains **30 core**. No construct #31, semantic
expansion, candidate benchmark executable or semantic-first freeze was made.

## 1. Capability matrix before implementation

| Capability / existing relation | Lowering responsibility | Runtime, types and state needed | Initial status |
| --- | --- | --- | --- |
| Ordered normalization: #13 trim, #15 map(trim), #16 stable_unique with case-sensitive #6, #17 for_each/#14 nonblank; #45 binds input/outcome | Emit operations from the source sequence and guard each element; preserve first normalized occurrence | Finite ordered string input, typed sequence result, Boolean branch; no state required | Interpreted on supplied invariant tuples, not generated |
| Insertion/frame: #10–12 exact selection of target and outside-target population, #43 complete-record order/equality, #6 and #21–23/#45 same operation tuple | Construct a post-state satisfying *both* exact singleton target and unchanged outside-target constraints, with identity freshness | Typed full records, identity, pre/post collection and durable state; exactness and ordering cannot be discarded | Abstract **composition hypothesis** in R5.9, not one integrated typed lowering rule |
| Default/version transition: #44 keyed missing-field default and identity preservation, #21–23 applicability, #30 cardinality and #45 outcome | Fill missing fields without replacing present fields; bind applicability/version and numeric outcome | Optional typed field, unique string identity, collection, versioned state and durable write | #44 has a separate witness evaluator; R5.13 rejected its transition |
| Typed record outcome: #1–6 typed record, projection/equality and #45 conditional alternatives | Construct/check the selected branch's payload, including every record field | Per-branch payload shape, typed expressions and runtime check before persistence | R5.13 emitted only string payloads |

These rows distinguish semantic inventory from a validated integrated contract.
No new transition meaning is inferred from a convenient target algorithm.

## 2–6. Implemented lowering and independent domains

`typed_lowering_r5_12.py` now checks typed trim/map(trim)/stable_unique,
nonblank/for_each and record construction. `generative_r5_13.py` emits the
corresponding operations, with the same case-sensitive first-occurrence
semantics as `invariants.py`; no supplied Python expressions execute as contract
data. Media catalogue input supplies any finite sequence of titles; a guarded
success returns a typed catalogue record containing the trimmed stable-unique
sequence, while blank entries select a different string-valued outcome. Tests
cover lengths 0, 1, 3 and 43, duplicates, pre-normalized input, order and
case distinctions. Bound semantic names are mapped to compiler-owned target
locals (including a tested target-language reserved word), not emitted as raw
code. Finite samples are not a proof over all lengths.

Device service input names a serial and destination; its typed success record
projects both input fields, its missing case returns a string, and its existing
keyed state replacement preserves an unrelated device. Branches may now declare
`value_type` (old contracts retain their implicit string); the generic runtime
checks selected payload shape **before** writing, and the independent verifier
checks it again against the originating contract.

Library holdings use #44's bounded `default_missing` transition: a uniquely
keyed string identity, one optional string/Boolean field, a statically typed
literal default, and records retaining order and every already-present field.
An `edition` input guard selects the transition, and #30 returns the pre-state
population count on that branch. Empty and mixed missing/present populations,
duplicate-identity rejection, unchanged branch bytes and identity/present-field
preservation were exercised. This is **not** a full state-version migration:
the edition is an invocation input, not checked against a durable versioned
envelope; no version change or multiple-field transition is generated. The
current optional-field representation is type metadata for the existing #5/#44
relation, not a new core construct. Defaults are restricted to typed constants
of the already supported #44 string/Boolean kinds.

## 4 and 7–9. Insertion, composition and semantic mutations

**Insertion remains unsupported.** R5.9:68–96 gives exact selection and
outside-target framing as an abstract composition hypothesis, not a validated
constructive relation in the current #45 typed AST. The current transition
checker rejects an `insert`-shaped state relation with
`UNSUPPORTED_LOWERING_CAPABILITY`; it does not implement `insert_task`, append
records while ignoring the frame, or claim that replacement tests demonstrate
insertion. Empty/nonempty insertion, target freshness, duplicates and wrong
replacement/deletion therefore have **no generated witness**. This is a
lowering-coverage/integration gap, not evidence that #10–12 are incoherent.

A **library** contract assembled entirely from supported relations combines
three *newly lowered* capabilities: for_each plus ordered normalization of
marks, #44 keyed default of holdings, and a record-valued result containing
both normalized marks and #30 count. It compiles with no composition-specific
lowerer edit; invalid marks take the unchanged/error branch. A separate novel
structural combination adds normalization inside a device operation's
cardinality guard (alongside existing select), and projects the normalized
array inside its typed record while replacing a state field. It also compiles
unchanged. Neither composition includes insertion or a durable version update.

| Semantic-only edit; lowerer/runtime unchanged | Observed regenerated result |
| --- | --- |
| Media outcome `stable_unique(map(trim(input.titles))` → `stable_unique(input.titles)` | `[' X ', 'X']` now remains two entries instead of one `['X']` |
| Device result `location ← input.location` → `location ← input.serial` | Record success field changes from `east` to `A` |
| Library #44 default `reserve` → `archive` | Only absent shelves receive `archive`; present shelves survive |

## 10–14. Unsupported, typing, grounding, conformance and authority

Unknown state relations and unintegrated #44 list-shaped transition/check
forms reject explicitly; unimplemented existing operators such as graph and
ordering still raise `UNSUPPORTED_LOWERING_CAPABILITY` at generation. They are
not silently omitted. Bad normalization source, invalid cardinality on scalar,
bad record payload mapping/declared shape and wrong default type reject before
normal execution. Runtime rejects a disposable malformed record payload before
durable write; duplicate #44 identities reject before write. This is bounded
type preservation, not a complete static proof of arbitrary relation composition.

Each successful synthetic execution uses the R5.13 provenance manifest,
generation digest, internal invocation/pre/post/outcome/write event, independent
subprocess stdout/exit and reopened raw durable file bytes. `challenge` checks
integrity and cross-observer agreement **before** `conforms` interprets the
originating typed contract. Media, device, holdings and composed successes are
grounded and conformant in tested cases. A disposable device *lowering fault*
retains the old location instead of replacing it: public output, file and event
agree and integrity is valid (**grounding succeeds**), while contract
conformance fails. A malformed target's payload is rejected before persistence;
this is a runtime-type test, not the grounding/conformance fault. The shared
AST checker/emitter/verifier can still have common-mode mistakes; grounding
does not establish universal correctness.

| Capability | Source authority classification | Why |
| --- | --- | --- |
| Ordered normalization | SEMANTICALLY_DRIVEN (bounded supported shape) | Semantic expression mutation changes generated sequence behavior |
| Collection insertion | UNSUPPORTED | No integrated constructive lowering; no generated insert |
| Default-only keyed transformation | PARTIALLY_SEMANTICALLY_DRIVEN | Changing #44 literal changes durable results; checked durable version transition/multiple defaults absent |
| Typed record outcome | SEMANTICALLY_DRIVEN (bounded supported shape) | Typed record field mapping mutation changes generated public payload |

The four-capability target **SEMANTICALLY_DRIVEN** is not met.

## 15–18. Audit, coverage ledger and construct accounting

New compiler behavior was inspected for task field names, task operations,
task-tag fixtures, frozen identities, version numbers, migration constants,
expected benchmark output shapes and command-specific branches. **No B02
specialization found.** `tag` in the generator means a generic #45 *outcome
alternative*, not a task label. Domain names and values live in disposable
synthetic test data. The R5.13 runtime filename is retained for compatibility.

| Semantic capability | Representation exists? | Validating lowering | Generative lowering | Grounded | Fault-tested |
| --- | --- | --- | --- | --- | --- |
| #13–17 ordered normalization | yes | yes, bounded typed AST | yes | yes | device fault in composed environment; no normalization-specific fault |
| #10–12/#43 framed insertion | abstract hypothesis | no integrated checker | no, explicit rejection | no | no |
| #44 missing-field default | yes | yes, bounded one-field check | yes, one optional string/Boolean field; **not versioned** | yes | not independently fault-injected |
| #30 count in a default outcome | yes | yes | yes | yes | no dedicated count fault |
| #45 record-valued alternative | yes | yes, branch-specific shape | yes | yes | device replacement fault and runtime malformed-payload rejection |

**Raw categorized machinery entries (prospective, not core additions):** typed
normalization/record AST checking and Python emission; optional-field #44
checking/emission; per-alternative runtime payload validation; extended
contract verifier; three synthetic domain fixtures and mutation/fault tests;
existing lineage, subprocess observer and durable-state challenge reused.
The historical **46 raw numbered entries / 30 candidate core** inventory is
unchanged; new machinery is unnumbered implementation/evidence accounting.

**Recommendation:** keep Phase 5C paused. Next independently validate a
target-neutral exact-selection/identity/frame contract in the same typed #45
AST, then test its constructive insertion lowering and a checked durable
version transition on new non-task domains before any frozen B02 retry. Do not
add #31 or weaken unsupported relations to force generation. B02 was not
retried against this generator; B17 is unexposed/unclassified; R5.2.2 remains
historical benchmark authority and the semantic-first format is globally
unfrozen.

Verification: `python -m unittest discover -s benchmark/harness -v` **155 OK**
(includes architecture R5.5, grounding R5.7, semantic prototypes, focused
R5.10–R5.13 and six R5.15 tests); application/compiler suite **31 OK**;
model validate and safety **OK**. Nested historical harness replays include
saved B02-stage checkpoints; they are **not R5.15 generated-B02 acceptance**.
`git diff --check` exited 0. Git separately warned about LF→CRLF conversions
of previously modified tracked files; those warnings are not failures.

R5_15_GENERAL_LOWERING_PARTIAL
