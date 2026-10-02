# R5.6 grounding and trust model — prospective, 2026-10-02

**Decision scope:** grounding architecture, not B01 capability repair or a new
acceptance protocol. [R5.5](R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md)
separated contract, slot binding, record and case verifier; its seven historical
tuples remain **synthetic**, not application traces. R5.2.2 remains the
authoritative benchmark execution boundary. B01 is inadequate and halted;
Phase 5C is paused; B17 is unexposed and unclassified; the semantic-first format
is UNFROZEN. Claims below distinguish *current implementation* from *proposed
architecture*.

## 1. Boundary inventory

Legend: **TRUSTED** = an explicit assumption in the current argument, not
verified truth; **CHECKED** = a stated predicate is mechanically enforced;
**OBSERVED** = an independent measurement of a particular run; **ASSUMED** =
relied on without a declared check; **UNGROUNDED** = no correspondence mechanism;
**UNKNOWN** = cannot determine completeness/fidelity from available evidence.
Statuses describe the *arrow*, not a claim that the node itself is correct.

```
 human requirement --[ASSUMED interpretation]--> Lykoi semantic representation
   --[CHECKED validity; TRUSTED compiler correctness]--> compiler/lowering
   --[CHECKED deterministic generation for current artifact; TRUSTED lowering]
      --> generated target implementation
   --[CHECKED model command references; UNGROUNDED prospective contract mapping]
      --> public operation boundary
   --[TRUSTED current runtime storage code; UNKNOWN effect completeness]
      --> persistence boundary
   --[ASSUMED process/environment/atomicity]--> actual runtime execution
   --[OBSERVED selected external CLI/file cases; UNKNOWN full effect coverage]
      --> observation capture
   --[UNGROUNDED record origin/fidelity in R5.5]--> execution record
   --[CHECKED record shape/slot projection/relation; TRUSTED record content]
      --> conformance verifier
```

| Arrow / current mechanism | Classification and failure at that arrow |
| --- | --- |
| Intent → semantic representation | **ASSUMED** interpretation: model or prototype contract can omit a requirement. Frozen text and R5.2.2 cases constrain benchmark claims, not complete interpretation. |
| Representation → compiler | **CHECKED** for current v0.3 model syntax, IDs, references and effects by `validator.py`; **TRUSTED** for validator soundness. R5.5 abstract contracts are separate, unfrozen prototype validators, not v0.3 integration. A valid model may specify the wrong behavior; a validator may accept an unsound binding. |
| Compiler → generated implementation | **CHECKED** generation determinism by compiler tests and `generator.py`'s artifact SHA-256 manifest; **TRUSTED** translation of meaning. The manifest lists *all* IDs for the single artifact, not per-operation provenance, does not verify deployed bytes at invocation, and a compiler defect can produce consistent wrong code and hash. |
| Generated implementation → public operation | **CHECKED** current command/behavior references and CLI construction in `runtime_template.py`; **UNGROUNDED** for mapping an R5.5 contract/binding to a real CLI entry, its raw arguments, defaults and error path. A similarly named but different function or stale command mapping may be observed. |
| Public operation → persistence boundary | **TRUSTED** current template's `state_layout`, `read_state`, `write_state`, `migrate`; **UNKNOWN** for coverage of all possible external writes. A different file, temporary file, cache or external resource may hold a divergent value. Current `os.replace` provides one-file replacement, not transaction/durability against power loss or concurrency. |
| Persistence boundary → actual execution | **ASSUMED** process isolation, storage namespace, filesystem semantics and capability values; no general scheduler/transaction model. A competing writer or runtime failure changes what the invocation actually saw or committed. |
| Actual execution → observation capture | **OBSERVED** for selected subprocess exit/stdout/stderr and independently read file bytes by R5.4 `probe.py`/external harness; **UNKNOWN** for unobserved resources/calls. `probe.py` has ordered `invoke` and `snapshot` steps, not a generic atomic four-slot capturer. A snapshot may be taken before commit or of the wrong namespace. |
| Capture → R5.5 execution record | **UNGROUNDED**: `observation.validate` checks a self-asserted `source: execution`, boundary string, sequence and four facts. No observer currently supplies authenticated same-invocation actual facts to `conformance.evaluate`; fabricated conforming tuples pass shape checks. |
| Record → verifier/verdict | **CHECKED** record shape, boundary equality, typed projection and supplied-tuple relation; **TRUSTED** input fidelity and evaluator correctness. `validate_trace` checks equal adjacent values, not absence of intervening writes. `evidence: observed_execution` is currently an API label, **not** verified provenance. A true verdict applies only to the supplied case. |

