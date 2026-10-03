# R5.29 — Authoritative pipeline consolidation (prospective)

## Architecture decision recorded before implementation

New non-task semantic applications use one entry point, `benchmark.semantic.current_pipeline`.
The application declares one identity, one durable state shape and named operations.
Each operation has a semantic AST contract. The R5.27 unified analyzer validates
it and produces a source-bound checked plan; the R5.28 relation planner and
emitter consume that plan to generate one artifact. The generic runtime owns the
durable boundary and execution event. Independent public/file observation grounds
the event before the semantic verifier interprets the originating source and
checked facts. Generated Python never supplies the verifier's expected behavior.

Historical R5.23 hash-locked generator/runtime/evidence modules remain unchanged
and callable by historical tests, but are retired from *new* semantic application
development. R5.25 and R5.26 are historical prototypes. The R5.27 analyzer and
R5.28 checked-plan emitter/verifier are promoted as implementation components,
not competing entry points. The v0.3 `air_compiler` backend remains the separate
canonical task-manager model compiler; this prospective boundary does not rename
or replace its versioned model semantics. Unsupported raw input, cross-shape
migration and frozen transport remain explicit limits.

The following sections record measured results after implementation; the gate is
based on whole-program behavior and architecture, not test counts.

## 1. Compiler-path inventory and lifecycle

| Component | Earlier/current role | R5.29 classification |
| --- | --- | --- |
| `generative_r5_13.py` AST/type/relation planner/emitter | R5.13 through locked R5.23 read/write implementation | HISTORICAL_EVIDENCE, RETIRED_FROM_CURRENT_USE; hash-locked |
| `generative_runtime_r5_13.py`, `generative_evidence_r5_13.py` | R5.13/R5.23 execution, grounding and verifier | HISTORICAL_EVIDENCE, TEST_FIXTURE; hash-locked |
| `optional_refinement_r5_25.py` | presence prototype | HISTORICAL_EVIDENCE, TEST_FIXTURE |
| `type_integration_r5_26.py` | read-only checker/emitter/verifier | HISTORICAL_EVIDENCE, TEST_FIXTURE |
| `unified_types_r5_27.py` | unified analyzer, source digest, scopes, order and operands; still delegates legacy expression forms to `_compile` | CURRENT_GENERAL analyzer; legacy checker delegation DUPLICATED |
| `refined_generator_r5_28.py` | checked emitter and relation planner; also legacy `typed`/`ordering_plan` and standalone generator | CURRENT_GENERAL emission component for application entry; old standalone checks DUPLICATED/TEST_FIXTURE |
| `refined_runtime_r5_28.py` | typed file/CLI boundary, helpers and capability log | SHARED_INFRASTRUCTURE, extended generic application dispatcher |
| `refined_evidence_r5_28.py` | independent contract interpretation and individual-operation grounding | CURRENT_GENERAL verifier component; standalone observer TEST_FIXTURE |
| `current_pipeline.py` | application-level checked entry, combined artifact, observation and grounding | CURRENT_GENERAL for its supported application subset |
| `src/air_compiler/` | canonical v0.3 task model backend | SHARED project infrastructure, distinct versioned model; not this prospective profile |

The same checked R5.27 plan is used to validate each operation and to lower its
relations and expressions. The application emits five functions into ONE
`operation.py` and ONE generic runtime; no feature-based compiler routing is
offered by `current_pipeline.generate(application, directory)`. Historical tests
continue to import their versioned modules explicitly. Source IDs, artifact and
runtime hashes and a generation digest are bound to the application; a changed
artifact must update its disposable manifest to pass integrity. The runtime
dispatches operation names generically and records that name in the invocation
event. The observer reads public stdout and state bytes independently; only
after grounding does `refined_evidence_r5_28.conforms` interpret the source
contract. No generated expectation is used.

**Important architectural limit:** the emitter is still an R5.28 module with
legacy self-checking/ordering branches, and the unified analyzer delegates old
expression kinds to the older `_compile`. The application assembler extracts
the checked `execute` function from rendered Python text, rather than using a
first-class multi-operation IR. This is an identified duplication and fragile
integration seam, not completed consolidation of all established capabilities.

## 2. Five-operation application and continuity

`benchmark/harness/test_current_pipeline_r5_29.py::application` defines a
publication archive, one `sequence<record>` durable shape and `create`, `query`,
`ordered`, `replace`, `remove`. Create uses external identity and UTC clock,
optional typed input, fallback label, exact framed insertion and a typed record
outcome. The query uses `present(seen) AND before(seen, cutoff) AND
equals(code,target)`; ordered read sorts selected rows by chronological `created`
then code. Replace guards cardinality-one refined selection and returns a
post-state projection; removal guards the same predicate and removes by key.
Each command has its own typed input and branch contract, sharing application
identity, state, generated artifact, runtime and provenance.

