# Phase 5C R4 — classified B13 continuation

B13 was prospectively frozen in `B13-FREEZE-R4.md` before either preflight or
agent exposure; both B12 restores passed B13 preflight. Prediction and
implementation event streams are `B13-*-r4.jsonl`.

| Track | B13 result | B13 acceptance | Applicable R4 external | Internal |
| --- | --- | --- | --- | --- |
| Conventional | `SUCCESS` | 2/2 | 26 passed, 4 explicit B11 skips (30 methods), 0 failures | 32/32 |
| Lykoi | `BLOCKED_BY_GAP` (B08 archival and B07 note append) | inapplicable | 7 passed, 2 B02 skips, 0 failures | 33/33 |

Lykoi's 27 implementation files remain byte-identical to B10. Both snapshots
independently restored to fresh workspaces with complete inventory checks.

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional | `6d32c94a845f5ef81deef71b38d55d01112e9cc0b8c4485be19306b0fb54740d` | `c0bf40b2ef666b3a7d82d01315c8146b342f106947b19b4f57eefcad8409d3f4` | 2 |
| Lykoi | `0a95522407d1fbc65a9df6738ce6a9da047f1785b44653801989f1a3982a4f46` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Conventional composed expectation SHA-256:
`c5c0e1a417a8e5d52beeb1b97437b3ed86272540069557fda44f7b88b94c3a8b`.
The R4 oracle/replacement hashes remain pinned in `R4-EXECUTION-PIN.md`.
B14 requires a new prospective freeze before either track sees it.
