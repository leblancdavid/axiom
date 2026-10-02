# R5.5 semantic architecture separation — prospective, 2026-10-02

**Scope:** architecture revision of the unfrozen prototype, not benchmark
capability work. R5.2.2 remains the authoritative corrected post-B16 boundary.
The R5.4 [checkpoint](R5_4-SEMANTIC-ARCHITECTURE-CHECKPOINT.md) and
[45-entry ledger](R5_4-SELECTION-VOCABULARY-LEDGER.md) remain historical inputs;
their evidence has not been upgraded. B01 is inadequate and halted, Phase 5C
paused, B17 unexposed and unclassified, semantic-first format UNFROZEN.

## Before / after and trust boundaries

```
Before: mixed #45 {operation, schema, checks, synthetic cases, expected holds}
        -> tuple evaluator                 [no actual-call binding]
        separate scenario probe -> subprocess + snapshots + comparisons

After:  abstract contract (contracts.py)     WHAT is required
             | referenced by
        checked slot map (binding.py)         WHERE facts map, not truth
             + actual facts (observation.py) WHAT happened, if faithfully captured
                         -> conformance.py    case-scoped relation result
        legacy fixture -> explicit extraction of contract + synthetic tuple runner
        scenario probe -> unchanged finite integration witnesses
```

The semantic contract is a typed named operation with four abstract slots:
input, pre-state, outcome, post-state. Its checks compose existing equality and
`default_missing` state relations; there is no Python, CLI, file, command name,
observer or test expectation in the extracted contract. The existing
`upgrade_items` fixture is a *sample*, not a general-purpose definition of all
operation outcomes: success/error alternatives and reachable-state domains are
not integrated. An abstract operation contract can reuse collection and state
relations by referring to their typed values; the current four-slot evaluator
demonstrates only equality and one keyed default relation, not integration of
all 29 candidates or universal quantification.

Binding has only operation identity, opaque boundary identity and a checked
bijection from four semantic slots to four fact names. It references a validated
contract and cannot redefine its checks. This is a **minimal prototype of the
interface responsibility**, not a checked public CLI/argument/storage mapping.
Neither an arbitrary boundary label nor a self-reported `source: execution`
proves adapter fidelity. A future target adapter must validate the operation
entry point, argument decoding, success/error envelope, state projection,
durability/effects and coverage; no Python-specific metadata is semantic.

Observation validates a complete four-fact record with invocation identity,
boundary and ordered sequence. It has no requirements or expectations. A trace
can assert `post(n) == pre(n+1)` on the same boundary without a new B01 semantic
operator. This does not prove the observer captured all effects or that the
boundary is atomic; no universal tracer was built. The verifier validates
contract, binding and observation, projects values, evaluates the relation,
and emits `conforms` for *one* invocation, `evidence: observed_execution`, and
`proof_status: not_established`. Its API trusts the record's origin; R5.5 tests
use fabricated records to test architecture, **not** to claim real application
conformance. The old `probe.py` still compares finite subprocess outcomes and
snapshots, but is not wired to this verifier.

**Contract** declares behavior, potentially for arbitrary valid inputs and
states. **Evidence** is supplied fixtures, observed execution, property samples
or bounded enumeration with explicit scope and provenance. **Proof** requires a
sound argument for the declared entire domain, including binding fidelity,
observer coverage or verified lowering, reachable states and environmental
assumptions. Passing seven synthetic cases or any finite acceptance suite is
neither an implementation-wide guarantee nor universal proof. Exhaustive
finite-domain evaluation licenses only its stated bounded domain.

## #45 decomposition and files

