# Phase 5C R4 — classified B12 continuation

`B12-FREEZE-R4.md` was recorded before both preflights and before agent
exposure. Each B11 restore passed B12 preflight. Fresh isolated prediction and
implementation event streams are the four `B12-*-r4.jsonl` files.

| Track | B12 classification | B12 acceptance | R4 external | Internal | Achieved |
| --- | --- | --- | --- | --- | --- |
| Conventional | `SUCCESS` | 2/2 | 24 passed, 4 explicit B11 skips (28 methods), 0 failures | 31/31 | B01–B12 |
| Lykoi | `BLOCKED_BY_GAP`, depends on B08 archival | inapplicable | 7 passed, 2 B02 skips (9 methods), 0 failures | 33/33 | B01, B04 |

The Lykoi agent left its model/compiler/generated implementation inventory
unchanged. B12 has no supersessions; the same four B11 supersessions and R4
replacements ran on Conventional. Both snapshots below independently restored
and matched their complete checkpoint inventories.

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional | `879f60ae85d80444e55d6ab834fc7e1d3e24b95a11ed3964d808b4d9887e4c2f` | `5bd135342900c0dc55024f9ac665460ed7035294bbcb27ad7af96802e76dadd4` | 2 |
| Lykoi | `ef2579b7cec9bb3e25bf8d24ef01f5f6da295b552525dfc3af5646e5992e2fdc` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Conventional composed expectation SHA-256:
`1f2d657f65b6a2e78039f8123243cd2b31036e1540e06ae1895b7e258b22fa14`.
The R4 runner and replacement hashes remain as in `R4-EXECUTION-PIN.md`.
B13 requires its own prospective freeze before prediction or implementation.