The current task manager's canonical source is `air/task_manager.json`; the
prospective contract in `benchmark/semantic/contracts.py` is **not** compiled
from it. Neither an R5.5 binding nor an observed CLI case presently closes that
cross-system link. The boundary proposed here must be implemented before
`observed_execution` can be read as a grounded assurance claim.

## 2. Correctness failure model

For a conformant-looking record, ask whether each fact came from the **same
selected public invocation** and its **declared actual durable state**:

| False appearance | Required discriminating evidence / residual limit |
| --- | --- |
| Wrong operation, stale binding, wrong decoded arguments (including omitted/default args) | Match invoked public entry token and raw argv/request, validated parse/normalization, generated operation ID and binding version; independently invoke that entry. ID emitted by the wrong lowering alone is not proof. |
| Pre-state from wrong path/tenant/schema, wrong time or cache | Resolve storage namespace from checked binding, inspect raw bytes/existence immediately before invocation, decode independently, record version and projection. Between snapshot and actual read there can still be a race. |
| Outcome transformed, error swallowed, wrong channel or failure after write | Record complete process exit/exception, raw output channels and decoded outcome; compare both; sample bytes after termination, including failure paths. An internal success recorded before public serialization is insufficient. |
| Post-state from memory or before durable commit; unexpected file creation/deletion | Reopen the declared persistent resource after successful boundary return/process exit, retain raw bytes/existence and compare semantic projection. Reopen establishes externally readable committed state under stated filesystem assumptions, not crash-safe fsync durability. |
| Right projected records but changed bytes, extra writes or hidden side effects | Compare byte snapshots and file inventory/effect sinks separately from semantic projection; isolate resource namespace. Undeclared network/global resources defeat a closed-world no-write claim. Identical before/after bytes do not prove no intermediate write. |
| Concurrent mutation / mixed invocation facts | Single invocation ID, ordered capture, isolated namespace or transaction/lock plus revision/commit tokens and repeatable snapshot; reject races or qualify the claim. A sequence field/equal adjacent states is not isolation. |
| Instrumentation bug, stale provenance or manually modified artifact | Independently compare public observations, regenerate and verify deployed artifact/metadata hashes, fail closed on mismatch; a matching compiler-generated label is not independent behavioral evidence. |

Threats are correctness failures, including honest compiler/observer defects;
hashes detect accidental drift under trusted hash/tooling, not malicious forgery.

## 3. Grounding-model comparison

Here **A** is external observation, **B** generated instrumentation, **C**
compiler-owned normalized adapters/boundaries, **D** static provenance, **E**
hybrid C+D with B for diagnostics and independent A for important effects.
All five operate outside core semantic vocabulary unless a state/effect relation
actually expresses application meaning. Target adapters and boundary tables are
compiler/binding metadata; event envelopes are runtime; case decisions are
verifier; independent oracles are evidence machinery.