| Historical #45 concern | Owner after separation | Status |
| --- | --- | --- |
| Typed operation `(I,S,Outcome,S')` constrained by relations | `benchmark/semantic/contracts.py` | Provisional semantic candidate; current evaluator supports only supplied typed sequences. |
| Actual interface/state location | `benchmark/semantic/binding.py` | Checked slot/boundary references only; concrete fidelity unimplemented. |
| Actual call and pre/outcome/post trace | `benchmark/semantic/observation.py` | Record/continuity validation only; capture mechanism not implemented here. |
| Relation check against grounded facts | `benchmark/semantic/conformance.py` | Case-scoped verdict; origin/fidelity trusted. |
| Synthetic cases and `holds` | `benchmark/semantic/operation_contract.py` and historical JSON | Compatibility integration fixture, extracted explicitly; no migration to runtime evidence. |

`benchmark/harness/test_semantic_architecture_r5_5.py` tests the layer
boundaries. The existing operation fixture and seven positive/negative witnesses
remain byte-for-byte intact; its compatibility evaluator now delegates typed
relation checks to the extracted contract module. `format.py`, `probe.py`,
frozen requirements, corrected oracle, current model/compiler and generated
artifacts remain unchanged. The selected scenario fixtures remain finite
integration witnesses (`seed/invoke/snapshot/observe`), not contract definitions
or generic execution traces. No old evidence is silently reclassified as an
observed contract-conformance run.

## Responsibility inventory (every historical ID exactly once)

The **RAW EXPERIMENTAL CONSTRUCT COUNT is 45**, preserving the R5.4 ledger IDs.
The **CANDIDATE CORE SEMANTIC CONSTRUCT COUNT is 29** (unfrozen). Primary
classifications below are inventory accounting, not declarations of a frozen
language. Ranges refer to every integer inclusively.

| Primary responsibility | IDs | Count | R5.4 movement / decomposition note |
| --- | --- | ---: | --- |
| Core/domain semantics | #1–8, #13–14, #25–27 | 13 | Same core candidates; #25 parsing from a field may be adapter work. |
| Collection semantics | #9–12, #15–20, #43 | 11 | Same; #11–12 may later be represented together. |
| State semantics | #21–23, #44 | 4 | Same; bounded semantic scope #23 is not a test runner. |
| Operation semantics | #45 | 1 | Only the abstract relation; actual-call binder split out, not counted as core. |
| Interface binding | — | 0 | New unnumbered boundary/slot metadata; no old ID for it. |
| Target/compiler metadata | — | 0 | Backend lowering remains outside this ledger. |
| Runtime observation | #24, #30–31 | 3 | Clock read, invocation and snapshot mechanisms; #30 mixes expected error/result assertions and must split. |
| Conformance verification | #32, #36 | 2 | Finite comparisons; #32 also mixes observation references, and #36 may eventually be a core inequality relation only if separately justified. |
| Evidence/test machinery | #28–29, #33–35 | 5 | Scenario, seed and expression helpers remain finite fixture work. |
| Evolution/link metadata | #37–40, #42 | 5 | Historical replacement/dependency/carrier links; #40 might have a distinct general analogue, not this composer. |
| Benchmark/research administration | #41 | 1 | Achieved-history guard, not application semantics. |
| Unresolved primary classification | — | 0 | Mixed concerns are flagged above rather than double-counted. |

