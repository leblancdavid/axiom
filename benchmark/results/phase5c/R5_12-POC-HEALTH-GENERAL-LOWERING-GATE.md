# R5.12 — POC health and general lowering gate (prospective, 2026-10-02)

**Authority and scope.** R5.2.2 remains the corrected historical execution
boundary. Reviewed the frozen B01 request, inherited baseline, R5.4 ledger,
R5.5–R5.11 prospective records, semantic modules and R5.11 generated template,
builder, observer, challenge and tests. This is a source-authority/overfit audit,
not a new acceptance freeze or a new benchmark attempt. The format is UNFROZEN;
Phase 5C remains paused; B17 is unexposed and unclassified. Universal
implementation correctness is not established.

## 1. Actual R5.11 dependency graph

| Stage → next | Actual responsibility, location | Classification |
| --- | --- | --- |
| Frozen intent → abstract contract | B01 + baseline manually decomposed into relational obligations in R5.11 record; `CONTRACT` is an operation-to-label index, **not** a typed executable contract | BENCHMARK-INFRASTRUCTURE for frozen text; B01-SPECIFIC for decomposition/index |
| Abstract operation contracts → compiler | `contracts.py` interprets supplied uniform record sequences and tagged outcomes; B01 nullable/versioned/numeric contract is *not* its input | SYNTHETIC-PROTOTYPE-SPECIFIC; intended general relation partial |
| Compiler/lowering → binding | `b01_integration_r5_11.build` substitutes only generation/variant constants into `b01_target_r5_11.py`; `operation_map` names command boundaries and hashes label lists | B01-SPECIFIC compiler; TARGET-SPECIFIC Python substitution; B01-SPECIFIC binding |
| Binding → executable | Template already implements command dispatch, validation, queries, migration, storage, and JSON CLI | B01-SPECIFIC behavioral implementation; TARGET-SPECIFIC CLI/file encoding |
| Executable → provenance | Contract/template/artifact digests and operation/boundary/persistence IDs; hashes establish consistency, not semantic derivation | VERIFICATION-SPECIFIC with B01-SPECIFIC mapping |
| Provenance → actual execution | CLI dispatch, `tasks.json`, commit, internal sidecar and fault variants | TARGET-SPECIFIC; B01-SPECIFIC branches; fault injection VERIFICATION-SPECIFIC |
| Execution → observation | Independent subprocess argv, exit/streams, file bytes and decoded pre/post captured before sidecar is read | VERIFICATION-SPECIFIC; target/file-specific observer; fixture invocations BENCHMARK-INFRASTRUCTURE |
| Observation → grounding | `challenge` checks invocation, operation, argv decoding, public JSON, raw file endpoints, event and artifact identity | VERIFICATION-SPECIFIC, with B01-SPECIFIC argument mapping |
| Grounding → conformance | `conforms` dispatches handwritten command expectations; #30 used via `cardinality.evaluate`; R5.12 routes only normal and exact-HIGH reads through general typed validating lowering | B01-SPECIFIC except general relations and new bounded VALIDATING lowering |

No unknown stage silently establishes coverage: observer completeness for other
files, intermediate effects and close-boundary clock reads remains UNKNOWN. The
historical `air/task_manager.json` → `src/air_compiler` → `generated/` pipeline
is separate from this prospective B01 candidate; it must not be conflated with
the R5.11 builder.

## 2. Audit of **all 30** prospective core candidates

Identifiers #1–23, #25–27, #43–45 are historical ledger IDs; **core #30** is
the *new* R5.10 cardinality entry, not historical observation #30. `Use` lists
the first motivating frozen clause and other clauses *cited in the ledger*;
these are clause references, not full-contract implementations. `Synth` refers
to supplied typed fixture families (selection, invariant, state, operation,
count, R5.12) and is not a grounded non-B01 application unless explicitly
stated. `R` means demonstrated relation/fixture reuse; `P` only plausible;
`—` none. Alternative formulations below are hypotheses, not reductions proved
equivalent. Every row is a semantic candidate unless a layer warning is stated.

