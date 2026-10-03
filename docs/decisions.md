# Experimental decisions

## R5.18 typed relation-set planning (prospective, 2026-10-02)

Plan same-collection keyed missing-field defaults as an N-way conjunction:
validate one identity and typed optional fields, deduplicate identical writes,
reject distinct literal writes to one field as `CONFLICTING_RELATIONS`, and
canonicalize independent writes before Python emission. Values read input/pre,
not intermediate post-state; disjoint field writes commute. The verifier builds
one expected post-population. Keep frame/default and unresolved same-field
expression overlaps explicitly unsupported rather than inferring list order.
This is compiler machinery under the existing 30-core vocabulary, not a new
semantic construct or authorization for benchmark execution. Preserve the
historical R5.17 locked test even though its old-lowerer rejection assertion
does not hold on the prospective implementation. See the
[R5.18 result](../benchmark/results/phase5c/R5_18-OVERLAPPING-RELATION-COMPOSITION-LOWERING.md).

## R5.17 clean frozen B02 retry halt (prospective, 2026-10-02)

Keep the pre-attempt R5.16 working-copy hashes fixed and classify B02's
multi-field legacy defaults as valid candidate semantics but unsupported
unchanged general lowering: the second keyed default on one collection raises
`UNSUPPORTED_LOWERING_CAPABILITY: overlapping collection relations`. Do not
divide one migration into multiple invocations, hand-author an adapter, or
patch compiler/runtime/verifiers within this retry. Without a generated B02
candidate, source authority, frozen acceptance and grounded conformance cannot
be claimed. Continue general compiler studies on independent domains in a
separate prospective experiment; do not activate B03 or B17. See
`benchmark/results/phase5c/R5_17-B02-GENERALIZATION-RETRY.md`.

## R5.16 framed and versioned general lowering (prospective, 2026-10-02)

Recognize the existing exact target/outside-target selection frame as a bounded
typed compiler relation category, and generate a fresh-key collection witness
without imposing storage order. Bind keyed missing-field defaults, version
applicability, version update and candidate cardinality to one actual durable
envelope/operation, rather than an invocation-supplied edition. Reject
overlapping collection changes explicitly. Independent specimen/archive calls,
semantic-only mutations and grounded fault variants support closing these two
targeted lowering gaps under the unchanged 30-core candidate vocabulary; this
does not establish all #45 combinations or permit a B02 retry. See
`benchmark/results/phase5c/R5_16-FRAMED-INSERTION-DURABLE-MIGRATION-LOWERING.md`.

## R5.15 partial general lowering (prospective, 2026-10-02)

Extend R5.13's typed generator only for existing ordered string normalization,
branch-typed record results and bounded #44 missing-field defaults. Reuse the
existing grounded subprocess/file challenge and independently interpreted
contract for non-task media, device and library executions; check semantic-only
mutations and a grounded lowering fault. Do not substitute append code for the
unintegrated #10–12/#43 exact insertion/frame hypothesis or treat an invocation
edition guard as a durable version transition. Leave these paths explicitly
unsupported until their typed relation and checked state binding are integrated.
The four-capability gate is **partial**, despite three-capability composition;
no construct #31 and no B02 retry. See
`benchmark/results/phase5c/R5_15-GENERAL-LOWERING-COVERAGE-EXPANSION.md`.

## R5.14 B02 frozen-architecture halt (prospective, 2026-10-02)

Hold 30 candidate constructs and R5.13 lowering fixed while screening the
complete frozen B02 plus B01/baseline contract. Candidate #13-17 already state
arbitrary ordered case-sensitive normalization; #21-23/#44/#45 and core #30
frame error, state, default and migration count. Stop at the lowering gate:
R5.13 cannot generate normalization, legacy defaults, insertion or typed task
results. Do not add a B02-specific branch, reuse the handwritten B01 template
as source-authoritative generation, or run acceptance without an authorized
candidate. Study general compiler breadth separately on non-task domains before
any retry; historical R5.2.2 classifications remain intact. See
`benchmark/results/phase5c/R5_14-B02-FROZEN-ARCHITECTURE-PRESSURE.md`.

## R5.13 constrained generative lowering (prospective, 2026-10-02)

