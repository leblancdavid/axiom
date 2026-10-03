# R5.32 public input binding profile

Versioned prospective interface/runtime contract, 2026-10-03. This profile wraps
`benchmark.semantic.current_pipeline`; it changes no core semantic meaning or
v0.3 frozen transport. Candidate core remains 30.

## Authority and interface

`current_pipeline.checked(application)` establishes the sealed CheckedPlan.
`public_binding_r5_32.metadata(plans, policy)` consumes only checked input slot
shapes. Supported public slot shapes are string, integer, instant, boolean and
optional versions of those shapes. Unsupported shapes fail before generation.
Argument aliases and optional finite decode domains are explicit binding policy.
Domains contain distinct concrete values valid for the checked base type; no
enum type is added and no domain is inferred from operation guards.

`public_binding_r5_32.generate(application, directory, policy)` generates the
semantic application through current_pipeline and installs a generic public
adapter, decoder, metadata and separate artifact identity. The synthetic CLI is:

```
python public_adapter_r5_32.py OP STATE SEMANTIC_TRACE BINDING_TRACE INVOCATION RAW_JSON GENERATION
```

The administrative paths/identities are explicit synthetic transport plumbing.
`RAW_JSON` is an object mapping public argument names to raw JSON data. A missing
key is omitted. JSON null is supplied; it is not absence for these scalar types.
Whole-payload malformed JSON/non-object data, unknown operation/argument,
required omission, malformed scalar and outside-domain failures have distinct
machine categories. This profile uses standard-library JSON object decoding;
duplicate keys follow that decoder's last-key behavior. A stricter duplicate-key
transport policy would require independently versioned metadata/verification.

## Decode rules and suppliedness

- String accepts JSON strings verbatim, including empty/blank strings. Application
  nonblank requirements belong to semantic predicates.
- Integer accepts a JSON integer (excluding bool) or ASCII decimal string with
  optional leading `+`/`-`, at least one digit, no whitespace/separators. Resource
  limits of Python integer conversion can reject exceptionally long strings.
- Instant accepts exactly the existing runtime's valid UTC-Z string domain.
  Existing `is_instant` semantics are reused, not tightened to a new RFC profile.
- Boolean accepts JSON bool only.
- Finite decoding checks explicit domain membership after scalar decoding.

Each declared slot records `supplied: bool` and one of OMITTED, BOUND_TYPED,
BINDING_FAILED. SUPPLIED_RAW is the conceptual pre-decode state, not a separately
persisted event. All-or-failure binding exposes a complete typed input record or
`input: null`; partially successful values cannot trigger operation invocation.
An omitted optional key stays absent in the semantic record. Fallback executes
inside generated semantics; the binder neither materializes defaults nor uses
fallback to validate supplied malformed data. Existing `present` over optional
input membership can distinguish explicit fallback-equivalent input.

## Failures and observable outcomes

A failure item has `argument`, checked `slot`, `expected` base shape and closed
`category`. Boundary-wide failures use null argument/slot where appropriate.
Raw values are excluded from diagnostics and binding evidence. Metadata retains
the domain expectation; runtime trace typed inputs retain existing disclosure
behavior. Synthetic study fixtures explicitly retain their non-sensitive raw
examples in external research evidence.

Binding failure returns exit 2, empty stderr and JSON:

```
{"status":"binding_failure","errors":[{"argument":"when","slot":"when",
"expected":"instant","category":"malformed_scalar","code":"input.malformed_scalar"}]}
```

Category-to-code mapping is declared by binding policy; all categories require
nonempty string mappings. A successful binding invokes the generated operation
and returns exit 0 with `{"status":"semantic_outcome","outcome":...}`. A typed
semantic rejection is still a semantic outcome. Backend/runtime failures retain
nonzero process failure; they do not acquire fictitious semantic execution events.
Binding failures are public boundary results, never undeclared #45 outcomes.

## Evidence and verification

Binding evidence records operation/invocation/generation, slot suppliedness and
decode result, `semantic_invoked`, public result and independent-byte-comparable
pre/post digests. Semantic evidence exists only for actual invocation. Observers
use fresh trace paths and independently capture payload/output/exit and durable
bytes. Grounding matches evidence to those observations; a separate concrete
decode oracle checks binding conformance without calling the binder. Only a
conformant binding passes its expected typed input to current_pipeline.challenge
for independent semantic grounding/conformance.

The binding-failure obligation is **no semantic state transition**, checked by
decoded durable equality. Observed byte equality is also recorded. Neither proves
the absence of a same-byte physical write, transient mutation or hidden invocation
with no observable effect. Binding trace writes themselves are expected.
Artifact seals and matching evidence are integrity/consistency checks, not hostile
runtime attestation or universal correctness proofs.
