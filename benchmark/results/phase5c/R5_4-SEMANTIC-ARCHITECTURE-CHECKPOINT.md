# R5.4 semantic architecture checkpoint — prospective, 2026-10-02

**Boundary:** R5.2.2 remains authoritative; B01 remains semantically inadequate
and the adequacy restart is halted there. The semantic-first format is UNFROZEN;
Phase 5C does not resume; B17 is unexposed and unclassified. This is an
architectural assessment, not a B01 repair, a new acceptance oracle, or an
amendment to frozen requests/cases. Sources: `benchmark/baseline.md`, frozen
`benchmark/requirements/B01.md` and B02–B16, `benchmark/README.md`,
`benchmark/semantic/{README.md,operation_contract.py,probe.py}`,
`R5_4-SELECTION-VOCABULARY-LEDGER.md`,
`R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md`, and the R5.2.2 corrected
post-B16 continuation. The current repository harness baseline is 109 tests;
verification of this checkpoint is recorded below.

## 1. Current architecture and trust boundary

```
 frozen B01–B16 requirement + inherited baseline [authoritative intent]
       | interpretation [human/reviewed; NOT mechanically complete]
       +--> Track B: air/task_manager.json [canonical current model]
       |       -> src/air_compiler validation/lowering -> generated/task_manager.py
       |          [model/schema checked; generated behavior not proven]
       +--> R5.4: benchmark/semantic/prototype.json, typed relation fixtures
       |       [selected semantic representation; separate validators]
       |       -> scenario compile_plan [structural checks] -> finite probe plan
       +--> Track A: benchmark/conventional/task_manager.py [Python source]
       |                     |
       +--> R5.2.2 external acceptance cases [independent finite oracle]
                             |
     public subprocess CLI(command, args) -> actual runtime input
              -> application <-> tasks.json in isolated working directory
              -> exit/status + JSON stdout result OR JSON stderr error
                             |
          external oracle / R5.4 probe: capture outcomes, selected file
          snapshots; compare observations [finite, checked per execution]
```

The **plan** has two distinct meanings: hash-pinned `experiments/` model-change
plans and R5.4 scenario plans compiled from selected records. Neither is an
operation contract nor a proof. A frozen behavioral requirement lives in
`benchmark/requirements/` plus `benchmark/baseline.md`; the corrected R5.2.2
acceptance boundary lives in `benchmark/results/phase5c/` and harness methods.
Current task-manager semantics live in `air/task_manager.json` and versioned
language documentation; prospective semantic requirements and fixtures live in
`benchmark/semantic/`. The generated implementation is `generated/task_manager.py`
(and pinned snapshot copies for post-B16 histories). The public API is the
subprocess CLI; arguments are actual runtime input, not a fixture's `input`.
Persistent storage is `tasks.json` across processes, not just an in-memory
record collection. Return and error are distinct observable exit/stream/JSON
outcomes. The acceptance oracle is the independent harness with the corrected
R5.2.2 carriers; an R5.4 scenario is a finite `seed`/`invoke`/`snapshot`/`observe`
witness. A semantic fixture is a supplied typed tuple tested by a relation
interpreter; an implementation test is a subprocess acceptance/regression test
or a test of compiler/prototype mechanics. A green prototype test does not turn
its fixture into a grounded implementation test.

Trust is explicit: frozen text and independently frozen oracle are *authorities*
for benchmark intent/finite acceptance, not proofs of completeness. Model-to-
requirement interpretation, scenario coverage, adapter fidelity, and compiler
correctness are currently trusted or separately reviewed, not established by
the tuple checker. Validators check local syntax, references and some relation
types; they do not bind their slots to the CLI. The external harness checks
actual subprocess outcomes and observable state on its chosen inputs. The R5.4
probe captures success/error and snapshots for selected cases on disposable
post-B16 snapshots, but it does not feed a universal stream of actual tuples to
#45. Even an independently passing harness certifies only its executed cases.

## 2. The grounding gap: five separate obligations

1. **Express:** specify a typed predicate `C_O(I,S,R,S')` over applicable
   operation invocations, including success/error alternatives, state validity,
   effects and any external clock/ID observations.
2. **Bind:** declare a checked interface mapping from operation `O` and its
   abstract input/state/outcome types to the public entry point, argument
   presence, state view and result/error shape. The mapping must cover the
   invoked boundary, not let a witness choose its own convenient rows.
3. **Observe:** for *one* invocation, capture actual arguments, persisted bytes
   or justified state projection before, complete exit/stdout/stderr outcome,
   and persisted state after, under the same storage namespace; retain ordering
   across processes and environment/capability inputs where relevant.