Executed chain: create A (created LATE, seen EARLY), create B (created EARLY,
seen LATE), query A, ordered query (`B,A`), replace A (`label=new`), query A
(`new`), remove A, query A (empty). All eight calls are independently grounded
and conformant; each prior independently read `after` byte string equals the
next independently read `before` byte string, including reads. Final durable
state contains B. The created external `instant` survives serialized storage
and is chronologically ordered by a generated read; the optional `seen` survives
create, serialized storage and read-side presence plus `before`. Ordering does
not rewrite the storage file. A separate persisted-present-value test checks
the same read path.

Optional *absence* through the constructor is **not established**: a typed
record expression referencing an omitted optional input currently raises on
the generated dictionary lookup. The absent-row refinement fault uses an
independently prepared typed state fixture. This limits the requested full
optional read-after-write closure; no optional semantics were changed here.

## 3. Mutation, grounding and fault evidence

Semantic-only changes to query cutoff, ordering key, replacement value and
remove target are regenerated through the application entry without compiler,
runtime or verifier edits; each changed program executes and conforms with
the changed result. Source-digest checks prevent stale checked-plan reuse.
Public outcome, internal event, independent pre/post durable bytes, logged
externals and artifact/runtime/application provenance are compared before
semantic evaluation.

| Disposable fault in single artifact | Independent outcome | Grounded | Conformant |
| --- | --- | --- | --- |
| A absent optional row included | wrong query population | yes | no |
| B chronological key inverted | wrong ordered population | yes | no |
| C replacement updates `seen` instead of `label` | wrong durable post-state | yes | no |
| D external clock result differs from persisted clock | wrong durable post-state | yes | no |
| E out-of-band durable corruption between commands | previous independently observed post bytes differ from next independently observed pre bytes | each invocation individually; chain fails | not a conformance-only result |

Fault E exposes a continuity discrepancy but the injection is between calls,
not an operation-caused unintended write. Therefore it is **not** the exact
requested operation-write fault witness.

## 4. Regression, unsupported semantics and capability matrix

The full historical harness verifies selection, normalization, string/integer
ordering, fallback, external values, keyed defaults, cardinality, insertion,
remove, replace, projections, record outcomes, overlapping defaults and
same-shape migration; R5.26–R5.28 verify refined reads/writes, chronological
ordering and `before`. These *historical regressions* do not establish each
capability through the new application entry. The machine-readable per-capability
assessment is in `R5_24-type-matrix.json` under `r5_29_current_application`.
Unsupported state/input shape, unrecognized state relations, incompatible
operand shapes and unguarded optional `before` reject during checking/planning.
Malformed raw input, typed malformed outcomes, cross-shape migration and frozen
transport are not supported; no scope expansion was made.

Verification: full benchmark harness 274/274 (five new R5.29 tests), including
architecture/grounding/semantic and R5.10–R5.28 focused suites;
application/compiler 31/31; validation OK; safety 0 capability violations
and 0 invalid transitions. Matrix JSON parsed; `git diff --check` passed.
LF→CRLF working-copy notices are separate from failures. The full historical
harness invokes its existing nested benchmark regression checks, including
previously recorded B02 cases; these were not used to generate, ground, or
evaluate an R5.29 B02 candidate and do not constitute an R5.29 retry.

## 5. Blockers, architecture gate and next recommendation

The count of **designated** current non-task application entry points is ONE.
However, duplicated historical inference/ordering in its downstream emitter,
text-based program assembly, historical-only coverage for many general
relations, incomplete absent-optional write closure and the incomplete E fault
mean that the requested authoritative *whole-general-pipeline* gate is not met.
Optional refinement and instant ordering are demonstrated inside the five-command
application, but R5.23's whole-general-pipeline blockers remain
`PARTIALLY_RESOLVED`, not `RESOLVED_IN_AUTHORITATIVE_GENERAL_PIPELINE`.
Suppliedness/well-formedness, malformed-input typed outcomes, cross-shape state
evolution and frozen transport binding remain distinct. Candidate core semantics
remain **30**, no #31. New machinery: application assembler, generic runtime
dispatcher, application-level observer/provenance, tests; historical files
remain pinned. No B02 retry or frozen B02 acceptance was run as R5.29 work;
historical suite diagnostics do not constitute a new retry. Phase 5C paused,
B03 untouched, B17 unexposed/unclassified, semantic-first format globally
unfrozen, R5.2.2 historical benchmark authority; no universal correctness claim.

**Exact R5.30 recommendation:** replace render-text extraction with a checked
multi-operation IR feeding the same emitter, eliminate downstream duplicate
type/ordering inference on the current entry, transfer the full historical
general-capability regression matrix to it, and independently demonstrate
optional absence construction plus a write-caused continuity fault without
altering established semantics. Keep the frozen benchmark boundary unchanged.

**Decision gate: `R5_29_PIPELINE_CONSOLIDATION_PARTIAL`**