Generate the operation's actual guarded control flow, typed result and bounded
keyed state replacement from non-task semantic data, leaving file I/O and event
transport in a domain-neutral runtime. Keep generated artifacts disposable and
challenge their provenance against the source contract and public/file endpoints.
Use an independent case verifier over the same source, plus a compiler fault
that grounds but fails conformance, to test the circularity boundary. Reject
valid relations beyond this subset explicitly; neither successful generation
nor test count licenses scaling or construct #31. See
`benchmark/results/phase5c/R5_13-SEMANTIC-DRIVEN-GENERATIVE-LOWERING.md`.

## R5.12 general lowering gate (prospective, 2026-10-02)

Keep the 30-core candidate provisional. R5.11's operation label hashes cannot
stand in for behavior derived from typed semantics: the B01 target template and
most verifier rules are separately authored. Introduce only a bounded,
target-neutral **validating** typed #45 lowerer for relations already justified;
use a non-task mutation and an explicitly unsupported valid combination to
challenge it. Two B01 read-only success cases now pass through this validator,
but B01 target generation remains manual. Gate further frozen-request testing
on a genuinely generative, source-authoritative operation path and independent
non-task challenge. See
`benchmark/results/phase5c/R5_12-POC-HEALTH-GENERAL-LOWERING-GATE.md`.

## R5.11 separately generated B01 integration (prospective, 2026-10-02)

Compose the 30 candidates for B01 insertion/completion framing, exact ordered
selection, versioned defaults and cardinality before building; do not introduce
#31 or an unsupported CRITICAL ordinal comparator. Generate a *new* B01-only
artifact with operation-level digests and persistence/operation events, then
challenge each event with independent CLI and file observations before case
conformance. Keep the historical checkpoint untouched. A B01-specific typed
adapter is appropriate as an integration experiment, but not a substitute for
a checked general #45 compiler or a language freeze. See
`benchmark/results/phase5c/R5_11-B01-INSTRUMENTED-INTEGRATION.md`.

## R5.10 cardinality relation (prospective, 2026-10-02)

The frozen v2 B01 three-row migration reports 3 although all priorities are
already present. Count legacy records converted by an explicit invocation,
not missing fields. Exact selection and keyed preservation cannot connect a
finite population to an integer field; add the general typed relation
`cardinality(collection, integer)` as prospective core #30, rather than a
migration-specific primitive, aggregate framework or derived index arithmetic.
Keep integer outcome typing distinct from grounding and versioned lowering.
See `benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md`.

## R5.9 B01 complete-contract gate (prospective, 2026-10-02)

Use the entire frozen B01 and inherited baseline, then attempt composed exact
selection/ordering and operation-state relations *before* considering new
vocabulary. Treat “above HIGH” as ordinally underspecified absent an observable
rank comparator, and preserve normal `(created_at,id)` order. Stop before core
construct #30: migration's numeric count relation needs focused review, while
full-schema contract integration, checked interface lowering and challenged
per-operation B01 execution are distinct responsibilities. Passing frozen
cases on a pinned artifact plus independent public/durable endpoints is not
R5.7 grounding without an internal event or B01 #45 conformance. See
`benchmark/results/phase5c/R5_9-B01-END-TO-END-ADEQUACY-RESTART.md`.

- Bounded collection operations give a validator a tractable semantic surface;
  they postpone arbitrary algorithms and may require a new v0.2 query operator.
- Stable entity IDs make rename impact observable and keep references intact.
  Command tokens remain stable public interface values unless deliberately edited.
- A type system, state invariants, explicit effects and contracts remain useful
  with AI authors: they limit the blast radius of a mistaken edit and expose
  assumptions that ordinary source often leaves implicit.
- Hand-optimized syntax, implicit imports and prose-only guarantees offer no
  benefit when humans are not expected to author the representation manually.
- A generated Python file embeds validated AIR and a fixed backend runtime.
  It is an artifact; changing its behavior requires changing AIR or the compiler.
- v0.2 adds a semantic index and structural diff; it does not model concurrency,
  transactions across multiple states, arbitrary computation or multiple backends. JSON replace is atomic for
  one file, not a concurrent multi-process transaction.
- Phase 1's AIR document and import paths remain available as historical and
  compatibility interfaces. New documentation and generated headers say Lykoi.
