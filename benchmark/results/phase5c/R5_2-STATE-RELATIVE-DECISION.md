# Phase 5C R5.2 prospective composition decision (design, before implementation)

Audit inputs: `RESUME-R5_1-B16-FRAGMENT-HALT.md`, `B16-READY-R5_1.md`,
`B16-ACCEPTANCE-COMPOSITION-AUDIT.md`, frozen `requirements/B16.md`,
`harness/capability_profile.py`, `capabilities/B10.json`, and both authoritative
B15-r4 checkpoints. Neither track has received B16.

## Finding

The contradiction is real and general: the frozen composer interprets a fragment
as one literal schema patch. `add_fields.owner` rejects Conventional's achieved
B10 field; `change_defaults.owner` rejects Lykoi's absent field. Declaring B10
as a B16 prerequisite would pre-classify Lykoi without an experiment. This is
not evidence of implementation capability or inability. The same issue recurs
whenever independently achieved histories have different representations of a
property required by a later request.

## Smallest proposed extension

Keep the original composer and all B01–B15 fragments immutable. Introduce a
versioned prospective composer that delegates legacy fragments to the original
composer, and adds one declarative `ensure_fields` operation for new fragments.
Each entry specifies ONE target field type and migration default, and an
explicit finite set of permitted prior defaults if the field exists. If absent,
append the field and install the declared type/default. If present, verify its
known type and current default against the frozen permitted set, then set the
same target default without appending. Reject unknown prior values, duplicates,
conflicting contributions, malformed declarations and implicit type changes.
No track label, implementation, generated output, prediction or test result is
an input to selection. The only branch is presence in the accumulated *achieved*
contract; the new request is applied only upon independent achievement.

This operation is a schema-level realization rule, not a claim that a track
has implemented the property. The semantic request remains the single frozen
B16 requirement. Other observable semantics (user commands, ownership
validation and migration errors) belong in the same B16 acceptance case for
both histories. Existing R5/R5.1 method supersessions stay independently gated
by achieved B16. For histories not achieving B16, the old profile and R5.1
acceptance remain byte-equivalent. Freeze exact per-history target profiles,
their hashes, fragment/case/composer hashes and prior-state provenance before
predictions. Future request fragments may use the same operation only when
prospectively frozen with explicit prior compatibility constraints.

This decision is recorded before any composer implementation, B16 case or
fragment freeze, preflight, prediction, or track modification.
