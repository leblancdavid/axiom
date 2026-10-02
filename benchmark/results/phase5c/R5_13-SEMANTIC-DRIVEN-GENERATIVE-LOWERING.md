# R5.13 — Semantic-driven generative lowering (prospective, 2026-10-02)

**Authority:** R5.2.2 remains historical benchmark authority. This is a
disposable, non-task synthetic experiment, not B01 generative coverage or a
frozen-request run. The authoritative sources are
`benchmark/semantic/r5_13-contract-{a,b,c}.json`; the test composes a fourth
contract D from A. Target Python is generated into temporary directories.

## 1–6. Domain, subset, structural typed lowering and implementation

Containers have typed `code`, `seal` and `zone` fields. A typed release request
names a code; durable state is a JSON record sequence. Contract A selects
exactly one matching locked container and returns tagged `released(code)` while
replacing its seal with `open`; otherwise it returns tagged
`unavailable(reason)` without writing. This is neither a task-manager domain
nor designed against a frozen request. The zone is an additional existing
state relation used in the structural variant.

**Declared supported subset:** record input; finite sequence-of-record state;
typed string/integer/Boolean references into input, pre-state and selection
item; typed literals, equality, conjunction, negation, exact selection and
cardinality; ordered guarded #45 outcome alternatives with string payloads
and final unconditional alternative; preservation or bounded keyed field
replacement. Guards are first-match; replacement updates all equal-key rows,
not a uniquely constrained single row. There is no concurrency guarantee.
This is a constrained projection of existing candidates, not construct #31.

