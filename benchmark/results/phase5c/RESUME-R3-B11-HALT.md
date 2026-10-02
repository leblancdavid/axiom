# Lykoi Phase 5C-R3 halt — B11 frozen supersession incomplete

**Status: PHASE_5C_HALTED.** Valid execution and independently restored
checkpoints exist through B10. B11's requirement, prospective case and
capability fragment were frozen in `B11-FREEZE-R3.md`; both B11 preflights
passed, prediction streams were captured, and isolated implementation sessions
began. During B11 execution, before classifying either track or creating a
B11 checkpoint, review of the frozen applicable regression suite exposed an
unresolved methodology defect. No B11 acceptance/regression result is scored.

## Exact issue

B11 changes `delete` on a completed **unarchived** task to
`delete_requires_archive` without changing storage. The prospective frozen
`benchmark/harness/capabilities/B11.json` supersedes two obsolete methods:
`regression.Regression.test_baseline_lifecycle_filters_failures` and
`regression.Regression.test_b01_priority_and_regression`.

It omits **two more achieved and applicable frozen methods** that require the
opposite deletion outcome:

- `benchmark/harness/cases/B04.py`, method
  `regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations`:
  lines 39–44 complete `labelled`, then require its unarchived deletion to
  succeed. B04 is achieved on both tracks.
- `benchmark/harness/cases/B07.py`, method
  `regression_B07.cases.<locals>.Notes.test_append_order_trim_and_failed_append`:
  lines 42–45 complete `first`, then require its unarchived deletion to
  succeed. B07 is achieved on Conventional.

The capability-aware regression runner selects both methods from the achieved
set and skips only IDs explicitly declared in the achieved B11 fragment. A
Conventional implementation satisfying B11 must fail the two un-superseded
assertions. Altering the B11 fragment or case now, weakening the regressions,
special-casing implementation behavior, or classifying the predictable
failures as a legitimate implementation regression would silently amend a
frozen prospective contract after implementation began. The B11 replacement
case also lacks an explicit preservation of all B04 source and B07 note
assertions needed if those methods were prospectively superseded. No automatic
amendment is made. This is a protocol/acceptance-composition defect, not a
result for either track.

## Preserved B11 and valid continuation evidence

`B11-FREEZE-R3.md`, `B11-conventional-prediction.jsonl`,
`B11-lykoi-prediction.jsonl`, `B11-conventional-implementation.jsonl`, and
`B11-lykoi-implementation.jsonl` preserve the available execution sequence.
The modified Conventional B11 workspace is quarantined at
`C:\Users\lblan\AppData\Local\Temp\opencode\phase5c-r3-B10-verify-conventional`;
it is **not** a valid continuation checkpoint. Lykoi's B11 workspace is at
`C:\Users\lblan\AppData\Local\Temp\opencode\phase5c-r3-B10-verify-lykoi`.
Neither is to be used for continuation without a separately authorized
protocol decision. No B11 checkpoint, snapshot, attempt classification,
regression result or B12–B20 freeze/attempt exists.

| Last valid track state | Checkpoint SHA-256 | Snapshot SHA-256 | Achieved |
| --- | --- | --- | --- |
| Conventional B10 | `5bb65e500add4ff348a0004cd216efb44519bc11d3c4815a7ee22f6c7e367688` | `f771bbdb709a34bfd2113de70e370ed95812cf9b36123328adf12676973164a7` | B01–B10 |
| Lykoi B10 | `cb2fb04d04fa80c6af67c7ef6933002995b40fcd5bb84bc7f51599f49f6ee9a6` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | B01, B04 |

Both B10 checkpoint/snapshot pairs were restored independently and their
complete inventories matched. `RESUME-R2-PROGRESS.md` and all earlier R3
progress evidence remain unchanged. B01–B10 raw outcomes are in those records:
Conventional B01–B10 `SUCCESS`; Lykoi B01/B04 `SUCCESS`, B02/B05/B06/B07/B08/B10
`AXIOM_CAPABILITY_GAP`, and B03/B09 `BLOCKED_BY_GAP` (B02 and B08 respectively).
Latest verified applicable external/internal results are Conventional 22/22
and 28/28; Lykoi 7/7 (two skipped) and 33/33. There is no final B01–B20
record and Phase 5C is not complete.

**Stop.** Further B11–B20 execution requires separate protocol review and
explicit authorization. Do not begin Phase 6 or modify Lykoi.
