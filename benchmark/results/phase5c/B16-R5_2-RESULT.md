# B16 — independent track classifications (R5.2)

Frozen identity: `B16-FREEZE-R5_2.md`; common requirement SHA-256
`cf9ede733a5b305677dc954a50a9146d9766a7943e0a2f70099b9db4c4fdc1be`,
case `b4e3bf5eaa3286d3f9569a0f48a3a8974fbc0d4defaf97f8f64958d64b24f49b`,
fragment `2e50f5ff3fc35ae3adfbed5c263b192f887b5d476da8af943262c87421e5411d`.
Independent frozen preflight/predictions: `B16-PREFLIGHT-AND-PREDICTIONS-R5_2.md`.
Targets: Conventional `272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8`;
Lykoi `0c61e3be245c0b0e2870ed872c71ea62a6423b59c90575ac720e41f608040f98`.

## Conventional — SUCCESS

From the independent B15 restoration, the source-maintained implementation
added persisted user IDs with built-in `system`, required valid ownership on
create, and schema-11 migration of empty owners to `system` with atomic failure
on unresolved nonempty owners. The frozen prospective external oracle ran
read-only against the implementation: **33 passed, 28 explicit supersession
skips, 0 failures (61 methods)**. All three B16 case methods passed, including
retry after registration; all 24 applicable conditional R5 replacement methods
passed. Internal suite **39/39 passed**. Achieved B01–B16; R5 conditional
acceptance activates. The implementation remains isolated in the Conventional
B16 workspace and is to be captured by its checkpoint/snapshot below.

## Lykoi — AXIOM_CAPABILITY_GAP

From the independent B15 restoration, assessed the frozen Lykoi compiler's
ability to represent persistent users and validate task owners without
transplanting Conventional's implementation. An in-memory copy of the actual
`air/task_manager.json` with a second state `state_users`, passed to its
unchanged `air_compiler.validator.validate(Program(...))`, rejects with
`AirError: v0.1 requires exactly one state` at `validator.py:195–196` (the
version-neutral check also applies to the B15 v0.3 model). Every behavior is
bound to a single state and its output type at `validator.py:324–334`; a list
behavior cannot accept inputs at lines 353–357, and the allowed filters at
359–381 compare fields to literals or the clock, not a dynamically populated
user registry. These frozen rules cannot express an independently persisted
user collection with `create-user`/`list-users`, or a dynamic existing-user
referential guard on `create` and migration. Missing capability: **multiple
persistent entity states with cross-entity lookup/validation**. B10's earlier
owner gap is not a B16 prerequisite; this B16 gap is independently identified.
No new Lykoi axiom/primitive was added, no B16 semantics activated, and its
27 implementation files remain byte-identical to B15. Its applicable B15
external suite reran read-only: **7 passed, 2 existing B02 skips, 0 failures
(9 methods)**; internal suite **33/33 passed**. Achieved remains B01,B04;
applicable expectation remains
`9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13`.

## Checkpoint and independent restore

The versioned format-4 writer pinned the R5.2 composer, protocol amendment,
B16 requirement/case/fragment, prospective oracle, applicable conditional
oracle and full implementation inventory. Both checkpoints independently
validated and restored into **new** verification workspaces:

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files | Restored expectation |
| --- | --- | --- | ---: | --- |
| Conventional | `c2602584521bcacaaf68ac1394531f835fe9578765a1eb5b31aa943c5f728c8a` | `383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e` | 2 | `272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8` |
| Lykoi | `7318a230fb2a89bce5722b02a0899f72122e5bde5679c0fba4d0a896c55edf95` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 | `9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13` |

Evidence: `B16-*-attempts-r5_2.json`, `checkpoint-*-B16-r5_2.json`,
`snapshot-*-B16-r5_2.tar`, and the independent preflight and checkpoint
fixtures. Original B01–B15 checkpoints/snapshots and all R5/R5.1/R5.2 frozen
artifacts were not edited.