Sum: 13 + 11 + 4 + 1 + 0 + 0 + 3 + 2 + 5 + 5 + 1 = **45**.
R5.4 grouped ten finite observation/evidence items (#24,#28–36) and six
administrative/evolution items (#37–42). R5.5 separates those ten into 3
observation, 2 verification and 5 evidence; the six into 5 evolution and 1
administration. The core candidate count stays 29 only because #45 is counted
solely for its abstract relation; this is not a measure of architectural quality.
The unnumbered binding map, observation envelope and conformance verdict are
**prototype metadata**, not stealth additions to the 45 numbered constructs.
If a future ledger counts newly named metadata, it must publish a new raw
denominator instead of pretending they were historical IDs.

## AI-native representation and source of truth

| Choice reviewed | Classification | Machine dependence / direction |
| --- | --- | --- |
| JSON object keys, typed slots, stable IDs and exact key validation | USEFUL_FOR_TOOLING | Deterministic validation and references; JSON itself is not proven optimal. |
| Ordered collection values and trace sequence | REQUIRED_FOR_SEMANTICS | Collection order or execution order is material; object-key display order is not. |
| Descriptive `operation`/scenario names | USEFUL_FOR_AI | Stable references matter; English spellings are not semantic requirements. |
| `seed/invoke/snapshot/observe` statement-like steps | USEFUL_FOR_TOOLING | Ordered fixture execution, not a reason to model semantic source as statements. |
| Repeated `origin`, `carrier`, `holds` in fixtures | USEFUL_FOR_TOOLING | Evidence/lineage bookkeeping; should not be duplicated into core contracts. |
| Pretty-printed generated Python and readable variable names | HUMAN_PRESENTATION_ONLY | Not an authoritative source requirement; no generated-code redesign here. |
| Human-readable validator errors | USEFUL_FOR_TOOLING | Diagnostics help debugging; wording is not contract meaning. |
| Whether graph/relational serialization improves AI editing | UNKNOWN | No controlled comparison; do not select a format by appearance. |

The intended authoritative project representation is Lykoi semantic source
plus separately checked deployment/binding metadata: `project -> deterministic
compiler -> target artifact -> executable -> independently observed behavior`.
The currently canonical application model is `air/task_manager.json`; R5.5's
`benchmark/semantic/` modules are prospective and **not integrated** into that
model. Generated Python is reproducible implementation output, not ordinary
manually maintained source. Machine-stable semantic IDs, contract/binding
versions and hashes, artifact provenance, source-to-lowering associations,
runtime invocation/operation IDs and diagnostic location mappings should survive
compilation to support traceability, verification and failure attribution.
The current manifest offers artifact provenance; it is not a general source map
or sound execution proof. Human presentations can be views over machine records.

Target pressure test: the abstract four-slot relation makes no Python claim and
could retain meaning with Python, JavaScript, Rust, C/C++, JVM/.NET or WebAssembly
lowering. Each target would need its own checked entry/state adapter and runtime
assumptions (errors, clocks, concurrency, persistence); equivalent observable
behavior does **not** require similar algorithms, layouts, control flow or
generated code. This is theoretical portability, not demonstrated backends.

## Invariants, open work and B01 boundary

Separation of semantic meaning, mapping, fact record and case verdict is
enforced by distinct modules and closed-key validators. Finite evidence is
never emitted as proof; generated structure is not compared as semantic
equality; fixture bookkeeping stays out of the core count. Human readability
is optional; generated code remains an artifact. **Not established:** binding
fidelity to actual public calls/storage, provenance authentication of an
observation, observer completeness/atomicity, success/error and effect typing,
reachability and totality, a single integrated semantic schema, or proof.
The prototype can still be fooled by a fabricated but well-formed record;
the scenario runner retains mixed observation/comparison steps. These are
important responsibility gaps, so the architecture is improved but partial.

Known B01 gaps remain: create insertion and frame, completion frame, migration
outcome/version, priority-domain “above HIGH” order, and universal public-call
and persistent-state binding. None was implemented or classified as adequate.
No B01 behavioral fixture was added. Further work should challenge adapters
on an unseen interface and ensure that coverage and observation provenance are
checked independently before restarting semantic adequacy research.

## Verification

R5.5 architecture-focused tests: six tests (closed responsibility boundaries,
typed mapping, fixture/trace distinction, finite verdict, nonmutation and
sequential continuity), OK. Existing prototype tests continue to exercise the
unchanged seven supplied tuples. `python -m unittest discover -s
benchmark/harness -v`: **115 tests, OK** (109 previous + 6 architecture tests).
`python -m unittest discover -s tests -v`: **31 tests, OK**. `git diff
--check`: exit 0, no whitespace errors; PowerShell/Git issued working-copy
LF-to-CRLF conversion warnings separately. The new module-only edit after the
full suite was a removal of an unnecessary binding import in the observation
module; architecture tests were rerun afterwards. These checks are development
evidence, not a proof of adapter fidelity or benchmark adequacy.

R5_5_ARCHITECTURE_PARTIAL