| Criterion | A: external | B: instrumented | C: controlled adapters | D: provenance | E: hybrid |
| --- | --- | --- | --- | --- | --- |
| Grounding strength | Strong for sampled public effects, weak internal attribution | Same-call internal values if hooks correct; circular if hooks lie | Stronger boundary coverage *if* all generated effects traverse adapters | Identity/lineage only, no behavior evidence | Attribution + independently checked sampled effects; still scoped |
| Portability / target independence | Observer per public protocol/storage | Hooks per backend/runtime | Adapter implementation per target; portable abstract signature | Portable mapping schema, lowering-specific entries | Portable contract; backend-specific hooks and observer |
| Runtime overhead | Process/snapshot I/O, potentially high | Trace serialization per event; tunable | Indirection/controlled I/O and checks | Negligible at runtime except lookup/hash | Higher on audited cases; sampling possible |
| Compiler complexity | Low; hard discovery of actual boundaries | Hook placement/control-flow coverage | High: enforce effect routing, error/commit ordering | Medium: mapping through all lowering stages | Highest integration cost; localized modules |
| Incorrect persistence | Detect selected declared durable bytes if read independently | Detect only what hook observes; pre-commit reports can lie | Detect adapter writes but bugs in adapter/commit can escape | Cannot detect | External reopen after return checks selected sink against adapter report |
| Hidden writes | Inventory/sandbox may detect within scoped resources | Uninstrumented writes escape | Routing prevents generated out-of-adapter writes only if closed lowering/authority is enforced | Cannot detect | Resource inventory/effect audit challenges adapter completeness; undeclared channels remain |
| Failure/no-write | Before/after raw bytes and public error, not intermediate writes | Can log attempted writes, may omit failure edge | Reject/abort or commit control; hooks at both success and failure | Maps failure path only if emitted | Compare bytes/existence on failure and hook/adapter write audit; scope explicit |
| Migration | Versioned byte snapshots; mapping needed to decode | Version transition events need faithful ordering | Versioned decoder/encoder + commit boundary | Maps migration IDs to generated units | Raw version and bytes plus independently decoded migration outcome |
| Concurrency | Hard to isolate/attribute; require locking or revisions | Events can interleave; trace IDs needed | Transaction boundaries/revisions possible, backend-specific | IDs do not serialize writers | Isolate first; require consistent snapshots/commit tokens for concurrent claims |
| Modified generated code | Still sees public behavior but contract mapping uncertain | Hooks can be removed/spoofed | Routing may be bypassed | Hash mismatch invalidates map | Refuse provenance-based verdict; external-only evidence separately labeled |
| Debugging value | Reproducible actual outputs/bytes | Fine-grained timeline | Failure at stable controlled boundary | Runtime → lowering → semantic entity lookup | Correlates independent mismatch with exact boundary and semantic contract |

A alone cannot prove that a particular semantic operation was exercised, or
that a named path captures all application state. B alone shares compiler
defects with the generated implementation. C is the best *coverage design*
for compiler-owned code, conditional on forbidding or explicitly declaring
escape hatches; D is necessary attribution but never a correctness witness.
E reduces, rather than eliminates, circular trust. Neither generated output's
idiomaticity nor its unreadability strengthens any model by itself.

## 4. Stable identity and provenance

**Finding:** existing semantic IDs support identity within the v0.3 model and
`inspect`/`diff`/`impact`. The artifact manifest records a deterministic
artifact hash and a broad list of IDs. The R5.5 binding uses an opaque boundary
string; it does not attest to an executable location. An ID is useful only if
its meaning, namespace, uniqueness and mapping are validated end-to-end.

Proposed identity roles (no prescribed syntax): operation and contract IDs
identify semantic meaning/version; state type, slot and field IDs identify
semantic projection/schema evolution; outcome IDs distinguish success/error
variants when specified; generation-unit IDs identify compiler-produced units,
not additional application concepts. Semantic identity should survive a
deterministic regeneration and unrelated layout refactors; lowering-unit IDs
need only be stable for the *same compiler/model inputs*. Check uniqueness and
references project-wide, record collisions and deliberate rename/replacement
edges, and never silently recycle an ID with changed meaning. Version or hash
contracts and binding descriptions separately so a stable operation ID cannot
mask a stale contract. At each lowering step map source IDs to produced units,
including many-to-many and shared runtime units; preserve operation ID and
invocation correlation at public and persistence boundaries. Avoid claiming
that a single line or unit uniquely implements an operation when code is shared.

**Proposed machine-readable provenance artifact:** bind canonical model digest,
contract digest/version, binding digest, compiler/backend/runtime versions,
generation input digest, artifact digests, target unit IDs and emitted boundary
IDs to semantic operation/contract/state IDs, public entry mapping, and declared
effect sinks/schema projections. Build it deterministically with the artifact;
verify it against the *deployed bytes* before attaching a runtime event to a
contract. A runtime event supplies generation/boundary/invocation identifiers
and observation schema version; an independent runner supplies its own session,
argv, outcome and durable-state evidence. Tooling can trace failure → runtime
boundary → generated unit → semantic operation → contract without reading
pretty-printed target source. Unlike today's all-IDs manifest, mappings must be
specific enough to diagnose wrong-lowering and stale-binding errors. Provenance
is an auditable **claim by the compiler**, not proof of semantic equivalence;
independent durable snapshots and public outcomes remain necessary. No source
map or artifact was implemented in R5.6.

