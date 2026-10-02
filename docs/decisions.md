# Experimental decisions

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
