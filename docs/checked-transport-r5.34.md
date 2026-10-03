# Lykoi prospective checked transport — R5.34

Versioned interface/runtime machinery, not application semantics. The sole
semantic entry remains `benchmark.semantic.current_pipeline`. Core stays 30,
no #31; R5.32 binding and R5.33 operation semantics are unchanged.

## Responsibility

Transport routes public calls, preserves supplied raw membership, calls binding,
invokes generated execution and encodes checked outcomes. It cannot implement
predicates, defaults, record transitions, normalization, migration or application
validation. Explicit finite decode domains are R5.32 checked interface restrictions,
not inferred semantic predicates. Successfully bound values may be semantically
rejected independently.

## Checked profile

`checked_transport_r5_34.specification(plans)` derives a default machine-oriented
specification. `validate(plans, spec)` consumes sealed input slots, outcomes,
pre/post shapes, applicability presence and contract digest; no alternate analyzer.
A specification is a list of descriptors:

* `public` external operation name; `semantic` checked operation key;
* `arguments`: public name, semantic slot, scalar `decoder`, raw `representation`
  (`text`/`json`) and optional explicit finite `domain`;
* `outcomes`: exact checked tag/payload type, `json` encoding and public status
  (`SUCCESS`/`SEMANTIC_FAILURE`).

Requiredness derives from slot typing. Required slots must be mapped; optional
mappings may be omitted. Public operation subsets/aliases are permitted, but
public names and per-operation argument/slot bindings must be unique. Every
declared outcome must be mapped with its exact checked type. Default profiles
classify all tags as success; failure classification is explicit public policy,
never guessed from tag spelling or application predicates.

Unknown operations/slots, duplicate routes/bindings, required mapping absence,
incompatible decoders/representations/domains and incomplete/foreign/wrongly typed
outcomes reject. One registered decoder per scalar base type reuses R5.32;
extensible decoder plugins are not implemented.

Generation validates before normal artifact production and delegates to
current_pipeline. Persisted profiles carry application ID/source digest, unit
contract digests and generation identity. Artifact seal covers profile, adapter
and binder; runtime checks semantic artifact/runtime/manifest/profile identities
before binding or reading state. Stale regeneration rejects. These are revision/
integrity checks, not signatures against hostile writers. Process-local plan
node identities are not serialized as stable identities.

## CLI

```text
python transport_runtime_r5_34.py STATE SEMANTIC_TRACE TRANSPORT_TRACE INVOCATION PUBLIC_OPERATION [--ARG RAW_VALUE ...]
```

Infrastructure paths are separate from semantic input. Each flag/value pair
supplies one raw argument. Absence creates no key; empty text remains supplied.
Text stays text until R5.32 binding, including integer/instant decoding. Generic
JSON representation parsing yields raw wire data (e.g. false), not semantic
values. Repeated flags reject. Positional semantic arguments, collection/nullable
input binding and implicit missing-store initialization are outside this profile.

Generic result encoding validates tag/payload against checked shapes and emits
unchanged scalar, record, nested record or sequence data as tagged JSON.

| Status | Exit | Meaning |
| --- | --- | --- |
| SUCCESS | 0 | declared typed outcome classified as public success |
| SEMANTIC_FAILURE | 1 | declared typed outcome classified as public failure |
| BINDING_FAILURE | 2 | structured R5.32 failure, no semantic invocation |
| INVOCATION_FAILURE | 3 | generated runtime rejected, no typed event/outcome |
| TRANSPORT_FAILURE | 4 | invalid route/grammar or profile integrity rejection |

Normal statuses use stdout envelopes with empty public stderr. Integrity errors
use stderr before trace/state access. Arbitrary stream/envelope/exit configuration
is not implemented. Generated stderr is retained independently as evidence.
Availability belongs to generated pre-state typing/applicability; transport keeps
metadata but does not evaluate/copy state-version predicates.

## Evidence and future adapters

Independent observation records command/argv, stdout/stderr/exit and durable
pre/post bytes. Transport events record raw arguments, suppliedness/binding and
separate generated subprocess response. Independent argv reconstruction, R5.32
decode oracle and current semantic challenge produce separate transport-binding,
input-binding, semantic-execution and transport-output verdicts. Null means no
applicable/evaluable verdict. Runtime rejection does not earn semantic conformance.
Snapshots can expose forbidden durable mutation but do not prove no transient
writes, concurrency isolation, crash atomicity or malicious-runtime sandboxing.

Future HTTP/RPC/GUI adapters need wire routing/membership extraction and public
encoding/status translation around common checked descriptors, R5.32 binding
and generated invocation. They need independent actual-wire observations/faults.
They must not implement application transitions/defaults. No network/server or
additional transport is implemented.

Evidence: [R5.34 result](../benchmark/results/phase5c/R5_34-CHECKED-TRANSPORT-BINDING.md).
