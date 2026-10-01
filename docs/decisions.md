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
  compatibility interfaces. New documentation and generated headers say Axiom.
- The priority experiment required two general semantic extensions: an optional
  typed input with default and a typed field-equality selection of a collection.
  Neither extension accepts Python snippets.
- An explicit additive migration avoids reinterpreting legacy persisted state;
  its narrow vocabulary cannot express every future data migration.

Modification experiments should record changed AIR IDs, validation diagnostics,
generator output hash and application test results for each request.
