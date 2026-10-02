# Semantic requirement prototype — prospective, unfrozen

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
Fixture execution injects a controlled UTC value. The disposable subprocess
probe cannot control the application's clock and **rejects** plans mixing
clock reads with CLI invocations; such plans need a separately verified
controlled application-clock adapter before executable acceptance.

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