- The priority experiment required two general semantic extensions: an optional
  typed input with default and a typed field-equality selection of a collection.
  Neither extension accepts Python snippets.
- An explicit additive migration avoids reinterpreting legacy persisted state;
  its narrow vocabulary cannot express every future data migration.
- Intent may be probabilistic. Program semantics should not be. Plans use
  explicit ID-addressed operations, a source-model fingerprint and deterministic
  validation; semantic relationships are derived from the canonical model.
- A nullable timestamp is distinct from an absent record field. A clock-based
  predicate names its capability and incurs a checked `clock_read` effect;
  scenario fixtures hold a fixed clock instant for repeatable verification.
- If the system knows an operation is invalid, an AI-generated change must not
  silently introduce it. Validate lifecycle mutations and scoped authority
  before generation. Behaviors possess the minimum declared authority needed.
- A completed task with an old due date is a valid persisted record; "not
  overdue" is a derived-query guarantee. Evidence labels distinguish
  structural constraints, runtime checks and actually executed scenarios.

Modification experiments should record changed AIR IDs, validation diagnostics,
generator output hash and application test results for each request.

## Phase 5C semantic-first benchmark direction (prospective)

Use a bounded bridge from the frozen B01–B16 requirements and corrected R5.2.2
executable boundary instead of requiring exhaustive reconstruction of every
Python-test path before B17. Preserve unfinished R5.3 evidence and its unknown
global coverage. A small typed requirement format should name scenarios,
preconditions, observations and supersession lineage; B17–B20 will be authored
semantic-first and independently checked before exposure. See
`benchmark/results/phase5c/R5_4-BOUNDED-BRIDGE-DECISION.md` for the exact
authorization boundary and gates. This is a methodological decision, not a
finding of equivalence or improved efficiency.

## Phase 5C B17 partial-dependency measurement (prospective)

Keep the existing request-level outcomes through B20 for comparability with
B01–B16: B17 completion requires B16's persistent users/ownership, so a track
missing B16 is request-level `BLOCKED_BY_GAP -> B16`. Preserve independently
observable B17 clauses as separate diagnostic evidence, without partial
achievement or semantic activation. Model exact clause prerequisites so the
request-level dependency can be derived without flattening all B17 clauses to
one opaque edge. Conventional continues with full B17 acceptance on its B16
state. See `benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md`;
this is not a result from a B17 run or a rule for future benchmarks.

# Prospective Phase 5C format boundary (2026-10-02)

Keep the invariant rule prototype separate from existing scenario plans until
clause IDs and CLI carrier bindings can be independently checked. Use a small
typed AST (finite sequence and directed graph domains; named transformations,
comparisons and graph validity) rather than example enumeration or arbitrary
Python predicates. The fresh adequacy screen halts on B01 selection, so this
is an experimental design decision, not an acceptance or schema freeze. See
`benchmark/results/phase5c/R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md`.

## Exact selection prototype (2026-10-02)

Use a declarative, typed exact-selection relation rather than a named
HIGH/tag filter or an executable predicate. Keep B02's stable-unique
transformation and B14's graph invariant separate: forcing either into
selection loses first-occurrence or reachability precision. Count vocabulary
growth before proposing another operator. B01 still lacks a general
state-field transition and explicit normal-order binding; stop adequacy there.
This is an unfrozen prototype decision, not a benchmark protocol change.
# Prospective B01 relation boundary (2026-10-02)

Keep ascending normal ordering independent of exact source-relative selection:
the latter selects occurrences from an already ordered source. Prototype
migration as keyed before/after preservation with a missing-field default,
reusing finite transition scope rather than merging ordered tag normalization
or dependency-graph integrity into one broad mutation operator. Both are
unfrozen design hypotheses, not changes to the Lykoi compiler or an acceptance
freeze. See `benchmark/results/phase5c/R5_4-B01-ORDER-TRANSITION-ADEQUACY-HALT.md`.

## Prospective operation-contract binding (2026-10-02)