| # / responsibility | Motivation; frozen use; synthetic use and reuse | B01 pressure, overlap / possible primitive replacement | Assessment |
| --- | --- | --- | --- |
| 1 record schema | B01 shape; B03 cited; typed selection/state/operation/count/R5.12; R | Introduced B01; records could be typed product values | STRONG_CORE_CANDIDATE |
| 2 field projection | B01 fields; B03; selection/R5.12; R | Introduced B01; general projection; overlaps observation `ref` only by appearance | STRONG_CORE_CANDIDATE |
| 3 finite sequence | B01 collections; B02/B03; selection/invariants/count/R5.12; R | Introduced B01; finite relation domain | STRONG_CORE_CANDIDATE |
| 4 bound variable | B01 predicate; B02/B03/B14; selection/invariants; R | Introduced B01; could use quantified relation argument instead | PROVISIONAL_CORE_CANDIDATE |
| 5 typed literal | B01 equality; B02/B03/B14; selection/invariants/R5.12; R | Introduced B01; declarative constants essential, not fixture IDs | STRONG_CORE_CANDIDATE |
| 6 equals | B01 exactness; B02/B03/B14; selection/operation/R5.12; R | Introduced B01; general typed equality | STRONG_CORE_CANDIDATE |
| 7 and | B02 predicates; B14/B01 fixture; invariants/contracts/R5.12; R | Not introduced B01; general Boolean connective | STRONG_CORE_CANDIDATE |
| 8 not | B14 predicate; B01 fixture; invariants/conditional contracts/R5.12; R | Not introduced B01; negation overlaps conditional encoding but not equality | STRONG_CORE_CANDIDATE |
| 9 contains | B03 tags; no other frozen clause established; selection fixtures; P | Not B01; membership may derive from existential exact selection | PROVISIONAL_CORE_CANDIDATE |
| 10 selection | B01 exact HIGH; B03; selection/count/R5.12; R | Introduced B01; general filter; selection semantics overlap #11/#12 modes | STRONG_CORE_CANDIDATE |
| 11 exactness | B01 all-and-only; B03; selection/count; R | Introduced B01; exact result may be expressible as relational equality | PROVISIONAL_CORE_CANDIDATE |
| 12 source-relative | B01 list-high; B03; selection fixtures; R | Introduced B01; can alternatively order a selected view with #43 | POSSIBLE_OVERFIT |
| 13 trim | B02 string normalization; no further clause; invariant fixtures; P | Not B01; could be general string transform | PROVISIONAL_CORE_CANDIDATE |
| 14 nonblank | B02 title/tag; no further clause established; invariant fixtures; P | Not B01 origin; `not(equals(trim(x),''))` may replace | REDUNDANT_CANDIDATE |
| 15 map(trim) | B02 tags; no further clause; invariant fixtures; P | Not B01; named transform may be generic map + #13 | POSSIBLE_OVERFIT |
| 16 stable_unique | B02 ordered tags; no further clause; invariant fixtures; P | Not B01; first-occurrence relational characterization possible | PROVISIONAL_CORE_CANDIDATE |
| 17 for_each | B02 invariants; no further clause; invariant fixtures; P | Not B01; overlaps #23 universal finite scope | REDUNDANT_CANDIDATE |
| 18 directed graph | B14 dependencies; no other clause established; graph fixtures; P | Not B01; graph could be typed node/edge relation | PROVISIONAL_CORE_CANDIDATE |
| 19 add_edge | B14 transition; no further clause; graph fixtures; P | Not B01; set union with edge singleton might replace | POSSIBLE_OVERFIT |
| 20 acyclic | B14 invariant; no further clause; graph fixtures; P | Not B01; reachability/irreflexivity could replace if available | PROVISIONAL_CORE_CANDIDATE |
| 21 transition | B02 state; B14; state/invariant/operation fixtures; R | Not B01 origin; #45 binds a richer tuple, but not same responsibility | STRONG_CORE_CANDIDATE |
| 22 precondition | B02 applicability; B14; state/invariant/contracts; R | Not B01 origin; predicate guard could be #45 applicability | PROVISIONAL_CORE_CANDIDATE |
| 23 finite domain scope | B02 universal rule; B14; invariant/count fixtures; R | Not B01 origin; may combine with #17 quantified predicate | PROVISIONAL_CORE_CANDIDATE |
| 25 instant | B09 timestamp; B12 and B01 overdue; clock/state fixtures; R | Not introduced B01; parsing at external boundary belongs in adapter | POSSIBLE_LAYER_MISCLASSIFICATION |
| 26 offset | B12 time; no further clause; clock fixtures; P | Not B01; typed arithmetic relation could subsume | PROVISIONAL_CORE_CANDIDATE |
| 27 before | B09 strict time; B12/B01 overdue; clock fixtures; R | Not introduced B01; generic strict instant ordering | STRONG_CORE_CANDIDATE |
| 43 lexicographic_order | B01 normal order; no independent frozen reuse established; state/R5.12; P | B01-introduced; generic ordered view; overlaps #12 and fixture-only #35 | POSSIBLE_OVERFIT |
| 44 default_missing | B01 v1/v2 migration; no independent frozen reuse established; state/operation/count; P | B01-introduced; per-key preservation/default may decompose into keyed frame + absent-field equality | POSSIBLE_OVERFIT |
| 45 abstract operation relation | B01 public operation gap; other clauses plausible; synthetic vials and operation/R5.12; R | B01-introduced; *actual-call binder* must stay in binding/verification, not core | POSSIBLE_LAYER_MISCLASSIFICATION |
| core 30 cardinality | B01 numeric migration; no independent frozen use established; count/R5.12 filtered population; R synthetic | B01-introduced, obviously general finite sequence size; cannot derive numeric result from current relations | STRONG_CORE_CANDIDATE |

