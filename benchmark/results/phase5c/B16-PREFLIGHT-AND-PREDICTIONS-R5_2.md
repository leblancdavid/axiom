# B16 independent preflights and frozen predictions (before implementation)

Both preflights restored their own pinned B15 snapshots into distinct disposable
workspaces, checked checkpoint identity, full implementation inventory and
generated artifact (Lykoi), confirmed the shared B16 requirement/case/fragment
hashes against `B16-FREEZE-R5_2.md`, and composed each applicable oracle without
executing B16 against either B15 app. `test_phase5c_b16_gate_r5_2.py` passed
1/1; checkpoint writer/restore fixture passed 2/2 and full harness discovery
passed 28/28 before the preflight. No B16 residue exists in either predecessor.

| Preflight | B15 predecessor | Achieved prior | Frozen B16 target | Conditional replacement methods |
| --- | --- | --- | --- | ---: |
| Conventional PASS | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` | B01–B15 | `272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8` | 24 |
| Lykoi PASS | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` | B01,B04 | `0c61e3be245c0b0e2870ed872c71ea62a6423b59c90575ac720e41f608040f98` | 5 |

Neither preflight found a new protocol contradiction. The prospective target
hashes are specifications, not implementation observations.

## Frozen Conventional prediction

**Predicted `SUCCESS`.** Source-maintained Python can represent a separate
persistent user registry with built-in `system`; require an existing owner on
creation; migrate empty owner to `system`; fail without writing for unresolved
nonempty owners; and preserve B01–B15 behaviors. The significant risk is
the migration/owner validation ordering and updating existing internal tests
that still create ownerless tasks. Validate functionally using the shared B16
case, applicable 24 conditional replacements, accumulated external regressions
and internal tests. This is a prediction, not an outcome.

## Frozen Lykoi prediction

**Predicted `AXIOM_CAPABILITY_GAP`.** The B15 Lykoi achieved profile has no
B10 owner field. The frozen compiler/model's previously evidenced rejection
of list-valued command inputs and filters (B05/B06/B10), combined with the
absence of modeled persistent user-entity creation/listing and cross-entity
referential validation, makes the required `create-user`/`list-users` and
existing-user ownership semantics unlikely to be expressible in its frozen
language. B16 has no declared B10 prerequisite: an absent prior owner is
allowed by the frozen target; the prediction must be tested against the frozen
Lykoi system and does not grant permission to extend that system.

These predictions are fixed before either implementation or B16 test execution.
