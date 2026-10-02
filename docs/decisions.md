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