4. **Verify:** check that the observation is well formed, that the mapping is
   faithful, and that `C_O` holds for the observed tuple; reject missing or
   incomplete observations and assess the coverage of attempted invocations.
5. **Prove:** a universal conformance claim additionally needs a sound argument
   for *all reachable valid states and applicable inputs*, totality, error
   paths, adapters, effects, and composition—not just passing executions.

`operation_contract.py` uses a literal operation name and supplied
`input.rows`, `pre.records`, `result`, `post.records`. Its seven fixtures
distinguish right-result/wrong-state, right-state/wrong-result and other wrong
tuples, but no call occurs there. In particular, its `input.rows == pre.records`
and `result == post.records` are properties of `upgrade_items`, not universal
CLI laws. `probe.py` independently invokes real commands and can snapshot
`tasks.json`, but its scenario-specific comparisons do not establish the
abstract-to-public mapping or universal coverage. Thus `relation(I,S,R,S')`
does not imply any of `I = actual invocation input`, `S = actual pre-state`,
`R = actual outcome`, `S' = actual post-state`—nor that all four came from the
*same* call. Decoded record equality alone can miss forbidden byte writes.

Diagnosis: **B + C + D + E**, with **F** necessary only for a universal
implementation theorem. B is absent checked interface/storage projection
metadata; C is absent lowering of such metadata into an adapter or generated
boundary; D is absent generic actual-call/pre/post observation; E is absent
trace-to-contract conformance checking and coverage. **A is not established as
the cause of grounding**: the abstract operation relation is a plausible
semantic concept, although the currently separate type validators and missing
success/error/state semantics need design work. Missing create/update/frame
relations are *separate* potential semantic expressiveness gaps, not evidence
that CLI instrumentation belongs in the language. Universal quantification in
a contract expresses an obligation; it cannot by itself discharge F.

## 3. Competing grounding architectures

| Criterion | A: language owns grounding | B: compiler owns grounding | C: runtime/verifier owns grounding | D: hybrid |
| --- | --- | --- | --- | --- |
| Language complexity | High: command/storage/trace vocabulary enters source | Low: abstract contracts | Low: abstract contracts | Low: abstract contracts; checked binding outside core |
| Implementation freedom | Low if source names CLI/files | Moderate: lowering must support alternate representations | High in contract; observer must discover boundaries reliably | High behind declared interface/state projection |
| Python/future-language portability | Low unless every backend adopts CLI/storage syntax | Metadata and compiler adapter per backend | Observer adapter per backend; inferred mapping is fragile | Portable contract + backend-specific binding/observer adapters |
| Incorrect persistence / right return, wrong state / failure writes | Detectable only if language grounding is faithfully implemented; source declarations alone prove nothing | Not detected by metadata/lowering alone; generated enforcement can help only with trusted compiler/storage adapter | Detected **on observed calls** if complete before/after snapshots include relevant bytes and error outcomes | Detected **on observed calls** with static state boundary + independent byte/effect observation |
| Migration | Must encode storage versions/commands in core | Abstract state evolution maps through versioned lowering; adapter needed to check real bytes | Can observe before/after versions, but needs a reliable schema/state interpretation | Abstract versioned relation + declared version mapping + observed actual before/after |
| Runtime instrumentation | Required for executable conformance unless formal proof replaces it | Optional for generation, required for independently observed conformance | Essential; wrapper/snapshot sufficient for bounded CLI, deeper effects need hooks | Essential for finite conformance; selected boundary can use black-box snapshots |
| Arbitrary valid inputs | May state them universally, not verify all by declaration | May generate generic behavior, but no independent universal guarantee | Can evaluate any *supplied* valid input; no exhaustive reachability by default | Same; bindings do not enumerate the domain |
| Finite vs universal | Semantic assertion is not a proof | Compilation is not automatically a proof | Finite traces never imply universal proof | Same; proof requires separate soundness obligations |
| Benchmark overfitting | High: B01 command/file syntax in language | Medium: lowering templates may encode fixture expectations | Medium: observer can target only known examples | Lower if operation/state interface is general and evidence selection is separately audited |

**Recommendation: D as a design hypothesis**, with B's checked static mapping
and C's independent observation; not a claim that it already works. A conflates
intent and deployment. B alone trusts generation and misses independent
observation. C alone needs an unexplained way to identify the correct input,
storage boundary, error and persistence view; arbitrary snapshots are not a
faithful binder. A generic operation signature/state-view mapping with
backend-specific adapters is smaller than a command-specific semantic DSL.
For a single-file CLI, a wrapper can capture before/after bytes without
instrumenting application internals; multi-resource/concurrent effects require
stronger coverage, isolation and an explicit observational scope. An observer
that shares a buggy implementation's own state projection is not independent.

