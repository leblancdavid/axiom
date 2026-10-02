# Semantic requirement prototype — prospective, unfrozen

The [R5.10 migration-count review](../results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md)
adds prospective core #30: `cardinality(C,n)` holds exactly when `C` is a
well-typed finite sequence and `n` is its nonnegative mathematical size.
`cardinality.py` checks a typed element domain (string, Boolean or record with
optional fields), an outcome record's projected integer field and equality.
Repeated elements count by occurrence. Boolean, floating and string counts
are rejected; negative integers are typed but non-conformant. This supplies no
arithmetic, ordering or aggregation. A separate R5.10 synthetic tuple composes
this relation with exact selection and #44 priority defaulting. It is not an
integrated #45 integer-outcome checker, versioned B01 lowering or B01 grounding.
The historical 45-entry ledger remains historical; the prospective count is
30 core (46 raw categorized entries), not a format freeze.

The [R5.5 architecture result](../results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md)
separates the #45 abstract relation (`contracts.py`), checked but ungrounded
interface slot map (`binding.py`), concrete record shape (`observation.py`) and
case-scoped verifier (`conformance.py`). `operation_contract.py` keeps the
historical combined synthetic fixture readable via explicit extraction; those
cases are not captured application executions. The scenario probe remains a
finite integration witness, not a universal contract verifier. B01 adequacy is
halted and the semantic-first format remains unfrozen.
The [R5.8 prospective contract semantics](../results/phase5c/R5_8-CONDITIONAL-OUTCOME-EXPRESSIVENESS.md)
generalize #45's typed tuple relation for a finite tagged outcome record
(`kind` in declared variants; `value` is a sequence of the declared record
type) and closed Boolean predicates. For typed outcomes, `checks` are
conjoined; each is `and` (at least two predicates), `not` (one predicate),
`equals` (two same-typed terms) or `default_missing` (pre/post or pre/pre).
Terms are typed slot `ref` (`input.rows`, `pre.records`, `post.records`,
`result.kind`, `result.value`) or a string `literal`. The latter state relation
compares the declared record/default view; on pre/pre it tests whether all
optional fields are present. A conditional obligation `C => P` is encoded as
`not(and(C,not(P)))`. There is no execution order in these predicates.
Historical untagged, flat-check contracts remain accepted. This is an unfrozen
synthetic contract prototype, not a change to the v0.3 model language.

`prototype.json` contains **selected witnesses**, not a transcription of all
B01–B16 clauses or the R5.2.2 oracle. `b17-draft.json` is a pre-exposure
semantic-first **draft**, not a frozen B17 fragment, case or replacement map.
Neither file authorizes skipping a historical test or classifying an attempt.
See the [bounded-bridge decision](../results/phase5c/R5_4-BOUNDED-BRIDGE-DECISION.md).
The [format adequacy halt](../results/phase5c/R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md)
records the original gaps. The subsequent
[B17 partial-dependency halt](../results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION-HALT.md)
records the frozen-text analysis; its classification question is resolved by
the [prospective adjudication](../results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md).
None of this is a pinned semantic schema or B17 acceptance freeze.
The [adequacy restart halt](../results/phase5c/R5_4-SEMANTIC-ADEQUACY-RESTART-HALT.md)
records the working controlled subprocess clock and the newly identified
finite-scenario expressiveness gap at B02; no downstream pre-exposure gate is
claimed complete.
The [invariant prototype restart](../results/phase5c/R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md)
adds typed universal collection/graph rules and links finite semantic fixture
cases, then halts the fresh B01–B16 screen at B01's missing general selection
rule. These fixtures are not CLI-derived acceptance cases and do not freeze the
format or certify the historical bridge.
The [selection restart](../results/phase5c/R5_4-SELECTION-ADEQUACY-RESTART-HALT.md)
adds a separate typed exact ordered-query prototype for B01/B03, with finite
positive and negative witnesses. Its [vocabulary ledger](../results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md)
measures 42 implemented prototype constructs. The restarted screen stops at
B01's remaining general state-field preservation/default and normal-order
binding gaps. `selection.py`, `invariants.py` and scenario `format.py` are
separate experiments, not a combined schema or acceptance bridge.
The [B01 order/transition restart](../results/phase5c/R5_4-B01-ORDER-TRANSITION-ADEQUACY-HALT.md)
adds independent typed `lexicographic_order` and keyed `default_missing`
relations with finite witnesses in `state-relation-fixtures.json`. Their
collection inputs are not yet universally bound to public commands and
persisted state. The B01 adequacy screen therefore still halts; the ledger
now inventories 44 unfrozen constructs.
The [operation-contract investigation](../results/phase5c/R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md)
prototypes typed input/pre/result/post tuples for an arbitrary operation,
reusing equality and `default_missing`. Seven synthetic witnesses distinguish
result, source and state errors, but do not bind actual invocations or prove
universal behavior. The ledger now counts 45 provisional constructs. B01 and
the adequacy gate remain halted; the meaning of priority “above HIGH” is
still uncertain as an independent semantic requirement.
Prospective blocked-request clause evidence has a
[separate diagnostic template](diagnostic-template.md); it never contributes
to `compile_plan`'s achieved-request input or to active replacements.

