# Lykoi Phase 5C resumed execution — immutable interim evidence through B09

**Status: IN PROGRESS.** B09 was frozen in `B09-FREEZE-R3.md` before either
preflight or prediction. Both B08 continuation states passed independent B09
preflights. All prior progress records remain preserved.

| Track | B09 attempted | B09 achieved | Raw classification | Applicable external regression | Internal | Resulting achieved set |
| --- | --- | --- | --- | --- | --- | --- |
| Conventional | yes | yes | `SUCCESS` | 20/20 | 24/24 | B01–B09 |
| Lykoi | reached; blocked | no | `BLOCKED_BY_GAP` (`depends_on: ["B08"]`) | 7/7 (2 skipped) | 33/33 | B01, B04 |

B09 expressly requires selecting nonarchived tasks. The B08 archived state is
unavailable to Lykoi, so B09 cannot be meaningfully implemented against that
track's actual achieved state. `B09-lykoi-prediction.jsonl` additionally
records an observed limitation of input-dependent due-window filters; the
primary B09 classification remains the frozen dependency block, not an
additional independent gap determination. `B09-lykoi-implementation.jsonl`
records the blocked execution decision. Lykoi implementation bytes are
unchanged. No regression or implementation failure was classified.

| Track | Format-3 checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional B09 | `c377a7d05d690cb86bac426230c6a5640702e6482a45263bdcbbbff7967b8a9c` | `7fbc0dbcc2652e116de3d4180c85bf229d234310290ad46a9d7b3f7fb54627a2` | 2 |
| Lykoi B09 | `03e4706e3b68b93534164b11c9768ad37816a3ddf85598352425c23638edb67f` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both snapshots restored independently against their inventories. `B09-` files
contain the raw predictions, implementation events, acceptance (Conventional),
regressions, internal tests, attempt histories, and checkpoint evidence. Tool,
timing and token fields are preserved in raw streams where provided.

**Next boundary:** freeze B10 acceptance and capability metadata before any
B10 preflight or agent exposure.
