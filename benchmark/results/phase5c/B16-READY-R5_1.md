# Phase 5C B16-ready boundary — corrected R5.1

**Status: READY BEFORE B16 EXPOSURE.** This record supersedes the halted R5
validation attempt as a continuation boundary, not as historical evidence.
Effective amendment: `PHASE5C-R5-PIN-FIX-1`, the immutable additive
`PROTOCOL_AMENDMENT_R5_1_PIN_FIX.md` (SHA-256
`a0379f157ae781c05ee066de5eea7326b8b6e00ec19e3cb393c15ad43abf0ee8`)
over the immutable original `PROTOCOL_AMENDMENT_R5_B16.md` (SHA-256
`54ff1293e3a52976e48423ce8c8ace83adea7fc78571aac50bfe8e0764b0387e`).
The defective original R5 runner `regression_phase5c_r5.py` remains at hash
`26c24272474a4a814d2adf016a174bfc243f93be23f6f7da126635133a6c9444`
and remains quarantined by `RESUME-R5-B16-VALIDATION-HALT.md`. R5.1's
separate corrected runner is `benchmark/harness/regression_phase5c_r5_1.py`
at `419a5feb9c09643adfa7c48ac9cf5123e255451571ff91345103cd7aa83e28c0`.
The only source difference between old and corrected runner is the one-line
R4 hash correction documented in the R5.1 addendum. Authoritative R4 runner
hash: `61830ce905deff3565180b3767e933f50e5c17bfef25ca4bcac41f9c4a706cb9`.

## Frozen acceptance inventory and activation

The unchanged `benchmark/harness/cases/B16_R5_replacements.py`, SHA-256
`9310e8f19557c8e9dfee4a1c4527524ec38c5de238d5b11d3ef9f5e08aa72d74`,
has exactly 27 original→replacement method mappings: 24 active affected
Conventional methods (23 ownerless successful creation plus B10 migration)
and five active affected Lykoi methods at their B15 states. Exact IDs and
retained assertions are recorded by the unchanged pinned audit and R5
amendment; both B11/R4 original supersessions and R4 replacements compose
without collisions. Frozen fixture
`benchmark/harness/test_phase5c_r5.py` is
`6e01d242a18119253feb58323bfb8c6099b2ecf2dfbedc1f5bf504f473ee8229`.
For each track, B16's prospective supersessions activate **only if that track
independently achieves B16**. At this boundary, neither track has achieved,
received, predicted, or attempted B16. The B16 condition is INACTIVE on both.

## Fresh independent B15 restorations and read-only validation

Both tracks were restored *again* after R5.1 freeze, from their authoritative
B15 checkpoints/snapshots into separate clean disposable workspaces, and full
checkpoint validation, snapshot hash, file inventory and Lykoi generated
artifact checks passed. `phase5d.py run --read-only` verified complete
implementation inventories before and after each external and internal run.

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files | Achieved at B15 | R5.1 external | Internal |
| --- | --- | --- | ---: | --- | --- | --- |
| Conventional | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` | `8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc` | 2 | B01–B15 | 30 passed / 34 methods; four explicit existing B11 skips; 0 failure events | 39/39 |
| Lykoi | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 | B01, B04 | 7 passed / 9 methods; two existing B02 skips; 0 failure events | 33/33 |

Conventional composed expectation SHA-256:
`27f67747e9a5b059fb5c3e4f0ecf4686c4e61782517f509ef1a359c77e7b61d8`.
Lykoi composed expectation SHA-256:
`9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13`.
These exact external/internal counts equal `RESUME-R4-B15-PROGRESS.md`.
No B16 case or replacement executed on either real B15 state.

The repository harness discovery suite reran after the new restores and passed
20/20. Its three R5 composition fixture methods passed: actual B15 sets
remain at R4 composition, hypothetical B16 achievement activates 24 and five
separate track-local replacements, and the 27-method inventory has precisely
the two deliberate B10 special bodies. Conventional B11 baseline/B01/B04
supersessions stay active and its B11/R4 source/notes replacements are eligible
for B16 replacement; Lykoi's original pre-B11 versions remain eligible only
on Lykoi if it achieves B16. Synthetic states did not alter either restored
B15 implementation or checkpoint.

## Environment/repository pin and continuation gate

HEAD `7833065ed702192ddd498a2e4fb4179741ad4b38`, Windows 11 Home build
26200, Python 3.14.3 at
`C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe`,
OpenCode CLI 1.18.32; same R4-pinned effective `workspace.py`,
`workspace_phase5e.py`, `phase5d.py`, composer, original oracle, R4 runner
and B11 replacements. Validation used `python -B`, with observer-run temporary
and cache directories outside both isolated workspaces. At recording, the
repository has the untracked additive R5/R5.1 amendment, replacement, runner,
fixture, halt and ready records; no tracked frozen historical file was changed.

**Next gate:** freeze B16 requirement/case/fragment/metadata under the normal
protocol before either B16 preflight/prediction. Use only R5.1's corrected
runner. Do not score B16 or produce a checkpoint before independent preflight,
prediction, implementation, applicable external/internal validation and valid
classification on each track. Stop before any future semantic contradiction.