## 4. Contract versus conformance evidence

**CONTRACT** is a typed, potentially universally quantified requirement over
applicable operations and reachable valid states: for each invocation, its
actual outcome and resulting state must satisfy the relation. It describes
allowed behavior; it does not create observations. **EVIDENCE OF CONFORMANCE**
is an observation, test result or sound derivation about an implementation,
tagged with mapping, observer, state coverage and assumptions. An observed
tuple is a witness about that invocation, not a proof that all tuples comply.

| Evidence | Permitted claim (subject to faithful binding and checks) |
| --- | --- |
| One semantic fixture | The relation evaluator accepts/rejects that supplied tuple; no application claim. |
| Many semantic fixtures | Broader sampled interpreter discrimination; no application or universal claim. |
| Acceptance tests | Implementations satisfy the executed frozen cases under that oracle and environment; not complete frozen-text equivalence. |
| Property-based tests | Conformance for generated cases, distribution/seeds and assumptions recorded; no universal result merely from many samples. |
| Runtime traces | Contract holds/fails for captured actual calls, states and effects within observer coverage; an omitted call/effect invalidates a blanket claim. |
| Static analysis | Only properties justified by its stated soundness, abstractions and trusted assumptions; warnings/absence of warnings alone prove nothing universal. |
| Exhaustive finite-domain checking | Universal over the **explicitly bounded**, fully enumerated input/reachable-state domain, given sound mapping, transition and environment model; not unbounded behavior. |
| Formal proof (future, if supported) | A theorem over a specified scope only after sound contract semantics, compiler/runtime/adapters, reachability, totality and implementation correspondence are discharged or explicitly trusted. |

## 5. Is #45 semantic? Vocabulary by responsibility

Yes, the *relation* `operation : (I,S) -> (Outcome,S')` is reusable across
CLIs, function calls, storage engines, databases and benchmarks: it constrains
an atomic abstract state transition and its externally visible result, with
success/error variants, without prescribing an algorithm or representation.
Its minimal underlying concept is a typed before/input/outcome/after relation
with an operation identity and applicability domain. An operation contract can
compose that relation with selection, equality, defaulting, frames and other
domain constraints. The proposed *universal actual-operation binder* in the
old #45 description is **not** that relation: it spans interface metadata,
observation, verifier and ultimately proof. No freeze of #45 follows.

The following accounts for **every one of the 45** ledger entries exactly
once. Counts are bookkeeping for candidate responsibility, not a claim of
minimality or completed integration:

| Responsibility | IDs (count) | Architectural reading |
| --- | --- | --- |
| Domain/data semantics | #1–8 (8), #13–14 (2), #25–27 (3) | Record shape/projection, values, booleans, strings and typed time operations; #25's parsing may need separation from observation of a field. |
| Collection/graph relations | #9–12 (4), #15–20 (6), #43 (1) | Membership, exact selection/order, normalization, graph update and acyclicity. #11–12 are independent obligations, though future encoding may merge them. |
| State relations and scoped constraints | #21–23 (3), #44 (1) | Before/after, applicability, bounded scope and keyed missing-field default. #23 is a bounded semantic quantifier, not a finite test runner. |
| Abstract operation contract | #45 (1) | Only the typed relation and applicability/outcome obligation; its advertised actual-call binder is misplaced. |
| Finite observation/evidence machinery | #24 (1), #28–36 (9) | Clock read by controlled adapter; scenario, seed, invoke, snapshot, observe, ref, list, sorted, distinct are witness/probe operations. #34–36 can resemble core list/order/inequality, but here operate on *observed fixture values*, not general contracts. |
| Benchmark evolution/administration | #37–42 (6) | Adds/retains/replaces/depends_on/when/carrier select and track historical acceptance roots; #40 can have a general requirement-dependency analogue, but its present achieved-history composer is not a domain semantic operator. |

