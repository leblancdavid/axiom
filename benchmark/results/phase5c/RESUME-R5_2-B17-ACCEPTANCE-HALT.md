# Phase 5C — B17 pre-prediction acceptance-composition halt

**Status: B16 validly classified and independently checkpointed on both tracks.
B17 not frozen beyond its pre-existing requirement, predicted, attempted,
implemented or classified. B18–B20 unprocessed. Do not claim Phase 5C complete.**

Authoritative B16 result and continuation evidence:
`B16-R5_2-RESULT.md`, `checkpoint-conventional-B16-r5_2.json`,
`snapshot-conventional-B16-r5_2.tar`, `checkpoint-lykoi-B16-r5_2.json`,
`snapshot-lykoi-B16-r5_2.tar`. Conventional B16 is `SUCCESS`, achieved B01–B16;
Lykoi B16 is `AXIOM_CAPABILITY_GAP`, achieved B01,B04, with no Lykoi system
extension. Both snapshots were independently restored with inventory and
checkpoint validation. Earlier frozen evidence remains unchanged.

## Newly detected contradiction, before B17 prediction

The pre-existing `requirements/B17.md` requires all mutating task commands to
receive `--actor USER_ID` and requires user objects to include `role`. The
already-frozen shared B16 acceptance case `benchmark/harness/cases/B16.py`
line 27 expects `list-users` to return `[{'id': 'system'}]`, lines 34–35 expect
ID-only user objects, lines 45–48 create tasks with no actor, and lines 81–83
create a user and task without a role/actor. Lines 74 and 92–94 repeat the
obsolete user shape. Its B16 tests remain applicable to Conventional after
achieving B17 but would fail an implementation honoring B17. Additionally,
the 24 applicable B16/R5 conditional replacements replay earlier successful
`create` commands with `--owner system` but **without** a B17 actor; they would
contradict B17's `actor_required` even when earlier assertions remain valid.
Frozen B16 case/replacement bytes cannot be silently edited; existing B11/R4
and B16/R5 supersessions do not specify B17 actor/role replacements.

This is an acceptance-oracle composition contradiction, not evidence that a
track cannot implement B17. No B17 case, fragment, prediction or implementation
has been written. The normal protocol cannot classify B17 until a prospective,
versioned, explicitly authorized conditional supersession/acceptance plan
preserves unrelated old assertions while reconciling role shape and actor
requirements. It must be gated by each track's achieved B17 state, leaving
Lykoi's B16-gap oracle unchanged unless that track actually achieves B17.
Only after independent audit, authorization, freeze and revalidation should
B17 exposure resume. **Request authorization for this new protocol amendment.**