## 5. Durable-state grounding and generated-artifact policy

Distinct layers: a local variable or domain object is an intermediate value;
a cache can lag or lead storage; a transaction's working set may roll back;
committed persistent state is visible after the storage commit; externally
visible state may include additional file/database/network sinks. A four-slot
record must name the state view and observation time. For the current single-file
CLI, an external runner can resolve the **same working directory**, snapshot
path existence and raw `tasks.json` bytes before process start, invoke one
public CLI call with recorded argv, wait for process termination, then reopen
and snapshot bytes/existence and complete exit/stdout/stderr. Decode and check
the declared schema/version **independently**; record both raw and projected
values. This grounds *one declared file view under isolated execution*, not all
possible durable effects. For failure/no-write compare raw bytes/existence,
plus observed scoped effect inventory; byte equality alone only proves equal
endpoints. Existing `write_state` uses temp file and `os.replace`; before/after
of `tasks.json` misses temporary writes and cannot certify power-loss durability.

For a future compiler-controlled persistence adapter, surround real
read/commit/abort boundaries, report operation and state IDs, resource namespace,
transaction/revision, schema version, attempted/committed writes and error
outcome. Independently reopen at a consistency point *after* the public call;
never call a pre-commit in-memory buffer the post-state. Define isolation or
version-based rejection for races. DB/network backends need independently
queryable committed views and explicit consistency assumptions. If generated
target code can perform arbitrary writes outside the adapter, the safe claim is
only about listed observed sinks. A closed-world effect-routing claim requires
checked lowering/authority and tested adapters; v0.3 effects are model-level
checks, **not** an OS sandbox or evidence of complete I/O interception.

Generated target artifacts are disposable: semantic model and checked binding
are authoritative. Regeneration may overwrite local edits. Check manifest and
deployed-byte hashes immediately before execution and, where deployment can
change during execution, pin the executed image or recheck after; a mismatch
invalidates provenance-based binding and strong grounding verdicts. Preserve a
separate external-only observation label if useful, never quietly attach a
stale semantic ID. A hash is a drift detector, not a security/DRM boundary; a
new build requires fresh provenance and checks. Current generation writes an
artifact and manifest, but does **not** enforce this execution-time policy.

## 6. Circular trust and independent checks

```
 compiler -> generated behavior -> compiler-generated hooks -> reported facts
       \-> compiler-generated provenance --------------------------/
                         | (shared defect can agree with itself)
 independent runner -> raw public request + complete outcome + durable bytes
                         | (separate capture/decoder and isolated namespace)
 verifier <- checked provenance + both observations + abstract contract
 ```

Useful independent challenges: compare hook-recorded input/outcome with public
argv/exit/streams; compare adapter post-state with direct durable reopening and
raw bytes; exercise error/no-write cases; inventory scoped effects; compare
generated artifact hash against regenerated deterministic output; use separate
acceptance oracle/differential and property-based cases; inject faults in
observers, bindings and lowering. An independent verifier implementation can
challenge the evaluator itself, but does not make a self-reported observation
true. Acceptance tests and differential tests cover selected behaviors, not all
contracts. Checks must fail closed on missing event, ID mismatch, unmapped
public call, hash mismatch, race or unobservable state when making a *strong*
grounded claim; they may still retain raw diagnostic evidence.

The trusted computing base remains: semantic interpretation, validator and
contract evaluator soundness; compiler lowering and effect-routing completeness;
runtime/adapter/observer correctness; deployment/hash tooling; independent
runner and durable decoder; OS/process/storage consistency and isolation; and
the assumptions behind the chosen acceptance oracle. Independent checks reduce
correlated errors but do not eliminate this base. No universal proof follows.

## 7. Assurance vocabulary (non-cumulative unless prerequisites stated)