Classification totals: **11 strong, 10 provisional, 5 possible overfit, 2
possible layer misclassification, 2 redundant**. These labels are qualitative;
overlap concerns are not evidence
that a construct can be deleted. No core #31 was introduced. The 30 are not a
single integrated validated language; #15/#19/#43/#44 deserve independent
non-task stress before retention, while #14/#17 deserve equivalence studies.

## 3. B01 vocabulary pressure

By *first motivation*, ledger entries **#1–6, #10–12, #43–45 and core #30 =
13/30** originate primarily in B01. Among those, **7** (#1–6,#30) have
obviously general responsibilities (#30 also has synthetic cross-domain reuse);
**3** (#10–12) have cited cross-clause use (B03), but this is not a grounded
B03 execution; **3** (#43–45) have only plausible other-clause use as complete
relations (synthetic tuple reuse of #45 does not establish general target
lowering). **Zero** have literal task/priority names in their *definitions*.
The other 17 originated in other requirements or general prototypes. Thus
“introduced for B01” is not synonymous with “B01-only”; the concentration at
the last three is nevertheless a warning. R5.12 does not inspect new frozen
material or claim any B02 implementation.

## 4–5. Candidate audit and semantic-source authority

| Instance | Classification and consequence |
| --- | --- |
| `CONTRACT` contains `B01-v3-prospective`, priority literals, named commands and `exact_HIGH_selection`; `operation_map` digests lists of labels | B01-SPECIFIC indexing/provenance; neither specifies nor lowers the actual condition. A valid changed label changes digest but not executable behavior. |
| `build` reads a complete Python template and replaces `__GENERATION__`/`__VARIANT__` only | B01-SPECIFIC manually assembled behavior + TARGET-SPECIFIC compiler shell; contract digest affects metadata, not algorithm. |
| Template `execute`: create defaults, exact HIGH, overdue clock, complete, delete, v1/v2 migration, count and JSON envelope; `checked` hard-codes row fields/priorities; argparse hard-codes commands | B01-SPECIFIC manually authored implementation. These are not generated from typed semantic operations; target encoding alone would be legitimate adapter work if parametrized by actual semantic data. |
| Template `wrong_count` and `false_post` | VERIFICATION-SPECIFIC disposable faults; not primary behavior but target-code switches; keep outside a future production lowerer. |
| `conforms` hard-codes create/complete framing, error classification, overdue clock, migration defaults/count and row fields; list read rules now partly passed to typed lowering | B01-SPECIFIC verifier semantics. #30 itself general; selecting *legacy* rows and writing version 3 remain B01-coded. A checker agreeing with separately authored code is not compiler authority. |
| `challenge` reconstructs `--title`, `--id`, `tasks.json`, JSON exit convention and per-command IDs | B01-SPECIFIC/TARGET-SPECIFIC binding inside otherwise VERIFICATION-SPECIFIC grounding; this adapter has to be independently justified, not moved into core. |
| R5.11 tests use HIGH/CRITICAL, v2 three-record fixture, and frozen B01 profile | BENCHMARK-INFRASTRUCTURE / VERIFICATION-SPECIFIC selected evidence, not source of universal operation rules. |
| R5.7 template hard-codes vial-sealing algorithm, while its `contract()` computes an independent synthetic tuple checker | SYNTHETIC-PROTOTYPE-SPECIFIC instance of the same authority limitation. |

**Authority partition:** `SEMANTIC SOURCE → GENERAL LOWERING → GENERATED
BEHAVIOR`: no complete B01 operation. The v0.3 canonical `air/` pipeline has
its own generated task manager, but does not consume this prospective 30-core
B01 contract. R5.11 is `SEMANTIC LABEL INDEX + SEPARATELY AUTHORED
IMPLEMENTATION` for *all seven* commands. The R5.12 typed checker adds
`SEMANTIC SOURCE → GENERAL VALIDATING LOWERING → CASE VERDICT` for grounded
normal-list and exact-HIGH-list tuples; it does **not** regenerate either
command's target behavior. Rebuilding the R5.11 candidate still produces the
same template implementation because changing a valid typed read constraint
does not change `execute`. The gap is a checked contract-to-target behavioral
lowering, not an absent SHA-256 digest. B01 case conformance remains finite.

## 6–9. #45 lowering and challenges

`benchmark/semantic/typed_lowering_r5_12.py` implements a **bounded validating
lowering**: closed typed input/pre/post and per-tag typed outcome payloads;
field references, typed literals, equality, conjunction, negation, exact
selection, ordered result and cardinality; branch-specific constraints are
compiled to a reusable tuple checker. No benchmark identity, task operation,
priority or migration branch exists in the general interpreter. Its source is
typed relation structure, not callback Python code. It has no state mutation
generator, no independent observation, no runtime interception and no universal
proof. `default_missing`, valid #44 in a new combination, intentionally raises
`UnsupportedLowering` rather than being patched to fit this audit.

`b01_integration_r5_11._read_contract` is a **B01 adapter specification**:
record fields, selected HIGH predicate and `(created_at,id)` order remain
declared there. For two read-only success paths `conforms` now calls the same
general validating lowerer used by an independent non-task synthetic domain.
All other B01 behavior still uses the old handwritten checker. Original B01
target construction was re-exercised by the R5.11 integration tests (fresh
disposable build and unmodified frozen profile); no B01 generated target
algorithm changed. In particular the B01 semantic label index is **not**
silently presented as this typed contract.

The synthetic contract operates on `code/active/weight` records with *success*
returning sorted selected items **and** an integer count, and *rejected*
returning a typed reason with unchanged state. Changing the typed predicate
from `active=true` to `active=false`, with no lowering edit, rejects the old
result and accepts the new one. Wrong cardinality and wrong error reason fail.
This establishes sensitivity of **validated behavior**, not generated
implementation behavior. A novel valid pairing of keyed `default_missing` with
this tagged selection/count contract is rejected as **LEGITIMATELY UNSUPPORTED
LOWERING**, not an invalid semantic composition: #44's prototype gives that
relation meaning, but this lowerer has no general keyed/default semantics.
Type-mismatched equality is separately rejected as invalid. The unsupported
case is evidence of incomplete compiler breadth, not proof of B01-specialized
code in this general evaluator. Deterministic artifact generation from typed
source remains a future generative requirement; a runtime contract check would
need faithful invocation/effect capture rather than merely calling this checker.

## 10–11. Representation health and full complexity accounting

Stable IDs are present in scenario/relationship records and command mapping,
but the R5.11 semantic operation identity is a command spelling; its digest of
labels lacks an authoritative typed relation/source map. Canonical sorted-key
compact JSON produces deterministic digests, and template substitution is
deterministic for a given template/contract/variant. It does not normalize
equivalent predicates or detect changes that alter behavior without changing
the label index. R5.11 duplicates obligations in prose, label lists, target
code and verifier; references are local in typed fixture ASTs but cross-module
source authority is missing. There is no measured token/editing cost or
controlled AI-authoring comparison. Statement-like `seed/invoke/observe` plans,
CLI-shaped operation labels and embedded Python template mimic ordinary
programming syntax where semantic authoring need not; ordered steps remain
useful for *execution evidence*. Human-readable names, source locations and
diagnostics aid debugging and research without becoming core semantics.

| Responsibility | Count and accounting boundary |
| --- | --- |
| Candidate core semantics | 30: 13 domain (#1–8,#13–14,#25–27), 12 collection (#9–12,#15–20,#43,core #30), 4 state (#21–23,#44), 1 abstract operation (#45). |
| Historical non-core numbered | 16: runtime observation 3 (#24,#30–31 historical), verification 2 (#32,#36), evidence 5 (#28–29,#33–35), lineage 5 (#37–40,#42), administration 1 (#41); total raw prospective accounting 46. |
| Unnumbered compiler/lowering | At least 5 responsibilities: type validation, AST relation compilation, template rendering, domain algorithm implementation, target adapter/encoding. Only the first two are general in R5.12; counting functions as constructs would be misleading. |
| Unnumbered binding | At least 4: operation entry, argv/input map, outcome map, persistence/state projection. R5.5's slot bijection does not implement these. |
| Unnumbered provenance | At least 4: contract, template and artifact digests, per-operation generation/boundary association. |
| Unnumbered observation | At least 5: subprocess invocation, stdout/stderr/exit, pre-file bytes, post-file readback, internal event. |
| Unnumbered grounding | At least 4: invocation/operation match, input/output challenge, pre/post challenge, artifact drift check. |
| Unnumbered verifier | At least 4: typed projection, case relation evaluation, no-write endpoint check, verdict separation. B01 adapter dispatch remains additional code. |
| Unnumbered test/evidence | At least 5: synthetic witnesses, target fault variants, B01 grounded samples, external acceptance, persisted evidence. |
| Unnumbered benchmark/research administration | At least 4: frozen requirement/oracle, checkpoint history, achieved profiles, versioned prospective gates. |

These **at least 35 unnumbered responsibilities** are architectural inventory,
not additional semantic constructs or a precise function count. The 16
historical non-core entries are *not* added twice to the 31; the latter describe
concrete implementation responsibilities, some implementing the former. A
30-core claim alone cannot measure total platform cost.

## 12–13. Fair comparison and overfitting assessment

The historical Conventional B01 track authored Python application behavior
against the frozen request and oracle; it did not author a prospective 30-core
semantic representation, provenance events or tuple checker. The R5.11
prospective Lykoi candidate also authored Python application behavior manually
in a template **plus** semantic analysis, digest index, observer/grounder and
B01 checker. Both candidates have an executable artifact and the original
frozen B01 profile; only the new prospective candidate has selected grounded
case conformance and fault-discrimination evidence. Those differences are
factual, not relative productivity or a ranking. The v0.3 `air/` compiler and
the R5.7–R5.12 verifier platform are one-time research/platform costs; the
R5.11 template, B01 adapters, contract labels and tests are per-program costs.
Their totals cannot be inferred from tests or filenames, and no controlled
authoring-time/token denominator was recorded. Conventional acceptance detects
observable failure in sampled cases; prospective grounding additionally
distinguishes falsely reported state from a faithfully reported wrong count.

**For overfit:** B01-specific template, checker and binding; two competing
sources of hand-authored behavioral knowledge; label-hash provenance can make
this look like compilation; last B01-motivated relations #43/#44 lack
independent grounded use; finite fixtures concentrate on the same domain;
unsupported novel combinations expose compiler immaturity. **Against:** core
definitions of selection/cardinality/typed tuple are not priority commands;
B03 cross-clause selection use and synthetic vials, counted strings and the
new non-task sorted/filtered/count domain; changed synthetic predicate changes
verdict without lowerer edits; the negative-combination test fails explicitly
instead of silently adopting a B01 shortcut; grounded vs nongrounded failure
separation works on real calls. These facts support a plausible reusable
semantic/grounding direction but **substantial per-application implementation
overfit risk**. Passing B01 does not settle the question.

## 14–18. Gate

* **Semantic-model health:** coherent enough for further *synthetic* testing;
  30 provisional candidates are neither minimized nor one integrated schema.
* **Compiler/lowering health:** typed source now drives a bounded validating
  verdict for two read operations and the independent synthetic contract;
  it does **not** drive B01 implementation. Most operations remain separately
  authored. No generative #45 compiler claim is justified.
* **Grounding health:** R5.7–R5.11 challenge design is reusable in principle
  across synthetic and B01 observed calls, with target/B01 bindings and limited
  file/clock/effect coverage; no universal implementation proof.
* **Overfitting risk:** significant, concentrated in template, adapters,
  duplicated contract authority, and untested relation combinations, rather
  than obviously task-named core primitives.
* **Scaling readiness:** **NO**. Do not test another frozen request yet.
  First make typed semantic contract the actual input to constrained generative
  operation lowering (at minimum a complete read-only selection/order form and
  one simple state transition), validate the binding and provenance against
  that source, and repeat a non-task mutation with *generated target behavior*.
  Then reassess unsupported #44 and B01 create/complete/migration; preserve
  honest limits instead of fabricating synthesis of arbitrary algorithms.

**Verification (repo root):** full `python -m unittest discover -s
benchmark/harness -v`: **144 tests OK**; `$env:PYTHONPATH='src'; python -m
unittest discover -s tests -v`: **31 OK**. Independently focused patterns:
architecture R5.5 **6 OK**, grounding R5.7 **10 OK**, semantic prototypes
**33 OK**, R5.10 **4 OK**, R5.11 **4 OK** (including fresh candidate build
and frozen B01 profile), R5.12 **3 OK**. `git diff --check`: exit 0, no
whitespace failures. Git separately printed four LF→CRLF working-copy
conversion warnings for tracked files; these are not test/whitespace failures.
The full suite includes historical tests over already-frozen materials and
does not constitute a new frozen-request attempt. No B02 work, Phase 5C resumption, B17 exposure/classification,
format freeze, historical checkpoint edit or construct #31 follows.

R5_12_LOWERING_NOT_GENERAL_ENOUGH