## Selected scenario prototype (v1; v2 experimental time extension)

Each scenario has a stable semantic `id`, a frozen requirement `origin`, a
lineage disposition (`adds`, `retains`, `replaces`) and one or more variants.
Variant applicability is a pair of explicit achieved-request `requires` and
`forbids` lists. The same ID can have distinct, **non-overlapping** variants
for different achieved histories. An optional `carrier` records a historical
method ID; it is *provenance*, not a skip directive. A future bridge must
verify its source hash, active disposition, predecessor edge and observations.

Steps execute in order in a fresh directory:

- `seed`: write a literal JSON value to `tasks.json` (a fixture, not an
  application mutation);
- `invoke`: call a public command with string arguments, binding its JSON
  success result or requiring an error code; success means exit 0, JSON stdout
  and empty stderr; error means exit 1, no stdout and the baseline JSON error
  envelope;
- `snapshot`: bind the exact bytes of `tasks.json` or `null` if absent;
- `observe`: compare two typed expressions (`equals`) or require distinct
  values. Expressions are a JSON `literal`, a prior `ref` with field/index
  access, a `list` of expressions, or `sorted` rows by explicit fields.

Prototype v2 additionally permits a named `clock` step with `source: utc_now`;
`clock_ref` is an instant bound once by that step, `instant` explicitly parses
an application field/UTC literal, and `offset` derives an instant in integral
seconds. `before` compares *typed instants* with a declared expected boolean,
distinguishing strict-before from equality. Parsing never reads the clock.
Fixture execution binds a controlled UTC value once. `probe.py` runs each
clock-dependent invocation through `clock_adapter.py`, a subprocess bootstrap
that binds timezone-aware `datetime.now` before loading the application. The
same instant is used for `clock_ref`, application clock reads and acceptance
observations; a missing or mismatched binding fails closed. The adapter rejects
naive/local clock reads. It is a disposable Python execution adapter for these
scenarios, not an application change or an authoritative acceptance freeze.

`relationships.py` is a separate prospective, checked requirement-ID
composition vocabulary: each record declares an exact ID, originating request,
achieved-history guard, `depends_on` IDs, and at most one `replaces` semantic
root. Validation rejects unknown/malformed targets, dependency cycles, future
replacement targets and nonroot targets. Composition requires an exact active
dependency, resolves a replacement root to its currently active assertion,
rejects inactive/duplicate replacements, and preserves unrelated roots. The
old scenario `lineage.prior` strings are **not** these checked records; the two
prototypes have not been integrated into a frozen clause inventory.

The validator rejects unknown keys, commands, predicates, unbound/duplicate
bindings, duplicate observations, inconsistent origins and overlapping
variants. It does **not** infer that chosen observations exhaust a requirement,
that a historical `prior` ID has the claimed meaning, or that a `carrier`
preserves every assertion. Prototype records are manually reviewed against
the frozen requirement and corrected source; those links must be independently
verified and hash-pinned before a prospective protocol freeze. The fixed CLI
command list and `tasks.json` adapter are benchmark-boundary mechanics, not
new Lykoi language semantics.

From the repository root, run
`python -m unittest discover -s benchmark/harness -p test_semantic_format_prototype.py -v`.
The disposable probe extracts only the application member of each pinned
post-B16 snapshot and runs applicable example plans in independent temporary
directories. Its successes are **witnesses for those scenarios only**; they
do not revalidate the full frozen R5.2.2 suites or prove equivalence to every
Python-test path. The B17 draft is only validated/compiled, never run against
an implementation.

## Before authoritative B17 acceptance

1. Trace all B01–B16 frozen clauses and *affected* historical assertions to
   stable IDs and original setup/observation phases. Pin the actual effective
   loaded R5.2.2 dispositions (including R4/R5 and repaired carriers) in both
   histories. If a replacement method is selected, enumerate and check all
   its retained observations and helpers; leaving it out is not permission to
   skip them. Preserve the executable parent for unselected methods.
2. Complete B17's semantic cases, including task mutation on every relevant
   command, missing/unknown actor, ADMIN/USER roles, permission precedence,
   read-only exemptions and no-write checks. Link each changed **active**
   historical site to its reviewed successor; adapt error and shape checks
   without dropping unrelated assertions. The draft's `prior` IDs are not a
   substitute for the carrier-retention inventory.
3. Build independently reviewed, backend-neutral derived cases and a
   fail-closed conditional composer. Pin source hashes, semantic records,
   executable cases, and selected suites; run both target histories on fresh
   B16 restores against the unchanged parent and composed suites. Freeze a
   separately versioned prospective protocol **before B17 exposure**.

Use [the authoring log template](measurement-template.md) for each B17–B20
cycle (time when measurable, record size, carriers and observations
inspected/changed/retained, corrections, independent verification and
post-freeze defects). Compare only against evidenced B11–B16 denominators,
accounting for different request complexity.
