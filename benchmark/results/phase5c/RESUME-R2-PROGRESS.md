# Lykoi Phase 5C resumed execution — interim evidence through B06

**Status: IN PROGRESS.** B04–B06 have completed; B07–B20 have not been
attempted. This is not the final Phase 5C report. Earlier Phase 5C halt records,
the Phase 5B freeze and both Phase 5D/5E amendments remain unchanged.

## Frozen acceptance and capability records

The B04, B05 and B06 prospective requirement/case/fragment hashes were frozen
before either agent received each request. See `B04-FREEZE-R2.md`,
`B05-FREEZE-R2.md`, `B06-FREEZE-R2.md`. Each preflight passed independently
against the preceding format-3 checkpoint and actual achieved set. Prediction
JSONL files precede the corresponding implementation JSONL files. Both agent
tracks used `openai/gpt-6-sol` through isolated OpenCode sessions with
`PYTHONDONTWRITEBYTECODE=1` and external temp/cache paths. The Lykoi compiler,
runtime and schema were not edited. Historical `axiom` serialization IDs and
the frozen `AXIOM_CAPABILITY_GAP` label are retained.

| Request | Conventional attempted / achieved / classification | Lykoi attempted / achieved / classification | External regression (Conventional; Lykoi) | Internal (Conventional; Lykoi) |
| --- | --- | --- | --- | --- |
| B01 | yes / yes / SUCCESS (historical) | yes / yes / SUCCESS (historical) | Phase 5B | Phase 5B |
| B02 | yes / yes / SUCCESS (historical) | yes / no / AXIOM_CAPABILITY_GAP (historical) | Phase 5B | Phase 5B |
| B03 | yes / yes / SUCCESS (Phase 5D continuation) | reached / no / BLOCKED_BY_GAP (B02; Phase 5D continuation) | 9/9; 5/5 applicable | 8/8; 31/31 |
| B04 | yes / yes / SUCCESS | yes / yes / SUCCESS | 11/11; 7/7 applicable (2 skipped) | 10/10; 33/33 |
| B05 | yes / yes / SUCCESS | yes / no / AXIOM_CAPABILITY_GAP: input-dependent list filter | 12/12; 7/7 applicable (2 skipped) | 11/11; 33/33 |
| B06 | yes / yes / SUCCESS | yes / no / AXIOM_CAPABILITY_GAP: input-dependent list filter and trim assignment | 14/14; 7/7 applicable (2 skipped) | 14/14; 33/33 |
| B07–B20 | not reached / not attempted | not reached / not attempted | N/A | N/A |

Resulting Conventional achieved history: B01, B02, B03, B04, B05, B06.
Resulting Lykoi achieved history: B01, B04. Lykoi B03's B02 dependency
block is distinct from intrinsic gaps at B02, B05 and B06. No regressions or
implementation failures have been classified in B04–B06.

## Last verified continuation states

| Track | Format-3 checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional B06 | `7c1eaaf2bc4ca622fd74cf3a89db8549e20231fd60847ff3e9ff143541b9a631` | `a84c27d7833a9e1b1b5a593d4f703928e1c8746285e3b8463e369ad06bc59dad` | 2 |
| Lykoi B06 | `93a1ee6bc1882d477b12fe689f62f06eaafc89075a31d140b37d92aaa8926e30` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both B06 snapshots restored independently and matched their complete file
inventories. B04 and B05 checkpoint/snapshot pairs and each attempt history are
also in this directory. Format-3 records bind requirement, external case,
capability fragment, prior checkpoint, application inventory, expectation,
baseline manifest and frozen oracle/harness hashes. Phase 5D/5E integrity
suite: 13/13 passed after B06. B04–B06 read-only validation preserved each
track's workspace inventory; no runtime cache entered a checkpoint.

For each request and track, `Bxx-<track>-prediction.jsonl` and
`Bxx-<track>-implementation.jsonl` contain full raw OpenCode event streams;
`Bxx-<track>-acceptance.log` (when attempted), `-regression.log` and
`-internal.log` contain raw verification output. `B04-conventional-prior-regression.log`
is an unsuccessful *operator probe* against a B03 checkpoint after the app had
changed, rejected as expected by the runner's checkpoint/app hash guard; the
valid B04 checkpoint and resulting 11/11 regression are recorded separately.
Agent event streams supply tool/timing/token fields where provided; unavailable
telemetry and blinded reviews are N/A. No comparative interpretation is made.

**Next boundary:** construct and freeze the B07 case and capability fragment
before either B07 preflight or agent receives the B07 requirement. Start from
the two pinned B06 checkpoints/snapshots above. Do not report
`PHASE_5C_COMPLETE` without executing B07–B20 and final integrity validation.
