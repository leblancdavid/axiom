# Phase 5C R4 — classified B14 continuation

B14's requirement/case/fragment were frozen in `B14-FREEZE-R4.md` before
both preflights and separate prediction and implementation streams. Both B13
restores passed B14 preflight. Raw agent events are `B14-*-r4.jsonl`.

| Track | B14 outcome | B14 acceptance | R4 external | Internal |
| --- | --- | --- | --- | --- |
| Conventional | `SUCCESS` | 2/2 | 28 passed, 4 explicit B11 skips (32 methods), 0 failures | 37/37 |
| Lykoi | `LYKOI_CAPABILITY_GAP` (independent array/append/graph semantics) | inapplicable | 7 passed, 2 B02 skips, 0 failures | 33/33 |

The Lykoi agent probed the validator in memory and left all 27 implementation
files byte-identical to B10. Both validated snapshots independently restored
and passed complete inventory checks.

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional | `bf3b9a937b62089301c6dcd5b38021c16767c4f2c0ab9b34001ac870b377223e` | `bdf92afd7e285642c9a90ae8e742e3fed7de7393ae12c7fd83d4e2e5c0f41ecf` | 2 |
| Lykoi | `c09cc8a636a43faed891fe0a85a06bc84d606b567fd9205be235a159d5b85c28` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Conventional composed expectation SHA-256:
`f555fe5021d77cfd575d1f57077a97b24b8f06762023eb6cf8ed34cc9a2f1040`.
R4 oracle/replacement identities remain pinned in `R4-EXECUTION-PIN.md`.
