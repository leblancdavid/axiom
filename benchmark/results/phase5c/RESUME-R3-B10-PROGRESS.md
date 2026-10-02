# Lykoi Phase 5C resumed execution — immutable interim evidence through B10

**Status: IN PROGRESS.** B10 was frozen in `B10-FREEZE-R3.md` before both
independent preflights and predictions. Previous progress/evidence remains
unchanged.

| Track | B10 attempted | B10 achieved | Raw classification | Applicable external regression | Internal | Resulting achieved set |
| --- | --- | --- | --- | --- | --- | --- |
| Conventional | yes | yes | `SUCCESS` | 22/22 | 28/28 | B01–B10 |
| Lykoi | yes | no | `AXIOM_CAPABILITY_GAP` | 7/7 (2 skipped) | 33/33 | B01, B04 |

The Lykoi transcript `B10-lykoi-implementation.jsonl` preserves an in-memory
validated/generated partial candidate and probes demonstrating untrimmed
owner output, an omitted optional input failing a nonblank guard, and rejection
of input-dependent `list-owner` filtering. B10 independently requires these
behaviors and is an intrinsic Lykoi capability gap. No Lykoi implementation
bytes changed. No B10 regression or implementation failure was classified.

| Track | Format-3 checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional B10 | `5bb65e500add4ff348a0004cd216efb44519bc11d3c4815a7ee22f6c7e367688` | `f771bbdb709a34bfd2113de70e370ed95812cf9b36123328adf12676973164a7` | 2 |
| Lykoi B10 | `cb2fb04d04fa80c6af67c7ef6933002995b40fcd5bb84bc7f51599f49f6ee9a6` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both snapshots independently restored against complete inventories. Raw
prediction/implementation streams and acceptance, regression, internal,
attempt-history and checkpoint evidence are in the `B10-` files. Tool/timing/
token measurements are preserved in event streams where available.

**Next boundary:** freeze B11 acceptance and any expressly superseded legacy
case methods before either B11 preflight or agent exposure.