| Status | Required evidence / maximum claim |
| --- | --- |
| `contract_defined` | Typed validated contract and stated applicability; describes intended behavior only. |
| `binding_checked` | Verified versioned signature, entry, argument decoding, outcome/error envelope, storage projection and sink references; no invocation claim. Today's R5.5 slot bijection alone falls short. |
| `provenance_intact` | Reproducible model/compiler/binding manifest and deployed artifact hashes checked; identifies the built image, not its correctness. |
| `observed_case_conformant` | Prior statuses plus independently captured same-call public input/outcome, post-termination declared durable pre/post and scoped effect evidence, checked against the contract; only this invocation/environment/view. Missing or ungrounded facts cannot receive this status. |
| `property_sampled` | Recorded generator, seeds, input/state domain, observer coverage and passing grounded cases; only sampled cases, never a frequency-based universal theorem. |
| `finite_domain_exhaustive` | Enumerated finite reachable states, inputs, errors and environment schedule within a stated bound, with grounded mapping and a completeness argument; universal **only within that bound**. |
| `statically_established` | Explicit property, scope and sound analysis/translation assumptions; only the discharged property, possibly conditional on adapters. |
| `formally_proven` | Machine-checkable proof/justified proof chain for declared domain, reachability, effects, error paths, lowering and environment/adapter assumptions; not implied by any finite test count. |

Statuses are evidence descriptors, not a linear score: static proof of one
property need not imply grounded runtime evidence for a different property.
R5.5's existing `evidence: observed_execution` must remain interpreted as
*record source asserted* until an independent grounding path exists; its
`proof_status: not_established` correctly prevents a proof claim.

## 8. AI-native generated structure

Compiler-owned, normalized operation entry/exit, storage adapter and stable-ID
event sites permit mechanical coverage checks, deterministic provenance,
cross-target trace correlation and precise failure localization. Repetition can
make missing event/commit branches detectable by structural checks. Human
readability is not required for the generated file; diagnostics can be
human-readable *views of semantic IDs and provenance*. Do not obfuscate it.

Against idiomatic target code, measure: percentage of public entries and effect
sinks mapped; fault-injection detection (wrong input, sink, outcome and commit);
regeneration reproducibility; stale-artifact rejection; runtime/trace overhead;
adapter and verifier defect rates; portability effort for a second backend;
debugging time from runtime failure to semantic contract; and change blast
radius. Normalization costs indirection, performance and compiler complexity;
may weaken target-specific optimizations, hide native diagnostics or create a
single faulty shared adapter. Idiomatic generated code can still be instrumented
and externally checked. Neither style alone establishes semantic correctness;
compare under the same observable cases and failures.

**Prototype decision:** no new code prototype was necessary for this conceptual
choice. R5.5's fabricated-record tests already demonstrate what the verifier
can be fooled by, while the existing `probe.py` independently exercises selected
subprocess outputs/file snapshots without joining them to the contract. R5.6
does not relabel either as a grounded end-to-end run. Architecture-specific
verification here runs the existing R5.5 focused tests; the *next* prototype
should use an unrelated synthetic operation, not repair B01. It should connect
checked public binding and deployed-image provenance to an externally captured
same-invocation tuple, then exercise wrong operation/input/result/state source,
pre/post timing, error writes, stale mapping and modified artifact. A deliberate
hidden sink should cause a scoped/unknown-effects verdict, not a false pass.
Only after this prototype passes fault injection should case-grounded assurance
be enabled. This is a testable recommendation, not an implemented capability.

## 9. B01 issue ownership (classification, no repairs)

| Existing blocker | Owning layer(s) and open boundary |
| --- | --- |
| Actual public-call grounding | **GROUNDING, COMPILER/BINDING, OBSERVATION, VERIFICATION**: checked real entry/args plus independent same-call capture and comparison; not a new operation construct. |
| Durable pre/post-state grounding | **GROUNDING, COMPILER/BINDING, OBSERVATION, VERIFICATION**: explicit state view, committed readback, failure byte/effect checks; concurrency/undeclared writes remain scoped. |
| Create insertion semantics | **CORE SEMANTICS, DOMAIN SEMANTICS**: fresh key, insertion, exact frame and outcome relation; independent of capture mechanism. |
| Completion framing | **CORE SEMANTICS, DOMAIN SEMANTICS**: target update, non-target preservation and result/error relation. |
| Migration outcome/version behavior | **CORE SEMANTICS, DOMAIN SEMANTICS, COMPILER/BINDING, OBSERVATION**: versioned before/after and result obligations plus actual envelope/committed version mapping. |
| CRITICAL / “above HIGH” | **BENCHMARK AMBIGUITY, DOMAIN SEMANTICS, UNKNOWN**: frozen text does not specify an independent observable ordinal comparator; exact-HIGH and round-trip are distinguishable. Do not infer sorted-by-priority from “above”. |