Investigate one typed operation-reference contract over input, actual
pre-state, outcome and actual post-state, rather than command-specific binders
or an unrestricted logic language. Reuse selection, ordering, equality and
keyed defaults under a universal applicable-state/invocation scope. The
synthetic tuple checker does **not** implement universal public-operation or
storage binding, and keyed insertion/update frames are still open. Treat
priority domain order separately from normal list order; the frozen B01
contract gives no observable comparator. Halt B01 adequacy and keep the
format unfrozen. See `benchmark/results/phase5c/R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md`.

## R5.4 semantic architecture checkpoint (prospective, 2026-10-02)

Recommend a hybrid for the *next prototype iteration*: semantic source states
abstract typed operation contracts; compiler/interface metadata checks public
entry points and durable state views; an independent runtime observer supplies
actual same-invocation tuples; a verifier evaluates conformance for those
tuples. Neither static binding nor finite traces establish universal correctness.
The present #45 mixes contract and grounding, while the 45-entry inventory
counts observation and benchmark-lineage machinery as vocabulary. Splitting
these responsibilities and integrating types is required before another B01
adequacy attempt; this recommendation does not implement or freeze that split.
See `benchmark/results/phase5c/R5_4-SEMANTIC-ARCHITECTURE-CHECKPOINT.md`.

## R5.5 responsibility split (prospective, 2026-10-02)

Extract #45's typed relation as a provisional semantic contract and place
implementation slot mapping, execution fact records and case-scoped comparison
in distinct modules. Retain the seven R5.4 synthetic witnesses through an
explicit compatibility extractor; do not relabel them execution traces. Keep
binding metadata and benchmark lineage out of core vocabulary. The checked
slot map does not validate a real entry point or durable state view, and a
self-reported observation source does not prove capture fidelity. Consequently
the gate is **R5_5_ARCHITECTURE_PARTIAL**, pending independent grounding, rather
than a claim of universal conformance or permission to restart B01. Generated
target code remains an artifact; semantics and target-specific adapter details
must not be conflated. See
`benchmark/results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md`.

## R5.6 grounding architecture (prospective, 2026-10-02)

Recommend a scoped hybrid before returning to semantic adequacy: compiler-owned
normalized public/persistence boundaries and versioned per-operation provenance,
with independently captured public arguments/outcomes and committed durable
state readback for selected calls. Binding metadata identifies a boundary; it
cannot attest to execution. Generated instrumentation improves correlation and
diagnosis but shares compiler defects with implementation, so an external
observer must challenge it. A mismatch between deployed bytes and provenance
invalidates provenance-based claims; undeclared writes and unsynchronized
concurrent changes limit claims to explicitly observed resources and schedules.
Machine-oriented generated structure is permitted where it improves coverage or
traceability, without making unreadability a goal. Adopt distinct evidence
levels; finite grounded cases are never universal proof. This is an architecture
to prototype, not an implemented adapter or a benchmark gate advance. See
`benchmark/results/phase5c/R5_6-GROUNDING-TRUST-MODEL.md`.

## R5.7 implementation gate (prospective, 2026-10-02)

Retain the R5.6 hybrid grounding direction for single-resource, isolated
observed cases: deterministic generated boundaries and per-operation hashes are
challenged against separately captured public calls and committed file bytes
before using the R5.5 conformance evaluator. Incorrect behavior can be
grounding-valid while false event reports and modified artifacts are rejected.
The decision is **partial**, because the current abstract contract cannot type
conditional error outcomes or their no-write obligations; the prototype's
separate adapter policy is not a semantic substitute. Halt before core construct
#30 and review that exact expressiveness gap. See
`benchmark/results/phase5c/R5_7-GROUNDING-PROTOTYPE.md`.

## R5.8 conditional outcomes (prospective, 2026-10-02)

Choose **EXISTING_CONSTRUCT_GENERALIZATION** for #45: its typed operation
relation now accepts an outcome record with a finite class domain and composed
Boolean/state predicates. Implications assembled from `and`/`not` bind outcome
and post-state conditions to one invocation. Do not add error-specific
semantics or construct #30. Semantic equality of the declared state is the
failure postcondition; attempted writes require separate effect/observation
work if that stronger property is requested. This decision resolves the narrow
R5.7 conditional classification gap without changing the benchmark boundary.
See `benchmark/results/phase5c/R5_8-CONDITIONAL-OUTCOME-EXPRESSIVENESS.md`.