**Raw prototype count: 45. Candidate core semantic count: 29** (#1–23,
#25–27, #43–45), counting #45 only after separating its semantic relation
from grounding. Excluded: ten finite-observation constructs (#24,#28–36)
and six administrative constructs (#37–42). No entry currently supplies a
general checked compiler/interface mapping; command allowlists, `tasks.json`
paths, subprocess/clock adapters and verifier comparison behavior live in
prototype code but are **not** separate ledger numbers. The candidate 29 are
still provisional, possibly redundant and not one integrated schema; a core
count is neither an adequacy score nor license to remove time/observation
concepts needed at an interface. Generic time and effects can have semantic
types while *reading a concrete clock* belongs to the capability/observer
boundary. A general version-evolution relation belongs in state semantics;
benchmark supersession lineage (#37–42) is not application migration metadata.

## 6. B01 unresolved issues: assign ownership, do not repair

| Issue | Likely owning layer(s) | Boundary of present conclusion |
| --- | --- | --- |
| All actual public calls | Compiler/interface binding + runtime observation + verifier; proof machinery for universal conformance | Contract quantification is semantic, not a magic call interceptor. |
| Persistent pre/post state | Interface storage projection + runtime observation + verifier | Check byte-level no-write where required; sequential invocations need shared persisted namespace, not a new semantic binder. |
| Create insertion | Semantic contract / domain model | Fresh key, exact added record and frame are genuine relational obligations, separate from grounding. |
| Completion framing | Semantic contract / domain model | Target update, unchanged other fields/records and outcome are abstract state rules. |
| Migration outcome and version | Domain model + semantic contract, then compiler version mapping + runtime observation/verifier | #44 alone neither binds the current version nor checks result count and bytes. |
| Priority domain / “above HIGH” | Benchmark-text ambiguity + domain model, unresolved | Round-trip and exact-HIGH membership are observable; independent ordinal comparison is not specified. |

## 7. Cross-clause pressure test (only exposed B02–B16)

One static signature/state-view binding and one observer tuple shape should
cover: create/default/migration for B02/B04/B06/B10 and B16 `create-user`;
read-only `list-users`/ordinary lists (B16 and baseline); filtered queries
B03/B05/B06/B09/B10/B12, with `S' = S` and observable clock for B12;
mutations B07/B08/B11/B13/B14/B15, including linked entities; no-write error
outcomes throughout; and versioned migration including B16 invalid-owner
failure. B14 needs graph relations; B02 ordered normalization; B16 cross-entity
identity; none requires a new *grounding* mechanism per command type. Where
requirements demand byte-identical no-write, compare bytes and file absence;
where concurrency or external resources are introduced, declare what lies
within the observed atomic boundary. This is architectural reuse based on
frozen text, **not** an adequacy classification of B02–B16 or a claim those
relations and mappings have been implemented. Special per-command public-call,
persistence or migration observers would be a warning sign.

## 8. Next prototype recommendation and decision gate

- **Lykoi semantic source:** typed entities, valid/reachable-state assumptions,
  operation input/output/error signatures, abstract `(I,S,Outcome,S')` contracts,
  applicable states and composable query/state relations. Keep real clock/IDs
  as explicit capabilities, without prescribing Python, CLI or JSON files.
- **Compiler/interface metadata:** checked mapping of abstract operation to
  public entry point, argument presence/default parsing, success/error envelope,
  versioned state representation and effect/storage boundary. Validate and
  lower it per backend, and test mapping fidelity independently; do not trust
  generated code's declarations as observations.
- **Runtime observation:** capture actual calls, before/after durable state and
  complete outcomes/effects for the same invocation, in a reproducible isolated
  environment; supply controlled external capabilities where needed. A
  black-box snapshot is sufficient only for its declared storage boundary.
- **Verification:** validate traces and metadata, evaluate contracts over
  grounded tuples, retain R5.2.2 as independent finite acceptance authority,
  and report observer/coverage limitations. Keep test fixtures, lineage and
  acceptance administration outside the core semantic vocabulary.
- **Claims:** finite evidence licenses only case-scoped conformance; arbitrary
  valid inputs may be *specified* universally and sampled without being proven.
- **Universal proof:** requires a sound, complete interface/state/effect model,
  a correctness argument for implementation or compiler lowering and adapters,
  reachability/totality and environment assumptions, and induction/composition
  for unbounded executions (or genuinely exhaustive bounded-domain claims).

The existing direction has a reusable abstract core, but #45 currently names
both a relation and an unimplemented actual-execution binder; the ledger mixes
semantic operators with test steps and benchmark administration, and separate
validators do not form one checked contract-to-trace path. This requires an
architectural **responsibility split and integrated typed boundary** before
resuming B01 adequacy. It does not establish that B01 needs a new command,
persistence, sequential-call or migration-specific semantic primitive.

**Verification (2026-10-02):** `python -m unittest discover -s
benchmark/harness -v` — 109 tests, OK. `git diff --check` — exit 0
(PowerShell working-copy line-ending warnings only). These development checks
do not revalidate R5.2.2 snapshots or prove the proposed architecture.

B01 remains halted, the semantic format remains unfrozen, Phase 5C does not
resume, and B17 remains unexposed and unclassified.

SEMANTIC_ARCHITECTURE_REVISION_REQUIRED