## 10. Accounting and recommended architecture

No experimental mechanism was added in this **documentation-only** phase.
Historical numbered raw constructs: **45**; provisional candidate core
semantic constructs: **29**. Preserve [R5.5's full 45-ID inventory](R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md#responsibility-inventory-every-historical-id-exactly-once):
core/domain 13, collection 11, state 4, operation 1 = 29;
runtime observation 3, conformance verification 2, evidence/test 5,
evolution/link metadata 5, benchmark/research administration 1 = 16.
Numbered compiler/binding metadata 0; numbered provenance constructs 0.
Existing unnumbered slot map/record/verdict and **proposed** generation-unit
IDs, manifests, adapters, event envelopes and assurance statuses are respectively
compiler/binding metadata, provenance, runtime observation, verifier and
evidence machinery, **not** stealth core constructs or new numbered entries.
If future work inventories newly named machinery, publish a new denominator
alongside the unchanged historical 45; counts do not imply adequacy.

**Recommendation: E, staged compiler-owned normalized boundaries + specific
provenance + independent public/durable observation.** Start with an isolated
single-resource synthetic operation and externally readable commit boundary;
admit more resources/concurrency only with explicit scope and adapter checks.

1. **Semantic layer trusts** typed abstract operation/state/outcome/effect
   meaning and explicitly stated environmental assumptions, not trace origin,
   CLI/file names or generated implementation claims.
2. **Compiler guarantees to be established** deterministic lowering, checked
   identity/entry/effect routing, emitted normalized boundaries and versioned
   manifests tied to deployed bytes. Today's generator does not guarantee
   complete routing or per-operation provenance.
3. **Binding metadata establishes** an independently checkable, versioned map
   from semantic operation/slots to public entry, argument decoding, outcome
   envelope, durable resource/view and generation boundary; it never proves a
   call occurred.
4. **Runtime observation captures** actual raw public request and outcome,
   same-invocation correlation, pre/post raw durable existence/bytes with
   independently decoded views after commit/termination, and scoped effect/
   environment/consistency evidence; hooks supplement but do not replace it.
5. **Verifier independently checks** deployed provenance, binding and event
   correlation, public/hook agreement, typed contract relation, raw no-write
   obligations, scope and missing/racy facts; it reports evidence level rather
   than accepting a self-declared source label.
6. **Trusted base** includes compiler/validator, runtime and adapters, external
   observer/decoder/verifier, artifact/deployment checks and storage/OS
   assumptions; separate oracle tests challenge correlated compiler defects.
7. **Finite claim** is conformance for observed invocations in the named
   environment and observed durable/effect scope, with explicit gaps; sampled
   tests never imply all public calls or hidden effects conform.
8. **Universal correctness** would additionally require sound semantics,
   complete reachable input/state/error/effect/environment coverage, sound
   lowering and adapter correspondence or proof, concurrency/termination and
   composition arguments; exhaustiveness only applies to explicitly bounded
   domains.

This identifies a coherent *architecture to prototype*, not a grounded
implementation or a decision to restart semantic adequacy. The limits on
arbitrary outside-adapter writes and concurrent durability are expressible as
explicit claim scopes rather than silently trusted state. B01 remains
inadequate and halted, Phase 5C paused, B17 unexposed and unclassified, format
UNFROZEN; R5.2.2 remains authoritative for benchmark execution state.

## Verification

From repository root, `python -m unittest discover -s benchmark/harness -v`:
**115 tests, OK**; `PYTHONPATH=src python -m unittest discover -s tests -v`:
**31 tests, OK**; focused architecture check
`python -m unittest discover -s benchmark/harness -p test_semantic_architecture_r5_5.py -v`:
**6 tests, OK**. These exercise current separation and historical benchmark
mechanics; they do not verify the recommended architecture's grounding.
`git diff --check`: exit 0, **no whitespace errors**. Git separately reported
working-copy LF-to-CRLF conversion warnings on the three edited `docs/` files;
those warnings are not test or whitespace failures. The new untracked result
file also passed `git diff --no-index --check -- NUL <result file>` (exit 0),
with the same separate line-ending warning.

R5_6_GROUNDING_MODEL_READY