**Unsupported existing capabilities:** nullable values, order, membership,
trim, nonblank, map(trim), stable uniqueness, graph/edge/acyclicity, clock
instants/offsets/before, keyed `default_missing` (#44), general lifecycle and
transition relations, arbitrary payload types/state shapes and universal
quantification. These can be **VALID SEMANTICS, LOWERING NOT YET IMPLEMENTED**.

`generative_r5_13.py` checks AST types using R5.12's typed expression compiler.
It emits reference projection, escaped typed literals, Boolean expressions,
selection comprehension, cardinality length, branch conditionals, result
expressions and keyed record replacement or preservation. Identifiers are
quoted data/field references, never compiler dispatch cases. It does not
execute Python supplied by the contract. **GENERATED PROGRAM DATA/LOGIC** is
the emitted `execute` function with actual predicates, result and transition
code, rather than a copied JSON contract. **GENERIC RUNTIME** is
`generative_runtime_r5_13.py`: parse input/file, read pre-state, call execute,
persist on write, report outcome and event. It has no container field, tag or
predicate. **MANUALLY AUTHORED TEST HARNESS** is
`test_generative_r5_13.py`; `generative_evidence_r5_13.py` is independent
observer/challenger/verifier infrastructure, not executable domain behavior.
Durable file endpoints are independently inspectable; failure preserves raw
bytes. Single-file persistence does not guarantee concurrency safety.

## 7–8. Semantic and structural mutations

The compiler/runtime/adapter/verifier are unchanged between versions.

| Semantic diff | Generated artifact diff | Observed behavior on `c1` in `[{c1,locked,south},{c2,open,north}]` |
| --- | --- | --- |
| A→B: version A→B and selected literal `item.seal == locked` → `item.seal == open` | emitted comprehension predicate literal `locked` → `open` | A `released`, `c1.seal=open`, write; B `unavailable`, identical file bytes/no write. B succeeds on `c2`. |
| A→C: version A→C and selected field/relation `item.seal == locked` → `item.zone == north` | emitted comprehension indexed field `seal` → `zone` and literal `locked` → `north` | C `unavailable`, identical file bytes/no write on `c1`; succeeds on `c2`. |

Canonical contract / target artifact / generation SHA-256 prefixes:
A `711bd66b / 59ef7f70 / f3871dda`, B `28344b71 / 6d22bb32 /
2aea0196`, C `fc27b5dd / 2f1bcb97 / 5a88d3c8`. Behavior, not just
metadata, changes. B is a value mutation; C changes typed field structure.

## 9–11. Novel combination, negative lowering and type safety

D (composed as contract data from A in the test) uses
`not(input.code == "blocked")` rather than selection/cardinality, replaces
`zone` with `east` rather than `seal` with `open`, and returns literal `moved`
rather than the projected code. It generates without lowerer edits; `c1`
returns `released(moved)` and changes zone but not seal; `blocked` returns
`unavailable`. This is a supported novel composition, not arbitrary synthesis.

Valid #44 `default_missing` in a guard and in a transition explicitly raise
`UNSUPPORTED_LOWERING_CAPABILITY` rather than silently dropping meaning.
Invalid typed string-versus-sequence comparison, integer assignment to string
field, and integer payload for a string outcome raise `ValueError` before
generation, separately from unsupported semantics. The state is deliberately
bounded; shape and field references are statically checked. The generic runtime
checks input and pre/post state against generated type declarations; mistyped
runtime input exits without changing durable bytes.

## 12–16. Provenance, grounding, conformance, circularity, regeneration

Semantic operation ID/version and canonical contract digest feed the manifest
alongside artifact and generic runtime digests. Generation identity hashes all
three. Runtime events carry invocation/generation/input/pre/post/outcome and
write intent. The independent subprocess observer captures public exit,
stdout/stderr and raw pre/reopened post file bytes **before** reading the event.
The R5.7–R5.11-style challenge compares event to those independent endpoints
and contract/artifact/runtime integrity. Only grounded events reach the
case-scoped verifier, which interprets the **same originating typed contract**
using R5.12's evaluator plus independent transition evaluation. No second
hand-authored expected behavior contract exists. A/B/C/D selected cases are
grounded and conformant; a false internal post-state fails grounding.

The shared typed AST machinery could have common-mode defects; observation
alone does not prove lowering correct. A disposable injected *lowering fault*
generates a replacement retaining the old field value instead of the declared
new value. The contract remains A. Provenance and independent public/file/event
observations agree (**grounding passes**), while originating-contract
conformance **fails**. This distinguishes source authority from self-report.
File endpoints do not expose every intermediate effect.

Fresh identical A generations in two directories have byte-identical target
and equal manifests. No timestamps/paths/nonces enter generation; subprocess
invocation nonce varies intentionally. A manual appended target comment breaks
artifact integrity; regeneration overwrites it. Only semantic edit → regenerate
→ behavior change is authoritative, never a manual target edit.

## 17–21. Representation, generality, accounting and recommendation

Normalized typed reference ASTs make mutations and audits checkable and stable
hashes straightforward. Costs include verbose serialization, token overhead,
nested-reference/debugging complexity and plausible but incorrect well-typed
field, literal or branch-order choices. No controlled AI-authoring or token
measurement establishes that this representation is more productive.

Generality answers: **yes within this narrow subset** for multiple non-task
contracts A–D without domain-specific compiler code, behavioral value mutation,
behavioral structural mutation and novel composition. **Yes for the tested #44
negative cases**: valid unsupported relations fail explicitly. **Yes for
selected subprocess cases**: generated behavior is independently grounded and
checked against its originating contract. None of these establish universal
correctness, arbitrary state synthesis or B01 generative coverage.

**Construct accounting:** 30 candidate core constructs / 46 raw categorized
experimental entries, unchanged; no #31. New unnumbered responsibilities are
compiler type checking/emission, generic runtime/file adapter, operation and
artifact lineage, independent observer/challenge/verifier and test fixtures;
these are outside the core count and do not duplicate the 16 historical
numbered non-core entries.

**Exact next step:** keep Phase 5C paused; stress the same lowering on another
independent non-task state shape and adversarial compositions, then investigate
checked richer state/outcome binding and shared-verifier error modes before
reassessing B01 generation. Do not resume B02 or expose/classify B17.
Semantic-first format remains UNFROZEN, R5.2.2 remains authoritative for
historical execution, and the 30-core count is unchanged.

**Verification (repository root):** `python -m unittest discover -s
benchmark/harness -v`: 149 OK; `$env:PYTHONPATH='src'; python -m unittest
discover -s tests -v`: 31 OK. Focused discover patterns: architecture R5.5
6 OK, grounding R5.7 10 OK, `test_semantic*prototype.py` 33 OK, R5.10 4 OK,
R5.11 4 OK, R5.12 3 OK, R5.13 5 OK. `git diff --check`: exit 0, no whitespace
failures. Git separately emitted LF→CRLF working-copy warnings for four tracked
files (`b01_integration_r5_11.py`, `decisions.md`, `project-overview.md`,
`research-log.md`); these are not test failures.

R5_13_GENERATIVE_LOWERING_VALIDATED
