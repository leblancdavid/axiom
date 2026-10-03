# Lykoi prospective state evolution — R5.33

Versioned **bounded operation-contract generalization**, not a language freeze.
The sole application compiler entry is `benchmark.semantic.current_pipeline`.
The canonical v0.3 application model and historical semantic profiles retain
their versions. Candidate core count remains 30; no construct #31 is added.

## Signature and applicability

An R5.33 contract retains id/input/branches and declares:

```json
{
  "version": "R5.33",
  "state": {"pre": "<shape>", "post": "<shape>"},
  "requires": {"equals": ["<typed operand>", "<typed operand>"]}
}
```

The placeholders above are explanatory, not valid source. Each shape uses the
existing record/sequence/optional/nullable/scalar declarations. Both roots must
be records or sequences. Applicability is an existing Boolean semantic
precondition (#22), analyzed against input/pre only, with no external-capability
acquisition. The generated public invocation boundary validates the concrete
pre-type and predicate **before** executing the operation. A false predicate
or incompatible type produces an unavailable invocation, unchanged durable state
and no semantic event; it is not an operation-declared semantic failure outcome.
No pre-invocation malformed-input outcome mapping is introduced here.

Application state metadata is `{"versions": {"V1": shapeA, "V2": shapeB}}`.
These checked identities register allowed durable types; names do not themselves
test a stored version. Version-valued applicability/equalities remain semantic
source. Every operation's pre/post declaration must match registered types.
The runtime receives an operation-specific input/pre/post/outcome/capability
descriptor plus its generated applicability predicate. Structural compatibility
alone never authorizes a version-disallowed operation.

## Existing relation composition across types

A side-qualified form of #44 declares:

```json
{"default_missing": {
  "source": [], "target": ["specimens"], "identity": "accession",
  "field": "medium", "value": {"literal": {"type": "string", "value": "mineral"}}
}}
```

Empty source/target paths identify the corresponding root; one field names a
record-root collection projection. Paths are resolved against their own checked
slot types. Both collections have independently declared record elements with
string identities. Identity sets must be exact and unique. Each target row must
equal the old keyed row with the declared value installed only where absent.
Present fields, including optional information, are preserved. The source field
may be absent from its schema, or optional with compatible base type; the target
may require it. No whole-row structural widening or renaming is performed.

N defaults may target one collection only with identical source projection and
identity. Their fields are distinct. All source fields must exist unchanged in
the target, except optional-to-required tightening justified by a checked
default. Every new/tightened field must have a default. Removing/renaming source
fields is rejected. This profile does not define an arbitrary record map.

Existing `post_equals` constructs target record fields from typed expressions
over input/pre. It supports typed nested record construction, source-field
preservation, version literals and metadata. A cross-type branch must completely
cover its target root: either its root sequence or every record field. Collection
construction and equality cannot overlap. No unmentioned field is copied from
pre to post. The compiler therefore cannot supply hidden envelope behavior.

Whole-state preserve is valid only when both declared types are identical.
Same-shape operations may use the existing insertion/replacement/removal/default/
equality planner and preserve behavior. Older R5.27 source is unchanged shorthand
for equal pre/post slots. Both cross-type branch outcomes must be independently
typed against the target slot; no failure branch can pretend pre is post.

## Authority, lowering and verification

The existing authoritative analyzer records independent slots, scoped operand
facts, side-qualified relation bindings (including source/target collection and
field types), checked applicability, outcome types and evolution branch IDs.
These facts participate in the CheckedPlan seal. Current emitters/interpreters
consume them without another semantic analyzer. Source and fact mutation reject.

Constructive lowering initializes the target and fills only checked target
projections. Persistence decodes/checks pre with the pre descriptor, invokes,
checks the post descriptor/outcome, then serializes post. Independent verification
first checks both concrete types, then applicability, branch/outcome, keyed #44
row equations, identities and all target equalities. Grounding separately checks
actual public call, exact pre/post byte readback, event and artifact integrity.

## Durability limits

Normal generated execution computes and validates the complete target before
writing. A computation/type/applicability failure does not initiate the durable
write. The existing file binding uses direct `write_text`, not an atomic replace,
transaction, lock, fsync or crash recovery. Interrupted I/O can truncate or leave
partial durable bytes; concurrent access is unprotected. Evidence distinguishes
pre-state, execution and post-state for completed calls, not every intermediate
write. A committed write followed by an event/output failure may lack grounding.
No transactional atomicity or universal correctness is claimed.

Evidence and decision: [R5.33 result](../benchmark/results/phase5c/R5_33-CROSS-SHAPE-STATE-EVOLUTION.md).
